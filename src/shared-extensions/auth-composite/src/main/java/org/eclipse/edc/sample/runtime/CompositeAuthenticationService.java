
package org.eclipse.edc.sample.runtime;

import java.util.Arrays;
import java.util.List;
import java.util.Map;

import org.eclipse.edc.api.auth.spi.AuthenticationService;
import org.eclipse.edc.api.auth.spi.registry.ApiAuthenticationProviderRegistry;
import org.eclipse.edc.spi.monitor.Monitor;
import org.eclipse.edc.spi.system.configuration.Config;

public class CompositeAuthenticationService implements AuthenticationService {

    private final String[] compositeTypes;
    private final ApiAuthenticationProviderRegistry providerRegistry;
    private final Config config;
    private final Monitor monitor;


    public CompositeAuthenticationService(
        String[] compositeTypes,
        ApiAuthenticationProviderRegistry providerRegistry,
        Config config,
        Monitor monitor) {
        this.compositeTypes = compositeTypes;
        this.providerRegistry = providerRegistry;
        this.config = config;
        this.monitor = monitor;
    }

    @Override
    public boolean isAuthenticated(Map<String, List<String>> headers) {
        monitor.debug("Received authentication request");

        var providers = Arrays.stream(compositeTypes).map(x -> {
            return providerRegistry.resolve(x).provide(config).getContent();
        }).toList();

        for (int i = 0; i < providers.size(); i++) {
            var provider = providers.get(i);
            try {
                monitor.debug(String.format("Trying %s", compositeTypes[i]));

                if (provider.isAuthenticated(headers)) {
                    monitor.debug(String.format("%s has passed", compositeTypes[i]));
                    return true;
                }
            } catch (Exception e) {
                monitor.debug(e.getMessage());
            }
        }
        return false;
    }
}
