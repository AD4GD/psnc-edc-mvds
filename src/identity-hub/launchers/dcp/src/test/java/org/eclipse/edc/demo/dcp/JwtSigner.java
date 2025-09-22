/*
 *  Copyright (c) 2024 Metaform Systems, Inc.
 *
 *  This program and the accompanying materials are made available under the
 *  terms of the Apache License, Version 2.0 which is available at
 *  https://www.apache.org/licenses/LICENSE-2.0
 *
 *  SPDX-License-Identifier: Apache-2.0
 *
 *  Contributors:
 *       Metaform Systems, Inc. - initial API and implementation
 *
 */

package org.eclipse.edc.demo.dcp;

import com.fasterxml.jackson.databind.ObjectMapper;
import com.nimbusds.jose.JOSEException;
import com.nimbusds.jose.JOSEObjectType;
import com.nimbusds.jose.JWSAlgorithm;
import com.nimbusds.jose.JWSHeader;
import com.nimbusds.jwt.JWTClaimsSet;
import com.nimbusds.jwt.SignedJWT;
import org.eclipse.edc.iam.did.spi.document.DidDocument;
import org.eclipse.edc.keys.keyparsers.PemParser;
import org.eclipse.edc.security.token.jwt.CryptoConverter;
import org.junit.jupiter.api.extension.ExtensionContext;
import org.junit.jupiter.params.ParameterizedTest;
import org.junit.jupiter.params.provider.Arguments;
import org.junit.jupiter.params.provider.ArgumentsProvider;
import org.junit.jupiter.params.provider.ArgumentsSource;

import java.io.File;
import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Paths;
import java.security.KeyPair;
import java.security.PrivateKey;
import java.security.PublicKey;
import java.time.Instant;
import java.util.Date;
import java.util.Map;
import java.util.stream.Stream;

import static org.mockito.Mockito.mock;

/**
 * Use this test to read a verifiable credential from the file system, and sign it with a given private key. You will need:
 * <ul>
 *     <li>A JSON file containing the VC</li>
 *     <li>A public/private key pair in either JWK or PEM format</li>
 * </ul>
 */
@SuppressWarnings("NewClassNamingConvention")
public class JwtSigner {

    public static final String ISSUER_PRIVATE_KEY_FILE_PATH = System.getProperty("user.dir") + "/../../../../docker/identity-hub/certs/issuer_private.pem";
    public static final String ISSUER_PUBLIC_KEY_FILE_PATH = System.getProperty("user.dir") + "/../../../../docker/identity-hub/certs/issuer_public.pem";
    public static final File ISSUER_DID_DOCUMENT_K8S = new File(System.getProperty("user.dir") + "/../../../../docker/issuer-service/assets/did.k8s.json");
    
    public static final String DATASPACE_ISSUER_DID_K8S = "did:web:dataspace-issuer";
    
    public static final String CONSUMER_IH_DID = "did:web:consumer-ih%3A7083:alice";
    public static final String PROVIDER_IH_DID = "did:web:provider-ih%3A7093:bob";
    public static final String FC_IH_DID = "did:web:fc-ih%3A7103:piotr";


    private final ObjectMapper mapper = new ObjectMapper();

