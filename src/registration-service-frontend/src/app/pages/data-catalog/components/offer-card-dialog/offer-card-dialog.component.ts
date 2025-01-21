import { Component, Inject } from '@angular/core';
import { MAT_DIALOG_DATA, MatDialog, MatDialogRef } from '@angular/material/dialog';
import { CommonModule } from '@angular/common';
import { MatDialogModule } from '@angular/material/dialog';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { MatTooltipModule } from '@angular/material/tooltip';
import { CatalogOffer } from '../../../../core/api/models/catalog-offer';
import { AssetType } from '../../../../core/api/enums/asset-type.enum';
import { JsonLdDialogComponent } from '../json-ld-dialog/json-ld-dialog.component';

@Component({
  selector: 'app-offer-card-dialog',
  imports: [
    CommonModule,
    MatIconModule,
    MatTooltipModule,
    MatDialogModule,
    MatButtonModule,
  ],
  templateUrl: './offer-card-dialog.component.html',
  styleUrl: './offer-card-dialog.component.scss'
})
export class OfferCardDialogComponent {
  AssetType=AssetType;

  offer!: CatalogOffer;

  constructor(
    public dialogRef: MatDialogRef<OfferCardDialogComponent>,
    private dialog: MatDialog,
    @Inject(MAT_DIALOG_DATA) public data: any
  ) {
    this.offer = data;
  }

  close(): void {
    this.dialogRef.close();
  }

  openJsonLd(): void {
    this.dialog.open(JsonLdDialogComponent, {
      width: '600px',
      data: this.offer.policy,
    });
  }
}
