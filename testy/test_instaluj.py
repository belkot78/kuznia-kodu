"""Testy statyczne instalatorow i profili maszyn (offline). Skryptow instaluj/* NIE uruchamiamy: czytamy ich tekst."""
import re
import shutil
import subprocess
from pathlib import Path

import pytest

KORZEN = Path(__file__).resolve().parents[1]
PS1 = KORZEN / "instaluj" / "windows.ps1"
SH = KORZEN / "instaluj" / "linux.sh"


@pytest.fixture(scope="module")
def ps():
    return PS1.read_text(encoding="utf-8")


def test_windows_ps1_tylko_ascii(ps):
    """PowerShell 5.1 czyta plik bez BOM jako ANSI: polskie znaki psuja skrypt."""
    assert ps.isascii(), [l for l in ps.splitlines() if not l.isascii()][:3]


def test_windows_ps1_blokady_metoda_net_a_nie_icacls_deny(ps):
    assert "FileSystemAccessRule" in ps and "'Deny'" in ps
    kod = re.sub(r"<#.*?#>", "", ps, flags=re.S)                       # bez komentarzy (opisuja zakaz)
    kod = "\n".join(l for l in kod.splitlines() if not l.lstrip().startswith("#"))
    assert not re.search(r"icacls(\.exe)?[^\n]*/deny", kod, re.I)
    assert "/setowner" in ps                      # zmiana wlasciciela na wlasciciela (Pawla)
    # prawa odbierane agentowi: jawna lista, bez odczytu i bez SYNCHRONIZE
    prawa = re.search(r"'(WriteData[^']*)'", ps).group(1)
    for wymagane in ("WriteData", "AppendData", "Delete", "DeleteSubdirectoriesAndFiles", "ChangePermissions",
                     "TakeOwnership"):
        assert wymagane in prawa
    for zakazane in ("ReadData", "Synchronize", "FullControl", "Modify", "GenericWrite"):
        assert zakazane not in prawa


def kod_bez_komentarzy(ps):
    kod = re.sub(r"<#.*?#>", "", ps, flags=re.S)
    return "\n".join(l for l in kod.splitlines() if not l.lstrip().startswith("#"))


def test_windows_ps1_blokady_przez_getaccesscontrol_a_nie_set_acl(ps):
    """#7 z porzadkow: Set-Acl probuje zapisac tez wlasciciela; blokady maja isc przez GetAccessControl('Access')."""
    kod = kod_bez_komentarzy(ps)
    assert "GetAccessControl($SekcjaDostep)" in kod and "SetAccessControl($acl)" in kod
    assert "AccessControlSections]'Access'" in kod
    assert not re.search(r"\bSet-Acl\b", kod)
    assert not re.search(r"\bGet-Acl\b", kod)
    blok = kod[kod.index("function Set-BlokadaZapisu"):kod.index("function Add-RegulaJesliBrak")]
    assert "SetAccessControl" in blok and "Set-Acl" not in blok


def test_windows_ps1_instalacja_wymaga_repo(ps):
    kod = kod_bez_komentarzy(ps)
    assert "[string[]]$Repo" in ps
    assert re.search(r"\$instalacjaRepo -and \$Repo\.Count -eq 0", kod)
    zajawka = kod[kod.index("$instalacjaRepo -and"):]
    assert "exit 2" in zajawka[:600]               # komunikat i wyjscie, zanim cokolwiek zostanie zmienione
    assert "Get-ChildItem -LiteralPath $KatalogRepo" in kod   # domyslne repo tylko dla -Sprawdz i -TestAgenta


def test_windows_ps1_nie_blokuje_katalogu_pluginu(ps):
    kod = kod_bez_komentarzy(ps)
    for linia in kod.splitlines():
        if "Set-BlokadaZapisu" in linia and not linia.lstrip().startswith("function"):
            assert "luginu" not in linia and "$Plugin" not in linia, linia
    assert "Set-BlokadaZapisu $katalogPluginu" not in kod
    assert "Test-ZgodnoscPluginu" in kod and "Get-FileHash" in kod        # wykrywanie zamiast zapobiegania
    assert "CLAUDE.md agenta" in kod and "Test-CrlfPluginu" in kod


def test_windows_ps1_ma_tryb_testagenta(ps):
    kod = kod_bez_komentarzy(ps)
    assert "[switch]$TestAgenta" in ps
    assert "WindowsIdentity]::GetCurrent().Name" in kod and "whoami" in ps
    assert "deniedMcpServers" in kod
    assert "'CreateNew', 'Write'" in kod and "'Open', 'Write'" in kod        # test zapisu plikow kontrolnych
    assert "safe.directory" in kod and "git config --global --add safe.directory" in kod
    assert "DozwoloneFolderyC" in kod and "$env:SystemDrive" in kod          # wszystkie foldery na C:\
    assert "Test-Crlf" in kod and "Test-SafeDirectory" in kod


def test_windows_ps1_bez_start_process_credential(ps):
    kod = kod_bez_komentarzy(ps)
    assert "Start-Process" not in kod and "-Credential" not in kod and "Get-Credential" not in kod
    assert "UTF8" in kod                                    # #8b: polskie znaki w wyniku programow zewnetrznych


def test_windows_ps1_tryb_instalacji_katalogu_projektow(ps):
    kod = kod_bez_komentarzy(ps)
    assert "[switch]$InstalujKatalogProjektow" in ps
    assert "'InheritOnly'" in kod and "'Deny'" in kod and "'FullControl'" in kod
    assert "'Modify'" in kod and "'Allow'" in kod


