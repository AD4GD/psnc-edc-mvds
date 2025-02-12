import { HttpHeaders } from "@angular/common/http";
import { OAuthService } from "angular-oauth2-oidc";
import { AppConfigService } from "../../../../app.config.service";

export const getHeaders = (configService: AppConfigService, authService: OAuthService): HttpHeaders => {
    if (!configService.isOAuthConfigured()) {
        return new HttpHeaders();
    }

    var config = configService.getConfig();

    if (config.edcApiKey !== undefined) {
        return new HttpHeaders({
            'x-api-key': `${config.edcApiKey}`,
        });
    } else {
        return new HttpHeaders({
            'Authorization': `Bearer ${authService.getAccessToken()}`,
        });
    }
}
