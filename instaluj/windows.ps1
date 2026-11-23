<#
.SYNOPSIS
  Instalator metody kuznia-kodu dla Windows (miniPC, laptop). Uruchamia Pawel. Agent Claude Code ten skrypt
  tylko pisze, nigdy go nie uruchamia. Wymaga Windows PowerShell 5.1 (powershell.exe), nie PowerShell 7.

.DESCRIPTION
  Kolejnosc zakladania projektu (METODA sekcja 10): NAJPIERW plugin, POTEM blokady.
    1. agent, w katalogu repo: claude plugin install kuznia@kuznia-kodu --scope project
       a potem: git checkout -- .claude/settings.json (instalator przestawia kolejnosc kluczy),
    2. Pawel: commit, push, git config core.hooksPath .githooks,
    3. Pawel (ten skrypt, jako administrator): -Repo <repo> (blokady), a raz na maszyne -InstalujKatalogProjektow,
    4. agent (zalogowany jako claude-agent): -TestAgenta.

  Tryby (dokladnie jeden naraz):
    (bez trybu)  INSTALACJA, wymaga administratora i parametru -Repo (jedno lub kilka repozytoriow). Bez -Repo
                 konczy sie komunikatem i niczego nie zmienia. Robi:
                 - sprawdza, czy istnieje konto agenta (NIE tworzy go),
                 - kopiuje szablon-uzytkownika do profilu agenta: .claude\CLAUDE.md (nadpisuje),
                   .claude\settings.json oraz profil PowerShell (tylko gdy ich brak),
                 - zmienia wlasciciela plikow kontrolnych repo na wlasciciela (Pawla) i zaklada blokady zapisu NTFS.
                 Katalog pluginu NIE jest blokowany: agent musi moc go aktualizowac, a obrona to wykrywanie zmian
                 (patrz -Sprawdz i -TestAgenta: porownanie skrotow z repo).
    -Sprawdz     tylko raport (konto wlasciciela, NICZEGO nie zmienia, administrator niepotrzebny; do odczytu
                 profilu agenta moze byc potrzebny): wlasciciele i blokady plikow kontrolnych, katalog projektow,
                 foldery w katalogu projektow bez blokady, zgodnosc pluginu w cache i CLAUDE.md agenta z repo.
    -InstalujKatalogProjektow  (administrator) wzorzec z Legiona: dziedziczony zakaz FullControl dla agenta na
                 katalogu projektow (tylko w dol, InheritOnly), zakaz zakladania czegokolwiek bezposrednio w nim,
                 oraz jawne Modify na katalogu repozytoriow (_repo), ktore wygrywa z odziedziczonym zakazem.
                 Kazdy nowy folder w katalogu projektow jest od razu zamkniety.
    -TestAgenta  test dostepu zalogowanego JAKO agent (niczego nie zmienia, nie pyta o haslo): whoami i przerwanie,
                 jesli to nie konto agenta, foldery na C:\ (poza lista dozwolonych), podfoldery katalogu projektow
                 (tylko _repo ma DOSTEP), deniedMcpServers w ustawieniach agenta, zapis w plikach kontrolnych
                 kazdego repo (ma byc odmowa), CRLF w plikach pluginu w cache, zgodnosc skrotow pluginu i
                 CLAUDE.md z repo oraz safe.directory dla repo (przy braku podaje gotowe polecenie).

  Blokady sa zakladane metoda .NET: GetAccessControl('Access') i SetAccessControl() na obiekcie pliku lub folderu,
  z jawna lista praw (bez SYNCHRONIZE i bez praw odczytu). Nie uzywamy Set-Acl (probuje zapisac tez wlasciciela)
  ani "icacls /deny" z prawami w nawiasie (taki wpis potrafi zablokowac tez odczyt). Do zmiany wlasciciela
  uzywany jest "icacls /setowner" (bez /deny). W icacls wpis (N) to PELNY zakaz, nie puste zezwolenie.
  Pliki kontrolne kazdego repo: .claude\, .githooks\, .git\config, .git\hooks\, tools\przeglad.py,
  tools\przeglad_konfig.py, tools\tests\test_settings.py.
  Blokada znika, gdy git zapisze plik od nowa (latka, pull, checkout): po kazdej takiej zmianie zaloz blokady ponownie
  i uruchom -TestAgenta.

.PARAMETER Agent             nazwa konta agenta (domyslnie claude-agent)
.PARAMETER Wlasciciel        konto wlasciciela plikow kontrolnych (domyslnie Belkot)
.PARAMETER KatalogProjektow  katalog z projektami (domyslnie C:\Projects)
.PARAMETER KatalogRepo       katalog z repozytoriami (domyslnie C:\Projects\_repo)
.PARAMETER Repo              repozytoria do zablokowania (WYMAGANE w instalacji); w -Sprawdz i -TestAgenta domyslnie
                             wszystkie podkatalogi KatalogRepo z .git
.PARAMETER Plugin            katalog cache pluginu (domyslnie <profil agenta>\.claude\plugins\cache\kuznia-kodu)
.PARAMETER DozwoloneFolderyC foldery na C:\, do ktorych agent ma miec dostep w -TestAgenta (reszta ma dac odmowe)
.PARAMETER Sprawdz           tylko raport (patrz wyzej)
.PARAMETER TestAgenta        test jako agent (patrz wyzej)
.PARAMETER InstalujKatalogProjektow  zamkniecie katalogu projektow (patrz wyzej)

