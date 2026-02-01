package pl.psnc.edc.extension.catalogproxy;

import org.eclipse.edc.runtime.metamodel.annotation.Extension;
import org.eclipse.edc.runtime.metamodel.annotation.Inject;
import org.eclipse.edc.spi.message.RemoteMessageDispatcherRegistry;
import org.eclipse.edc.spi.system.ServiceExtension;
import org.eclipse.edc.spi.system.ServiceExtensionContext;
import org.eclipse.edc.web.spi.WebService;
import org.eclipse.edc.spi.types.TypeManager;
import pl.psnc.edc.extension.catalogproxy.controller.CatalogProxyController;

@Extension(value = CatalogProxyExtension.NAME)
public class CatalogProxyExtension implements ServiceExtension {

    public static final String NAME = "Catalog Proxy Extension";

    @Inject
    private WebService webService;

    @Inject
    private RemoteMessageDispatcherRegistry dispatcherRegistry;
    
    @Inject
    private TypeManager typeManager;

    @Override
    public String name() {
        return NAME;
    }

    @Override
    public void initialize(ServiceExtensionContext context) {
        var monitor = context.getMonitor();
        monitor.info("Initializing Catalog Proxy Extension");

        var controller = new CatalogProxyController(monitor, dispatcherRegistry, context.getConfig(), typeManager.getMapper());
        webService.registerResource("catalogproxy", controller);
    }
}
