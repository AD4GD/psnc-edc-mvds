import { Component } from '@angular/core';
import { BreakpointObserver, Breakpoints } from '@angular/cdk/layout';
import { Observable } from 'rxjs';
import { map, shareReplay } from 'rxjs/operators';
import { routes } from '../../app-routing.module';
import { Title } from '@angular/platform-browser';
import { OAuthService } from 'angular-oauth2-oidc';

@Component({
  selector: 'app-navigation',
  templateUrl: './navigation.component.html',
  styleUrls: ['./navigation.component.scss']
})
export class NavigationComponent {

  isHandset$: Observable<boolean> = this.breakpointObserver.observe(Breakpoints.Handset)
    .pipe(
      map(result => result.matches),
      shareReplay()
    );

  routes = routes;

  constructor(
    public titleService: Title,
    private breakpointObserver: BreakpointObserver,
    private oauthService: OAuthService) {
  }
  
  logout() {
    this.oauthService.logOut();
  }

  isLoggedIn() {
    return this.oauthService.getAccessToken() != null;
  }

  getUsername() {
    return this.oauthService.getIdentityClaims()?.preferred_username;
  }
}
