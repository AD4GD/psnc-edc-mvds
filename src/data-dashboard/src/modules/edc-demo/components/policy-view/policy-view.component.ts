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
  searchText: string = '';
  pageIndex = 0;
  pageSize = 20;
  allPolicies: PolicyDefinition[] = [];
  pagedPolicies: PolicyDefinition[] = [];
  filteredPolicies: PolicyDefinition[] = [];
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
      this.applyFilterAndPagination();
    });
  }

  ngOnInit(): void {
    this.loadPolicies();
  }

  applyFilterAndPagination() {
    // Filtering
    if (this.searchText) {
      this.filteredPolicies = this.allPolicies.filter(policy =>
        (policy.id).toLowerCase().includes(this.searchText.toLowerCase()) ||
        policy.policy.assigner?.toLowerCase().includes(this.searchText.toLowerCase()) ||
        policy.policy.assignee?.toLowerCase().includes(this.searchText.toLowerCase())
      );
    } else {
      this.filteredPolicies = [...this.allPolicies];
    }
    // Reset pageIndex if out of bands
    if (this.pageIndex * this.pageSize >= this.filteredPolicies.length && this.filteredPolicies.length > 0) {
      this.pageIndex = 0;
    }
    // Pagination
    const start = this.pageIndex * this.pageSize;
    const end = start + this.pageSize;
    this.pagedPolicies = this.filteredPolicies.slice(start, end);
  }

  onSearch() {
    this.pageIndex = 0;
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
