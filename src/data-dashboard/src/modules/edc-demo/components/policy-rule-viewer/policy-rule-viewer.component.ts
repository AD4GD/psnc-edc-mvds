import {Component, Input, OnInit} from '@angular/core';
import { MatDialog } from '@angular/material/dialog';
import { JsonLdObject } from '@think-it-labs/edc-connector-client';
import { PolicyRuleModalComponent } from '../policy-rule-modal/policy-rule-modal.component';
import { PolicyRule } from '../../models/policy-rule';
import { OBLIGATION_RULE, PERMISSION_RULE, PROHIBITION_RULE } from 'src/modules/app/policy-rule-types';

@Component({
  selector: 'policy-rules',
  templateUrl: './policy-rule-viewer.component.html',
  styleUrls: ['./policy-rule-viewer.component.scss']
})
export class PolicyRuleViewerComponent implements OnInit {

  @Input() permissionRules: any[] | undefined = [];
  @Input() prohibitionRules: any[] | undefined = [];
  @Input() obligationRules: any[] | undefined = [];

  rules: PolicyRule[] = [];


  constructor(public dialog: MatDialog) {
  }

  ngOnInit(): void {
    this.rules = this.getTransformedRules();
    console.log(this.rules);
  }

  private getTransformedRules(): PolicyRule[] {
    const rawRulesArray: any[] = [];
    this.addIfExists(rawRulesArray, this.permissionRules, PERMISSION_RULE.id);
    this.addIfExists(rawRulesArray, this.prohibitionRules, PROHIBITION_RULE.id);
    this.addIfExists(rawRulesArray, this.obligationRules, OBLIGATION_RULE.id);

    return rawRulesArray.flatMap((x: any) => 
      x.array.map((rawRule: any) => this.getTransformedRule(rawRule, x.type)));
  }

  private addIfExists(rawRulesArray: any[], arrayToAdd: JsonLdObject[] | undefined, type: string) {
    if (arrayToAdd === undefined) {
      return;
    }

    rawRulesArray.push({ type: type, array: arrayToAdd });
  }

  private getTransformedRule(rawRule: JsonLdObject, type: string): PolicyRule {
    const content = rawRule;
    return {
      type: type,
      content: content,
    }
  }

  getTypeColor(type: string) {
    return "warn";
  }

  openDialog(content: JsonLdObject): void {
    const dialogRef = this.dialog.open(PolicyRuleModalComponent, {
      width: 'fit-content',
      data: { content: content }
    });

    dialogRef.afterClosed().subscribe(result => {
      console.log('The dialog was closed');
    });
  }
}
