import { HttpErrorResponse } from '@angular/common/http';
import { ChangeDetectorRef, Component, OnDestroy, OnInit } from '@angular/core';
import { first } from 'rxjs/operators';
import { MatDialog } from '@angular/material/dialog';
import { AssetInput, Asset } from "../../../mgmt-api-client/model";
import { AssetService, QUERY_LIMIT } from "../../../mgmt-api-client";
import { AssetEditorDialog } from "../asset-editor-dialog/asset-editor-dialog.component";
import { ConfirmationDialogComponent, ConfirmDialogModel } from "../confirmation-dialog/confirmation-dialog.component";
import { NotificationService, SorterService, UtilService } from "../../services";
import { PageEvent } from '@angular/material/paginator';
import { MetadataDisplayComponent } from '../common/metadata-display/metadata-display.component';
import { METADATA_CONTEXT } from 'src/modules/app/variables';
import { Subject } from 'rxjs';
import { takeUntil } from 'rxjs/operators';
import { UnauthorizedStateService } from 'src/modules/app/auth/unauthorized-state.service';


@Component({
  selector: 'edc-demo-asset-viewer',
  templateUrl: './asset-viewer.component.html',
  styleUrls: ['./asset-viewer.component.scss']
})
export class AssetViewerComponent implements OnInit, OnDestroy {
  paginationState = {
    filteredList: [] as Asset[],
    pagedList: [] as Asset[],
    pageIndex: 0,
    pageSize: 20
  };
  allAssets: Asset[] = [];
  searchText = '';
  isTransferring = false;
  isUnauthorized = false;
  private readonly destroy$ = new Subject<void>();

  constructor(
    private assetService: AssetService,
    private notificationService: NotificationService,
    private readonly dialog: MatDialog,
    private readonly metadataViewDialog: MatDialog,
    private readonly sorterService: SorterService,
    private readonly cdref: ChangeDetectorRef,
    private readonly unauthorizedState: UnauthorizedStateService,
    public readonly utilService: UtilService,
  ) { }

  loadAssets() {
    this.assetService.requestAssets({ 
      limit: QUERY_LIMIT,
      offset: 0 
    }).subscribe({
      next: assets => {
      this.allAssets = assets.sort((a, b) =>
        this.sorterService.naturalSort(
          a.properties.optionalValue<string>('edc', 'name') || a['@id'],
          b.properties.optionalValue<string>('edc', 'name') || b['@id'] 
        )
      );
      this.utilService.applyFilterAndPagination(
        [...this.allAssets],
        this.filterAssets.bind(this),
        this.searchText,
        this.paginationState
      );
      },
      error: (err: HttpErrorResponse) => {
        if (this.unauthorizedState.isUnauthorized('management')) {
          return;
        }
        this.showError(err as any, 'Failed to load assets');
      }
    });
  }

  filterAssets(mainList: Asset[]): Asset[] {
    return mainList.filter(asset =>
      (asset.properties.optionalValue<string>('edc', 'name') || '').toLowerCase().includes(this.searchText.toLowerCase()) ||
      (asset.properties.optionalValue<string>('edc', 'baseUrl') || '').toLowerCase().includes(this.searchText.toLowerCase()) ||
      this.utilService.searchThroughMetadata(this.findMetadataForAsset(asset), this.searchText) ||
      asset.id.toLowerCase().includes(this.searchText.toLowerCase())
    );
  }

  ngOnInit(): void {
    this.unauthorizedState
      .isUnauthorized$('management')
      .pipe(takeUntil(this.destroy$))
      .subscribe((isUnauthorized) => {
        this.isUnauthorized = isUnauthorized;
        if (isUnauthorized) {
          this.allAssets = [];
          this.paginationState.filteredList = [];
          this.paginationState.pagedList = [];
        }
      });

    this.loadAssets();
  }

  ngOnDestroy(): void {
    this.destroy$.next();
    this.destroy$.complete();
  }

  isBusy() {
    return this.isTransferring;
  }

  onSearch() {
    this.paginationState.pageIndex = 0;
    this.utilService.applyFilterAndPagination(
      [...this.allAssets],
      this.filterAssets.bind(this),
      this.searchText,
      this.paginationState
    );
  }

  onPageChange(event: PageEvent) {
    this.utilService.onPageChange(
      event, 
      [...this.allAssets],
      this.filterAssets.bind(this), 
      this.searchText,
      this.paginationState
    );
  }

  onDelete(asset: Asset) {
    const dialogData = ConfirmDialogModel.forDelete("asset", `"${asset.id}"`)
    const ref = this.dialog.open(ConfirmationDialogComponent, {data: dialogData});

    ref.afterClosed().subscribe({
      next: res => {
        if (res) {
          this.assetService.removeAsset(asset.id).subscribe({
            next: () => this.loadAssets(),
            // next: () => this.fetch$.next(null),
            error: err => this.showError(err, "This asset cannot be deleted"),
            complete: () => this.notificationService.showInfo("Successfully deleted")
          });
        }
      }
    });
  }

  onCreate() {
    const dialogRef = this.dialog.open(AssetEditorDialog);
    dialogRef.afterClosed().pipe(first()).subscribe((result: { assetInput?: AssetInput }) => {
      const newAsset = result?.assetInput;
      if (newAsset) {
        this.assetService.createAsset(newAsset).subscribe({
          next: ()=> this.loadAssets(),
          error: err => this.showError(err, "This asset cannot be created"),
          complete: () => this.notificationService.showInfo("Successfully created"),
        })
      }
    })
  }
  private showError(error: string, errorMessage: string) {
    this.notificationService.showError(errorMessage);
    console.error(error);
  }

  onSelect(asset: Asset) {
    const dialogRef = this.metadataViewDialog.open(MetadataDisplayComponent, {
      data: { 
        metadata: this.findMetadataForAsset(asset),
        asset_name: asset.properties.optionalValue<string>('edc', 'name') || asset.id,
      },
    });
    dialogRef.afterClosed().subscribe( );
  }
  
  shouldDisplayMetadata(asset : Asset) : boolean {
    if (!asset) return false;
    const metadata = this.findMetadataForAsset(asset)
    for (var prop in metadata) {
      if(metadata.hasOwnProperty(prop) && metadata[prop] !== null )
        return true;
    }
    return false;
  }

  findMetadataForAsset(asset: Asset) {
    const result: Record<string, any> = {};

    const properties: any = (asset as any)?.properties;
    const additionalKeys: string[] = Array.isArray(properties?.additionalPropertyKeys)
      ? properties.additionalPropertyKeys
      : [];
    const valuesMap: Record<string, any> = properties?.properties ?? {};

    additionalKeys.forEach((key) => {
      const normalizedKey = key.startsWith('asset:prop:') ? key.substring('asset:prop:'.length) : key;
      result[normalizedKey] = valuesMap[key];
    });
    
    if (Object.keys(result).length > 0) {
      return result;
    }

    return properties ?? {};
  }

  /**
   * Safely compare value to true, handles both boolean and string "true"/"false"
   */
  isAllowed(value: any): boolean {
    if (typeof value === 'boolean') {
      return value;
    }
    if (typeof value === 'string') {
      return value.toLowerCase() === 'true';
    }
    return !!value;
  }

  ngAfterContentChecked() {
    this.cdref.detectChanges();
  }
}
