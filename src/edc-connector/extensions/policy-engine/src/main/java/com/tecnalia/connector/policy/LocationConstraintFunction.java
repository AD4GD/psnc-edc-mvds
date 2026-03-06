package com.tecnalia.connector.policy;

import org.eclipse.edc.participant.spi.ParticipantAgentPolicyContext;
import org.eclipse.edc.policy.model.Operator;
import org.eclipse.edc.policy.model.Permission;
import org.eclipse.edc.spi.monitor.Monitor;

import java.util.Collection;
import java.util.Objects;

import static java.lang.String.format;

public class LocationConstraintFunction {
    private final Monitor monitor;

    public LocationConstraintFunction(Monitor monitor) {
        this.monitor = monitor;
    }

    // Register this with ParticipantAgentPolicyContext
    public boolean evaluate(Operator operator, Object rightValue, Permission permission, ParticipantAgentPolicyContext context) {
        var participantAgent = context.participantAgent();

        monitor.debug("LOCATION Policy CLAIMS list");
        participantAgent.getClaims().forEach((k, v) -> monitor.debug(format("LOCATION Policy claims %s = %s", k, v)));
        monitor.debug("LOCATION Policy ATTRIBUTES list");
        participantAgent.getAttributes().forEach((k, v) -> monitor.debug(format("LOCATION Policy attributes %s = %s", k, v)));

        var participantId = participantAgent.getIdentity();
        var region = participantAgent.getClaims().get("region");

        monitor.debug(format("LOCATION Policy consumer ID = %s", participantId));
        monitor.debug(format("LOCATION Policy region = %s", region));
        monitor.debug(format("Operator = %s", operator));
        monitor.debug(format("Rightvalue = %s", rightValue));

        monitor.info(format("Evaluating constraint: location %s %s", operator, rightValue));
        return switch (operator) {
            case EQ  -> Objects.equals(region, rightValue);
            case NEQ -> !Objects.equals(region, rightValue);
            case IN  -> (rightValue instanceof Collection<?> c) && c.contains(region);
            default  -> false;
        };
    }
}
