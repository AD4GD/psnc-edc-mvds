import { Component, Input } from '@angular/core';

@Component({
  selector: 'edc-demo-access-denied-banner',
  templateUrl: './access-denied-banner.component.html',
  styleUrls: ['./access-denied-banner.component.scss']
})
export class AccessDeniedBannerComponent {
  @Input() resourceName?: string;
  @Input() details?: string;

  get title(): string {
    return 'Insufficient permissions';
  }

  get message(): string {
    const resource = this.resourceName?.trim();
    if (resource) {
      return `You are not authorized to view ${resource}.`;
    }
    return 'You are not authorized to view this content.';
  }
}
