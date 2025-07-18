import { ChangeDetectorRef, Component, Inject, OnInit } from '@angular/core';
import { MatDialog } from '@angular/material/dialog';
import { BehaviorSubject, Observable, of } from 'rxjs';
import { map, switchMap } from 'rxjs/operators';
import { CatalogBrowserService, NotificationService, UtilService } from "../../services";
import { Router} from "@angular/router";
import { TransferProcessStates } from "../../models/transfer-process-states";
import { ContractOffer } from "../../models/contract-offer";
import { NegotiationResult } from "../../models/negotiation-result";
import { ContractNegotiation } from "../../../mgmt-api-client/model";
import { MetadataDisplayComponent } from '../common/metadata-display/metadata-display.component';
import { METADATA_CONTEXT, DATASET_CONTEXT } from 'src/modules/app/variables';

interface RunningTransferProcess {
  processId: string;
  assetId?: string;
  state: TransferProcessStates;
}

@Component({
  selector: 'edc-demo-catalog-browser',
  templateUrl: './catalog-browser.component.html',
  styleUrls: ['./catalog-browser.component.scss']
})
export class CatalogBrowserComponent implements OnInit {

  filteredContractOffers$: Observable<ContractOffer[]> = of([]);
  searchText = '';
  runningTransferProcesses: RunningTransferProcess[] = [];
  runningNegotiations: Map<string, NegotiationResult> = new Map<string, NegotiationResult>(); // contractOfferId, NegotiationResult
  finishedNegotiations: Map<string, ContractNegotiation> = new Map<string, ContractNegotiation>(); // contractOfferId, contractAgreementId
  private fetch$ = new BehaviorSubject(null);
  private pollingHandleNegotiation?: any;
  
  constructor(
    private apiService: CatalogBrowserService,
    private readonly metadataViewDialog: MatDialog,
    private router: Router,
    private notificationService: NotificationService,
    @Inject('HOME_CONNECTOR_STORAGE_ACCOUNT') private homeConnectorStorageAccount: string,
    private readonly cdref: ChangeDetectorRef,
    public readonly utilService: UtilService,
  ) { }

  ngOnInit(): void {
    this.filteredContractOffers$ = this.fetch$
      .pipe(
        switchMap(() => {
          const contractOffers$ = this.apiService.getContractOffers();
          return !!this.searchText ?
            contractOffers$.pipe(map(contractOffers => contractOffers.filter(contractOffer => 
              contractOffer.id.toLowerCase().includes(this.searchText.toLowerCase())
              || contractOffer.assetId.toLowerCase().includes(this.searchText.toLowerCase())
              || contractOffer.properties.name?.toLowerCase().includes(this.searchText.toLowerCase())
            )))
            :
            contractOffers$;
        }));
  }

  onSearch() {
    this.fetch$.next(null);
  }

  onSelect(offer: ContractOffer) {
    const dialogRef = this.metadataViewDialog.open(MetadataDisplayComponent, {
      data: { 
        metadata: this.findMetadataForAsset(offer),
        asset_name: offer.properties.name || offer.assetId,
      },
    });
    dialogRef.afterClosed().subscribe( );
  }

  shouldDisplayMetadata(offer : ContractOffer) : boolean {
    const metadata = this.findMetadataForAsset(offer)
    for (var prop in metadata) {
      if(metadata.hasOwnProperty(prop) && metadata[prop] !== null )
        return true;
    }
    return false;
  }

  findMetadataForAsset(offer: ContractOffer) {
    return offer[DATASET_CONTEXT].filter((_asset : any) => {
      return _asset['@id'] === offer.assetId || _asset.id === offer.assetId;
    })?.[0]?.[METADATA_CONTEXT]?.[0] || {};
  }

  onNegotiateClicked(contractOffer: ContractOffer) {
    console.log("Negotiation cliked");
    console.log(`Contract Offer Id: ${contractOffer.id!} | assetId: ${contractOffer.assetId}`);
    console.log(contractOffer);

    const initiateRequest: any = {
      "@context": {
        "edc": "https://w3id.org/edc/v0.0.1/ns/"
      },
      "@type": "ContractRequest",
      counterPartyAddress: contractOffer.originator,
      protocol: "dataspace-protocol-http",
      policy: {
        "@context": "http://www.w3.org/ns/odrl.jsonld",
        "@id": `${contractOffer.id}`,
        "@type": "Offer",
        assigner: `${contractOffer.participantId}`,
        target: `${contractOffer.assetId}`,
        obligation: contractOffer.policy.obligation,
        permission: contractOffer.policy.permission,
        prohibition: contractOffer.policy.prohibition,
      }
    };

    const finishedNegotiationStates = [
      "FINALIZED",
      "VERIFIED",
      "TERMINATED",
      "ERROR"];

    this.apiService.initiateNegotiation(initiateRequest).subscribe(negotiationId => {
      this.finishedNegotiations.delete(initiateRequest.policy["@id"]);
      this.runningNegotiations.set(initiateRequest.policy["@id"], {
        id: negotiationId,
        offerId: initiateRequest.policy["@id"]
      });

      if (!this.pollingHandleNegotiation) {
        // there are no active negotiations
        this.pollingHandleNegotiation = setInterval(() => {

          for (const negotiation of this.runningNegotiations.values()) {
            this.apiService.getNegotiationState(negotiation.id).subscribe(updatedNegotiation => {
              console.log(`Negotiation state: ${updatedNegotiation.state!}`);
              console.log(updatedNegotiation);

              if (updatedNegotiation.state! == "TERMINATED") {
                const messageJson = JSON.parse(updatedNegotiation["https://w3id.org/edc/v0.0.1/ns/errorDetail"][0]["@value"] ?? "");
                const messageString = messageJson["dspace:reason"] ?? "";
                this.notificationService.showError(`Error starting negotiation (${messageString})`);
              }

              if (finishedNegotiationStates.includes(updatedNegotiation.state!)) {
                let offerId = negotiation.offerId;
                this.runningNegotiations.delete(offerId);
                if (updatedNegotiation.state! === "VERIFIED" || updatedNegotiation.state! === "FINALIZED") {
                  this.finishedNegotiations.set(offerId, updatedNegotiation);
                  this.notificationService.showInfo("Contract Negotiation complete!", "Show me!", () => {
                    this.router.navigate(['/contracts'])
                  })
                }
              }

              if (this.runningNegotiations.size === 0) {
                clearInterval(this.pollingHandleNegotiation);
                this.pollingHandleNegotiation = undefined;
              }
            });
          }
        }, 1000);
      }
    }, error => {
      console.error(error);
      this.notificationService.showError("Error starting negotiation");
    });
  }

  isBusy(contractOffer: ContractOffer) {
    return this.runningNegotiations.get(contractOffer.id) !== undefined || !!this.runningTransferProcesses.find(tp => tp.assetId === contractOffer.assetId);
  }

  getState(contractOffer: ContractOffer): string {
    const transferProcess = this.runningTransferProcesses.find(tp => tp.assetId === contractOffer.assetId);
    if (transferProcess) {
      return TransferProcessStates[transferProcess.state];
    }

    const negotiation = this.runningNegotiations.get(contractOffer.id);
    if (negotiation) {
      return 'negotiating';
    }

    return '';
  }

  isNegotiated(contractOffer: ContractOffer) {
    return this.finishedNegotiations.get(contractOffer.id) !== undefined;
  }

  ngAfterContentChecked() {
    this.cdref.detectChanges();
  }
}
