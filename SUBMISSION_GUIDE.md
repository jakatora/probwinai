# Publikacja ProbWin AI w sklepach - przewodnik krok po kroku

Wszystko co przygotowalem jest gotowe. Teraz **Ty** musisz wykonac kroki ktorych
nie mozna zautomatyzowac (konta, platnosci, screenshoty z urzadzenia, decyzje
biznesowe).

## Faza 0: Wymagania wstepne

### 0.1. Zainstaluj Flutter SDK

1. Pobierz: <https://docs.flutter.dev/get-started/install/windows>
2. Rozpakuj do `C:\flutter` (lub innej sciezki bez spacji)
3. Dodaj `C:\flutter\bin` do PATH
4. Sprawdz:

```powershell
flutter --version
flutter doctor
```

`flutter doctor` powie ci czego brakuje. Musisz miec:

- Flutter SDK ✓
- Android toolchain (Android Studio z SDK) - **POBIERZ jesli nie masz**
- Visual Studio Build Tools / Visual Studio Community (opcjonalne)
- Chrome dla testow web (opcjonalne)

### 0.2. Zainstaluj Android Studio

<https://developer.android.com/studio>

W Android Studio:

1. Tools -> SDK Manager
2. Zainstaluj Android SDK 34 (target)
3. Zainstaluj Build-tools 34.0.0
4. Zaakceptuj wszystkie licencje:

```powershell
flutter doctor --android-licenses
```

(naciskaj `y` aby zaakceptowac kazdą licencje)

### 0.3. Utworz local.properties dla Flutter

Plik `mobile/android/local.properties`:

```properties
sdk.dir=C:\\Users\\Startklaar\\AppData\\Local\\Android\\Sdk
flutter.sdk=C:\\flutter
flutter.versionName=0.1.0
flutter.versionCode=1
```

Dostosuj sciezki do swojej instalacji.

---

## Faza 1: Google Play - przygotowanie aplikacji

### 1.1. Stworz ikony aplikacji

Ja zostawilem placeholder `mobile/assets/icon.svg`. Musisz wyeksportowac do PNG:

**Wariant A (latwy):** uzyj generatora online <https://www.appicon.co/>

1. Wgraj swoja grafike 1024x1024 PNG (cokolwiek z ProbWin AI)
2. Wybierz "iOS + Android"
3. Pobierz ZIP
4. Skopiuj iconset do `mobile/android/app/src/main/res/` i `mobile/ios/Runner/Assets.xcassets/`

**Wariant B (przez pakiet flutter_launcher_icons):**

1. Wyeksportuj `icon.svg` jako PNG 1024x1024
2. Zapisz jako `mobile/assets/icon.png`
3. Z folderu `mobile/`:

```powershell
flutter pub get
flutter pub run flutter_launcher_icons
flutter pub run flutter_native_splash:create
```

To wygeneruje wszystkie warianty automatycznie.

### 1.2. Wygeneruj keystore

W PowerShellu, z folderu projektu:

```powershell
./build_scripts/generate_keystore.ps1
```

Skrypt zapyta o hasla i dane do certyfikatu. **ZAPISZ HASLA W PASSWORD MANAGER**.

Po wykonaniu masz:

- `mobile/android/probwinai-release.keystore` - keystore do podpisywania
- `mobile/android/key.properties` - haslo (gitignored)

**KRYTYCZNE:** zrob backup `probwinai-release.keystore` na zewnetrznym dysku/USB. Bez tego pliku **nie da sie aktualizowac aplikacji w Google Play** (Google nie pozwala zmienic klucza dla istniejacej aplikacji).

### 1.3. Zbuduj release AAB

```powershell
./build_scripts/build_android_release.ps1
```

Po sukcesie masz: `mobile/build/app/outputs/bundle/release/app-release.aab`

### 1.4. Testuj lokalnie przed uploadem

```powershell
# Zainstaluj APK na podlaczonym telefonie / emulatorze
cd mobile
flutter install --release
```

Sprawdz:

- [ ] Welcome screen sie wyswietla przy pierwszym uruchomieniu
- [ ] Lista meczow ladowanie OK (po wczesniejszym uruchomieniu `py scripts/seed_demo.py` na serwerze)
- [ ] Karta meczu otwiera sie OK
- [ ] Settings -> URL serwera dziala
- [ ] Nawigacja wstecz dziala
- [ ] Dark mode wyglada OK

---

## Faza 2: Google Play - konto i submission

### 2.1. Stworz konto Google Play Console

1. Idz na <https://play.google.com/console>
2. Zaloguj sie kontem Google (najlepiej dedykowane konto firmowe)
3. Zaplacz **$25 jednorazowo**
4. Wypelnij dane (typ konta: Personal / Organization)
5. Czekaj na weryfikacje konta (zwykle 1-2 dni, czasem dluzej)

