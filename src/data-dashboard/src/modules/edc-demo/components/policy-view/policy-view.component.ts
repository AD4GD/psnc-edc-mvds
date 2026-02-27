import { HttpErrorResponse } from '@angular/common/http';
import { ChangeDetectorRef, Component, OnDestroy, OnInit } from '@angular/core';
import { PolicyService, QUERY_LIMIT } from "../../../mgmt-api-client";
import { Observer } from "rxjs";
import { first } from "rxjs/operators";
import { MatDialog } from "@angular/material/dialog";
import { NewPolicyDialogComponent } from "../new-policy-dialog/new-policy-dialog.component";
import { ConfirmationDialogComponent, ConfirmDialogModel } from "../confirmation-dialog/confirmation-dialog.component";
import { PolicyDefinition, PolicyDefinitionInput, IdResponse } from "../../../mgmt-api-client/model";
import { NotificationService, SorterService, UtilService } from '../../services';
import { PageEvent } from '@angular/material/paginator';
import { Subject } from 'rxjs';
import { takeUntil } from 'rxjs/operators';
import { UnauthorizedStateService } from 'src/modules/app/auth/unauthorized-state.service';

@Component({
  selector: 'app-policy-view',
  templateUrl: './policy-view.component.html',
  styleUrls: ['./policy-view.component.scss']
})
export class PolicyViewComponent implements OnInit, OnDestroy {
  paginationState = {
    filteredList: [] as PolicyDefinition[],
    pagedList: [] as PolicyDefinition[],
    pageIndex: 0,
    pageSize: 20
  };
  searchText: string = '';
  allPolicies: PolicyDefinition[] = [];
  isUnauthorized = false;
  private readonly errorOrUpdateSubscriber: Observer<IdResponse>;
  private readonly destroy$ = new Subject<void>();

  constructor(
    private policyService: PolicyService,
    private notificationService: NotificationService,
    private readonly dialog: MatDialog,
    private readonly sorterService: SorterService,
    private readonly cdref: ChangeDetectorRef,
    private readonly unauthorizedState: UnauthorizedStateService,
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
      offset: 0,
      sortField: 'id',
      sortOrder: 'ASC'
    }).subscribe({
      next: policies => {
        this.allPolicies = policies
        this.utilService.applyFilterAndPagination(
          [...this.allPolicies],
          this.filterPolicies,
          this.searchText,
          this.paginationState
        );
      },
      error: (err: HttpErrorResponse) => {
        if (this.unauthorizedState.isUnauthorized('management')) {
          return;
        }
        this.showError(err as any, 'Failed to load policies');
      }
    });
  }

  ngOnInit(): void {
    this.unauthorizedState
      .isUnauthorized$('management')
      .pipe(takeUntil(this.destroy$))
      .subscribe((isUnauthorized) => {
        this.isUnauthorized = isUnauthorized;
        if (isUnauthorized) {
          this.allPolicies = [];
          this.paginationState.filteredList = [];
          this.paginationState.pagedList = [];
        }
      });

    this.loadPolicies();
  }

  ngOnDestroy(): void {
    this.destroy$.next();
    this.destroy$.complete();
  }

  filterPolicies(mainList: PolicyDefinition[]): PolicyDefinition[] {
    return mainList.filter(policy =>
      (policy.id).toLowerCase().includes(this.searchText.toLowerCase()) ||
      policy.policy.assigner?.toLowerCase().includes(this.searchText.toLowerCase()) ||
      policy.policy.assignee?.toLowerCase().includes(this.searchText.toLowerCase())
    );
  }

  onSearch() {
    this.paginationState.pageIndex = 0;
    this.utilService.applyFilterAndPagination(
      [...this.allPolicies],
      this.filterPolicies.bind(this),
      this.searchText,
      this.paginationState
    );
  }

  onPageChange(event: PageEvent) {
    this.utilService.onPageChange(
      event, 
      [...this.allPolicies],
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
