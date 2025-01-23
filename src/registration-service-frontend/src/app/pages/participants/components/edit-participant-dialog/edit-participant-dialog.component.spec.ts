import { ComponentFixture, TestBed } from '@angular/core/testing';

import { EditParticipantDialogComponent } from './edit-participant-dialog.component';

describe('EditParticipantDialogComponent', () => {
  let component: EditParticipantDialogComponent;
  let fixture: ComponentFixture<EditParticipantDialogComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [EditParticipantDialogComponent]
    })
    .compileComponents();

    fixture = TestBed.createComponent(EditParticipantDialogComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
