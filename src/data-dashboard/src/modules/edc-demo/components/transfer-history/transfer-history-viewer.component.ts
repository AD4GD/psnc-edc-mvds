import { HttpErrorResponse } from '@angular/common/http';
import { Component, OnDestroy, OnInit } from '@angular/core';
import { QUERY_LIMIT, TransferProcessService } from "../../../mgmt-api-client";
import { TransferProcess } from "../../../mgmt-api-client/model";
import { AppConfigService } from "../../../app/app-config.service";
import { ConfirmationDialogComponent, ConfirmDialogModel } from "../confirmation-dialog/confirmation-dialog.component";
import { MatDialog } from "@angular/material/dialog";
import { PageEvent } from '@angular/material/paginator';
import { UtilService } from '../../services';
import { Subject } from 'rxjs';
import { takeUntil } from 'rxjs/operators';
import { UnauthorizedStateService } from 'src/modules/app/auth/unauthorized-state.service';

@Component({
  selector: 'edc-demo-transfer-history',
  templateUrl: './transfer-history-viewer.component.html',
  styleUrls: ['./transfer-history-viewer.component.scss']
})
export class TransferHistoryViewerComponent implements OnInit, OnDestroy {
  paginationState = {
    filteredList: [] as TransferProcess[],
    pagedList: [] as TransferProcess[],
    pageIndex: 0,
    pageSize: 20
  };
  columns: string[] = ['id', 'state', 'lastUpdated', 'connectorId', 'assetId', 'contractId', 'action'];
  transferProcesses: TransferProcess[] = [];
  storageExplorerLinkTemplate: string | undefined;
  isUnauthorized = false;
  private readonly destroy$ = new Subject<void>();

  constructor(
    private transferProcessService: TransferProcessService,
    private dialog : MatDialog,
    private appConfigService: AppConfigService,
    private utilService: UtilService,
    private readonly unauthorizedState: UnauthorizedStateService,
  ) { }

  ngOnInit(): void {
    this.unauthorizedState
      .isUnauthorized$('management')
      .pipe(takeUntil(this.destroy$))
      .subscribe((isUnauthorized) => {
        this.isUnauthorized = isUnauthorized;
        if (isUnauthorized) {
          this.transferProcesses = [];
          this.paginationState.filteredList = [];
          this.paginationState.pagedList = [];
        }
      });

    this.loadTransferProcesses();
    this.storageExplorerLinkTemplate = this.appConfigService.getConfig()?.storageExplorerLinkTemplate
  }

  ngOnDestroy(): void {
    this.destroy$.next();
    this.destroy$.complete();
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
    .subscribe({
      next: transferProcesses => { 
        this.transferProcesses = transferProcesses;
        this.utilService.applyFilterAndPagination(
          [...this.transferProcesses],
          () => {},
          '',
          this.paginationState
        );
      },
      error: (err: HttpErrorResponse) => {
        if (this.unauthorizedState.isUnauthorized('management')) {
          return;
        }
        console.error(err);
      }
    })
  }

  onPageChange(event: PageEvent) {
    this.utilService.onPageChange(
      event, 
      [...this.transferProcesses],
      () => {},
      '', 
      this.paginationState
    );
  }

  asDate(epochMillis?: number) {
    return epochMillis ? new Date(epochMillis).toLocaleString() : '';
  }
}
