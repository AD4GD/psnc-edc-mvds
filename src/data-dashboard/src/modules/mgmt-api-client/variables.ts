import { InjectionToken } from '@angular/core';

export const BASE_PATH = new InjectionToken<string>('basePath');
export const COLLECTION_FORMATS = {
    'csv': ',',
    'tsv': '   ',
    'ssv': ' ',
    'pipes': '|'
}

export const MIME_TO_EXTENSION: Record<string, string> = {
    'application/json': '.json',
    'text/plain': '.txt',
    'text/csv': '.csv',
    'application/pdf': '.pdf',
    'image/png': '.png',
    'image/jpeg': '.jpg',
    'application/octet-stream': '.bin',
    // Add more mappings as needed
};

export const getMediaTypes = (): string[] => {
    // Return an array of all MIME types (keys from the object)
    return Object.keys(MIME_TO_EXTENSION);
};