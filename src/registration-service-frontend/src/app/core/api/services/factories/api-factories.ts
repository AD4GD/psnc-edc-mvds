import { EdcConnectorClient } from "@think-it-labs/edc-connector-client";
import { ConfigService } from "../../../app.config.service";
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

export const getCatalogApi = (configService: ConfigService, edcConnectorClient: EdcConnectorClient): CatalogApi => {
  const isUseFakeApi = configService.getConfig().isUseFakeBackend;
  return isUseFakeApi ? new MockCatalogApiService() : new CatalogApiService(edcConnectorClient);
};

export const getBackendApi = (configService: ConfigService, http: HttpClient): BackendApi => {
  const isUseFakeApi = configService.getConfig().isUseFakeBackend;
  return isUseFakeApi ? new MockBackendApiService() : new BackendApiService(configService, http);
}

export const getClient = (
  configService: ConfigService,
  edcConnectorClient: EdcConnectorClient,
  http: HttpClient,
): RegistrationServiceClient => {
  return {
    catalog: new CatalogService(getCatalogApi(configService, edcConnectorClient)),
    backend: new BackendService(getBackendApi(configService, http)),
  };
}
