import { ChangeDetectorRef, Component, OnInit } from '@angular/core';
import { first } from 'rxjs/operators';
import { MatDialog } from '@angular/material/dialog';
import { ContractDefinitionEditorDialog } from '../contract-definition-editor-dialog/contract-definition-editor-dialog.component';
import { ContractDefinitionService, QUERY_LIMIT } from "../../../mgmt-api-client";
import { ConfirmationDialogComponent, ConfirmDialogModel } from "../confirmation-dialog/confirmation-dialog.component";
import { NotificationService, SorterService, UtilService } from "../../services";
import { ContractDefinitionInput, ContractDefinition } from "../../../mgmt-api-client/model"
import { PageEvent } from '@angular/material/paginator';


@Component({
  selector: 'edc-demo-contract-definition-viewer',
  templateUrl: './contract-definition-viewer.component.html',
  styleUrls: ['./contract-definition-viewer.component.scss']
})
export class ContractDefinitionViewerComponent implements OnInit {
  searchText = '';
  pageIndex = 0;
  pageSize = 20;
  allContractDefinitions: ContractDefinition[] = [];
  pagedContractDefinitions: ContractDefinition[] = [];
  filteredContractDefinitions: ContractDefinition[] = [];

  constructor(
    private contractDefinitionService: ContractDefinitionService,
    private notificationService: NotificationService,
    private readonly dialog: MatDialog,
    private readonly sorterService: SorterService,
    private readonly cdref: ChangeDetectorRef,
    public readonly utilService: UtilService,
  ) { }

  loadContractDefinitions() {
    this.contractDefinitionService.queryAllContractDefinitions({ 
      limit: QUERY_LIMIT,
      offset: 0 
    }).subscribe(contractDefinitions => {
      this.allContractDefinitions = contractDefinitions.sort((a, b) =>
        this.sorterService.naturalSort( a.id, b.id )
      );
      this.applyFilterAndPagination();
    });
  }

  ngOnInit(): void {
    this.loadContractDefinitions();
  }

  applyFilterAndPagination() {
      // Filtering
      if (this.searchText) {
        this.filteredContractDefinitions = this.allContractDefinitions.filter(contractDefinition =>
          contractDefinition.id.toLowerCase().includes(this.searchText.toLowerCase())
        );
      } else {
        this.filteredContractDefinitions = [...this.allContractDefinitions];
      }
      // Reset pageIndex if out of bands
      if (this.pageIndex * this.pageSize >= this.filteredContractDefinitions.length && this.filteredContractDefinitions.length > 0) {
        this.pageIndex = 0;
      }
      // Pagination
      const start = this.pageIndex * this.pageSize;
      const end = start + this.pageSize;
      this.pagedContractDefinitions = this.filteredContractDefinitions.slice(start, end);
    }

  onSearch() {
    this.pageIndex = 0;
    // this.fetch$.next(null);
    this.applyFilterAndPagination();
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
    this.applyFilterAndPagination();
  }

  onDelete(contractDefinition: ContractDefinition) {
    const dialogData = ConfirmDialogModel.forDelete("contract definition", contractDefinition.id);

    const ref = this.dialog.open(ConfirmationDialogComponent, {data: dialogData});

    ref.afterClosed().subscribe(res => {
      if (res) {
        this.contractDefinitionService.deleteContractDefinition(contractDefinition.id)
          .subscribe(() => this.loadContractDefinitions());
      }
    });

  }

  onCreate() {
    const dialogRef = this.dialog.open(ContractDefinitionEditorDialog);
    dialogRef.afterClosed().pipe(first()).subscribe((result: { contractDefinition?: ContractDefinitionInput }) => {
      const newContractDefinition = result?.contractDefinition;
      if (newContractDefinition) {
        this.contractDefinitionService.createContractDefinition(newContractDefinition)
          .subscribe({
              next: () => this.loadContractDefinitions(),
              error: () => this.notificationService.showError("Contract definition cannot be created"),
              complete: () => this.notificationService.showInfo("Contract definition created")
          });
      }
    });
  }

  ngAfterContentChecked() {
    this.cdref.detectChanges();
  }
}
