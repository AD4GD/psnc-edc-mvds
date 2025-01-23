import { ComponentFixture, TestBed } from '@angular/core/testing';

import { AddParticipantDialogComponent } from './add-participant-dialog.component';

describe('AddParticipantDialogComponent', () => {
  let component: AddParticipantDialogComponent;
  let fixture: ComponentFixture<AddParticipantDialogComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [AddParticipantDialogComponent]
    })
    .compileComponents();

    fixture = TestBed.createComponent(AddParticipantDialogComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
