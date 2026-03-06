package psnc.keycloak.admin.confirmation;

import org.keycloak.Config;
import org.keycloak.events.EventListenerProvider;
import org.keycloak.events.EventListenerProviderFactory;
import org.keycloak.models.KeycloakSession;
import org.keycloak.models.KeycloakSessionFactory;

public final class AdminApprovalEventListenerProviderFactory implements EventListenerProviderFactory {

    private boolean instanceEnabled;
    private String realmAttributeKey;

    @Override
    public EventListenerProvider create(KeycloakSession session) {
        return new AdminApprovalEventListenerProvider(session, instanceEnabled, realmAttributeKey);
    }

    @Override
    public void init(Config.Scope config) {
        // Instance-level toggle: set in keycloak.conf / env as provider config
        this.instanceEnabled = config.getBoolean("enabled", true);
        this.realmAttributeKey = config.get("realmAttributeKey", "adminApprovalEnabled");
    }

    @Override
    public void postInit(KeycloakSessionFactory factory) {}

    @Override
    public void close() {}

    @Override
    public String getId() {
        // This is what you add in Realm -> Events -> Config -> Event Listeners
        return "admin-approval";
    }
}