.EXAMPLE
  powershell -ExecutionPolicy Bypass -File instaluj\windows.ps1 -Repo C:\Projects\_repo\kuznia-kodu     (administrator)
  powershell -ExecutionPolicy Bypass -File instaluj\windows.ps1 -InstalujKatalogProjektow                (administrator)
  powershell -ExecutionPolicy Bypass -File instaluj\windows.ps1 -Sprawdz
  powershell -ExecutionPolicy Bypass -File instaluj\windows.ps1 -TestAgenta                              (konto agenta)
#>
#requires -Version 5.1
[CmdletBinding()]
param(
    [string]$Agent = 'claude-agent',
    [string]$Wlasciciel = 'Belkot',
    [string]$KatalogProjektow = 'C:\Projects',
    [string]$KatalogRepo = 'C:\Projects\_repo',
    [string[]]$Repo = @(),
    [string]$Plugin = '',
    [string[]]$DozwoloneFolderyC = @('Windows', 'Program Files', 'Program Files (x86)', 'ProgramData', 'Users'),
    [switch]$Sprawdz,
    [switch]$TestAgenta,
    [switch]$InstalujKatalogProjektow
)

$ErrorActionPreference = 'Stop'
# Wynik programow zewnetrznych (git, whoami) czytamy jako UTF-8, zeby polskie znaki w sciezkach nie dawaly falszywych bledow.
try { [Console]::OutputEncoding = [System.Text.Encoding]::UTF8 } catch { }
$script:Bledy = New-Object System.Collections.ArrayList
$script:Ostrzezenia = New-Object System.Collections.ArrayList

function Pisz([string]$tekst, [string]$kolor = 'Gray') { Write-Host $tekst -ForegroundColor $kolor }
function Blad([string]$tekst) { [void]$script:Bledy.Add($tekst); Pisz ('[BLAD]  ' + $tekst) 'Red' }
function Ostrzez([string]$tekst) { [void]$script:Ostrzezenia.Add($tekst); Pisz ('[UWAGA] ' + $tekst) 'Yellow' }
function Ok([string]$tekst) { Pisz ('[OK]    ' + $tekst) 'Green' }

if ($PSVersionTable.PSEdition -eq 'Core') {
    Pisz 'Ten skrypt wymaga Windows PowerShell 5.1 (powershell.exe), nie PowerShell 7.' 'Red'
    exit 2
}

function Test-Administrator {
    $p = New-Object Security.Principal.WindowsPrincipal([Security.Principal.WindowsIdentity]::GetCurrent())
    return $p.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
}

# Prawa odbierane agentowi: jawna lista (bez ReadData, bez SYNCHRONIZE, bez ReadPermissions).
$PrawaZakazu = [System.Security.AccessControl.FileSystemRights](
    'WriteData, AppendData, WriteExtendedAttributes, WriteAttributes, Delete, DeleteSubdirectoriesAndFiles, ChangePermissions, TakeOwnership')
$SekcjaDostep = [System.Security.AccessControl.AccessControlSections]'Access'
$SekcjaWlasciciel = [System.Security.AccessControl.AccessControlSections]'Owner'
$TypSid = [System.Security.Principal.SecurityIdentifier]

# ---------------------------------------------------------------- konta i profile

function Get-SidKonta([string]$nazwa) {
    try {
        $konto = New-Object System.Security.Principal.NTAccount($nazwa)
        return $konto.Translate($TypSid)
    } catch { return $null }
}

function Get-SidAgenta {
    if ($TestAgenta) { return [System.Security.Principal.WindowsIdentity]::GetCurrent().User }
    try { return (Get-LocalUser -Name $Agent -ErrorAction Stop).SID } catch { }
    return (Get-SidKonta $Agent)
}

function Test-KontoAgenta {
    try { Get-LocalUser -Name $Agent -ErrorAction Stop | Out-Null; return $true } catch { return $false }
}

