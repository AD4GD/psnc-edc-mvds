import { ChangeDetectorRef, Component, OnInit } from '@angular/core';
// import { BehaviorSubject, Observable, of } from 'rxjs';
// import { first, map, switchMap, tap } from 'rxjs/operators';
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


@Component({
  selector: 'edc-demo-asset-viewer',
  templateUrl: './asset-viewer.component.html',
  styleUrls: ['./asset-viewer.component.scss']
})
export class AssetViewerComponent implements OnInit {

  // filteredAssets$: Observable<Asset[]> = of([]);
  // private fetch$ = new BehaviorSubject(null);
  allAssets: Asset[] = [];
  pagedAssets: Asset[] = [];
  filteredAssets: Asset[] = [];
  searchText = '';
  isTransferring = false;
  pageIndex = 0;
  pageSize = 20;

  constructor(
    private assetService: AssetService,
    private notificationService: NotificationService,
    private readonly dialog: MatDialog,
    private readonly metadataViewDialog: MatDialog,
    private readonly sorterService: SorterService,
    private readonly cdref: ChangeDetectorRef,
    public readonly utilService: UtilService,
  ) { }

  loadAssets() {
    this.assetService.requestAssets({ 
      limit: QUERY_LIMIT,
      offset: 0 
    }).subscribe(assets => {
      this.allAssets = assets.sort((a, b) =>
        this.sorterService.naturalSort(
          a.properties.optionalValue<string>('edc', 'name') || a['@id'],
          b.properties.optionalValue<string>('edc', 'name') || b['@id'] 
        )
      );
      this.applyFilterAndPagination();
    });
  }

  ngOnInit(): void {
    this.loadAssets();
    // this.filteredAssets$ = this.fetch$
    //   .pipe(
    //     switchMap(() => {
    //       const assets$ = this.assetService.requestAssets({
    //         limit: QUERY_LIMIT,
    //         offset: 0,
    //       }).pipe(
    //         map(assets => { 
    //           console.log(assets); 
    //           return assets.sort((a, b) => 
    //             this.sorterService.naturalSort(a.properties.optionalValue<string>('edc', 'name') || '', b.properties.optionalValue<string>('edc', 'name') || ''))
    //           })
    //       );
    //       return !!this.searchText
    //         ? assets$.pipe(map(assets => assets.filter(asset => 
    //           asset.properties.optionalValue<string>('edc', 'name')?.includes(this.searchText)
    //           || asset.id.toLowerCase().includes(this.searchText.toLowerCase())
    //         )))
    //         : assets$;
    //     })
    //   )
    // this.filteredAssets$.subscribe(assets => {
    //   this.pageIndex = 0; // reset przy zmianie filtrów
    //   this.updatePagedAssets(assets);
    // });
  }

  applyFilterAndPagination() {
    // Filtrowanie
    if (this.searchText) {
      this.filteredAssets = this.allAssets.filter(asset =>
        (asset.properties.optionalValue<string>('edc', 'name') || '').toLowerCase().includes(this.searchText.toLowerCase()) ||
        (asset.properties.optionalValue<string>('edc', 'baseUrl') || '').toLowerCase().includes(this.searchText.toLowerCase()) ||
        this.utilService.searchThroughMetadata(this.findMetadataForAsset(asset), this.searchText) ||
        asset.id.toLowerCase().includes(this.searchText.toLowerCase())
      );
    } else {
      this.filteredAssets = [...this.allAssets];
    }
    // Reset pageIndex jeśli poza zakresem
    if (this.pageIndex * this.pageSize >= this.filteredAssets.length && this.filteredAssets.length > 0) {
      this.pageIndex = 0;
    }
    // Paginacja
    const start = this.pageIndex * this.pageSize;
    const end = start + this.pageSize;
    this.pagedAssets = this.filteredAssets.slice(start, end);
  }

  isBusy() {
    return this.isTransferring;
  }

  onSearch() {
    this.pageIndex = 0;
    // this.fetch$.next(null);
    this.applyFilterAndPagination();
  }

  onPageChange(event: PageEvent) {
    if (event.pageSize !== this.pageSize) {
      const firstItemIndex = this.pageIndex * this.pageSize;
      this.pageIndex = Math.floor(firstItemIndex / event.pageSize);
      this.pageSize = event.pageSize;
    } else {
      this.pageIndex = event.pageIndex;
      this.pageSize = event.pageSize;
    }
    this.applyFilterAndPagination();
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
          // next: () => this.fetch$.next(null),
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
    const metadata = this.findMetadataForAsset(asset)
    for (var prop in metadata) {
      if(metadata.hasOwnProperty(prop) && metadata[prop] !== null )
        return true;
    }
    return false;
  }

  findMetadataForAsset(asset: Asset) {
    return asset.properties[METADATA_CONTEXT]?.[0]
  }

  ngAfterContentChecked() {
    this.cdref.detectChanges();
  }
}
