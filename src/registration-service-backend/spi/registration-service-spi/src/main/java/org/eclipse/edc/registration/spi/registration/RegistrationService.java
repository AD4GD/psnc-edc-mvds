/*
 *  Copyright (c) 2023 Amadeus
 *
 *  This program and the accompanying materials are made available under the
 *  terms of the Apache License, Version 2.0 which is available at
 *  https://www.apache.org/licenses/LICENSE-2.0
 *
 *  SPDX-License-Identifier: Apache-2.0
 *
 *  Contributors:
 *       Amadeus - initial API and implementation
 *
 */

package org.eclipse.edc.registration.spi.registration;

import org.eclipse.edc.registration.spi.model.Participant;
import org.eclipse.edc.registration.spi.model.ParticipantFullRepresentation;
import org.jetbrains.annotations.Nullable;
import org.eclipse.edc.registration.spi.model.ParticipantStatus;

import java.util.List;
import java.util.Map;

/**
 * Registration service for dataspace participants.
 */
public interface RegistrationService {

    /**
     * Find a participant by its DID.
     *
     * @param did DID of participant.
     * @return participant.
     */
    @Nullable
    Participant findByDid(String did);

    /**
     * List all dataspace participants.
     *
     * @return all participants.
     */
    List<ParticipantFullRepresentation> listParticipants();

    /**
     * Add a participant to a dataspace.
     *
     * @param did the DID of the dataspace participant to add.
     */
    void addParticipant(String did, String protocolUrl);

    void updateParticipantStatus(String did, ParticipantStatus newStatus);

    void updateParticipantClaims(String did, Map<String, String> updatedClaims);

    void deleteParticipant(String did);
}