    @ParameterizedTest
    @ArgumentsSource(InputOutputProvider.class)
    void generateJwt(String rawCredentialFilePath, File vcResource, String did, String issuerDid, File issuerDidDocument) throws JOSEException, IOException {

        var header = new JWSHeader.Builder(JWSAlgorithm.EdDSA)
                .keyID(issuerDid + "#key-1")
                .type(JOSEObjectType.JWT)
                .build();


        var credential = mapper.readValue(new File(rawCredentialFilePath), Map.class);

        var claims = new JWTClaimsSet.Builder()
                .audience(did)
                .subject(did)
                .issuer(issuerDid)
                .claim("vc", credential)
                .issueTime(Date.from(Instant.now()))
                .build();

        // this must be the path to the Credential issuer's private key
        var privateKey = (PrivateKey) new PemParser(mock()).parse(readFile(ISSUER_PRIVATE_KEY_FILE_PATH)).orElseThrow(f -> new RuntimeException(f.getFailureDetail()));
        var publicKey = (PublicKey) new PemParser(mock()).parse(readFile(ISSUER_PUBLIC_KEY_FILE_PATH)).orElseThrow(f -> new RuntimeException(f.getFailureDetail()));

        // sign raw credentials with new issuer public key
        var jwt = new SignedJWT(header, claims);
        jwt.sign(CryptoConverter.createSignerFor(privateKey));

        // replace the "rawVc" field in the VC resources file, so that it gets seeded to the database
        var content = Files.readString(vcResource.toPath());
        var updatedContent = content.replaceFirst("\"rawVc\":.*,", "\"rawVc\": \"%s\",".formatted(jwt.serialize()));
        Files.write(vcResource.toPath(), updatedContent.getBytes());

        // update issuer DID document with new public key
        var issuerJwk = CryptoConverter.createJwk(new KeyPair(publicKey, null));
        var didDoc = mapper.readValue(issuerDidDocument, DidDocument.class);

        var issuerPk = didDoc.getVerificationMethod().get(0).getPublicKeyJwk();
        issuerPk.clear();
        issuerPk.putAll(issuerJwk.toPublicJWK().toJSONObject());
        Files.write(issuerDidDocument.toPath(), mapper.writeValueAsBytes(didDoc));
    }

    private String readFile(String path) {
        try {
            return Files.readString(Paths.get(path));
        } catch (IOException e) {
            throw new RuntimeException(e);
        }
    }

    private static class InputOutputProvider implements ArgumentsProvider {
        @Override
        public Stream<? extends Arguments> provideArguments(ExtensionContext extensionContext) {
            var basePath = "/../../../../docker/identity-hub/credentials/";
            var membershipVc = "membership_vc.json";
            var membershipCredential = "membership-credential.json";
            var dataprocessorVc = "dataprocessor_vc.json";
            var dataprocessorCredential = "dataprocessor-credential.json";

            return Stream.of(

                    // PROVIDER credentials, K8S and local
                    Arguments.of(GetAssetPath(basePath, "provider", membershipVc),
                            new File(GetAssetPath(basePath, "provider", membershipCredential)),
                            PROVIDER_IH_DID, DATASPACE_ISSUER_DID_K8S, ISSUER_DID_DOCUMENT_K8S),

                    Arguments.of(GetAssetPath(basePath, "provider", dataprocessorVc),
                            new File(GetAssetPath(basePath, "provider", dataprocessorCredential)),
                            PROVIDER_IH_DID, DATASPACE_ISSUER_DID_K8S, ISSUER_DID_DOCUMENT_K8S),

                    // CONSUMER credentials, K8S and local
                    Arguments.of(GetAssetPath(basePath, "consumer", membershipVc),
                            new File(GetAssetPath(basePath, "consumer", membershipCredential)),
                            CONSUMER_IH_DID, DATASPACE_ISSUER_DID_K8S, ISSUER_DID_DOCUMENT_K8S),

                    Arguments.of(GetAssetPath(basePath, "consumer", dataprocessorVc),
                            new File(GetAssetPath(basePath, "consumer", dataprocessorCredential)),
                            CONSUMER_IH_DID, DATASPACE_ISSUER_DID_K8S, ISSUER_DID_DOCUMENT_K8S),

                    // FC credentials, K8S and local
                    Arguments.of(GetAssetPath(basePath, "federated-catalog", membershipVc),
                            new File(GetAssetPath(basePath, "federated-catalog", membershipCredential)),
                            FC_IH_DID, DATASPACE_ISSUER_DID_K8S, ISSUER_DID_DOCUMENT_K8S),

                    Arguments.of(GetAssetPath(basePath, "federated-catalog", dataprocessorVc),
                            new File(GetAssetPath(basePath, "federated-catalog", dataprocessorCredential)),
                            FC_IH_DID, DATASPACE_ISSUER_DID_K8S, ISSUER_DID_DOCUMENT_K8S)

            );
        }

        private String GetAssetPath(String basePrefix, String folder, String fileName) {
                return String.format("%s%s%s/%s", System.getProperty("user.dir"), basePrefix, folder, fileName);
        }
    }
}
