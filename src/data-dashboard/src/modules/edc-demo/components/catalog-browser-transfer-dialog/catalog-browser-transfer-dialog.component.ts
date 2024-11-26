import {Component, Inject, OnInit} from '@angular/core';
import {MAT_DIALOG_DATA, MatDialogRef} from '@angular/material/dialog';
import {StorageType} from '../../models/storage-type';


@Component({
  selector: 'edc-demo-catalog-browser-transfer-dialog',
  templateUrl: './catalog-browser-transfer-dialog.component.html',
  styleUrls: ['./catalog-browser-transfer-dialog.component.scss']
})
export class CatalogBrowserTransferDialog implements OnInit {

  name: string = '';
  storageTypeId = '';

  proxyUrlPath: string = '';
  
  // Initialize an array for key-value pairs (query params)
  proxyQueryParams: { key: string; value: string }[] = [];

  // ReadOnly
  isProxyPath: boolean = false;
  isProxyQueryParams: boolean = false;

  constructor(@Inject('STORAGE_TYPES') public storageTypes: StorageType[],
              private dialogRef: MatDialogRef<CatalogBrowserTransferDialog>,
              @Inject(MAT_DIALOG_DATA) data: any) {
    this.isProxyPath = data.isProxyPath;
    this.isProxyQueryParams = data.isProxyQueryParams;
  }

  ngOnInit(): void {
  }

  addQueryParam() {
    this.proxyQueryParams.push({ key: '', value: '' });
  }

  removeQueryParam(index: number) {
    this.proxyQueryParams.splice(index, 1);
  }

  onTransfer() {
    this.dialogRef.close({
      storageTypeId: this.storageTypeId, 
      proxyUrlPath: this.proxyUrlPath, 
      proxyQueryParams: this.proxyQueryParams
    });
  }

}
