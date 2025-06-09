import { Component, Inject } from '@angular/core';
import { MAT_DIALOG_DATA, MatDialogRef } from '@angular/material/dialog';
import { UtilService } from 'src/modules/edc-demo/services';

@Component({
  selector: 'jsonld-metadata-display',
  templateUrl: './metadata-display.component.html',
  styleUrls: ['./metadata-display.component.scss']
})
export class MetadataDisplayComponent {
  constructor(
    @Inject(MAT_DIALOG_DATA) public data: any,
    public readonly utilService: UtilService,
    public dialogRef: MatDialogRef<MetadataDisplayComponent>
  ) {}

  close(): void {
    this.dialogRef.close();
  }
}