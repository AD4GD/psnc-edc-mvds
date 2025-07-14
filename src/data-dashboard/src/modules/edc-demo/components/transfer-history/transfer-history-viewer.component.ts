import { Component, OnInit } from '@angular/core';
import { QUERY_LIMIT, TransferProcessService } from "../../../mgmt-api-client";
import { TransferProcess } from "../../../mgmt-api-client/model";
import { AppConfigService } from "../../../app/app-config.service";
import { ConfirmationDialogComponent, ConfirmDialogModel } from "../confirmation-dialog/confirmation-dialog.component";
import { MatDialog } from "@angular/material/dialog";
import { PageEvent } from '@angular/material/paginator';

@Component({
  selector: 'edc-demo-transfer-history',
  templateUrl: './transfer-history-viewer.component.html',
  styleUrls: ['./transfer-history-viewer.component.scss']
})
export class TransferHistoryViewerComponent implements OnInit {
  columns: string[] = ['id', 'state', 'lastUpdated', 'connectorId', 'assetId', 'contractId', 'action'];
  transferProcesses: TransferProcess[] = [];
  pagedTransferProcesses: TransferProcess[] = [];
  storageExplorerLinkTemplate: string | undefined;
  pageIndex = 0;
  pageSize = 20;

  constructor(
    private transferProcessService: TransferProcessService,
    private dialog : MatDialog,
    private appConfigService: AppConfigService,
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
    this.transferProcessService.queryAllTransferProcesses({
      limit : QUERY_LIMIT,
      offset : 0,
      sortField: 'createdAt',
      sortOrder: 'DESC'
    })
    .subscribe(transferProcesses => { 
      this.transferProcesses = transferProcesses;
      this.applyPagination();
    })
  }

  onPageChange(event: PageEvent) {
    if (event.pageSize !== this.pageSize) {
      const firstItemIndex = this.pageIndex * this.pageSize;
      this.pageIndex = Math.floor(firstItemIndex / event.pageSize);
      this.pageSize = event.pageSize;
    } else {
      this.pageIndex = event.pageIndex;
      this.pageSize = event.pageSize;
    }
    this.applyPagination();
  }
  
  applyPagination() {
    // Reset pageIndex if out of bands
    if (this.pageIndex * this.pageSize >= this.transferProcesses.length && this.transferProcesses.length > 0) {
      this.pageIndex = 0;
    }
    // Pagination
    const start = this.pageIndex * this.pageSize;
    const end = start + this.pageSize;
    this.pagedTransferProcesses = this.transferProcesses.slice(start, end);
  }

  asDate(epochMillis?: number) {
    return epochMillis ? new Date(epochMillis).toLocaleDateString() : '';
  }
}
