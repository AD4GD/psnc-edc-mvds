
package org.eclipse.edc.sample.runtime;

import java.util.Arrays;

import org.eclipse.edc.api.auth.spi.ApiAuthenticationProvider;
import org.eclipse.edc.api.auth.spi.AuthenticationService;
import org.eclipse.edc.api.auth.spi.registry.ApiAuthenticationProviderRegistry;
import org.eclipse.edc.runtime.metamodel.annotation.Extension;
import org.eclipse.edc.runtime.metamodel.annotation.Inject;
import org.eclipse.edc.runtime.metamodel.annotation.Setting;
import org.eclipse.edc.spi.monitor.Monitor;
import org.eclipse.edc.spi.result.Result;
import org.eclipse.edc.spi.system.ServiceExtension;
import org.eclipse.edc.spi.system.ServiceExtensionContext;
import org.eclipse.edc.spi.system.configuration.Config;
import static org.eclipse.edc.web.spi.configuration.WebServiceConfigurer.WEB_HTTP_PREFIX;

import com.fasterxml.jackson.databind.ObjectMapper;

 /**
  * Extension that registers an AuthenticationService that uses API Keys and register
  * an {@link ApiAuthenticationProvider} under the type called tokenbased
  */
 @Extension(value = CompositeAuthenticationExtension.NAME)
 public class CompositeAuthenticationExtension implements ServiceExtension {

     public static final String NAME = "Composite API Authentication";
     public static final String AUTH_KEY = "auth";

     public static final String CONFIG_ALIAS = WEB_HTTP_PREFIX + ".<context>." + AUTH_KEY + ".";

     @Setting(context = CONFIG_ALIAS, value = "All types that can be applied")
     public static final String INCLUDES_TYPES = "includes";

     public static final String COMPOSITE_TYPE = "composite";
     public static final String NONE_TYPE = "none";

     @Inject
     private ApiAuthenticationProviderRegistry providerRegistry;

     private Monitor monitor;


     @Override
     public String name() {
        return NAME;
     }

     @Override
     public void initialize(ServiceExtensionContext context) {
        monitor = context.getMonitor();
        providerRegistry.register(COMPOSITE_TYPE, this::compositeProvider);
        providerRegistry.register(NONE_TYPE, this::noneProvider);
    }

     public Result<AuthenticationService> compositeProvider(Config config) {

        String[] compositeTypes = new String[0];
        var compositeTypesString = config.getString(INCLUDES_TYPES);
        ObjectMapper objectMapper = new ObjectMapper();
        try {
            compositeTypes = objectMapper.readValue(compositeTypesString, String[].class);
            monitor.debug(Arrays.toString(compositeTypes));
        } catch (Exception e) {
            e.printStackTrace();
        }

        return Result.success(new CompositeAuthenticationService(compositeTypes, providerRegistry, config, monitor));
    }

    public Result<AuthenticationService> noneProvider(Config config) {
        return Result.success(new NoneAuthenticationService(monitor));
    }
}
