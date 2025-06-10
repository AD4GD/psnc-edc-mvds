import {ChangeDetectorRef, Component, Inject, OnInit, Query} from '@angular/core';
import {
  AssetService,
  ContractAgreementService,
  MIME_TO_EXTENSION,
  QUERY_LIMIT,
  TransferProcessService
} from "../../../mgmt-api-client";
import {asyncScheduler, forkJoin, Observable, of, scheduled} from "rxjs";
import { Asset, ContractAgreement, TransferProcessInput, IdResponse, TransferProcess } from "../../../mgmt-api-client/model";
import {ContractOffer} from "../../models/contract-offer";
import {filter, first, map, switchMap, tap} from "rxjs/operators";
import { CatalogBrowserTransferDialog } from "../catalog-browser-transfer-dialog/catalog-browser-transfer-dialog.component";
import {MatDialog} from "@angular/material/dialog";
import {Router} from "@angular/router";
import {TransferProcessStates} from "../../models/transfer-process-states";
import { AppConfigService } from '../../../app/app-config.service';
import { MINIO_STORAGE_TYPE } from 'src/modules/app/variables';
import { EdrService } from 'src/modules/mgmt-api-client/api/edr.service';
import { PublicService } from 'src/modules/mgmt-api-client/api/public.service';
import { EdcConnectorClientContext, QuerySpec } from '@think-it-labs/edc-connector-client';
import { SorterService, CatalogBrowserService, NotificationService, UtilService } from '../../services';

interface RunningTransferProcess {
  processId: string;
  contractId: string;
  state: TransferProcessStates;
  storageType: string;
  proxyDataAddressOptions: any;
  isTransferStarted: boolean;
}

interface ContractAgreementWithOfferData extends ContractAgreement {
  contractOffer: ContractOffer | null;
}

@Component({
  selector: 'app-contract-viewer',
  templateUrl: './contract-viewer.component.html',
  styleUrls: ['./contract-viewer.component.scss']
})

export class ContractViewerComponent implements OnInit {

  contracts$: Observable<ContractAgreementWithOfferData[]> = of([]);
  private runningTransfers: RunningTransferProcess[] = [];
  private pollingHandleTransfer?: any;

  constructor(
    private contractAgreementService: ContractAgreementService,
    private edrService: EdrService,
    private publicService: PublicService,
    public dialog: MatDialog,
    @Inject('HOME_CONNECTOR_STORAGE_ACCOUNT') private homeConnectorStorageAccount: string,
    private transferService: TransferProcessService,
    private catalogService: CatalogBrowserService,
    private router: Router,
    private notificationService: NotificationService,
    private appConfigService: AppConfigService,
    private sorterService: SorterService,
    private readonly cdref: ChangeDetectorRef,
    public readonly utilService: UtilService,
  ) { }

  private static isFinishedState(state: string): boolean {
    return [
      "STARTED",
      "COMPLETED",
      "ERROR",
      "ENDED"].includes(state);
  }

  ngOnInit(): void {
    this.contracts$ = this.contractAgreementService.queryAllAgreements({
      limit : QUERY_LIMIT,
      offset : 0,
    }).pipe(
      switchMap(contracts => {
        return this.loadContractsWithAssets(
          contracts.sort((a, b) => {
            // Sort by contractSigningDate (descending)
            const dateA = a.contractSigningDate || 0;
            const dateB = b.contractSigningDate || 0;
            if (dateA !== dateB) {
              return dateB - dateA; // Newest first
            }

            return this.sorterService.naturalSort(a.assetId || '', b.assetId || '');
          })
      )})
    );
  }

  loadContractsWithAssets(contracts: ContractAgreement[]): Observable<ContractAgreementWithOfferData[]> {
    return this.getAllContractOffers().pipe(
      switchMap((allOffers: ContractOffer[]) => {
        const contractObservables: Observable<ContractAgreementWithOfferData>[] = contracts.map(contract => {
          const offerData = this.getContractOfferForAssetId(contract.assetId, allOffers);
          const contractWithOffer = contract as ContractAgreementWithOfferData;
          contractWithOffer.contractOffer = offerData;
          // Wrap the result in an observable
          return scheduled([contractWithOffer], asyncScheduler);
        });
  
        // Combine all observables
        return forkJoin(contractObservables).pipe(
          map(results => results.filter(item => item !== null)));
      })
    );
  }

  asDate(epochSeconds?: number): string {
    if(epochSeconds){
      const d = new Date(0);
      d.setUTCSeconds(epochSeconds);
      return d.toLocaleDateString();
    }
    return '';
  }

