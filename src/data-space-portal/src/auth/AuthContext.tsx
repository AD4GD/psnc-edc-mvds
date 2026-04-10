import React, { createContext, useContext, useState, useEffect, useCallback, useRef } from "react";
import Keycloak from "keycloak-js";
import type { AppConfig } from "../config/AppConfig";

interface UserInfo {
  user_id: string;
  email: string;
  name: string;
  preferred_username: string;
  is_admin: boolean;
  roles: string[];
  participant_id: string | null;
  participant: Record<string, any> | null;
}

interface AuthState {
  keycloak: Keycloak | null;
  authenticated: boolean;
  token: string | null;
  user: UserInfo | null;
  loading: boolean;
  login: () => void;
  logout: () => void;
  refreshUser: () => Promise<void>;
}

const AuthContext = createContext<AuthState | null>(null);

export function AuthProvider({
  config,
  children,
}: {
  config: AppConfig;
  children: React.ReactNode;
}) {
  const [keycloak, setKeycloak] = useState<Keycloak | null>(null);
  const [authenticated, setAuthenticated] = useState(false);
  const [token, setToken] = useState<string | null>(null);
  const [user, setUser] = useState<UserInfo | null>(null);
  const [loading, setLoading] = useState(true);
  const initRef = useRef(false);

  const fetchUser = useCallback(
    async (accessToken: string) => {
      try {
        const res = await fetch(`${config.apiBaseUrl}/v1/auth/me`, {
          headers: { Authorization: `Bearer ${accessToken}` },
        });
        if (res.ok) {
          const data = await res.json();
          setUser(data);
        }
      } catch (err) {
        console.error("Failed to fetch user info:", err);
      }
    },
    [config.apiBaseUrl]
  );

  useEffect(() => {
    if (initRef.current) return;
    initRef.current = true;

    const kc = new Keycloak({
      url: config.keycloakUrl,
      realm: config.keycloakRealm,
      clientId: config.keycloakClientId,
    });

    kc.init({ onLoad: "check-sso", silentCheckSsoRedirectUri: undefined })
      .then(async (auth) => {
        setKeycloak(kc);
        setAuthenticated(auth);
        if (auth && kc.token) {
          setToken(kc.token);
          await fetchUser(kc.token);
        }
        setLoading(false);

        // Auto-refresh token
        setInterval(async () => {
          try {
            const refreshed = await kc.updateToken(30);
            if (refreshed && kc.token) {
              setToken(kc.token);
            }
          } catch {
            console.warn("Token refresh failed");
          }
        }, 30000);
      })
      .catch((err) => {
        console.error("Keycloak init failed:", err);
        setLoading(false);
      });
  }, [config, fetchUser]);

  const login = useCallback(() => {
    keycloak?.login();
  }, [keycloak]);

  const logout = useCallback(() => {
    keycloak?.logout({ redirectUri: window.location.origin });
  }, [keycloak]);

  const refreshUser = useCallback(async () => {
    if (token) {
      await fetchUser(token);
    }
  }, [token, fetchUser]);

  return React.createElement(
    AuthContext.Provider,
    {
      value: {
        keycloak,
        authenticated,
        token,
        user,
        loading,
        login,
        logout,
        refreshUser,
      },
    },
    children
  );
}

export function useAuth(): AuthState {
  const ctx = useContext(AuthContext);
  if (!ctx) {
    throw new Error("useAuth must be used within AuthProvider");
  }
  return ctx;
}
