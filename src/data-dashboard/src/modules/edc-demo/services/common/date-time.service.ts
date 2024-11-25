import { Injectable } from "@angular/core";

@Injectable({
  providedIn: 'root'
})
export class DateTimeService {

  constructor() {
  }

  public getCurrentLocalTimeString() {
    let currentDate = new Date();

    let year = currentDate.getFullYear();
    let month = String(currentDate.getMonth() + 1).padStart(2, '0');
    let day = String(currentDate.getDate()).padStart(2, '0');
    let hours = String(currentDate.getHours()).padStart(2, '0');
    let minutes = String(currentDate.getMinutes()).padStart(2, '0');
    let seconds = String(currentDate.getSeconds()).padStart(2, '0');

    return `${year}-${month}-${day}T${hours}:${minutes}:${seconds}`;
  }

  public getDateUtcFormatString(localDateString: any) {
    const userLocalDate = new Date(localDateString);
    const utcDate = new Date(userLocalDate.toISOString());
    const utcString = utcDate.toISOString();
    return utcString;
  }
}
