package com.psnc.mvds.ishare.service;

import com.fasterxml.jackson.databind.ObjectMapper;
import com.nimbusds.jose.JWSAlgorithm;
import com.nimbusds.jose.JWSHeader;
import com.nimbusds.jose.JOSEObjectType;
import com.nimbusds.jose.JWSSigner;
import com.nimbusds.jose.crypto.RSASSASigner;
import com.nimbusds.jwt.JWTClaimsSet;
import com.nimbusds.jwt.SignedJWT;
import com.psnc.mvds.ishare.model.IShareTokenResponse;
import okhttp3.*;
import org.eclipse.edc.spi.monitor.Monitor;
import org.eclipse.edc.spi.result.Result;
import org.eclipse.edc.spi.security.Vault;

import java.io.ByteArrayInputStream;
import java.nio.charset.StandardCharsets;
import java.security.KeyFactory;
import java.security.PrivateKey;
import java.security.cert.Certificate;
import java.security.cert.CertificateFactory;
import java.security.cert.X509Certificate;
import java.security.interfaces.RSAPrivateKey;
import java.security.spec.PKCS8EncodedKeySpec;
import java.util.*;
import java.util.concurrent.locks.ReadWriteLock;
import java.util.concurrent.locks.ReentrantReadWriteLock;

/**
 * Service for managing iShare access tokens with caching and validation
 */
public class IShareTokenService {
    
    private static final String GRANT_TYPE = "client_credentials";
    private static final String CLIENT_ASSERTION_TYPE = "urn:ietf:params:oauth:client-assertion-type:jwt-bearer";
    private static final String ISHARE_DID_PREFIX = "did:ishare:";
    private static final int TOKEN_VALIDITY_SECONDS = 30;
    
    private final String participantRegistryUrl;
    private final String clientId;
    private final String prId;
    private final String vaultKeySecretName;
    private final String vaultCertSecretName;
    private final Vault vault;
    private final Monitor monitor;
    private final OkHttpClient httpClient;
    private final ObjectMapper objectMapper;
    
    private IShareTokenResponse cachedToken;
    private final ReadWriteLock tokenLock = new ReentrantReadWriteLock();
    
    public IShareTokenService(
            String participantRegistryUrl,
            String clientId,
            String prId,
            String vaultKeySecretName,
            String vaultCertSecretName,
            Vault vault,
            Monitor monitor,
            OkHttpClient httpClient,
            ObjectMapper objectMapper) {
        
        this.participantRegistryUrl = normalizeBaseUrl(participantRegistryUrl);
        this.clientId = clientId;
        this.prId = prId;
        this.vaultKeySecretName = vaultKeySecretName;
        this.vaultCertSecretName = vaultCertSecretName;
        this.vault = vault;
        this.monitor = monitor;
        this.httpClient = httpClient;
        this.objectMapper = objectMapper;
    }
    
    /**
     * Get a valid access token, using cached token if available and valid
     */
    public Result<String> getAccessToken() {
        // Check if cached token is valid
        tokenLock.readLock().lock();
        try {
            if (cachedToken != null && cachedToken.isValid()) {
                monitor.debug(String.format("Using cached token, valid for %d more seconds", 
                    cachedToken.getRemainingValiditySeconds()));
                return Result.success(cachedToken.getAccessToken());
            }
        } finally {
            tokenLock.readLock().unlock();
        }
        
        // Need to get a new token
        tokenLock.writeLock().lock();
        try {
            // Double-check in case another thread just updated it
            if (cachedToken != null && cachedToken.isValid()) {
                return Result.success(cachedToken.getAccessToken());
            }
            
            monitor.info("Fetching new access token from Participant Registry");
            var result = fetchNewToken();
            
            if (result.succeeded()) {
                cachedToken = result.getContent();
                monitor.info(String.format("Successfully fetched new token, valid for %d seconds", 
                    cachedToken.getExpiresIn()));
                return Result.success(cachedToken.getAccessToken());
            } else {
                monitor.severe("Failed to fetch access token: " + result.getFailureDetail());
                return Result.failure(result.getFailureMessages());
            }
        } finally {
            tokenLock.writeLock().unlock();
        }
    }
    
