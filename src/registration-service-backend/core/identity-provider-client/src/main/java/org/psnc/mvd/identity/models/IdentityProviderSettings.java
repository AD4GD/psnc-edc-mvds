
package org.psnc.mvd.identity.models;


public class IdentityProviderSettings {
    private String adminLogin;
    private String adminPassword;
    private String serverUrl;
    private String adminRealm;
    private String adminClientId;
    private String identityRealm;


    public IdentityProviderSettings(
        String adminLogin,
        String adminPassword,
        String serverUrl,
        String adminRealm,
        String adminClientId,
        String identityRealm
        ) {
        this.adminLogin = adminLogin;
        this.adminPassword = adminPassword;
        this.serverUrl = serverUrl;
        this.adminRealm = adminRealm;
        this.adminClientId = adminClientId;
        this.identityRealm = identityRealm;
    }

    public String getAdminLogin() {
        return adminLogin;
    }

    public String getAdminPassword() {
        return adminPassword;
    }

    public String getServerUrl() {
        return serverUrl;
    }

    public String getAdminRealm() {
        return adminRealm;
    }

    public String getAdminClientId() {
        return adminClientId;
    }

    public String getIdentityRealm() {
        return identityRealm;
    }
}
