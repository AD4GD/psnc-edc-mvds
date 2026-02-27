package pl.psnc.edc.extension.catalogproxy.controller;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.databind.node.ObjectNode;
import jakarta.ws.rs.Consumes;
import jakarta.ws.rs.HeaderParam;
import jakarta.ws.rs.POST;
import jakarta.ws.rs.Path;
import jakarta.ws.rs.Produces;
import jakarta.ws.rs.QueryParam;
import jakarta.ws.rs.container.AsyncResponse;
import jakarta.ws.rs.container.Suspended;
import jakarta.ws.rs.core.MediaType;
import jakarta.ws.rs.core.Response;
import org.eclipse.edc.connector.controlplane.catalog.spi.CatalogRequestMessage;
import org.eclipse.edc.spi.message.RemoteMessageDispatcherRegistry;
import org.eclipse.edc.spi.monitor.Monitor;
import org.eclipse.edc.spi.query.QuerySpec;
import org.eclipse.edc.spi.response.StatusResult;
import org.eclipse.edc.spi.system.configuration.Config;

import java.net.URI;
import java.net.http.HttpClient;
import java.net.http.HttpRequest;
import java.net.http.HttpResponse;
import java.nio.charset.StandardCharsets;
import java.time.Duration;
import java.util.concurrent.CompletableFuture;
import java.util.concurrent.TimeUnit;

@Path("/catalog")
public class CatalogProxyController {

    private final Monitor monitor;
    private final Config config;
    private final ObjectMapper mapper;
    private final HttpClient httpClient;

    private final RemoteMessageDispatcherRegistry dispatcherRegistry;

    private final String dspCounterPartyAddress;
    private final String dspCounterPartyId;
    private final String dspProtocol;

    private final String httpTargetUrl;
    private final String httpApiKeyHeader;
    private final String httpApiKey;

    private final boolean dspEnabled;

    public CatalogProxyController(
        Monitor monitor,
        RemoteMessageDispatcherRegistry dispatcherRegistry,
        Config config,
        ObjectMapper mapper)
    {
        this.monitor = monitor;
        this.config = config;
        this.dispatcherRegistry = dispatcherRegistry;
        this.mapper = mapper;

        // DSP support (disabled by default; Federated Catalog 0.10 DSP doesn't return aggregated catalog)
        this.dspEnabled = config.getBoolean("edc.catalog.proxy.dsp.enabled", false);

        // DSP-first target (Federated Catalog protocol endpoint)
        this.dspCounterPartyAddress = config.getString(
            "edc.catalog.proxy.dsp.counterparty.address",
            "http://federated-catalog:8182/protocol"
        );
        this.dspCounterPartyId = config.getString(
            "edc.catalog.proxy.dsp.counterparty.id",
            "federated-catalog"
        );
        this.dspProtocol = config.getString(
            "edc.catalog.proxy.dsp.protocol",
            "dataspace-protocol-http"
        );

        // HTTP fallback target (Federated Catalog REST API)
        this.httpTargetUrl = config.getString(
            "edc.catalog.proxy.http.target.url",
            "http://federated-catalog:8181/catalog/v1alpha/catalog/query"
        );
        this.httpApiKeyHeader = config.getString(
            "edc.catalog.proxy.http.apikey.header",
            "x-api-key"
        );
        this.httpApiKey = config.getString(
            "edc.catalog.proxy.http.apikey",
            "edc"
        );

        this.httpClient = HttpClient.newBuilder()
        .connectTimeout(Duration.ofSeconds(10))
        .build();
    }

