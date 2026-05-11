# PowerShell: buduje release Android Bundle (AAB) gotowy do uploadu w Google Play.
# Wymagania:
#   - Flutter SDK w PATH
#   - Android SDK + akceptowane licencje (flutter doctor)
#   - keystore + key.properties wygenerowane przez generate_keystore.ps1

$ErrorActionPreference = "Stop"

Push-Location "$PSScriptRoot/.."

try {
    Write-Host "=== ProbWin AI - Android Release Build ==="
    Write-Host ""

    # Sprawdz wymagania
    if (-not (Test-Path "mobile/android/key.properties")) {
        Write-Host "[X] Brak mobile/android/key.properties"
        Write-Host "    Uruchom najpierw: build_scripts/generate_keystore.ps1"
        exit 1
    }

    Push-Location mobile

    Write-Host "[1/4] flutter pub get..."
    & flutter pub get
    if ($LASTEXITCODE -ne 0) { throw "flutter pub get failed" }

    Write-Host "[2/4] Generuje ikony (jesli sa assety)..."
    if (Test-Path "assets/icon.png") {
        & flutter pub run flutter_launcher_icons
    } else {
        Write-Host "    Brak assets/icon.png - pomijam (uzupelnij przed publikacja!)"
    }

    # Odczytaj API_URL z .env lub uzyj domyslnego
    $apiUrl = $env:PROBWIN_API_URL
    if (-not $apiUrl) {
        $apiUrl = "https://probwinai-api.up.railway.app"  # podmien na swoj produkcyjny URL
        Write-Host "    [i] Brak PROBWIN_API_URL w env - uzywam default: $apiUrl"
        Write-Host "    [i] Aby zmienic: `$env:PROBWIN_API_URL=`"https://twoj-api.com`""
    } else {
        Write-Host "    API_URL: $apiUrl"
    }

    Write-Host "[3/4] flutter clean + build appbundle..."
    & flutter clean
    & flutter build appbundle --release --dart-define=API_URL=$apiUrl
    if ($LASTEXITCODE -ne 0) { throw "flutter build failed" }

    $aab = "build/app/outputs/bundle/release/app-release.aab"
    if (-not (Test-Path $aab)) {
        throw "AAB nie zostal utworzony: $aab"
    }

    $sizeKB = (Get-Item $aab).Length / 1024
    Write-Host ""
    Write-Host "[OK] AAB zbudowany: mobile/$aab"
    Write-Host "     Rozmiar: $([math]::Round($sizeKB, 1)) KB"
    Write-Host ""
    Write-Host "Nastepny krok:"
    Write-Host "  1. Zaloguj sie do Google Play Console: https://play.google.com/console"
    Write-Host "  2. Utworz nowa aplikacje (lub wybierz istniejaca)"
    Write-Host "  3. Production -> Create new release -> Upload AAB"
    Write-Host "  4. Wypelnij Release Notes (co nowego w tej wersji)"
    Write-Host "  5. Rollout -> Submit for review"

} finally {
    Pop-Location
    Pop-Location
}
