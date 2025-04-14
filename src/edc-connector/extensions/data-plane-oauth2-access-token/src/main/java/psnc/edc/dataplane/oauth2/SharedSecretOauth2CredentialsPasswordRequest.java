package psnc.edc.dataplane.oauth2;

import com.fasterxml.jackson.annotation.JsonCreator;
import org.jetbrains.annotations.NotNull;
import org.eclipse.edc.iam.oauth2.spi.client.Oauth2CredentialsRequest;

import java.util.Objects;

public class SharedSecretOauth2CredentialsPasswordRequest extends Oauth2CredentialsRequest {

    private static final String CLIENT_ID = "client_id";
    private static final String CLIENT_SECRET = "client_secret";
    private static final String USERNAME = "username";
    private static final String PASSWORD = "password";

    @NotNull
    public String getClientId() {
        return params.get(CLIENT_ID);
    }

    @NotNull
    public String getClientSecret() {
        return params.get(CLIENT_SECRET);
    }

    @NotNull
    public String getUser() {
        return params.get(USERNAME);
    }

    @NotNull
    public String getPassword() {
        return params.get(PASSWORD);
    }

    public static class Builder<B extends SharedSecretOauth2CredentialsPasswordRequest.Builder<B>> extends Oauth2CredentialsRequest.Builder<SharedSecretOauth2CredentialsPasswordRequest, SharedSecretOauth2CredentialsPasswordRequest.Builder<B>> {

        protected Builder(SharedSecretOauth2CredentialsPasswordRequest request) {
            super(request);
        }

        @JsonCreator
        public static <B extends SharedSecretOauth2CredentialsPasswordRequest.Builder<B>> SharedSecretOauth2CredentialsPasswordRequest.Builder<B> newInstance() {
            return new SharedSecretOauth2CredentialsPasswordRequest.Builder<>(new SharedSecretOauth2CredentialsPasswordRequest());
        }

        public B clientSecret(String secret) {
            param(CLIENT_SECRET, secret);
            return self();
        }

        public B clientId(String id) {
            param(CLIENT_ID, id);
            return self();
        }

        public B username(String secret) {
            param(USERNAME, secret);
            return self();
        }

        public B password(String id) {
            param(PASSWORD, id);
            return self();
        }

        @SuppressWarnings("unchecked")
        @Override
        public B self() {
            return (B) this;
        }

        @Override
        public SharedSecretOauth2CredentialsPasswordRequest build() {
            Objects.requireNonNull(request.params.get(CLIENT_ID), CLIENT_ID);
            Objects.requireNonNull(request.params.get(CLIENT_SECRET), CLIENT_SECRET);
            Objects.requireNonNull(request.params.get(USERNAME), USERNAME);
            Objects.requireNonNull(request.params.get(PASSWORD), PASSWORD);
            return super.build();
        }
    }
}