function Get-ProfilAgenta {
    if ($TestAgenta) { return $env:USERPROFILE }
    try {
        $sid = (Get-LocalUser -Name $Agent -ErrorAction Stop).SID.Value
        $wpis = Get-ItemProperty -Path ('HKLM:\SOFTWARE\Microsoft\Windows NT\CurrentVersion\ProfileList\' + $sid) -ErrorAction Stop
        return [Environment]::ExpandEnvironmentVariables($wpis.ProfileImagePath)
    } catch {
        return (Join-Path ($env:SystemDrive + '\Users') $Agent)
    }
}

function Get-Repozytoria {
    if ($Repo.Count -gt 0) {
        foreach ($r in $Repo) {
            $pelna = [System.IO.Path]::GetFullPath($r).TrimEnd('\')
            if (-not (Test-Path -LiteralPath (Join-Path $pelna '.git'))) { Blad ('to nie jest repozytorium git (brak .git): ' + $pelna) }
            else { $pelna }
        }
        return
    }
    if (-not (Test-Path -LiteralPath $KatalogRepo)) { return }
    Get-ChildItem -LiteralPath $KatalogRepo -Directory -Force |
        Where-Object { Test-Path -LiteralPath (Join-Path $_.FullName '.git') } | ForEach-Object { $_.FullName }
}

# Pliki kontrolne repo: @{ Sciezka; Folder }
function Get-PlikiKontrolne([string]$repo) {
    $lista = @(
        @{ Sciezka = '.claude'; Folder = $true },
        @{ Sciezka = '.githooks'; Folder = $true },
        @{ Sciezka = '.git\config'; Folder = $false },
        @{ Sciezka = '.git\hooks'; Folder = $true },
        @{ Sciezka = 'tools\przeglad.py'; Folder = $false },
        @{ Sciezka = 'tools\przeglad_konfig.py'; Folder = $false },
        @{ Sciezka = 'tools\tests\test_settings.py'; Folder = $false }
    )
    foreach ($e in $lista) { @{ Sciezka = (Join-Path $repo $e.Sciezka); Folder = $e.Folder } }
}

# ---------------------------------------------------------------- ACL (metoda .NET, bez Set-Acl)

function Get-AclDostep([string]$sciezka) {
    return (Get-Item -LiteralPath $sciezka -Force).GetAccessControl($SekcjaDostep)
}

# Reguly dotyczace agenta; $jawne = $true: tylko reguly nadane bezposrednio (bez odziedziczonych).
function Get-RegulyAgenta([string]$sciezka, [bool]$jawne = $false) {
    $sid = Get-SidAgenta
    if ($null -eq $sid) { return }
    $acl = Get-AclDostep $sciezka
    foreach ($r in $acl.GetAccessRules($true, (-not $jawne), $TypSid)) {
        if ($r.IdentityReference.Value -eq $sid.Value) { $r }
    }
}

function Test-Blokada([string]$sciezka) {
    $reguly = @(Get-RegulyAgenta $sciezka | Where-Object { $_.AccessControlType -eq 'Deny' })
    foreach ($r in $reguly) {
        if (([int]$r.FileSystemRights -band [int]$PrawaZakazu) -eq [int]$PrawaZakazu) { return $true }
    }
    return $false
}

function Test-Wlasciciel([string]$sciezka) {
    $sidWlasciciela = Get-SidKonta $Wlasciciel
    if ($null -eq $sidWlasciciela) { throw ('nie znaleziono konta wlasciciela: ' + $Wlasciciel) }
    $acl = (Get-Item -LiteralPath $sciezka -Force).GetAccessControl($SekcjaWlasciciel)
    $w = $acl.GetOwner($TypSid)
    return ($w.Value -eq $sidWlasciciela.Value)
}

function Set-BlokadaZapisu([string]$sciezka, [bool]$folder) {
    if (-not (Test-Wlasciciel $sciezka)) {
        $parametry = @($sciezka, '/setowner', $Wlasciciel, '/C', '/Q')
        if ($folder) { $parametry += '/T' }
        & icacls.exe @parametry | Out-Null
        if ($LASTEXITCODE -ne 0) { throw ('icacls /setowner nie powiodl sie dla ' + $sciezka) }
    }
    if (Test-Blokada $sciezka) { Ok ('blokada juz jest: ' + $sciezka); return }
    $dziedziczenie = if ($folder) { 'ContainerInherit, ObjectInherit' } else { 'None' }
    $regula = New-Object System.Security.AccessControl.FileSystemAccessRule -ArgumentList @((Get-SidAgenta), $PrawaZakazu, $dziedziczenie, 'None', 'Deny')
    $element = Get-Item -LiteralPath $sciezka -Force
    $acl = $element.GetAccessControl($SekcjaDostep)
    $acl.AddAccessRule($regula)
    $element.SetAccessControl($acl)
    Ok ('zalozono blokade zapisu: ' + $sciezka)
}

# Dodaje regule, jesli identycznej nie ma wsrod regul jawnych. Zwraca $true, gdy dodano.
function Add-RegulaJesliBrak($acl, $regula) {
    foreach ($r in $acl.GetAccessRules($true, $false, $TypSid)) {
        if ($r.IdentityReference.Value -eq $regula.IdentityReference.Value -and
            $r.AccessControlType -eq $regula.AccessControlType -and
            [int]$r.FileSystemRights -eq [int]$regula.FileSystemRights -and
            $r.InheritanceFlags -eq $regula.InheritanceFlags -and
            $r.PropagationFlags -eq $regula.PropagationFlags) { return $false }
    }
    $acl.AddAccessRule($regula)
    return $true
}

function Install-KatalogProjektow {
    foreach ($k in @($KatalogProjektow, $KatalogRepo)) {
        if (-not (Test-Path -LiteralPath $k)) { throw ('brak katalogu: ' + $k + ' (zaloz go jako wlasciciel i uruchom ponownie)') }
    }
    $sid = Get-SidAgenta
    if ($null -eq $sid) { throw ('nie znaleziono konta agenta: ' + $Agent) }
    $pelny = [System.Security.AccessControl.FileSystemRights]'FullControl'
    $zapis = [System.Security.AccessControl.FileSystemRights]'WriteData, AppendData'
    $modyfikacja = [System.Security.AccessControl.FileSystemRights]'Modify'
    # 1. katalog projektow: zakaz dziedziczony tylko w dol, plus zakaz zakladania czegokolwiek bezposrednio w nim
    $r1 = New-Object System.Security.AccessControl.FileSystemAccessRule -ArgumentList @($sid, $pelny, 'ContainerInherit, ObjectInherit', 'InheritOnly', 'Deny')
    $r2 = New-Object System.Security.AccessControl.FileSystemAccessRule -ArgumentList @($sid, $zapis, 'None', 'None', 'Deny')
    $el = Get-Item -LiteralPath $KatalogProjektow -Force
    $acl = $el.GetAccessControl($SekcjaDostep)
    $zmiana = $false
    if (Add-RegulaJesliBrak $acl $r1) { $zmiana = $true }
    if (Add-RegulaJesliBrak $acl $r2) { $zmiana = $true }
    if ($zmiana) { $el.SetAccessControl($acl); Ok ('zalozono zakaz dla ' + $Agent + ' na ' + $KatalogProjektow + ' (dziedziczony w dol)') }
    else { Ok ('zakaz na ' + $KatalogProjektow + ' juz jest') }
    # 2. katalog repozytoriow: jawne Modify, ktore wygrywa z odziedziczonym zakazem
    $r3 = New-Object System.Security.AccessControl.FileSystemAccessRule -ArgumentList @($sid, $modyfikacja, 'ContainerInherit, ObjectInherit', 'None', 'Allow')
    $el2 = Get-Item -LiteralPath $KatalogRepo -Force
    $acl2 = $el2.GetAccessControl($SekcjaDostep)
    if (Add-RegulaJesliBrak $acl2 $r3) { $el2.SetAccessControl($acl2); Ok ('zalozono Modify dla ' + $Agent + ' na ' + $KatalogRepo) }
    else { Ok ('Modify na ' + $KatalogRepo + ' juz jest') }
    Pisz 'Wczesniejsze blokady pojedynczych folderow (jesli byly) zostaja; usun je recznie, gdy nie sa potrzebne.' 'DarkGray'
}

# ---------------------------------------------------------------- zgodnosc z repo (skroty)

function Get-ZrodloPluginu { return [System.IO.Path]::GetFullPath((Join-Path $PSScriptRoot '..')).TrimEnd('\') }

function Get-KatalogPluginuWCache([string]$profilAgenta) {
    $manifest = Join-Path (Get-ZrodloPluginu) '.claude-plugin\plugin.json'
    if (-not (Test-Path -LiteralPath $manifest)) { Blad ('brak manifestu pluginu w repo: ' + $manifest); return $null }
    $wersja = (Get-Content -LiteralPath $manifest -Raw -Encoding UTF8 | ConvertFrom-Json).version
    $baza = if ($Plugin) { $Plugin } else { Join-Path $profilAgenta '.claude\plugins\cache\kuznia-kodu' }
    return @{ Wersja = $wersja; Katalog = (Join-Path (Join-Path $baza 'kuznia') $wersja) }
}

$PodkatalogiPluginu = @('.claude-plugin', 'agents', 'skills', 'hooks')

function Get-PlikiPluginu([string]$korzen) {
    foreach ($p in $PodkatalogiPluginu) {
        $katalog = Join-Path $korzen $p
        if (Test-Path -LiteralPath $katalog) {
            Get-ChildItem -LiteralPath $katalog -Recurse -File -Force |
                Where-Object { $_.FullName -notmatch '__pycache__' -and $_.Extension -ne '.pyc' }
        }
    }
}

function Get-Sciezka-Wzgledna([string]$korzen, [string]$pelna) { return $pelna.Substring($korzen.TrimEnd('\').Length + 1) }

# Porownuje pliki pluginu w cache agenta z wersja w repo (wykrywanie zamiast zapobiegania).
function Test-ZgodnoscPluginu([string]$profilAgenta) {
    $cel = Get-KatalogPluginuWCache $profilAgenta
    if ($null -eq $cel) { return }
    $zrodlo = Get-ZrodloPluginu
    if (-not (Test-Path -LiteralPath $cel.Katalog)) {
        Blad ('brak pluginu w wersji ' + $cel.Wersja + ' w cache: ' + $cel.Katalog + ' (zaktualizuj plugin u agenta, patrz README)')
        return
    }
    $roznice = 0
    $znane = @{}
    foreach ($f in @(Get-PlikiPluginu $zrodlo)) {
        $rel = Get-Sciezka-Wzgledna $zrodlo $f.FullName
        $znane[$rel.ToLowerInvariant()] = $true
        $plikCache = Join-Path $cel.Katalog $rel
        if (-not (Test-Path -LiteralPath $plikCache)) { Blad ('plugin w cache: brak pliku ' + $rel); $roznice++; continue }
        $a = (Get-FileHash -LiteralPath $f.FullName -Algorithm SHA256).Hash
        $b = (Get-FileHash -LiteralPath $plikCache -Algorithm SHA256).Hash
        if ($a -ne $b) { Blad ('plugin w cache rozni sie od repo (skrot): ' + $rel); $roznice++ }
    }
    foreach ($f in @(Get-PlikiPluginu $cel.Katalog)) {
        $rel = Get-Sciezka-Wzgledna $cel.Katalog $f.FullName
        if (-not $znane.ContainsKey($rel.ToLowerInvariant())) { Blad ('plugin w cache: plik spoza repo: ' + $rel); $roznice++ }
    }
    if ($roznice -eq 0) { Ok ('plugin w cache zgodny z repo, wersja ' + $cel.Wersja) }
}

function Test-Crlf([string]$plik) {
    $b = [System.IO.File]::ReadAllBytes($plik)
    for ($i = 0; $i -lt ($b.Length - 1); $i++) { if ($b[$i] -eq 13 -and $b[$i + 1] -eq 10) { return $true } }
    return $false
}

function Test-CrlfPluginu([string]$profilAgenta) {
    $cel = Get-KatalogPluginuWCache $profilAgenta
    if ($null -eq $cel -or -not (Test-Path -LiteralPath $cel.Katalog)) { return }
    $zle = 0
    foreach ($f in @(Get-PlikiPluginu $cel.Katalog)) {
        if (Test-Crlf $f.FullName) { Blad ('CRLF w pliku pluginu w cache (psuje naglowek agenta): ' + (Get-Sciezka-Wzgledna $cel.Katalog $f.FullName)); $zle++ }
    }
    if ($zle -eq 0) { Ok 'pliki pluginu w cache maja koncowki LF' }
}

function Test-ZgodnoscPliku([string]$zrodlo, [string]$plik, [string]$opis, [bool]$krytyczny) {
    if (-not (Test-Path -LiteralPath $zrodlo)) { Blad ('brak wzorca w repo: ' + $zrodlo); return }
    if (-not (Test-Path -LiteralPath $plik)) {
        if ($krytyczny) { Blad ('brak ' + $opis + ': ' + $plik) } else { Ostrzez ('brak ' + $opis + ': ' + $plik) }
        return
    }
    $a = (Get-FileHash -LiteralPath $zrodlo -Algorithm SHA256).Hash
    $b = (Get-FileHash -LiteralPath $plik -Algorithm SHA256).Hash
    if ($a -eq $b) { Ok ($opis + ' zgodny z repo: ' + $plik) }
    elseif ($krytyczny) { Blad ($opis + ' rozni sie od wzorca w repo: ' + $plik) }
    else { Ostrzez ($opis + ' rozni sie od wzorca w repo: ' + $plik) }
}

function Test-UstawieniaAgenta([string]$profilAgenta) {
    $plik = Join-Path $profilAgenta '.claude\settings.json'
    if (-not (Test-Path -LiteralPath $plik)) { Blad ('brak ' + $plik + ' (konektory claude.ai nie sa zablokowane na koncie agenta)'); return }
    try { $json = Get-Content -LiteralPath $plik -Raw -Encoding UTF8 | ConvertFrom-Json } catch { Blad ('ustawienia agenta nie sa poprawnym JSON: ' + $plik); return }
    $wpisy = @($json.deniedMcpServers | Where-Object { $_.serverUrl -eq '*://*/*' })
    if ($wpisy.Count -gt 0) { Ok 'deniedMcpServers obecne w ustawieniach agenta' }
    else { Blad ('brak deniedMcpServers (serverUrl *://*/*) w ' + $plik + ' (wzor: szablon-uzytkownika\settings.json)') }
}

# ---------------------------------------------------------------- raport (-Sprawdz) i instalacja

function Pokaz-PlikKontrolny([string]$sciezka) {
    if (-not (Test-Path -LiteralPath $sciezka)) { Ostrzez ('brak pliku lub folderu: ' + $sciezka); return }
    if (-not (Test-Wlasciciel $sciezka)) { Blad ('wlasciciel inny niz ' + $Wlasciciel + ': ' + $sciezka) }
    if (Test-Blokada $sciezka) { Ok ('zablokowany dla ' + $Agent + ': ' + $sciezka) }
    else { Blad ('BRAK blokady zapisu dla ' + $Agent + ': ' + $sciezka) }
}

# Ostrzega tylko o regulach Allow z zerowymi prawami (nietypowe). Wpis (N) w icacls to pelny zakaz i nie jest ostrzezeniem.
function Szukaj-ZezwolenBezPraw([string]$sciezka) {
    if (-not (Test-Path -LiteralPath $sciezka)) { return }
    foreach ($r in @(Get-RegulyAgenta $sciezka)) {
        if ($r.AccessControlType -eq 'Allow' -and [int]$r.FileSystemRights -eq 0) {
            Ostrzez ('zezwolenie bez praw dla ' + $Agent + ' w ' + $sciezka)
        }
    }
}

function Test-JestRepo([string]$folder) {
    return ([System.IO.Path]::GetFullPath($folder).TrimEnd('\') -ieq [System.IO.Path]::GetFullPath($KatalogRepo).TrimEnd('\'))
}

function Sprawdz-KatalogProjektow {
    if (-not (Test-Path -LiteralPath $KatalogProjektow)) { Ostrzez ('brak katalogu projektow: ' + $KatalogProjektow); return }
    Szukaj-ZezwolenBezPraw $KatalogProjektow
    $pelny = [int][System.Security.AccessControl.FileSystemRights]'FullControl'
    $zakazDziedziczony = @(Get-RegulyAgenta $KatalogProjektow $true | Where-Object {
        $_.AccessControlType -eq 'Deny' -and ([int]$_.FileSystemRights -band $pelny) -eq $pelny -and ($_.PropagationFlags -band 2) -eq 2 })
    if ($zakazDziedziczony.Count -gt 0) { Ok ('katalog projektow: dziedziczony zakaz FullControl (InheritOnly) dla ' + $Agent) }
    else { Blad ('katalog projektow: brak dziedziczonego zakazu dla ' + $Agent + ' (uruchom -InstalujKatalogProjektow)') }
    if (Test-Path -LiteralPath $KatalogRepo) {
        $modify = [int][System.Security.AccessControl.FileSystemRights]'Modify'
        $zezwolenie = @(Get-RegulyAgenta $KatalogRepo $true | Where-Object {
            $_.AccessControlType -eq 'Allow' -and ([int]$_.FileSystemRights -band $modify) -eq $modify })
        if ($zezwolenie.Count -gt 0) { Ok ('_repo: jawne Modify dla ' + $Agent) }
        else { Blad ('_repo: brak jawnego Modify dla ' + $Agent + ' (uruchom -InstalujKatalogProjektow)') }
    } else { Ostrzez ('brak katalogu repozytoriow: ' + $KatalogRepo) }
    foreach ($f in @(Get-ChildItem -LiteralPath $KatalogProjektow -Directory -Force | ForEach-Object { $_.FullName })) {
        if (Test-JestRepo $f) { continue }
        Szukaj-ZezwolenBezPraw $f
        # Odmowa moze wynikac tez z braku Allow, wiec to tylko wskazowka; rozstrzyga -TestAgenta.
        $deny = @(Get-RegulyAgenta $f | Where-Object { $_.AccessControlType -eq 'Deny' -and ([int]$_.FileSystemRights -band 1) -eq 1 })
        if ($deny.Count -eq 0) { Ostrzez ('folder bez blokady odczytu dla ' + $Agent + ' (nowo zalozony?): ' + $f) }
    }
}

# ---------------------------------------------------------------- test jako agent (-TestAgenta)

function Czy-Odmowa($blad) {
    $e = $blad.Exception
    while ($null -ne $e) {
        if ($e -is [System.UnauthorizedAccessException]) { return $true }
        $e = $e.InnerException
    }
    return $false
}

function Test-DostepFolder([string]$sciezka) {
    try {
        $en = [System.IO.Directory]::EnumerateFileSystemEntries($sciezka).GetEnumerator()
        [void]$en.MoveNext()
        return 'DOSTEP'
    } catch {
        if (Czy-Odmowa $_) { return 'odmowa' }
        return ('BLAD: ' + $_.Exception.GetType().Name)
    }
}

# Proba zapisu: plik - otwarcie do zapisu (bez zapisania bajtu), folder - utworzenie pliku. Odmowa jest wynikiem poprawnym.
# Gdyby zapis sie powiodl (to jest wlasnie BLAD zabezpieczenia), plik probny jest od razu usuwany.
function Test-ZapisFolderu([string]$sciezka, [bool]$folder) {
    try {
        if ($folder) {
            $cel = Join-Path $sciezka ('kuznia-test-zapisu-' + [guid]::NewGuid().ToString('N') + '.tmp')
            $fs = [System.IO.File]::Open($cel, 'CreateNew', 'Write')
            $fs.Close()
            Remove-Item -LiteralPath $cel -Force -ErrorAction SilentlyContinue
        } else {
            $fs = [System.IO.File]::Open($sciezka, 'Open', 'Write')
            $fs.Close()
        }
        return 'ZAPIS'
    } catch {
        if (Czy-Odmowa $_) { return 'odmowa' }
        return ('BLAD: ' + $_.Exception.GetType().Name)
    }
}

function Test-SafeDirectory([string[]]$repozytoria) {
    $git = Get-Command git.exe -ErrorAction SilentlyContinue
    if (-not $git) { Ostrzez 'brak git.exe w PATH konta agenta: nie sprawdzam safe.directory'; return }
    $wpisy = @()
    try { $wpisy = @(& git.exe config --global --get-all safe.directory 2>$null) } catch { }
    foreach ($r in $repozytoria) {
        $cel = $r.Replace('\', '/').TrimEnd('/')
        $jest = $false
        foreach ($w in $wpisy) {
            $n = ([string]$w).Replace('\', '/').TrimEnd('/')
            if ($n -eq '*' -or $n -ieq $cel) { $jest = $true }
        }
        if ($jest) { Ok ('safe.directory jest dla: ' + $r) }
        else {
            Blad ('brak safe.directory dla: ' + $r + ' (git zglosi dubious ownership)')
            Pisz ('        WKLEJ (okno: konto ' + $Agent + '): git config --global --add safe.directory ' + $cel) 'Yellow'
        }
    }
}

function Test-JakoAgent {
    $tozsamosc = [System.Security.Principal.WindowsIdentity]::GetCurrent().Name
    Pisz ('whoami: ' + $tozsamosc) 'Cyan'
    if (-not ($tozsamosc -ieq $Agent -or $tozsamosc -like ('*\' + $Agent))) {
        Blad ('to nie jest konto agenta (' + $Agent + '): test w innym oknie daje falszywe DOSTEP. Zaloguj sie jako ' + $Agent + ' i uruchom ponownie.')
        return
    }
    if (Test-Administrator) { Blad ('konto ' + $Agent + ' ma uprawnienia administratora (nie powinno)'); return }
    Ok ('test wykonywany na koncie agenta: ' + $tozsamosc)

    Pisz '--- foldery na C:\ (poza lista dozwolonych ma byc odmowa) ---' 'Cyan'
    $korzen = $env:SystemDrive + '\'
    foreach ($d in @(Get-ChildItem -LiteralPath $korzen -Directory -Force -ErrorAction SilentlyContinue)) {
        if ($d.Name -ieq (Split-Path -Leaf $KatalogProjektow)) { continue }
        $w = Test-DostepFolder $d.FullName
        if ($DozwoloneFolderyC -contains $d.Name) {
            if ($w -eq 'DOSTEP') { Ok ('dozwolony folder systemowy: ' + $d.FullName) } else { Ostrzez ('dozwolony folder daje ' + $w + ': ' + $d.FullName) }
        } elseif ($w -eq 'odmowa') { Ok ('odmowa (oczekiwana): ' + $d.FullName) }
        else { Blad ('test jako agent: ' + $w + ', oczekiwano odmowa: ' + $d.FullName) }
    }

    Pisz ('--- katalog projektow: ' + $KatalogProjektow + ' (tylko _repo ma DOSTEP) ---') 'Cyan'
    if (Test-Path -LiteralPath $KatalogProjektow) {
        foreach ($f in @(Get-ChildItem -LiteralPath $KatalogProjektow -Directory -Force -ErrorAction SilentlyContinue)) {
            $w = Test-DostepFolder $f.FullName
            if (Test-JestRepo $f.FullName) {
                if ($w -eq 'DOSTEP') { Ok ('DOSTEP (oczekiwany): ' + $f.FullName) } else { Blad ('test jako agent: ' + $w + ', oczekiwano DOSTEP: ' + $f.FullName) }
            } elseif ($w -eq 'odmowa') { Ok ('odmowa (oczekiwana): ' + $f.FullName) }
            else { Blad ('test jako agent: ' + $w + ', oczekiwano odmowa: ' + $f.FullName) }
        }
        $wz = Test-ZapisFolderu $KatalogProjektow $true
        if ($wz -eq 'odmowa') { Ok ('zakladanie plikow bezposrednio w ' + $KatalogProjektow + ': odmowa (oczekiwana)') }
        else { Blad ('zakladanie plikow bezposrednio w ' + $KatalogProjektow + ': ' + $wz + ', oczekiwano odmowa') }
    } else { Ostrzez ('brak katalogu projektow dla tego konta: ' + $KatalogProjektow) }

    $profil = Get-ProfilAgenta
    $zrodloUz = Join-Path (Get-ZrodloPluginu) 'szablon-uzytkownika'
    Pisz '--- profil agenta ---' 'Cyan'
    Test-UstawieniaAgenta $profil
    Test-ZgodnoscPliku (Join-Path $zrodloUz 'CLAUDE.md') (Join-Path $profil '.claude\CLAUDE.md') 'CLAUDE.md agenta' $true
    $profilPs = Join-Path $profil 'Documents\WindowsPowerShell\Microsoft.PowerShell_profile.ps1'
    Test-ZgodnoscPliku (Join-Path $zrodloUz 'profile.ps1') $profilPs 'profil PowerShell agenta' $false

    Pisz '--- plugin w cache ---' 'Cyan'
    Test-CrlfPluginu $profil
    Test-ZgodnoscPluginu $profil

    $repozytoria = @(Get-Repozytoria)
    if ($repozytoria.Count -eq 0) { Ostrzez ('nie znaleziono repozytoriow w ' + $KatalogRepo + ' (podaj -Repo)') }
    Pisz '--- zapis w plikach kontrolnych (ma byc odmowa) ---' 'Cyan'
    foreach ($r in $repozytoria) {
        Pisz ('repo: ' + $r) 'Cyan'
        foreach ($e in (Get-PlikiKontrolne $r)) {
            if (-not (Test-Path -LiteralPath $e.Sciezka)) { Ostrzez ('brak (pomijam): ' + $e.Sciezka); continue }
            $w = Test-ZapisFolderu $e.Sciezka $e.Folder
            if ($w -eq 'odmowa') { Ok ('zapis: odmowa (oczekiwana): ' + $e.Sciezka) }
            else { Blad ('zapis w pliku kontrolnym: ' + $w + ', oczekiwano odmowa: ' + $e.Sciezka) }
        }
    }
    Pisz '--- safe.directory ---' 'Cyan'
    Test-SafeDirectory $repozytoria
}

# ---------------------------------------------------------------- start
$tryby = @($Sprawdz.IsPresent, $TestAgenta.IsPresent, $InstalujKatalogProjektow.IsPresent) | Where-Object { $_ }
if (@($tryby).Count -gt 1) {
    Pisz 'Podaj najwyzej jeden z trybow: -Sprawdz, -TestAgenta, -InstalujKatalogProjektow.' 'Red'
    exit 2
}
$instalacjaRepo = (-not $Sprawdz -and -not $TestAgenta -and -not $InstalujKatalogProjektow)
if ($instalacjaRepo -and $Repo.Count -eq 0) {
    Pisz 'Instalacja wymaga parametru -Repo (jedno lub kilka repozytoriow). Nic nie zmieniono.' 'Yellow'
    Pisz 'Przyklad (administrator): powershell -ExecutionPolicy Bypass -File instaluj\windows.ps1 -Repo C:\Projects\_repo\nazwa' 'Yellow'
    Pisz 'Kolejnosc: najpierw plugin (claude plugin install ... --scope project), potem commit i push, dopiero potem blokady.' 'Yellow'
    exit 2
}

$nazwaTrybu = if ($Sprawdz) { '(tryb -Sprawdz: tylko raport)' } elseif ($TestAgenta) { '(tryb -TestAgenta: test jako agent)' } elseif ($InstalujKatalogProjektow) { '(instalacja katalogu projektow)' } else { '(instalacja blokad repo)' }
Pisz ('kuznia-kodu / windows.ps1 ' + $nazwaTrybu) 'Cyan'

if ($TestAgenta) {
    Test-JakoAgent
    Pisz ('Podsumowanie: bledy ' + $script:Bledy.Count + ', uwagi ' + $script:Ostrzezenia.Count) 'Cyan'
    if ($script:Bledy.Count -gt 0) { exit 1 }
    exit 0
}

if (-not (Test-KontoAgenta)) { Blad ('brak konta ' + $Agent + ' (skrypt go nie tworzy; zaloz je jako zwykle konto bez uprawnien administratora)') }
else { Ok ('konto agenta istnieje: ' + $Agent) }

if (-not $Sprawdz -and -not (Test-Administrator)) {
    Blad 'ten tryb wymaga uruchomienia jako administrator (albo uzyj -Sprawdz)'
}
if ($script:Bledy.Count -gt 0 -and -not $Sprawdz) { Pisz 'Przerwano: popraw bledy wyzej.' 'Red'; exit 1 }

if ($InstalujKatalogProjektow) {
    Install-KatalogProjektow
    Pisz '--- katalog projektow ---' 'Cyan'
    Sprawdz-KatalogProjektow
    Pisz ('Podsumowanie: bledy ' + $script:Bledy.Count + ', uwagi ' + $script:Ostrzezenia.Count) 'Cyan'
    Pisz ('Teraz zaloguj sie jako ' + $Agent + ' i uruchom: windows.ps1 -TestAgenta') 'Cyan'
    if ($script:Bledy.Count -gt 0) { exit 1 }
    exit 0
}

$profil = Get-ProfilAgenta
$zrodloUz = Join-Path (Get-ZrodloPluginu) 'szablon-uzytkownika'
$repozytoria = @(Get-Repozytoria)
if ($script:Bledy.Count -gt 0 -and -not $Sprawdz) { Pisz 'Przerwano: popraw bledy wyzej.' 'Red'; exit 1 }
if ($repozytoria.Count -eq 0) { Ostrzez ('nie znaleziono repozytoriow w ' + $KatalogRepo + ' (podaj -Repo)') }

if (-not $Sprawdz) {
    # Wzorce dla profilu agenta. CLAUDE.md nadpisujemy; settings.json i profil PowerShell tylko gdy ich nie ma
    # (agent albo wlasciciel moze miec w nich wlasne ustawienia). Nic z tego nie jest blokowane: obrona to wykrywanie.
    $katalogClaude = Join-Path $profil '.claude'
    if (-not (Test-Path -LiteralPath $katalogClaude)) { New-Item -ItemType Directory -Path $katalogClaude | Out-Null }
    $kopie = @(
        @{ Z = 'CLAUDE.md'; Do = (Join-Path $katalogClaude 'CLAUDE.md'); Nadpisz = $true },
        @{ Z = 'settings.json'; Do = (Join-Path $katalogClaude 'settings.json'); Nadpisz = $false },
        @{ Z = 'profile.ps1'; Do = (Join-Path $profil 'Documents\WindowsPowerShell\Microsoft.PowerShell_profile.ps1'); Nadpisz = $false }
    )
    foreach ($k in $kopie) {
        $zr = Join-Path $zrodloUz $k.Z
        if (-not (Test-Path -LiteralPath $zr)) { throw ('brak pliku zrodlowego: ' + $zr) }
        if ((Test-Path -LiteralPath $k.Do) -and -not $k.Nadpisz) { Pisz ('pomijam (juz istnieje, porownanie w -TestAgenta): ' + $k.Do) 'DarkGray'; continue }
        $katalogDocelowy = Split-Path -Parent $k.Do
        if (-not (Test-Path -LiteralPath $katalogDocelowy)) { New-Item -ItemType Directory -Path $katalogDocelowy -Force | Out-Null }
        Copy-Item -LiteralPath $zr -Destination $k.Do -Force
        Ok ('skopiowano: ' + $k.Do)
    }
    foreach ($r in $repozytoria) {
        foreach ($e in (Get-PlikiKontrolne $r)) {
            if (Test-Path -LiteralPath $e.Sciezka) { Set-BlokadaZapisu $e.Sciezka $e.Folder }
            else { Ostrzez ('pomijam (brak): ' + $e.Sciezka) }
        }
    }
    Pisz 'Po zmianie plikow kontrolnych przez git (apply, pull, checkout) zaloz blokady ponownie: git zapisuje plik od nowa i blokada znika.' 'DarkGray'
}

# raport (w obu trybach; po instalacji potwierdza wynik)
Pisz '--- stan blokad ---' 'Cyan'
foreach ($r in $repozytoria) {
    Pisz ('repo: ' + $r) 'Cyan'
    foreach ($e in (Get-PlikiKontrolne $r)) { Pokaz-PlikKontrolny $e.Sciezka; Szukaj-ZezwolenBezPraw $e.Sciezka }
}
if ($Sprawdz) {
    Pisz '--- katalog projektow ---' 'Cyan'
    Sprawdz-KatalogProjektow
    Pisz '--- zgodnosc z repo (wykrywanie) ---' 'Cyan'
    if (Test-Path -LiteralPath $profil) {
        Test-ZgodnoscPliku (Join-Path $zrodloUz 'CLAUDE.md') (Join-Path $profil '.claude\CLAUDE.md') 'CLAUDE.md agenta' $true
        Test-ZgodnoscPluginu $profil
    } else { Ostrzez ('brak dostepu do profilu agenta: ' + $profil + ' (uruchom jako administrator albo uzyj -TestAgenta na koncie agenta)') }
}

Pisz ('Podsumowanie: bledy ' + $script:Bledy.Count + ', uwagi ' + $script:Ostrzezenia.Count) 'Cyan'
if (-not $Sprawdz) {
    Pisz ('Dalej: zaloguj sie jako ' + $Agent + ' (czerwony znak zachety w oknie) i uruchom: windows.ps1 -TestAgenta') 'Cyan'
}
if ($script:Bledy.Count -gt 0) { exit 1 }
exit 0
