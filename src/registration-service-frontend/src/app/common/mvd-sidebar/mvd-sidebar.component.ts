import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ActivatedRoute, Route, Router, RouterModule, RouterOutlet } from '@angular/router';
import { MatSidenavModule } from '@angular/material/sidenav';
import { MatListModule } from '@angular/material/list';
import { MatIconModule } from '@angular/material/icon';
import { routes } from '../../app-routes.module'
import { OAuthService } from 'angular-oauth2-oidc';

export interface SidebarCategory {
  category: string,
  routes: Route[]
}

@Component({
  selector: 'mvd-sidebar',
  templateUrl: './mvd-sidebar.component.html',
  styleUrl: './mvd-sidebar.component.scss',
  standalone: false,
})
export class MvdSidebarComponent implements OnInit {

  routesCategories: SidebarCategory[];
  activeRoute: string | null = null;

  constructor(
    private router: Router, 
    private activatedRoute: ActivatedRoute,
    private oauthService: OAuthService
  ) {
    const filteredRoutes = routes.filter((x) => x.path !== '');

    const categoryMap = this.groupRoutesByCategories(filteredRoutes);

    this.routesCategories = Object.keys(categoryMap).map((category) => ({
      category,
      routes: categoryMap[category],
    }));
  }

  ngOnInit(): void {
    this.router.events.subscribe(() => {
      this.activeRoute = this.router.url;
    });

    this.activeRoute = this.router.url;
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

  private groupRoutesByCategories = (routes: Route[]) => {
    const categoryMap: Record<string, Route[]> = {};
    routes.forEach((route) => {
      const category = route.data?.category || 'Uncategorized';
      if (!categoryMap[category]) {
        categoryMap[category] = [];
      }
      categoryMap[category].push(route);
    });
    return categoryMap;
  }
}
