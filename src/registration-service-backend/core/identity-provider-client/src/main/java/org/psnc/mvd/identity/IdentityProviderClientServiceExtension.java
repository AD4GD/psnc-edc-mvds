
package org.psnc.mvd.identity;

import org.eclipse.edc.runtime.metamodel.annotation.Extension;
import org.eclipse.edc.runtime.metamodel.annotation.Inject;
import org.eclipse.edc.runtime.metamodel.annotation.Provider;
import org.eclipse.edc.runtime.metamodel.annotation.Setting;
import org.eclipse.edc.spi.EdcException;
import org.eclipse.edc.spi.monitor.Monitor;
import org.eclipse.edc.spi.system.ServiceExtension;
import org.eclipse.edc.spi.system.ServiceExtensionContext;

import org.psnc.mvd.identity.keycloak.KeycloakIdentityProviderClient;
import org.psnc.mvd.identity.models.IdentityProviderSettings;

import static java.lang.String.format;

@Extension(IdentityProviderClientServiceExtension.NAME)
public class IdentityProviderClientServiceExtension implements ServiceExtension {

    public static final String NAME = "Identity Provider Client Service";

    @Setting
    private static final String IDENTITYPROVIDER_ADMIN_LOGIN_NAME_SETTING = "psnc.identityprovider.admin.login";

    @Setting
    private static final String IDENTITYPROVIDER_ADMIN_PASSWORD_NAME_SETTING = "psnc.identityprovider.admin.password";

    @Setting
    private static final String IDENTITYPROVIDER_SERVER_URL_NAME_SETTING = "psnc.identityprovider.server.url";

    @Setting
    private static final String IDENTITYPROVIDER_ADMIN_REALM_NAME_SETTING = "psnc.identityprovider.admin.realm";

    @Setting
    private static final String IDENTITYPROVIDER_ADMIN_CLIENT_ID_NAME_SETTING = "psnc.identityprovider.admin.client.id";

    @Setting
    private static final String IDENTITYPROVIDER_IDENTITY_REALM_NAME_SETTING = "psnc.identityprovider.identity.realm";

    @Inject
    private Monitor monitor;

    @Override
    public String name() {
        return NAME;
    }

    @Provider
    public IdentityProviderClient identityProviderClient(ServiceExtensionContext context) {
        var adminLogin = context.getSetting(IDENTITYPROVIDER_ADMIN_LOGIN_NAME_SETTING, null);
        if (adminLogin == null) {
            throw new EdcException(format("The admin login '(%s)' was null!", IDENTITYPROVIDER_ADMIN_LOGIN_NAME_SETTING));
        }

        var adminPassword = context.getSetting(IDENTITYPROVIDER_ADMIN_PASSWORD_NAME_SETTING, null);
        if (adminPassword == null) {
            throw new EdcException(format("The admin password '(%s)' was null!", IDENTITYPROVIDER_ADMIN_PASSWORD_NAME_SETTING));
        }

        var serverUrl = context.getSetting(IDENTITYPROVIDER_SERVER_URL_NAME_SETTING, null);
        if (serverUrl == null) {
            throw new EdcException(format("The server url '(%s)' was null!", IDENTITYPROVIDER_SERVER_URL_NAME_SETTING));
        }

        var realm = context.getSetting(IDENTITYPROVIDER_ADMIN_REALM_NAME_SETTING, "master");
        var adminClient = context.getSetting(IDENTITYPROVIDER_ADMIN_CLIENT_ID_NAME_SETTING, "admin-cli");
        var identityRealm = context.getSetting(IDENTITYPROVIDER_IDENTITY_REALM_NAME_SETTING, "DAPS");

        var settings = new IdentityProviderSettings(
                adminLogin,
                adminPassword,
                serverUrl,
                realm,
                adminClient,
                identityRealm
        );

        return new KeycloakIdentityProviderClient(monitor, settings);
    }
}
