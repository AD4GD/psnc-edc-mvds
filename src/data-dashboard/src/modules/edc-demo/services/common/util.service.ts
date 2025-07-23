import { Injectable } from "@angular/core";
import { PageEvent } from "@angular/material/paginator";

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
                // search keys and values
                for (const key of Object.keys(obj)) {
                    if (key.toLowerCase().includes(lowerSearch)) return true;
                    if (search(obj[key])) return true;
                }
            }
            return false;
        }

        return search(metadata);
    }

    onPageChange(
        event: PageEvent, 
        mainList: any[],
        filterFunction: Function, 
        searchText: string = '', 
        out: { filteredList: any[], pagedList: any[], pageIndex: number, pageSize: number }
    ) {
        if (event.pageSize !== out.pageSize) {
            const firstItemIndex = out.pageIndex * out.pageSize;
            out.pageIndex = Math.floor(firstItemIndex / event.pageSize);
            out.pageSize = event.pageSize;
        } else {
            out.pageIndex = event.pageIndex;
            out.pageSize = event.pageSize;
        }
        this.applyFilterAndPagination(
            mainList,
            filterFunction,
            searchText,
            out
        );
    }

    applyFilterAndPagination(
        mainList: any[], 
        filterFunction: Function, 
        searchText: string = '', 
        out: { filteredList: any[], pagedList: any[], pageIndex: number, pageSize: number }
    ) {
        // Filtering
        let filteredList = [];
        if (searchText !== '') {
            filteredList = filterFunction([...mainList]);
        } else {
            filteredList = [...mainList];
        }
        // Reset pageIndex if out of bands
        if (out.pageIndex * out.pageSize >= filteredList.length && filteredList.length > 0) {
            out.pageIndex = 0;
        }
        // Pagination
        const start = out.pageIndex * out.pageSize;
        const end = start + out.pageSize;
        const pagedList = filteredList.slice(start, end);
        // Update values through reference
        out.filteredList = [...filteredList];
        out.pagedList = [...pagedList];
    }
}
