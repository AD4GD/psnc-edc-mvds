package psnc.edc.dataplane.oauth2;

import org.eclipse.edc.connector.dataplane.http.spi.HttpDataAddress;
import org.eclipse.edc.connector.dataplane.http.spi.HttpParamsDecorator;
import org.eclipse.edc.connector.dataplane.http.spi.HttpRequestParams;
import org.eclipse.edc.iam.oauth2.spi.Oauth2DataAddressValidator;
import org.eclipse.edc.iam.oauth2.spi.client.Oauth2Client;
import org.eclipse.edc.spi.EdcException;
import org.eclipse.edc.spi.types.domain.transfer.DataFlowStartMessage;

/**
 * Requests the OAuth2 token if configured in the DataAddress
*/
public class DataPlaneHttpOauth2RequestParamsDecorator implements HttpParamsDecorator {

    private final DataPlaneHttpOauth2CredentialsRequestFactory requestFactory;
    private final Oauth2Client client;
    private final Oauth2DataAddressValidator validator = new Oauth2DataAddressValidator();

    public DataPlaneHttpOauth2RequestParamsDecorator(DataPlaneHttpOauth2CredentialsRequestFactory requestFactory, Oauth2Client client) {
        this.requestFactory = requestFactory;
        this.client = client;
    }

    @Override
    public HttpRequestParams.Builder decorate(DataFlowStartMessage request, HttpDataAddress address, HttpRequestParams.Builder params) {
        if (validator.test(address)) {
            return requestFactory.create(address)
                .compose(client::requestToken)
                .map(tokenRepresentation -> params.header("Authorization", "Bearer " + tokenRepresentation.getToken()))
                .orElseThrow(failure -> new EdcException("Cannot authenticate through OAuth2: " + failure.getFailureDetail()));
        } else {
            return params;
        }
    }
}