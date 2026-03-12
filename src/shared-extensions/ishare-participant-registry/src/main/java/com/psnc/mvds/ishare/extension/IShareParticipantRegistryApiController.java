package com.psnc.mvds.ishare.extension;

import com.psnc.mvds.ishare.client.IShareParticipantRegistryClient;
import com.psnc.mvds.ishare.model.IShareApiResponse;
import com.psnc.mvds.ishare.service.IShareTokenService;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.Parameter;
import io.swagger.v3.oas.annotations.media.Content;
import io.swagger.v3.oas.annotations.media.ExampleObject;
import io.swagger.v3.oas.annotations.media.Schema;
import io.swagger.v3.oas.annotations.responses.ApiResponse;
import io.swagger.v3.oas.annotations.responses.ApiResponses;
import io.swagger.v3.oas.annotations.tags.Tag;
import jakarta.ws.rs.*;
import jakarta.ws.rs.core.MediaType;
import jakarta.ws.rs.core.Response;
import org.eclipse.edc.spi.result.Result;

import java.util.HashMap;
import java.util.Map;

/**
 * REST API for iShare Participant Registry operations
 */
@Path("/ishare")
@Produces(MediaType.APPLICATION_JSON)
@Consumes(MediaType.APPLICATION_JSON)
@Tag(name = "iShare Participant Registry", 
     description = "API endpoints for interacting with iShare Participant Registry, including token management and resource queries")
public class IShareParticipantRegistryApiController {
    
    private final IShareTokenService tokenService;
    private final IShareParticipantRegistryClient prClient;
    
    public IShareParticipantRegistryApiController(
            IShareTokenService tokenService,
            IShareParticipantRegistryClient prClient) {
        this.tokenService = tokenService;
        this.prClient = prClient;
    }
    
    /**
     * Get or refresh access token
     */
    @GET
    @Path("/token")
    @Operation(
        summary = "Get access token",
        description = "Retrieves the current cached access token or fetches a new one if expired. " +
                      "Use refresh=true to force token refresh."
    )
    @ApiResponses({
        @ApiResponse(
            responseCode = "200",
            description = "Successfully retrieved or refreshed token",
            content = @Content(
                mediaType = MediaType.APPLICATION_JSON,
                schema = @Schema(implementation = TokenResponse.class),
                examples = @ExampleObject(value = "{\"success\":true,\"token\":\"eyJhbGc...\",\"hasValidToken\":true}")
            )
        ),
        @ApiResponse(
            responseCode = "500",
            description = "Failed to retrieve token",
            content = @Content(
                mediaType = MediaType.APPLICATION_JSON,
                examples = @ExampleObject(value = "{\"success\":false,\"error\":\"Failed to authenticate\"}")
            )
        )
    })
    public Response getToken(
            @Parameter(description = "Force refresh of the token", example = "false")
            @QueryParam("refresh") @DefaultValue("false") boolean refresh) {
        Result<String> result = refresh ? 
            tokenService.refreshAccessToken() : 
            tokenService.getAccessToken();
        
        if (result.succeeded()) {
            Map<String, Object> response = new HashMap<>();
            response.put("success", true);
            response.put("token", result.getContent());
            response.put("hasValidToken", tokenService.hasValidToken());
            return Response.ok(response).build();
        } else {
            Map<String, Object> response = new HashMap<>();
            response.put("success", false);
            response.put("error", result.getFailureDetail());
            return Response.status(Response.Status.INTERNAL_SERVER_ERROR)
                    .entity(response)
                    .build();
        }
    }
    
    /**
     * Check token status
     */
    @GET
    @Path("/token/status")
    @Operation(
        summary = "Check token status",
        description = "Returns whether a valid cached token is currently available"
    )
    @ApiResponses({
        @ApiResponse(
            responseCode = "200",
            description = "Token status retrieved",
            content = @Content(
                mediaType = MediaType.APPLICATION_JSON,
                examples = @ExampleObject(value = "{\"hasValidToken\":true}")
            )
        )
    })
    public Response getTokenStatus() {
        Map<String, Object> response = new HashMap<>();
        response.put("hasValidToken", tokenService.hasValidToken());
        return Response.ok(response).build();
    }

