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

import org.eclipse.edc.policy.engine.spi.AtomicConstraintFunction;
import org.eclipse.edc.policy.engine.spi.PolicyContext;
import org.eclipse.edc.policy.model.Operator;
import org.eclipse.edc.policy.model.Permission;
import org.eclipse.edc.spi.monitor.Monitor;
import org.jetbrains.annotations.Nullable;

import java.time.ZoneOffset;
import java.time.ZonedDateTime;
import static java.lang.String.format;


public class TimeIntervalConstraintFunction implements AtomicConstraintFunction<Permission> {
    private final Monitor monitor;

    public TimeIntervalConstraintFunction(Monitor monitor) {
        this.monitor = monitor;
    }

    @Override
    public boolean evaluate(Operator operator, Object rightValue, Permission rule, PolicyContext context) {
        final var current = getCurrentDate();
        final var dateValue = getDateOf(rightValue.toString());
        monitor.info(format("Evaluating constraint: current %s TimeInterval %s %s", current.toString(), operator, rightValue.toString()));
        switch (operator) {
            case EQ:
                return current.isEqual(dateValue);
            case NEQ:
                return !current.isEqual(dateValue);
            case LT:
                return current.isBefore(dateValue);
            case LEQ:
                return !current.isAfter(dateValue);
            case GT:
                return current.isAfter(dateValue);
            case GEQ:
                return !current.isBefore(dateValue);
            default:
                return false;
        }
    }


    /**
     * Convert a string to a {@link ZonedDateTime}.
     *
     * @param calendar The time as string.
     * @return The new ZonedDateTime object.
     * @throws DateTimeParseException if the string could not be converted.
     */
    private static ZonedDateTime getDateOf(final String calendar) {
        return ZonedDateTime.parse(calendar);
    }


     /**
     * Get current system date.
     *
     * @return The date object.
     */
    public static ZonedDateTime getCurrentDate() {
        return ZonedDateTime.now(ZoneOffset.UTC);
    }
}
