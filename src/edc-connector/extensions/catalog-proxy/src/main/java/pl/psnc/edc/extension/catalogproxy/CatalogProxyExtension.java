package pl.psnc.edc.extension.catalogproxy;

import org.eclipse.edc.runtime.metamodel.annotation.Extension;
import org.eclipse.edc.runtime.metamodel.annotation.Inject;
import org.eclipse.edc.spi.message.RemoteMessageDispatcherRegistry;
import org.eclipse.edc.spi.system.ServiceExtension;
import org.eclipse.edc.spi.system.ServiceExtensionContext;
import org.eclipse.edc.web.spi.WebService;
import org.eclipse.edc.spi.types.TypeManager;
import pl.psnc.edc.extension.catalogproxy.controller.CatalogProxyController;
import org.eclipse.edc.web.spi.configuration.PortMapping;
import org.eclipse.edc.web.spi.configuration.PortMappingRegistry;
import org.eclipse.edc.runtime.metamodel.annotation.Configuration;
import org.eclipse.edc.runtime.metamodel.annotation.Setting;
import org.eclipse.edc.runtime.metamodel.annotation.Settings;
import org.eclipse.edc.runtime.metamodel.annotation.Inject;

@Extension(value = CatalogProxyExtension.NAME)
public class CatalogProxyExtension implements ServiceExtension {

    public static final String NAME = "Catalog Proxy Extension";

    @Inject
    private WebService webService;

    @Inject
    private RemoteMessageDispatcherRegistry dispatcherRegistry;

    @Inject
    private TypeManager typeManager;

    @Inject
    private PortMappingRegistry portMappingRegistry;

    @Configuration
    private CatalogProxyApiConfiguration apiConfiguration;

    @Override
    public String name() {
        return NAME;
    }

    @Override
    public void initialize(ServiceExtensionContext context) {
        var monitor = context.getMonitor();
        monitor.info("Initializing Catalog Proxy Extension");

        portMappingRegistry.register(new PortMapping("catalogproxy", apiConfiguration.port(), apiConfiguration.path()));

        var controller = new CatalogProxyController(monitor, dispatcherRegistry, context.getConfig(), typeManager.getMapper());
        webService.registerResource("catalogproxy", controller);
    }

    @Settings
    record CatalogProxyApiConfiguration(
            @Setting(key = "web.http." + "catalogproxy" + ".port", description = "Port for " + "catalogproxy" + " api context", defaultValue = 8086 + "")
            int port,
            @Setting(key = "web.http." + "catalogproxy" + ".path", description = "Path for " + "catalogproxy" + " api context", defaultValue = "/api/catalog-proxy")
            String path
    ) {

    }
}
