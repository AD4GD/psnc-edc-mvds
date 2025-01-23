import { ComponentFixture, TestBed } from '@angular/core/testing';

import { MvdSidebarComponent } from './mvd-sidebar.component';

describe('MvdSidebarComponent', () => {
  let component: MvdSidebarComponent;
  let fixture: ComponentFixture<MvdSidebarComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [MvdSidebarComponent]
    })
    .compileComponents();

    fixture = TestBed.createComponent(MvdSidebarComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