def test_windows_ps1_sprawdz_bez_ostrzezenia_o_pustych_wpisach_n(ps):
    """(N) w icacls to pelny zakaz (METODA 0.4, sekcja 12), a nie pusty wpis."""
    kod = kod_bez_komentarzy(ps)
    assert "pusty wpis" not in kod.lower() and "Szukaj-PustychWpisow" not in kod
    assert "bez blokady" in kod                              # foldery w katalogu projektow bez blokady


def test_windows_ps1_kolejnosc_w_pomocy_plugin_przed_blokadami(ps):
    pomoc = ps[:ps.index("[CmdletBinding()]")]
    assert pomoc.index("claude plugin install") < pomoc.index("-Repo <repo> (blokady)")
    assert "NAJPIERW plugin, POTEM blokady" in pomoc
    assert "-TestAgenta" in pomoc[pomoc.index("(blokady)"):]            # przypomnienie o tescie po instalacji


def test_windows_ps1_nie_tworzy_konta_ani_nie_poszerza_uprawnien(ps):
    for niedozwolone in ("New-LocalUser", "net user", "Add-LocalGroupMember", "net localgroup",
                         "Set-ExecutionPolicy", "Invoke-WebRequest", "Invoke-Expression", "iex "):
        assert niedozwolone.lower() not in ps.lower(), niedozwolone
    assert "NIE tworzy" in ps or "nie tworzy" in ps


def test_windows_ps1_ma_tryb_sprawdz_i_test_dostepu(ps):
    assert "[switch]$Sprawdz" in ps
    assert "DOSTEP" in ps and "odmowa" in ps
    assert "bez blokady" in ps                    # nowo zalozone foldery w katalogu projektow
    assert "_repo" in ps and "KatalogRepo" in ps


def test_windows_ps1_wymaga_administratora_tylko_poza_trybem_sprawdz(ps):
    assert "Test-Administrator" in ps
    assert re.search(r"if \(-not \$Sprawdz -and -not \(Test-Administrator\)\)", ps)


def test_windows_ps1_pliki_kontrolne_zgodne_z_metoda(ps):
    for sciezka in (".claude", ".githooks", ".git\\config", ".git\\hooks", "tools\\przeglad.py",
                    "tools\\przeglad_konfig.py", "tools\\tests\\test_settings.py"):
        assert sciezka in ps, sciezka
    assert "szablon-uzytkownika" in ps and ".claude\\CLAUDE.md" in ps
    assert "plugins" in ps


def test_windows_ps1_nawiasy_i_cudzyslowy_sa_zbalansowane(ps):
    """Przyblizona kontrola skladni bez uruchamiania PowerShella (parser PowerShella nie byl dostepny)."""
    bez_komentarzy = re.sub(r"<#.*?#>", "", ps, flags=re.S)
    bez_komentarzy = "\n".join(l for l in bez_komentarzy.splitlines() if not l.lstrip().startswith("#"))
    for otwarty, zamkniety in (("{", "}"), ("(", ")"), ("[", "]")):
        assert bez_komentarzy.count(otwarty) == bez_komentarzy.count(zamkniety), (otwarty, zamkniety)


def test_linux_sh_jest_szkicem_proposed_i_ma_poprawna_skladnie():
    tresc = SH.read_text(encoding="utf-8")
    assert tresc.startswith("#!/bin/sh") and "PROPOSED" in tresc
    assert "id \"$AGENT\"" in tresc and "useradd" not in tresc and "adduser" not in tresc
    sh = shutil.which("sh")
    if sh:
        w = subprocess.run([sh, "-n", str(SH)], capture_output=True, text=True)   # tylko skladnia, bez wykonania
        assert w.returncode == 0, w.stderr


@pytest.mark.parametrize("nazwa", ["minipc", "legion", "_szablon"])
def test_profil_maszyny_ma_wymagane_pola(nazwa):
    tresc = (KORZEN / "maszyny" / f"{nazwa}.md").read_text(encoding="utf-8")
    for pole in ("System i wersja", "Konto agenta", "Katalog repozytoriów", "Interpreter dla agenta",
                 "Rodzaj izolacji", "Dostępne poziomy dostępu"):
        assert pole in tresc, pole


def test_profil_legion_oznacza_braki_jako_open_question():
    assert "OPEN QUESTION" in (KORZEN / "maszyny" / "legion.md").read_text(encoding="utf-8")


def test_windows_ps1_test_blokada_liczy_tylko_reguly_jawne(ps):
    """Odziedziczony Deny FullControl z katalogu projektow nie moze udawac blokady (recenzja PK-M0.1, bloker)."""
    kod = kod_bez_komentarzy(ps)
    blok = kod[kod.index("function Test-Blokada"):kod.index("function Test-Wlasciciel")]
    assert "Get-RegulyAgenta $sciezka $true" in blok
    assert "function Get-RegulyAgenta([string]$sciezka, [bool]$jawne = $false)" in kod


def test_windows_ps1_porownuje_tez_szablon_i_maszyny_w_pluginie(ps):
    linia = next(l for l in ps.splitlines() if l.startswith("$PodkatalogiPluginu"))
    for katalog in ("agents", "skills", "hooks", "szablon", "szablon-uzytkownika", "maszyny"):
        assert f"'{katalog}'" in linia, katalog
