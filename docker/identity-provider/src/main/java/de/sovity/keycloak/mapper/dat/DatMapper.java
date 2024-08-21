/*
 *   Copyright 2024 sovity GmbH
 *
 *   Licensed under the Apache License, Version 2.0 (the "License");
 *   you may not use this file except in compliance with the License.
 *   You may obtain a copy of the License at
 *
 *       http://www.apache.org/licenses/LICENSE-2.0
 *
 *   Unless required by applicable law or agreed to in writing, software
 *   distributed under the License is distributed on an "AS IS" BASIS,
 *   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 *   See the License for the specific language governing permissions and
 *   limitations under the License.
 *
 *   SPDX-License-Identifier: Apache-2.0
 *
 */

package de.sovity.keycloak.mapper.dat;

import org.keycloak.models.ClientSessionContext;
import org.keycloak.models.KeycloakSession;
import org.keycloak.models.ProtocolMapperModel;
import org.keycloak.models.UserSessionModel;
import org.keycloak.protocol.oidc.mappers.AbstractOIDCProtocolMapper;
import org.keycloak.protocol.oidc.mappers.OIDCAccessTokenMapper;
import org.keycloak.protocol.oidc.mappers.OIDCAttributeMapperHelper;
import org.keycloak.provider.ProviderConfigProperty;
import org.keycloak.representations.AccessToken;

import java.util.ArrayList;
import java.util.Arrays;
import java.util.List;
import java.util.stream.Collectors;

public class DatMapper extends AbstractOIDCProtocolMapper implements OIDCAccessTokenMapper {

    /*
     * A config which keycloak uses to display a generic dialog to configure the token.
     */
    private static final List<ProviderConfigProperty> configProperties = new ArrayList<>();

    /*
     * The ID of the token mapper. Is public, because we need this id in our data-setup project to
     * configure the protocol mapper in keycloak.
     */
    public static final String PROVIDER_ID = "dat-mapper";

    public static final String SUBJECT_CLAIM = "subject-claim";
    public static final String AUDIENCE_CLAIM = "audience-claim";
    private static final String DEFAULT_AUDIENCE = "idsc:IDS_CONNECTORS_ALL";

    private static final String SCOPE_CLAIM = "scope-claim";
    private static final String DEFAULT_SCOPE = "idsc:IDS_CONNECTOR_ATTRIBUTES_ALL";


    private static final Object DEFAULT_SECURITY_PROFILE = "idsc:BASE_SECURITY_PROFILE";

    private static final String SECURITY_PROFILE_CLAIM = "security-profile-claim";

    private static final String REFERRING_CONNECTOR_CLAIM = "referring-connector-claim";

    private static final String TRANSPORT_CERTS_CLAIM = "transport-certs-claim";

    private static final String EXTENDED_GUARANTEE_CLAIM = "extended-guarantee-claim";

    static {
        OIDCAttributeMapperHelper.addTokenClaimNameConfig(configProperties);

        ProviderConfigProperty subjectProperty = new ProviderConfigProperty();
        subjectProperty.setName(SUBJECT_CLAIM);
        subjectProperty.setLabel("Subject");
        subjectProperty.setType(ProviderConfigProperty.STRING_TYPE);
        subjectProperty.setHelpText("Defaults to keycloak-client-id. Subject the requesting connector the token is created for. This is the connector requesting the DAT. The sub value must be the combined entry of the SKI and AKI of the IDS X509 as presented in Sec. 4.2.1. In this context, this is identical to iss.");
        configProperties.add(subjectProperty);

        ProviderConfigProperty audienceProperty = new ProviderConfigProperty();
        audienceProperty.setName(AUDIENCE_CLAIM);
        audienceProperty.setLabel("Audience");
        audienceProperty.setType(ProviderConfigProperty.STRING_TYPE);
        audienceProperty.setDefaultValue(DEFAULT_AUDIENCE);
        audienceProperty.setHelpText("Defaults to " + DEFAULT_AUDIENCE + ". The audience of the token. This can limit the validity for certain connectors.");
        configProperties.add(audienceProperty);

        ProviderConfigProperty scopeProperty = new ProviderConfigProperty();
        scopeProperty.setName(SCOPE_CLAIM);
        scopeProperty.setLabel("Scope");
        scopeProperty.setType(ProviderConfigProperty.STRING_TYPE);
        scopeProperty.setDefaultValue(DEFAULT_SCOPE);
        scopeProperty.setHelpText("Defaults to " + DEFAULT_SCOPE + ". List of scopes. Currently, the scope is limited to \"ids_connector_attributes\" but can be used for scoping purposes in the future.");
        configProperties.add(scopeProperty);

        ProviderConfigProperty securityProfileProperty = new ProviderConfigProperty();
        securityProfileProperty.setName(SECURITY_PROFILE_CLAIM);
        securityProfileProperty.setLabel("securityProfile");
        securityProfileProperty.setType(ProviderConfigProperty.STRING_TYPE);
        securityProfileProperty.setDefaultValue(DEFAULT_SECURITY_PROFILE);
        securityProfileProperty.setHelpText("Defaults to " + DEFAULT_SECURITY_PROFILE + ". States that the requesting connector conforms to a certain security profile and has been certified to do so. The value must be an URI, in particular an instance of the ids:SecurityProfile class.");
        configProperties.add(securityProfileProperty);

        ProviderConfigProperty referringConnectorProperty = new ProviderConfigProperty();
        referringConnectorProperty.setName(REFERRING_CONNECTOR_CLAIM);
        referringConnectorProperty.setLabel("referringConnector");
        referringConnectorProperty.setType(ProviderConfigProperty.STRING_TYPE);
        referringConnectorProperty.setHelpText("(OPTIONAL) The URI of the subject, the connector represented by the DAT. Is used to connect identifier of the connector with the self-description identifier as defined by the IDS Information Model. A receiving connector can use this information to request more information at a Broker or directly by dereferencing this URI.");
        configProperties.add(referringConnectorProperty);

        ProviderConfigProperty transportCertsSha256Property = new ProviderConfigProperty();
        transportCertsSha256Property.setName(TRANSPORT_CERTS_CLAIM);
        transportCertsSha256Property.setLabel("transportCertsSha256");
        transportCertsSha256Property.setType(ProviderConfigProperty.STRING_TYPE);
        transportCertsSha256Property.setHelpText("(OPTIONAL) Contains the public keys of the used transport certificates. The identifying X509 certificate should not be used for the communication encryption. Therefore, the receiving party needs to connect the identity of a connector by relating its hostname (from the communication encryption layer) and the used private/public key pair, with its IDS identity claim of the DAT. The public transportation key must be one of the \"transportCertsSha256\" values. Otherwise, the receiving connector must expect that the requesting connector is using a false identity claim.");
        configProperties.add(transportCertsSha256Property);

        ProviderConfigProperty extendedGuaranteeProperty = new ProviderConfigProperty();
        extendedGuaranteeProperty.setName(EXTENDED_GUARANTEE_CLAIM);
        extendedGuaranteeProperty.setLabel("extendedGuarantee");
        extendedGuaranteeProperty.setType(ProviderConfigProperty.STRING_TYPE);
        extendedGuaranteeProperty.setHelpText("(OPTIONAL) In case a connector fulfills a certain security profile but deviates for a subset of attributes, it can inform the receiving connector about its actual security features. This can only happen if a connector reaches a higher level for a certain security attribute than the actual reached certification asks for. A deviation to lower levels is not possible, as this would directly invalidate the complete certification level.");
        configProperties.add(extendedGuaranteeProperty);

        OIDCAttributeMapperHelper.addIncludeInTokensConfig(configProperties, DatMapper.class);
    }

