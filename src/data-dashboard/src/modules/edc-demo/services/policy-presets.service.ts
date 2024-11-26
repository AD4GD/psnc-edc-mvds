import { Inject, Injectable } from "@angular/core";
import { LOCATION_PRESET, PURPOSE_PRESET, TIME_INTERVAL_PRESET } from "src/modules/app/policy-presets";
import { DateTimeService } from "./common/date-time.service";

@Injectable({
  providedIn: 'root'
})
export class PolicyPresetsService {

  constructor(private dateTimeService: DateTimeService) {
  }

  public fillOdrlTemplate(inputData: any) {
    if (inputData == null) {
      return;
    }

    const fillData = this.getOdrlFillData(inputData);
    const templateJsonString = JSON.stringify(inputData.odrlJson);
    const filledJsonString = templateJsonString.replace(/{{(\w+)}}/g, (match, key) => {
      return fillData[key] || match;
    });
    console.log(filledJsonString);
    inputData.odrlJson = JSON.parse(filledJsonString);
  }

  private getOdrlFillData(inputData: any): any {
    if (inputData == null) {
      return;
    }

    if (inputData.presetTypeId == TIME_INTERVAL_PRESET.id) {
      return {
        timeFrom: this.dateTimeService.getDateUtcFormatString(inputData.fromDateString), 
        timeTo: this.dateTimeService.getDateUtcFormatString(inputData.toDateString),
      };
    }
    else if (inputData.presetTypeId == LOCATION_PRESET.id) {
      return {
        location: inputData.allowedLocation,
      };
    }
    else if (inputData.presetTypeId == PURPOSE_PRESET.id) {
      return {
        purpose: inputData.allowedPurpose,
      };
    }

    return {};
  }
}
