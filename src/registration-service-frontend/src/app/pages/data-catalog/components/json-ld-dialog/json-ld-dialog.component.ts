import { Component, Inject } from '@angular/core';
import { MAT_DIALOG_DATA, MatDialogRef } from '@angular/material/dialog';
import { MatDialogModule } from '@angular/material/dialog';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'app-json-ld-dialog',
  imports: [
    MatDialogModule,
    CommonModule,
  ],
  templateUrl: './json-ld-dialog.component.html',
  styleUrl: './json-ld-dialog.component.scss'
})
export class JsonLdDialogComponent {

  jsonLd: any;

  constructor(
    public dialogRef: MatDialogRef<JsonLdDialogComponent>,
    @Inject(MAT_DIALOG_DATA) public data: any
  ) {
    this.jsonLd = data;
  }
}
