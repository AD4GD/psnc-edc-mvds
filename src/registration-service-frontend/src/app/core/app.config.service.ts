import { Injectable } from '@angular/core';
import { appConfig, AppConfig } from '../app.config';

@Injectable({
  providedIn: 'root',
})
export class ConfigService {
  private config!: AppConfig;

  constructor() {
  }

  loadConfig(): Promise<void> {
    return fetch('/assets/config/app.config.json')
      .then((response) => {
        if (!response.ok) {
          throw new Error(`Failed to load config.json: ${response.statusText}`);
        }
        return response.json();
      })
      .then((config) => {
        console.log(config);
        this.config = config;
        console.log(this.config);
      })
      .catch((error) => {
        console.error('Error loading configuration:', error);
      });
  }

  getConfig(): AppConfig {
    console.log(this.config);
    return this.config;
  }
}