    public String getDisplayCategory() {
        return "Token mapper";
    }

    public String getDisplayType() {
        return "DAT Mapper";
    }

    public String getHelpText() {
        return "Ensures all claims required by the IDS-G specification of a DAT are set";
    }

    public List<ProviderConfigProperty> getConfigProperties() {
        return configProperties;
    }

    public String getId() {
        return PROVIDER_ID;
    }

    @Override
    public AccessToken transformAccessToken(AccessToken token, ProtocolMapperModel mappingModel, KeycloakSession session, UserSessionModel userSession, ClientSessionContext clientSessionCtx) {
        // Delete unnecessary azp and typ oidc claims
        token.issuedFor(null);
        token.type(null);

        token.getOtherClaims().put("@context", "https://w3id.org/idsa/contexts/context.jsonld");
        token.getOtherClaims().put("@type", "ids:DatPayload");

        String subjectClaimValue = mappingModel.getConfig().get(SUBJECT_CLAIM);
        if (subjectClaimValue == null) {
            // NB: Client ID is not the Keycloak ID, which is a UUID. Rather, it is the "name" of the client.
            subjectClaimValue = clientSessionCtx.getClientSession().getClient().getClientId();
        }
        token.setSubject(subjectClaimValue);

        String audienceClaimValue = mappingModel.getConfig().get(AUDIENCE_CLAIM);
        if (audienceClaimValue != null) {
            token.audience(audienceClaimValue);
        }

        String scopeClaimValue = mappingModel.getConfig().get(SCOPE_CLAIM);
        if (scopeClaimValue != null) {
            token.setScope(scopeClaimValue);
        }

        token.getOtherClaims().put("securityProfile", mappingModel.getConfig().get(SECURITY_PROFILE_CLAIM));

        String referringConnectorClaimValue = mappingModel.getConfig().get(REFERRING_CONNECTOR_CLAIM);
        if (referringConnectorClaimValue != null) {
            token.getOtherClaims().put("referringConnector", referringConnectorClaimValue);
        }

        String transportCertsSha256ClaimValue = mappingModel.getConfig().get(TRANSPORT_CERTS_CLAIM);
        if (transportCertsSha256ClaimValue != null) {
            List<String> transportCertsSha256ValueList = Arrays.stream(transportCertsSha256ClaimValue.split(",")).collect(Collectors.toList());
            token.getOtherClaims().put("transportCertsSha256", transportCertsSha256ValueList);
        }

        String extendedGuaranteeClaimValue = mappingModel.getConfig().get(EXTENDED_GUARANTEE_CLAIM);
        if (extendedGuaranteeClaimValue != null) {
            List<String> extendedGuaranteeValueList = Arrays.stream(extendedGuaranteeClaimValue.split(",")).collect(Collectors.toList());
            token.getOtherClaims().put("extendedGuaranteeClaimValue", extendedGuaranteeValueList);
        }

        Long iat = token.getIat();
        token.nbf(iat);

        return token;
    }
}
