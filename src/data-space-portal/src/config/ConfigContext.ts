import React, { createContext, useContext } from "react";
import type { AppConfig } from "./AppConfig";

const ConfigContext = createContext<AppConfig | null>(null);

export function ConfigProvider({
  config,
  children,
}: {
  config: AppConfig;
  children: React.ReactNode;
}) {
  return React.createElement(ConfigContext.Provider, { value: config }, children);
}

export function useConfig(): AppConfig {
  const cfg = useContext(ConfigContext);
  if (!cfg) {
    throw new Error("useConfig must be used within ConfigProvider");
  }
  return cfg;
}
