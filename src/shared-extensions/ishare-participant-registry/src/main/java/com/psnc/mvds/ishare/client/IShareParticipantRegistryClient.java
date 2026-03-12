package com.psnc.mvds.ishare.client;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.psnc.mvds.ishare.model.IShareApiResponse;
import com.psnc.mvds.ishare.service.IShareTokenService;
import okhttp3.OkHttpClient;
import okhttp3.Request;
import okhttp3.Response;
import org.eclipse.edc.spi.monitor.Monitor;
import org.eclipse.edc.spi.result.Result;

import java.util.HashMap;
import java.util.Map;

/**
 * Client for interacting with iShare Participant Registry endpoints
 */
public class IShareParticipantRegistryClient {
    
    private final String participantRegistryUrl;
    private final IShareTokenService tokenService;
    private final Monitor monitor;
    private final OkHttpClient httpClient;
    private final ObjectMapper objectMapper;
    
    public IShareParticipantRegistryClient(
            String participantRegistryUrl,
            IShareTokenService tokenService,
            Monitor monitor,
            OkHttpClient httpClient,
            ObjectMapper objectMapper) {
        
        this.participantRegistryUrl = participantRegistryUrl;
        this.tokenService = tokenService;
        this.monitor = monitor;
        this.httpClient = httpClient;
        this.objectMapper = objectMapper;
    }
    
    /**
     * Get parties from the Participant Registry
     * @see <a href="https://dev.ishare.eu/participant-registry-role/parties">iShare Parties API</a>
     */
    public Result<IShareApiResponse> getParties() {
        return getParties(new HashMap<>());
    }
    
    /**
     * Get parties from the Participant Registry with query parameters
     * @param queryParams Query parameters like eori_number, name, certificate_subject_name, etc.
     * @see <a href="https://dev.ishare.eu/participant-registry-role/parties">iShare Parties API</a>
     */
    public Result<IShareApiResponse> getParties(Map<String, String> queryParams) {
        monitor.info("Fetching parties from Participant Registry");
        return executeAuthenticatedGet("/parties", queryParams);
    }
    
    /**
     * Get a specific party by ID
     * @param partyId The party ID (e.g., EORI number)
     */
    public Result<IShareApiResponse> getParty(String partyId) {
        monitor.info("Fetching party: " + partyId);
        return executeAuthenticatedGet("/parties/" + partyId, new HashMap<>());
    }
    
    /**
     * Get trusted list from the Participant Registry
     * @see <a href="https://dev.ishare.eu/participant-registry-role/trusted-list">iShare Trusted List API</a>
     */
    public Result<IShareApiResponse> getTrustedList() {
        monitor.info("Fetching trusted list from Participant Registry");
        return executeAuthenticatedGet("/trusted_list", new HashMap<>());
    }
    
    /**
     * Get dataspaces from the Participant Registry
     * @see <a href="https://dev.ishare.eu/participant-registry-role/dataspaces">iShare Dataspaces API</a>
     */
    public Result<IShareApiResponse> getDataspaces() {
        return getDataspaces(new HashMap<>());
    }
    
    /**
     * Get dataspaces from the Participant Registry with query parameters
     * @param queryParams Query parameters like name, dataspace_id, etc.
     * @see <a href="https://dev.ishare.eu/participant-registry-role/dataspaces">iShare Dataspaces API</a>
     */
    public Result<IShareApiResponse> getDataspaces(Map<String, String> queryParams) {
        monitor.info("Fetching dataspaces from Participant Registry");
        return executeAuthenticatedGet("/dataspaces", queryParams);
    }
    
    /**
     * Get a specific dataspace by ID
     * @param dataspaceId The dataspace ID
     */
    public Result<IShareApiResponse> getDataspace(String dataspaceId) {
        monitor.info("Fetching dataspace: " + dataspaceId);
        return executeAuthenticatedGet("/dataspaces/" + dataspaceId, new HashMap<>());
    }
    
    /**
     * Get frameworks from the Participant Registry
     * @see <a href="https://dev.ishare.eu/participant-registry-role/frameworks">iShare Frameworks API</a>
     */
    public Result<IShareApiResponse> getFrameworks() {
        monitor.info("Fetching frameworks from Participant Registry");
        return executeAuthenticatedGet("/frameworks", new HashMap<>());
    }
    
    /**
     * Get a specific framework by ID
     * @param frameworkId The framework ID
     */
    public Result<IShareApiResponse> getFramework(String frameworkId) {
        monitor.info("Fetching framework: " + frameworkId);
        return executeAuthenticatedGet("/frameworks/" + frameworkId, new HashMap<>());
    }
    
    /**
     * Execute an authenticated GET request to the Participant Registry
     */
    private Result<IShareApiResponse> executeAuthenticatedGet(String path, Map<String, String> queryParams) {
        try {
            // Get access token
            var tokenResult = tokenService.getAccessToken();
            if (tokenResult.failed()) {
                return Result.failure("Failed to get access token: " + tokenResult.getFailureDetail());
            }
            String accessToken = tokenResult.getContent();
            
            // Build URL with query parameters
            StringBuilder urlBuilder = new StringBuilder(participantRegistryUrl + path);
            if (!queryParams.isEmpty()) {
                urlBuilder.append("?");
                boolean first = true;
                for (Map.Entry<String, String> entry : queryParams.entrySet()) {
                    if (!first) {
                        urlBuilder.append("&");
                    }
                    urlBuilder.append(entry.getKey()).append("=").append(entry.getValue());
                    first = false;
                }
            }
            String url = urlBuilder.toString();
            
            monitor.debug("Making request to: " + url);
            
            // Build request
            Request request = new Request.Builder()
                    .url(url)
                    .get()
                    .header("Authorization", "Bearer " + accessToken)
                    .header("Accept", "application/json")
                    .build();
            
            // Execute request
            try (Response response = httpClient.newCall(request).execute()) {
                String responseBody = response.body() != null ? response.body().string() : "";
                
                IShareApiResponse apiResponse = new IShareApiResponse(response.code(), responseBody);
                
                if (!response.isSuccessful()) {
                    String errorMsg = String.format("Request to %s failed with status %d: %s", 
                        path, response.code(), responseBody);
                    monitor.warning(errorMsg);
                    apiResponse.setErrorMessage(errorMsg);
                } else {
                    // Parse JSON body
                    try {
                        JsonNode jsonBody = objectMapper.readTree(responseBody);
                        apiResponse.setJsonBody(jsonBody);
                        monitor.info(String.format("Successfully fetched data from %s", path));
                    } catch (Exception e) {
                        monitor.warning("Failed to parse JSON response: " + e.getMessage());
                    }
                }
                
                return Result.success(apiResponse);
            }
            
        } catch (Exception e) {
            String errorMsg = String.format("Exception while calling %s: %s", path, e.getMessage());
            monitor.severe(errorMsg, e);
            return Result.failure(errorMsg);
        }
    }
}
