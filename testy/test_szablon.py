"""Testy szablonu: wlasne testy szablonu przechodza, znaczniki sa spojne, wymagane pliki istnieja (offline)."""
import os
import re
import subprocess
import sys
from pathlib import Path

KORZEN = Path(__file__).resolve().parents[1]
SZABLON = KORZEN / "szablon"
ZNACZNIKI_DOZWOLONE = {"NAZWA", "POZIOM", "GALAZ", "VENV_PYTHON", "KOMENDA_PUSH", "OPIS", "DOPISZ"}

WYMAGANE = [
    "CLAUDE.md", ".gitignore", ".gitattributes", ".claude/settings.json",
    "docs/recenzja-projekt.md", "docs/wdrozenie.md", "docs/stan.md", "docs/porzadki.md",
    "docs/pakiety/_szablon-pakietu.md",
    "tools/przeglad.py", "tools/przeglad_konfig.py", "tools/requirements-dev.txt",
    "tools/tests/test_settings.py", "tools/tests/test_przeglad.py", "tools/tests/test_hooki.py",
    ".githooks/pre-commit", ".githooks/pre-push",
]


def test_szablon_ma_wymagane_pliki_ukladu_z_metody():
    brak = [p for p in WYMAGANE if not (SZABLON / p).is_file()]
    assert not brak, brak
    assert (KORZEN / "szablon-uzytkownika" / "CLAUDE.md").is_file()


def test_znaczniki_w_szablonie_sa_znane():
    """Znaczniki-identyfikatory (WIELKIE_LITERY, ewentualnie z `: opisem`) musza byc na liscie; pozostale
    {{...}} to opisowe placeholdery do uzupelnienia przez planiste."""
    nieznane = set()
    for p in SZABLON.rglob("*"):
        if p.is_file() and p.suffix in {".md", ".json", ".py", ".txt", ""} and "__pycache__" not in p.parts:
            for m in re.findall(r"\{\{([^}]*)\}\}", p.read_text(encoding="utf-8")):
                nazwa = m.split(":")[0]
                if re.fullmatch(r"[A-Z_]+", nazwa) and nazwa not in ZNACZNIKI_DOZWOLONE:
                    nieznane.add((p.name, m))
    assert not nieznane, nieznane


def test_markery_venv_i_galaz_sa_zgodne_w_settings_i_testach():
    s = (SZABLON / ".claude" / "settings.json").read_text(encoding="utf-8")
    t = (SZABLON / "tools" / "tests" / "test_settings.py").read_text(encoding="utf-8")
    assert "{{VENV_PYTHON}}" in s and "{{VENV_PYTHON}}" in t
    assert "{{GALAZ}}" in t


def test_szablon_przechodzi_wlasne_testy():
    env = {**os.environ, "PYTHONDONTWRITEBYTECODE": "1"}
    w = subprocess.run([sys.executable, "-m", "pytest", "-q", "-p", "no:cacheprovider", "--import-mode=importlib",
                        "tools/tests"], cwd=str(SZABLON), capture_output=True, text=True, encoding="utf-8",
                       errors="replace", timeout=280, env=env)
    assert w.returncode == 0, w.stdout[-2000:] + w.stderr[-500:]


def test_szablon_przeglad_na_samym_sobie_nie_zglasza_sekretow():
    """(b) skan sekretow na calym szablonie (bez uruchamiania testow)."""
    sys.path.insert(0, str(SZABLON / "tools"))
    try:
        import przeglad
        pliki = przeglad.lista_plikow(SZABLON)
        ok, uwagi = przeglad.kontrola_sekretow(SZABLON, pliki)
    finally:
        sys.path.remove(str(SZABLON / "tools"))
        sys.modules.pop("przeglad", None)
        sys.modules.pop("przeglad_konfig", None)
    assert ok, uwagi
