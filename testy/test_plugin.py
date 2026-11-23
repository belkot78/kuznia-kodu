"""Testy statyczne pluginu kuznia: JSON marketplace i pluginu, agent, skille, hooki (offline)."""
import json
import re
from pathlib import Path

import pytest

KORZEN = Path(__file__).resolve().parents[1]
SKILLE = ["pakiet", "status", "nowy-projekt", "przenies", "retro"]


def frontmatter(sciezka):
    tekst = sciezka.read_text(encoding="utf-8")
    m = re.match(r"---\r?\n(.*?)\r?\n---\r?\n", tekst, re.S)
    assert m, f"{sciezka.name}: brak frontmattera"
    pola = {}
    for linia in m.group(1).splitlines():
        k, _, v = linia.partition(":")
        pola[k.strip()] = v.strip()
    return pola, tekst[m.end():]


def wczytaj(rel):
    return json.loads((KORZEN / rel).read_text(encoding="utf-8"))


def test_marketplace_json():
    m = wczytaj(".claude-plugin/marketplace.json")
    assert m["name"] == "kuznia-kodu"
    assert m["owner"]["name"]
    assert [p["name"] for p in m["plugins"]] == ["kuznia"]
    assert m["plugins"][0]["source"] == "./"   # caly katalog repo jest pluginem (szablony w srodku)


def test_plugin_json_zgodny_z_marketplace():
    p = wczytaj(".claude-plugin/plugin.json")
    m = wczytaj(".claude-plugin/marketplace.json")
    assert p["name"] == m["plugins"][0]["name"] == "kuznia"
    assert re.fullmatch(r"\d+\.\d+\.\d+", p["version"])


def test_agent_recenzent():
    pola, tresc = frontmatter(KORZEN / "agents" / "recenzent.md")
    assert pola["name"] == "recenzent"
    assert pola["model"] == "opus"
    assert pola["tools"] == "Read, Grep, Glob"
    assert pola["description"]
    assert "docs/recenzja-projekt.md" in tresc
    assert ".recenzja/diff.patch" in tresc
    for waga in ("BLOKUJACE", "UWAGA", "SUGESTIA", "ZATWIERDZAM", "ODRZUCAM"):
        assert waga in tresc


@pytest.mark.parametrize("nazwa", SKILLE)
def test_skill_ma_poprawny_frontmatter(nazwa):
    pola, tresc = frontmatter(KORZEN / "skills" / nazwa / "SKILL.md")
    assert pola["name"] == nazwa
    assert pola["description"]
    assert tresc.strip()


def test_brak_nieoczekiwanych_skilli():
    katalogi = sorted(p.name for p in (KORZEN / "skills").iterdir() if p.is_dir())
    assert katalogi == sorted(SKILLE)


@pytest.mark.parametrize("nazwa", SKILLE)
def test_skille_wywolywane_tylko_przez_pawla(nazwa):
    pola, _ = frontmatter(KORZEN / "skills" / nazwa / "SKILL.md")
    assert pola.get("disable-model-invocation") == "true"


def test_skill_pakiet_zawiera_zasady_metody():
    _, tresc = frontmatter(KORZEN / "skills" / "pakiet" / "SKILL.md")
    for fragment in ("docs/porzadki.md", ".recenzja/diff.patch", "Najwyżej jedna dodatkowa runda", "dalej",
                     "@{upstream}", "kuznia:recenzent", "ASCII", "sekret", "NIE poszerzaj allow"):
        assert fragment in tresc, fragment
    assert "praca.md" not in tresc            # R4: brak praca.md
    assert "PK-07" not in tresc               # odlozone uwagi tylko w docs/porzadki.md


def test_skill_status_tylko_odczyt():
    _, tresc = frontmatter(KORZEN / "skills" / "status" / "SKILL.md")
    assert "Tylko odczyt" in tresc
    for zakazane in ("git add", "git commit", "git push"):
        assert f"`{zakazane}" not in tresc


def test_skill_przenies_niczego_nie_instaluje():
    _, tresc = frontmatter(KORZEN / "skills" / "przenies" / "SKILL.md")
    assert "Niczego nie instalujesz" in tresc


def test_skill_nowy_projekt_wskazuje_szablon_w_pluginie():
    _, tresc = frontmatter(KORZEN / "skills" / "nowy-projekt" / "SKILL.md")
    assert "${CLAUDE_PLUGIN_ROOT}/szablon/" in tresc
    for poziom in ("P0", "P1", "P2"):
        assert poziom in tresc


def test_skill_retro_nie_zmienia_metody_samodzielnie():
    _, tresc = frontmatter(KORZEN / "skills" / "retro" / "SKILL.md")
    assert "tylko Paweł" in tresc
    assert "CHANGELOG.md" in tresc


def test_hooks_json_tylko_python():
    h = wczytaj("hooks/hooks.json")["hooks"]
    assert set(h) == {"PostToolUse", "Stop"}
    komendy = [x["command"] for wpis in (h["PostToolUse"] + h["Stop"]) for x in wpis["hooks"]]
    assert len(komendy) == 2
    for k in komendy:
        assert k.startswith('python "${CLAUDE_PLUGIN_ROOT}/hooks/kontrola.py"')
        assert "powershell" not in k.lower() and ".ps1" not in k
    assert h["PostToolUse"][0]["matcher"] == "Edit|Write|MultiEdit"
    assert (KORZEN / "hooks" / "kontrola.py").is_file()


def test_plugin_nie_dostarcza_uprawnien():
    """Uprawnien plugin nie przenosi (FACT z METODA §5): zadnego settings.json w katalogu glownym pluginu."""
    assert not (KORZEN / "settings.json").exists()
    for rel in (".claude-plugin/plugin.json", ".claude-plugin/marketplace.json", "hooks/hooks.json"):
        assert "permissions" not in wczytaj(rel)
