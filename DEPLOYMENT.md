# Deployment - publikujemy backend ProbWin AI

**Po co:** App Store / Google Play reviewerzy otworza Twoja aplikacje na urzadzeniu testowym. Aplikacja **musi** umiec polaczyc sie z Twoim API publicznym - bez tego dostaniesz `1.1.1 (Doesn't work)` rejection.

## Wybor hostingu - rekomendacja

| Opcja | Koszt | Czas setup | Plus | Minus |
| --- | --- | --- | --- | --- |
| **Railway** | $5/mies free credit (~hobby project mieści się) | 10 min | Auto deploy z GitHub, HTTPS, persistent volume | Po $5 zaczyna naliczac |
| **Fly.io** | Darmowy plan (3 maszyny shared, 256MB) | 15 min | Generous free tier, persistent volumes, edge sieć | Wymaga `flyctl` CLI |
| **Render** | Free plan (uspia po 15 min nieaktywnosci -> cold start) | 10 min | Najprostszy, GitHub auto-deploy | Cold start ~30s niezdrowy dla mobile UX |
| **VPS (Hetzner)** | 5€/mies stale | 1-2h | Pelna kontrola, najtansza dlugoterminowo | Sam ogarniasz nginx, systemd, certyfikaty |

**Moja rekomendacja:** **Railway** dla MVP - najprostsze, auto deploy z push. Migracja do VPS gdy aplikacja wystartuje.

---

## Wariant A: Railway (rekomendowany)

### Wymagania

- Konto GitHub (juz masz)
- Repo z kodem aplikacji pushnięte do GitHub

### Kroki

#### 1. Push kodu do GitHub

```powershell
cd C:\Users\Startklaar\Documents\asystenbiznesu\prob-win-ai
git init
git add .
git commit -m "Initial commit"

# Stworz nowe repo na GitHub: https://github.com/new
# Nazwa: probwinai-app, Private
# Potem:
git remote add origin https://github.com/[twoj-user]/probwinai-app.git
git branch -M main
git push -u origin main
```

#### 2. Stworz projekt na Railway

1. Wejdz na <https://railway.app>
2. Sign in with GitHub
3. **New Project** -> **Deploy from GitHub repo** -> wybierz `probwinai-app`
4. Railway wykryje `Dockerfile` i `railway.json` automatycznie

#### 3. Ustaw zmienne srodowiskowe

W Railway: Project -> Variables (lewa zakladka):

```text
ANTHROPIC_API_KEY      = sk-ant-...  (Twoj klucz Claude, opcjonalnie)
ODDS_API_KEY           = ...         (Twoj klucz the-odds-api, opcjonalnie)
ALLOWED_ORIGINS        = *           (lub `https://probwinai.github.io` dla wiekszego bezpieczenstwa)
DATABASE_PATH          = /data/probwin.sqlite
ELO_CACHE_PATH         = /data/elo_cache.json
PORT                   = 8000        (Railway nadpisze automatycznie ale dla pewnosci)
```

#### 4. Dodaj persistent volume

Railway -> Settings -> Volumes:

- **Mount path:** `/data`
- **Size:** 1 GB (wystarczy z duzym zapasem)

To zachowa baze SQLite i cache Clubelo miedzy restartami.

#### 5. Wygeneruj publiczny URL

Railway -> Settings -> Networking -> **Generate Domain**

Dostajesz: `https://probwinai-app-production-XXXX.up.railway.app`

#### 6. Test

```powershell
curl https://probwinai-app-production-XXXX.up.railway.app/api/health
```

Powinno zwrocic JSON `{"status":"ok",...}`.

#### 7. Seed danych (jednorazowo)

Railway pozwala uruchomic jednorazowa komende:

```bash
# W Railway UI: Services -> probwinai-app -> Settings -> One-time command
python scripts/seed_demo.py
```

Lub przez Railway CLI:

```powershell
npm install -g @railway/cli
railway login
railway run python scripts/seed_demo.py
```

#### 8. Sprawdz aplikacje

```powershell
# Lista meczow:
curl https://probwinai-app-production-XXXX.up.railway.app/api/matches

# Dashboard HTML:
# Otworz w przegladarce: https://probwinai-app-production-XXXX.up.railway.app/
```

#### 9. Daily cron

Railway nie ma wbudowanego cron-a. Opcje:

- **GitHub Actions** (darmowy, latwy):

```yaml
# Plik: .github/workflows/daily-refresh.yml
name: Daily refresh
on:
  schedule:
    - cron: '0 6 * * *'  # 06:00 UTC = 08:00 CEST
  workflow_dispatch:      # rowniez recznie
jobs:
  refresh:
    runs-on: ubuntu-latest
    steps:
      - run: |
          curl -X POST https://probwinai-app-production-XXXX.up.railway.app/api/refresh?top=10
```