### 2.2. Stworz aplikacje w Console

1. Kliknij "Create app"
2. Nazwa: **ProbWin AI: Statystyki Pilki**
3. Default language: Polski (PL)
4. App or game: **App**
5. Free or paid: **Free**
6. Zaznacz wszystkie deklaracje (Developer Program Policies, US export laws)

### 2.3. Skonfiguruj listing

W "Main store listing":

1. Wklej teksty z `store_listing/google_play_PL.md`
2. Upload graphics:
   - **App icon**: 512x512 PNG
   - **Feature graphic**: 1024x500 PNG
   - **Screenshots**: 4-5 sztuk, 1080x1920 px (telefon)

### 2.4. Stworz strone polityki prywatnosci

1. Stworz repo GitHub (np. `probwinai`)
2. Stworz folder `docs/` w repo
3. Skopiuj `legal/index.html` do `docs/index.html`
4. **WYPELNIJ wszystkie `[placeholder]`** w `index.html` (email, adres, etc.)
5. Push do GitHub
6. Settings -> Pages -> Source: Deploy from branch: main, Folder: /docs
7. Po kilku minutach masz URL: `https://[twoj-user].github.io/probwinai/`
8. Wklej ten URL w Google Play Console: App content -> Privacy policy

### 2.5. Wypelnij obowiazkowe sekcje "App content"

W Google Play Console:

#### Ads

- "Does your app contain ads?" -> **No**

#### App access

- "Is all app functionality available without restrictions?" -> **Yes**

#### Content rating

- Wypelnij ankiete (Sport, brak przemocy, brak seksualnych tresci)
- Zaznacz **"References to gambling"** = TAK (kursy bukmacherskie)
- Wynik: **PEGI 16-18** lub **ESRB Teen-Mature**

#### Target audience

- Wiek docelowy: **18+ (Adults only)**
- Czy aplikacja jest celowo adresowana do dzieci? **No**

#### Data safety

Wypelnij wedlug specyfikacji w `store_listing/google_play_PL.md`:

- **Personal info / Financial / Location / etc.**: NO data collected
- **Data sharing**: NO sharing

Najprostszy mozliwy przypadek - "Aplikacja nie zbiera ani nie udostepnia danych uzytkownika".

#### Government apps

- Czy aplikacja jest tworzona dla rzadu? **No**

#### Financial features

- Czy aplikacja oferuje uslugi finansowe? **No**

#### Health

- Czy aplikacja zbiera dane zdrowotne? **No**

#### News

- Czy aplikacja jest aplikacja newsową? **No**

### 2.6. Upload AAB

1. **Production** -> "Create new release"
2. Upload `mobile/build/app/outputs/bundle/release/app-release.aab`
3. Release name: `0.1.0 - Initial release`
4. Release notes (po polsku):

```text
Pierwsze wydanie ProbWin AI.

Funkcje:
- Top 10 najwazniejszych meczow dnia z najwiekszych lig
- Statystyczne prawdopodobienstwa wynikow
- Komentarz AI dla kazdego meczu
- Forma druzyn i historia H2H
- Porownanie modelu z kursem bukmachera
- Dark mode
```

5. Kliknij **Review release**
6. Sprawdz wszystkie ostrzezenia (musisz miec 0 errors, mozesz miec warnings)
7. **Start rollout to Production**

### 2.7. Czekaj na review

- Pierwsze submission: zwykle **1-3 dni**
- Mozliwe pytania od Google review team -> odpowiadaj szybko
- Po akceptacji: aplikacja idzie do sklepu (proces "Available on Google Play" po dodatkowych kilku godzinach)

### 2.8. Jesli review odmowi

Najczestsze powody dla naszej aplikacji:

1. **"Gambling app without license"** -> odpowiedz: "App does not accept bets, does not process payments, does not connect to any specific bookmaker. It's an informational analytics tool. Reference: Policy 5.1 paragraph 2."
2. **"Privacy policy URL inaccessible"** -> sprawdz czy GitHub Pages dziala (open w incognito)
3. **"Target API level too low"** -> upewnij sie targetSdk=34 (obecny min Google)
4. **"App crashes on launch"** -> testuj na fizycznym urzadzeniu z roznymi wersjami Androida

Mozesz odpowiedziec na pytania review przez Console -> Policy Center.

---

## Faza 3: App Store (po sukcesie Google Play)

### 3.1. Konto Apple Developer

1. Idz na <https://developer.apple.com/programs/>
2. Stworz Apple ID (jesli nie masz)
3. Wlacz 2-factor authentication (wymagane)
4. Zaplaczyc **$99/rok**
5. Weryfikacja konta: 1-2 dni, czasem wiecej

### 3.2. Codemagic CI setup

Skoro nie masz Mac, uzyjemy Codemagic do buildowania iOS:

