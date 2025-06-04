import {Component, OnInit} from '@angular/core';
import {BehaviorSubject, Observable, of} from 'rxjs';
import {first, map, switchMap, tap} from 'rxjs/operators';
import {MatDialog} from '@angular/material/dialog';
import {AssetInput, Asset } from "../../../mgmt-api-client/model";
import {AssetService, QUERY_LIMIT} from "../../../mgmt-api-client";
import {AssetEditorDialog} from "../asset-editor-dialog/asset-editor-dialog.component";
import {ConfirmationDialogComponent, ConfirmDialogModel} from "../confirmation-dialog/confirmation-dialog.component";
import { NotificationService, SorterService, UtilService } from "../../services";


@Component({
  selector: 'edc-demo-asset-viewer',
  templateUrl: './asset-viewer.component.html',
  styleUrls: ['./asset-viewer.component.scss']
})
export class AssetViewerComponent implements OnInit {

  filteredAssets$: Observable<Asset[]> = of([]);
  searchText = '';
  isTransferring = false;
  private fetch$ = new BehaviorSubject(null);

  constructor(
    private assetService: AssetService,
    private notificationService: NotificationService,
    private readonly dialog: MatDialog,
    private readonly sorterService: SorterService,
    public readonly utilService: UtilService,
  ) { }

  private showError(error: string, errorMessage: string) {
    this.notificationService.showError(errorMessage);
    console.error(error);
  }

  ngOnInit(): void {
    this.filteredAssets$ = this.fetch$
      .pipe(
        switchMap(() => {
          const assets$ = this.assetService.requestAssets({
            limit: QUERY_LIMIT,
            offset: 0,
          }).pipe(
            map(assets => { 
              console.log(assets); 
              return assets.sort((a, b) => 
                this.sorterService.naturalSort(a.properties.optionalValue<string>('edc', 'name') || '', b.properties.optionalValue<string>('edc', 'name') || ''))
              })
          );
          return !!this.searchText
            ? assets$.pipe(map(assets => assets.filter(asset => 
              asset.properties.optionalValue<string>('edc', 'name')?.includes(this.searchText) 
              || asset.id.toLowerCase().includes(this.searchText.toLowerCase())
            )))
            : assets$;
        }));
  }

  isBusy() {
    return this.isTransferring;
  }

  onSearch() {
    this.fetch$.next(null);
  }

  onDelete(asset: Asset) {
    const dialogData = ConfirmDialogModel.forDelete("asset", `"${asset.id}"`)
    const ref = this.dialog.open(ConfirmationDialogComponent, {data: dialogData});

    ref.afterClosed().subscribe({
      next: res => {
        if (res) {
          this.assetService.removeAsset(asset.id).subscribe({
            next: () => this.fetch$.next(null),
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
          next: ()=> this.fetch$.next(null),
          error: err => this.showError(err, "This asset cannot be created"),
          complete: () => this.notificationService.showInfo("Successfully created"),
        })
      }
  })
}
}
