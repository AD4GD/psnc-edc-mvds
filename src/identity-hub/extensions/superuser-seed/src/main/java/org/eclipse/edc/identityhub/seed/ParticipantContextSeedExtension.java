/*
 *  Copyright (c) 2024 Metaform Systems, Inc.
 *
 *  This program and the accompanying materials are made available under the
 *  terms of the Apache License, Version 2.0 which is available at
 *  https://www.apache.org/licenses/LICENSE-2.0
 *
 *  SPDX-License-Identifier: Apache-2.0
 *
 *  Contributors:
 *       Metaform Systems, Inc. - initial API and implementation
 *       PSNC - converted to bootstrap endpoint for production use
 *
 */

package org.eclipse.edc.identityhub.seed;

import org.eclipse.edc.runtime.metamodel.annotation.Extension;
import org.eclipse.edc.runtime.metamodel.annotation.Inject;
import org.eclipse.edc.runtime.metamodel.annotation.Setting;
import org.eclipse.edc.spi.monitor.Monitor;
import org.eclipse.edc.spi.security.Vault;
import org.eclipse.edc.spi.system.ServiceExtension;
import org.eclipse.edc.spi.system.ServiceExtensionContext;
import org.eclipse.edc.identityhub.spi.participantcontext.ParticipantContextService;
import org.eclipse.edc.web.spi.WebService;

/**
 * Exposes a bootstrap endpoint for creating the Identity Hub super-user.
 * <p>
 * Unlike the original demo extension that auto-created the super-user on startup
 * (which failed when Vault was sealed), this extension registers an HTTP endpoint
 * that can be called externally when all infrastructure is confirmed ready.
 * <p>
 * The endpoint is self-protecting: it only works when no participants exist yet.
 */
@Extension(value = ParticipantContextSeedExtension.NAME)
public class ParticipantContextSeedExtension implements ServiceExtension {
    public static final String NAME = "ParticipantContext Bootstrap Extension";
    public static final String DEFAULT_SUPER_USER_PARTICIPANT_ID = "super-user";

    @Setting(value = "Explicitly set the initial API key for the Super-User")
    public static final String SUPERUSER_APIKEY_PROPERTY = "edc.ih.api.superuser.key";

    @Setting(value = "Config value to set the super-user's participant ID.", defaultValue = DEFAULT_SUPER_USER_PARTICIPANT_ID)
    public static final String SUPERUSER_PARTICIPANT_ID_PROPERTY = "edc.ih.api.superuser.id";

    @Inject
    private ParticipantContextService participantContextService;

    @Inject
    private Vault vault;

    @Inject
    private WebService webService;

    @Override
    public String name() {
        return NAME;
    }

    @Override
    public void initialize(ServiceExtensionContext context) {
        var monitor = context.getMonitor();
        var superUserParticipantId = context.getSetting(SUPERUSER_PARTICIPANT_ID_PROPERTY, DEFAULT_SUPER_USER_PARTICIPANT_ID);
        var superUserApiKey = context.getSetting(SUPERUSER_APIKEY_PROPERTY, null);

        var controller = new BootstrapController(participantContextService, vault, monitor, superUserParticipantId, superUserApiKey);
        webService.registerResource(controller);

        monitor.info("Bootstrap endpoint registered at POST /api/bootstrap");
    }
}
