package com.tecnalia.connector.policy;

import org.eclipse.edc.policy.engine.spi.PolicyContext;
import org.eclipse.edc.policy.model.Operator;
import org.eclipse.edc.policy.model.Permission;
import org.eclipse.edc.spi.monitor.Monitor;

import java.time.ZoneOffset;
import java.time.ZonedDateTime;

import static java.lang.String.format;

public class TimeIntervalConstraintFunction {
    private final Monitor monitor;

    public TimeIntervalConstraintFunction(Monitor monitor) {
        this.monitor = monitor;
    }

    // Register this with PolicyContext (or a narrower context if you prefer)
    public boolean evaluate(Operator operator, Object rightValue, Permission rule, PolicyContext context) {
        var current = getCurrentDate();
        var dateValue = getDateOf(String.valueOf(rightValue));
        monitor.info(format("Evaluating constraint: current %s TimeInterval %s %s", current, operator, rightValue));

        return switch (operator) {
            case EQ  -> current.isEqual(dateValue);
            case NEQ -> !current.isEqual(dateValue);
            case LT  -> current.isBefore(dateValue);
            case LEQ -> !current.isAfter(dateValue);
            case GT  -> current.isAfter(dateValue);
            case GEQ -> !current.isBefore(dateValue);
            default  -> false;
        };
    }

    private static ZonedDateTime getDateOf(final String calendar) {
        return ZonedDateTime.parse(calendar);
    }

    public static ZonedDateTime getCurrentDate() {
        return ZonedDateTime.now(ZoneOffset.UTC);
    }
}
