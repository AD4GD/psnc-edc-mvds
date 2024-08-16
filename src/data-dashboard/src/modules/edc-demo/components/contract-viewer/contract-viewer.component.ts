import {Component, Inject, OnInit} from '@angular/core';
import {
  AssetService,
  ContractAgreementService,
  TransferProcessService
} from "../../../mgmt-api-client";
import {from, Observable, of} from "rxjs";
import { Asset, ContractAgreement, TransferProcessInput, IdResponse, TransferProcess } from "../../../mgmt-api-client/model";
import {ContractOffer} from "../../models/contract-offer";
import {filter, first, map, switchMap, tap} from "rxjs/operators";
import {NotificationService} from "../../services/notification.service";
import {
  CatalogBrowserTransferDialog
} from "../catalog-browser-transfer-dialog/catalog-browser-transfer-dialog.component";
import {MatDialog} from "@angular/material/dialog";
import {CatalogBrowserService} from "../../services/catalog-browser.service";
import {Router} from "@angular/router";
import {TransferProcessStates} from "../../models/transfer-process-states";
import { AppConfigService } from '../../../app/app-config.service';
import { MINIO_STORAGE_TYPE } from 'src/modules/app/variables';
import { EdrService } from 'src/modules/mgmt-api-client/api/edr.service';
import { PublicService } from 'src/modules/mgmt-api-client/api/public.service';
import { EdcConnectorClientContext } from '@think-it-labs/edc-connector-client';

interface RunningTransferProcess {
  processId: string;
  contractId: string;
  state: TransferProcessStates;
  storageType: string;
}

@Component({
  selector: 'app-contract-viewer',
  templateUrl: './contract-viewer.component.html',
  styleUrls: ['./contract-viewer.component.scss']
})
export class ContractViewerComponent implements OnInit {

  contracts$: Observable<ContractAgreement[]> = of([]);
  private runningTransfers: RunningTransferProcess[] = [];
  private pollingHandleTransfer?: any;

  constructor(private contractAgreementService: ContractAgreementService,
              private edrService: EdrService,
              private publicService: PublicService,
              public dialog: MatDialog,
              @Inject('HOME_CONNECTOR_STORAGE_ACCOUNT') private homeConnectorStorageAccount: string,
              private transferService: TransferProcessService,
              private catalogService: CatalogBrowserService,
              private router: Router,
              private notificationService: NotificationService,
              private appConfigService: AppConfigService) {
  }

  private static isFinishedState(state: string): boolean {
    return [
      "STARTED",
      "COMPLETED",
      "ERROR",
      "ENDED"].includes(state);
  }

  ngOnInit(): void {
    this.contracts$ = this.contractAgreementService.queryAllAgreements();
  }

  asDate(epochSeconds?: number): string {
    if(epochSeconds){
      const d = new Date(0);
      d.setUTCSeconds(epochSeconds);
      return d.toLocaleDateString();
    }
    return '';
  }

  onTransferClicked(contract: ContractAgreement) {
    const dialogRef = this.dialog.open(CatalogBrowserTransferDialog);

    dialogRef.afterClosed().pipe(first()).subscribe(result => {
      if (result === undefined || result.storageTypeId === undefined || result.storageTypeId === "") {
        return;
      }

      const storageTypeId: string = result.storageTypeId;

      this.createTransferRequest(contract, storageTypeId)
        .pipe(switchMap(trq => this.transferService.initiateTransfer(trq)))
        .subscribe(transferId => {
          this.startPolling(transferId, contract["@id"]!, storageTypeId);
        }, error => {
          console.error(error);
          this.notificationService.showError("Error initiating transfer");
        });
    });
  }

  isTransferInProgress(contractId: string): boolean {
    return !!this.runningTransfers.find(rt => rt.contractId === contractId);
  }

