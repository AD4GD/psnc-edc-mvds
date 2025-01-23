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
 *
 */

package org.eclipse.edc.demo.participants.resolver;

import com.fasterxml.jackson.core.type.TypeReference;
import com.fasterxml.jackson.databind.ObjectMapper;
import org.eclipse.edc.crawler.spi.TargetNode;
import org.eclipse.edc.crawler.spi.TargetNodeDirectory;
import org.eclipse.edc.spi.EdcException;
import org.eclipse.edc.spi.monitor.Monitor;

import java.io.File;
import java.io.IOException;
import java.util.List;
import java.util.Map;
import java.util.Objects;

/**
 * {@link TargetNodeDirectory} that is initialized with a file. On the first getAll() request
 * From then on, they are held in memory and cached.
 * <p>
 */
public class LazyLoadNodeDirectory implements TargetNodeDirectory {
    private static final TypeReference<Map<String, String>> MAP_TYPE = new TypeReference<>() {
    };
    private final ObjectMapper mapper;
    private final File participantListFile;
    private final Monitor monitor;


    public LazyLoadNodeDirectory(ObjectMapper mapper, File participantListFile, Monitor monitor) {

        this.mapper = mapper;
        this.participantListFile = participantListFile;
        this.monitor = monitor;
    }

    @Override
    public List<TargetNode> getAll() {
        try {
            var entries = mapper.readValue(participantListFile, MAP_TYPE);

            return entries.entrySet().stream()
                    .map(e -> createNode(e.getKey(), e.getValue()))
                    .filter(Objects::nonNull)
                    .toList();
        } catch (IOException e) {
            throw new EdcException(e);
        }
    }

    @Override
    public void insert(TargetNode targetNode) {
        //noop
    }

    private TargetNode createNode(String id, String serviceEndpoint) {
        return new TargetNode(id, id, serviceEndpoint, List.of("dataspace-protocol-http"));
    }
}
