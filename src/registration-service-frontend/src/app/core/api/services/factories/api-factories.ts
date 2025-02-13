import { EdcConnectorClient } from "@think-it-labs/edc-connector-client";
import { MockBackendApiService } from "../fake/mock-backend-api.service";
import { MockCatalogApiService } from "../fake/mock-catalog-api.service";
import { BackendApiService } from "../impl/backend-api.service";
import { CatalogApiService } from "../impl/catalog-api.service";
import { RegistrationServiceClient } from "../impl/registration-service-client";
import { BackendApi } from "../interfaces/backend-api.interface";
import { CatalogApi } from "../interfaces/catalog-api.interface";
import { CatalogService } from "../../../services/catalog.service";
import { BackendService } from "../../../services/backend.service";
import { HttpClient } from "@angular/common/http";
import { AppConfigService } from "../../../../app.config.service";
import { OAuthService } from "angular-oauth2-oidc";

const getCatalogApi = (configService: AppConfigService, edcConnectorClient: EdcConnectorClient): CatalogApi => {
  const isUseFakeApi = configService.getConfig().isUseFakeBackend;
  return isUseFakeApi === true ? new MockCatalogApiService() : new CatalogApiService(edcConnectorClient);
};

const getBackendApi = (configService: AppConfigService, authService: OAuthService, http: HttpClient): BackendApi => {
  const isUseFakeApi = configService.getConfig().isUseFakeBackend;
  console.log(http);
  return isUseFakeApi === true ? new MockBackendApiService() : new BackendApiService(configService, authService, http);
}

export const getClient = (
  configService: AppConfigService,
  edcConnectorClient: EdcConnectorClient,
  authService: OAuthService,
  http: HttpClient,
): RegistrationServiceClient => {
  console.log(http);
  return {
    catalog: new CatalogService(getCatalogApi(configService, edcConnectorClient)),
    backend: new BackendService(getBackendApi(configService, authService, http)),
  };
}
