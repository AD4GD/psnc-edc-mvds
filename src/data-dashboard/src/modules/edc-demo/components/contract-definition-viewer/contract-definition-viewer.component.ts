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
  paginationState = {
    filteredList: [] as ContractDefinition[],
    pagedList: [] as ContractDefinition[],
    pageIndex: 0,
    pageSize: 20
  };
  searchText = '';
  allContractDefinitions: ContractDefinition[] = [];
  pagedContractDefinitions: ContractDefinition[] = [];

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
      this.utilService.applyFilterAndPagination(
        [...this.allContractDefinitions],
        this.filterContractDefinitions.bind(this),
        this.searchText,
        this.paginationState
      );
    });
  }

  filterContractDefinitions(mainList: ContractDefinition[]): ContractDefinition[] {
    return mainList.filter(contractDefinition =>
      contractDefinition.id.toLowerCase().includes(this.searchText.toLowerCase())
    );
  }

  ngOnInit(): void {
    this.loadContractDefinitions();
  }

  onSearch() {
    this.paginationState.pageIndex = 0;
    this.utilService.applyFilterAndPagination(
      [...this.allContractDefinitions],
      this.filterContractDefinitions.bind(this),
      this.searchText,
      this.paginationState
    );
  }
  
  onPageChange(event: PageEvent) {
    this.utilService.onPageChange(
      event, 
      [...this.allContractDefinitions],
      this.filterContractDefinitions.bind(this),
      this.searchText,
      this.paginationState
    );
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
