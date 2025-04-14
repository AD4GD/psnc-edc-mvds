import { Injectable } from "@angular/core";

@Injectable({
    providedIn: 'root'
})
export class SorterService {

    constructor() {
    }

    /**
     * Natural sorting function for strings concatenated with numbers.
     * Ensures that numeric parts are compared numerically.
     */
    public naturalSort(a: string, b: string): number {
        const regex = /(\d+)|(\D+)/g;
    
        const aParts = a.match(regex) || [];
        const bParts = b.match(regex) || [];
    
        for (let i = 0; i < Math.max(aParts.length, bParts.length); i++) {
            const aPart = aParts[i] || '';
            const bPart = bParts[i] || '';
        
            // Compare numeric parts numerically
            const aNum = parseInt(aPart, 10);
            const bNum = parseInt(bPart, 10);
        
            if (!isNaN(aNum) && !isNaN(bNum)) {
                if (aNum !== bNum) {
                return aNum - bNum;
                }
            } else {
                // Compare non-numeric parts lexicographically
                if (aPart !== bPart) {
                return aPart.localeCompare(bPart);
                }
            }
        }
    
        return 0; // Equal
    }
}