- **Railway add-on:** Cron service za $1/mies (oddzielna usluga)

### Konfiguracja Flutter na nowy URL

Po deploy zaktualizuj URL w buildzie aplikacji:

```powershell
$env:PROBWIN_API_URL = "https://probwinai-app-production-XXXX.up.railway.app"
./build_scripts/build_android_release.ps1
```

Albo dla buildu lokalnego:

```powershell
cd mobile
flutter run --dart-define=API_URL=https://probwinai-app-production-XXXX.up.railway.app
```

---

## Wariant B: Fly.io

### Wymagania

- Konto Fly.io: <https://fly.io/app/sign-up>
- `flyctl` CLI

### Setup `flyctl` na Windows

```powershell
# Powershell jako Administrator
iwr https://fly.io/install.ps1 -useb | iex
```

Zrestartuj terminal, potem:

```powershell
flyctl auth login
```

### Deploy

```powershell
cd C:\Users\Startklaar\Documents\asystenbiznesu\prob-win-ai
flyctl launch --copy-config --name probwinai-api --region waw --no-deploy
flyctl volumes create probwinai_data --size 1 --region waw
flyctl secrets set ANTHROPIC_API_KEY=sk-ant-...
flyctl secrets set ODDS_API_KEY=...
flyctl deploy
```

Po deployu:

```powershell
flyctl status
# Open: https://probwinai-api.fly.dev
```

URL bedzie: `https://probwinai-api.fly.dev`

---

## Bezpieczenstwo produkcyjne

### CORS

Po deployu zmien `ALLOWED_ORIGINS` z `*` na konkretne URLs:

```text
ALLOWED_ORIGINS = https://probwinai.github.io,https://probwinai-app.up.railway.app
```

W produkcji aplikacja mobilna **nie potrzebuje CORS** (nie jest browserem) - mozesz nawet ustawic `ALLOWED_ORIGINS=https://probwinai.github.io` i aplikacja mobilna nadal bedzie dzialac (mobile ignoruje CORS).

### Klucze API w sekretach

NIGDY nie commituj `.env` do GitHub. Klucze sa w:
- Railway: Variables
- Fly.io: `flyctl secrets`
- Codemagic: Environment groups

### HTTPS

Railway i Fly.io daja HTTPS automatycznie. iOS i Android **wymagaja HTTPS** dla production (Apple ATS, Google Network Security Config).

### Rate limiting (opcjonalne na MVP)

Jak aplikacja wystartuje:

```bash
pip install slowapi
```

Dodaj do `backend/main.py`:

```python
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter

@app.get("/api/matches")
@limiter.limit("100/minute")
def get_matches(...): ...
```

---

## Monitoring

### Logi

- Railway: Project -> Service -> Logs (live tail)
- Fly.io: `flyctl logs`

### Uptime monitoring

Darmowe opcje:
- <https://uptimerobot.com> (free 50 monitorow, 5 min interwal)
- <https://betterstack.com/uptime>

Dodaj monitor na `https://[twoj-url]/api/health` - dostaniesz email gdy serwer padnie.

---

## Koszty dlugoterminowe (szacunek)

Dla aplikacji z ~100-1000 uzytkownikow dziennie:

| Usluga | Miesieczny koszt |
| --- | --- |
| Railway (lub Fly.io) | $5-10 |
| Domain (.com) | $1/mies ($12/rok) |
| the-odds-api.com (jak przekroczysz free) | $30-100 |
| Anthropic Claude API (~10 meczow/dzien x 30 dni x $0.10) | ~$30 |
| Google Play Developer | $0 (jednorazowo zaplacone) |
| Apple Developer | ~$8 ($99/12) |
| **Razem** | **~$45-150/mies** |

Plus: jak zaczniesz monetyzowac (subskrypcja / reklamy), Apple/Google biora 15-30% prowizji.

---

## Quick start dla niecierpliwych

```powershell
# 1. Push do GitHub
git init && git add . && git commit -m "init"
# (stworz repo na github.com/new, copy URL)
git remote add origin https://github.com/[user]/probwinai-app.git
git push -u origin main

# 2. Railway: https://railway.app -> New Project -> Deploy from GitHub
# (klikasz; Railway sam czyta Dockerfile)

# 3. Po 3-5 min: Settings -> Generate Domain
# (dostajesz https://...up.railway.app)

# 4. Test
curl https://[twoj-url].up.railway.app/api/health

# 5. Seed
railway run python scripts/seed_demo.py

# 6. Build aplikacji z nowym URL
$env:PROBWIN_API_URL = "https://[twoj-url].up.railway.app"
./build_scripts/build_android_release.ps1

# Done. Upload AAB do Google Play Console.
```
