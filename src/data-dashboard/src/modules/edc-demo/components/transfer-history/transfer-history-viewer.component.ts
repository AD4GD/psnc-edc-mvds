import {Component, OnInit} from '@angular/core';
import {map, Observable, of} from 'rxjs';
import {QUERY_LIMIT, TransferProcessService} from "../../../mgmt-api-client";
import {TransferProcess} from "../../../mgmt-api-client/model";
import {AppConfigService} from "../../../app/app-config.service";
import {ConfirmationDialogComponent, ConfirmDialogModel} from "../confirmation-dialog/confirmation-dialog.component";
import {MatDialog} from "@angular/material/dialog";
import { SorterService } from '../../services/common/sorter.service';

@Component({
  selector: 'edc-demo-transfer-history',
  templateUrl: './transfer-history-viewer.component.html',
  styleUrls: ['./transfer-history-viewer.component.scss']
})
export class TransferHistoryViewerComponent implements OnInit {

  columns: string[] = ['id', 'state', 'lastUpdated', 'connectorId', 'assetId', 'contractId', 'action'];
  transferProcesses$: Observable<TransferProcess[]> = of([]);
  storageExplorerLinkTemplate: string | undefined;

  constructor(
    private transferProcessService: TransferProcessService,
    private dialog : MatDialog,
    private appConfigService: AppConfigService,
    private readonly sorterService: SorterService
  ) { }

  ngOnInit(): void {
    this.loadTransferProcesses();
    this.storageExplorerLinkTemplate = this.appConfigService.getConfig()?.storageExplorerLinkTemplate
  }

  onDeprovision(transferProcess: TransferProcess): void {

    const dialogData = new ConfirmDialogModel("Confirm deprovision", `Deprovisioning resources for transfer [${transferProcess["@id"]}] will take some time and once started, it cannot be stopped.`)
    dialogData.confirmColor = "warn";
    dialogData.confirmText = "Confirm";
    dialogData.cancelText = "Abort";
    const ref = this.dialog.open(ConfirmationDialogComponent, {data: dialogData});

    ref.afterClosed().subscribe(res => {
      if (res) {
       this.transferProcessService.deprovisionTransferProcess(transferProcess["@id"]!).subscribe(() => this.loadTransferProcesses());
      }
    });
  }

  showStorageExplorerLink(transferProcess: TransferProcess) {
    return transferProcess.dataDestination?.properties?.type === 'AzureStorage' && transferProcess.state === 'COMPLETED';
  }

  showDeprovisionButton(transferProcess: TransferProcess) {
    return ['COMPLETED', 'PROVISIONED', 'REQUESTED', 'REQUESTED_ACK', 'IN_PROGRESS', 'STREAMING'].includes(transferProcess.state!);
  }

  loadTransferProcesses() {
    this.transferProcesses$ = this.transferProcessService.queryAllTransferProcesses({
      limit : QUERY_LIMIT,
      offset : 0
    }).pipe(
      map(transferProcesses => { 
        return transferProcesses.sort((a, b) => {
          // Sort by contractSigningDate (descending)
          const dateA = a.createdAt || 0;
          const dateB = b.createdAt || 0;
          if (dateA !== dateB) {
            return dateB - dateA; // Newest first
          }
          return this.sorterService.naturalSort(a.id, b.id); // Fallback to natural sort on createdAt)
        })
      })
    );
  }

  asDate(epochMillis?: number) {
    return epochMillis ? new Date(epochMillis).toLocaleDateString() : '';
  }
}
