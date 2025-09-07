# Backend - Audytor Dostępności PDF

Ten projekt zawiera backend dla aplikacji A11y PDF Audit Server, napisany w Pythonie z użyciem frameworka FastAPI.

---

## Wymagania

Przed uruchomieniem projektu upewnij się, że masz zainstalowane następujące narzędzia:

- **Docker & Docker Compose**: Do uruchomienia całej aplikacji w kontenerach.
- **Python 3.10+**: Do lokalnego uruchomienia i dewelopmentu backendu.
- **Git**: Do klonowania i zarządzania kodem źródłowym.

---

## 🚀 Uruchomienie Całej Aplikacji (Zalecane)

Ta metoda uruchomi jednocześnie backend, frontend i bazę danych za pomocą jednego polecenia.

1.  **Sklonuj repozytorium**:

    ```bash
    git clone <URL_TWOJEGO_REPOZYTORIUM>
    cd <nazwa-folderu-projektu>
    ```

2.  **Skonfiguruj zmienne środowiskowe**:
    Utwórz plik `.env` w głównym katalogu projektu (obok pliku `docker-compose.yml`) i dodaj do niego poniższą zawartość. **Ustaw bezpieczne hasło!**

    ```env
    POSTGRES_USER=user
    POSTGRES_PASSWORD=moje-super-tajne-haslo-123
    POSTGRES_DB=mydb
    ```

3.  **Uruchom kontenery**:
    ```bash
    docker-compose up --build
    ```

Backend będzie dostępny pod adresem `http://localhost:8000`.

---

## 🛠️ Lokalne Uruchomienie Tylko Backendu (Do Dewelopmentu)

Poniższe kroki pozwolą Ci uruchomić sam serwer backendowy na Twojej maszynie, co jest przydatne podczas pisania kodu i debugowania.

1.  **Przejdź do folderu backendu**:
    Upewnij się, że jesteś w głównym folderze projektu, a następnie wejdź do katalogu z kodem backendu.

    ```bash
    cd backend
    ```

2.  **Utwórz środowisko wirtualne Pythona**:
    To polecenie stworzy folder `.venv`, w którym będą przechowywane wszystkie zależności tego projektu, izolując je od reszty systemu.

    ```bash
    py -m venv .venv
    ```

3.  **Aktywuj środowisko wirtualne**:
    Musisz to robić za każdym razem, gdy otwierasz nowy terminal, aby pracować nad projektem.

    ```bash
    # Dla Windows (PowerShell)
    .\.venv\Scripts\Activate.ps1
    ```

    Po aktywacji, na początku wiersza poleceń pojawi się napis `(.venv)`.

4.  **Zainstaluj zależności**:
    Ta komenda zainstaluje wszystkie biblioteki Pythona potrzebne do działania projektu, które są zdefiniowane w pliku `requirements.txt`.

    ```bash
    pip install -r requirements.txt
    ```

5.  **Uruchom serwer deweloperski**:
    Polecenie to uruchomi serwer FastAPI, który będzie automatycznie przeładowywał się po każdej zmianie w kodzie (`--reload`).
    ```bash
    uvicorn main:app --reload
    ```

---

## Weryfikacja

Po uruchomieniu serwera (niezależnie od metody), otwórz przeglądarkę i przejdź pod adres:

**`http://localhost:8000/docs`**

Powinieneś zobaczyć automatycznie wygenerowaną, interaktywną dokumentację API (Swagger UI). To potwierdza, że backend działa poprawnie.

## 🧪 Testowanie Endpointu

Po uruchomieniu aplikacji możesz łatwo przetestować główny endpoint do analizy plików PDF.

1.  **Otwórz interaktywną dokumentację** w przeglądarce, przechodząc pod adres:
    **`http://localhost:8000/docs`**

2.  **Znajdź endpoint `POST /upload/pdf/`** w sekcji "PDF Processing" i rozwiń go.

3.  Kliknij przycisk **"Try it out"**.

4.  W nowo otwartym formularzu kliknij **"Choose File"** i wybierz plik PDF ze swojego komputera.

5.  Naciśnij niebieski przycisk **"Execute"**.

6.  **Sprawdź wynik** w sekcji "Server response". Powinieneś otrzymać odpowiedź w formacie JSON z analizą Twojego pliku, np.:
    ```json
    {
    	"filename": "przykladowy.pdf",
    	"page_count": 10,
    	"is_tagged": true,
    	"contains_text": true,
    	"extracted_text_preview": "To jest początek tekstu..."
    }
    ```
