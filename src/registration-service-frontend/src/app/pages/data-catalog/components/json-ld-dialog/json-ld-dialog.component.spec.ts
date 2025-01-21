import { ComponentFixture, TestBed } from '@angular/core/testing';

import { JsonLdDialogComponent } from './json-ld-dialog.component';

describe('JsonLdDialogComponent', () => {
  let component: JsonLdDialogComponent;
  let fixture: ComponentFixture<JsonLdDialogComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [JsonLdDialogComponent]
    })
    .compileComponents();

    fixture = TestBed.createComponent(JsonLdDialogComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
