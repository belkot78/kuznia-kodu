"""Testy statyczne pluginu kuznia: JSON marketplace i pluginu, agent, skille, hooki (offline)."""
import json
import os
import re
import shutil
import subprocess
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


def test_hooks_json_przez_przenosny_launcher():
    """Hook `command` idzie na Windows przez Git Bash, a na Linuksie przez sh: launcher wybiera python3/python/py."""
    h = wczytaj("hooks/hooks.json")["hooks"]
    assert set(h) == {"PostToolUse", "Stop"}
    komendy = [x["command"] for wpis in (h["PostToolUse"] + h["Stop"]) for x in wpis["hooks"]]
    assert len(komendy) == 2
    for k in komendy:
        assert k.startswith('sh "${CLAUDE_PLUGIN_ROOT}/hooks/uruchom.sh"')     # placeholder w cudzyslowie
        assert not k.startswith("python") and "powershell" not in k.lower() and ".ps1" not in k
    assert h["PostToolUse"][0]["matcher"] == "Edit|Write|MultiEdit"
    assert (KORZEN / "hooks" / "kontrola.py").is_file()


def test_launcher_hookow_wybiera_interpreter_i_przekazuje_argumenty():
    tresc = (KORZEN / "hooks" / "uruchom.sh").read_text(encoding="utf-8")
    assert tresc.startswith("#!/bin/sh") and "\r" not in tresc
    assert "python3 python py" in tresc
    assert 'exec "$kandydat" "$KATALOG/kontrola.py" "$@"' in tresc          # stdin i argumenty bez zmian
    assert "exit 1" in tresc                                                 # brak interpretera: blad nieblokujacy
    assert "powershell" not in tresc.lower()


def test_launcher_hookow_ma_poprawna_skladnie_i_uruchamia_kontrole(tmp_path):
    sh = shutil.which("sh")
    if not sh:
        pytest.skip("brak sh w PATH")
    launcher = KORZEN / "hooks" / "uruchom.sh"
    assert subprocess.run([sh, "-n", str(launcher)], capture_output=True).returncode == 0
    w = subprocess.run([sh, str(launcher), "post"], input='{"tool_input": {}}', capture_output=True, text=True,
                       cwd=str(tmp_path), env={**os.environ, "CLAUDE_PROJECT_DIR": str(tmp_path)})
    assert w.returncode == 0, w.stderr


def test_plugin_nie_dostarcza_uprawnien():
    """Uprawnien plugin nie przenosi (FACT z METODA §5): zadnego settings.json w katalogu glownym pluginu."""
    assert not (KORZEN / "settings.json").exists()
    for rel in (".claude-plugin/plugin.json", ".claude-plugin/marketplace.json", "hooks/hooks.json"):
        assert "permissions" not in wczytaj(rel)


def test_wersja_pluginu_0_4_0():
    assert wczytaj(".claude-plugin/plugin.json")["version"] == "0.4.0"


def test_skill_nowy_projekt_ma_kolejnosc_plugin_przed_blokadami():
    _, tresc = frontmatter(KORZEN / "skills" / "nowy-projekt" / "SKILL.md")
    sekcja = tresc[tresc.index("## 3. Plugin"):tresc.index("## 4. Sprawdź")]
    assert sekcja.index("claude plugin install") < sekcja.index("Przywróć plik: `git checkout -- .claude/settings.json`")
    assert tresc.index("## 3. Plugin") < tresc.index("windows.ps1 -Repo") < tresc.index("-TestAgenta")
    for fragment in ("▶ WKLEJ", "👁 POWINIENEŚ ZOBACZYĆ", "claude-agent", "Belkot", "safe.directory", ".gitattributes"):
        assert fragment in tresc, fragment


def test_skill_status_ostrzega_o_kolejnosci_kluczy_i_wersji_pluginu():
    _, tresc = frontmatter(KORZEN / "skills" / "status" / "SKILL.md")
    assert "git checkout -- .claude/settings.json" in tresc and "kolejnością kluczy" in tresc
    assert "plugin.json" in tresc and "nie wiem" in tresc


def test_skill_pakiet_ma_konwencje_krokow_pawla_i_lacznik_z_blokadami():
    _, tresc = frontmatter(KORZEN / "skills" / "pakiet" / "SKILL.md")
    assert "▶ WKLEJ" in tresc and "👁 POWINIENEŚ ZOBACZYĆ" in tresc
    assert "-TestAgenta" in tresc and "ponowne założenie blokad" in tresc


def test_launcher_pomija_niedzialajacy_interpreter(tmp_path):
    """Zaslepka (np. python3 ze sklepu Microsoft) jest znaleziona, ale sie nie uruchamia: launcher idzie dalej."""
    sh = shutil.which("sh")
    if not sh:
        pytest.skip("brak sh w PATH")
    tresc = (KORZEN / "hooks" / "uruchom.sh").read_text(encoding="utf-8")
    assert '"$kandydat" -c "import sys"' in tresc
    zaslepka = tmp_path / "python3"
    zaslepka.write_text("#!/bin/sh\nexit 9\n", encoding="utf-8", newline="\n")
    zaslepka.chmod(0o755)
    env = {**os.environ, "PATH": str(tmp_path) + os.pathsep + os.environ["PATH"], "CLAUDE_PROJECT_DIR": str(tmp_path)}
    w = subprocess.run([sh, str(KORZEN / "hooks" / "uruchom.sh"), "post"], input='{"tool_input": {}}',
                       capture_output=True, text=True, cwd=str(tmp_path), env=env)
    assert w.returncode == 0, w.stderr