    @POST
    @Path("/request")
    @Consumes(MediaType.APPLICATION_JSON)
    @Produces(MediaType.APPLICATION_JSON)
    public void getCatalog(
        @HeaderParam("Authorization") String token,
        @QueryParam("providerUrl") String providerUrl,
        String body,
        @Suspended AsyncResponse responseSuspended)
    {
        // Auth is handled by the web context (composite: tokenbased + delegated).

        // DSP is disabled by default (FC 0.10 doesn't return aggregated catalog via DSP).
        // To enable DSP-first flow, set edc.catalog.proxy.dsp.enabled=true in config.
        if (!dspEnabled) {
            monitor.info("DSP is disabled; using HTTP fallback directly.");
            fetchViaHttp(providerUrl, body, responseSuspended);
            return;
        }

        // === DSP-first flow (disabled by default) ===
        {/** We leave it right now and cope with this when updating edc version to latest because in 0.10 FC doesn't support fetching catalog through DSP */}

        // 1) Try DSP first (connector-to-federated-catalog)
        var querySpec = parseQuerySpec(body);
        var dspAddress = (providerUrl != null && !providerUrl.isBlank()) ? providerUrl : dspCounterPartyAddress;

        monitor.info("Proxying catalog request via DSP to: " + dspAddress);

        var dspMessageBuilder = CatalogRequestMessage.Builder.newInstance()
            .protocol(dspProtocol)
            .counterPartyAddress(dspAddress)
            .querySpec(querySpec);

        if (dspCounterPartyId != null && !dspCounterPartyId.isBlank()) {
            dspMessageBuilder.counterPartyId(dspCounterPartyId);
        }

        var dspMessage = dspMessageBuilder.build();

        // DSP catalog dispatcher returns raw JSON as byte[]; dispatching as Catalog.class causes ClassCastException ([B -> Catalog).
        CompletableFuture<StatusResult<byte[]>> dspFuture = dispatcherRegistry.dispatch(byte[].class, dspMessage);

        dspFuture.orTimeout(30, TimeUnit.SECONDS).whenComplete((catalogResult, throwable) -> {
            if (throwable == null && catalogResult != null && catalogResult.succeeded()) {
                var bytes = catalogResult.getContent();
                var jsonPayload = bytes != null ? new String(bytes, StandardCharsets.UTF_8) : null;
                if (jsonPayload != null && !jsonPayload.isBlank()) {
                    // If FC (0.10) answers via /protocol, it may return only a self-description catalog.
                    // In that case, fall back to FC REST /catalog/.../query to obtain the aggregated catalog.
                    if (providerUrl == null || providerUrl.isBlank()) {
                        try {
                            var json = mapper.readTree(jsonPayload);
                            if (looksLikeFederatedCatalogSelfDescription(json)) {
                                monitor.info("DSP returned Federated Catalog self-description; falling back to HTTP /catalog query.");
                            } else {
                                responseSuspended.resume(Response.ok(jsonPayload, MediaType.APPLICATION_JSON).build());
                                return;
                            }
                        } catch (Exception e) {
                            // If payload isn't parseable JSON, return it rather than risk masking a real response.
                            monitor.warning("Failed to inspect DSP catalog payload; returning as-is. Reason: " + e.getMessage());
                            responseSuspended.resume(Response.ok(jsonPayload, MediaType.APPLICATION_JSON).build());
                            return;
                        }
                    } else {
                        // providerUrl explicitly set -> treat as single target and return DSP payload as-is.
                        responseSuspended.resume(Response.ok(jsonPayload, MediaType.APPLICATION_JSON).build());
                        return;
                    }
                }

                monitor.warning("DSP catalog fetch returned empty payload; falling back to HTTP.");
            }

            var failureDetail = throwable != null
                ? throwable.toString()
                : (catalogResult != null ? catalogResult.getFailureDetail() : "null result");
            monitor.warning("DSP catalog fetch failed, falling back to HTTP. Reason: " + failureDetail);

            // 2) Fallback to HTTP (tokenbased x-api-key)
            fetchViaHttp(providerUrl, body, responseSuspended);
        });
    }