    /**
     * Force refresh of the access token
     */
    public Result<String> refreshAccessToken() {
        tokenLock.writeLock().lock();
        try {
            monitor.info("Forcing refresh of access token");
            cachedToken = null;
            return getAccessToken();
        } finally {
            tokenLock.writeLock().unlock();
        }
    }
    
    /**
     * Check if there is a valid cached token
     */
    public boolean hasValidToken() {
        tokenLock.readLock().lock();
        try {
            return cachedToken != null && cachedToken.isValid();
        } finally {
            tokenLock.readLock().unlock();
        }
    }
    
    /**
     * Fetch a new token from the Participant Registry
     */
    private Result<IShareTokenResponse> fetchNewToken() {
        try {
            // Create client assertion JWT
            var clientAssertionResult = createClientAssertion();
            if (clientAssertionResult.failed()) {
                return Result.failure(clientAssertionResult.getFailureMessages());
            }
            String clientAssertion = clientAssertionResult.getContent();
            
            // Build request body
                String ishareClientId = getClientId();
            FormBody requestBody = new FormBody.Builder()
                    .add("grant_type", GRANT_TYPE)
                    .add("client_assertion_type", CLIENT_ASSERTION_TYPE)
                    .add("client_assertion", clientAssertion)
                    .add("client_id", ishareClientId)
                    .add("scope", "iSHARE")
                    .build();
            
            // Build request
                String tokenEndpoint = getTokenEndpoint();
            Request request = new Request.Builder()
                    .url(tokenEndpoint)
                    .post(requestBody)
                    .header("Content-Type", "application/x-www-form-urlencoded")
                    .build();
            
            // Execute request
            try (Response response = httpClient.newCall(request).execute()) {
                String responseBody = response.body() != null ? response.body().string() : "";
                
                if (!response.isSuccessful()) {
                    String errorMsg = String.format("Token request failed with status %d: %s", 
                        response.code(), responseBody);
                    monitor.warning(errorMsg);
                    return Result.failure(errorMsg);
                }
                
                // Parse response
                IShareTokenResponse tokenResponse = objectMapper.readValue(responseBody, IShareTokenResponse.class);
                tokenResponse.setReceivedAt(System.currentTimeMillis());
                
                return Result.success(tokenResponse);
            }
            
        } catch (Exception e) {
            String errorMsg = "Exception while fetching token: " + e.getMessage();
            monitor.severe(errorMsg, e);
            return Result.failure(errorMsg);
        }
    }
    
    /**
     * Create a client assertion JWT as per iShare specification
     * JWT header includes x5c certificate chain for signature verification
     */
    private Result<String> createClientAssertion() {
        try {
            // Load private key from keystore
            var keyResult = loadPrivateKey();
            if (keyResult.failed()) {
                return Result.failure(keyResult.getFailureMessages());
            }
            RSAPrivateKey privateKey = keyResult.getContent();
            
            // Load certificate chain for x5c header
            var certResult = loadCertificateChainForHeader();
            if (certResult.failed()) {
                return Result.failure(certResult.getFailureMessages());
            }
            List<com.nimbusds.jose.util.Base64> x5cChain = certResult.getContent();
                String ishareClientId = getClientId();
            
            // Build JWT claims — iss/sub = orgID (client_id), aud = PR's DID/EORI
            long now = System.currentTimeMillis() / 1000;
            JWTClaimsSet claimsSet = new JWTClaimsSet.Builder()
                    .issuer(ishareClientId)
                    .subject(ishareClientId)
                    .audience(prId)
                    .jwtID(UUID.randomUUID().toString())
                    .issueTime(new Date(now * 1000))
                    .expirationTime(new Date((now + TOKEN_VALIDITY_SECONDS) * 1000))
                    .build();
            
                // Build JWT header
            var headerBuilder = new JWSHeader.Builder(JWSAlgorithm.RS256)
                    .type(JOSEObjectType.JWT);

                // iShare requirement: include full certificate chain in x5c
                headerBuilder.x509CertChain(x5cChain);
            
            // Sign JWT
            SignedJWT signedJWT = new SignedJWT(
                    headerBuilder.build(),
                    claimsSet);
            
            JWSSigner signer = new RSASSASigner(privateKey);
            signedJWT.sign(signer);
            
            return Result.success(signedJWT.serialize());
            
        } catch (Exception e) {
            String errorMsg = "Failed to create client assertion: " + e.getMessage();
            monitor.severe(errorMsg, e);
            return Result.failure(errorMsg);
        }
    }

