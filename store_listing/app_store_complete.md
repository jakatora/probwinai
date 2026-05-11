# App Store Connect - kompletny przewodnik po polach

Wszystkie pola ktore App Store Connect bedzie chcial wypelnic, z gotowymi wartosciami do skopiowania. Idz po kolei, sekcja po sekcji.

---

## SEKCJA 1: App Information (juz wypelnione, ale tu kompletny zestaw)

### Localizable Information (English U.S.) — primary

| Pole | Wartosc do skopiowania |
| --- | --- |
| **Name** | `ProbWin AI: Football Stats` |
| **Subtitle** | `Match analysis with AI insight` |
| **Privacy Policy URL** | `https://[twoj-github-user].github.io/probwinai/` |

### Localizable Information (Polish — opcjonalna lokalizacja)

W App Store Connect dodaj polski jezyk: Edit -> Localizations -> "+" -> Polish.

| Pole PL | Wartosc |
| --- | --- |
| **Name** | `ProbWin AI: Statystyki Pilki` |
| **Subtitle** | `Analiza meczow ze sztuczna inteligencja` |

### General Information

| Pole | Wartosc |
| --- | --- |
| **Bundle ID** | `com.probwinai.app` (juz zarejestrowany) |
| **SKU** | `probwinai-ios-001` (juz wpisany przy tworzeniu) |
| **Primary Category** | `Sports` |
| **Secondary Category** | `Reference` |
| **Content Rights** | "Does not contain, show, or access third-party content" |
| **Age Rating** | 17+ (wynik ankiety - patrz nizej) |

### Age Rating questionnaire

Otworz Edit obok Age Rating, odpowiedz:

| Pytanie | Odpowiedz |
| --- | --- |
| Cartoon or Fantasy Violence | None |
| Realistic Violence | None |
| Prolonged Graphic or Sadistic Realistic Violence | None |
| Profanity or Crude Humor | None |
| Mature/Suggestive Themes | None |
| Horror/Fear Themes | None |
| Medical/Treatment Information | None |
| Alcohol, Tobacco, or Drug Use or References | None |
| **Simulated Gambling** | **Yes** |
| **Contests** | None |
| Sexual Content or Nudity | None |
| Graphic Sexual Content and Nudity | None |
| Unrestricted Web Access | No |

Drugi panel:
- "Made for Kids" -> **No**

Final rating: **17+** (Apple automatycznie wymusi to przez Simulated Gambling).

---

## SEKCJA 2: Pricing and Availability

| Pole | Wartosc |
| --- | --- |
| **Price** | Free |
| **Availability** | Poland, United Kingdom, United States, Germany, Canada, Australia |

> NIE udostepniaj w: UAE, Saudi Arabia, Pakistan, Bangladesh, Indonesia (zakazy hazardu).

### Volume Purchase Program (VPP)
- Nie zaznaczaj (nie sprzedajemy do firm).

### Discoverability
- "Available" - default

---

## SEKCJA 3: App Privacy

Klik **Get Started** -> **Edit** -> odpowiadasz:

**Pytanie:** "Do you or your third-party partners collect data from this app?"

**Odpowiedz:** **No, we do not collect data from this app.**

To wszystko - **Publish**.

---

## SEKCJA 4: Version Information (1.0) - to wypelniasz dopiero PO uploadzie buildu z Codemagic

### Promotional Text (max 170 chars, MOZNA ZMIENIAC bez re-submission!)

```text
Daily top 10 football matches with statistical probabilities and AI commentary. Understand bookmaker odds through transparent analytics. No bets, just insights.
```

(159 znakow)

### Description (max 4000 chars)

```text
ProbWin AI is an analytical tool for football fans that shows the top 10 most important matches each day, with detailed statistics and AI-generated commentary.

WHAT THE APP SHOWS
==================

For each match:

* Elo ratings for both teams (source: Clubelo.com)
* Form over the last 5 matches (W/D/L)
* Goal statistics (scored/conceded, averages)
* H2H - recent head-to-head results
* Bookmaker odds (1/X/2) from public aggregators
* Mathematical probabilities computed by Elo model
* AI commentary in plain language - context, injuries, motivation

NOT A BETTING ADVISOR
=====================

ProbWin AI is NOT a betting advisor. We don't promise profits. The app is an informational tool for people who want to better understand football.

Validation on 3 Premier League seasons showed that public statistical data alone (Elo, form, H2H) is insufficient to beat the bookmaker. Bookmakers have an informational advantage (injuries, lineups, sharp money). We display the math transparently so you can interpret it yourself.

FEATURES
========

* Daily refresh of top 10 matches from major leagues (Premier League, La Liga, Bundesliga, Serie A, Ligue 1)
* Detailed match card with statistics and AI commentary
* Model vs bookmaker probability comparison
* Dark mode for evening analysis
* Offline cache - last fetched matches available without internet
* No ads, no betting push notifications, no bookmaker affiliations

RESPONSIBLE PLAY
================

The app is for users 18+. Age verification required at first launch. If you bet, do so responsibly. Free help (Poland): 801 199 990. International: www.begambleaware.org

The app does NOT accept bets, does NOT process payments, is NOT affiliated with any specific bookmaker. Bookmaker odds are sourced from public data aggregators.

PRIVACY
=======

We collect zero personal data. No accounts, no login, no tracking. All settings stored locally on your device.

SUPPORTED LEAGUES
=================

Premier League (England), La Liga (Spain), Bundesliga (Germany), Serie A (Italy), Ligue 1 (France).

CONTACT
=======

Email: [twoj-email]
```

