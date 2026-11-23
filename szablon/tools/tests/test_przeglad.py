"""Testy silnika tools/przeglad.py na atrapach w katalogach tymczasowych (offline, dane syntetyczne).

Sztuczne sekrety sa skladane z fragmentow w czasie testu, zeby ten plik sam nie wygladal jak wyciek.
Uruchom:  python -m pytest tools/tests/test_przeglad.py
"""
import subprocess
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))   # katalog tools
import przeglad  # noqa: E402

CIAG = "A1b2C3d4E5f6G7h8I9j0K1l2M3n4O5p6Q7r8"   # atrapa, 36 znakow z cyframi i literami


def zapisz(root, rel, tresc):
    p = Path(root) / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(tresc, encoding="utf-8")
    return rel


def skan(tmp_path, rel, tresc):
    zapisz(tmp_path, rel, tresc)
    return przeglad.kontrola_sekretow(tmp_path, [rel])


# ---------------------------------------------------------------- (b) sekrety
@pytest.mark.parametrize("tresc", [
    "KLUCZ = '" + "sk-ant-" + CIAG + "'\n",                       # klucz API Anthropic
    "x = '" + "sk-" + CIAG + "'\n",                               # klucz API OpenAI
    "x = '" + "AIza" + "SyA" + CIAG[:32] + "'\n",                 # klucz API Google
    "x = '" + "ghp_" + CIAG + "'\n",                              # token GitHub
    "-----" + "BEGIN RSA " + "PRIVATE KEY-----\n",                # klucz prywatny
    "has" "lo = '" + "Tajne" + "Haslo" + "123" + "'\n",              # literal przypisany do nazwy sekretu
])
def test_sekret_w_pliku_tymczasowym(tmp_path, tresc):
    ok, uwagi = skan(tmp_path, "src/modul.py", tresc)
    assert not ok, uwagi


def test_wartosc_bez_nazwy_sekretu_nie_jest_sekretem(tmp_path):
    assert skan(tmp_path, "src/m.py", "pole = '" + "abc123def456ghi789" + "'\n")[0]


def test_komunikat_nie_zawiera_wartosci_sekretu(tmp_path):
    sekret = "sk-ant-" + CIAG
    ok, uwagi = skan(tmp_path, "src/m.py", f"KLUCZ = '{sekret}'\n")
    assert not ok
    assert sekret not in " ".join(uwagi) and CIAG not in " ".join(uwagi)
    assert "src/m.py:1" in uwagi[0]


def test_sekret_bez_cudzyslowu_w_yaml_i_sh(tmp_path):
    assert not skan(tmp_path, "config.yaml", "haslo: " + "abc123def456ghi\n")[0]
    assert not skan(tmp_path, "run.sh", "export API_" + "TOKEN=" + "abc123def456ghi\n")[0]


@pytest.mark.parametrize("tresc", [
    "KLUCZ = os.environ['X']\n",
    "haslo = pobierz_haslo()\n",
    "token = '<wstaw-token>'\n",
    "password = 'zmien_mnie'\n",
    "secret = 'przyklad-synt-1234567890'\n",
    "token: str\n",
])
def test_brak_alarmu_dla_atrap_i_wywolan(tmp_path, tresc):
    ok, uwagi = skan(tmp_path, "src/m.py", tresc)
    assert ok, uwagi


@pytest.mark.parametrize("rel", [".env", ".env.local", "data/baza.sqlite3", "data/baza.sqlite3-wal", "a.db",
                                 "klucz.pem", "klucz.key", "dane/x.txt", "archiwum.zip", "venv/x.py"])
def test_zakazane_nazwy_plikow_i_folderow(tmp_path, rel):
    zapisz(tmp_path, rel, "x\n")
    ok, uwagi = przeglad.kontrola_sekretow(tmp_path, [rel])
    assert not ok and "zakazany plik lub folder" in uwagi[0]


def test_env_example_jest_dozwolony(tmp_path):
    assert skan(tmp_path, ".env.example", "PORT=8000\n")[0]


def test_wyjatek_sekretu_dotyczy_pliku_nazwy_i_literalu(tmp_path, monkeypatch):
    monkeypatch.setitem(przeglad.WYJATKI_SEKRETY, "src/ui.py", {("token", "Pokaz token")})
    assert skan(tmp_path, "src/ui.py", "tok" "en = 'Pokaz token'\n")[0]
    assert not skan(tmp_path, "src/ui.py", "tok" "en = 'Inny literal'\n")[0]
    assert not skan(tmp_path, "src/inny.py", "tok" "en = 'Pokaz token'\n")[0]