  onTransferClicked(contract: ContractAgreementWithOfferData) {

    const offer = contract.contractOffer!;
    console.log(offer);

    const dialogRef = this.dialog.open(CatalogBrowserTransferDialog, {
      data: {
        isProxyPath: offer.properties.proxyPath ?? false,
        isProxyQueryParams: offer.properties.proxyQueryParams ?? false,
      }
    });

    dialogRef.afterClosed().pipe(first()).subscribe(result => {
      if (result === undefined || result.storageTypeId === undefined || result.storageTypeId === "") {
        return;
      }

      console.log(result);

      const storageTypeId: string = result.storageTypeId;
      const proxyDataAddressOptions: any = {
        proxyPath: result.proxyUrlPath,
        proxyQueryParams: result.proxyQueryParams
      }

      this.createTransferRequest(contract, storageTypeId, proxyDataAddressOptions)
        .pipe(switchMap(trq => this.transferService.initiateTransfer(trq)))
        .subscribe(transferId => {
          this.startPolling(transferId, contract["@id"]!, storageTypeId, proxyDataAddressOptions);
        }, error => {
          console.error(error);
          this.notificationService.showError("Error initiating transfer");
        });
    });
  }

  isTransferInProgress(contractId: string): boolean {
    return !!this.runningTransfers.find(rt => rt.contractId === contractId);
  }

  private createTransferRequest(contract: ContractAgreement, storageTypeId: string, proxyDataAddressOptions: any): Observable<TransferProcessInput> {
    return this.getContractOfferForAssetIdAsync(contract.assetId!).pipe(map(contractOffer => {
      const backendUrl = this.appConfigService.getConfig()?.backendUrl;
      console.log(backendUrl);

      const callbackAddresses = [];

      if (storageTypeId == MINIO_STORAGE_TYPE) {
        callbackAddresses.push(
          {
            "events": [
              "transfer.process.started"
            ],
            "uri": this.getUrlWithQueryParams(backendUrl!, proxyDataAddressOptions)
          }
        )
      }

      const iniateTransfer : any = {
        connectorId: contract.providerId,
        counterPartyAddress: contractOffer.originator,
        contractId: contract.id,
        assetId: contractOffer.assetId,
        transferType: "HttpData-PULL",
        dataDestination: {
          "type": storageTypeId,
        },
        callbackAddresses: callbackAddresses
      };

      return iniateTransfer;
    }));

  }

  /**
   * This method is used to obtain that URL of the connector that is offering a particular asset from the catalog.
   * This is a bit of a hack, because currently there is no "clean" way to get the counter-party's URL for a ContractAgreement.
   *
   * @param assetId Asset ID of the asset that is associated with the contract.
   */
  private getContractOfferForAssetIdAsync(assetId: string): Observable<ContractOffer> {
    console.log(assetId);
    return this.catalogService.getContractOffers()
      .pipe(
        map(offers => {
          return offers.find(o => o.assetId === assetId);}
        ),
        map(o => {
          if (o) return o;
          else throw new Error(`No offer found for asset ID ${assetId}`);
        }))
  }

  private getAllContractOffers(): Observable<ContractOffer[]> {
    return this.catalogService.getContractOffers();
  }

  private getContractOfferForAssetId(assetId: string, contractOffers: ContractOffer[]): ContractOffer | null {
    // console.log(assetId);
    const offer = contractOffers.find(o => o.assetId === assetId);
    if (offer) {
      return offer;
    }
    console.log(`No offer found for asset ID ${assetId}`);
    return null;
  }

  private startPolling(transferProcessId: IdResponse, contractId: string, storageType: string, proxyDataAddressOptions: any) {

    // track this transfer process
    this.runningTransfers.push({
      processId: transferProcessId.id!,
      state: TransferProcessStates.REQUESTED,
      contractId: contractId,
      storageType: storageType,
      proxyDataAddressOptions: proxyDataAddressOptions,
      isTransferStarted: false,
    });

    if (!this.pollingHandleTransfer) {
      console.log(proxyDataAddressOptions.proxyPath);
      this.pollingHandleTransfer = setInterval(this.pollRunningTransfers(), 1000);
    }

  }

