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

package org.eclipse.edc.registration.manager;

/**
 * Manager for participant registration state machine.
 */
public interface ParticipantManager {

    /**
     * Start the participant manager state machine processor thread.
     */
    void start();

    /**
     * Stop the participant manager state machine processor thread.
     */
    void stop();
}
