# EDC PSNC Bruno Collection

Kolekcja requestów API dla Eclipse Dataspace Connector (EDC) w narzędziu Bruno.

## Bruno

[Bruno](https://www.usebruno.com/) to opensource'owe narzędzie do testowania API (alternatywa dla Postmana/Insomnia). Kolekcje są przechowywane jako pliki lokalne w repozytorium, co ułatwia współdzielenie i wersjonowanie.

### Instalacja Bruno

- **macOS**: `brew install bruno`
- **Windows/Linux**: Pobierz z [usebruno.com](https://www.usebruno.com/downloads)

## Otwieranie kolekcji

1. Uruchom Bruno
2. Kliknij **Open Collection** (lub `Cmd/Ctrl + O`)
3. Wskaż folder: `.../psnc-edc-mvds/requests/EDC PSNC`
4. Bruno załaduje kolekcję zawierającą wszystkie foldery z requestami

## Environments (środowiska)

Kolekcja zawiera 3 predefiniowane środowiska w folderze `environments/`:

- **Local.yml** – lokalne środowisko deweloperskie
- **BST2 DAPS.yml** – środowisko testowe BST2 z DAPS
- **BST2 DCP.yml** – środowisko testowe BST2 z DCP

### Wybieranie środowiska

1. W prawym górnym rogu Bruno wybierz dropdown **Environment**
2. Wybierz jedno z dostępnych środowisk (np. `Local`, `BST2 DAPS`)
3. Zmienne ze środowiska (np. `{{baseUrl}}`, `{{apiKey}}`) zostaną automatycznie podstawione w requestach

### Edycja środowisk

Kliknij ikonę ⚙️ obok dropdownu Environment, aby edytować zmienne:
- `baseUrl` – adres bazowy API
- `connectorUrl` – URL connectora
- `apiKey` – klucz autoryzacyjny
- inne zmienne specyficzne dla środowiska

## Wykonywanie requestów

### Struktura kolekcji

```
Connector/         – zarządzanie EDC connector
Data Space Hub/    – operacje na Data Space Hub
Data Transfer/     – transfery danych
Federated Catalog/ – katalog federacyjny
Identity Hub/      – zarządzanie tożsamością
```

### Wywoływanie requestu

1. Rozwiń folder w lewym panelu (np. `Connector`)
2. Wybierz request (np. `GET Health Check`)
3. Sprawdź URL i parametry (zmienne środowiska są automatycznie podstawiane)
4. Kliknij **Send** (lub `Cmd/Ctrl + Enter`)
5. Odpowiedź pojawi się w dolnym panelu

### Zmienne w requestach

Requesty używają zmiennych środowiskowych w formacie `{{variableName}}`:

```
GET {{baseUrl}}/api/v1/health
Authorization: {{apiKey}}
```

Bruno automatycznie podmienia wartości z wybranego środowiska.

## Porady

- **Pre-request Scripts**: niektóre requesty mogą mieć skrypty wykonywane przed wysłaniem
- **Tests**: po otrzymaniu odpowiedzi mogą być uruchamiane testy walidacyjne
- **Sekwencje**: requesty można uruchamiać sekwencyjnie używając funkcji **Run Collection**
- **Dokumentacja**: każdy request może zawierać zakładkę **Docs** z dodatkowym opisem

## Przydatne skróty

- `Cmd/Ctrl + Enter` – wyślij request
- `Cmd/Ctrl + S` – zapisz zmiany
- `Cmd/Ctrl + O` – otwórz kolekcję
- `Cmd/Ctrl + ,` – ustawienia Bruno
