import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ActivatedRoute, Route, Router, RouterModule, RouterOutlet } from '@angular/router';
import { MatSidenavModule } from '@angular/material/sidenav';
import { MatListModule } from '@angular/material/list';
import { MatIconModule } from '@angular/material/icon';
import { routes } from '../../app.routes'

export interface SidebarCategory {
  category: string,
  routes: Route[]
}

@Component({
  selector: 'mvd-sidebar',
  imports: [
    CommonModule,
    RouterModule,
    RouterOutlet, 
    MatSidenavModule, 
    MatListModule,
    MatIconModule
  ],
  templateUrl: './mvd-sidebar.component.html',
  styleUrl: './mvd-sidebar.component.scss'
})
export class MvdSidebarComponent implements OnInit {

  routesCategories: SidebarCategory[];
  activeRoute: string | null = null;

  constructor(private router: Router , private activatedRoute: ActivatedRoute) {
    const filteredRoutes = routes.filter((x) => x.path !== '');

    const categoryMap = this.groupRoutesByCategories(filteredRoutes);

    this.routesCategories = Object.keys(categoryMap).map((category) => ({
      category,
      routes: categoryMap[category],
    }));
  }

  ngOnInit(): void {
    this.router.events.subscribe(() => {
      this.activeRoute = this.router.url; // Tracks the current active route
    });

    // Set initial active route when the page loads
    this.activeRoute = this.router.url;
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
