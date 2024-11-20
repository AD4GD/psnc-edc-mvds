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

import org.eclipse.edc.policy.engine.spi.PolicyEngine;
import org.eclipse.edc.policy.engine.spi.RuleBindingRegistry;
import org.eclipse.edc.policy.model.Permission;
import org.eclipse.edc.runtime.metamodel.annotation.Inject;
import org.eclipse.edc.spi.monitor.Monitor;
import org.eclipse.edc.spi.system.ServiceExtension;
import org.eclipse.edc.spi.system.ServiceExtensionContext;
import org.eclipse.edc.spi.types.TypeManager;
import org.eclipse.edc.connector.controlplane.contract.spi.policy.ContractNegotiationPolicyContext;
import org.eclipse.edc.connector.controlplane.contract.spi.policy.TransferProcessPolicyContext;
import org.eclipse.edc.policy.engine.spi.PolicyContext;

import static org.eclipse.edc.connector.controlplane.contract.spi.policy.ContractNegotiationPolicyContext.NEGOTIATION_SCOPE;
import static org.eclipse.edc.connector.controlplane.contract.spi.policy.TransferProcessPolicyContext.TRANSFER_SCOPE;
import static org.eclipse.edc.jsonld.spi.PropertyAndTypeNames.ODRL_USE_ACTION_ATTRIBUTE;
import static org.eclipse.edc.policy.engine.spi.PolicyEngine.ALL_SCOPES;
import static org.eclipse.edc.policy.model.OdrlNamespace.ODRL_SCHEMA;
//import static org.eclipse.edc.spi.CoreConstants.EDC_NAMESPACE;


/**
 * Extension to initialize the policies.
 */

public class PolicyFunctionsExtension implements ServiceExtension {

    private static final String TIME_INTERVAL = "timeInterval";
    private static final String TIME_INTERVAL_EVALUATION_KEY = "https://w3id.org/edc/v0.0.1/ns/" + TIME_INTERVAL;
    private static final String PURPOSE = "purpose";
    private static final String PURPOSE_EVALUATION_KEY = "https://w3id.org/edc/v0.0.1/ns/" + PURPOSE;
    private static final String LOCATION = "location";
    private static final String LOCATION_EVALUATION_KEY = "https://w3id.org/edc/v0.0.1/ns/" + LOCATION;

    @Inject
    private RuleBindingRegistry ruleBindingRegistry;

    @Inject
    private PolicyEngine policyEngine;

    @Inject
    private TypeManager typeManager;

    @Inject
    private Monitor monitor;

    @Override
    public String name() {
        return "Policy functions.";
    }

    /**
     * Initializes the extension by binding the policies to the rule binding registry.
     *
     * @param context service extension context.
     */
    @Override
    public void initialize(ServiceExtensionContext context) {
        Monitor monitor = context.getMonitor();
        monitor.info("Starting custom policies.");

        ruleBindingRegistry.bind(ODRL_USE_ACTION_ATTRIBUTE, ALL_SCOPES);
        ruleBindingRegistry.bind(TIME_INTERVAL_EVALUATION_KEY, NEGOTIATION_SCOPE);
        policyEngine.registerScope(ALL_SCOPES, PolicyContext.class);
        policyEngine.registerScope(NEGOTIATION_SCOPE, ContractNegotiationPolicyContext.class);
        policyEngine.registerScope(TRANSFER_SCOPE, TransferProcessPolicyContext.class);
        policyEngine.registerFunction(ALL_SCOPES, Permission.class, TIME_INTERVAL_EVALUATION_KEY, new TimeIntervalConstraintFunction(monitor));
        ruleBindingRegistry.bind(PURPOSE_EVALUATION_KEY, NEGOTIATION_SCOPE);
        policyEngine.registerFunction(ALL_SCOPES, Permission.class, PURPOSE_EVALUATION_KEY, new PurposeConstraintFunction(monitor));
        ruleBindingRegistry.bind(LOCATION_EVALUATION_KEY, NEGOTIATION_SCOPE);
        policyEngine.registerFunction(ALL_SCOPES, Permission.class, LOCATION_EVALUATION_KEY, new LocationConstraintFunction(monitor));

    }

}
