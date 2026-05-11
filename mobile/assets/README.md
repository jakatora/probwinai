# Assets — ikony i grafiki

Folder zawiera SVG placeholdery. **Przed publikacja zamien na finalne PNG.**

## Wymagane pliki

| Plik | Format | Wymiary | Cel |
| --- | --- | --- | --- |
| `icon.png` | PNG | 1024x1024 | Glowna ikona aplikacji |
| `icon_foreground.png` | PNG | 1024x1024 | Adaptive icon foreground (Android 8+), centralne 60% to bezpieczna strefa |
| `splash.png` | PNG | 1152x1152 | Splash screen (centrowane, przezroczyste tlo) |
| `feature_graphic.png` | PNG | 1024x500 | Google Play feature graphic (gora listingu) |

## Generowanie z SVG

Najszybsza droga:

1. Otworz `icon.svg` w Inkscape / Figma / Photoshop
2. Wyeksportuj jako PNG 1024x1024
3. Zapisz jako `icon.png` w tym folderze
4. Powtorz dla pozostalych plikow

Lub uzyj online narzedzia: <https://realfavicongenerator.net/svg>

## Generowanie wersji na rozne rozdzielczosci

Po dostarczeniu `icon.png` 1024x1024, uruchom z folderu `mobile/`:

```bash
flutter pub get
flutter pub run flutter_launcher_icons
flutter pub run flutter_native_splash:create
```

To wygeneruje wszystkie warianty (mipmap-mdpi, hdpi, xhdpi, xxhdpi, xxxhdpi
dla Android + AppIcon.appiconset dla iOS).