def test_tryb_indeksu_czyta_zawartosc_indeksu(tmp_path):
    git(tmp_path, "init", "-q")
    zapisz(tmp_path, "src/m.py", "x = 1\n")
    git(tmp_path, "add", "src/m.py")
    zapisz(tmp_path, "src/m.py", "has" "lo = '" + "Tajne" + "Haslo" + "123" + "'\n")   # tylko w katalogu roboczym
    wyjscia = []
    assert przeglad.uruchom(tmp_path, "b", wypis=wyjscia.append, indeks=True)
    git(tmp_path, "add", "src/m.py")
    assert not przeglad.uruchom(tmp_path, "b", wypis=wyjscia.append, indeks=True)


def test_indeks_obsluguje_tylko_kontrole_b(tmp_path):
    with pytest.raises(ValueError):
        przeglad.uruchom(tmp_path, "a", indeks=True)


# ---------------------------------------------------------------- (c) importy i adresy
def test_import_spoza_zaleznosci_daje_alarm(tmp_path):
    rel = zapisz(tmp_path, "src/m.py", "import requests_obcy\nimport json\n")
    ok, uwagi = przeglad.kontrola_importow_i_adresow(tmp_path, [rel], [rel])
    assert not ok and "requests_obcy" in uwagi[0]


def test_import_z_pyproject_toml_jest_dozwolony(tmp_path):
    zapisz(tmp_path, "pyproject.toml", '[project]\nname = "x"\ndependencies = ["fastapi>=0.1", "python-multipart"]\n'
                                       '[project.optional-dependencies]\ndev = ["pytest"]\n')
    rel = zapisz(tmp_path, "src/m.py", "import fastapi\nimport multipart\nimport pytest\n")
    assert przeglad.kontrola_importow_i_adresow(tmp_path, [rel], [rel])[0]


def test_import_z_requirements_gdy_brak_pyproject(tmp_path):
    zapisz(tmp_path, "tools/requirements-dev.txt", "# komentarz\npyyaml>=6\n")
    rel = zapisz(tmp_path, "src/m.py", "import yaml\n")
    assert przeglad.kontrola_importow_i_adresow(tmp_path, [rel], [rel])[0]


def test_uszkodzony_pyproject_nie_wywala_kontroli(tmp_path):
    zapisz(tmp_path, "pyproject.toml", "to nie jest toml [[[")
    rel = zapisz(tmp_path, "src/m.py", "import json\n")
    assert przeglad.kontrola_importow_i_adresow(tmp_path, [rel], [rel])[0]


def test_adres_spoza_listy_hostow(tmp_path):
    rel = zapisz(tmp_path, "src/m.py", 'A = "https://obcy.invalid/api"\nB = "http://localhost:8000"\n')
    ok, uwagi = przeglad.kontrola_importow_i_adresow(tmp_path, [rel], [rel])
    assert not ok and "obcy.invalid" in uwagi[0] and len(uwagi) == 1


def test_nasluch_na_wszystkich_interfejsach(tmp_path):
    rel = zapisz(tmp_path, "src/m.py", "HOST = '" + "0.0.0." + "0" + "'\n")
    ok, uwagi = przeglad.kontrola_importow_i_adresow(tmp_path, [rel], [rel])
    assert not ok and "nasluch" in uwagi[0]


# ---------------------------------------------------------------- (d) niebezpieczne wywolania
@pytest.mark.parametrize("kod,nazwa", [
    ("eval('1')", "eval"), ("exec('x=1')", "exec"), ("import os\nos.system('x')", "os.system"),
    ("import os as o\no.popen('x')", "os.popen"), ("import subprocess\nsubprocess.run(['x'])", "subprocess.run"),
    ("from subprocess import Popen\nPopen(['x'])", "subprocess.Popen"),
])
def test_niebezpieczne_wywolania(tmp_path, kod, nazwa):
    zapisz(tmp_path, "src/m.py", kod + "\n")
    ok, uwagi = przeglad.kontrola_niebezpiecznych(tmp_path, ["src/m.py"])
    assert not ok and nazwa in uwagi[0]


def test_wyjatek_wywolania_dotyczy_pliku(tmp_path, monkeypatch):
    monkeypatch.setitem(przeglad.WYJATKI_D, "src/dozwolony.py", {"subprocess.run"})
    zapisz(tmp_path, "src/dozwolony.py", "import subprocess\nsubprocess.run(['x'])\n")
    zapisz(tmp_path, "src/inny.py", "import subprocess\nsubprocess.run(['x'])\n")
    assert przeglad.kontrola_niebezpiecznych(tmp_path, ["src/dozwolony.py"])[0]
    assert not przeglad.kontrola_niebezpiecznych(tmp_path, ["src/inny.py"])[0]


def test_wywolania_poza_katalogami_d_sa_pomijane(tmp_path):
    zapisz(tmp_path, "inne/m.py", "eval('1')\n")
    assert przeglad.kontrola_niebezpiecznych(tmp_path, ["inne/m.py"])[0]