  private createTransferRequest(contract: ContractAgreement, storageTypeId: string): Observable<TransferProcessInput> {
    return this.getContractOfferForAssetId(contract.assetId!).pipe(map(contractOffer => {
      const backendUrl = this.appConfigService.getConfig()?.backendUrl;
      console.log(backendUrl);
      const iniateTransfer : any = {
        connectorId: "provider",
        counterPartyAddress: contractOffer.originator,
        contractId: contract.id,
        assetId: contractOffer.assetId,
        transferType: "HttpData-PULL",
        dataDestination: {
          "type": storageTypeId,
        },
        callbackAddresses: [
          {
            "events": [
              "transfer.process.started"
            ],
            "uri": backendUrl
          }
        ]
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
  private getContractOfferForAssetId(assetId: string): Observable<ContractOffer> {
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

  private startPolling(transferProcessId: IdResponse, contractId: string, storageType: string) {
    // track this transfer process
    this.runningTransfers.push({
      processId: transferProcessId.id!,
      state: TransferProcessStates.REQUESTED,
      contractId: contractId,
      storageType: storageType
    });

    if (!this.pollingHandleTransfer) {
      this.pollingHandleTransfer = setInterval(this.pollRunningTransfers(), 1000);
    }

  }

  private pollRunningTransfers() {
    return () => {
      from(this.runningTransfers) //create from array
        .pipe(switchMap(runningTransferProcess => this.catalogService.getTransferProcessesById(runningTransferProcess.processId).pipe(
          map(transferProcess => ({ runningTransferProcess, transferProcess })) // Combine both into an object
          )
        ),
        filter(({ transferProcess }) => ContractViewerComponent.isFinishedState(transferProcess.state!)),
          tap(({ runningTransferProcess, transferProcess }) => {
            this.processStartedTransfer(transferProcess, runningTransferProcess.storageType);
          })
        )
        .subscribe(() => {
        // clear interval if necessary
        if (this.runningTransfers.length === 0) {
          clearInterval(this.pollingHandleTransfer);
          this.pollingHandleTransfer = undefined;
        }
      }, error => this.notificationService.showError(error))
    }
  }

  private processStartedTransfer = (transfer: TransferProcess, storageType: string) => {
    console.log(transfer);
    console.log(storageType);

    if (storageType == MINIO_STORAGE_TYPE) {
      this.completeTransfer(transfer);
      return;
    }

    this.processStartedLocalTransfer(transfer);
  }

  private processStartedLocalTransfer = async (transfer: TransferProcess) => {
    console.log(transfer);
    try {
      const address = await this.edrService.requestDataAddress(transfer.id).toPromise();
      console.log(address);

      const endpoint = address["https://w3id.org/edc/v0.0.1/ns/endpoint"][0]["@value"];
      const authCode = address["https://w3id.org/edc/v0.0.1/ns/authorization"][0]["@value"];
      console.log(endpoint);
      console.log(authCode);

      const adjustedEndpoint = this.adjustServiceUrl(endpoint);
      console.log(adjustedEndpoint);

      const context = new EdcConnectorClientContext(undefined, {
        public: adjustedEndpoint
      });

      const data: Response = await this.publicService.getTransferredData(authCode, context).toPromise();
      console.log(data);

      // Save to downloads
      const jsonData = await data.json();
      console.log(jsonData);
      const blob = new Blob([JSON.stringify(jsonData, null, 2)], { type: 'application/json' });
      const url = URL.createObjectURL(blob);

      const a = document.createElement('a');
      a.href = url;
      a.download = `${transfer.assetId}.json`;
      document.body.appendChild(a);
      a.click();

      URL.revokeObjectURL(url);
      document.body.removeChild(a);
      //

      this.completeTransfer(transfer);
    } catch (e: any) {
      const message = (e as Error).message;
      console.log(e);
      this.notificationService.showError(message);
    }

  }

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

      // Return the modified or original URL
      return parsedUrl.toString();
    } catch (error) {
      console.error('Invalid URL provided:', error);
      return url; // Return the original URL in case of an error
    }
  }

  private completeTransfer = (transferProcess: any) => {
    // remove from in-progress
    this.runningTransfers = this.runningTransfers.filter(rtp => rtp.processId !== transferProcess.id)
    this.notificationService.showInfo(`Transfer [${transferProcess.id}] complete!`, "Show me!", () => {
      this.router.navigate(['/transfer-history'])
    })
  }
}
