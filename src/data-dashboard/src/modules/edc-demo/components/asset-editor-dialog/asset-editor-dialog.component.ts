import { Component, Inject, OnInit } from '@angular/core';
import { AssetInput } from "@think-it-labs/edc-connector-client";
import { MatDialogRef } from "@angular/material/dialog";
import { StorageType } from "../../models/storage-type";
import { MatTabChangeEvent } from '@angular/material/tabs';
import { getMediaTypes } from 'src/modules/mgmt-api-client';
import { OAuth2AssetProps } from '../../models/oauth2-asset-props';


@Component({
  selector: 'edc-demo-asset-editor-dialog',
  templateUrl: './asset-editor-dialog.component.html',
  styleUrls: ['./asset-editor-dialog.component.scss']
})
export class AssetEditorDialog implements OnInit {

  id: string = '';
  version: string = '';
  name: string = '';

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

  mediaTypes: string[] = getMediaTypes(); // Get all available media types
  contenttype: string = 'application/json'; // Default selected content type
  isOtherSelected: boolean = false; // Flag to show/hide custom input

  iamClientId: string = '';
  iamClientSecret: string = '';
  iamTokenUrl: string = '';
  iamScope: string = '';
  iamGrantType: string = 'client_credentials';
  iamUser: string = '';
  iamPassword: string = '';

  grantTypes: string[] = ['client_credentials', 'password']


  constructor(private dialogRef: MatDialogRef<AssetEditorDialog>,
      @Inject('STORAGE_TYPES') public storageTypes: StorageType[]) {
        this.mediaTypes = getMediaTypes();
  }

  ngOnInit(): void {
  }

  getPublicProperties() {
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

  onSave() {
    
    this.baseUrl = this.getWithoutTrailingSlashIfExists(this.baseUrl);

    const publicProperties = this.getPublicProperties();
    const dataAddress = this.getDataAddress();

    const assetInput: AssetInput = {
      "@id": this.id,
      properties: publicProperties,
      dataAddress: dataAddress,
    };

    this.dialogRef.close({ assetInput });
  }

  onContentTypeChange(selectedValue: string): void {
    this.isOtherSelected = selectedValue === 'other';
    if (!this.isOtherSelected) {
      this.contenttype = selectedValue; // Update content type for predefined options
    }
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
      ...this.getHeaderProps(),
      ...(this.authorizationTypeTab != "OAuth 2.0" ? this.getOAuth2Props(): {})
    };

    return resultDataAddress;
  }

  getHeaderProps() {
    return this.staticHeaders.reduce((acc, { key, value }) => {
      acc[`header:${key}`] = value;
      return acc;
    }, {} as any)
  }

  getOAuth2Props() {
    const oauthProps: OAuth2AssetProps = {
      "oauth2:tokenUrl": this.iamTokenUrl,
      "oauth2:clientId": this.iamClientId,
      "oauth2:clientSecret": this.iamClientSecret,
      "oauth2:grantType": this.iamGrantType,
      "oauth2:user": this.iamUser == '' ? undefined : this.iamUser,
      "oauth2:password": this.iamPassword == '' ? undefined : this.iamPassword,
      "oauth2:scope": this.iamScope == '' ? undefined : this.iamScope,
    };

    return oauthProps;
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

  private getWithoutTrailingSlashIfExists(baseUrl: string) {
    let resultUrl: string;
    baseUrl = baseUrl.replace(/\s/g, "");

    if (baseUrl[baseUrl.length - 1] == '/') {
      resultUrl = baseUrl.slice(0, -1);
    } else {
      resultUrl = baseUrl;
    }

    return resultUrl;
  }
}
