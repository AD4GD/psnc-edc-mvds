import { HttpErrorResponse } from '@angular/common/http';
import { ChangeDetectorRef, Component, OnDestroy, OnInit } from '@angular/core';
import { MatDialog } from '@angular/material/dialog';
import { ActivatedRoute, Router } from '@angular/router';
import { asyncScheduler, Subject, scheduled, of } from 'rxjs';
import { filter, first, map, switchMap, takeUntil, tap } from 'rxjs/operators';
import { EdcConnectorClientContext } from '@think-it-labs/edc-connector-client';
import {
    ContractNegotiation,
    IdResponse,
    TransferProcess,
    TransferProcessInput
} from '../../../mgmt-api-client/model';
import { MIME_TO_EXTENSION, TransferProcessService } from '../../../mgmt-api-client';
import { EdrService } from 'src/modules/mgmt-api-client/api/edr.service';
import { PublicService } from 'src/modules/mgmt-api-client/api/public.service';
import { AppConfigService } from 'src/modules/app/app-config.service';
import { DATASET_CONTEXT, METADATA_CONTEXT, MINIO_STORAGE_TYPE } from 'src/modules/app/variables';
import { UnauthorizedStateService } from 'src/modules/app/auth/unauthorized-state.service';
import { CatalogBrowserTransferDialog } from '../catalog-browser-transfer-dialog/catalog-browser-transfer-dialog.component';
import { ContractOffer } from '../../models/contract-offer';
import { TransferProcessStates } from '../../models/transfer-process-states';
import { CatalogBrowserService, NotificationService, ParticipantsRegistryService, UtilService } from '../../services';

interface RunningTransferProcess {
    processId: string;
    contractId: string;
    state: TransferProcessStates | string;
    storageType: string;
    proxyDataAddressOptions: any;
    isTransferStarted: boolean;
}

@Component({
    selector: 'edc-demo-offer-details',
    templateUrl: './offer-details.component.html',
    styleUrls: ['./offer-details.component.scss']
})
export class OfferDetailsComponent implements OnInit, OnDestroy {
    offerId = '';
    participantId = '';
    offer?: ContractOffer;
    metadata: any = {};
    isUnauthorized = false;
    isLoading = true;
    loadError = '';

    negotiationState = 'IDLE';
    negotiation?: ContractNegotiation;
    negotiationInProgress = false;
    contractAgreementId?: string;
    isDownloading = false;

    private runningTransfers: RunningTransferProcess[] = [];
    private pollingHandleNegotiation?: any;
    private pollingHandleTransfer?: any;
    private readonly destroy$ = new Subject<void>();

    constructor(
        private readonly route: ActivatedRoute,
        private readonly router: Router,
        private readonly catalogService: CatalogBrowserService,
        private readonly transferService: TransferProcessService,
        private readonly edrService: EdrService,
        private readonly publicService: PublicService,
        private readonly participantsRegistry: ParticipantsRegistryService,
        private readonly notificationService: NotificationService,
        private readonly appConfigService: AppConfigService,
        private readonly unauthorizedState: UnauthorizedStateService,
        private readonly cdref: ChangeDetectorRef,
        public readonly utilService: UtilService,
        public readonly dialog: MatDialog
    ) {}

    ngOnInit(): void {
        this.unauthorizedState
        .isUnauthorized$('catalog')
        .pipe(takeUntil(this.destroy$))
        .subscribe((isUnauthorized) => {
            this.isUnauthorized = isUnauthorized;
            if (isUnauthorized) {
                this.offer = undefined;
                this.metadata = {};
            }
        });

        this.offerId = this.route.snapshot.paramMap.get('id') ?? '';
        this.participantId = this.route.snapshot.queryParamMap.get('participantId') ?? '';
        this.loadOffer();
    }

    ngOnDestroy(): void {
        this.destroy$.next();
        this.destroy$.complete();
        if (this.pollingHandleNegotiation) {
            clearInterval(this.pollingHandleNegotiation);
        }
        if (this.pollingHandleTransfer) {
            clearInterval(this.pollingHandleTransfer);
        }
    }

