package psnc.edc.dataplane.oauth2;

import org.eclipse.edc.connector.dataplane.http.spi.HttpRequestParamsProvider;
import org.eclipse.edc.iam.oauth2.spi.client.Oauth2Client;
import org.eclipse.edc.runtime.metamodel.annotation.Extension;
import org.eclipse.edc.runtime.metamodel.annotation.Inject;
import org.eclipse.edc.spi.system.ServiceExtension;
import org.eclipse.edc.spi.system.ServiceExtensionContext;

import java.time.Clock;

/**
 * Provides support for adding OAuth2 authentication to http data transfer
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

    @Override
    public String name() {
        return NAME;
    }
 
    @Override
    public void initialize(ServiceExtensionContext context) {
        var requestFactory = new DataPlaneHttpOauth2CredentialsRequestFactory(clock);
        var oauth2ParamsDecorator = new DataPlaneHttpOauth2RequestParamsDecorator(requestFactory, oauth2Client);

        paramsProvider.registerSourceDecorator(oauth2ParamsDecorator);
    }
}