    /**
     * Generate signed client_assertion for manual debugging of /connect/token requests.
     */
    @GET
    @Path("/token/assertion")
    @Operation(
        summary = "Generate client assertion for debugging",
        description = "Generates a signed JWT client_assertion and returns token endpoint and form parameters. " +
                "Use only in development environments."
    )
    @ApiResponses({
        @ApiResponse(
            responseCode = "200",
            description = "Successfully generated client assertion",
            content = @Content(mediaType = MediaType.APPLICATION_JSON)
        ),
        @ApiResponse(
            responseCode = "500",
            description = "Failed to generate client assertion"
        )
    })
    public Response getTokenAssertion() {
        var assertionResult = tokenService.createClientAssertionForDebug();
        if (assertionResult.failed()) {
            Map<String, Object> response = new HashMap<>();
            response.put("success", false);
            response.put("error", assertionResult.getFailureDetail());
            return Response.status(Response.Status.INTERNAL_SERVER_ERROR)
                    .entity(response)
                    .build();
        }

        Map<String, Object> response = new HashMap<>();
        response.put("success", true);
        response.put("tokenEndpoint", tokenService.getTokenEndpoint());
        response.put("client_id", tokenService.getClientId());
        response.put("grant_type", "client_credentials");
        response.put("client_assertion_type", "urn:ietf:params:oauth:client-assertion-type:jwt-bearer");
        response.put("scope", "iSHARE");
        response.put("client_assertion", assertionResult.getContent());
        return Response.ok(response).build();
    }
    
    /**
     * Get parties from Participant Registry
     */
    @GET
    @Path("/parties")
    @Operation(
        summary = "Get parties",
        description = "Retrieves a list of registered parties (participants) from the Participant Registry. " +
                      "Results can be filtered using query parameters."
    )
    @ApiResponses({
        @ApiResponse(
            responseCode = "200",
            description = "Successfully retrieved parties",
            content = @Content(mediaType = MediaType.APPLICATION_JSON)
        ),
        @ApiResponse(
            responseCode = "500",
            description = "Failed to retrieve parties"
        )
    })
    public Response getParties(
            @Parameter(description = "Filter by EORI number", example = "EU.EORI.NL000000000")
            @QueryParam("eori_number") String eoriNumber,
            @Parameter(description = "Filter by party name", example = "Example Company")
            @QueryParam("name") String name,
            @Parameter(description = "Filter by certificate subject name")
            @QueryParam("certificate_subject_name") String certificateSubjectName) {
        
        Map<String, String> queryParams = new HashMap<>();
        if (eoriNumber != null) queryParams.put("eori_number", eoriNumber);
        if (name != null) queryParams.put("name", name);
        if (certificateSubjectName != null) queryParams.put("certificate_subject_name", certificateSubjectName);
        
        Result<IShareApiResponse> result = prClient.getParties(queryParams);
        return buildResponse(result);
    }
    
    /**
     * Get a specific party by ID
     */
    @GET
    @Path("/parties/{partyId}")
    @Operation(
        summary = "Get party by ID",
        description = "Retrieves detailed information about a specific party using its ID (typically EORI number)"
    )
    @ApiResponses({
        @ApiResponse(
            responseCode = "200",
            description = "Successfully retrieved party",
            content = @Content(mediaType = MediaType.APPLICATION_JSON)
        ),
        @ApiResponse(
            responseCode = "404",
            description = "Party not found"
        ),
        @ApiResponse(
            responseCode = "500",
            description = "Failed to retrieve party"
        )
    })
    public Response getParty(
            @Parameter(description = "The party ID (EORI number)", example = "EU.EORI.NL000000000", required = true)
            @PathParam("partyId") String partyId) {
        Result<IShareApiResponse> result = prClient.getParty(partyId);
        return buildResponse(result);
    }
    
    /**
     * Get trusted list from Participant Registry
     */
    @GET
    @Path("/trusted_list")
    @Operation(
        summary = "Get trusted list",
        description = "Retrieves the list of trusted certificate authorities and certificates from the Participant Registry"
    )
    @ApiResponses({
        @ApiResponse(
            responseCode = "200",
            description = "Successfully retrieved trusted list",
            content = @Content(mediaType = MediaType.APPLICATION_JSON)
        ),
        @ApiResponse(
            responseCode = "500",
            description = "Failed to retrieve trusted list"
        )
    })
    public Response getTrustedList() {
        Result<IShareApiResponse> result = prClient.getTrustedList();
        return buildResponse(result);
    }
    
    /**
     * Get dataspaces from Participant Registry
     */
    @GET
    @Path("/dataspaces")
    @Operation(
        summary = "Get dataspaces",
        description = "Retrieves a list of registered dataspaces from the Participant Registry. " +
                      "Results can be filtered using query parameters."
    )
    @ApiResponses({
        @ApiResponse(
            responseCode = "200",
            description = "Successfully retrieved dataspaces",
            content = @Content(mediaType = MediaType.APPLICATION_JSON)
        ),
        @ApiResponse(
            responseCode = "500",
            description = "Failed to retrieve dataspaces"
        )
    })
    public Response getDataspaces(
            @Parameter(description = "Filter by dataspace name", example = "Example Dataspace")
            @QueryParam("name") String name,
            @Parameter(description = "Filter by dataspace ID", example = "DATASPACE123")
            @QueryParam("dataspace_id") String dataspaceId) {
        
        Map<String, String> queryParams = new HashMap<>();
        if (name != null) queryParams.put("name", name);
        if (dataspaceId != null) queryParams.put("dataspace_id", dataspaceId);
        
        Result<IShareApiResponse> result = prClient.getDataspaces(queryParams);
        return buildResponse(result);
    }
    
