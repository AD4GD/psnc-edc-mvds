/*
Copyright (c) 2024 Tecnalia, Basque Research & Technology Alliance (BRTA)

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

SPDX-License-Identifier: MIT

*/
package com.tecnalia.connector.policy;

import org.eclipse.edc.connector.controlplane.contract.spi.types.agreement.ContractAgreement;
import org.eclipse.edc.policy.engine.spi.AtomicConstraintRuleFunction;
import org.eclipse.edc.policy.engine.spi.PolicyContext;
import org.eclipse.edc.policy.model.Operator;
import org.eclipse.edc.policy.model.Permission;
import org.eclipse.edc.runtime.metamodel.annotation.Inject;
import org.eclipse.edc.participant.spi.ParticipantAgent;
import org.eclipse.edc.spi.monitor.Monitor;
import org.eclipse.edc.connector.controlplane.contract.spi.policy.ContractNegotiationPolicyContext;

import static java.lang.String.format;
import java.util.Collection;
import java.util.Objects;
import java.util.Map;

public class PurposeConstraintFunction implements AtomicConstraintRuleFunction<Permission, ContractNegotiationPolicyContext> {
    private Monitor monitor;

    public PurposeConstraintFunction (Monitor monitor) {
        this.monitor = monitor;
    }

    @Override
    public boolean evaluate(Operator operator, Object rightValue, Permission rule, ContractNegotiationPolicyContext context) {
        
        var participantAgent = context.participantAgent();
        
        monitor.debug("PURPOSE Policy CLAIMS list");
        for (String key : participantAgent.getClaims().keySet()) {
            monitor.debug(format("PURPOSE Policy claims %s = %s", key, participantAgent.getClaims().get(key)));
        }
        monitor.debug("PURPOSE Policy ATTRIBUTES list");
        for (String key : participantAgent.getAttributes().keySet()) {
            monitor.debug(format("PURPOSE Policy attributes %s = %s", key, participantAgent.getAttributes().get(key)));
        }
        
        var participantId = participantAgent.getIdentity();
        var urlPurpose = participantAgent.getClaims().get("purpose");

        monitor.debug(format("PURPOSE consumer ID = %s", participantId));
        monitor.debug(format("PURPOSE Policy purpose = %s", urlPurpose));
        monitor.debug(format("Operator = %s", operator));
        monitor.debug(format("Rightvalue = %s", rightValue));

        monitor.info(format("Evaluating constraint: purpose %s %s", operator, rightValue.toString()));
        return switch (operator) {
            case EQ -> Objects.equals(urlPurpose, rightValue);
            case NEQ -> !Objects.equals(urlPurpose, rightValue);
            case IN -> ((Collection<?>) rightValue).contains(urlPurpose);
            default -> false;
        };



    }
}
