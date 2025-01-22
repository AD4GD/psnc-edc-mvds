import { Component, Inject } from '@angular/core';
import { MAT_DIALOG_DATA, MatDialogRef } from '@angular/material/dialog';
import { Participant } from '../../../../core/api/models/participant';
import { CommonModule } from '@angular/common';
import { MatDialogModule } from '@angular/material/dialog';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { MatTooltipModule } from '@angular/material/tooltip';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { MatOptionModule } from '@angular/material/core';
import { ReactiveFormsModule } from '@angular/forms';
import { FormsModule } from '@angular/forms';
import { MatChipsModule } from '@angular/material/chips';
import { NgModule } from '@angular/core';
import { MatSelectChange, MatSelectModule } from '@angular/material/select';
import { MatSnackBar, MatSnackBarModule } from '@angular/material/snack-bar';
import { FormControl } from '@angular/forms';
import { ParticipantStatusType } from '../../../../core/api/enums/participant-status-type.enum';
import { RegistrationServiceClient } from '../../../../core/api/services/impl/registration-service-client';

@Component({
  selector: 'app-edit-participant-dialog',
  imports: [
    CommonModule,
    MatIconModule,
    MatTooltipModule,
    MatDialogModule,
    MatButtonModule,
    MatFormFieldModule,
    ReactiveFormsModule,
    FormsModule,
    MatSelectModule,
    MatInputModule,
    MatOptionModule,
    MatChipsModule,
    MatSnackBarModule,
  ],
  templateUrl: './edit-participant-dialog.component.html',
  styleUrl: './edit-participant-dialog.component.scss'
})
export class EditParticipantDialogComponent {

  didControl: FormControl;
  protocolControl: FormControl;
  statusControl: FormControl;
  statusTypes = Object.values(ParticipantStatusType)
    .filter(key => isNaN(Number(key)))
    .map(x => ({ label: x, value: x}));

  participant: Participant;
  claimsValueArray: { key: string; value: string, isValid: boolean }[] = [];

  constructor(
      public dialogRef: MatDialogRef<EditParticipantDialogComponent>,
      @Inject(MAT_DIALOG_DATA) public data: any,
      private snackBar: MatSnackBar,
      private client: RegistrationServiceClient,
    ) {
      this.participant = data;
      this.didControl = new FormControl(data.did);
      this.protocolControl = new FormControl(data.protocolUrl);
      this.statusControl = new FormControl(data.status);
      this.syncFromMap();
      this.didControl.disable();
      this.protocolControl.disable();
  }

  close(): void {
    this.dialogRef.close();
  }

  areMapsEqual(map1: Map<string, string>, map2: Map<string, string>): boolean {
    if (map1.size !== map2.size) {
        return false;
    }

    for (const [key, value] of map1) {
        if (map2.get(key) !== value || !map2.has(key)) {
            return false;
        }
    }

    return true;
}

  private showToast(message: string, type: 'success' | 'error' | 'info'): void {
    const config = {
      duration: 3000,
      panelClass: ['snack-bar-' + type],
    };
    this.snackBar.open(message, 'Close', config);
  }

  apply(): void {
    if (this.statusControl.value != this.participant.status) {
      this.client.backend.updateParticipantStatus(this.participant.did, this.statusControl.value).subscribe((x) => {
        console.log(x);
        if (x.ok) {
          this.showToast('Status: Update successful!', 'success');
        } else {
          this.showToast('Status: Update failed.', 'error');
        }
      });
    }
    if (!this.areMapsEqual(this.participant.claims ?? new Map<string, string>(), this.getMapFromArray())) {
      console.log(this.getMapFromArray());
      this.client.backend.updateParticipantClaims(this.participant.did, this.getMapFromArray()).subscribe((x) => {
        if (x.ok) {
          this.showToast('Claims: Update successful!', 'success');
        } else {
          this.showToast('Claims: Update failed.', 'error');
        }
      });
    }
    this.close();
  }

  syncFromMap(): void {
    this.claimsValueArray = Array.from(this.participant.claims ?? [], ([key, value]) => ({ key, value, isValid: true }));
  }

  getMapFromArray(): Map<string, string> {
    return new Map(this.claimsValueArray.map(({ key, value }) => [key, value]));
  }

  validateFields(): void {
    const keysSet = new Set<string>();
    this.claimsValueArray.forEach(item => {
      const isKeyValueValid = item.key.trim() !== '' && item.value.trim() !== '';
      const isKeyUnique = !keysSet.has(item.key.trim());
      if (isKeyValueValid) {
        keysSet.add(item.key.trim());
      }

      item.isValid = isKeyValueValid && isKeyUnique;
    });
  }

  addItem(): void {
    this.claimsValueArray.push({ key: '', value: '', isValid: false });
  }

  removeItem(index: number): void {
    this.claimsValueArray.splice(index, 1);
  }
}
