import { ChangeDetectorRef, Component, OnInit } from '@angular/core';
import { PolicyService, QUERY_LIMIT } from "../../../mgmt-api-client";
import { Observer } from "rxjs";
import { first } from "rxjs/operators";
import { MatDialog } from "@angular/material/dialog";
import { NewPolicyDialogComponent } from "../new-policy-dialog/new-policy-dialog.component";
import { ConfirmationDialogComponent, ConfirmDialogModel } from "../confirmation-dialog/confirmation-dialog.component";
import { PolicyDefinition, PolicyDefinitionInput, IdResponse } from "../../../mgmt-api-client/model";
import { NotificationService, SorterService, UtilService } from '../../services';
import { PageEvent } from '@angular/material/paginator';

@Component({
  selector: 'app-policy-view',
  templateUrl: './policy-view.component.html',
  styleUrls: ['./policy-view.component.scss']
})
export class PolicyViewComponent implements OnInit {
  paginationState = {
    filteredList: [] as PolicyDefinition[],
    pagedList: [] as PolicyDefinition[],
    pageIndex: 0
  };
  searchText: string = '';
  pageSize = 20;
  allPolicies: PolicyDefinition[] = [];
  private readonly errorOrUpdateSubscriber: Observer<IdResponse>;

  constructor(
    private policyService: PolicyService,
    private notificationService: NotificationService,
    private readonly dialog: MatDialog,
    private readonly sorterService: SorterService,
    private readonly cdref: ChangeDetectorRef,
    public readonly utilService: UtilService,
  ) {
    this.errorOrUpdateSubscriber = {
      next: x => this.loadPolicies,
      error: err => this.showError(err, "An error occurred."),
      complete: () => {
        this.notificationService.showInfo("Successfully completed")
      },
    }
  }

  loadPolicies() {
    this.policyService.queryAllPolicies({ 
      limit: QUERY_LIMIT,
      offset: 0 
    }).subscribe(policies => {
      this.allPolicies = policies.sort((a, b) =>
        this.sorterService.naturalSort(
          a['@id'],
          b['@id'] 
        )
      );
      this.utilService.applyFilterAndPagination(
        this.allPolicies,
        this.pageSize,
        this.filterPolicies,
        this.searchText,
        this.paginationState
      );
    });
  }

  ngOnInit(): void {
    this.loadPolicies();
  }

  filterPolicies(mainList: PolicyDefinition[], searchText: string): PolicyDefinition[] {
    return mainList.filter(policy =>
      (policy.id).toLowerCase().includes(searchText.toLowerCase()) ||
      policy.policy.assigner?.toLowerCase().includes(searchText.toLowerCase()) ||
      policy.policy.assignee?.toLowerCase().includes(searchText.toLowerCase())
    );
  }

  onSearch() {
    this.paginationState.pageIndex = 0;
    this.utilService.applyFilterAndPagination(
      this.allPolicies,
      this.pageSize,
      this.filterPolicies,
      this.searchText,
      this.paginationState
    );
  }

  onPageChange(event: PageEvent) {
    this.utilService.onPageChange(
      event, 
      this.allPolicies,
      this.pageSize, 
      this.filterPolicies, 
      this.searchText,
      this.paginationState
    );
  }

  onCreate() {
    const dialogRef = this.dialog.open(NewPolicyDialogComponent);
    dialogRef.afterClosed().pipe(first()).subscribe({ next: (newPolicyDefinition: PolicyDefinitionInput) => {
        if (newPolicyDefinition) {
          this.policyService.createPolicy(newPolicyDefinition).subscribe(
            {
              next: (response: IdResponse) => this.errorOrUpdateSubscriber.next(response),
              error: (error: Error) => this.showError(error, "An error occurred while creating the policy.")
            }
          );
        }
      }
    });
  }

  delete(policy: PolicyDefinition) {
    let policyId = policy['@id']!;
    const dialogData = ConfirmDialogModel.forDelete("policy", policyId);
    const ref = this.dialog.open(ConfirmationDialogComponent, {data: dialogData});

    ref.afterClosed().subscribe({

      next: (res: any) => {
        if (res) {
          this.policyService.deletePolicy(policyId).subscribe(
            {
              next: (response: IdResponse) => this.errorOrUpdateSubscriber.next(response),
              error: (error: Error) => this.showError(error, "An error occurred while deleting the policy.")
            }
          );
        }
      }
    });
  }

  private showError(error: Error, errorMessage: string) {
    console.error(error);
    this.notificationService.showError(errorMessage);
  }

  ngAfterContentChecked() {
    this.cdref.detectChanges();
  }
}