    /**
     * Get a specific dataspace by ID
     */
    @GET
    @Path("/dataspaces/{dataspaceId}")
    @Operation(
        summary = "Get dataspace by ID",
        description = "Retrieves detailed information about a specific dataspace using its ID"
    )
    @ApiResponses({
        @ApiResponse(
            responseCode = "200",
            description = "Successfully retrieved dataspace",
            content = @Content(mediaType = MediaType.APPLICATION_JSON)
        ),
        @ApiResponse(
            responseCode = "404",
            description = "Dataspace not found"
        ),
        @ApiResponse(
            responseCode = "500",
            description = "Failed to retrieve dataspace"
        )
    })
    public Response getDataspace(
            @Parameter(description = "The dataspace ID", example = "DATASPACE123", required = true)
            @PathParam("dataspaceId") String dataspaceId) {
        Result<IShareApiResponse> result = prClient.getDataspace(dataspaceId);
        return buildResponse(result);
    }
    
    /**
     * Get frameworks from Participant Registry
     */
    @GET
    @Path("/frameworks")
    @Operation(
        summary = "Get frameworks",
        description = "Retrieves a list of data sharing frameworks registered in the Participant Registry"
    )
    @ApiResponses({
        @ApiResponse(
            responseCode = "200",
            description = "Successfully retrieved frameworks",
            content = @Content(mediaType = MediaType.APPLICATION_JSON)
        ),
        @ApiResponse(
            responseCode = "500",
            description = "Failed to retrieve frameworks"
        )
    })
    public Response getFrameworks() {
        Result<IShareApiResponse> result = prClient.getFrameworks();
        return buildResponse(result);
    }
    
    /**
     * Get a specific framework by ID
     */
    @GET
    @Path("/frameworks/{frameworkId}")
    @Operation(
        summary = "Get framework by ID",
        description = "Retrieves detailed information about a specific data sharing framework using its ID"
    )
    @ApiResponses({
        @ApiResponse(
            responseCode = "200",
            description = "Successfully retrieved framework",
            content = @Content(mediaType = MediaType.APPLICATION_JSON)
        ),
        @ApiResponse(
            responseCode = "404",
            description = "Framework not found"
        ),
        @ApiResponse(
            responseCode = "500",
            description = "Failed to retrieve framework"
        )
    })
    public Response getFramework(
            @Parameter(description = "The framework ID", example = "iSHARE", required = true)
            @PathParam("frameworkId") String frameworkId) {
        Result<IShareApiResponse> result = prClient.getFramework(frameworkId);
        return buildResponse(result);
    }
    
    /**
     * Helper method to build HTTP response from API result
     */
    private Response buildResponse(Result<IShareApiResponse> result) {
        if (result.failed()) {
            Map<String, Object> response = new HashMap<>();
            response.put("success", false);
            response.put("error", result.getFailureDetail());
            return Response.status(Response.Status.INTERNAL_SERVER_ERROR)
                    .entity(response)
                    .build();
        }
        
        IShareApiResponse apiResponse = result.getContent();
        
        if (!apiResponse.isSuccess()) {
            Map<String, Object> response = new HashMap<>();
            response.put("success", false);
            response.put("statusCode", apiResponse.getStatusCode());
            response.put("error", apiResponse.getErrorMessage());
            response.put("body", apiResponse.getBody());
            return Response.status(apiResponse.getStatusCode())
                    .entity(response)
                    .build();
        }
        
        // Return the JSON body directly if available
        if (apiResponse.getJsonBody() != null) {
            return Response.ok(apiResponse.getJsonBody()).build();
        } else {
            return Response.ok(apiResponse.getBody()).build();
        }
    }
    
    /**
     * Schema class for OpenAPI documentation - Token response
     */
    @Schema(description = "Response containing access token information")
    public static class TokenResponse {
        @Schema(description = "Whether the operation was successful", example = "true")
        public boolean success;
        
        @Schema(description = "The access token (JWT)", example = "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9...")
        public String token;
        
        @Schema(description = "Whether a valid cached token exists", example = "true")
        public boolean hasValidToken;
    }
}
