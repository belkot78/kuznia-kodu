"""Ustawienia tego repo (.claude/settings.json) musza byc zgodne z szablonem po podstawieniu znacznikow.

`.claude/` jest plikiem kontrolnym (blokada zapisu dla agenta), wiec zmiany w szablonie dochodza tu lacznikiem
`docs/pakiety/PK-M0.1-claude.patch`, ktory naklada Pawel. Dopoki lacznik jest nienalozony (`git apply --check`
przechodzi w przod), test zgodnosci jest pomijany z jawnym komunikatem; po nalozeniu (albo gdy lacznik juz nie pasuje)
zgodnosc jest wymagana bez wyjatkow.
"""
import json
import subprocess
from pathlib import Path

import pytest

KORZEN = Path(__file__).resolve().parents[1]
USTAWIENIA = KORZEN / ".claude" / "settings.json"
SZABLON = KORZEN / "szablon" / ".claude" / "settings.json"
LACZNIK = KORZEN / "docs" / "pakiety" / "PK-M0.1-claude.patch"
VENV_PYTHON = "/c/Users/claude-agent/.venvs/kuznia-kodu/Scripts/python.exe"


def wczytaj(p):
    return json.loads(p.read_text(encoding="utf-8"))


def oczekiwane():
    tekst = SZABLON.read_text(encoding="utf-8").replace("{{VENV_PYTHON}}", VENV_PYTHON)
    return json.loads(tekst)


def git(*argumenty):
    return subprocess.run(["git", "-c", f"safe.directory={KORZEN.as_posix()}", "-C", str(KORZEN), *argumenty],
                          capture_output=True, text=True, encoding="utf-8", errors="replace")


def lacznik_nienalozony():
    return LACZNIK.is_file() and git("apply", "--check", str(LACZNIK)).returncode == 0


def test_lacznik_claude_zmienia_tylko_ustawienia():
    if not LACZNIK.is_file():
        pytest.skip("lacznik PK-M0.1-claude.patch juz nalozony i usuniety")
    pliki = [l.split(" b/")[-1] for l in LACZNIK.read_text(encoding="utf-8").splitlines() if l.startswith("diff --git")]
    assert pliki == [".claude/settings.json"]


def test_lacznik_claude_jest_poprawny():
    """Albo nienalozony (git apply --check przechodzi), albo juz nalozony (przechodzi odwrotnie)."""
    if not LACZNIK.is_file():
        pytest.skip("lacznik PK-M0.1-claude.patch usuniety po nalozeniu")
    nalozony = git("apply", "--check", "-R", str(LACZNIK)).returncode == 0
    assert nalozony or lacznik_nienalozony()


def test_ustawienia_repo_zgodne_z_szablonem():
    if lacznik_nienalozony():
        pytest.skip("OCZEKUJE NA PAWLA: docs/pakiety/PK-M0.1-claude.patch jeszcze nienalozony (git apply)")
    obecne, wzor = wczytaj(USTAWIENIA), oczekiwane()
    for klucz in ("model", "deniedMcpServers", "extraKnownMarketplaces", "enabledPlugins"):
        assert obecne[klucz] == wzor[klucz], klucz
    for lista in ("allow", "deny", "ask"):
        assert sorted(obecne["permissions"][lista]) == sorted(wzor["permissions"][lista]), lista
    assert obecne["permissions"]["defaultMode"] == "acceptEdits"
    assert "hooks" not in obecne
