package com.psnc.mvds.ishare.extension;

import com.fasterxml.jackson.databind.ObjectMapper;
import com.psnc.mvds.ishare.client.IShareParticipantRegistryClient;
import com.psnc.mvds.ishare.model.IShareApiResponse;
import com.psnc.mvds.ishare.service.IShareTokenService;
import okhttp3.OkHttpClient;
import org.eclipse.edc.runtime.metamodel.annotation.Extension;
import org.eclipse.edc.runtime.metamodel.annotation.Inject;
import org.eclipse.edc.runtime.metamodel.annotation.Provider;
import org.eclipse.edc.runtime.metamodel.annotation.Setting;
import org.eclipse.edc.spi.monitor.Monitor;
import org.eclipse.edc.spi.result.Result;
import org.eclipse.edc.spi.security.Vault;
import org.eclipse.edc.spi.system.ServiceExtension;
import org.eclipse.edc.spi.system.ServiceExtensionContext;

import java.util.HashMap;
import java.util.Map;
import java.util.concurrent.TimeUnit;

/**
 * Extension for integrating with iShare Participant Registry
 */
@Extension(value = IShareParticipantRegistryExtension.NAME)
public class IShareParticipantRegistryExtension implements ServiceExtension {
    
    public static final String NAME = "iShare Participant Registry Extension";
    
    @Setting(value = "Base URL of the iShare Participant Registry", required = true)
    public static final String ISHARE_PR_URL = "ishare.pr.url";
    
    @Setting(value = "Organization identifier (EORI) of this participant — used as iss and sub in JWT client assertions", required = true)
    public static final String ISHARE_CLIENT_ID = "ishare.client.id";
    
    @Setting(value = "DID or EORI of the iShare Participant Registry — used as aud in JWT client assertions", required = true)
    public static final String ISHARE_PR_ID = "ishare.pr.id";
    
    @Setting(value = "Vault secret name storing the RSA private key in PKCS#8 PEM format", required = true)
    public static final String ISHARE_VAULT_KEY_SECRET = "ishare.vault.key.secret";
    
    @Setting(value = "Vault secret name storing the CA-signed certificate chain in PEM format", required = true)
    public static final String ISHARE_VAULT_CERT_SECRET = "ishare.vault.cert.secret";
    
    @Setting(value = "Enable auto-initialization of iShare client on startup", defaultValue = "false")
    public static final String ISHARE_AUTO_INIT = "ishare.auto.init";
    
    @Inject
    private Monitor monitor;
    
    @Inject
    private Vault vault;
    
    private IShareTokenService tokenService;
    private IShareParticipantRegistryClient prClient;
    
    @Override
    public String name() {
        return NAME;
    }
    
    @Override
    public void initialize(ServiceExtensionContext context) {
        monitor.info("Initializing iShare Participant Registry Extension");
        
        // Get configuration
        String prUrl = context.getSetting(ISHARE_PR_URL, null);
        String clientId = context.getSetting(ISHARE_CLIENT_ID, null);
        String prId = context.getSetting(ISHARE_PR_ID, null);
        String vaultKeySecret = context.getSetting(ISHARE_VAULT_KEY_SECRET, null);
        String vaultCertSecret = context.getSetting(ISHARE_VAULT_CERT_SECRET, null);
        boolean autoInit = Boolean.parseBoolean(context.getSetting(ISHARE_AUTO_INIT, "false"));
        
        // Validate configuration
        if (prUrl == null || clientId == null || prId == null || vaultKeySecret == null || vaultCertSecret == null) {
            monitor.warning("iShare Participant Registry is not configured. Extension will not be initialized.");
            monitor.warning("Required settings: " + ISHARE_PR_URL + ", " + ISHARE_CLIENT_ID + ", " +
                ISHARE_PR_ID + ", " + ISHARE_VAULT_KEY_SECRET + ", " + ISHARE_VAULT_CERT_SECRET);
            return;
        }
        
        // Create HTTP client with reasonable timeouts
        OkHttpClient httpClient = new OkHttpClient.Builder()
                .connectTimeout(30, TimeUnit.SECONDS)
                .readTimeout(30, TimeUnit.SECONDS)
                .writeTimeout(30, TimeUnit.SECONDS)
                .build();
        
        ObjectMapper objectMapper = new ObjectMapper();
        
        // Initialize token service — reads keys from Hashicorp Vault at runtime
        tokenService = new IShareTokenService(
                prUrl,
                clientId,
                prId,
                vaultKeySecret,
                vaultCertSecret,
                vault,
                monitor,
                httpClient,
                objectMapper
        );
        
        // Initialize PR client
        prClient = new IShareParticipantRegistryClient(
                prUrl,
                tokenService,
                monitor,
                httpClient,
                objectMapper
        );
        
        monitor.info("iShare Participant Registry Extension initialized successfully");
        
        // Auto-initialize if configured
        if (autoInit) {
            monitor.info("Auto-initialization enabled, testing token acquisition...");
            Result<String> tokenResult = tokenService.getAccessToken();
            if (tokenResult.succeeded()) {
                monitor.info("Successfully acquired access token from Participant Registry");
            } else {
                monitor.warning("Failed to acquire access token: " + tokenResult.getFailureDetail());
            }
        }
    }
    
    @Provider
    public IShareTokenService tokenService() {
        return tokenService;
    }
    
    @Provider
    public IShareParticipantRegistryClient participantRegistryClient() {
        return prClient;
    }
    
    /**
     * Get the token service instance
     */
    public IShareTokenService getTokenService() {
        return tokenService;
    }
    
    /**
     * Get the Participant Registry client instance
     */
    public IShareParticipantRegistryClient getParticipantRegistryClient() {
        return prClient;
    }
    
    /**
     * Test method to fetch parties from PR
     */
    public Result<IShareApiResponse> testGetParties() {
        if (prClient == null) {
            return Result.failure("Participant Registry client not initialized");
        }
        return prClient.getParties();
    }
    
    /**
     * Test method to fetch trusted list from PR
     */
    public Result<IShareApiResponse> testGetTrustedList() {
        if (prClient == null) {
            return Result.failure("Participant Registry client not initialized");
        }
        return prClient.getTrustedList();
    }
    
    /**
     * Test method to fetch dataspaces from PR
     */
    public Result<IShareApiResponse> testGetDataspaces() {
        if (prClient == null) {
            return Result.failure("Participant Registry client not initialized");
        }
        return prClient.getDataspaces();
    }
}
