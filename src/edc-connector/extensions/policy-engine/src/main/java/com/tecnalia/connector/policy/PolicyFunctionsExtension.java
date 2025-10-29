package com.tecnalia.connector.policy;

import org.eclipse.edc.connector.controlplane.contract.spi.policy.ContractNegotiationPolicyContext;
import org.eclipse.edc.connector.controlplane.contract.spi.policy.TransferProcessPolicyContext;
import org.eclipse.edc.policy.engine.spi.PolicyContext;
import org.eclipse.edc.policy.engine.spi.PolicyEngine;
import org.eclipse.edc.policy.engine.spi.RuleBindingRegistry;
import org.eclipse.edc.policy.model.Permission;
import org.eclipse.edc.runtime.metamodel.annotation.Inject;
import org.eclipse.edc.spi.monitor.Monitor;
import org.eclipse.edc.spi.system.ServiceExtension;
import org.eclipse.edc.spi.system.ServiceExtensionContext;

import static org.eclipse.edc.connector.controlplane.contract.spi.policy.ContractNegotiationPolicyContext.NEGOTIATION_SCOPE;
import static org.eclipse.edc.connector.controlplane.contract.spi.policy.TransferProcessPolicyContext.TRANSFER_SCOPE;
import static org.eclipse.edc.jsonld.spi.PropertyAndTypeNames.ODRL_USE_ACTION_ATTRIBUTE;

public class PolicyFunctionsExtension implements ServiceExtension {

    private static final String TIME_INTERVAL = "timeInterval";
    private static final String TIME_INTERVAL_EVALUATION_KEY = "https://w3id.org/edc/v0.0.1/ns/" + TIME_INTERVAL;

    private static final String PURPOSE = "purpose";
    private static final String PURPOSE_EVALUATION_KEY = "https://w3id.org/edc/v0.0.1/ns/" + PURPOSE;

    private static final String LOCATION = "regionLocation";
    private static final String LOCATION_EVALUATION_KEY = "https://w3id.org/edc/v0.0.1/ns/" + LOCATION;

    @Inject private RuleBindingRegistry ruleBindingRegistry;
    @Inject private PolicyEngine policyEngine;
    @Inject private Monitor monitor;

    @Override
    public String name() { return "Policy functions."; }

    @Override
    public void initialize(ServiceExtensionContext context) {
        var log = context.getMonitor();
        log.info("Starting custom policies.");

        // 1) Bind the action AND each leftOperand to the scopes you want
        ruleBindingRegistry.bind(ODRL_USE_ACTION_ATTRIBUTE, NEGOTIATION_SCOPE);
        ruleBindingRegistry.bind(ODRL_USE_ACTION_ATTRIBUTE, TRANSFER_SCOPE);

        ruleBindingRegistry.bind(TIME_INTERVAL_EVALUATION_KEY, NEGOTIATION_SCOPE);
        ruleBindingRegistry.bind(PURPOSE_EVALUATION_KEY,      NEGOTIATION_SCOPE);
        ruleBindingRegistry.bind(LOCATION_EVALUATION_KEY,     NEGOTIATION_SCOPE);

        // 2) Register functions for the specific context types
        var timeFn     = new TimeIntervalConstraintFunction(monitor);
        var purposeFn  = new PurposeConstraintFunction(monitor);
        var locationFn = new LocationConstraintFunction(monitor);

        // Time constraint evaluated in generic PolicyContext (works across scopes where bound)
        policyEngine.registerFunction(PolicyContext.class, Permission.class, TIME_INTERVAL_EVALUATION_KEY, timeFn::evaluate);

        // Purpose uses the contract negotiation context
        policyEngine.registerFunction(ContractNegotiationPolicyContext.class, Permission.class, PURPOSE_EVALUATION_KEY, purposeFn::evaluate);

        // Location uses the participant-agent-aware context
        policyEngine.registerFunction(ContractNegotiationPolicyContext.class, Permission.class, LOCATION_EVALUATION_KEY, locationFn::evaluate);
    }
}
