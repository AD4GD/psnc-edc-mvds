import {Component, OnInit} from '@angular/core';
import {BehaviorSubject, Observable, of} from 'rxjs';
import {first, map, switchMap, tap} from 'rxjs/operators';
import {MatDialog} from '@angular/material/dialog';
import {
  ContractDefinitionEditorDialog
} from '../contract-definition-editor-dialog/contract-definition-editor-dialog.component';
import { ContractDefinitionService, QUERY_LIMIT } from "../../../mgmt-api-client";
import {ConfirmationDialogComponent, ConfirmDialogModel} from "../confirmation-dialog/confirmation-dialog.component";
import {NotificationService} from "../../services/notification.service";
import { ContractDefinitionInput, ContractDefinition } from "../../../mgmt-api-client/model"
import { SorterService } from '../../services/common/sorter.service';


@Component({
  selector: 'edc-demo-contract-definition-viewer',
  templateUrl: './contract-definition-viewer.component.html',
  styleUrls: ['./contract-definition-viewer.component.scss']
})
export class ContractDefinitionViewerComponent implements OnInit {

  filteredContractDefinitions$: Observable<ContractDefinition[]> = of([]);
  searchText = '';
  private fetch$ = new BehaviorSubject(null);

  constructor(
    private contractDefinitionService: ContractDefinitionService,
    private notificationService: NotificationService,
    private readonly dialog: MatDialog,
    private readonly sorterService: SorterService
  ) { }

  ngOnInit(): void {
    this.filteredContractDefinitions$ = this.fetch$.pipe(
      switchMap(() => {
        const contractDefinitions$ = this.contractDefinitionService.queryAllContractDefinitions({
          limit : QUERY_LIMIT,
          offset : 0,
        }).pipe(
          map(contractDefinitions => {
            return contractDefinitions.sort((a, b) => 
              this.sorterService.naturalSort(a.id, b.id))
            })
        );
        return !!this.searchText ?
          contractDefinitions$.pipe(map(contractDefinitions => contractDefinitions.filter(contractDefinition => contractDefinition['@id']!.toLowerCase().includes(this.searchText.toLowerCase()))))
          :
          contractDefinitions$;
      }));
  }

  onSearch() {
    this.fetch$.next(null);
  }

  onDelete(contractDefinition: ContractDefinition) {
    const dialogData = ConfirmDialogModel.forDelete("contract definition", contractDefinition.id);

    const ref = this.dialog.open(ConfirmationDialogComponent, {data: dialogData});

    ref.afterClosed().subscribe(res => {
      if (res) {
        this.contractDefinitionService.deleteContractDefinition(contractDefinition.id)
          .subscribe(() => this.fetch$.next(null));
      }
    });

  }

  shouldShowTooltip(element: HTMLElement, value: string | undefined): boolean {
    if (!element || !value) return false;
    return element.offsetWidth < element.scrollWidth;
  }

  onCreate() {
    const dialogRef = this.dialog.open(ContractDefinitionEditorDialog);
    dialogRef.afterClosed().pipe(first()).subscribe((result: { contractDefinition?: ContractDefinitionInput }) => {
      const newContractDefinition = result?.contractDefinition;
      if (newContractDefinition) {
        this.contractDefinitionService.createContractDefinition(newContractDefinition)
          .subscribe({
              next: () => this.fetch$.next(null),
              error: () => this.notificationService.showError("Contract definition cannot be created"),
              complete: () => this.notificationService.showInfo("Contract definition created")
          });
      }
    });
  }

}
