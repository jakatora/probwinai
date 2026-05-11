# App Store Submission — click-by-click checklist

Lista wszystkiego co Ty robisz w App Store Connect. Wszystkie teksty/wartosci masz juz przygotowane.

## Przed otwarciem App Store Connect

- [x] Wpis aplikacji utworzony (Bundle ID `com.probwinai.app`, SKU `probwinai-ios-001`) ✅
- [ ] **Ikona aplikacji** - konwertuj `store_listing/app_icon/icon_1024.svg` na PNG 1024x1024
- [ ] **6 screenshotow** - konwertuj wszystkie `store_listing/screenshots/*.svg` na PNG 1290x2796
- [ ] **Privacy URL dziala** - GitHub Pages live
- [ ] **Build w TestFlight** - upload IPA przez Codemagic

> Jak konwertowac SVG na PNG: otworz `store_listing/screenshots/preview.html` w Chrome i postępuj wg instrukcji.

## App Store Connect - Sekcja 1: App Information

Wejdz na <https://appstoreconnect.apple.com> -> My Apps -> ProbWin AI: Football Stats -> **App Information** (lewa zakladka).

- [ ] **Subtitle:** `Match analysis with AI insight`
- [ ] **Privacy Policy URL:** `https://[twoj-github-user].github.io/probwinai/`
- [ ] **Category - Primary:** `Sports`
- [ ] **Category - Secondary:** `Reference`
- [ ] **Content Rights:** wybierz *"Does not contain, show, or access third-party content"*
- [ ] **Age Rating:** kliknij Edit, wypelnij ankiete (patrz `app_store_complete.md` Sekcja 1)
  - [ ] Simulated Gambling: **Yes**
  - [ ] Reszta: None
  - [ ] Made for Kids: No
  - [ ] Wynik: **17+**
- [ ] Klik **Save**

## Sekcja 2: Pricing and Availability

Lewa zakladka -> **Pricing and Availability**.

- [ ] **Price:** Free
- [ ] **Availability:** Poland, United Kingdom, United States, Germany, Canada, Australia (zaznacz, ZOSTAW WSZYSTKO INNE PUSTE)
- [ ] **Volume Purchase Program:** NIE zaznaczaj
- [ ] Klik **Save**

## Sekcja 3: App Privacy

Lewa zakladka -> **App Privacy** -> **Get Started**.

- [ ] **Do you or your third-party partners collect data from this app?** -> **No**
- [ ] Klik **Publish**

## Sekcja 4: Version 1.0 - Prepare for Submission

Lewa zakladka -> **1.0 Prepare for Submission**.

### Screenshots (sekcja gora strony)

- [ ] iPhone 6.7" Display: wgraj minimum 3 PNG (sugerowane 5):
  - [ ] `02_match_list.png` (pozycja 1)
  - [ ] `03_match_detail_ai.png` (pozycja 2 - kluczowy hero)
  - [ ] `04_match_detail_probability.png` (pozycja 3)
  - [ ] `05_match_detail_teams.png` (pozycja 4)
  - [ ] `01_welcome.png` (pozycja 5)

> Apple uzyje screenshotow 6.7" automatycznie dla mniejszych iPhone'ow.

- [ ] iPad: pomin (jesli nie wspierasz - my nie wspieramy w MVP)

### Promotional Text

- [ ] Wklej:
```text
Daily top 10 football matches with statistical probabilities and AI commentary. Understand bookmaker odds through transparent analytics. No bets, just insights.
```

### Description

- [ ] Wklej tekst z `store_listing/app_store_complete.md` (sekcja Description) - **podmien [twoj-email] na rzeczywisty email**

### Keywords

- [ ] Wklej *(bez spacji po przecinkach!)*:
```text
football,soccer,stats,probability,ai,analysis,fixtures,elo,odds,premierleague,laliga,bundesliga
```

### Support URL

- [ ] `https://[twoj-github-user].github.io/probwinai/`

### Marketing URL (opcjonalne)

- [ ] `https://[twoj-github-user].github.io/probwinai/`

### Version

- [ ] `1.0`

### Copyright

- [ ] `2026 [Twoje imie/firma]`

### App Review Information

- [ ] **Sign-In Required:** No
- [ ] **First Name:** [Twoje imie]
- [ ] **Last Name:** [Twoje nazwisko]
- [ ] **Phone Number:** [Twoj telefon z prefiksem]
- [ ] **Email:** [Twoj email]
- [ ] **Notes:** wklej DUZY blok z `store_listing/app_store_complete.md` (sekcja "Notes for review") - KRYTYCZNE dla gambling-related app!

### Version Release

- [ ] **Manually release this version**
- [ ] Phased Release: Release at the same time (mozesz przelaczyc na 7-day phased dla pewnosci)

### Build

⚠️ Tej sekcji NIE wypelnisz dopoki nie masz buildu z Codemagic w TestFlight.

