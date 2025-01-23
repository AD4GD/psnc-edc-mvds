import { ComponentFixture, TestBed } from '@angular/core/testing';

import { OfferCardDialogComponent } from './offer-card-dialog.component';

describe('OfferCardModalComponent', () => {
  let component: OfferCardDialogComponent;
  let fixture: ComponentFixture<OfferCardDialogComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [OfferCardDialogComponent]
    })
    .compileComponents();

    fixture = TestBed.createComponent(OfferCardDialogComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
