# Legal documents - ProbWin AI

Ten folder zawiera **gotowe dokumenty prawne** dla submission w Google Play / App Store.

## Pliki

| Plik | Cel |
| --- | --- |
| `index.html` | **PL+EN polityka prywatnosci + regulamin w 1 pliku** - do GitHub Pages |
| `privacy_pl.md` | Polityka prywatnosci PL (zrodlo Markdown) |
| `privacy_en.md` | Polityka prywatnosci EN |
| `terms_pl.md` | Regulamin PL |
| `terms_en.md` | Regulamin EN |

## Co MUSISZ uzupelnic przed publikacja

Wszystkie placeholdery `[...]` w plikach. Konkretnie:

- `[Imie i nazwisko / nazwa firmy]` - kto jest administratorem
- `[Adres]` - adres pocztowy (Google/Apple czesto pyta)
- `[Email kontaktowy]` lub `[kontakt@example.com]` - rzeczywisty email
- `[NIP]` w `terms_pl.md` - jesli prowadzisz dzialalnosc

W `index.html` zmien WSZYSTKIE wystapienia `[kontakt@example.com]` na rzeczywisty email.

## Jak opublikowac na GitHub Pages

### Wariant A: dedykowane repo

```bash
# 1. Stworz nowe repo GitHub: probwinai.github.io (uzytkownik) lub privacy-policy (project)
# 2. Skopiuj plik:
cp legal/index.html /sciezka/do/repo/index.html
# 3. Commit + push
cd /sciezka/do/repo
git add index.html
git commit -m "Add privacy policy and terms"
git push

# 4. W repo na GitHub: Settings -> Pages -> Source: Deploy from branch: main
# 5. URL bedzie: https://[twoj-username].github.io/[nazwa-repo]/
```

### Wariant B: katalog `docs/` w glownym repo aplikacji

```bash
# Skopiuj do docs/ w glownym repo
cp legal/index.html docs/index.html

# Wlacz GitHub Pages:
# Settings -> Pages -> Source: Deploy from branch: main, Folder: /docs
# URL: https://[username].github.io/[repo-name]/
```

## Co zaktualizowac w aplikacji po publikacji

Jak juz znasz URL polityki, zaktualizuj `mobile/lib/screens/welcome_screen.dart`:

```dart
() => _openUrl("https://[username].github.io/probwinai/")  // <-- TWOJ URL
```

I w `mobile/lib/screens/settings_screen.dart` dodaj link "Polityka prywatnosci".

## Wymagania Google Play

- Privacy policy URL **MUSI byc publicznie dostepny** w momencie submission (review tester sprawdza)
- Musi pokrywac dane zbierane przez aplikacje (u nas: zero osobistych)
- Musi byc w jezyku target market (PL dla Polski, EN dla USA, etc.)
- Plik HTML zalecany; PDF tez akceptowany ale gorzej

## Wymagania Apple App Store

- W App Store Connect: pole "Privacy Policy URL" jest wymagane
- Aplikacja musi miec **App Privacy Details** w listing (deklarujesz co zbierasz)
- Dla naszej aplikacji: **NIE zbieramy zadnych danych osobowych** (najprostszy przypadek)
