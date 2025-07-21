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

    searchThroughMetadata(metadata: Record<string, any>, searchText: string) {
        const lowerSearch = searchText.toLowerCase();

        function search(obj: any): boolean {
            if (obj == null) return false;
            if (typeof obj === 'string') {
                return obj.toLowerCase().includes(lowerSearch);
            }
            if (typeof obj === 'number' || typeof obj === 'boolean') {
                return obj.toString().toLowerCase().includes(lowerSearch);
            }
            if (Array.isArray(obj)) {
                return obj.some(item => search(item));
            }
            if (typeof obj === 'object') {
                // Przeszukaj klucze
                for (const key of Object.keys(obj)) {
                    if (key.toLowerCase().includes(lowerSearch)) return true;
                    if (search(obj[key])) return true;
                }
            }
            return false;
        }

        return search(metadata);
    }
}
