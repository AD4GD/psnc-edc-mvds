package org.eclipse.edc.sample.runtime;

import java.util.Arrays;
import java.util.Base64;
import java.util.Collections;
import java.util.List;
import java.util.Map;

import com.fasterxml.jackson.databind.JsonNode;

import org.eclipse.edc.api.auth.spi.AuthenticationService;
import org.eclipse.edc.api.auth.spi.registry.ApiAuthenticationProviderRegistry;
import org.eclipse.edc.spi.monitor.Monitor;
import org.eclipse.edc.spi.system.configuration.Config;
import com.fasterxml.jackson.databind.ObjectMapper;

public class CompositeAuthenticationService implements AuthenticationService {

    private final String[] compositeTypes;
    private final ApiAuthenticationProviderRegistry providerRegistry;
    private final Config config;
    private final Monitor monitor;
    private final ObjectMapper mapper;

    public CompositeAuthenticationService(
        String[] compositeTypes,
        ApiAuthenticationProviderRegistry providerRegistry,
        Config config,
        Monitor monitor,
        ObjectMapper mapper) {
        this.compositeTypes = compositeTypes;
        this.providerRegistry = providerRegistry;
        this.config = config;
        this.monitor = monitor;
        this.mapper = mapper;
    }

    @Override
    public boolean isAuthenticated(Map<String, List<String>> headers) {
        var providers = Arrays.stream(compositeTypes).map(x -> new Entry(x, providerRegistry.resolve(x).provide(config).getContent())).toList();

        var requiredAudiences = getOptionalList("audience", "dac.audience");
        var requiredRoles = getOptionalList("roles", "dac.roles");

        for (var entry : providers) {
            try {
                if (entry.service.isAuthenticated(headers)) {
                    if ("delegated".equals(entry.name)) {
                        if (!requiredAudiences.isEmpty()) {
                            if (!checkAudiences(headers, requiredAudiences)) {
                                monitor.warning("Audience check failed for delegated auth. Required all: " + requiredAudiences);
                                continue;
                            }
                        }

                        if (!requiredRoles.isEmpty()) {
                            if (!checkRoles(headers, requiredRoles)) {
                                monitor.warning("Role check failed for delegated auth. Required any of: " + requiredRoles);
                                continue;
                            }
                        }
                    }

                    return true;
                }
            } catch (Exception e) {
                monitor.debug(e.getMessage());
            }
        }
        return false;
    }

    private List<String> getOptionalList(String primaryKey, String fallbackKey) {
        var raw = config.getString(primaryKey, null);
        if (raw == null) {
            raw = config.getString(fallbackKey, null);
        }
        if (raw == null || raw.isBlank()) {
            return Collections.emptyList();
        }
        return parseStringList(raw);
    }

    private List<String> parseStringList(String raw) {
        try {
            var trimmed = raw.trim();
            if (trimmed.startsWith("[")) {
                var arr = mapper.readValue(trimmed, String[].class);
                return Arrays.stream(arr).filter(s -> s != null && !s.isBlank()).map(String::trim).toList();
            }
        } catch (Exception e) {
            monitor.debug("Failed to parse roles JSON array, falling back to CSV. Reason: " + e.getMessage());
        }

        return Arrays.stream(raw.split(","))
            .map(String::trim)
            .filter(s -> !s.isBlank())
            .toList();
    }

    private boolean checkAudiences(Map<String, List<String>> headers, List<String> requiredAudiences) {
        String token = extractBearerToken(headers);
        if (token == null) return false;

        try {
            String[] parts = token.split("\\.");
            if (parts.length < 2) return false;

            byte[] payloadBytes = Base64.getUrlDecoder().decode(parts[1]);
            var json = mapper.readTree(payloadBytes);
            var audNode = json.get("aud");

            if (audNode == null) {
                monitor.debug("Token missing 'aud' claim");
                return false;
            }

            // We require ALL configured audiences to be present in the token's aud claim.
            for (var required : requiredAudiences) {
                if (!hasAudience(audNode, required)) {
                    monitor.debug("Token audience mismatch. Missing: " + required);
                    return false;
                }
            }

            return true;

        } catch (Exception e) {
            monitor.severe("Failed to parse token for audience check", e);
        }
        return false;
    }

    private boolean hasAudience(JsonNode audNode, String expectedAudience) {
        if (audNode == null || expectedAudience == null) {
            return false;
        }

        if (audNode.isArray()) {
            for (var node : audNode) {
                if (expectedAudience.equals(node.asText())) {
                    return true;
                }
            }
            return false;
        }

        return expectedAudience.equals(audNode.asText());
    }

    private boolean checkRoles(Map<String, List<String>> headers, List<String> requiredRoles) {
        String token = extractBearerToken(headers);
        if (token == null) return false;

        try {
            String[] parts = token.split("\\.");
            if (parts.length < 2) return false;

            byte[] payloadBytes = Base64.getUrlDecoder().decode(parts[1]);
            var json = mapper.readTree(payloadBytes);

            var resourceAccess = json.get("resource_access");
            if (resourceAccess == null || !resourceAccess.isObject()) {
                monitor.debug("Token missing 'resource_access' claim");
                return false;
            }

            var fields = resourceAccess.fields();
            while (fields.hasNext()) {
                var clientEntry = fields.next();
                JsonNode rolesNode = clientEntry.getValue().get("roles");
                if (rolesNode != null && rolesNode.isArray()) {
                    for (var role : rolesNode) {
                        var roleName = role != null ? role.asText() : null;
                        if (roleName == null) {
                            continue;
                        }
                        for (var required : requiredRoles) {
                            if (required.equals(roleName)) {
                                return true;
                            }
                        }
                    }
                }
            }
        } catch (Exception e) {
            monitor.severe("Failed to parse token for role check", e);
            return false;
        }

        monitor.debug("Token roles mismatch. Required any of: " + requiredRoles);
        return false;
    }

    private String extractBearerToken(Map<String, List<String>> headers) {
        for (var entry : headers.entrySet()) {
            if ("authorization".equalsIgnoreCase(entry.getKey())) {
                List<String> values = entry.getValue();
                if (values != null && !values.isEmpty()) {
                    String value = values.get(0);
                    if (value.toLowerCase().startsWith("bearer ")) {
                        return value.substring(7);
                    }
                }
            }
        }
        return null;
    }

    private static class Entry {
        String name;
        AuthenticationService service;
        Entry(String name, AuthenticationService service) {
            this.name = name;
            this.service = service;
        }
    }
}