# ---------------------------------------------------------------- (a) testy i calosc
def git(root, *argumenty):
    return subprocess.run(["git", "-C", str(root), "-c", "user.name=t", "-c", "user.email=t@example.org",
                           *argumenty], capture_output=True, text=True, check=True)


def test_testy_tylko_z_bialej_listy(tmp_path):
    zapisz(tmp_path, "tests/test_ok.py", "def test_ok():\n    assert True\n")
    zapisz(tmp_path, "inne/test_poza_lista.py", "def test_zle():\n    assert False\n")
    ok, uwagi = przeglad.kontrola_testow(tmp_path, ["tests/test_ok.py", "inne/test_poza_lista.py"])
    assert ok, uwagi


def test_failujacy_test_daje_fail(tmp_path):
    zapisz(tmp_path, "tests/test_zly.py", "def test_zly():\n    assert False\n")
    ok, uwagi = przeglad.kontrola_testow(tmp_path, ["tests/test_zly.py"])
    assert not ok and "kod wyjscia" in uwagi[0]


def test_brak_testow_to_fail(tmp_path):
    assert not przeglad.kontrola_testow(tmp_path, ["src/m.py"])[0]


def test_uruchom_calosc_pass_i_fail(tmp_path):
    zapisz(tmp_path, "tests/test_ok.py", "def test_ok():\n    assert True\n")
    zapisz(tmp_path, "src/m.py", "x = 1\n")
    wyjscie = []
    assert przeglad.uruchom(tmp_path, "abcd", wypis=wyjscie.append)
    assert wyjscie[-1] == "WYNIK: PASS"
    zapisz(tmp_path, "src/zly.py", "eval('1')\n")
    wyjscie.clear()
    assert not przeglad.uruchom(tmp_path, "abcd", wypis=wyjscie.append)
    assert wyjscie[-1] == "WYNIK: FAIL"


def test_nieznana_kontrola_to_blad(tmp_path):
    with pytest.raises(ValueError):
        przeglad.uruchom(tmp_path, "z", wypis=lambda *_: None)


def test_main_kod_wyjscia_2_przy_zlej_kontroli(tmp_path):
    assert przeglad.main(["--root", str(tmp_path), "--kontrole", "z"]) == 2


def test_repo_bez_commitow_wszystkie_pliki_sa_nowe(tmp_path):
    git(tmp_path, "init", "-q")
    zapisz(tmp_path, "a.py", "x = 1\n")
    assert przeglad.nowe_pliki(tmp_path, ["a.py"], None) == ["a.py"]
    git(tmp_path, "add", "a.py")
    git(tmp_path, "commit", "-q", "-m", "x")
    assert przeglad.nowe_pliki(tmp_path, ["a.py"], None) == []


def test_lista_plikow_w_repo_git_pomija_ignorowane(tmp_path):
    git(tmp_path, "init", "-q")
    zapisz(tmp_path, ".gitignore", ".env\n")
    zapisz(tmp_path, ".env", "X=1\n")
    zapisz(tmp_path, "a.py", "x = 1\n")
    assert przeglad.lista_plikow(tmp_path) == [".gitignore", "a.py"]


def test_pliki_z_polskimi_znakami_w_nazwie_sa_kontrolowane(tmp_path):
    """git bez -z cytuje takie sciezki; plik wypadalby z kontroli (fail-open)."""
    git(tmp_path, "init", "-q")
    rel_dane = "dane/ha\u015blo.txt"
    rel_src = "src/za\u017c\u00f3\u0142\u0107.py"
    zapisz(tmp_path, rel_dane, "x\n")
    zapisz(tmp_path, rel_src, "x = 1\n")
    assert przeglad.lista_plikow(tmp_path) == sorted([rel_dane, rel_src])
    git(tmp_path, "add", "-f", rel_dane, rel_src)
    assert przeglad.pliki_z_indeksu(tmp_path) == sorted([rel_dane, rel_src])
    ok, uwagi = przeglad.kontrola_sekretow(tmp_path, [rel_dane])
    assert not ok and "zakazany plik lub folder" in uwagi[0]
    assert not przeglad.uruchom(tmp_path, "b", wypis=lambda *_: None, indeks=True)


def test_sekret_w_pliku_z_polska_nazwa_jest_wykryty_w_indeksie(tmp_path):
    git(tmp_path, "init", "-q")
    rel = "src/za\u017c\u00f3\u0142\u0107.py"
    zapisz(tmp_path, rel, "KLUCZ = '" + "sk-ant-" + CIAG + "'\n")
    git(tmp_path, "add", rel)
    assert not przeglad.uruchom(tmp_path, "b", wypis=lambda *_: None, indeks=True)