1. Stworz konto: <https://codemagic.io>
2. Podlacz repo GitHub
3. W Codemagic Apps -> Settings:
   - **App Store Connect Integration**: dodaj App Store Connect API key
   - **Code Signing**: pozwol Codemagic zarzadzac certyfikatami (najlatwiej)
4. Push do brancha `main` -> Codemagic automatycznie buduje iOS przez `codemagic.yaml`

### 3.3. Stworz aplikacje w App Store Connect

1. Idz na <https://appstoreconnect.apple.com>
2. My Apps -> "+" -> New App
3. Platforma: **iOS**
4. Nazwa: **ProbWin AI: Football Stats**
5. Bundle ID: **com.probwinai.app** (musi byc zarejestrowany w developer.apple.com -> Certificates)
6. SKU: **probwinai-001** (dowolne unikalne)
7. User Access: Full Access

### 3.4. Skonfiguruj listing

Wklej teksty z `store_listing/app_store_EN.md`:

- Name, Subtitle, Promotional Text, Description, Keywords
- Support URL, Marketing URL, Privacy Policy URL
- Screenshots (z symulatora iPhone 15 Pro Max - flutter run w simulatorze, potem cmd+s)
- Age rating: **17+** (gambling references)
- Category: **Sports**

### 3.5. Upload binarki przez Codemagic

Po pierwszym buildzie Codemagic automatycznie wrzuca IPA do TestFlight.

### 3.6. TestFlight beta

1. W App Store Connect -> TestFlight
2. Internal Testing -> zapros siebie (Apple ID)
3. Pobierz TestFlight app na iPhone, otworz, zaakceptuj zaproszenie
4. Testuj aplikacje na prawdziwym urzadzeniu

### 3.7. Submit for review

1. App Store Connect -> wybierz wersje (0.1.0)
2. Wybierz build (z TestFlight)
3. Wypelnij "App Review Information":
   - Email + telefon do reviewera
   - **Notes for review**: wklej tekst z `store_listing/app_store_EN.md` (sekcja Submission notes)
4. Submit for review

### 3.8. Czekaj

- Apple review: **1-7 dni** (czasem dluzej)
- Spodziewaj sie pytan od review team o nature aplikacji (gambling)
- Odpowiadaj szybko i precyzyjnie

---

## Faza 4: Po publikacji

### Monitoring

- Google Play Console -> Statistics, Crashes, Reviews
- App Store Connect -> Analytics, Customer Reviews
- Odpowiadaj na recenzje (zwlaszcza negatywne)

### Aktualizacje

Co miesiac releasujesz nowa wersje z poprawkami:

```powershell
# Zaktualizuj wersje w pubspec.yaml:
# version: 0.2.0+2

# Build
./build_scripts/build_android_release.ps1

# Upload do Google Play (Production -> Create release)
# Codemagic automatycznie zbuduje iOS po pushu do main
```

### Ważne metryki do sledzenia

- Conversion rate (instalacje / impressions)
- Crash-free users %
- Retention D1 / D7 / D30
- Rating sredni (utrzymaj >4.0)

---

## Checklist FINAL przed kazdym uploadem

Przed kazdym submission:

- [ ] Wszystkie [placeholder] zastapione (email, adres, URL)
- [ ] Privacy policy URL dziala (sprawdz w przegladarce incognito)
- [ ] Ikona aplikacji wygenerowana (nie placeholder)
- [ ] AAB/IPA testowany na fizycznym urzadzeniu
- [ ] Screenshoty zaktualizowane (5 sztuk minimum)
- [ ] Release notes wypelnione
- [ ] Version code zwiekszony (kazdy upload musi miec wyzszy)
- [ ] Backup keystore na zewnetrznym dysku

---

## Rozwiazywanie problemow

### "Flutter doctor pokazuje X errors"

Najczestsze:

- **No Android SDK** -> zainstaluj Android Studio
- **Android licenses not accepted** -> `flutter doctor --android-licenses`
- **Chrome not found** -> ignorujesz (tylko dla web buildow)

### "AAB upload nie przechodzi w Google Play"

- Sprawdz czy targetSdk = 34
- Sprawdz czy versionCode jest unikalny
- Sprawdz czy nie commitiowales keystore do repo

### "Apple review odrzucil aplikacje za gambling"

Najczesciej wymagaja:

1. Demo video pokazujace ze nie ma `Place bet` przycisku
2. Potwierdzenie ze nie ma in-app purchase
3. Dokladniejszy "Submission notes" wyjasniajacy ze to tool informacyjny

Mozesz odpowiedziec przez Resolution Center w App Store Connect.

---

## Kontakt podczas submission

Jesli utkniesz na jakimkolwiek kroku - wroc do mnie z dokladna trescia bledu/pytania review team. Wspolnie odpowiemy.

**Estymowany calkowity czas:** 2-4 tygodnie od dzis do aplikacji w obu sklepach.
