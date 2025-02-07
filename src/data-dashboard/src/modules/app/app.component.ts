import { Component, OnInit } from '@angular/core';
import { Title } from '@angular/platform-browser';
import { ActivatedRoute, NavigationEnd, Router } from '@angular/router';
import { filter, map } from 'rxjs/operators';
import {AppConfigService} from "./app-config.service";
import { OAuthService } from 'angular-oauth2-oidc';
import { FetchInterceptorService } from './fetch-edc.interceptor';

@Component({
  selector: 'app-root',
  templateUrl: './app.component.html',
  styleUrls: ['./app.component.scss']
})
export class AppComponent implements OnInit {

  constructor(
    private router: Router,
    private titleService: Title,
    private configService: AppConfigService,
    private activatedRoute: ActivatedRoute,
    private oauthService: OAuthService,
    private fetchInterceptor: FetchInterceptorService) {
      fetchInterceptor.initFetchInterceptor();
  }

  async ngOnInit(): Promise<void> {
    if (this.configService.isOAuthConfigured()) {
      this.oauthService.configure(this.configService.getOAuthConfig()!);
    }

    const appTitle = this.titleService.getTitle();
    this.router
      .events
      .pipe(
        filter(event => event instanceof NavigationEnd),
        map(() => {
          const child = this.activatedRoute.firstChild;
          if (child?.snapshot.data['title']) {
            return child.snapshot.data['title'];
          }
          return appTitle;
        })
      ).subscribe((title: string) => {
        this.titleService.setTitle(title);
    });
  }

  themeClass(): string | undefined {
    return this.configService.getConfig()?.theme;
  }
}