### Keywords (max 100 chars, comma-separated, BEZ SPACJI po przecinku!)

```text
football,soccer,stats,probability,ai,analysis,fixtures,elo,odds,premierleague,laliga,bundesliga
```

(99 znakow - max precyzyjnie)

> WAZNE: Bez spacji po przecinkach. Apple kazdy znak liczy.

### Support URL

```text
https://[twoj-github-user].github.io/probwinai/
```

(Wystarczy ze privacy/terms strona ma sekcje "Kontakt" - to wystarczy jako support URL)

### Marketing URL (opcjonalne)

```text
https://[twoj-github-user].github.io/probwinai/
```

### Version

```text
1.0
```

### Copyright

```text
2026 [Twoje imie/nazwa firmy]
```

Przyklad:
- `2026 Jan Kowalski` (jesli osoba fizyczna)
- `2026 ProbWin AI` (jesli marka)

### What's New (release notes dla 1.0)

```text
First release of ProbWin AI.

* Top 10 daily football matches across major European leagues
* Mathematical probability calculations using Elo ratings
* AI-generated match commentary in plain language
* Bookmaker odds comparison
* Team form and head-to-head history
* Dark mode interface
```

---

## SEKCJA 5: Screenshots (1290x2796 iPhone 6.7")

Apple wymaga **co najmniej 3 screenshoty** dla iPhone 6.7" (iPhone 15 Pro Max).
Mozna wgrac do **10 screenshotow** maksymalnie.

W folderze `store_listing/screenshots/` masz 6 gotowych SVG. Otwierasz w przegladarce, robisz screenshot, uploadujesz.

Konwersja SVG -> PNG:
1. Otworz `store_listing/screenshots/preview.html` w przegladarce Chrome
2. DevTools (F12) -> przelacz na Device Mode (Ctrl+Shift+M)
3. Custom resolution: 1290 x 2796
4. Dla kazdego screenu: Ctrl+Shift+P -> "Capture full size screenshot"
5. PNG zapisuje sie automatycznie

Alternatywnie online: <https://cloudconvert.com/svg-to-png> (uploadnij SVG, pobierz PNG).

**6 screenshotow gotowych:**

1. `01_welcome.svg` - ekran powitalny (responsible gambling)
2. `02_match_list.svg` - lista top 10 meczow
3. `03_match_detail_ai.svg` - karta meczu z AI komentarzem (kluczowa)
4. `04_match_detail_probability.svg` - paski prawdopodobienstw
5. `05_match_detail_teams.svg` - druzyny i forma
6. `06_match_detail_h2h.svg` - historia H2H

Wybierz 3-5 najlepszych (rekomenduje: 01, 02, 03, 04, 05).

### Kolejnosc na liscie sklepu (drag-and-drop w App Store Connect)

App Store wyswietla screenshoty w kolejnosci ktora ustawisz. Sugeruje:

1. **02_match_list** - hook (uzytkownik widzi co dostanie)
2. **03_match_detail_ai** - kluczowa wartosc (AI commentary)
3. **04_match_detail_probability** - tech wow (model vs bookmaker)
4. **05_match_detail_teams** - statystyki
5. **01_welcome** - na koniec, pokazuje compliance/responsible gambling

---

## SEKCJA 6: App Review Information

Wypelnij PRZED submission. To pole jest **prywatne** - widzi tylko Apple reviewer.

### Sign-In Required

- **No** (aplikacja nie ma logowania)

### Contact Information

| Pole | Wartosc |
| --- | --- |
| **First Name** | [Twoje imie] |
| **Last Name** | [Twoje nazwisko] |
| **Phone Number** | [Twoj telefon z prefiksem, np. +48 600 000 000] |
| **Email** | [Twoj email] |

> Apple **moze zadzwonic** w sprawie gambling-related app. Daj realny numer.

### Notes for review (KRYTYCZNE dla naszej aplikacji)

Skopiuj i wklej dokladnie:

```text
ProbWin AI is an INFORMATIONAL sport statistics application. It does NOT:
- Accept real-money bets or any form of wagering
- Process payments or in-app purchases
- Connect to any specific bookmaker as an affiliate or partner
- Recommend specific bets, betting strategies, or outcomes

The app displays publicly available bookmaker odds (aggregated by the-odds-api.com)
alongside our own mathematical probability model based on Elo ratings.
This comparison is purely educational - users see the math, draw their own
conclusions.

KEY POINTS:
- No betting functionality whatsoever
- No "place bet" buttons or similar
- No real-money transactions
- App is for users 18+ with age verification at first launch
- Privacy policy and terms accessible at first launch
- Gambling helpline (Poland: 801 199 990) prominently linked

We comply with Apple Guideline 5.3 (Gaming, Gambling, and Lotteries):
- The app is not a gambling product
- 17+ age rating selected (because we display bookmaker odds as information)
- We do not have a gambling license because we are NOT a gambling operator

The Welcome screen at first launch displays:
1. App description (statistical/informational)
2. Disclaimer that the app is NOT a betting advisor
3. Responsible gambling warning with helpline tel link
4. Age 18+ confirmation checkbox
5. Terms acceptance checkbox

Demo account: not required (app has no login).

For any questions about the app's compliance, please contact:
[twoj-email]

Thank you for reviewing.
```

### Attachment

Opcjonalne. Mozesz uploadnac:
- Demo video aplikacji (max 30s, mp4)
- PDF z opisem feature

NIE jest wymagane. Skip jesli nie masz.

---

## SEKCJA 7: General App Information (gornajZakladka "App Information")

Te pola sa **tylko raz** dla calej aplikacji (nie per-wersja):

| Pole | Wartosc |
| --- | --- |
| **Name** | `ProbWin AI: Football Stats` (juz wpisane) |
| **Subtitle** | `Match analysis with AI insight` |
| **Primary Language** | English (U.S.) |
| **Privacy Policy URL** | `https://[user].github.io/probwinai/` |
| **Bundle ID** | `com.probwinai.app` (read-only po stworzeniu) |
| **SKU** | `probwinai-ios-001` (read-only) |
| **Primary Category** | Sports |
| **Secondary Category** | Reference |

---

## SEKCJA 8: Build (czeka na Codemagic)

Po pierwszym buildzie z Codemagic do TestFlight, w App Store Connect -> 1.0 Prepare for Submission -> Build -> "+" -> wybierz `0.1.0 (101)`.

### Export Compliance Information

Apple zapyta o uzycie kryptografii. Odpowiedzi:

| Pytanie | Odpowiedz |
| --- | --- |
| Does your app use encryption? | **No** *(uzywamy tylko HTTPS standardowego, ktory jest exempt)* |

Lub jesli zaznaczysz "Yes":
- "Does your app use any of the following non-exempt encryption?" -> No
- Nie wymaga uploadu kluczowych dokumentow (CCATS).

### Content Rights

- "Does this app use third-party content?" -> **No** *(uzywamy publicznych API, NIE ma tutaj problemu)*

### Advertising Identifier (IDFA)

- "Does this app use the Advertising Identifier (IDFA)?" -> **No**

---

## SEKCJA 9: Version Release

Po wszystkich powyzszych:

| Pole | Wartosc |
| --- | --- |
| **Release** | **Manually release this version** *(zalecane - sam decydujesz kiedy aplikacja idzie do sklepu po approve)* |
| **Phased Release** | **Release at the same time** *(MVP, ale dla v2 mozesz przelaczyc na 7-day phased)* |

---

## FINAL CHECKLIST przed kliknieciem "Submit for Review"

- [ ] App Information: Name, Subtitle, Privacy URL, Category, Age Rating wypelnione
- [ ] Pricing: Free, country list ustawiona (bez UAE/SA/PK/BD/ID)
- [ ] App Privacy: "Do not collect data" submitted
- [ ] Version 1.0: Promotional, Description, Keywords, Support URL wypelnione
- [ ] Copyright wypelniony (`2026 [imie]`)
- [ ] Screenshots: minimum 3 dla iPhone 6.7", uploadnięte w dobrej kolejnosci
- [ ] What's New (release notes) wypelnione
- [ ] App Review Information: contact + notes (BARDZO DLUGIE notes dla gambling!)
- [ ] Build wybrany z TestFlight
- [ ] Export Compliance: No encryption
- [ ] Content Rights: No third-party content
- [ ] IDFA: Not used
- [ ] Release: Manual

Po wszystkim klikasz **Submit for Review**.

Status zmienia sie na **Waiting for Review**, potem **In Review**, potem albo:
- **Pending Developer Release** (approved! Ty decydujesz kiedy "release")
- **Rejected** (Apple ma uwagi - odpowiedz w Resolution Center)
