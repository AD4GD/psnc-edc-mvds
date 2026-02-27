# idp-filler: Keycloak Configuration Service

## Overview

`idp-filler` to automatyczne narzędzie do konfiguracji Keycloak w ekosystemie Data Space. Zajmuje się:

- **Tworzeniem i konfiguracją realms** (DAPS, Organizations)
- **Rejestracją klientów OAuth2** (UI, Federated Catalog, Connectors)
- **Zarządzaniem użytkownikami i grupami** z odpowiednimi rolami
- **Integracją zewnętrznych IdP** (np. EGI Check-in)

### Kluczowe komponenty

Keycloak pełni różne role w zależności od instancji:

1. **Data Space Keycloak (port 8081)** — Trust Anchor
   - Hosts DAPS realm (minting signed tokens dla connectorów)
   - Hosts Organizations realm (logowanie użytkowników)
   - Zarządza wymianą tokenów między participantami
   - Hosts Federated Catalog

2. **Participant Keycloak (dla consumer/provider)** — Identity Provider
   - Provides user authentication via `data-space-users` client
   - Hosts Organizations realm (user details)
   - Acts as OIDC provider dla Data Space (federation)

## Użycie

### Local Development (Docker Compose)

```bash
cd bin
./devstack up -d
```

Kontenery `*-idp-filler` startują automatycznie i wykonują:
1. `configure_dataspace.py` — konfiguracja DS Keycloak
2. `configure_participant.py` — konfiguracja participant Keycloak

### Production / Manual Setup

W produkcji `idp-filler` powinna być wywoływana:
- Na starcie systemu (initial setup)
- Gdy rejestruje się nowy participant (add external IdP)
- Gdy dodaje się nowy connector (add client + roles)

Ustaw zmienne środowiskowe:

```bash
export KC_BASE=http://keycloak.example.com:8080
export KC_USER=admin
export KC_PASS=secure_password
export IDP_MODE=daps  # lub 'organization'
```

Następnie uruchom odpowiedni skrypt (patrz sekcja poniżej).

## Wymagania

### Python 3.11+

Biblioteki:
```bash
pip install python-keycloak requests
```

Lub z requirements.txt (jeśli istnieje):
```bash
pip install -r requirements.txt
```

W Docker kontenery mają już zainstalowane zależności w `Dockerfile`.

## Skrypty

### 1. `configure_dataspace.py`

**Cel:** Konfiguracja Data Space Keycloak (Trust Anchor)

**Co robi:**
- Tworzy/aktualizuje realm `DAPS` (Digital Authority Service)
  - Rejestruje DAPS clients dla connectorów (consumer, provider, federated-catalog)
  - Uploaduje JKS certyfikaty dla każdego connectora
- Tworzy/aktualizuje realm `Organizations`
  - Public client `data-space-users` dla logowania użytkowników
  - Konfiguruje Federated Catalog jako target audience
  - Tworzy administratora Registration Service (RS)
- Rejestruje participantów w Registration Service

**Zmienne:**
- `KC_BASE`: URL Data Space Keycloak (default: `http://localhost:8081`)
- `KC_USER`, `KC_PASS`: Admin credentials (default: `admin/edc`)
- `WEB_HTTP_RS_URI`: URL Registration Service (default: `http://localhost:38182`)
- `RS_USERNAME`, `RS_PASSWORD`: RS admin user (default: `rs-admin/edc`)

**Uruchomienie:**
```bash
python3 configure_dataspace.py
```

---

### 2. `configure_participant.py`

**Cel:** Konfiguracja Participant Keycloak (np. consumer/provider)

**Co robi:**
- Tworzy realm `Organizations`
- Rejestruje clients:
  - `data-space-users` — public SPA client dla user login (PKCE, offline_access)
  - `federated-catalog` — private client dla Federated Catalog access
- Tworzy role `access-catalog` w kontekście federated-catalog
- Tworzy grupę `federated-catalog` z przypisaną rolą
- Tworzy testowych użytkowników:
  - `test` — ma dostęp do katalogu
  - `test-no-fc` — bez dostępu do katalogu

