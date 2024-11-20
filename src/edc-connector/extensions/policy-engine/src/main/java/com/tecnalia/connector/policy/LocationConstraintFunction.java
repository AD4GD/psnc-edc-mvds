/*
 *  Copyright (c) 2024 Fraunhofer Institute for Software and Systems Engineering
 *
 *  This program and the accompanying materials are made available under the
 *  terms of the Apache License, Version 2.0 which is available at
 *  https://www.apache.org/licenses/LICENSE-2.0
 *
 *  SPDX-License-Identifier: Apache-2.0
 *
 *  Contributors:
 *       Fraunhofer Institute for Software and Systems Engineering - initial API and implementation
 *
 */

package com.tecnalia.connector.policy;

import org.eclipse.edc.connector.controlplane.contract.spi.types.agreement.ContractAgreement;

import org.eclipse.edc.policy.engine.spi.AtomicConstraintRuleFunction;
import org.eclipse.edc.policy.engine.spi.PolicyContext;
import org.eclipse.edc.policy.model.Operator;
import org.eclipse.edc.policy.model.Permission;
import org.eclipse.edc.participant.spi.ParticipantAgent;
import org.eclipse.edc.spi.monitor.Monitor;
import org.eclipse.edc.policy.engine.spi.DynamicAtomicConstraintRuleFunction;
import org.eclipse.edc.participant.spi.ParticipantAgentPolicyContext;

import java.util.Collection;
import java.util.Objects;
import java.util.Map;

import static java.lang.String.format;

public class LocationConstraintFunction implements AtomicConstraintRuleFunction<Permission, ParticipantAgentPolicyContext> {
    
    private final Monitor monitor;

    
    public LocationConstraintFunction(Monitor monitor) {
        this.monitor = monitor;
    }
    
    @Override
    public boolean evaluate(Operator operator, Object rightValue, Permission permission, ParticipantAgentPolicyContext context) {
	
        var participantAgent = context.participantAgent();
		
        monitor.debug("LOCATION Policy CLAIMS list");
        for (String key : participantAgent.getClaims().keySet()) {
            monitor.debug(format("LOCATION Policy claims %s = %s", key, participantAgent.getClaims().get(key)));
        }
        monitor.debug("LOCATION Policy ATTRIBUTES list");
        for (String key : participantAgent.getAttributes().keySet()) {
            monitor.debug(format("LOCATION Policy attributes %s = %s", key, participantAgent.getAttributes().get(key)));
        }
        
	var participantId = participantAgent.getIdentity();
        var region = participantAgent.getClaims().get("region");

        monitor.debug(format("LOCATION Policy consumer ID = %s", participantId));
        monitor.debug(format("LOCATION Policy region = %s", region));
        monitor.debug("LOCATION Policy CLAIMS list");
	monitor.debug(format("Operator = %s", operator));
        monitor.debug(format("Rightvalue = %s", rightValue));
	        
        monitor.info(format("Evaluating constraint: location %s %s", operator, rightValue.toString()));
        return switch (operator) {
            case EQ -> Objects.equals(region, rightValue);
            case NEQ -> !Objects.equals(region, rightValue);
            case IN -> ((Collection<?>) rightValue).contains(region);
            default -> false;
        };
    }
}
