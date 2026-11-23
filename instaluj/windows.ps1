<#
.SYNOPSIS
  Instalator metody kuznia-kodu dla Windows (miniPC, laptop). Uruchamia Pawel jako administrator.
  Agent Claude Code ten skrypt tylko pisze, nigdy go nie uruchamia.

.DESCRIPTION
  Bez -Sprawdz (wymaga administratora):
    1. sprawdza, czy istnieje konto agenta (NIE tworzy go),
    2. kopiuje szablon-uzytkownika\CLAUDE.md do profilu agenta (.claude\CLAUDE.md),
    3. zmienia wlasciciela plikow kontrolnych na wlasciciela (Pawla) i zaklada blokady zapisu NTFS dla agenta.
  Blokady sa zakladane metoda .NET (FileSystemAccessRule, jawna lista praw, bez SYNCHRONIZE i bez praw odczytu),
  NIE przez "icacls /deny" z prawami w nawiasie (taki wpis potrafi zablokowac tez odczyt). Do zmiany wlasciciela
  uzywany jest "icacls /setowner" (bez /deny).
  Pliki kontrolne kazdego repo: .claude\, .githooks\, .git\config, .git\hooks\, tools\przeglad.py,
  tools\przeglad_konfig.py, tools\tests\test_settings.py. Dodatkowo: katalog pluginu i .claude\CLAUDE.md w profilu agenta.

  Z -Sprawdz (administrator niepotrzebny; NIC nie zmienia):
    - raportuje wlasciciela i blokady plikow kontrolnych,
    - ostrzega o pustych wpisach (N) dla agenta (zezwolenie bez praw, a nie zakaz) i o folderach w katalogu
      projektow bez blokady (np. nowo zalozonych),
    - wykonuje test dostepu JAKO agent (pyta o haslo konta agenta, chyba ze -BezTestuDostepu): kazdy folder
      w katalogu projektow poza _repo ma dac "odmowa", a _repo "DOSTEP". Kod wyjscia 1, gdy cos jest nie tak.

.PARAMETER Agent             nazwa konta agenta (domyslnie claude-agent)
.PARAMETER Wlasciciel        konto wlasciciela plikow kontrolnych (domyslnie Belkot)
.PARAMETER KatalogProjektow  katalog z projektami (domyslnie C:\Projects)
.PARAMETER KatalogRepo       katalog z repozytoriami (domyslnie C:\Projects\_repo)
.PARAMETER Repo              konkretne repozytoria (domyslnie wszystkie podkatalogi KatalogRepo z .git)
.PARAMETER Plugin            katalog pluginu (PROPOSED: <profil agenta>\.claude\plugins\cache\kuznia-kodu)
.PARAMETER Sprawdz           tylko raport (patrz wyzej)
.PARAMETER BezTestuDostepu   z -Sprawdz: pomija test dostepu jako agent

.EXAMPLE
  powershell -ExecutionPolicy Bypass -File instaluj\windows.ps1 -Sprawdz
  powershell -ExecutionPolicy Bypass -File instaluj\windows.ps1          (jako administrator)
#>
[CmdletBinding()]
param(
    [string]$Agent = 'claude-agent',
    [string]$Wlasciciel = 'Belkot',
    [string]$KatalogProjektow = 'C:\Projects',
    [string]$KatalogRepo = 'C:\Projects\_repo',
    [string[]]$Repo = @(),
    [string]$Plugin = '',
    [switch]$Sprawdz,
    [switch]$BezTestuDostepu
)

$ErrorActionPreference = 'Stop'
$script:Bledy = New-Object System.Collections.ArrayList
$script:Ostrzezenia = New-Object System.Collections.ArrayList

function Pisz([string]$tekst, [string]$kolor = 'Gray') { Write-Host $tekst -ForegroundColor $kolor }
function Blad([string]$tekst) { [void]$script:Bledy.Add($tekst); Pisz ('[BLAD]  ' + $tekst) 'Red' }
function Ostrzez([string]$tekst) { [void]$script:Ostrzezenia.Add($tekst); Pisz ('[UWAGA] ' + $tekst) 'Yellow' }
function Ok([string]$tekst) { Pisz ('[OK]    ' + $tekst) 'Green' }

