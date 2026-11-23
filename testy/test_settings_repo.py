"""Ustawienia tego repo (.claude/settings.json) po nalozeniu docs/po-pk-m0.patch musza byc zgodne z szablonem.

Przed nalozeniem lacznika w repo jest tymczasowy plik startowy (bez pluginu): test jest wtedy pomijany.
Po nalozeniu (robi Pawel po pushu) sprawdza, ze listy allow/deny/ask i wpisy pluginu sa takie jak w szablonie
po podstawieniu znacznikow ({{VENV_PYTHON}}, {{GALAZ}}).
"""
import json
import subprocess
from pathlib import Path

import pytest

KORZEN = Path(__file__).resolve().parents[1]
USTAWIENIA = KORZEN / ".claude" / "settings.json"
SZABLON = KORZEN / "szablon" / ".claude" / "settings.json"
PATCH = KORZEN / "docs" / "po-pk-m0.patch"
VENV_PYTHON = "/c/Users/claude-agent/.venvs/kuznia-kodu/Scripts/python.exe"


def wczytaj(p):
    return json.loads(p.read_text(encoding="utf-8"))


def oczekiwane():
    tekst = SZABLON.read_text(encoding="utf-8").replace("{{VENV_PYTHON}}", VENV_PYTHON)
    return json.loads(tekst)


def git(*argumenty):
    return subprocess.run(["git", "-c", f"safe.directory={KORZEN.as_posix()}", "-C", str(KORZEN), *argumenty],
                          capture_output=True, text=True, encoding="utf-8", errors="replace")


def czy_docelowe():
    return "enabledPlugins" in wczytaj(USTAWIENIA)


def test_lacznik_po_pk_m0_istnieje_i_jest_poprawny():
    """Albo jeszcze nienalozony (git apply --check przechodzi), albo juz nalozony (przechodzi odwrotnie)."""
    assert PATCH.is_file()
    nalozony = git("apply", "--check", "-R", str(PATCH)).returncode == 0
    nienalozony = git("apply", "--check", str(PATCH)).returncode == 0
    assert nalozony or nienalozony


def test_lacznik_zmienia_tylko_ustawienia_i_gitignore():
    pliki = [l.split(" b/")[-1] for l in PATCH.read_text(encoding="utf-8").splitlines() if l.startswith("diff --git")]
    assert sorted(pliki) == [".claude/settings.json", ".gitignore"]


def test_lacznik_usuwa_wpis_o_tymczasowej_kopii_recenzenta():
    tekst = PATCH.read_text(encoding="utf-8")
    assert "-.claude/agents/" in tekst
    assert "enabledPlugins" in tekst


def test_ustawienia_po_nalozeniu_lacznika_zgodne_z_szablonem():
    if not czy_docelowe():
        pytest.skip("tymczasowe ustawienia startowe: lacznik docs/po-pk-m0.patch jeszcze nienalozony")
    obecne, wzor = wczytaj(USTAWIENIA), oczekiwane()
    for klucz in ("model", "deniedMcpServers", "extraKnownMarketplaces", "enabledPlugins"):
        assert obecne[klucz] == wzor[klucz], klucz
    for lista in ("allow", "deny", "ask"):
        assert sorted(obecne["permissions"][lista]) == sorted(wzor["permissions"][lista]), lista
    assert obecne["permissions"]["defaultMode"] == "acceptEdits"
    assert "hooks" not in obecne
