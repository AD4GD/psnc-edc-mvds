import { Injectable } from '@angular/core';
import { CatalogService } from '../../../services/catalog.service';
import { BackendService } from '../../../services/backend.service';

@Injectable({
  providedIn: 'root',
})
export class RegistrationServiceClient {
  constructor(
    public catalog: CatalogService,
    public backend: BackendService
  ) {}
}
