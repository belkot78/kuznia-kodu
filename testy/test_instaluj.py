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


def test_windows_ps1_nie_tworzy_konta_ani_nie_poszerza_uprawnien(ps):
    for niedozwolone in ("New-LocalUser", "net user", "Add-LocalGroupMember", "net localgroup",
                         "Set-ExecutionPolicy", "Invoke-WebRequest", "Invoke-Expression", "iex "):
        assert niedozwolone.lower() not in ps.lower(), niedozwolone
    assert "NIE tworzy" in ps or "nie tworzy" in ps


def test_windows_ps1_ma_tryb_sprawdz_z_testem_dostepu_i_ostrzezeniem_n(ps):
    assert "[switch]$Sprawdz" in ps
    assert "DOSTEP" in ps and "odmowa" in ps
    assert "-Credential" in ps                    # test wykonywany JAKO agent
    assert "(N)" in ps and "[int]$r.FileSystemRights -eq 0" in ps    # pusty wpis: zezwolenie bez praw
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
