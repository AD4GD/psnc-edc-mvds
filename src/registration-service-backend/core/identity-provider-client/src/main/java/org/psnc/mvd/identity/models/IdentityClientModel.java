
package org.psnc.mvd.identity.models;

import java.util.Map;

public class IdentityClientModel {
    private String clientId;
    private Map<String, String> claims;


    public IdentityClientModel(String clientId, Map<String, String> claims) {
        this.clientId = clientId;
        this.claims = claims;
    }

    public String getClientId() {
        return clientId;
    }

    public Map<String, String> getClaims() {
        return claims;
    }
}
