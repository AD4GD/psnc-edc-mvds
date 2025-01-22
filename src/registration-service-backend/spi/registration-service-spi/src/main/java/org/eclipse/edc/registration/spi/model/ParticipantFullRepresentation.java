package org.eclipse.edc.registration.spi.model;
import com.fasterxml.jackson.databind.annotation.JsonDeserialize;

import java.util.Map;

/**
 * The full representation of the participant
 * conists of stored base model in the backend db + keycloak claims
 * Dataspace participant.
 */
@JsonDeserialize(builder = ParticipantFullRepresentation.Builder.class)
public class ParticipantFullRepresentation extends Participant {

    private Map<String, String> claims;

    private ParticipantFullRepresentation() {
        super();
    }

    public ParticipantFullRepresentation(Participant participant) {
        this.setDid(participant.getDid());
        this.setProtocolUrl(participant.getProtocolUrl());
        this.setStatus(participant.getState());
    }

    public Map<String, String> getClaims() {
        return claims;
    }

    public void setClaims(Map<String, String> claims) {
        this.claims = claims;
    }
}
