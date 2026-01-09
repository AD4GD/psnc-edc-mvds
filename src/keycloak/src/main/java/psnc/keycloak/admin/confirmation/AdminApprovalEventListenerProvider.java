package psnc.keycloak.admin.confirmation;

import org.jboss.logging.Logger;
import org.keycloak.events.Event;
import org.keycloak.events.EventListenerProvider;
import org.keycloak.events.EventType;
import org.keycloak.events.admin.AdminEvent;
import org.keycloak.models.GroupModel;
import org.keycloak.models.KeycloakSession;
import org.keycloak.models.RealmModel;
import org.keycloak.models.UserModel;

public final class AdminApprovalEventListenerProvider implements EventListenerProvider {
    private static final Logger LOG = Logger.getLogger(AdminApprovalEventListenerProvider.class);

    private static final String PENDING_GROUP_NAME = "pending-approval";
    private static final String APPROVAL_ATTR = "approvalStatus";
    private static final String STATUS_PENDING = "pending";
    private static final String STATUS_APPROVED = "approved";

    private final KeycloakSession session;
    private final boolean instanceEnabled;
    private final String realmAttributeKey;

    public AdminApprovalEventListenerProvider(KeycloakSession session,
                                              boolean instanceEnabled,
                                              String realmAttributeKey) {
        this.session = session;
        this.instanceEnabled = instanceEnabled;
        this.realmAttributeKey = realmAttributeKey;
    }

    @Override
    public void onEvent(Event event) {
        // Log once, but do not spam for every event type in production
        LOG.debugf("ADMIN-APPROVAL EVENT: type=%s realmId=%s userId=%s clientId=%s ip=%s",
                event.getType(), event.getRealmId(), event.getUserId(), event.getClientId(), event.getIpAddress());

        if (event.getType() != EventType.REGISTER && event.getType() != EventType.VERIFY_EMAIL) {
            return;
        }

        RealmModel realm = session.realms().getRealm(event.getRealmId());
        if (realm == null) {
            LOG.warnf("ADMIN-APPROVAL: realm not found for realmId=%s", event.getRealmId());
            return;
        }

        if (!isEnabledForRealm(realm)) {
            LOG.debugf("ADMIN-APPROVAL: disabled for realm=%s (%s)", realm.getName(), realm.getId());
            return;
        }

        String userId = event.getUserId();
        if (userId == null || userId.isBlank()) {
            LOG.warnf("ADMIN-APPROVAL: event userId is null/blank. type=%s details=%s",
                    event.getType(), event.getDetails());
            return;
        }

        UserModel user = session.users().getUserById(realm, userId);
        if (user == null) {
            LOG.warnf("ADMIN-APPROVAL: user not found by id=%s in realm=%s (%s). type=%s details=%s",
                    userId, realm.getName(), realm.getId(), event.getType(), event.getDetails());
            return;
        }

        if (event.getType() == EventType.REGISTER) {
            handleRegister(realm, user);
            return;
        }

        if (event.getType() == EventType.VERIFY_EMAIL) {
            handleVerifyEmail(realm, user);
        }
    }

    private void handleRegister(RealmModel realm, UserModel user) {
        // IMPORTANT: keep enabled so email verification can complete
        user.setSingleAttribute(APPROVAL_ATTR, STATUS_PENDING);

        GroupModel pendingGroup = findGroup(realm, PENDING_GROUP_NAME);
        if (pendingGroup != null) {
            user.joinGroup(pendingGroup);
        } else {
            LOG.warnf("ADMIN-APPROVAL: group '%s' not found in realm=%s", PENDING_GROUP_NAME, realm.getName());
        }

        LOG.infof("User %s (%s) registered; marked pending approval in realm %s (enabled=%s emailVerified=%s)",
                user.getUsername(), user.getId(), realm.getName(), user.isEnabled(), user.isEmailVerified());
    }

    private void handleVerifyEmail(RealmModel realm, UserModel user) {
        // Only apply to users that are actually pending approval
        boolean isPending = STATUS_PENDING.equals(user.getFirstAttribute(APPROVAL_ATTR));
        boolean emailVerified = user.isEmailVerified();
        boolean enabled = user.isEnabled();

        if (!emailVerified) {
            // Defensive: VERIFY_EMAIL should imply this, but keep it explicit.
            LOG.warnf("ADMIN-APPROVAL: VERIFY_EMAIL event but user.isEmailVerified=false for user=%s (%s)",
                    user.getUsername(), user.getId());
            return;
        }

        if (!isPending) {
            // Avoid disabling users that are already approved or not part of this workflow
            LOG.debugf("ADMIN-APPROVAL: user %s (%s) VERIFY_EMAIL ignored (approvalStatus=%s)",
                    user.getUsername(), user.getId(), user.getFirstAttribute(APPROVAL_ATTR));
            return;
        }

        if (!enabled) {
            LOG.debugf("ADMIN-APPROVAL: user %s (%s) already disabled; nothing to do",
                    user.getUsername(), user.getId());
            return;
        }

        // Disable after successful email verification
        user.setEnabled(false);

        LOG.infof("User %s (%s) verified email and is now disabled awaiting admin approval in realm %s",
                user.getUsername(), user.getId(), realm.getName());
    }

    private GroupModel findGroup(RealmModel realm, String name) {
        return realm.getGroupsStream()
                .filter(g -> name.equals(g.getName()))
                .findFirst()
                .orElse(null);
    }

    @Override
    public void onEvent(AdminEvent adminEvent, boolean includeRepresentation) {
        // You can implement approval here (admin enables user + moves groups) if desired.
        // For now, still no-op.
    }

    private boolean isEnabledForRealm(RealmModel realm) {
        boolean enabled = instanceEnabled;
        String v = realm.getAttribute(realmAttributeKey);
        if (v != null) enabled = Boolean.parseBoolean(v);
        return enabled;
    }

    @Override
    public void close() {}
}