Jak juz bedzie:
- [ ] Build -> "+" -> wybierz najnowszy build (np. `0.1.0 (101)`)
- [ ] **Export Compliance:** "Does your app use encryption?" -> **No** (uzywamy tylko standardowego HTTPS exemption)
- [ ] **Content Rights:** "Does this app use third-party content?" -> **No**
- [ ] **Advertising Identifier:** "Does this app use IDFA?" -> **No**

### What's New (Release Notes)

- [ ] Wklej:
```text
First release of ProbWin AI.

* Top 10 daily football matches across major European leagues
* Mathematical probability calculations using Elo ratings
* AI-generated match commentary in plain language
* Bookmaker odds comparison
* Team form and head-to-head history
* Dark mode interface
```

## Final - Submit for Review

- [ ] Wszystkie pola powyzej zielone? Sprawdz w lewym menu - "Prepare for Submission" -> wszystkie sekcje powinny miec zielone checkmarki
- [ ] Klik **Add for Review** (gora strony, prawy gorny rog) lub **Submit for Review**
- [ ] Potwierdz w dialog box

**Status zmienia sie na "Waiting for Review"**. Pierwsze submission: 1-7 dni.

## Po submission - co moze sie wydarzyc

### Status "Pending Developer Release"

Apple zatwierdzilo! Sam decydujesz kiedy aplikacja idzie live:

- [ ] App Store Connect -> 1.0 -> **Release this version** (przycisk u gory)
- W ciagu 2-3 godzin aplikacja jest wyszukiwalna w App Store

### Status "Rejected"

Apple ma uwagi. W zakladce **Resolution Center** zobaczysz konkretny Guideline + opis problemu. Najczestsze dla naszej aplikacji:

| Powod | Co odpowiedziec |
| --- | --- |
| 5.3 Gaming, Gambling | Wklej skrocona wersja "Notes for review" - podkreslamy ze NIE jest gambling operator, brak transakcji |
| 1.4.3 Promotes gambling | Pokaz screenshot welcome screen z disclaimerem, link do helpline |
| 5.1.1 Privacy missing | Sprawdz GitHub Pages incognito, popraw URL |
| 2.1 App incomplete | Twoj backend niedostepny (Railway down?) - upewnij sie ze API_URL w buildzie wskazuje na live serwer |
| 4.3 Design - Spam | Bardzo rzadkie, zwykle wymaga unikalnej wartosci - mamy AI commentary jako differentiator |

Mozesz odpowiedziec w **Resolution Center** i ponowic submission. Apple czesto pyta 1-2 razy zanim zatwierdzi gambling-related app.

## Estymowany czas

- **Sekcja 1-3 (App Info, Pricing, Privacy):** 30 min (juz prawie zrobione)
- **Sekcja 4 (Version 1.0 + screenshots):** 1h
- **App Review wait:** 1-7 dni
- **Total:** ~2-3 godziny pracy + tydzien czekania

---

## Lista plikow ktore juz masz przygotowane

| Plik | Cel |
| --- | --- |
| `store_listing/app_store_complete.md` | **Glowny dokument** - wszystkie teksty App Store |
| `store_listing/SUBMISSION_CHECKLIST.md` | **Ten plik** - krok po kroku co klikac |
| `store_listing/app_icon/icon_1024.svg` | Ikona 1024x1024 (konwertuj na PNG) |
| `store_listing/screenshots/01-06_*.svg` | 6 mockupow ekranow (konwertuj na PNG) |
| `store_listing/screenshots/preview.html` | Podglad wszystkich screenshotow + instrukcja konwersji |
| `legal/index.html` | Privacy policy + ToS do GitHub Pages |

## Co teraz musisz konkretnie zrobic

### Krok 1 (10 min): Konwersja SVG -> PNG

Otworz `store_listing/screenshots/preview.html` w Chrome. Wybierz **Sposob B (CloudConvert)** - najszybsze:

1. <https://cloudconvert.com/svg-to-png>
2. Drag-drop wszystkich 6 SVG na raz
3. Settings (kazdy plik): Output Width = 1290, Output Height = 2796
4. Convert
5. Pobierz ZIP
6. Wypakuj do `store_listing/screenshots/png/`

Powtorz dla `app_icon/icon_1024.svg` -> 1024x1024 PNG.

### Krok 2 (30 min): GitHub Pages dla privacy

Patrz `legal/README.md`. Stworz repo `probwinai`, wgraj `legal/index.html`, wlacz Pages.

### Krok 3 (15 min): Wypelnij App Store Connect Sekcje 1-3

Patrz checklist powyzej, podaj wartosci z `app_store_complete.md`.

> Po tych 3 krokach masz wszystko **oprocz buildu z Codemagic**. Build wymaga zakonczonej fazy deploymentu backendu (Railway) i konfiguracji Codemagic.
