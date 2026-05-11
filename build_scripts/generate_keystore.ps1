# PowerShell: generuje keystore do podpisywania release builds Android.
# UZYWAJ TYLKO RAZ. Wynikowy plik probwinai-release.keystore i hasla
# musisz przechowywac BEZPIECZNIE (np. password manager, NIE w repo).
#
# Wymaga: Java JDK zainstalowany (keytool w PATH).

$ErrorActionPreference = "Stop"

$KEYSTORE_PATH = "$PSScriptRoot/../mobile/android/probwinai-release.keystore"
$KEY_ALIAS = "probwinai"
$VALIDITY_YEARS = 25  # 25 lat = wymog Google Play (min 2030+ wedlug aktualnych zasad)

if (Test-Path $KEYSTORE_PATH) {
    Write-Host "[!] Keystore juz istnieje: $KEYSTORE_PATH"
    Write-Host "    Jesli chcesz wygenerowac nowy, usun najpierw poprzedni."
    Write-Host "    UWAGA: NOWY KEYSTORE = TWOJA APLIKACJA W SKLEPIE STANIE SIE 'NOWA' (brak update'u istniejacej)!"
    exit 1
}

# Wymus podanie hasla (interaktywnie, hidden)
Write-Host "Generuje keystore: $KEYSTORE_PATH"
Write-Host "Podaj haslo do keystore (min 6 znakow):"
$keystorePass = Read-Host -AsSecureString
$keystorePassPlain = [System.Net.NetworkCredential]::new("", $keystorePass).Password

Write-Host "Podaj haslo do klucza (zwykle to samo co keystore):"
$keyPass = Read-Host -AsSecureString
$keyPassPlain = [System.Net.NetworkCredential]::new("", $keyPass).Password

if ($keystorePassPlain.Length -lt 6 -or $keyPassPlain.Length -lt 6) {
    Write-Host "[X] Haslo musi miec min 6 znakow"
    exit 1
}

# Dane do certyfikatu (mozesz dac fake jesli nie chcesz ujawniac swoich danych)
Write-Host "Podaj dane do certyfikatu (mozna kropki):"
$cn = Read-Host "Imie i nazwisko / nazwa firmy"
$ou = Read-Host "Jednostka organizacyjna (np. ProbWin AI Team)"
$o = Read-Host "Organizacja (np. ProbWin AI)"
$l = Read-Host "Miasto"
$st = Read-Host "Wojewodztwo / region"
$c = Read-Host "Kod kraju (2 litery, np. PL)"

$dname = "CN=$cn, OU=$ou, O=$o, L=$l, ST=$st, C=$c"

& keytool -genkey -v `
    -keystore $KEYSTORE_PATH `
    -alias $KEY_ALIAS `
    -keyalg RSA `
    -keysize 2048 `
    -validity ($VALIDITY_YEARS * 365) `
    -storepass $keystorePassPlain `
    -keypass $keyPassPlain `
    -dname $dname

if ($LASTEXITCODE -ne 0) {
    Write-Host "[X] keytool fail. Sprawdz czy Java JDK zainstalowane."
    exit 1
}

# Stworz key.properties dla Gradle (gitignored!)
$keyProps = @"
storePassword=$keystorePassPlain
keyPassword=$keyPassPlain
keyAlias=$KEY_ALIAS
storeFile=$([System.IO.Path]::GetFileName($KEYSTORE_PATH))
"@

$keyPropsPath = "$PSScriptRoot/../mobile/android/key.properties"
Set-Content -Path $keyPropsPath -Value $keyProps -Encoding UTF8

Write-Host ""
Write-Host "[OK] Keystore wygenerowany: $KEYSTORE_PATH"
Write-Host "[OK] key.properties zapisany: $keyPropsPath"
Write-Host ""
Write-Host "WAZNE:"
Write-Host "  1. Zapisz haslo w password managerze (Bitwarden, 1Password)"
Write-Host "  2. Zachowaj BACKUP pliku keystore (np. szyfrowany dysk, USB)"
Write-Host "  3. Jesli zgubisz keystore - NIE BEDZIESZ MOGL aktualizowac aplikacji w Google Play!"
Write-Host "  4. NIGDY nie commituj keystore ani key.properties do gita"
Write-Host ""
Write-Host "Sprawdz .gitignore - powinien zawierac:"
Write-Host "  mobile/android/key.properties"
Write-Host "  mobile/android/*.keystore"