    private void fetchViaHttp(String providerUrl, String body, AsyncResponse responseSuspended) {
        var httpUrl = (providerUrl != null && !providerUrl.isBlank()) ? providerUrl : httpTargetUrl;
        monitor.info("Proxying catalog request via HTTP to: " + httpUrl);

        var outgoingBody = normalizeQuerySpecForRest(body);
        var httpRequestBuilder = HttpRequest.newBuilder()
            .uri(URI.create(httpUrl))
            .timeout(Duration.ofSeconds(30))
            .header("Content-Type", MediaType.APPLICATION_JSON)
            .header("Accept", MediaType.APPLICATION_JSON)
            .POST(HttpRequest.BodyPublishers.ofString(outgoingBody));

        if (httpApiKey != null && !httpApiKey.isBlank()) {
            httpRequestBuilder.header(httpApiKeyHeader, httpApiKey);
        }

        httpClient.sendAsync(httpRequestBuilder.build(), HttpResponse.BodyHandlers.ofString())
        .whenComplete((httpResponse, httpThrowable) -> {
            if (httpThrowable != null) {
                monitor.severe("Error proxying catalog request (HTTP fallback)", httpThrowable);
                responseSuspended.resume(Response.status(Response.Status.BAD_GATEWAY)
                    .entity("Error fetching catalog: " + httpThrowable.getMessage())
                    .build());
                return;
            }

            if (httpResponse == null) {
                responseSuspended.resume(Response.status(Response.Status.BAD_GATEWAY)
                    .entity("Error fetching catalog: empty response")
                    .build());
                return;
            }

            var contentType = httpResponse.headers().firstValue("content-type").orElse(MediaType.APPLICATION_JSON);
            responseSuspended.resume(Response.status(httpResponse.statusCode())
                .type(contentType)
                .entity(httpResponse.body())
                .build());
        });
    }

    private boolean looksLikeFederatedCatalogSelfDescription(JsonNode catalogJson) {
        if (catalogJson == null || !catalogJson.isObject()) {
            return false;
        }

        // Typical FC DSP response in this stack: a single catalog object with participantId = federated-catalog and empty dataset.
        var participantId = catalogJson.get("dspace:participantId");
        if (participantId == null || !"federated-catalog".equals(participantId.asText())) {
            return false;
        }

        var datasets = catalogJson.get("dcat:dataset");
        if (datasets != null && datasets.isArray() && datasets.size() > 0) {
            return false;
        }

        return true;
    }

    private QuerySpec parseQuerySpec(String body) {
        if (body == null || body.isBlank()) {
            return QuerySpec.none();
        }

        try {
            JsonNode json = mapper.readTree(body);

            Integer offset = json.has("offset") && json.get("offset").canConvertToInt() ? json.get("offset").asInt() : null;
            Integer limit = json.has("limit") && json.get("limit").canConvertToInt() ? json.get("limit").asInt() : null;

            var builder = QuerySpec.Builder.newInstance();
            if (offset != null) {
                builder.offset(offset);
            }
            if (limit != null) {
                builder.limit(limit);
            }

            // Optional: support sortField/sortOrder if present (not required for current payload)
            if (json.hasNonNull("sortField")) {
                builder.sortField(json.get("sortField").asText());
            }
            if (json.hasNonNull("sortOrder")) {
                try {
                    builder.sortOrder(org.eclipse.edc.spi.query.SortOrder.valueOf(json.get("sortOrder").asText()));
                } catch (IllegalArgumentException ignored) {
                    // ignore invalid sortOrder
                }
            }

            return builder.build();
        } catch (Exception e) {
            monitor.warning("Failed to parse QuerySpec from body. Falling back to QuerySpec.none(): " + e.getMessage());
            return QuerySpec.none();
        }
    }

    private String normalizeQuerySpecForRest(String body) {
        try {
            if (body == null || body.isBlank()) {
                var obj = mapper.createObjectNode();
                obj.put("@type", "QuerySpec");
                return mapper.writeValueAsString(obj);
            }

            var json = mapper.readTree(body);
            if (json != null && json.isObject()) {
                var obj = (ObjectNode) json;
                if (!obj.hasNonNull("@type")) {
                    obj.put("@type", "QuerySpec");
                }
                return mapper.writeValueAsString(obj);
            }

            var obj = mapper.createObjectNode();
            obj.put("@type", "QuerySpec");
            return mapper.writeValueAsString(obj);
        } catch (Exception e) {
            monitor.warning("Failed to normalize QuerySpec body for REST; using default QuerySpec. Reason: " + e.getMessage());
            var obj = mapper.createObjectNode();
            obj.put("@type", "QuerySpec");
            try {
                return mapper.writeValueAsString(obj);
            } catch (Exception ignored) {
                return "{\"@type\":\"QuerySpec\"}";
            }
        }
    }

}
