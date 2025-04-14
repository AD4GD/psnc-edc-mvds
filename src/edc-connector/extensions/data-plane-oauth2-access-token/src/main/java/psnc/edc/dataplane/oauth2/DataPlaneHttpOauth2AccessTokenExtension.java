package psnc.edc.dataplane.oauth2;

import org.eclipse.edc.connector.dataplane.http.spi.HttpRequestParamsProvider;
import org.eclipse.edc.iam.oauth2.spi.client.Oauth2Client;
import org.eclipse.edc.runtime.metamodel.annotation.Extension;
import org.eclipse.edc.runtime.metamodel.annotation.Inject;
import org.eclipse.edc.spi.monitor.Monitor;
import org.eclipse.edc.spi.system.ServiceExtension;
import org.eclipse.edc.spi.system.ServiceExtensionContext;

import java.time.Clock;

/**
 * Modified implementation of data-plane-http-oauth2 extension
 * with added password grant type support
*/
@Extension(value = DataPlaneHttpOauth2AccessTokenExtension.NAME)
public class DataPlaneHttpOauth2AccessTokenExtension implements ServiceExtension {
    public static final String NAME = "Data Plane HTTP OAuth2";

    @Inject
    private Clock clock;

    @Inject
    private HttpRequestParamsProvider paramsProvider;

    @Inject
    private Oauth2Client oauth2Client;

    @Inject
    private Monitor monitor;

    @Override
    public String name() {
        return NAME;
    }
 
    @Override
    public void initialize(ServiceExtensionContext context) {
        var requestFactory = new DataPlaneHttpOauth2CredentialsRequestFactory(monitor, clock);
        var oauth2ParamsDecorator = new DataPlaneHttpOauth2RequestParamsDecorator(monitor, requestFactory, oauth2Client);

        paramsProvider.registerSourceDecorator(oauth2ParamsDecorator);
    }
}