    private loadOffer(): void {
        if (!this.offerId) {
            this.loadError = 'Missing offer id.';
            this.isLoading = false;
            return;
        }

        if (!this.participantId) {
            this.loadError = 'Missing participant id. Open this offer from the catalog.';
            this.isLoading = false;
            return;
        }

        this.isLoading = true;

        this.participantsRegistry.getOriginator(this.participantId)
        .pipe(first())
        .subscribe({
            next: originator => {
                if (!originator) {
                    this.loadError = `Participant ${this.participantId} not found in registry.`;
                    this.isLoading = false;
                    return;
                }
                this.requestDataset(originator, this.participantId);
            },
            error: err => {
                console.error(err);
                this.loadError = 'Failed to load participant registry.';
                this.isLoading = false;
            }
        });
    }

    private requestDataset(originator: string, participantId: string): void {
        this.catalogService.requestDatasetOfferById(originator, this.offerId, participantId)
        .pipe(first())
        .subscribe({
            next: offer => {
                this.offer = offer;
                const extracted = this.extractMetadata(offer, offer.assetId);
                this.metadata = this.hasMetadataValue(extracted)
                    ? extracted
                    : {};
                this.isLoading = false;
            },
            error: (err: HttpErrorResponse) => {
                if (this.unauthorizedState.isUnauthorized('catalog')) {
                    return;
                }
                this.notificationService.showError('Failed to load offer details');
                this.isLoading = false;
                console.error(err);
            }
        });
    }

    onNegotiateClicked(): void {
        if (!this.offer || this.negotiationInProgress) {
            return;
        }

        const initiateRequest: any = {
            "@context": {
                "edc": "https://w3id.org/edc/v0.0.1/ns/"
            },
            "@type": "ContractRequest",
            counterPartyAddress: this.offer.originator,
            protocol: "dataspace-protocol-http",
            policy: {
                "@context": "http://www.w3.org/ns/odrl.jsonld",
                "@id": `${this.offer.id}`,
                "@type": "Offer",
                assigner: `${this.offer.participantId}`,
                target: `${this.offer.assetId}`,
                obligation: this.offer.policy.obligation,
                permission: this.offer.policy.permission,
                prohibition: this.offer.policy.prohibition,
            }
        };

        const finishedNegotiationStates = [
            "FINALIZED",
            "VERIFIED",
            "TERMINATED",
            "ERROR"
        ];

        this.negotiationInProgress = true;
        this.negotiationState = 'REQUESTED';

        this.catalogService.initiateNegotiation(initiateRequest).subscribe(negotiationId => {
        if (!this.pollingHandleNegotiation) {
            this.pollingHandleNegotiation = setInterval(() => {
                this.catalogService.getNegotiationState(negotiationId).subscribe(updatedNegotiation => {
                    this.negotiation = updatedNegotiation;
                    this.negotiationState = updatedNegotiation.state ?? 'UNKNOWN';

                    if (updatedNegotiation.state === 'TERMINATED') {
                        const rawError = updatedNegotiation["https://w3id.org/edc/v0.0.1/ns/errorDetail"]?.[0]?.["@value"];
                        if (rawError) {
                            try {
                                const messageJson = JSON.parse(rawError);
                                const messageString = messageJson["dspace:reason"] ?? '';
                                if (messageString) {
                                    this.notificationService.showError(`Error starting negotiation (${messageString})`);
                                }
                            } catch (e) {
                                this.notificationService.showError('Error starting negotiation');
                            }
                        }
                    }

                    if (finishedNegotiationStates.includes(updatedNegotiation.state ?? '')) {
                        this.negotiationInProgress = false;
                        clearInterval(this.pollingHandleNegotiation);
                        this.pollingHandleNegotiation = undefined;

                        if (updatedNegotiation.state === 'VERIFIED' || updatedNegotiation.state === 'FINALIZED') {
                            this.contractAgreementId = this.getContractAgreementId(updatedNegotiation);
                            this.notificationService.showInfo('Contract negotiation complete!');
                        }
                    }
                });
            }, 1000);
        }
        }, error => {
            this.negotiationInProgress = false;
            console.error(error);
            this.notificationService.showError('Error starting negotiation');
        });
    }

