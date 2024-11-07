import { Component, Inject, OnInit } from '@angular/core';
import { AssetInput } from "@think-it-labs/edc-connector-client";
import { MatDialogRef } from "@angular/material/dialog";
import { StorageType } from "../../models/storage-type";
import { MatTabChangeEvent } from '@angular/material/tabs';


@Component({
  selector: 'edc-demo-asset-editor-dialog',
  templateUrl: './asset-editor-dialog.component.html',
  styleUrls: ['./asset-editor-dialog.component.scss']
})
export class AssetEditorDialog implements OnInit {

  id: string = '';
  version: string = '';
  name: string = '';
  contenttype: string = '';

  storageTypeId: string = 'AzureStorage';
  account: string = '';
  container: string = 'src-container';
  blobname: string = '';
  baseUrl: string = '';

  authToken: string = '';
  apiKey: string = '';

  isProxyPath: boolean = true;
  isProxyQueryParams: boolean = true;

  authorizationTypeTab: string = 'Authorization Token';
  staticHeaders: { key: string; value: string }[] = [];

  isDisplayBaseUrl: boolean = true;


  constructor(private dialogRef: MatDialogRef<AssetEditorDialog>,
      @Inject('STORAGE_TYPES') public storageTypes: StorageType[]) {
  }

  ngOnInit(): void {
  }

  onSave() {
    
    const properties = this.getProperties();
    const dataAddress = this.getDataAddress();

    const assetInput: AssetInput = {
      "@id": this.id,
      properties: properties,
      dataAddress: dataAddress
    };

    this.dialogRef.close({ assetInput });
  }

  getProperties() {
    const properties: any = {
      "name": this.name,
      "version": this.version,
      "contenttype": this.contenttype,
      "proxyPath": this.isProxyPath.toString(),
      "proxyQueryParams": this.isProxyQueryParams.toString(),
    };

    if (this.isDisplayBaseUrl) {
      properties.baseUrl = this.baseUrl;
    }

    return properties;
  }

  getDataAddress() {
    if (this.authToken != "" || this.apiKey != "") {
      if (this.authorizationTypeTab == "Authorization Token") {
        this.addOrReplaceHeader("authorization", this.authToken);
      }
      else if (this.authorizationTypeTab == "API Key") {
        this.addOrReplaceHeader("x-api-key", this.apiKey);
      }
    }

    if (this.contenttype != "") {
      this.addOrReplaceHeader("content-type", this.contenttype);
    }

    const dataAddress = {
      "type": "HttpData", // this.storageTypeId,
      "baseUrl": this.baseUrl,
      "proxyPath": this.isProxyPath.toString(),
      "proxyQueryParams": this.isProxyQueryParams.toString(),
      "contentType": this.contenttype,
    }

    const resultDataAddress = {
      ...dataAddress,
      ...this.staticHeaders.reduce((acc, { key, value }) => {
            acc[`header:${key}`] = value;
            return acc;
        }, {} as any)
    };

    return resultDataAddress;
  }

  addOrReplaceHeader(headerKey: string, headerValue: string) {
    if (this.staticHeaders.some(x => x.key.toLowerCase() == headerKey)) {
      this.staticHeaders.forEach(x => {
        if (x.key.toLowerCase() == headerKey) {
          x.value = headerValue;
        }
      });
    } else {
      this.staticHeaders.push({key: headerKey, value: headerValue});
    }
  }

  addHeader() {
    this.staticHeaders.push({ key: '', value: '' });
  }

  removeHeader(index: number) {
    this.staticHeaders.splice(index, 1);
  }

  onAuthorizationTypeTabChange(event: MatTabChangeEvent) {
    this.authorizationTypeTab = event.tab.textLabel;
  }
}
