import { HttpErrorResponse } from '@angular/common/http';
import { Component, OnDestroy, OnInit } from '@angular/core';
import { CatalogBrowserService, NotificationService, SorterService, UtilService } from "../../services";
import { Router } from "@angular/router";
import { ContractOffer } from "../../models/contract-offer";
import { PageEvent } from '@angular/material/paginator';
import { DATASET_CONTEXT, METADATA_CONTEXT } from 'src/modules/app/variables';
import { Subject } from 'rxjs';
import { takeUntil } from 'rxjs/operators';
import { UnauthorizedStateService } from 'src/modules/app/auth/unauthorized-state.service';

@Component({
  selector: 'edc-demo-catalog-browser',
  templateUrl: './catalog-browser.component.html',
  styleUrls: ['./catalog-browser.component.scss']
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
    private readonly unauthorizedState: UnauthorizedStateService
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
  }
  
  onPageChange(event: PageEvent) {
    this.utilService.onPageChange(
      event, 
      [...this.allContractOffers],
      this.filterContractOffers.bind(this),
      this.searchText,
      this.paginationState
    );
  }

  findMetadataForAsset(offer: ContractOffer) {
    const asset = offer[DATASET_CONTEXT]?.filter((_asset : any) => {
      return _asset['@id'] === offer.assetId || _asset.id === offer.assetId;
    })?.[0];
    
    if (!asset) return {};
    
    if (asset['metadata']) {
      return asset['metadata'];
    }
    
    // Fallback to METADATA_CONTEXT (old JSON-LD transformed format)
    return asset[METADATA_CONTEXT]?.[0] || {};
  }

  onOfferClicked(contractOffer: ContractOffer): void {
    this.router.navigate(['/offer', contractOffer.assetId], {
      queryParams: {
        participantId: contractOffer.participantId
      }
    });
  }
}