    onTransferClicked(): void {
        if (!this.offer || !this.contractAgreementId || this.isTransferInProgress()) {
            return;
        }

        const dialogRef = this.dialog.open(CatalogBrowserTransferDialog, {
            data: {
                isProxyPath: this.offer.properties.proxyPath ?? false,
                isProxyQueryParams: this.offer.properties.proxyQueryParams ?? false,
            }
        });

        dialogRef.afterClosed().pipe(first()).subscribe(result => {
            if (result === undefined || result.storageTypeId === undefined || result.storageTypeId === "") {
                return;
            }

            console.log('[Transfer] Dialog result:', result);

            const storageTypeId: string = result.storageTypeId;
            const proxyDataAddressOptions: any = {
                proxyPath: result.proxyUrlPath,
                proxyQueryParams: result.proxyQueryParams
            };

            this.createTransferRequest(this.contractAgreementId!, storageTypeId, proxyDataAddressOptions)
                .pipe(switchMap(trq => this.transferService.initiateTransfer(trq)))
                .subscribe(transferId => {
                    console.log(`[Transfer] Initiated with ID:`, transferId);
                    this.startPolling(transferId, this.contractAgreementId!, storageTypeId, proxyDataAddressOptions);
                }, error => {
                    console.error('[Transfer] Error initiating transfer:', error);
                    this.notificationService.showError('Error initiating transfer');
                });
        });
    }

    isTransferInProgress(): boolean {
        return this.runningTransfers.length > 0;
    }

    getTransferState(): string {
        const current = this.runningTransfers[0];
        if (!current) {
            return 'IDLE';
        }
        if (typeof current.state === 'string') {
            return current.state;
        }
        return TransferProcessStates[current.state];
    }

    hasMetadata(): boolean {
        return this.hasMetadataValue(this.metadata);
    }

    hasSpatialData(): boolean {
        if (!this.metadata) return false;
        const spatialKey = 'dct:spatial';
        return !!this.metadata[spatialKey];
    }

    getSpatialData(): any {
        if (!this.metadata) return null;
        const spatialKey = 'dct:spatial';
        console.log(`[Spatial Data] Key: ${spatialKey}, Value:`, this.metadata[spatialKey] || null);
        return this.metadata[spatialKey] || null;
    }

    getOfferTitle(): string {
        return this.offer?.properties?.name || this.offer?.assetId || 'Offer';
    }

    backToCatalog(): void {
        this.router.navigate(['/browse-catalog']);
    }

    private static isFinishedState(state: string): boolean {
        return [
            'STARTED',
            'COMPLETED',
            'ERROR',
            'ENDED'
        ].includes(state);
    }

    private createTransferRequest(contractId: string, storageTypeId: string, proxyDataAddressOptions: any) {
        const backendUrl = this.appConfigService.getConfig()?.backendUrl;

        const callbackAddresses = [];

        if (storageTypeId == MINIO_STORAGE_TYPE && backendUrl) {
        callbackAddresses.push(
            {
            "events": [
                "transfer.process.started"
            ],
            "uri": this.getUrlWithQueryParams(backendUrl, proxyDataAddressOptions)
            }
        );
        }

        const initiateTransfer: any = {
            connectorId: this.offer?.participantId,
            counterPartyAddress: this.offer?.originator,
            contractId: contractId,
            assetId: this.offer?.assetId,
            transferType: 'HttpData-PULL',
            dataDestination: {
                "type": storageTypeId,
            },
            callbackAddresses: callbackAddresses
        };
        console.log('[Transfer] Request payload:', initiateTransfer);

        return of(initiateTransfer);
    }

