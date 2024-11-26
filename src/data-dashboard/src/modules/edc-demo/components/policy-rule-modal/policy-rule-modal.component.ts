import {Component, Inject, Input, OnInit} from '@angular/core';
import { JsonLdObject } from '@think-it-labs/edc-connector-client';
import { MatDialogRef, MAT_DIALOG_DATA } from '@angular/material/dialog';
import { MatSnackBar } from '@angular/material/snack-bar';

@Component({
  selector: 'policy-rule-modal',
  templateUrl: './policy-rule-modal.component.html',
  styleUrls: ['./policy-rule-modal.component.scss']
})
export class PolicyRuleModalComponent {

  @Input() content: JsonLdObject | undefined;


  constructor(
    public dialogRef: MatDialogRef<PolicyRuleModalComponent>,
    private snackBar: MatSnackBar,
    @Inject(MAT_DIALOG_DATA) public data: any
  ) {
    this.content = data.content;
  }

  public close(): void {
    this.dialogRef.close();
  }

  public copyToClipboard(): void {
    const jsonString = JSON.stringify(this.content, null, 2);
    navigator.clipboard.writeText(jsonString).then(() => {
      // Show success message when content is copied
      this.snackBar.open('Copied to clipboard!', '', {
        duration: 2000,
      });
    }).catch((err) => {
      console.error('Failed to copy: ', err);
    });
  }
}
