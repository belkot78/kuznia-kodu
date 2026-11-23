"""Testy hookow git z .githooks/ na atrapie repo w katalogu tymczasowym (offline, dane syntetyczne).

Hooki sa skryptami sh uruchamianymi przez git (core.hooksPath), bez PowerShella.
Uruchom:  python -m pytest tools/tests/test_hooki.py
"""
import os
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

KORZEN = Path(__file__).resolve().parents[2]
CIAG = "A1b2C3d4E5f6G7h8I9j0K1l2M3n4O5p6Q7r8"

pytestmark = pytest.mark.skipif(shutil.which("git") is None or shutil.which("sh") is None,
                                reason="wymaga git i sh w PATH")


def git(repo, *argumenty, sprawdz=True):
    return subprocess.run(["git", "-C", str(repo), "-c", "user.name=t", "-c", "user.email=t@example.org",
                           *argumenty], capture_output=True, text=True, encoding="utf-8", errors="replace",
                          check=sprawdz)


@pytest.fixture()
def repo(tmp_path):
    r = tmp_path / "atrapa"
    r.mkdir()
    git(r, "init", "-q")
    (r / "tools").mkdir()
    for nazwa in ("przeglad.py", "przeglad_konfig.py"):
        shutil.copy(KORZEN / "tools" / nazwa, r / "tools" / nazwa)
    shutil.copytree(KORZEN / ".githooks", r / ".githooks")
    for hook in (r / ".githooks").iterdir():     # LF w skryptach sh (autocrlf na Windows)
        hook.write_bytes(hook.read_bytes().replace(b"\r\n", b"\n"))
    git(r, "config", "core.hooksPath", ".githooks")
    (r / "tests").mkdir()
    (r / "tests" / "test_ok.py").write_text("def test_ok():\n    assert True\n", encoding="utf-8")
    return r


def zapisz(repo, rel, tresc):
    p = repo / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(tresc, encoding="utf-8")


def commit(repo, *pliki):
    git(repo, "add", "-f", *pliki)
    return git(repo, "commit", "-q", "-m", "test", sprawdz=False)


def test_commit_bez_sekretu_przechodzi(repo):
    zapisz(repo, "src/ok.py", "x = 1\n")
    w = commit(repo, "src/ok.py")
    assert w.returncode == 0, w.stderr


def test_commit_z_sekretem_jest_zablokowany_a_wartosc_nie_wycieka(repo):
    sekret = "sk-ant-" + CIAG
    zapisz(repo, "src/klucz.py", f"KLUCZ = '{sekret}'\n")
    w = commit(repo, "src/klucz.py")
    assert w.returncode != 0
    assert "COMMIT ZABLOKOWANY" in w.stderr
    assert sekret not in w.stdout + w.stderr and CIAG not in w.stdout + w.stderr


@pytest.mark.parametrize("rel", [".env", "data/baza.sqlite3", "dane/x.txt", "klucz.pem"])
def test_commit_zakazanych_plikow_jest_zablokowany(repo, rel):
    zapisz(repo, rel, "x\n")
    assert commit(repo, rel).returncode != 0


def test_skan_dotyczy_indeksu_a_nie_katalogu_roboczego(repo):
    zapisz(repo, "src/m.py", "x = 1\n")
    git(repo, "add", "src/m.py")
    zapisz(repo, "src/m.py", "has" "lo = '" + "Tajne" + "Haslo" + "123" + "'\n")   # tylko w katalogu roboczym
    assert git(repo, "commit", "-q", "-m", "test", sprawdz=False).returncode == 0


def path_bez_pythona(tmp_path):
    """PATH, w ktorym sh i git dzialaja, a interpretera Pythona nie ma (niezaleznie od systemu).

    Windows (Git Bash): katalogi sh i git nie maja pythona, wiec wystarcza same. Linux/macOS: sh i git leza w
    katalogu z python3, wiec budujemy osobny katalog z dowiazaniami tylko do potrzebnych polecen."""
    sh, git_exe = shutil.which("sh"), shutil.which("git")
    katalogi = {str(Path(sh).parent), str(Path(git_exe).parent)}
    nazwy_pythona = ("python", "python3", "py")
    ma_pythona = any((Path(k) / n).exists() or (Path(k) / (n + ".exe")).exists() for k in katalogi for n in nazwy_pythona)
    if not ma_pythona:
        return os.pathsep.join(sorted(katalogi))
    bin_ = tmp_path / "bin-bez-pythona"
    bin_.mkdir()
    for nazwa in ("sh", "git", "basename", "dirname"):
        zrodlo = shutil.which(nazwa)
        if zrodlo:
            (bin_ / nazwa).symlink_to(zrodlo)
    return str(bin_)


def test_brak_interpretera_blokuje_commit(repo, tmp_path):
    zapisz(repo, "src/ok.py", "x = 1\n")
    git(repo, "add", "-f", "src/ok.py")
    sh = shutil.which("sh")
    w = subprocess.run([sh, str(repo / ".githooks" / "pre-commit")], cwd=str(repo), capture_output=True,
                       text=True, env={"PATH": path_bez_pythona(tmp_path), "HOME": str(tmp_path / "pusty")})
    assert w.returncode != 0 and "BLAD INTERPRETERA" in w.stderr


def test_pre_push_pass_i_fail(repo):
    sh = shutil.which("sh")
    hook = str(repo / ".githooks" / "pre-push")
    # python z PATH nie musi miec pytesta: pakiety biezacego srodowiska udostepniamy przez PYTHONPATH
    env = {**os.environ, "PYTHONPATH": str(Path(pytest.__file__).resolve().parents[1])}
    assert subprocess.run([sh, hook], cwd=str(repo), capture_output=True, env=env).returncode == 0
    (repo / "tests" / "test_zly.py").write_text("def test_zly():\n    assert False\n", encoding="utf-8")
    w = subprocess.run([sh, hook], cwd=str(repo), capture_output=True, text=True, env=env)
    assert w.returncode != 0 and "PUSH ZABLOKOWANY" in w.stderr


def test_hooki_nie_uzywaja_powershella():
    for hook in (KORZEN / ".githooks").iterdir():
        tresc = hook.read_text(encoding="utf-8").lower()
        assert "powershell" not in tresc and ".ps1" not in tresc
        assert tresc.startswith("#!/bin/sh")