    private startPolling(transferProcessId: IdResponse, contractId: string, storageType: string, proxyDataAddressOptions: any) {
        this.runningTransfers.push({
            processId: transferProcessId.id!,
            state: TransferProcessStates.REQUESTED,
            contractId: contractId,
            storageType: storageType,
            proxyDataAddressOptions: proxyDataAddressOptions,
            isTransferStarted: false,
        });

        if (!this.pollingHandleTransfer) {
            this.pollingHandleTransfer = setInterval(this.pollRunningTransfers(), 1000);
        }
    }

    private pollRunningTransfers() {
        return () => {
        scheduled(this.runningTransfers, asyncScheduler)
            .pipe(
            switchMap(runningTransferProcess => this.catalogService.getTransferProcessesById(runningTransferProcess.processId).pipe(
                map(transferProcess => ({ runningTransferProcess, transferProcess }))
            )),
            tap(({ runningTransferProcess, transferProcess }) => {
                runningTransferProcess.state = transferProcess.state ?? runningTransferProcess.state;
                console.log(`[Poll] Transfer ${runningTransferProcess.processId} state: ${transferProcess.state}`);
            }),
            filter(({ runningTransferProcess, transferProcess }) =>
                OfferDetailsComponent.isFinishedState(transferProcess.state!) && !runningTransferProcess.isTransferStarted),
            tap(({ runningTransferProcess, transferProcess }) => {
                console.log(`[Transfer] Starting download for ${runningTransferProcess.processId} in state: ${transferProcess.state}`);
                try {
                    runningTransferProcess.isTransferStarted = true;
                    this.processStartedTransfer(
                        transferProcess, runningTransferProcess.storageType, runningTransferProcess.proxyDataAddressOptions
                    );
                } catch (err) {
                    console.error(`[Transfer Error] Failed to process transfer ${runningTransferProcess.processId}:`, err);
                    runningTransferProcess.isTransferStarted = false;
                }
            })
            )
            .subscribe(() => {
                // clear interval if necessary
                if (this.runningTransfers.length === 0) {
                    clearInterval(this.pollingHandleTransfer);
                    this.pollingHandleTransfer = undefined;
                    console.log('[Poll] Cleared interval');
                }
            }, error => {
                console.error('[Poll Error]', error);
                this.notificationService.showError(error);
            });
        };
    }

    private processStartedTransfer = (transfer: TransferProcess, storageType: string, proxyDataAddressOptions: any) => {
        console.log('[Transfer] Process started:', transfer);
        console.log('[Transfer] Storage type:', storageType);

        if (storageType == MINIO_STORAGE_TYPE) {
            console.log(`[Transfer] MinIO transfer completed: ${transfer.id}`);
            this.completeTransfer(transfer);
            return;
        }

        this.processStartedLocalTransfer(transfer, proxyDataAddressOptions);
    }

    private processStartedLocalTransfer = async (transfer: TransferProcess, proxyDataAddressOptions: any) => {
        console.log('[Transfer] Starting local transfer for:', transfer);
        try {
            const address = await this.edrService.requestDataAddress(transfer.id).toPromise();
            console.log('[EDR] Received address:', address);

            const endpoint = address["https://w3id.org/edc/v0.0.1/ns/endpoint"][0]["@value"];
            const authCode = address["https://w3id.org/edc/v0.0.1/ns/authorization"][0]["@value"];
            console.log('[EDR] Endpoint:', endpoint);
            console.log('[EDR] AuthCode:', authCode);

            const adjustedEndpoint = this.adjustServiceUrl(endpoint);
            const publicEndpoint = this.getUrlWithQueryParams(adjustedEndpoint, proxyDataAddressOptions);
            console.log('[EDR] Public endpoint:', publicEndpoint);

            const context = new EdcConnectorClientContext(undefined, {
                public: publicEndpoint
            });
            console.log('[EDR] Context public:', context.public);

            const data: Response = await this.publicService.getTransferredData(authCode, context).toPromise();
            console.log('[Data] Response:', data);

            // Stop polling immediately - file will download in background
            this.completeTransfer(transfer);
            
            // Start download in background (don't await)
            this.isDownloading = true;
            this.notificationService.showInfo('Download started, please wait...');
            this.saveFileToDownloads(data, transfer);
        } catch (e: any) {
            const message = (e as Error).message;
            console.log('[Transfer] Error:', e);
            this.isDownloading = false;
            this.notificationService.showError(message);
        }
    }

