/*
 *  Copyright (c) 2022 Microsoft Corporation
 *
 *  This program and the accompanying materials are made available under the
 *  terms of the Apache License, Version 2.0 which is available at
 *  https://www.apache.org/licenses/LICENSE-2.0
 *
 *  SPDX-License-Identifier: Apache-2.0
 *
 *  Contributors:
 *       Microsoft Corporation - initial API and implementation
 *
 */

package org.eclipse.edc.registration.service;


import org.eclipse.edc.registration.spi.model.Participant;
import org.eclipse.edc.registration.spi.registration.RegistrationService;
import org.eclipse.edc.registration.store.spi.ParticipantStore;
import org.eclipse.edc.spi.monitor.Monitor;
import org.eclipse.edc.spi.telemetry.Telemetry;
import org.eclipse.edc.transaction.spi.TransactionContext;
import org.jetbrains.annotations.Nullable;
import org.psnc.mvd.identity.IdentityProviderClient;
import org.eclipse.edc.registration.spi.model.ParticipantStatus;

import java.util.List;
import java.util.Map;
import java.util.UUID;

import static java.lang.String.format;
import static org.eclipse.edc.registration.spi.model.ParticipantStatus.DELETED;
import static org.eclipse.edc.registration.spi.model.ParticipantStatus.ONBOARDING_INITIATED;

public class RegistrationServiceImpl implements RegistrationService {

    private final Monitor monitor;
    private final ParticipantStore participantStore;
    private final Telemetry telemetry;
    private final TransactionContext transactionContext;
    private final IdentityProviderClient identityProviderClient;


    public RegistrationServiceImpl(
        Monitor monitor, ParticipantStore participantStore, Telemetry telemetry, TransactionContext transactionContext, IdentityProviderClient identityProviderClient) {
        this.monitor = monitor;
        this.participantStore = participantStore;
        this.telemetry = telemetry;
        this.transactionContext = transactionContext;
        this.identityProviderClient = identityProviderClient;
    }

    @Nullable
    public Participant findByDid(String did) {
        monitor.info(format("Find a participant by DID %s", did));
        return participantStore.findByDid(did);
    }

    public List<Participant> listParticipants() {
        monitor.info("List all participants of the dataspace.");
        return transactionContext.execute(participantStore::listParticipants);
    }

    public void addParticipant(String did) {
        monitor.info("Adding a participant in the dataspace.");

        var participant = Participant.Builder.newInstance()
                .id(UUID.randomUUID().toString())
                .did(did)
                .status(ONBOARDING_INITIATED)
                .traceContext(telemetry.getCurrentTraceContext())
                .build();

        transactionContext.execute(() -> participantStore.save(participant));
    }

    public void updateParticipantStatus(String did, ParticipantStatus newStatus) {
        monitor.info("Updating participant's status in the dataspace.");

        var participant = participantStore.findByDid(did);
        participant.forceTransitionTo(newStatus);

        transactionContext.execute(() -> participantStore.save(participant));
    }

    public void updateParticipantClaims(String did, Map<String, String> updatedClaims) {
        monitor.info("Updating participant's claims in the dataspace.");
        identityProviderClient.updateClient(did, updatedClaims);
    }

    public void deleteParticipant(String did) {
        monitor.info("Deleting participant from the dataspace.");

        var participant = participantStore.findByDid(did);
        participant.forceTransitionTo(DELETED);

        transactionContext.execute(() -> participantStore.save(participant));
    }
}
