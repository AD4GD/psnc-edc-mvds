import { Component } from '@angular/core';
import { MvdSidebarComponent } from './common/mvd-sidebar/mvd-sidebar.component';

@Component({
  selector: 'app-root',
  imports: [MvdSidebarComponent],
  templateUrl: './app.component.html',
  styleUrl: './app.component.scss'
})
export class AppComponent {
  title = 'registration-service-frontend';
}
