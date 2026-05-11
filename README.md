# ProbWin AI

Sport analytics z komentarzem AI. Aplikacja codziennie wybiera top 10 popularnych
meczow pilkarskich, liczy prawdopodobienstwa wynikow modelem statystycznym (Elo),
porownuje z kursem bukmachera i dodaje komentarz analityczny generowany przez
Claude AI z dostepem do internetu.

**ProbWin AI to narzedzie informacyjne. Nie rekomenduje zakladow.**

## Architektura

```text
prob-win-ai/
├── backend/                  # Python backend (FastAPI)
│   ├── models/               # Pydantic schemas + model probabilistyczny
│   ├── data/                 # Klienci API (Clubelo, football-data, the-odds-api)
│   ├── ai/                   # Generowanie komentarzy (Claude API)
│   ├── services/             # Orkiestracja insights + rendering HTML
│   ├── db/                   # SQLite cache
│   ├── templates/            # Jinja2 (raporty HTML)
│   └── main.py               # FastAPI app
├── scripts/                  # CLI tools
│   ├── generate_report.py    # Raport dla 1 meczu
│   ├── refresh_daily.py      # Codzienne odswiezenie top N
│   ├── seed_demo.py          # Napelnij baze 10 przykladowymi meczami (do demo)
│   └── cleanup_reports.py    # Usun raporty HTML starsze niz N dni
├── tests/                    # Pytest
├── mobile/                   # Flutter app (iOS + Android)
├── research/                 # Skrypty walidacyjne (backtest, walking-forward CV)
└── docs/                     # Dokumentacja architektury
```

## Szybki start (backend)

```bash
# 1. Stworz srodowisko Python 3.12+
py -3.12 -m venv .venv
.venv\Scripts\activate         # Windows
# source .venv/bin/activate    # Linux/Mac

# 2. Zainstaluj zaleznosci
pip install -r requirements.txt

# 3. Skonfiguruj klucze API (opcjonalne)
cp .env.example .env
# Wypelnij ANTHROPIC_API_KEY (Claude) i ODDS_API_KEY (the-odds-api.com)
# Bez kluczy aplikacja dziala z mockowanymi danymi.

# 4. Test jednego meczu
py scripts/generate_report.py "Aston Villa" "Liverpool" 3.10 3.90 2.05 --date 2026-05-17
# -> reports/aston-villa_vs_liverpool_2026-05-17.html

# 5. Codzienne odswiezenie top 10
py scripts/refresh_daily.py

# 6. Uruchom REST API
uvicorn backend.main:app --reload --port 8000
# -> http://localhost:8000        (lista meczow w HTML)
# -> http://localhost:8000/api/health
# -> http://localhost:8000/docs   (Swagger)
```

## Konfiguracja (.env)

| Zmienna | Opis | Domyslnie |
| --- | --- | --- |
| `ANTHROPIC_API_KEY` | Klucz Claude API (komentarze AI). Bez = mock | brak |
| `ODDS_API_KEY` | Klucz the-odds-api.com (kursy). Bez = mock | brak |
| `ODDS_API_SPORT` | Liga (soccer_epl, soccer_spain_la_liga, ...) | soccer_epl |
| `ODDS_API_REGION` | Region kursow (eu/uk/us) | eu |
| `TOP_N_MATCHES` | Ile meczow w 'top N' | 10 |
| `DATABASE_PATH` | Sciezka SQLite | backend/db/probwin.sqlite |
| `API_HOST` / `API_PORT` | FastAPI bind | 127.0.0.1 / 8000 |

## Aplikacja mobilna (Flutter)

```bash
cd mobile
flutter pub get
flutter run
```

Szczegoly: [`mobile/README.md`](mobile/README.md).

## Testy

```bash
py -3.12 -m pytest tests/ -v
```

## Daily cron na Windows

Otworz "Harmonogram zadan" -> "Utworz zadanie podstawowe":

- Uruchamiaj: codziennie 08:00
- Akcja: `py.exe`
- Argumenty: `C:\Users\Startklaar\Documents\asystenbiznesu\prob-win-ai\scripts\refresh_daily.py`

Lub PowerShell:

```powershell
$action = New-ScheduledTaskAction -Execute "py.exe" `
  -Argument "$PSScriptRoot\scripts\refresh_daily.py"
$trigger = New-ScheduledTaskTrigger -Daily -At 8am
Register-ScheduledTask -TaskName "ProbWin Daily Refresh" `
  -Action $action -Trigger $trigger
```

## Daily cron na Linux

```cron
0 8 * * * cd /path/to/prob-win-ai && /usr/bin/python3 scripts/refresh_daily.py
```

## API endpointy

| Endpoint | Opis |
| --- | --- |
| `GET /api/health` | Status, info o kluczach |
| `GET /api/matches?limit=50` | Lista meczow |
| `GET /api/matches/{id}` | Pelne insights dla meczu |
| `POST /api/refresh?top=10` | Manualny refresh |
| `GET /matches/{id}` | HTML preview raportu |
| `GET /` | HTML lista meczow (browser preview) |

## Zrodla danych

| Zrodlo | Cel | Tier |
| --- | --- | --- |
| [Clubelo.com](http://clubelo.com) | Ratingi Elo klubow | Darmowe, bez rejestracji |
| [football-data.co.uk](https://www.football-data.co.uk) | Historia meczow + kursy zamkniecia | Darmowe, bez rejestracji |
| [the-odds-api.com](https://the-odds-api.com) | Aktualne kursy 70+ bukmacherow (Betclic) | Darmowy plan 500 req/mies |
| [Claude API (Anthropic)](https://anthropic.com) | Komentarze AI z web_search | Platne (~$0.05-0.20/mecz) |

## Wyniki walidacji modelu

Walking-forward CV na 3 sezonach Premier League pokazal ze model NIE bije
bukmachera systematycznie (-10.7% ROI ogolem). To znany trudny problem -
biicie marzy bukmachera 6% wymaga zaawansowanych danych ($1000+/mies)
lub niszowych rynkow.

Decyzja produktowa: aplikacja pozycjonowana jako **narzedzie analityczne**
(NIE predyktor value bets). Wartoscia jest analiza AI + transparentne
prawdopodobienstwa, nie obietnica zysku.

Szczegoly: [`research/`](research/) - 5 skryptow walidacyjnych z dokumentacja.

## Disclaimer

ProbWin AI jest aplikacja informacyjna. Nie zacheca do hazardu, nie
rekomenduje konkretnych zakladow, nie gwarantuje zyskow. Hazard moze
uzalezniac. Pomoc: 801 199 990 (Polska).

Pozycjonowanie marketingowe: "sport analytics with AI", "match insights",
"football analysis". NIE: "betting tips", "sure bets", "winning predictions".
