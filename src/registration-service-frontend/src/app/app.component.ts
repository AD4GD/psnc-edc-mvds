import { Component, OnInit } from '@angular/core';
import { OAuthService } from 'angular-oauth2-oidc';
import { AppConfigService } from './app.config.service';
import { FetchInterceptorService } from './core/api/services/utils/fetch-edc.interceptor';

@Component({
  selector: 'app-root',
  templateUrl: './app.component.html',
  styleUrl: './app.component.scss',
  standalone: false,
})
export class AppComponent implements OnInit {
  title = 'registration-service-frontend';

  constructor(
    private configService: AppConfigService,
    private oauthService: OAuthService,
    private interceptor: FetchInterceptorService) {
      interceptor.initFetchInterceptor();
  }

  async ngOnInit(): Promise<void> {
    if (this.configService.isOAuthConfigured()) {
      this.oauthService.configure(this.configService.getOAuthConfig()!);
    }
  }
}
