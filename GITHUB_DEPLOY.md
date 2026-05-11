# Deployment przez GitHub - zero kosztow

Architektura: aplikacja mobilna pobiera **statyczne JSONy z GitHub Pages**, ktore sa
generowane codziennie przez **GitHub Actions cron** (darmowo).

```
                  GitHub Actions (08:00 CEST cron)
                              │
                  klucze API w GitHub Secrets
                              ↓
              python scripts/export_static_json.py
                              │
                              ↓
           docs/data/top10.json + matches/*.json
                              │
                              ↓
                      git push origin main
                              │
                              ↓
                   GitHub Pages auto-deploy
                              │
        https://[user].github.io/[repo]/data/top10.json
                              │
                              ↓
                      [Aplikacja Flutter]
```

**Koszt:** $0/mies.
**Limit:** GitHub Actions 2000 min/mies (zuzyjemy ~5 min/dzien = 150 min/mies) + GitHub Pages 100GB bandwidth/mies (bez znaczenia dla naszego ruchu).

---

## Krok 1: Push kodu do GitHub

```powershell
cd C:\Users\Startklaar\Documents\asystenbiznesu\prob-win-ai
git init
git add .
git commit -m "Initial commit: ProbWin AI v0.1.0"
```

Stworz repo na <https://github.com/new>:

- **Repository name:** `probwinai`
- **Visibility:** Public (wymagane dla darmowych GitHub Pages na User Plan; Pro/Team mozna Private)
- **NIE** zaznaczaj README, .gitignore, license (mamy juz w repo)

Po stworzeniu repo:

```powershell
git remote add origin https://github.com/[twoj-username]/probwinai.git
git branch -M main
git push -u origin main
```

## Krok 2: Wlacz GitHub Pages

W repo:

1. **Settings** -> **Pages** (lewa nawigacja, sekcja "Code and automation")
2. **Source:** `Deploy from a branch`
3. **Branch:** `main`
4. **Folder:** `/docs`
5. Klik **Save**

Po 1-2 minutach GitHub pokaze: *"Your site is live at <https://[username].github.io/probwinai/>"*

Sprawdz w przegladarce — powinienes zobaczyc strone startowa ProbWin AI.

## Krok 3: Dodaj sekrety dla GitHub Actions

W repo:

1. **Settings** -> **Secrets and variables** -> **Actions**
2. **New repository secret** -> dodaj:

| Name | Value | Opcjonalne? |
| --- | --- | --- |
| `ANTHROPIC_API_KEY` | `sk-ant-...` (klucz Claude API) | Tak, bez = mock commentary |
| `ODDS_API_KEY` | klucz z the-odds-api.com | Tak, bez = mock matches |

**Gdzie wziac klucze (opcjonalnie):**
- Anthropic Claude: <https://console.anthropic.com/settings/keys>
- the-odds-api.com: <https://the-odds-api.com/account/> (darmowy plan 500 req/mies)

Bez kluczy aplikacja **wciaz dziala** ale uzywa mockowanych danych. Idealne na MVP demo.

## Krok 4: Trigger pierwszy refresh

W repo:

1. **Actions** zakladka
2. Wybierz workflow **Daily refresh**
3. Klik **Run workflow** -> **Run workflow** (zielony przycisk)
4. Czekaj ~3-5 min az workflow sie skonczy
5. Po sukcesie zobaczysz nowy commit `Daily refresh: 2026-05-11` w main
6. Sprawdz URL: <https://[username].github.io/probwinai/data/top10.json>

Pierwszy refresh jest manualny. Pozniej cron uruchamia sie automatycznie codziennie o 06:00 UTC (08:00 CEST).

## Krok 5: Skonfiguruj URL w aplikacji mobilnej

Edytuj `mobile/lib/main.dart` linia z `kBuildtimeApiUrl`:

```dart
const String kBuildtimeApiUrl = String.fromEnvironment(
  "API_URL",
  defaultValue: "https://[twoj-username].github.io/probwinai/data",
);
```

Albo zostaw default i podaj URL przy buildzie:

```powershell
$env:PROBWIN_API_URL = "https://[twoj-username].github.io/probwinai/data"
./build_scripts/build_android_release.ps1
```

## Krok 6: Uzupelnij placeholdery w docs/index.html

Aby Apple/Google review zaakceptowali polityke prywatnosci:

1. Otworz `docs/index.html`
2. Znajdz **wszystkie** wystapienia `[kontakt@example.com]`, `[Imie / nazwa]`, `[Adres]`, `[contact@example.com]`, `[Full Name]`
3. Zamien na rzeczywiste dane
4. Commit + push:

```powershell
git add docs/index.html
git commit -m "Update privacy policy with contact info"
git push
```

## Krok 7: Wpisz URL polityki prywatnosci w App Store Connect

W App Store Connect -> App Information -> **Privacy Policy URL**:

```text
https://[twoj-username].github.io/probwinai/
```

(strona ma sekcje #privacy + #privacy-en — Apple zaakceptuje)

---

## Jak zmienic w przyszlosci

### Manualny refresh (np. po zmianie kursow)

Repo -> Actions -> Daily refresh -> Run workflow.

### Zmiana modelu / dodanie funkcji

```powershell
# Edytuj kod lokalnie
git add .
git commit -m "Add xG features to model"
git push
# Nastepny daily refresh automatycznie uzyje nowego kodu
```

### Wylaczenie codziennego cron (np. testowanie)

`.github/workflows/daily-refresh.yml`:

```yaml
on:
  # schedule:
  #   - cron: '0 6 * * *'
  workflow_dispatch:
```

Zostawia tylko manualne triggery.

---

## Limity / kiedy migrowac na backend serwerowy

GitHub Pages + Actions wystarczy do:
- ~1000-10000 userow dziennie (bandwidth limit 100GB/mies)
- 1× dziennie refresh (mozna podbic do co 2-3h)
- Brak personalizacji (wszyscy widza to samo)

Migracja na backend (Railway/Fly.io) potrzebna jak chcesz:
- **Push notifications** (wymaga server-side keep-alive)
- **Konta uzytkownikow** (login, preferences w cloud)
- **Real-time refresh** (uzytkownik klika "odswiez" -> aktualne dane)
- **Ulubione druzyny synced miedzy urzadzeniami**
- **>10k userow dziennie** (limit bandwidth)

Wtedy:
1. `flyctl deploy` z folderu projektu (mamy `fly.toml` gotowy)
2. Zmien URL w `kBuildtimeApiUrl` na `https://probwinai-api.fly.dev`
3. Static URL kontynuuje dzialac jako fallback offline

## Testowanie lokalnie

```powershell
# Generuj JSONy lokalnie
py -3.12 scripts/export_static_json.py --top 10 --no-ai

# Sprawdz w przegladarce
# Otworz: file:///C:/Users/Startklaar/Documents/asystenbiznesu/prob-win-ai/docs/data/top10.json
```

Lub uruchom prosty http server:

```powershell
cd docs
py -3.12 -m http.server 8080
# Otworz http://localhost:8080
```
