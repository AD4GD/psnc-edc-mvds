import { Component, Inject, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { MatIconModule } from '@angular/material/icon';
import { ReactiveFormsModule } from '@angular/forms';
import { MatButtonModule } from '@angular/material/button';
import { MatPaginatorModule } from '@angular/material/paginator';
import { MatSelectChange, MatSelectModule } from '@angular/material/select';
import { MatTooltipModule } from '@angular/material/tooltip';
import { FormControl } from '@angular/forms';
import { PageEvent } from '@angular/material/paginator';
import { RegistrationServiceClient } from '../../core/api/services/impl/registration-service-client';
import { CatalogOffer } from '../../core/api/models/catalog-offer';
import { debounceTime, map, Observable } from 'rxjs';
import { MatDialog } from '@angular/material/dialog';
import { OfferCardDialogComponent } from './components/offer-card-dialog/offer-card-dialog.component';

@Component({
  selector: 'app-data-catalog',
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
  ],
  templateUrl: './data-catalog.component.html',
  styleUrl: './data-catalog.component.scss'
})
export class DataCatalogComponent implements OnInit {
  searchControl = new FormControl('');

  sortControl = new FormControl('title-asc');
  sortOptions = [
    { label: 'Name (A-Z)', value: 'title-asc' },
    { label: 'Name (Z-A)', value: 'title-desc' },
    { label: 'Date (Newest)', value: 'lastUpdated-desc' },
    { label: 'Date (Oldest)', value: 'lastUpdated-asc' },
  ];

  pageSize = 6;
  pageIndex = 0;
  length = 0;
  pageSizeOptions: number[] = [6, 12, 18];

  isGridView = true;

  offers: CatalogOffer[] = [];


  constructor(private dialog: MatDialog,
    private client: RegistrationServiceClient) {
  }

  ngOnInit(): void {
    this.updateCurrentOffers();
    this.updateTotalPages();

    this.searchControl.valueChanges
      .pipe(
        debounceTime(300),
        map(value => value?.toLowerCase())
      )
      .subscribe(searchTerm => {
        if (searchTerm === undefined) {
          return;
        }
        this.updateCurrentOffers();
        this.updateTotalPages();
      });
  }

  onPageChange(event: PageEvent): void {
    this.pageIndex = event.pageIndex;
    this.pageSize = event.pageSize;
    this.updateCurrentOffers();
  }

  onSortChange(event: MatSelectChange): void {
    const [prop, direction] = event.value.split('-');
    this.updateCurrentOffers();
  }

  openDetails(item: any): void {
    this.dialog.open(OfferCardDialogComponent, {
      width: '1100px',
      maxWidth: 'none',
      data: item, // Pass the selected item as data to the dialog
    });
  }

  getOffersForCurrentPage(): Observable<CatalogOffer[]> {
    const offset = this.pageIndex * this.pageSize;
    return this.client.catalog.getOffers(
      this.pageSize, offset, this.searchControl.value?.toLowerCase()!);
  }

  updateCurrentOffers(): void {
    this.getOffersForCurrentPage().subscribe((data) => {
      this.offers = data;
      console.log(data);
    });
  }

  updateTotalPages(): void {
    this.client.catalog.getLength(
        this.searchControl.value?.toLowerCase()!).subscribe((length) => {
      this.length = length;
      console.log(length);
    });
  }
}
