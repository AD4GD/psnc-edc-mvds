import { HttpErrorResponse } from '@angular/common/http';
import { ChangeDetectionStrategy, ChangeDetectorRef, Component, OnDestroy, OnInit } from '@angular/core';
import { CatalogBrowserService, NotificationService, SorterService, UtilService } from "../../services";
import { Router } from "@angular/router";
import { ContractOffer } from "../../models/contract-offer";
import { PageEvent } from '@angular/material/paginator';
import { DATASET_CONTEXT } from 'src/modules/app/variables';
import { Subject } from 'rxjs';
import { takeUntil } from 'rxjs/operators';
import { UnauthorizedStateService } from 'src/modules/app/auth/unauthorized-state.service';

@Component({
  selector: 'edc-demo-catalog-browser',
  templateUrl: './catalog-browser.component.html',
  styleUrls: ['./catalog-browser.component.scss'],
  changeDetection: ChangeDetectionStrategy.OnPush
})
export class CatalogBrowserComponent implements OnInit, OnDestroy {
  paginationState = {
    filteredList: [] as ContractOffer[],
    pagedList: [] as ContractOffer[],
    pageIndex: 0,
    pageSize: 20
  };
  searchText = '';
  allContractOffers: ContractOffer[] = [];
  isUnauthorized = false;
  private readonly destroy$ = new Subject<void>();

  constructor(
    private apiService: CatalogBrowserService,
    private router: Router,
    private notificationService: NotificationService,
    public readonly utilService: UtilService,
    private readonly sorterService: SorterService,
    private readonly unauthorizedState: UnauthorizedStateService,
    private readonly cdr: ChangeDetectorRef
  ) { }

  loadContractOffers() {
    this.apiService.getContractOffers().subscribe({
      next: contractOffers => {
        this.allContractOffers = contractOffers.sort((a, b) =>
          this.sorterService.naturalSort( a.assetId, b.assetId )
        );
        this.utilService.applyFilterAndPagination(
          [...this.allContractOffers],
          this.filterContractOffers.bind(this),
          this.searchText,
          this.paginationState
        );
        this.cdr.markForCheck();
      },
      error: (err: HttpErrorResponse) => {
        if (this.unauthorizedState.isUnauthorized('catalog')) {
          return;
        }
        this.notificationService.showError('Failed to load catalog');
        console.error(err);
      }
    });
  }

  filterContractOffers(mainList: ContractOffer[]): ContractOffer[] {
    return mainList.filter(contractOffer =>
      contractOffer.id.toLowerCase().includes(this.searchText.toLowerCase()) ||
      contractOffer.assetId.toLowerCase().includes(this.searchText.toLowerCase()) ||
      contractOffer.originator.toLowerCase().includes(this.searchText.toLowerCase()) ||
      contractOffer.properties.name?.toLowerCase().includes(this.searchText.toLowerCase()) || 
      contractOffer.properties.baseUrl?.toLowerCase().includes(this.searchText.toLowerCase()) ||
      this.utilService.searchThroughMetadata(this.findMetadataForAsset(contractOffer), this.searchText)
    );
  }

  ngOnInit(): void {
    this.unauthorizedState
      .isUnauthorized$('catalog')
      .pipe(takeUntil(this.destroy$))
      .subscribe((isUnauthorized) => {
        this.isUnauthorized = isUnauthorized;
        if (isUnauthorized) {
          this.allContractOffers = [];
          this.paginationState.filteredList = [];
          this.paginationState.pagedList = [];
        }
        this.cdr.markForCheck();
      });

    this.loadContractOffers();
  }

  ngOnDestroy(): void {
    this.destroy$.next();
    this.destroy$.complete();
  }
  
  onSearch() {
    this.paginationState.pageIndex = 0;
    this.utilService.applyFilterAndPagination(
      [...this.allContractOffers],
      this.filterContractOffers.bind(this),
      this.searchText,
      this.paginationState
    );
    this.cdr.markForCheck();
  }

  trackByAssetId(index: number, item: ContractOffer): string {
    return item.assetId;
  }
  
  onPageChange(event: PageEvent) {
    this.utilService.onPageChange(
      event, 
      [...this.allContractOffers],
      this.filterContractOffers.bind(this),
      this.searchText,
      this.paginationState
    );
    this.cdr.markForCheck();
  }

  findMetadataForAsset(offer: ContractOffer) {
    const metadataFromProperties = this.extractMetadataFromProperties(offer?.properties);
    if (Object.keys(metadataFromProperties).length > 0) {
      return metadataFromProperties;
    }

    const asset = offer[DATASET_CONTEXT]?.filter((_asset : any) => {
      return _asset['@id'] === offer.assetId || _asset.id === offer.assetId;
    })?.[0];
    
    if (!asset) return {};

    return this.extractMetadataFromDataset(asset);
  }

  private extractMetadataFromProperties(properties: any): Record<string, any> {
    const result: Record<string, any> = {};
    if (!properties) {
      return result;
    }

    const additionalKeys: string[] = Array.isArray(properties.additionalPropertyKeys)
      ? properties.additionalPropertyKeys
      : [];
    const valuesMap = properties.properties ?? {};

    additionalKeys.forEach((key) => {
      const normalizedKey = key.startsWith('asset:prop:') ? key.substring('asset:prop:'.length) : key;
      result[normalizedKey] = valuesMap[key];
    });

    return result;
  }

  private extractMetadataFromDataset(dataset: any): Record<string, any> {
    const result: Record<string, any> = {};
    if (!dataset || typeof dataset !== 'object') {
      return result;
    }

    Object.keys(dataset).forEach((key) => {
      if (key === '@id' || key === '@type' || key === 'dct:identifier' || key === 'dct:title') {
        return;
      }
      if (key.startsWith('dct:') || key.startsWith('dcat:')) {
        result[key] = dataset[key];
      }
    });

    return result;
  }

  onOfferClicked(contractOffer: ContractOffer): void {
    this.router.navigate(['/offer', contractOffer.assetId], {
      queryParams: {
        participantId: contractOffer.participantId,
        originator: contractOffer.originator
      }
    });
  }
}
