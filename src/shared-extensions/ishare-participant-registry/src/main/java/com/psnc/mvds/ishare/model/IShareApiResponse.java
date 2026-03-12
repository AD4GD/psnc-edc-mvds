package com.psnc.mvds.ishare.model;

import com.fasterxml.jackson.databind.JsonNode;
import io.swagger.v3.oas.annotations.media.Schema;

/**
 * Generic model for iShare API responses
 */
@Schema(description = "Generic response from iShare Participant Registry API calls")
public class IShareApiResponse {
    
    @Schema(description = "HTTP status code", example = "200")
    private int statusCode;
    
    @Schema(description = "Raw response body")
    private String body;
    
    @Schema(description = "Parsed JSON response body")
    private JsonNode jsonBody;
    
    @Schema(description = "Whether the API call was successful", example = "true")
    private boolean success;
    
    @Schema(description = "Error message if the call failed")
    private String errorMessage;
    
    public IShareApiResponse() {
    }
    
    public IShareApiResponse(int statusCode, String body) {
        this.statusCode = statusCode;
        this.body = body;
        this.success = statusCode >= 200 && statusCode < 300;
    }
    
    public int getStatusCode() {
        return statusCode;
    }
    
    public void setStatusCode(int statusCode) {
        this.statusCode = statusCode;
        this.success = statusCode >= 200 && statusCode < 300;
    }
    
    public String getBody() {
        return body;
    }
    
    public void setBody(String body) {
        this.body = body;
    }
    
    public JsonNode getJsonBody() {
        return jsonBody;
    }
    
    public void setJsonBody(JsonNode jsonBody) {
        this.jsonBody = jsonBody;
    }
    
    public boolean isSuccess() {
        return success;
    }
    
    public void setSuccess(boolean success) {
        this.success = success;
    }
    
    public String getErrorMessage() {
        return errorMessage;
    }
    
    public void setErrorMessage(String errorMessage) {
        this.errorMessage = errorMessage;
    }
}
