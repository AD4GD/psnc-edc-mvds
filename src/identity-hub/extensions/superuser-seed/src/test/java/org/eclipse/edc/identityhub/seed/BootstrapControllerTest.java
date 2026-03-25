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

import jakarta.ws.rs.core.Response;
import org.eclipse.edc.identityhub.spi.participantcontext.ParticipantContextService;
import org.eclipse.edc.identityhub.spi.participantcontext.model.CreateParticipantContextResponse;
import org.eclipse.edc.identityhub.spi.participantcontext.model.ParticipantContext;
import org.eclipse.edc.spi.monitor.Monitor;
import org.eclipse.edc.spi.result.Result;
import org.eclipse.edc.spi.result.ServiceResult;
import org.eclipse.edc.spi.security.Vault;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;

import java.util.Map;

import static org.assertj.core.api.Assertions.assertThat;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.ArgumentMatchers.eq;
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.never;
import static org.mockito.Mockito.verify;
import static org.mockito.Mockito.when;

class BootstrapControllerTest {

    private static final String SUPER_USER = "super-user";
    private static final String VAULT_PROBE_KEY = "__vault_health_probe__";

    private final ParticipantContextService participantContextService = mock();
    private final Vault vault = mock();
    private final Monitor monitor = mock();

    private BootstrapController controller;

    @BeforeEach
    void setup() {
        controller = new BootstrapController(participantContextService, vault, monitor, SUPER_USER, null);
    }

    @Test
    void bootstrap_createsSuperUser() {
        when(participantContextService.getParticipantContext(eq(SUPER_USER)))
                .thenReturn(ServiceResult.notFound("not found"));
        when(vault.storeSecret(eq(VAULT_PROBE_KEY), any())).thenReturn(Result.success());
        when(vault.deleteSecret(eq(VAULT_PROBE_KEY))).thenReturn(Result.success());
        when(participantContextService.createParticipantContext(any()))
                .thenReturn(ServiceResult.success(new CreateParticipantContextResponse("generated-api-key", null, null)));

        var response = controller.bootstrap();

        assertThat(response.getStatus()).isEqualTo(200);
        var body = (Map<?, ?>) response.getEntity();
        assertThat(body.get("status")).isEqualTo("created");
        assertThat(body.get("apiKey")).isEqualTo("generated-api-key");

        verify(participantContextService).createParticipantContext(any());
    }

    @Test
    void bootstrap_returnsOkWhenSuperUserAlreadyExists() {
        when(participantContextService.getParticipantContext(eq(SUPER_USER)))
                .thenReturn(ServiceResult.success(superUserContext().build()));

        var response = controller.bootstrap();

        assertThat(response.getStatus()).isEqualTo(200);
        var body = (Map<?, ?>) response.getEntity();
        assertThat(body.get("status")).isEqualTo("already_exists");

        verify(participantContextService, never()).createParticipantContext(any());
        verify(vault, never()).storeSecret(eq(VAULT_PROBE_KEY), any());
    }

    @Test
    void bootstrap_returns503WhenVaultUnavailable() {
        when(participantContextService.getParticipantContext(eq(SUPER_USER)))
                .thenReturn(ServiceResult.notFound("not found"));
        when(vault.storeSecret(eq(VAULT_PROBE_KEY), any()))
                .thenReturn(Result.failure("connection refused"));

        var response = controller.bootstrap();

        assertThat(response.getStatus()).isEqualTo(Response.Status.SERVICE_UNAVAILABLE.getStatusCode());
        verify(participantContextService, never()).createParticipantContext(any());
    }

    @Test
    void bootstrap_returns500WhenCreationFails() {
        when(participantContextService.getParticipantContext(eq(SUPER_USER)))
                .thenReturn(ServiceResult.notFound("not found"));
        when(vault.storeSecret(eq(VAULT_PROBE_KEY), any())).thenReturn(Result.success());
        when(vault.deleteSecret(eq(VAULT_PROBE_KEY))).thenReturn(Result.success());
        when(participantContextService.createParticipantContext(any()))
                .thenReturn(ServiceResult.badRequest("some error"));

        var response = controller.bootstrap();

        assertThat(response.getStatus()).isEqualTo(500);
        var body = (Map<?, ?>) response.getEntity();
        assertThat(body.get("status")).isEqualTo("error");
    }

    @Test
    void bootstrap_usesApiKeyOverrideFromConfig() {
        var overrideKey = "c3VwZXItdXNlcgo=.custom-key";
        controller = new BootstrapController(participantContextService, vault, monitor, SUPER_USER, overrideKey);

        when(participantContextService.getParticipantContext(eq(SUPER_USER)))
                .thenReturn(ServiceResult.notFound("not found"))
                .thenReturn(ServiceResult.success(superUserContext().build()));
        when(vault.storeSecret(any(), any())).thenReturn(Result.success());
        when(vault.deleteSecret(any())).thenReturn(Result.success());
        when(participantContextService.createParticipantContext(any()))
                .thenReturn(ServiceResult.success(new CreateParticipantContextResponse("generated-api-key", null, null)));

        var response = controller.bootstrap();

        assertThat(response.getStatus()).isEqualTo(200);
        var body = (Map<?, ?>) response.getEntity();
        assertThat(body.get("apiKey")).isEqualTo(overrideKey);
        verify(vault).storeSecret(eq("super-user-apikey"), eq(overrideKey));
    }

    private ParticipantContext.Builder superUserContext() {
        return ParticipantContext.Builder.newInstance()
                .participantContextId(SUPER_USER)
                .apiTokenAlias("super-user-apikey");
    }
}
