# Używanie dokumentacji OpenAPI

Rozszerzenie iShare Participant Registry zawiera pełną dokumentację OpenAPI 3.0, która opisuje wszystkie dostępne endpointy REST API.

## Plik specyfikacji

Plik `openapi.yaml` zawiera kompletną specyfikację API zgodną z OpenAPI 3.0.

## Import do Postman

1. Otwórz Postman
2. Kliknij **Import**
3. Wybierz plik `openapi.yaml`
4. Postman automatycznie utworzy kolekcję z wszystkimi endpointami

## Import do Insomnia

1. Otwórz Insomnia
2. Kliknij **Create** > **Import From** > **File**
3. Wybierz plik `openapi.yaml`
4. Insomnia zaimportuje wszystkie endpointy

## Przeglądanie w Swagger UI

### Opcja 1: Online Swagger Editor

1. Otwórz https://editor.swagger.io/
2. Skopiuj zawartość `openapi.yaml`
3. Wklej do edytora
4. Po prawej stronie zobaczysz renderowaną dokumentację

### Opcja 2: Lokalny Swagger UI

```bash
# Użyj Docker
docker run -p 8080:8080 -e SWAGGER_JSON=/openapi.yaml \
  -v $(pwd)/openapi.yaml:/openapi.yaml \
  swaggerapi/swagger-ui

# Otwórz przeglądarkę: http://localhost:8080
```

## Przeglądanie w Redoc

```bash
# Użyj Docker
docker run -p 8080:80 -e SPEC_URL=openapi.yaml \
  -v $(pwd)/openapi.yaml:/usr/share/nginx/html/openapi.yaml \
  redocly/redoc

# Otwórz przeglądarkę: http://localhost:8080
```

## Generowanie klienta API

### Python

```bash
# Zainstaluj openapi-generator
pip install openapi-generator-cli

# Wygeneruj klienta Python
openapi-generator-cli generate -i openapi.yaml \
  -g python -o ./python-client

# Użyj wygenerowanego klienta
cd python-client
pip install -e .
```

### JavaScript/TypeScript

```bash
# Zainstaluj openapi-generator
npm install -g @openapitools/openapi-generator-cli

# Wygeneruj klienta TypeScript
openapi-generator-cli generate -i openapi.yaml \
  -g typescript-axios -o ./ts-client
```

### Java

```bash
# Wygeneruj klienta Java
openapi-generator-cli generate -i openapi.yaml \
  -g java -o ./java-client \
  --library okhttp-gson
```

## Walidacja specyfikacji

Możesz zwalidować specyfikację OpenAPI używając różnych narzędzi:

### Swagger Validator

```bash
docker run --rm -v $(pwd):/specs swaggerapi/swagger-validator \
  validate /specs/openapi.yaml
```

### Online validator

Wejdź na https://apitools.dev/swagger-parser/online/ i wklej zawartość pliku.

## Testowanie API z curl

Wszystkie endpointy wymienione w specyfikacji OpenAPI można testować bezpośrednio z curl:

```bash
# Pobierz token
curl -X GET "http://localhost:8080/api/ishare/token"

# Pobierz parties
curl -X GET "http://localhost:8080/api/ishare/parties"

# Pobierz konkretnego participanta
curl -X GET "http://localhost:8080/api/ishare/parties/EU.EORI.NL000000000"
```

## Integracja z CI/CD

Możesz użyć specyfikacji OpenAPI w pipeline CI/CD:

### Walidacja kontraktu

```yaml
# GitHub Actions
- name: Validate OpenAPI spec
  uses: char0n/swagger-editor-validate@v1
  with:
    definition-file: openapi.yaml
```

### Automatyczne testy

```yaml
# Newman (Postman CLI) może używać OpenAPI
- name: Run API tests
  run: |
    newman run openapi.yaml \
      --environment env.json \
      --reporters cli,json
```

## Więcej informacji

- [OpenAPI Specification](https://swagger.io/specification/)
- [OpenAPI Generator](https://openapi-generator.tech/)
- [Swagger UI](https://swagger.io/tools/swagger-ui/)
- [Redoc](https://redocly.com/redoc/)
