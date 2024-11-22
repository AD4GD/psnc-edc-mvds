import {Component, Inject, OnInit} from '@angular/core';
import { PolicyDefinitionInput } from "../../../mgmt-api-client/model";
import { MatDialogRef } from "@angular/material/dialog";
import { JsonLdObject, Policy } from '@think-it-labs/edc-connector-client';
import { PolicyPresetType } from '../../models/policy-preset-type';
import { CUSTOM_PRESET, LOCATION_PRESET, PURPOSE_PRESET, TIME_INTERVAL_PRESET } from 'src/modules/app/policy-presets';
import { OBLIGATION_RULE, PERMISSION_RULE, PROHIBITION_RULE } from 'src/modules/app/policy-rule-types';
import { PolicyPresetsService } from '../../services/policy-presets.service';
import { DateTimeService } from '../../services/common/policy-presets.service';

interface RuleItem {
  presetTypeId: string,
  policyRuleTypeId: string,
  odrlJson: JsonLdObject,
  allowedLocation: string,
  allowedPurpose: string,
  fromDateString: string,
  toDateString: string,
}

interface RuleListItem extends RuleItem {
  isShowOdrl: boolean
}

@Component({
  selector: 'app-new-policy-dialog',
  templateUrl: './new-policy-dialog.component.html',
  styleUrls: ['./new-policy-dialog.component.scss']
})
export class NewPolicyDialogComponent implements OnInit {
  editMode: boolean = false;

  policy: Policy = new Policy();
  policyDefinition: PolicyDefinitionInput = {
    "policy": this.policy,
    "@id": ''
  };

  addedRulesList: RuleListItem[] = [];
  
  availablePresetTypes: PolicyPresetType[] = [];
  currentRuleItem: RuleItem | null = null;

  constructor(
    @Inject("POLICY_PRESETS") private policyPresetTypes: PolicyPresetType[],
    @Inject("POLICY_RULE_TYPES") public policyRuleTypes: any[],
    private dialogRef: MatDialogRef<NewPolicyDialogComponent>,
    private policyPresetsService: PolicyPresetsService,
    private dateTimeService: DateTimeService) {
  }

  ngOnInit(): void {
    this.editMode = true;
    this.availablePresetTypes = [...this.policyPresetTypes];
    this.currentRuleItem = null;
  }

  createItem() {
    this.currentRuleItem = {
      presetTypeId: this.availablePresetTypes[0].id,
      policyRuleTypeId: this.policyRuleTypes[0].id,
      odrlJson: JSON.parse(this.availablePresetTypes[0].odrlJsonString),
      allowedLocation: '',
      allowedPurpose: '',
      fromDateString: '',
      toDateString: '',
    };

    console.log(this.currentRuleItem);
  }

  onPolicyRuleTypeIdChange(newType: string) {
    if (this.currentRuleItem == null) {
      return;
    }

    if (newType == PERMISSION_RULE.id) {
      this.availablePresetTypes = [...this.policyPresetTypes];
    }
    else {
      this.availablePresetTypes = [CUSTOM_PRESET];
    }
    this.createItem();
    this.currentRuleItem.policyRuleTypeId = newType;
  }

  addItem() {
    if (this.currentRuleItem == null) {
      return;
    }

    console.log(this.currentRuleItem);
    if (this.currentRuleItem.presetTypeId != CUSTOM_PRESET.id) {
      this.policyPresetsService.fillOdrlTemplate(this.currentRuleItem);
    }
    this.addedRulesList.push({ ...this.currentRuleItem, isShowOdrl: false });
    this.resetCurrentItem();
  }

  cancelItem() {
    this.resetCurrentItem();
  }

  removeItem(index: number) {
    this.addedRulesList.splice(index, 1);
  }

  onJsonLdUpdated(updatedJson: any) {
    if (this.currentRuleItem == null) {
      return;
    }
    this.currentRuleItem.odrlJson = updatedJson;
  }

  toggleIsShowOdrl(ruleListItem: any) {
    ruleListItem.isShowOdrl = !ruleListItem.isShowOdrl;
  }

  setNowFromDate() {
    if (this.currentRuleItem == null) {
      return;
    }
    this.currentRuleItem.fromDateString = this.dateTimeService.getCurrentLocalTimeString();
  }

  setNowToDate() {
    if (this.currentRuleItem == null) {
      return;
    }
    this.currentRuleItem.toDateString = this.dateTimeService.getCurrentLocalTimeString();
  }

  onPresetTypeChange(newType: string) {
    if (this.currentRuleItem == null) {
      return;
    }

    if (newType == CUSTOM_PRESET.id) {
      this.currentRuleItem.odrlJson = JSON.parse(CUSTOM_PRESET.odrlJsonString);
    }
    else {
      this.currentRuleItem.odrlJson = this.findFirstOdrlAndGetJson(newType);
    }
  }

  resetCurrentItem() {
    if (this.currentRuleItem == null) {
      return;
    }

    this.currentRuleItem = null;
    this.availablePresetTypes = [...this.policyPresetTypes];
  }

  onSave() {
    const rulesDictionary: any = {};
    rulesDictionary[PERMISSION_RULE.id] = [];
    rulesDictionary[PROHIBITION_RULE.id] = [];
    rulesDictionary[OBLIGATION_RULE.id] = [];

    this.addedRulesList.forEach(rule => {
      const rulesList = rulesDictionary[rule.policyRuleTypeId];
      rulesList.push(rule.odrlJson);
    });

    this.policy.permission = rulesDictionary[PERMISSION_RULE.id];
    this.policy.prohibition = rulesDictionary[PROHIBITION_RULE.id];
    this.policy.obligation = rulesDictionary[OBLIGATION_RULE.id];

    this.policy["@type"]="Set";
    this.policy["@context"]="http://www.w3.org/ns/odrl.jsonld";

    this.dialogRef.close({
      policy : this.policyDefinition.policy,
      '@id': this.policyDefinition.id
    })
  }

  private findFirstOdrlAndGetJson(id: string) {
    return JSON.parse(this.policyPresetTypes.find(x => x.id == id)!.odrlJsonString);
  }
}
