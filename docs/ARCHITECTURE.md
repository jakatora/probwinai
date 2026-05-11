# ProbWin AI - architektura

## Przeplyw danych (codzienny refresh)

```
              ┌────────────────────────────────────────┐
              │   scripts/refresh_daily.py             │
              │   (cron 8:00)                          │
              └─────────────────┬──────────────────────┘
                                │
                                ▼
         ┌──────────────────────────────────────────────┐
         │  the-odds-api.com  →  fetch_upcoming()      │
         │  Lista meczow + kursy 1X2 (Betclic)         │
         └──────────────────────┬───────────────────────┘
                                │
                                ▼
                  top N meczow (popularnosc)
                                │
                                ▼
              ┌─────────────────────────────────┐
              │ Dla kazdego meczu:              │
              │                                 │
              │  1. Clubelo.com → Elo           │
              │  2. football-data → forma + H2H │
              │  3. Elo + kurs → probability    │
              │  4. Claude API (web_search)     │
              │     → komentarz AI              │
              │                                 │
              │  -> MatchInsights (Pydantic)    │
              └─────────────────┬───────────────┘
                                │
                                ▼
            ┌──────────────────────────────────┐
            │  SQLite cache                    │
            │  matches table (JSON column)     │
            └──────────────────────────────────┘
                                │
                                ▼
            ┌──────────────────────────────────┐
            │  Konsumenci:                     │
            │  - FastAPI /api/matches          │
            │  - Flutter mobile (HTTP)         │
            │  - HTML preview (browser)        │
            │  - Static HTML reports/          │
            └──────────────────────────────────┘
```

## Warstwy backendu

### `backend/models/`
**Czysta domena.** Pydantic schematy + algorytm probability.
Nie zalezy od HTTP, DB, AI. Jednostkowe testy bez external mocks.

- `schemas.py` - MatchInput, MatchInsights, Probability, FormSummary, ...
- `probability.py` - `elo_to_probability()`, `odds_to_implied()`

### `backend/data/`
**Adaptery do zewnetrznych zrodel.** Kazdy klient enkapsuluje jedna uslugu.

- `clubelo.py` - HTTP do api.clubelo.com (z cache JSON na dysku)
- `football_data.py` - CSV z football-data.co.uk (forma, H2H)
- `odds_api.py` - HTTP do api.the-odds-api.com (kursy + mock fallback)
- `team_names.py` - slownik aliasow nazw druzyn

### `backend/ai/`
**Generowanie komentarzy.** Claude API z narzedziem web_search.
Bez klucza -> mock oparty o liczby.

- `commentary.py` - `generate_commentary(insights)`

### `backend/services/`
**Orkiestracja.** Sklejanie warstw w pelny raport.

- `insights_service.py` - InsightsService.generate()
- `reporting.py` - render HTML (Jinja2)

### `backend/db/`
**SQLite z dwiema operacjami:** save_match_list i save_insights.
Tabela `matches` ma kolumne `insights_json` (denormalizowany pelny obiekt).

### `backend/main.py`
**FastAPI app.** Tylko transport HTTP. Logika jest w services.

## Decyzje projektowe

### Dlaczego Pydantic v2?
Bo FastAPI, walidacja, JSON serialization, type safety - wszystko gratis.

### Dlaczego SQLite a nie PostgreSQL?
MVP. Dane sa zarzadzane przez 1 proces (cron + API server). Brak potrzeby
concurrent writes. Latwy deploy (jeden plik). Migracja do PostgreSQL trywialna
(SQLAlchemy ORM) jesli aplikacja wzrosnie.

### Dlaczego SQLite kolumna `insights_json` zamiast normalizacji?
Bo MatchInsights jest agregatem read-only (generowanym raz, czytanym wielokrotnie).
Brak korzysci z normalizacji - tylko narzut JOIN-ow. Ewolucja schematu = update
JSON, brak migracji.

### Dlaczego Flutter a nie React Native?
Jeden codebase, dwie platformy (iOS+Android), kompilacja AOT do natywnego kodu,
material design out of the box. RN tez OK, Flutter pozwolil zaoszczedzic czas
na UI components.

### Dlaczego mock fallback w odds_api.py i commentary.py?
Demo bez kosztow API + Etap A (proof of concept) niezalezny od kluczy zewnetrznych.

## Co NIE jest w MVP

- Autentykacja uzytkownikow (planowane Etap E)
- Push notifications (planowane Etap E)
- Wybor ulubionych druzyn (UI placeholder w settings, brak persistence per user)
- Wielojezycznosc (planowane Etap F)
- Statystyki xG (planowane Etap B+)
- Multi-liga w jednym refresh (Etap C: rozszerzenie odds_api o petle)

## Performance notes

- **Pierwszy refresh:** ~50-60s (pobiera Elo dla 20+ druzyn). Kolejne: <5s (cache).
- **Pojedynczy raport:** ~5s (AI commentary z web_search) lub <500ms (mock).
- **API endpoint:** <100ms (SQLite read).
- **Mobile cold start:** <2s (cache prefs + first /api/matches request).

## Bezpieczenstwo

- Klucze API w `.env` (gitignored).
- CORS allow * w `main.py` - tylko MVP, w produkcji ograniczyc do app URL.
- Brak rate limiting - dodac przed publikacja (slowapi).
- SQL: parameterized queries (sqlite3 ?-binding). Brak SQL injection.

## Roadmap (post-MVP)

| Etap | Cel | Czas szacunkowy |
|---|---|---|
| B | Backend produkcyjny (Docker, PostgreSQL, deploy do VPS) | 1-2 tyg |
| C | Multi-liga: La Liga, Bundesliga, Serie A, MLS | 3-5 dni |
| D | Aplikacja w Apple/Google sklepach (Apple Developer + Google Play) | 2-4 tyg w sklepach |
| E | Push notif, ulubione druzyny, konta uzytkownikow | 2-3 tyg |
| F | Wielojezycznosc, dark/light mode, accessibility | 1 tyg |
