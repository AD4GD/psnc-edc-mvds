import { Component, Inject } from '@angular/core';
import { MAT_DIALOG_DATA, MatDialogRef } from '@angular/material/dialog';
import { MatSnackBar } from '@angular/material/snack-bar';
import { RegistrationServiceClient } from '../../../../core/api/services/impl/registration-service-client';
import { FormControl } from '@angular/forms';

@Component({
  selector: 'app-add-participant-dialog',
  templateUrl: './add-participant-dialog.component.html',
  styleUrl: './add-participant-dialog.component.scss',
  standalone: false,
})
export class AddParticipantDialogComponent {

  didControl: FormControl = new FormControl("");
  protocolUrlControl: FormControl = new FormControl("");

  constructor(
        public dialogRef: MatDialogRef<AddParticipantDialogComponent>,
        @Inject(MAT_DIALOG_DATA) public data: any,
        private snackBar: MatSnackBar,
        private client: RegistrationServiceClient,
      ) {

  }

  close(): void {
    this.dialogRef.close();
  }

  confirm(): void {
    if (this.didControl.value == "" || this.protocolUrlControl.value == "") {
      this.showToast('Status: Add a participant failed!', 'error');
      return;
    }
    this.client.backend.addParticipant(this.didControl.value, this.protocolUrlControl.value).subscribe((x) => {
      console.log(x);
      if (x.ok) {
        this.showToast('Status: Add a participant is successful!', 'success');
      } else {
        this.showToast('Status: Add a participant failed!', 'error');
      }
    });
    this.close();
  }

  private showToast(message: string, type: 'success' | 'error' | 'info'): void {
    const config = {
      duration: 3000,
      panelClass: ['snack-bar-' + type],
    };
    this.snackBar.open(message, 'Close', config);
  }
}
