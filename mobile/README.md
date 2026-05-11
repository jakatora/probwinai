# ProbWin AI - mobile app

Flutter app dla iOS i Android. Wyswietla codzienne top 10 meczow z prawdopodobienstwami modelu, kursami bukmacherskimi i komentarzem AI.

## Wymagania

- Flutter SDK >= 3.3 ([instrukcja instalacji](https://docs.flutter.dev/get-started/install))
- Backend ProbWin AI uruchomiony (`uvicorn backend.main:app --port 8000` w katalogu rodzicielskim)

## Setup

```bash
# 1. Zainstaluj zaleznosci
flutter pub get

# 2. Sprawdz srodowisko
flutter doctor

# 3. Uruchom (emulator/symulator/telefon)
flutter run
```

## Konfiguracja URL serwera

Domyslnie aplikacja laczy sie z `http://10.0.2.2:8000` (Android emulator -> localhost komputera).

Inne scenariusze:
- **iOS Simulator:** `http://localhost:8000`
- **Telefon fizyczny w tej samej sieci:** `http://192.168.1.X:8000` (IP komputera)
- **Produkcja:** publiczny URL backendu

URL mozesz zmienic w aplikacji: Ustawienia -> Adres serwera API.

## Architektura

```
lib/
├── main.dart              # entrypoint
├── theme.dart             # kolory, ThemeData
├── api/
│   └── api_client.dart    # HTTP client do FastAPI backendu
├── models/
│   └── match.dart         # data classes (Match, MatchInsights, ...)
├── screens/
│   ├── home_screen.dart           # lista top 10 meczow
│   ├── match_detail_screen.dart   # pelna karta meczu z AI
│   └── settings_screen.dart       # ustawienia / manualny refresh
└── widgets/
    ├── match_card.dart            # karta meczu na liscie
    ├── probability_bar.dart       # pasek prawdopodobienstwa (model vs bukm.)
    └── form_indicator.dart        # kropki formy ostatnich meczow
```

## Budowanie release-owe

```bash
# Android APK
flutter build apk --release

# Android App Bundle (do Google Play)
flutter build appbundle --release

# iOS (wymaga macOS + Xcode)
flutter build ios --release
```
