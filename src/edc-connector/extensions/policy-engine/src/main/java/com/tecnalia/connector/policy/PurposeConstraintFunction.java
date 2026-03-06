package com.tecnalia.connector.policy;

import org.eclipse.edc.connector.controlplane.contract.spi.policy.ContractNegotiationPolicyContext;
import org.eclipse.edc.policy.engine.spi.PolicyContext;
import org.eclipse.edc.policy.model.Operator;
import org.eclipse.edc.policy.model.Permission;
import org.eclipse.edc.spi.monitor.Monitor;

import java.util.Collection;
import java.util.Objects;

import static java.lang.String.format;

public class PurposeConstraintFunction {
    private final Monitor monitor;

    public PurposeConstraintFunction(Monitor monitor) {
        this.monitor = monitor;
    }

    // Register this with ContractNegotiationPolicyContext
    public boolean evaluate(Operator operator, Object rightValue, Permission rule, ContractNegotiationPolicyContext context) {
        var participantAgent = context.participantAgent();

        monitor.debug("PURPOSE Policy CLAIMS list");
        participantAgent.getClaims().forEach((k, v) -> monitor.debug(format("PURPOSE Policy claims %s = %s", k, v)));
        monitor.debug("PURPOSE Policy ATTRIBUTES list");
        participantAgent.getAttributes().forEach((k, v) -> monitor.debug(format("PURPOSE Policy attributes %s = %s", k, v)));

        var participantId = participantAgent.getIdentity();
        var urlPurpose = participantAgent.getClaims().get("purpose");

        monitor.debug(format("PURPOSE consumer ID = %s", participantId));
        monitor.debug(format("PURPOSE Policy purpose = %s", urlPurpose));
        monitor.debug(format("Operator = %s", operator));
        monitor.debug(format("Rightvalue = %s", rightValue));

        monitor.info(format("Evaluating constraint: purpose %s %s", operator, rightValue));
        return switch (operator) {
            case EQ  -> Objects.equals(urlPurpose, rightValue);
            case NEQ -> !Objects.equals(urlPurpose, rightValue);
            case IN  -> (rightValue instanceof Collection<?> c) && c.contains(urlPurpose);
            default  -> false;
        };
    }
}