    /**
     * Debug helper for manual testing in tools like Bruno/Postman.
     */
    public Result<String> createClientAssertionForDebug() {
        return createClientAssertion();
    }

    /**
     * Returns the OAuth2 token endpoint used by this service.
     */
    public String getTokenEndpoint() {
        return participantRegistryUrl + "/connect/token";
    }

    /**
     * Returns client identifier used in token request and JWT iss/sub.
     */
    public String getClientId() {
        if (clientId == null || clientId.isBlank()) {
            return clientId;
        }
        return clientId.startsWith(ISHARE_DID_PREFIX) ? clientId : ISHARE_DID_PREFIX + clientId;
    }

    private static String normalizeBaseUrl(String url) {
        if (url == null) {
            return null;
        }
        return url.endsWith("/") ? url.substring(0, url.length() - 1) : url;
    }
    
    /**
     * Load RSA private key (PKCS#8 PEM) from Hashicorp Vault
     */
    private Result<RSAPrivateKey> loadPrivateKey() {
        String pem = vault.resolveSecret(vaultKeySecretName);
        if (pem == null || pem.isBlank()) {
            return Result.failure("Private key secret '" + vaultKeySecretName + "' not found in vault");
        }
        try {
            String base64 = pem
                    .replace("-----BEGIN PRIVATE KEY-----", "")
                    .replace("-----END PRIVATE KEY-----", "")
                    .replaceAll("\\s", "");
            byte[] derBytes = Base64.getDecoder().decode(base64);
            KeyFactory keyFactory = KeyFactory.getInstance("RSA");
            PrivateKey key = keyFactory.generatePrivate(new PKCS8EncodedKeySpec(derBytes));
            if (!(key instanceof RSAPrivateKey)) {
                return Result.failure("Key loaded from vault is not an RSA private key");
            }
            return Result.success((RSAPrivateKey) key);
        } catch (Exception e) {
            String errorMsg = "Failed to parse private key from vault: " + e.getMessage();
            monitor.severe(errorMsg, e);
            return Result.failure(errorMsg);
        }
    }
    
    /**
     * Load X.509 certificate chain (PEM) from Hashicorp Vault for x5c JWT header.
     * The PEM value may contain one or more certificates.
     */
    private Result<List<com.nimbusds.jose.util.Base64>> loadCertificateChainForHeader() {
        String pem = vault.resolveSecret(vaultCertSecretName);
        if (pem == null || pem.isBlank()) {
            return Result.failure("Certificate secret '" + vaultCertSecretName + "' not found in vault");
        }
        try {
            CertificateFactory cf = CertificateFactory.getInstance("X.509");
            Collection<? extends Certificate> certs = cf.generateCertificates(
                    new ByteArrayInputStream(pem.getBytes(StandardCharsets.UTF_8)));
            
            List<com.nimbusds.jose.util.Base64> x5cChain = new ArrayList<>();
            for (Certificate cert : certs) {
                if (cert instanceof X509Certificate) {
                    x5cChain.add(com.nimbusds.jose.util.Base64.encode(cert.getEncoded()));
                }
            }
            
            if (x5cChain.isEmpty()) {
                return Result.failure("No X.509 certificates found in vault secret '" + vaultCertSecretName + "'");
            }
            
            monitor.debug(String.format("Loaded certificate chain with %d certificate(s) for x5c header", x5cChain.size()));
            return Result.success(x5cChain);
        } catch (Exception e) {
            String errorMsg = "Failed to parse certificate chain from vault: " + e.getMessage();
            monitor.debug(errorMsg);
            return Result.failure(errorMsg);
        }
    }
}
