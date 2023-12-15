package org.eclipse.edc.extension.assetcollect;

import org.eclipse.edc.spi.system.ServiceExtension;
import org.eclipse.edc.spi.system.ServiceExtensionContext;

import org.eclipse.edc.runtime.metamodel.annotation.Extension;
import org.eclipse.edc.runtime.metamodel.annotation.Inject;
import org.eclipse.edc.runtime.metamodel.annotation.Setting;

import org.eclipse.edc.web.spi.WebService;

import org.eclipse.edc.connector.api.management.configuration.ManagementApiConfiguration;

@Extension(value = AssetCollectorEndpointExtension.NAME)
public class AssetCollectorEndpointExtension implements ServiceExtension {

    public static final String NAME = "Management API: Asset";

    @Setting
    public static final String EDC_API_ASSET_COLLECTOR_FILE = "edc.api.asset.collector.file";

    @Setting
    public static final String WEB_HTTP_MANAGEMENT_PATH = "web.http.management.path";

    @Setting
    public static final String WEB_HTTP_MANAGEMENT_PORT = "web.http.management.port";

    @Inject
    private WebService webService;

    @Inject
    private ManagementApiConfiguration config;

    @Override
    public String name() {
        return NAME;
    }


    @Override
    public void initialize(ServiceExtensionContext context) {
        webService.registerResource(config.getContextAlias(),
                                    new ApiCollector(
                                            context.getMonitor(),
                                            context.getSetting(EDC_API_ASSET_COLLECTOR_FILE, ""),
                                            context.getSetting(WEB_HTTP_MANAGEMENT_PATH, ""),
                                            context.getSetting(WEB_HTTP_MANAGEMENT_PORT, "")
                                    ));

    }
}