  private pollRunningTransfers() {
    return () => {
      scheduled(this.runningTransfers, asyncScheduler) //create from array
        .pipe(switchMap(runningTransferProcess => this.catalogService.getTransferProcessesById(runningTransferProcess.processId).pipe(
          map(transferProcess => ({ runningTransferProcess, transferProcess })) // Combine both into an object
          )
        ),
        filter(({ runningTransferProcess, transferProcess }) => 
          ContractViewerComponent.isFinishedState(transferProcess.state!) && !runningTransferProcess.isTransferStarted),
          tap(({ runningTransferProcess, transferProcess }) => {
            try {
              runningTransferProcess.isTransferStarted = true;
              this.processStartedTransfer(
                transferProcess, runningTransferProcess.storageType, runningTransferProcess.proxyDataAddressOptions);
            } catch {
              runningTransferProcess.isTransferStarted = false;
            }
          })
        )
        .subscribe(() => {
        // clear interval if necessary
        if (this.runningTransfers.length === 0) {
          clearInterval(this.pollingHandleTransfer);
          this.pollingHandleTransfer = undefined;
          console.log("cleared interval");
        }
      }, error => this.notificationService.showError(error))
    }
  }

  private processStartedTransfer = (transfer: TransferProcess, storageType: string, proxyDataAddressOptions: any) => {
    console.log(transfer);
    console.log(storageType);

    if (storageType == MINIO_STORAGE_TYPE) {
      this.completeTransfer(transfer);
      return;
    }

    this.processStartedLocalTransfer(transfer, proxyDataAddressOptions);
  }

  private processStartedLocalTransfer = async (transfer: TransferProcess, proxyDataAddressOptions: any) => {
    console.log(transfer);
    try {
      const address = await this.edrService.requestDataAddress(transfer.id).toPromise();
      console.log(address);

      const endpoint = address["https://w3id.org/edc/v0.0.1/ns/endpoint"][0]["@value"];
      const authCode = address["https://w3id.org/edc/v0.0.1/ns/authorization"][0]["@value"];
      console.log(endpoint);
      console.log(authCode);

      const adjustedEndpoint = this.adjustServiceUrl(endpoint);
      const publicEndpoint = this.getUrlWithQueryParams(adjustedEndpoint, proxyDataAddressOptions);
      console.log(publicEndpoint);

      const context = new EdcConnectorClientContext(undefined, {
        public: publicEndpoint
      });
      console.log(context.public);

      const data: Response = await this.publicService.getTransferredData(authCode, context).toPromise();
      console.log(data);

      this.saveFileToDownloads(data, transfer);
      this.completeTransfer(transfer);
    } catch (e: any) {
      const message = (e as Error).message;
      console.log(e);
      this.notificationService.showError(message);
    }
  }

  private saveFileToDownloads = async (data: Response, transfer: TransferProcess) => {
    const contentType = data.headers.get('Content-Type') || 'application/octet-stream';
    const blob = await data.blob();
  
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    
    const extension = MIME_TO_EXTENSION[contentType] || '';
    a.download = `${transfer.assetId}${extension}`;
  
    document.body.appendChild(a);
    a.click();
    URL.revokeObjectURL(url);
    document.body.removeChild(a);
  };
  
  // A fast fix for the problem related to a request to <service-name>:<port> on dev. env. (need localhost)
  // Temporary http scheme will be considered as a sign of a dev. environment
  private adjustServiceUrl = (url: string): string => {
    try {
      const parsedUrl = new URL(url);

      // Check if the scheme is 'http' and the hostname is 'provider-connector'
      if (parsedUrl.protocol === 'http:') {
        // Replace 'provider-connector' with 'localhost'
        parsedUrl.hostname = 'localhost';
      }

      return parsedUrl.toString();
      
    } catch (error) {
      console.error('Invalid URL provided:', error);
      return url; 
    }
  }

  private completeTransfer = (transferProcess: any) => {
    // remove from in-progress
    this.runningTransfers = this.runningTransfers.filter(rtp => rtp.processId !== transferProcess.id)
    this.notificationService.showInfo(`Transfer [${transferProcess.id}] complete!`, "Show me!", () => {
      this.router.navigate(['/transfer-history'])
    })
  }

  private getUrlWithQueryParams(url: string, proxyDataAddressOptions: any) {
    const proxyPath = proxyDataAddressOptions.proxyPath.replace(/\s/g, "");
    const proxyQueryParams: { key: string; value: string }[] = proxyDataAddressOptions.proxyQueryParams;

    let result = url;
    if (proxyPath != undefined && proxyPath != '') {
      if (proxyPath[0] != '/') {
        result += '/';
      }
      result += `${proxyPath}`;
    }
    if (proxyQueryParams != undefined && proxyQueryParams.length > 0) {
      const proxyQueryParamsStr = proxyQueryParams
        .map(x => `${x.key.replace(/\s/g, "")}=${x.value.replace(/\s/g, "")}`)
        .join("&");
      result += `?${proxyQueryParamsStr}`;
    }

    return result;
  }

  ngAfterContentChecked() {
    this.cdref.detectChanges();
  }
}
