package com.psnc.mvds.ishare.model;

import com.fasterxml.jackson.annotation.JsonProperty;
import io.swagger.v3.oas.annotations.media.Schema;

/**
 * Model for iShare OAuth2 token response
 */
@Schema(description = "OAuth2 token response from iShare Participant Registry")
public class IShareTokenResponse {
    
    @JsonProperty("access_token")
    @Schema(description = "The access token (JWT)", example = "eyJhbGciOiJSUzI1NiIs...")
    private String accessToken;
    
    @JsonProperty("token_type")
    @Schema(description = "Token type", example = "Bearer")
    private String tokenType;
    
    @JsonProperty("expires_in")
    @Schema(description = "Token validity duration in seconds", example = "3600")
    private long expiresIn;
    
    @Schema(description = "Timestamp when token was received (milliseconds)", example = "1709654400000")
    private long receivedAt;
    
    public IShareTokenResponse() {
        this.receivedAt = System.currentTimeMillis();
    }
    
    public String getAccessToken() {
        return accessToken;
    }
    
    public void setAccessToken(String accessToken) {
        this.accessToken = accessToken;
    }
    
    public String getTokenType() {
        return tokenType;
    }
    
    public void setTokenType(String tokenType) {
        this.tokenType = tokenType;
    }
    
    public long getExpiresIn() {
        return expiresIn;
    }
    
    public void setExpiresIn(long expiresIn) {
        this.expiresIn = expiresIn;
    }
    
    public long getReceivedAt() {
        return receivedAt;
    }
    
    public void setReceivedAt(long receivedAt) {
        this.receivedAt = receivedAt;
    }
    
    /**
     * Check if the token is still valid (with 60 second buffer)
     */
    public boolean isValid() {
        long now = System.currentTimeMillis();
        long validUntil = receivedAt + (expiresIn * 1000) - 60000; // 60 second buffer
        return now < validUntil;
    }
    
    /**
     * Get remaining validity time in seconds
     */
    public long getRemainingValiditySeconds() {
        long now = System.currentTimeMillis();
        long validUntil = receivedAt + (expiresIn * 1000);
        return Math.max(0, (validUntil - now) / 1000);
    }
}
