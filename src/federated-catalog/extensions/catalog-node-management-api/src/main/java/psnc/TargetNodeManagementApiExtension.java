package psnc;

import org.eclipse.edc.runtime.metamodel.annotation.Extension;
import org.eclipse.edc.spi.system.ServiceExtension;
import org.eclipse.edc.spi.system.ServiceExtensionContext;
import org.eclipse.edc.web.spi.WebService;
import org.eclipse.edc.crawler.spi.TargetNodeDirectory;
import org.eclipse.edc.web.spi.configuration.PortMapping;
import org.eclipse.edc.web.spi.configuration.PortMappingRegistry;
import org.eclipse.edc.runtime.metamodel.annotation.Configuration;
import org.eclipse.edc.runtime.metamodel.annotation.Setting;
import org.eclipse.edc.runtime.metamodel.annotation.Settings;
import org.eclipse.edc.runtime.metamodel.annotation.Inject;

@Extension(value = "Target Node Management API")
public class TargetNodeManagementApiExtension implements ServiceExtension {

    // EDC injects services registered in the runtime
    @Inject
    private WebService webService;

    @Inject
    private TargetNodeDirectory targetNodeDirectory;

    @Inject
    private PortMappingRegistry portMappingRegistry;

    @Configuration
    private TargetsApiConfiguration apiConfiguration;

    @Override
    public void initialize(ServiceExtensionContext context) {
        portMappingRegistry.register(new PortMapping("targets", apiConfiguration.port(), apiConfiguration.path()));

        // "targets" must match web.http.targets.* configuration
        webService.registerResource("targets",
                new TargetNodeManagementApiController(targetNodeDirectory));
    }

    @Settings
    record TargetsApiConfiguration(
            @Setting(key = "web.http." + "targets" + ".port", description = "Port for " + "targets" + " api context", defaultValue = 17171 + "")
            int port,
            @Setting(key = "web.http." + "targets" + ".path", description = "Path for " + "targets" + " api context", defaultValue = "/api/targets")
            String path
    ) {

    }
}