    private saveFileToDownloads = async (data: Response, transfer: TransferProcess) => {
        try {
            const contentType = data.headers.get('Content-Type') || 'application/octet-stream';
            console.log('[Download] Starting blob conversion...');
            const blob = await data.blob();
            console.log('[Download] Blob created, size:', blob.size, 'bytes');

            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;

            const extension = MIME_TO_EXTENSION[contentType] || '';
            a.download = `${transfer.assetId}${extension}`;

            console.log('[Download] Initiating browser download:', a.download);
            document.body.appendChild(a);
            a.click();
            
            // Give browser time to start download before cleanup
            await new Promise(resolve => setTimeout(resolve, 100));
            
            URL.revokeObjectURL(url);
            document.body.removeChild(a);
            console.log('[Download] File download initiated successfully');
            
            this.isDownloading = false;
            this.notificationService.showInfo(`File downloaded: ${a.download}`);
        } catch (err) {
            console.error('[Download] Error:', err);
            this.isDownloading = false;
            this.notificationService.showError('Download failed');
        }
    };

    private adjustServiceUrl = (url: string): string => {
        try {
            const parsedUrl = new URL(url);

            if (parsedUrl.protocol === 'http:' && this.appConfigService.getConfig()?.deploymentMode === 'local') {
                parsedUrl.hostname = 'localhost';
            }

            return parsedUrl.toString();
        } catch (error) {
            console.error('Invalid URL provided:', error);
            return url;
        }
    }

    private completeTransfer = (transferProcess: any) => {
        this.runningTransfers = this.runningTransfers.filter(rtp => rtp.processId !== transferProcess.id);
        this.notificationService.showInfo(`Transfer [${transferProcess.id}] complete!`, 'Show me!', () => {
            this.router.navigate(['/transfer-history']);
        });
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

    private extractMetadata(payload: any, assetId: string): any {
        if (!payload) {
            return {};
        }

        const datasetKeys = [
            DATASET_CONTEXT,
            'dcat:dataset',
            'http://www.w3.org/ns/dcat#dataset'
        ];

        let datasets: any[] = [];
        for (const key of datasetKeys) {
            if (payload[key]) {
                datasets = Array.isArray(payload[key]) ? payload[key] : [payload[key]];
                break;
            }
        }

        if (datasets.length === 0 && payload['@id'] === assetId) {
            datasets = [payload];
        }

        const dataset = datasets.find((_asset: any) => {
            return _asset['@id'] === assetId || _asset.id === assetId;
        }) ?? datasets[0];

        if (!dataset) {
            return {};
        }

        if (dataset['metadata']) {
            return dataset['metadata'];
        }

        if (dataset[METADATA_CONTEXT]?.[0]) {
            return dataset[METADATA_CONTEXT][0];
        }

        return {};
    }

    private hasMetadataValue(value: any): boolean {
        if (!value) {
            return false;
        }
        for (const prop in value) {
            if (Object.prototype.hasOwnProperty.call(value, prop) && value[prop] !== null) {
                return true;
            }
        }
        return false;
    }

    private getContractAgreementId(negotiation: ContractNegotiation): string | undefined {
        const direct = (negotiation as any).contractAgreementId;
        if (direct) {
            return direct;
        }

        const iri = (negotiation as any)["https://w3id.org/edc/v0.0.1/ns/contractAgreementId"];
        if (Array.isArray(iri) && iri[0]) {
            return iri[0]['@id'] || iri[0]['@value'];
        }

        return undefined;
    }

    ngAfterContentChecked() {
        this.cdref.detectChanges();
    }
}
