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

package org.eclipse.edc.registration.api;

import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.media.ArraySchema;
import io.swagger.v3.oas.annotations.media.Content;
import io.swagger.v3.oas.annotations.media.Schema;
import io.swagger.v3.oas.annotations.responses.ApiResponse;
import io.swagger.v3.oas.annotations.responses.ApiResponses;
import io.swagger.v3.oas.annotations.tags.Tag;
import jakarta.ws.rs.Consumes;
import jakarta.ws.rs.DELETE;
import jakarta.ws.rs.GET;
import jakarta.ws.rs.POST;
import jakarta.ws.rs.PATCH;
import jakarta.ws.rs.QueryParam;
import jakarta.ws.rs.Path;
import jakarta.ws.rs.PathParam;
import jakarta.ws.rs.Produces;
import jakarta.ws.rs.core.Context;
import jakarta.ws.rs.core.HttpHeaders;
import jakarta.ws.rs.core.MediaType;
import org.eclipse.edc.registration.model.ParticipantDto;
import org.eclipse.edc.registration.spi.model.Participant;
import org.eclipse.edc.registration.spi.registration.RegistrationService;
import org.eclipse.edc.spi.EdcException;
import org.eclipse.edc.spi.result.Result;
import org.eclipse.edc.transform.spi.TypeTransformerRegistry;
import org.eclipse.edc.web.spi.exception.ObjectNotFoundException;
import org.eclipse.edc.registration.spi.model.ParticipantStatus;

import java.util.List;
import java.util.Map;
import java.util.Objects;
import java.util.Optional;
import java.util.stream.Collectors;


/**
 * Registration Service API controller to manage dataspace participants.
 */
@Tag(name = "Registry")
@Produces({ MediaType.APPLICATION_JSON })
@Consumes({ MediaType.APPLICATION_JSON })
@Path("/registry")
public class RegistrationServiceApiController {

    private final RegistrationService service;
    private final TypeTransformerRegistry transformerRegistry;

    private final String CALLER_DID_HEADER = "CallerDid";

    /**
     * Constructs an instance of {@link RegistrationServiceApiController}
     *
     * @param service             service handling the registration service logic.
     * @param transformerRegistry dto transformer registry
     */
    public RegistrationServiceApiController(RegistrationService service, TypeTransformerRegistry transformerRegistry) {
        this.service = service;
        this.transformerRegistry = transformerRegistry;
    }

    @GET
    @Path("/participants/{did}")
    @Operation(description = "Get a participant by caller DID.")
    @ApiResponses(value = {
            @ApiResponse(
                    responseCode = "200",
                    description = "Dataspace participant.",
                    content = {
                            @Content(
                                    mediaType = "application/json",
                                    schema = @Schema(implementation = ParticipantDto.class)
                            )
                    }
            ),
            @ApiResponse(
                    responseCode = "404",
                    description = "Dataspace participant not found."
            )
    })
    public ParticipantDto getParticipantWithPathId(@PathParam("did") String did) {
        return getParticipant(did);
    }

    private ParticipantDto getParticipant(String did) {
        var issuer = Objects.requireNonNull(did);
        var participant = Optional.ofNullable(service.findByDid(issuer))
                .orElseThrow(() -> new ObjectNotFoundException(Participant.class, issuer));

        var result = transformerRegistry.transform(participant, ParticipantDto.class);
        if (result.failed()) {
            throw new EdcException(result.getFailureDetail());
        }
        return result.getContent();
    }

    @Path("/participants")
    @GET
    @Operation(description = "Gets all dataspace participants.")
    @ApiResponses(value = {
            @ApiResponse(
                    responseCode = "200",
                    description = "Dataspace participants.",
                    content = {
                            @Content(
                                    mediaType = "application/json",
                                    array = @ArraySchema(schema = @Schema(implementation = ParticipantDto.class))
                            )
                    }
            )
    })
    public List<ParticipantDto> listParticipants() {
        return service.listParticipants().stream()
                .map(participant -> transformerRegistry.transform(participant, ParticipantDto.class))
                .filter(Result::succeeded)
                .map(Result::getContent)
                .collect(Collectors.toList());
    }

    @Path("/participants")
    @POST
    @Operation(description = "Asynchronously request to add a dataspace participant.")
    @ApiResponse(responseCode = "204", description = "No content")
    public void addParticipant(
        @QueryParam("did") String did,
        @QueryParam("protocolUrl") String protocolUrl
    ) {
        var issuer = Objects.requireNonNull(did);

        service.addParticipant(issuer, protocolUrl);
    }

    @Path("/participants/{did}")
    @PATCH
    @Operation(description = "Asynchronously updates dataspace participant's status.")
    @ApiResponse(responseCode = "204", description = "No content")
    public void updateParticipantStatus(
        @PathParam("did") String did,
        @QueryParam("status") ParticipantStatus newStatus
        ) {
        var issuer = Objects.requireNonNull(did);

        service.updateParticipantStatus(issuer, newStatus);
    }

    @Path("/participants/{did}/claims")
    @PATCH
    @Operation(description = "Asynchronously updates dataspace participant's claims.")
    @ApiResponse(responseCode = "204", description = "No content")
    public void updateParticipantClaims(
        @PathParam("did") String did,
        Map<String, String> updatedClaims
        ) {
        service.updateParticipantClaims(did, updatedClaims);
    }

    @Path("/participants/{did}")
    @DELETE
    @Operation(description = "Asynchronously removes dataspace participant from the dataspace.")
    @ApiResponse(responseCode = "204", description = "No content")
    public void deleteParticipant(@PathParam("did") String did) {
        var issuer = Objects.requireNonNull(did);

        service.deleteParticipant(issuer);
    }
}
