
package org.psnc.mvd.identity.keycloak;

import org.eclipse.edc.spi.monitor.Monitor;
import org.eclipse.edc.spi.response.StatusResult;

import org.psnc.mvd.identity.IdentityProviderClient;
import org.psnc.mvd.identity.models.IdentityClientModel;
import org.psnc.mvd.identity.models.IdentityProviderSettings;

import org.keycloak.admin.client.Keycloak;
import org.keycloak.admin.client.KeycloakBuilder;
import org.keycloak.admin.client.resource.ProtocolMappersResource;
import org.keycloak.representations.idm.ClientRepresentation;
import org.keycloak.representations.idm.ClientScopeRepresentation;
import org.keycloak.representations.idm.ProtocolMapperRepresentation;

import java.util.Collections;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

public class KeycloakIdentityProviderClient implements IdentityProviderClient {

    private Monitor monitor;
    private IdentityProviderSettings settings;
    private Keycloak keycloakClient;


    public KeycloakIdentityProviderClient(
        Monitor monitor,
        IdentityProviderSettings settings
        ) {
        this.monitor = monitor;
        this.settings = settings;

        this.keycloakClient = KeycloakBuilder.builder()
            .serverUrl(settings.getServerUrl())
            .realm(settings.getAdminRealm())
            .clientId(settings.getAdminClientId())
            .username(settings.getAdminLogin())
            .password(settings.getAdminPassword())
            .build();
    }

    @Override
    public StatusResult<IdentityClientModel> getClient(String clientId) {

        var realm = settings.getIdentityRealm();
        List<ClientRepresentation> clients = keycloakClient.realm(realm).clients().findAll();

        ClientRepresentation existingClient = clients.stream()
                .filter(c -> clientId.equals(c.getClientId()))
                .findFirst()
                .orElse(null);

        var clientModel = new IdentityClientModel(clientId, null);

        String clientUuid = keycloakClient.realm(realm).clients().findByClientId(clientId).get(0).getId();
        List<ClientScopeRepresentation> clientScopes = keycloakClient.realm(realm).clients().get(clientUuid).getDefaultClientScopes();

        for (ClientScopeRepresentation scope : clientScopes) {
            monitor.debug("Client Scope Name: " + scope.getName());
        }

        return StatusResult.success(clientModel);
    }

    @Override
    public StatusResult<Void> addClient(String clientId) {
        ClientRepresentation client = new ClientRepresentation();
        client.setClientId(clientId);
        client.setEnabled(true);
        client.setName(clientId);

        // Enable Service Accounts
        client.setServiceAccountsEnabled(true);
        client.setStandardFlowEnabled(false);
        client.setImplicitFlowEnabled(false);
        client.setDirectAccessGrantsEnabled(false);
        client.setAuthorizationServicesEnabled(false);

        // Set the client's authentication type to Signed JWT (RS256)
        client.setClientAuthenticatorType("client-jwt");
        client.setAttributes(Collections.singletonMap("signatureAlgorithm", "RS256"));

        keycloakClient.realm(settings.getIdentityRealm()).clients().create(client);

        return StatusResult.success();
    }

    @Override
    public StatusResult<Void> updateClient(String clientId, Map<String, String> claims) {
        var realm = settings.getIdentityRealm();
        var clientInternalId = getInternalClientId(clientId);
        var clientResource = keycloakClient.realm(realm).clients().get(clientInternalId);
        var protocolMappers = clientResource.getProtocolMappers();

        createOrUpdate(protocolMappers, clientId, claims);

        return StatusResult.success();
    }

    @Override
    public StatusResult<Void> deleteClient(String clientId) {

        var realm = settings.getIdentityRealm();
        String clientInternalId = getInternalClientId(clientId);

        if (clientInternalId != null) {
            keycloakClient.realm(realm).clients().get(clientInternalId).remove();
        }

        return StatusResult.success();
    }

    private String getInternalClientId(String clientId) {
        var realm = settings.getIdentityRealm();
        List<ClientRepresentation> clients = keycloakClient.realm(realm).clients().findAll();

        String clientInternalId = clients.stream()
                .filter(c -> clientId.equals(c.getClientId()))
                .map(ClientRepresentation::getId)
                .findFirst()
                .orElse(null);
        return clientInternalId;
    }

    private void createOrUpdate(ProtocolMappersResource mappers, String clientId, Map<String, String> claims) {

        for (var claim : claims.entrySet()) {
            var claimId = claim.getKey();
            var claimValue = claim.getValue();

            var isExists = mappers.getMappers().stream().anyMatch(x -> x.getName().equals(claimId));

            if (isExists) {
                var updated = updateClaimValue(mappers, claimId, claimValue);
                mappers.update(updated.getId(), updated);
                monitor.info("Updated claim: "+claimId+" with value: "+claimValue);
            } else {
                var hardcodedClaim = getHardCodedMapper(claimId, claimValue);
                mappers.createMapper(hardcodedClaim);
                monitor.info("Created new claim: "+hardcodedClaim.getName());
            }
        }
    }

    private ProtocolMapperRepresentation getHardCodedMapper(String claimId, String claimValue) {
        ProtocolMapperRepresentation hardcodedClaimMapper = new ProtocolMapperRepresentation();
        hardcodedClaimMapper.setName(claimId);
        hardcodedClaimMapper.setProtocol("openid-connect");
        hardcodedClaimMapper.setProtocolMapper("oidc-hardcoded-claim-mapper");

        Map<String, String> config = new HashMap<>();
        config.put("claim.name", claimId);
        config.put("claim.value", claimValue);
        config.put("id.token.claim", "true");
        config.put("access.token.claim", "true");
        config.put("userinfo.token.claim", "true");
        hardcodedClaimMapper.setConfig(config);

        return hardcodedClaimMapper;
    }

    private ProtocolMapperRepresentation updateClaimValue(ProtocolMappersResource mappers, String claimId, String claimValue) {
        var mapper = mappers.getMappers().stream().filter(x -> x.getName().equals(claimId)).findFirst().orElseThrow();
        var config = mapper.getConfig();
        config.replace("claim.value", claimValue);
        mapper.setConfig(config);
        return mapper;
    }
}
