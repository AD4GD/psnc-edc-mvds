import { Component, Inject, OnInit, ViewChild } from '@angular/core';
import { CommonModule } from '@angular/common';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { MatIconModule } from '@angular/material/icon';
import { ReactiveFormsModule } from '@angular/forms';
import { MatButtonModule } from '@angular/material/button';
import { MatPaginator, MatPaginatorModule } from '@angular/material/paginator';
import { MatSort, MatSortModule } from '@angular/material/sort';
import { MatTableDataSource, MatTableModule } from '@angular/material/table';
import { MatSelectChange, MatSelectModule } from '@angular/material/select';
import { MatTooltipModule } from '@angular/material/tooltip';
import { RegistrationServiceClient } from '../../core/api/services/impl/registration-service-client';
import { Participant } from '../../core/api/models/participant';
import { MatDialog } from '@angular/material/dialog';
import { EditParticipantDialogComponent } from './components/edit-participant-dialog/edit-participant-dialog.component';
import { AddParticipantDialogComponent } from './components/add-participant-dialog/add-participant-dialog.component';
import { DialogService } from '../../core/services/dialog.service';

@Component({
  selector: 'app-participants',
  imports: [
      CommonModule,
      MatFormFieldModule,
      MatInputModule,
      MatIconModule,
      ReactiveFormsModule,
      MatButtonModule,
      MatPaginatorModule,
      MatSelectModule,
      MatTooltipModule,
      MatTableModule,
      MatSortModule,
    ],
  templateUrl: './participants.component.html',
  styleUrl: './participants.component.scss'
})
export class ParticipantsComponent implements OnInit {

  displayedColumns: string[] = ['did', 'protocolUrl', 'status', 'claims', 'action'];
  dataSource = new MatTableDataSource<Participant>([]);

  @ViewChild(MatPaginator) paginator!: MatPaginator;
  @ViewChild(MatSort) sort!: MatSort;

  constructor(
    private dialog: MatDialog,
    private client: RegistrationServiceClient,
    private dialogService: DialogService
  ) {
  }

  refreshParticipants(): void {
    this.client.backend.getParticipants().subscribe((data) => {
      data.forEach(x => x.claims = new Map(Object.entries(x.claims ?? [])));
      this.dataSource.data = data;
    });
  }

  ngOnInit(): void {
    this.refreshParticipants();
    this.dataSource.paginator = this.paginator;
    this.dataSource.sort = this.sort;
  }

  getClaimsArray(participant: Participant): { key: string; value: string }[] {
    if (!participant.claims) {
      return [];
    }
    var array = Array.from(participant.claims, ([key, value]) => ({ key, value }));
    console.log(array);
    return array;
  }

  applyFilter(event: Event) {
    const filterValue = (event.target as HTMLInputElement).value;
    this.dataSource.filter = filterValue.trim().toLowerCase();

    if (this.dataSource.paginator) {
      this.dataSource.paginator.firstPage();
    }
  }

  openAddDialog(): void {
    this.dialog.open(AddParticipantDialogComponent, {
      width: '600px',
      maxWidth: 'none',
    }).afterClosed().subscribe(x => {
      this.refreshParticipants();
    });
  }

  openEditDialog(item: any): void {
    this.dialog.open(EditParticipantDialogComponent, {
      width: '900px',
      maxWidth: 'none',
      data: item,
    }).afterClosed().subscribe(x => {
      this.refreshParticipants();
    });
  }

  openDeleteParticipantDialog(participant: Participant): void {
    this.dialogService.confirm('Are you sure you want to delete this item?').then((confirmed) => {
      if (confirmed) {
        console.log('Item deleted');
        this.client.backend.deleteParticipant(participant.did).subscribe(x => {
          this.refreshParticipants();
        });
      }
    });
  }
}