function Test-Administrator {
    $p = New-Object Security.Principal.WindowsPrincipal([Security.Principal.WindowsIdentity]::GetCurrent())
    return $p.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
}

# Prawa odbierane agentowi: jawna lista (bez ReadData, bez SYNCHRONIZE, bez ReadPermissions).
$PrawaZakazu = [System.Security.AccessControl.FileSystemRights](
    'WriteData, AppendData, WriteExtendedAttributes, WriteAttributes, Delete, DeleteSubdirectoriesAndFiles, ChangePermissions, TakeOwnership')

function Get-ProfilAgenta {
    try {
        $sid = (Get-LocalUser -Name $Agent -ErrorAction Stop).SID.Value
        $wpis = Get-ItemProperty -Path ('HKLM:\SOFTWARE\Microsoft\Windows NT\CurrentVersion\ProfileList\' + $sid) -ErrorAction Stop
        return [Environment]::ExpandEnvironmentVariables($wpis.ProfileImagePath)
    } catch {
        return (Join-Path ($env:SystemDrive + '\Users') $Agent)
    }
}

function Get-Repozytoria {
    if ($Repo.Count -gt 0) { return $Repo }
    if (-not (Test-Path -LiteralPath $KatalogRepo)) { return @() }
    return @(Get-ChildItem -LiteralPath $KatalogRepo -Directory -Force |
        Where-Object { Test-Path -LiteralPath (Join-Path $_.FullName '.git') } | ForEach-Object { $_.FullName })
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

function Test-KontoAgenta {
    try { Get-LocalUser -Name $Agent -ErrorAction Stop | Out-Null; return $true } catch { return $false }
}

function Get-RegulyAgenta([string]$sciezka) {
    $acl = Get-Acl -LiteralPath $sciezka
    $acl.Access | Where-Object { $_.IdentityReference.Value -like ('*\' + $Agent) -or $_.IdentityReference.Value -eq $Agent }
}

function Test-Blokada([string]$sciezka) {
    $reguly = @(Get-RegulyAgenta $sciezka | Where-Object { $_.AccessControlType -eq 'Deny' })
    foreach ($r in $reguly) {
        if (([int]$r.FileSystemRights -band [int]$PrawaZakazu) -eq [int]$PrawaZakazu) { return $true }
    }
    return $false
}

function Test-Wlasciciel([string]$sciezka) {
    $w = (Get-Acl -LiteralPath $sciezka).Owner
    return ($w -like ('*\' + $Wlasciciel) -or $w -eq $Wlasciciel)
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
    $regula = New-Object System.Security.AccessControl.FileSystemAccessRule($Agent, $PrawaZakazu, $dziedziczenie, 'None', 'Deny')
    $acl = Get-Acl -LiteralPath $sciezka
    $acl.AddAccessRule($regula)
    Set-Acl -LiteralPath $sciezka -AclObject $acl
    Ok ('zalozono blokade zapisu: ' + $sciezka)
}

# ---------------------------------------------------------------- raport (-Sprawdz) i instalacja

function Pokaz-PlikKontrolny([string]$sciezka) {
    if (-not (Test-Path -LiteralPath $sciezka)) { Ostrzez ('brak pliku lub folderu: ' + $sciezka); return }
    if (-not (Test-Wlasciciel $sciezka)) { Blad ('wlasciciel inny niz ' + $Wlasciciel + ': ' + $sciezka) }
    if (Test-Blokada $sciezka) { Ok ('zablokowany dla ' + $Agent + ': ' + $sciezka) }
    else { Blad ('BRAK blokady zapisu dla ' + $Agent + ': ' + $sciezka) }
}

function Szukaj-PustychWpisow([string]$sciezka) {
    if (-not (Test-Path -LiteralPath $sciezka)) { return }
    foreach ($r in @(Get-RegulyAgenta $sciezka)) {
        if ($r.AccessControlType -eq 'Allow' -and [int]$r.FileSystemRights -eq 0) {
            Ostrzez ('pusty wpis (N) dla ' + $Agent + ' w ' + $sciezka + ': to zezwolenie bez praw, a NIE zakaz')
        }
    }
}

function Test-DostepJakoAgent([string[]]$foldery) {
    $kred = Get-Credential -UserName ($env:COMPUTERNAME + '\' + $Agent) -Message ('Haslo konta ' + $Agent + ' (test dostepu, nic nie jest zapisywane)')
    if ($null -eq $kred) { Ostrzez 'test dostepu pominiety (brak poswiadczen)'; return $null }
    $lista = ($foldery | ForEach-Object { "'" + ($_ -replace "'", "''") + "'" }) -join ','
    $kod = '$ErrorActionPreference = ''Stop''; foreach ($p in @(' + $lista + ')) { ' +
        'try { Get-ChildItem -LiteralPath $p -Force -ErrorAction Stop | Select-Object -First 1 | Out-Null; $w = ''DOSTEP'' } ' +
        'catch [System.UnauthorizedAccessException] { $w = ''odmowa'' } catch { $w = ''BLAD: '' + $_.Exception.GetType().Name }; ' +
        'Write-Output ($p + ''|'' + $w) }'
    $zakodowany = [Convert]::ToBase64String([Text.Encoding]::Unicode.GetBytes($kod))
    $wy = [IO.Path]::GetTempFileName(); $er = [IO.Path]::GetTempFileName()
    try {
        Start-Process -FilePath 'powershell.exe' -Credential $kred -WorkingDirectory ($env:SystemRoot + '\System32') `
            -ArgumentList @('-NoProfile', '-NonInteractive', '-EncodedCommand', $zakodowany) `
            -RedirectStandardOutput $wy -RedirectStandardError $er -WindowStyle Hidden -Wait | Out-Null
        $wynik = @{}
        foreach ($l in (Get-Content -LiteralPath $wy)) {
            $i = $l.LastIndexOf('|')
            if ($i -gt 0) { $wynik[$l.Substring(0, $i)] = $l.Substring($i + 1) }
        }
        return $wynik
    } finally {
        Remove-Item -LiteralPath $wy, $er -Force -ErrorAction SilentlyContinue
    }
}

function Sprawdz-KatalogProjektow {
    if (-not (Test-Path -LiteralPath $KatalogProjektow)) { Ostrzez ('brak katalogu projektow: ' + $KatalogProjektow); return }
    $foldery = @(Get-ChildItem -LiteralPath $KatalogProjektow -Directory -Force | ForEach-Object { $_.FullName })
    $repoRoot = (Resolve-Path -LiteralPath $KatalogRepo -ErrorAction SilentlyContinue)
    Szukaj-PustychWpisow $KatalogProjektow
    foreach ($f in $foldery) {
        Szukaj-PustychWpisow $f
        $jestRepo = ($repoRoot -and ([IO.Path]::GetFullPath($f).TrimEnd('\') -ieq [IO.Path]::GetFullPath($KatalogRepo).TrimEnd('\')))
        if (-not $jestRepo) {
            $deny = @(Get-RegulyAgenta $f | Where-Object { $_.AccessControlType -eq 'Deny' -and ([int]$_.FileSystemRights -band 1) -eq 1 })
            if ($deny.Count -eq 0) { Ostrzez ('folder bez blokady odczytu dla ' + $Agent + ' (nowo zalozony?): ' + $f) }
        }
    }
    if ($BezTestuDostepu) { Pisz 'test dostepu jako agent pominiety (-BezTestuDostepu)' 'DarkGray'; return }
    $wyniki = Test-DostepJakoAgent $foldery
    if ($null -eq $wyniki) { return }
    foreach ($f in $foldery) {
        $jestRepo = ([IO.Path]::GetFullPath($f).TrimEnd('\') -ieq [IO.Path]::GetFullPath($KatalogRepo).TrimEnd('\'))
        $w = $wyniki[$f]
        if ($jestRepo) {
            if ($w -eq 'DOSTEP') { Ok ('test jako agent: DOSTEP (oczekiwany): ' + $f) } else { Blad ('test jako agent: ' + $w + ', oczekiwano DOSTEP: ' + $f) }
        } else {
            if ($w -eq 'odmowa') { Ok ('test jako agent: odmowa (oczekiwana): ' + $f) } else { Blad ('test jako agent: ' + $w + ', oczekiwano odmowa: ' + $f) }
        }
    }
}

# ---------------------------------------------------------------- start
Pisz ('kuznia-kodu / windows.ps1 ' + $(if ($Sprawdz) { '(tryb -Sprawdz: tylko raport)' } else { '(instalacja)' })) 'Cyan'

if (-not (Test-KontoAgenta)) { Blad ('brak konta ' + $Agent + ' (skrypt go nie tworzy; zaloz je jako zwykle konto bez uprawnien administratora)') }
else { Ok ('konto agenta istnieje: ' + $Agent) }

if (-not $Sprawdz -and -not (Test-Administrator)) {
    Blad 'ten tryb wymaga uruchomienia jako administrator (albo uzyj -Sprawdz)'
}

$profil = Get-ProfilAgenta
$plikAgenta = Join-Path $profil '.claude\CLAUDE.md'
$zrodlo = Join-Path $PSScriptRoot '..\szablon-uzytkownika\CLAUDE.md'
$katalogPluginu = if ($Plugin) { $Plugin } else { Join-Path $profil '.claude\plugins\cache\kuznia-kodu' }
$repozytoria = @(Get-Repozytoria)
if ($repozytoria.Count -eq 0) { Ostrzez ('nie znaleziono repozytoriow w ' + $KatalogRepo + ' (podaj -Repo)') }

if ($script:Bledy.Count -gt 0 -and -not $Sprawdz) { Pisz 'Przerwano: popraw bledy wyzej.' 'Red'; exit 1 }

if (-not $Sprawdz) {
    if (-not (Test-Path -LiteralPath $zrodlo)) { throw ('brak pliku zrodlowego: ' + $zrodlo) }
    $katalogClaude = Split-Path -Parent $plikAgenta
    if (-not (Test-Path -LiteralPath $katalogClaude)) { New-Item -ItemType Directory -Path $katalogClaude | Out-Null }
    Copy-Item -LiteralPath $zrodlo -Destination $plikAgenta -Force
    Ok ('skopiowano CLAUDE.md agenta: ' + $plikAgenta)
    Set-BlokadaZapisu $plikAgenta $false
    foreach ($r in $repozytoria) {
        foreach ($e in (Get-PlikiKontrolne $r)) {
            if (Test-Path -LiteralPath $e.Sciezka) { Set-BlokadaZapisu $e.Sciezka $e.Folder }
            else { Ostrzez ('pomijam (brak): ' + $e.Sciezka) }
        }
    }
    if (Test-Path -LiteralPath $katalogPluginu) { Set-BlokadaZapisu $katalogPluginu $true }
    else { Ostrzez ('brak katalogu pluginu (plugin nie zainstalowany?): ' + $katalogPluginu + ' - uruchom skrypt ponownie po instalacji') }
    Pisz 'Po zmianie plikow kontrolnych przez git pull zaloz blokady ponownie (git zapisuje plik od nowa i blokada znika).' 'DarkGray'
}

# raport (w obu trybach; po instalacji potwierdza wynik)
Pisz '--- stan blokad ---' 'Cyan'
if (Test-Path -LiteralPath $plikAgenta) { Pokaz-PlikKontrolny $plikAgenta; Szukaj-PustychWpisow $plikAgenta } else { Ostrzez ('brak ' + $plikAgenta) }
foreach ($r in $repozytoria) {
    Pisz ('repo: ' + $r) 'Cyan'
    foreach ($e in (Get-PlikiKontrolne $r)) { Pokaz-PlikKontrolny $e.Sciezka; Szukaj-PustychWpisow $e.Sciezka }
}
if (Test-Path -LiteralPath $katalogPluginu) { Pokaz-PlikKontrolny $katalogPluginu } else { Ostrzez ('brak katalogu pluginu: ' + $katalogPluginu) }
Pisz '--- katalog projektow ---' 'Cyan'
Sprawdz-KatalogProjektow

Pisz ('Podsumowanie: bledy ' + $script:Bledy.Count + ', uwagi ' + $script:Ostrzezenia.Count) 'Cyan'
if ($script:Bledy.Count -gt 0) { exit 1 }
exit 0
