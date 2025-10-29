package psnc.edc.dataplane.oauth2;

import org.eclipse.edc.iam.oauth2.spi.client.Oauth2CredentialsRequest;
import org.eclipse.edc.iam.oauth2.spi.client.SharedSecretOauth2CredentialsRequest;
import org.eclipse.edc.spi.result.Result;
import org.eclipse.edc.spi.types.domain.DataAddress;
import org.jetbrains.annotations.NotNull;
import org.jetbrains.annotations.Nullable;

import java.time.Clock;
import java.util.concurrent.TimeUnit;

import static org.eclipse.edc.iam.oauth2.spi.Oauth2DataAddressSchema.CLIENT_ID;
import static org.eclipse.edc.iam.oauth2.spi.Oauth2DataAddressSchema.SCOPE;
import static org.eclipse.edc.iam.oauth2.spi.Oauth2DataAddressSchema.TOKEN_URL;
import org.eclipse.edc.spi.monitor.Monitor;

/**
 * Factory class that provides methods to build {@link Oauth2CredentialsRequest} instances
*/
public class DataPlaneHttpOauth2CredentialsRequestFactory {

    private static final String GRANT_TYPE_SCHEMA = "oauth2:grantType";
    private static final String USERNAME_SCHEMA = "oauth2:username";
    private static final String PASSWORD_SCHEMA = "oauth2:password";
    private static final String CLIENT_SECRET_SCHEMA = "oauth2:clientSecret";

    private static final long DEFAULT_TOKEN_VALIDITY = TimeUnit.MINUTES.toSeconds(5);
    private static final String GRANT_CLIENT_CREDENTIALS = "client_credentials";
    private static final String GRANT_PASSWORD = "password";

    private final Clock clock;
    private final Monitor monitor;


    public DataPlaneHttpOauth2CredentialsRequestFactory(Monitor monitor, Clock clock) {
        this.clock = clock;
        this.monitor = monitor;
    }

    public Result<Oauth2CredentialsRequest> create(DataAddress dataAddress) {
        monitor.debug("token creation requested");

        if (dataAddress.getStringProperty(GRANT_TYPE_SCHEMA).equals(GRANT_PASSWORD)) {
            monitor.debug("password");
            return createSharedSecretPasswordRequest(dataAddress);
        }
        else {
            monitor.debug("client_credentials");
            return createSharedSecretClientCredentialsRequest(dataAddress);
        }
    }

    @NotNull
    private Result<Oauth2CredentialsRequest> createSharedSecretClientCredentialsRequest(DataAddress dataAddress) {
        return Result.success(SharedSecretOauth2CredentialsRequest.Builder.newInstance()
                .url(dataAddress.getStringProperty(TOKEN_URL))
                .grantType(GRANT_CLIENT_CREDENTIALS)
                .clientId(dataAddress.getStringProperty(CLIENT_ID))
                .clientSecret(dataAddress.getStringProperty(CLIENT_SECRET_SCHEMA))
                .scope(dataAddress.getStringProperty(SCOPE))
                .build());
    }

    @NotNull
    private Result<Oauth2CredentialsRequest> createSharedSecretPasswordRequest(DataAddress dataAddress) {
        return Result.success(SharedSecretOauth2CredentialsPasswordRequest.Builder.newInstance()
                .url(dataAddress.getStringProperty(TOKEN_URL))
                .grantType(GRANT_PASSWORD)
                .clientId(dataAddress.getStringProperty(CLIENT_ID))
                .clientSecret(dataAddress.getStringProperty(CLIENT_SECRET_SCHEMA))
                .username(dataAddress.getStringProperty(USERNAME_SCHEMA))
                .password(dataAddress.getStringProperty(PASSWORD_SCHEMA))
                .scope(dataAddress.getStringProperty(SCOPE))
                .build());
    }

    @Nullable
    private Long parseLong(String v) {
        try {
            return Long.parseLong(v);
        } catch (NumberFormatException e) {
            return null;
        }
    }
}
