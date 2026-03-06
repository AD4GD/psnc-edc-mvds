import type { AppConfig } from "./AppConfig";

export async function loadConfig(): Promise<AppConfig> {
  const response = await fetch("/app.config.json", {
    cache: "no-store"
  });

  if (!response.ok) {
    throw new Error("Failed to load app.config.json");
  }

  return response.json();
}
