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

package org.eclipse.edc.registration.spi.model;

import com.fasterxml.jackson.annotation.JsonCreator;
import com.fasterxml.jackson.databind.annotation.JsonDeserialize;
import com.fasterxml.jackson.databind.annotation.JsonPOJOBuilder;
import org.eclipse.edc.spi.entity.StatefulEntity;

import java.util.Arrays;
import java.util.Map;
import java.util.Objects;

import static java.lang.String.format;
import static java.util.Collections.unmodifiableMap;
import static org.eclipse.edc.registration.spi.model.ParticipantStatus.AUTHORIZED;
import static org.eclipse.edc.registration.spi.model.ParticipantStatus.AUTHORIZING;
import static org.eclipse.edc.registration.spi.model.ParticipantStatus.DENIED;
import static org.eclipse.edc.registration.spi.model.ParticipantStatus.FAILED;
import static org.eclipse.edc.registration.spi.model.ParticipantStatus.ONBOARDED;
import static org.eclipse.edc.registration.spi.model.ParticipantStatus.ONBOARDING_INITIATED;

/**
 * Dataspace participant.
 */
@JsonDeserialize(builder = Participant.Builder.class)
public class Participant extends StatefulEntity<Participant> {

    private String did;
    private String protocolUrl;

    public Participant() {
    }

    public String getDid() {
        return did;
    }

    public ParticipantStatus getStatus() {
        return ParticipantStatus.from(state);
    }

    public String getProtocolUrl() {
        return protocolUrl;
    }

    protected void setDid(String did) {
        this.did = did;
    }

    protected void setStatus(int state) {
        this.state = state;
    }

    protected void setProtocolUrl(String protocolUrl) {
        this.protocolUrl = protocolUrl;
    }

    @Override
    public Participant copy() {
        var builder = Builder.newInstance()
                .did(did)
                .state(state)
                .protocolUrl(protocolUrl);

        return copy(builder);
    }

    @Override
    public String stateAsString() {
        return ParticipantStatus.from(state).name();
    }

    public void forceTransitionTo(ParticipantStatus target) {
        transitionTo(target.code());
    }

    public void findTransitionTo(ParticipantStatus target) {
        if (target == AUTHORIZING) {
            transitionAuthorizing();
        }
        else if (target == AUTHORIZED) {
            transitionAuthorized();
        }
        else if (target == DENIED) {
            transitionDenied();
        }
        else if (target == ONBOARDED) {
            transitionOnboarded();
        }
        else if (target == FAILED) {
            transitionFailed();
        }
    }

    public void transitionAuthorizing() {
        transition(AUTHORIZING, ONBOARDING_INITIATED);
    }

    public void transitionAuthorized() {
        transition(AUTHORIZED, AUTHORIZING);
    }

    public void transitionDenied() {
        transition(DENIED, AUTHORIZING);
    }

    public void transitionOnboarded() {
        transition(ONBOARDED, AUTHORIZED);
    }

    public void transitionFailed() {
        transition(FAILED, AUTHORIZING, AUTHORIZED);
    }

    /**
     * Transition to a given end state from an allowed number of previous states.
     *
     * @param end    The desired state.
     * @param starts The allowed previous states.
     */
    private void transition(ParticipantStatus end, ParticipantStatus... starts) {
        if (Arrays.stream(starts).noneMatch(s -> s.code() == state)) {
            throw new IllegalStateException(format("Cannot transition from state %s to %s", ParticipantStatus.from(state), end));
        }
        transitionTo(end.code());
    }

    @JsonPOJOBuilder(withPrefix = "")
    public static class Builder extends StatefulEntity.Builder<Participant, Builder> {

        private Builder(Participant participant) {
            super(participant);
        }

        @JsonCreator
        public static Builder newInstance() {
            return new Builder(new Participant());
        }

        public Builder did(String did) {
            entity.did = did;
            return this;
        }

        public Builder status(ParticipantStatus status) {
            entity.state = status.code();
            return this;
        }

        public Builder protocolUrl(String protocolUrl) {
            entity.protocolUrl = protocolUrl;
            return this;
        }

        @Override
        public Builder traceContext(Map<String, String> traceContext) {
            entity.traceContext = unmodifiableMap(traceContext);
            return this;
        }

        @Override
        public Participant build() {
            Objects.requireNonNull(entity.did, "did");
            Objects.requireNonNull(entity.protocolUrl, "protocolUrl");
            return super.build();
        }


        @Override
        public Builder self() {
            return this;
        }
    }
}
