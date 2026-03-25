/*
 *  Copyright (c) 2025 PSNC
 *
 *  This program and the accompanying materials are made available under the
 *  terms of the Apache License, Version 2.0 which is available at
 *  https://www.apache.org/licenses/LICENSE-2.0
 *
 *  SPDX-License-Identifier: Apache-2.0
 *
 *  Contributors:
 *       PSNC - initial API and implementation
 *
 */

package org.eclipse.edc.identityhub.seed;

import jakarta.ws.rs.Consumes;
import jakarta.ws.rs.POST;
import jakarta.ws.rs.Path;
import jakarta.ws.rs.Produces;
import jakarta.ws.rs.core.MediaType;
import jakarta.ws.rs.core.Response;
import org.eclipse.edc.identityhub.spi.authentication.ServicePrincipal;
import org.eclipse.edc.identityhub.spi.participantcontext.ParticipantContextService;
import org.eclipse.edc.identityhub.spi.participantcontext.model.KeyDescriptor;
import org.eclipse.edc.identityhub.spi.participantcontext.model.ParticipantManifest;
import org.eclipse.edc.spi.monitor.Monitor;
import org.eclipse.edc.spi.security.Vault;

import java.util.List;
import java.util.Map;

import static java.util.Optional.ofNullable;

/**
 * Bootstrap controller for creating the Identity Hub super-user.
 * <p>
 * This endpoint is designed to be called by an external init script after
 * all infrastructure (Vault, database) is confirmed ready. It is self-protecting:
 * if the super-user already exists, it returns 200 with a message instead of failing.
 * <p>
 * No authentication is required — the endpoint verifies Vault connectivity before
 * proceeding, and it is intended to be called once during initial deployment.
 */
@Path("/bootstrap")
@Consumes(MediaType.APPLICATION_JSON)
@Produces(MediaType.APPLICATION_JSON)
public class BootstrapController {

    private static final String VAULT_PROBE_KEY = "__vault_health_probe__";

    private final ParticipantContextService participantContextService;
    private final Vault vault;
    private final Monitor monitor;
    private final String superUserParticipantId;
    private final String superUserApiKey;

    public BootstrapController(ParticipantContextService participantContextService,
                               Vault vault,
                               Monitor monitor,
                               String superUserParticipantId,
                               String superUserApiKey) {
        this.participantContextService = participantContextService;
        this.vault = vault;
        this.monitor = monitor;
        this.superUserParticipantId = superUserParticipantId;
        this.superUserApiKey = superUserApiKey;
    }

    /**
     * Creates the super-user participant context.
     * <p>
     * Returns:
     * - 200 with API key if super-user was created successfully
     * - 200 with message if super-user already exists (idempotent)
     * - 503 if Vault is not reachable
     * - 500 if creation fails for any other reason
     */
    @POST
    public Response bootstrap() {
        monitor.info("Bootstrap endpoint called — checking super-user status...");

        // Check if super-user already exists
        if (participantContextService.getParticipantContext(superUserParticipantId).succeeded()) {
            monitor.info("Super-user '%s' already exists, bootstrap is a no-op.".formatted(superUserParticipantId));
            return Response.ok(Map.of(
                    "status", "already_exists",
                    "participantId", superUserParticipantId,
                    "message", "Super-user already exists. Use the configured API key."
            )).build();
        }

        // Verify Vault is reachable before creating the super-user
        var vaultCheck = vault.storeSecret(VAULT_PROBE_KEY, "probe");
        if (vaultCheck.failed()) {
            monitor.warning("Bootstrap: Vault is not reachable — %s".formatted(vaultCheck.getFailureDetail()));
            return Response.status(Response.Status.SERVICE_UNAVAILABLE)
                    .entity(Map.of(
                            "status", "error",
                            "message", "Vault is not reachable. Ensure Vault is initialized and unsealed before calling bootstrap.",
                            "detail", vaultCheck.getFailureDetail()
                    )).build();
        }
        vault.deleteSecret(VAULT_PROBE_KEY);

        // Create the super-user
        monitor.info("Creating super-user '%s'...".formatted(superUserParticipantId));

        var result = participantContextService.createParticipantContext(ParticipantManifest.Builder.newInstance()
                .participantId(superUserParticipantId)
                .did("did:web:%s".formatted(superUserParticipantId))
                .active(true)
                .key(KeyDescriptor.Builder.newInstance()
                        .keyGeneratorParams(Map.of("algorithm", "EdDSA", "curve", "Ed25519"))
                        .keyId("%s-key".formatted(superUserParticipantId))
                        .privateKeyAlias("%s-alias".formatted(superUserParticipantId))
                        .build())
                .roles(List.of(ServicePrincipal.ROLE_ADMIN))
                .build());

        if (result.failed()) {
            monitor.severe("Bootstrap: Failed to create super-user — %s".formatted(result.getFailureDetail()));
            return Response.serverError()
                    .entity(Map.of(
                            "status", "error",
                            "message", "Failed to create super-user.",
                            "detail", result.getFailureDetail()
                    )).build();
        }

        // Determine the API key (override from config or auto-generated)
        var generatedKey = result.getContent();
        var apiKey = ofNullable(superUserApiKey).orElse(generatedKey.apiKey());

        // If an override key is configured, store it in Vault
        if (superUserApiKey != null) {
            participantContextService.getParticipantContext(superUserParticipantId)
                    .onSuccess(pc -> {
                        var storeResult = vault.storeSecret(pc.getApiTokenAlias(), superUserApiKey);
                        if (storeResult.failed()) {
                            monitor.warning("Bootstrap: Failed to store API key override in Vault — %s"
                                    .formatted(storeResult.getFailureDetail()));
                        }
                    });
        }

        monitor.info("Super-user '%s' created successfully.".formatted(superUserParticipantId));

        return Response.ok(Map.of(
                "status", "created",
                "participantId", superUserParticipantId,
                "apiKey", apiKey
        )).build();
    }
}