**Zmienne:**
- `KC_BASE`: URL Participant Keycloak (default: `http://localhost:8082`)
- `KC_USER`, `KC_PASS`: Admin credentials (default: `admin/edc`)
- `USER_NAME`, `USER_PASS`: Test user (default: `test/edc`)
- `FC_GROUP`: Grupa dla Federated Catalog access (default: `federated-catalog`)
- `CATALOG_CLIENT_SECRET`: Secret dla federated-catalog client (default: `catalog-secret`)

**Uruchomienie:**
```bash
python3 configure_participant.py
```

---

### 3. `participant_ensure_connector.py`

**Cel:** Rejestracja nowego Connectora w Participant Keycloak

**Co robi:**
- Tworzy client dla connectora (np. `provider-connector`)
- Tworzy rolę dostępu (np. `access-connector`)
- Tworzy grupę z przypisaną rolą
- Tworzy testowego użytkownika dla connectora
- Aktualizuje mapper scopes w `data-space-users` aby umożliwić JWT z audience=connector

**Zmienne:**
- `KC_BASE`: URL Participant Keycloak (default: `http://localhost:8083`)
- `KC_USER`, `KC_PASS`: Admin credentials (default: `admin/edc`)
- `CONNECTOR_CLIENT_ID`: Connector client ID (default: `provider-connector`)
- `CONNECTOR_SECRET`: Client secret (default: `connector-secret`)
- `CONNECTOR_ROLE`: Role name (default: `access-connector`)

**Uruchomienie:**
```bash
python3 participant_ensure_connector.py
```

---

### 4. `configure_egi.py`

**Status:** W trakcie rozwoju

**Cel:** Integracja EGI Check-in jako zewnętrzny Identity Provider

**Co robi (planowane):**
- Konfiguruje external OIDC IdP w Data Space realm (`provider-idp`)
- Łączy się z EGI Check-in:
  - JWKS endpoint dla weryfikacji podpisów
  - Token endpoint dla token exchange
  - Userinfo endpoint dla atrybutów użytkownika
- Konfiguruje mappery:
  - Username mapper — unikalny identyfikator z EGI
  - Group mapper — przypisanie użytkownikowi grup na podstawie claim `resource_access.*.roles`
- Ustawia token-exchange permissions dla wymiany EGI token → Data Space token

**Zmienne (planowane):**
- `KC_BASE`: URL Data Space Keycloak
- `REALM_NAME`: Target realm (default: `Organizations`)
- `EXCHANGE_CLIENT_ID`: Client uprawniany do token exchange (default: `data-space-token-exchange`)

**Uruchomienie (kiedy gotowe):**
```bash
python3 configure_egi.py
```

---

## Utility: `keycloak_utils.py`

Wspólne funkcje dla wszystkich skryptów:

- `wait_for_keycloak()` — czeka na dostępność Keycloak
- `get_connection()` — nawiązuje połączenie OAuth2
- `get_admin()` — inicjalizuje KeycloakAdmin
- `get_access_token()` — pobiera token admin
- `ensure_realm()` — tworzy/aktualizuje realm
- `ensure_client()` — tworzy/aktualizuje client
- `ensure_client_role()` — tworzy rolę dla clienta
- `ensure_group()` — tworzy grupę z rolami
- `ensure_user()` — tworzy użytkownika z hasłem
- `ensure_idp_mapper()` — konfiguruje mapper dla external IdP
- `upload_certificate()` — uploaduje JKS certyfikat do Keycloak


## Troubleshooting

### "Keycloak did not start"
```bash
# Sprawdź czy kontener Keycloak jest uruchomiony
docker ps | grep keycloak

# Jeśli nie, uruchom
./devstack up -d
```

### "Client not found"
Upewnij się, że uruchomiłeś `configure_dataspace.py` lub `configure_participant.py` zgodnie z role Keycloak.

### "Token validation failed"
Sprawdź:
- JWKS URL jest dostępny
- Realm i client ID są poprawne
- User ma odpowiednie role/scopes

## Zasoby

- [Keycloak Docs](https://www.keycloak.org/documentation)
- [python-keycloak](https://python-keycloak.readthedocs.io/)
- Data Space Architecture (patrz `deployment/` folder)
