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
import { DATASET_CONTEXT, METADATA_CONTEXT, STORAGE_TYPE } from 'src/modules/app/variables';
import { UnauthorizedStateService } from 'src/modules/app/auth/unauthorized-state.service';
import { CatalogBrowserTransferDialog } from '../catalog-browser-transfer-dialog/catalog-browser-transfer-dialog.component';
import { ContractOffer } from '../../models/contract-offer';
import { TransferProcessStates } from '../../models/transfer-process-states';
import { CatalogBrowserService, NotificationService, UtilService } from '../../services';

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
    originator = '';
    offer?: ContractOffer;
    metadata: any = {};
    isUnauthorized = false;
    isLoading = true;
    loadError = '';

    downloadProgress = 0;
    downloadedSizeMB = 0;
    hasContentLength = false;
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
        this.originator = this.route.snapshot.queryParamMap.get('originator') ?? '';
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

        if (!this.originator) {
            this.loadError = 'Missing originator. Open this offer from the catalog.';
            this.isLoading = false;
            return;
        }

        this.isLoading = true;

        this.requestDataset(this.originator, this.participantId);
    }

    private requestDataset(originator: string, participantId: string): void {
        this.catalogService.requestDatasetOfferById(originator, this.offerId, participantId)
        .pipe(first())
        .subscribe({
            next: offer => {
                this.offer = offer;
                console.log(offer);
                console.log(typeof offer.properties.proxyPath);
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
                        } else if (updatedNegotiation.state === 'ERROR') {
                            this.notificationService.showError('Negotiation failed - stopped polling');
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
                isProxyPath: this.isAllowed(this.offer.properties.proxyPath),
                isProxyQueryParams: this.isAllowed(this.offer.properties.proxyQueryParams),
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

        if (storageTypeId == STORAGE_TYPE && backendUrl) {
        callbackAddresses.push(
            {
            "events": [
                "transfer.process.started"
            ],
            "uri": this.getCallbackUrl(backendUrl, proxyDataAddressOptions)
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
                // Handle error state
                if (transferProcess.state === 'ERROR') {
                    console.error(`[Transfer] Transfer ${runningTransferProcess.processId} failed`);
                    this.runningTransfers = this.runningTransfers.filter(rtp => rtp.processId !== transferProcess.id);
                    this.notificationService.showError(`Transfer failed - stopped polling`);
                    return;
                }

                // Handle success states
                console.log(`[Transfer] Starting download for ${runningTransferProcess.processId} in state: ${transferProcess.state}`);
                try {
                    runningTransferProcess.isTransferStarted = true;
                    this.processStartedTransfer(
                        transferProcess, runningTransferProcess.storageType, runningTransferProcess.proxyDataAddressOptions
                    );
                } catch (err) {
                    console.error(`[Transfer Error] Failed to process transfer ${runningTransferProcess.processId}:`, err);
                    runningTransferProcess.isTransferStarted = false;
                    // Remove from running transfers on error
                    this.runningTransfers = this.runningTransfers.filter(rtp => rtp.processId !== transferProcess.id);
                    this.notificationService.showError(`Transfer processing failed - stopped polling`);
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

        if (storageType == STORAGE_TYPE) {
            console.log(`[Transfer] Storage transfer completed: ${transfer.id}`);
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
            console.log('[EDR] Proxy options:', proxyDataAddressOptions);

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
            this.downloadProgress = 0;
            this.downloadedSizeMB = 0;
            this.hasContentLength = false;
            this.notificationService.showInfo('Download started, please wait...');
            this.saveFileToDownloads(data, transfer, publicEndpoint);
        } catch (e: any) {
            const message = (e as Error).message;
            console.log('[Transfer] Error:', e);
            this.isDownloading = false;
            this.notificationService.showError(message);
            // Ensure transfer is removed from running transfers on error (without success notification)
            this.runningTransfers = this.runningTransfers.filter(rtp => rtp.processId !== transfer.id);
        }
    }

    private getFileExtensionFromUrl(urlString: string): string | null {
        try {
            const url = new URL(urlString);
            const pathname = url.pathname;
            const lastDot = pathname.lastIndexOf('.');
            if (lastDot > 0) {
                return pathname.substring(lastDot);
            }
        } catch (e) {
            console.log('[Download] Failed to parse URL for extension:', e);
        }
        return null;
    }

    private determineFileExtension(contentType: string | null, endpointUrl?: string): string {
        // Priority 1: Check MIME_TO_EXTENSION mapping (excluding application/octet-stream)
        if (contentType && contentType !== 'application/octet-stream' && MIME_TO_EXTENSION[contentType]) {
            console.log('[Download] Using extension from Content-Type:', contentType);
            return MIME_TO_EXTENSION[contentType];
        }

        // Priority 2: Try to extract extension from endpoint URL
        if (endpointUrl) {
            const urlExtension = this.getFileExtensionFromUrl(endpointUrl);
            if (urlExtension) {
                console.log('[Download] Using extension from endpoint URL:', urlExtension);
                return urlExtension;
            }
        }

        // Priority 3: Fallback to .json as default
        console.log('[Download] Using default .json extension');
        return '.json';
    }

    private saveFileToDownloads = async (data: Response, transfer: TransferProcess, endpointUrl?: string) => {
        try {
            const contentType = data.headers.get('Content-Type');
            const contentDisposition = data.headers.get('Content-Disposition') || '';
            const contentLength = data.headers.get('Content-Length');
            const totalSize = contentLength ? parseInt(contentLength, 10) : 0;
            
            console.log('[Download] Response headers:');
            console.log('[Download] Content-Type:', contentType);
            console.log('[Download] Content-Disposition:', contentDisposition);
            console.log('[Download] Content-Length:', contentLength);
            console.log('[Download] Endpoint URL:', endpointUrl);
            console.log('[Download] Total size:', totalSize, 'bytes');
            console.log('[Download] All headers:', {
                'content-type': contentType,
                'content-disposition': contentDisposition,
                'content-length': contentLength
            });
            
            console.log('[Download] Starting blob conversion with progress tracking...');
            const blob = await this.readResponseAsBlob(data, totalSize);
            console.log('[Download] Blob created, size:', blob.size, 'bytes');
            console.log('[Download] Blob type:', blob.type);

            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;

            const extension = this.determineFileExtension(contentType, endpointUrl);
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
            this.downloadProgress = 0;
            this.downloadedSizeMB = 0;
            this.notificationService.showInfo(`File downloaded: ${a.download}`);
        } catch (err) {
            console.error('[Download] Error:', err);
            this.isDownloading = false;
            this.downloadProgress = 0;
            this.downloadedSizeMB = 0;
            this.notificationService.showError('Download failed');
        }
    };

    private readResponseAsBlob = async (data: Response, totalSize: number): Promise<Blob> => {
        if (!data.body) {
            return await data.blob();
        }

        const reader = data.body.getReader();
        const chunks: Uint8Array[] = [];
        let downloadedSize = 0;
        const hasContentLength = totalSize > 0;

        try {
            while (true) {
                const { done, value } = await reader.read();
                if (done) break;

                chunks.push(value);
                downloadedSize += value.length;

                if (hasContentLength) {
                    this.downloadProgress = Math.round((downloadedSize / totalSize) * 100);
                    console.log(`[Download] Progress: ${downloadedSize}/${totalSize} bytes (${this.downloadProgress}%)`);
                } else {
                    // No Content-Length - show downloaded size in MB
                    this.downloadedSizeMB = parseFloat((downloadedSize / (1024 * 1024)).toFixed(2));
                    console.log(`[Download] Downloaded: ${this.downloadedSizeMB} MB (${downloadedSize} bytes)`);
                }
                
                // Update flag for template
                this.hasContentLength = hasContentLength;
            }
        } finally {
            reader.releaseLock();
        }

        const buffer = new Uint8Array(downloadedSize);
        let offset = 0;
        for (const chunk of chunks) {
            buffer.set(chunk, offset);
            offset += chunk.length;
        }

        const contentType = data.headers.get('Content-Type') || 'application/json';
        return new Blob([buffer], { type: contentType });
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

    private getCallbackUrl(url: string, proxyDataAddressOptions: any) {
        const callbackUrl = new URL(this.getUrlWithQueryParams(url, proxyDataAddressOptions));
        const connectorId = this.appConfigService.getConfig()?.connectorId || 'consumer';
        callbackUrl.searchParams.set('requester', connectorId);
        return callbackUrl.toString();
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
