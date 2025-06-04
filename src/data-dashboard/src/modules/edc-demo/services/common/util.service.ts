import { Injectable } from "@angular/core";

@Injectable({
    providedIn: 'root'
})
export class UtilService {
    constructor() { }

    shouldShowTooltip(element: HTMLElement, value: string | undefined): boolean {
        if (!element || !value) return false;
        return element.offsetWidth < element.scrollWidth;
    }
}
