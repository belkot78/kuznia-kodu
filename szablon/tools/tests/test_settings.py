"""Testy statyczne .claude/settings.json (wzor: metoda kuznia-kodu).

Sprawdzaja TEKST regul (allow/deny/ask) i wpisy pluginu oraz deniedMcpServers, nie dzialanie dopasowania w Claude
Code: tego nie da sie tu przetestowac. Granice dostepu pilnuje konto systemowe `claude-agent`, a ten plik pilnuje
granic ustawien: allow to tylko odczyt gita i testy, brak git push/add/commit w allow, komplet deny (sekrety,
push --force, pomijanie hooka commit, zapis w plikach konfiguracji i kontroli), ask na edycji plikow konfiguracji
i kontroli oraz blokada zdalnych serwerow MCP. Listy allow, deny i ask maja byc DOKLADNIE takie jak tutaj
(kazda zmiana = zmiana tego pliku, czyli swiadoma decyzja Pawla).

Uruchom:  python -m pytest tools/tests/test_settings.py
Znaczniki {{...}} uzupelnia skill /kuznia:nowy-projekt.
"""
import json
from pathlib import Path

import pytest

USTAWIENIA = Path(__file__).resolve().parents[2] / ".claude" / "settings.json"
USTAWIENIA_LOKALNE = USTAWIENIA.with_name("settings.local.json")

VENV_PYTHON = "{{VENV_PYTHON}}"          # np. /c/Users/claude-agent/.venvs/<nazwa>/Scripts/python.exe
GALAZ_ROBOCZA = "{{GALAZ}}"              # "main" (domyslnie) albo "dev"
WARIANT_DEV = GALAZ_ROBOCZA == "dev"

# --- allow: tylko odczyt gita i testy/przeglad. Bez golych Glob/Grep/Read/Edit.
GIT_BRANCH_DOKLADNIE = ["git branch", "git branch -a", "git branch --show-current"]
INTERPRETERY = ["python", ".venv/Scripts/python.exe", VENV_PYTHON]
POLECENIA_PYTHONA = ["-m pytest *", "tools/przeglad.py *", "tools/tests/test_*.py *"]
WYMAGANE_ALLOW = (["Bash(git status *)", "Bash(git log *)", "Bash(git diff *)", "Bash(git show *)"]
                  + [f"Bash({b})" for b in GIT_BRANCH_DOKLADNIE] + ["Bash(git rev-parse *)"]
                  + [f"Bash({i} {p})" for i in INTERPRETERY for p in POLECENIA_PYTHONA])

# --- deny
DENY_NARZEDZIE_POWERSHELL = ["PowerShell"]   # narzedzie PowerShell wylaczone (reguly deny sa typu Bash(...))
# Reguly deny nie maja wyjatkow, wiec .env.example (sledzony) zostaje poza lista, a warianty .env sa wyliczone.
DENY_ODCZYT = [
    "Read(**/.env)", "Read(**/.env.local)", "Read(**/.env.*.local)", "Read(**/.env.prod*)", "Read(**/.env.dev*)",
    "Read(**/.env.test*)", "Read(**/.env.staging*)", "Read(**/.env.bak*)", "Read(**/.env.backup*)",
    "Read(**/.env.old*)", "Read(**/.env.secrets*)", "Read(**/.env.ci*)",
    "Read(**/lokalne.yaml)", "Read(**/settings.local.json)",
    "Read(**/*.sqlite3*)", "Read(**/*.sqlite)", "Read(**/*.db)",
    "Read(**/*.pem)", "Read(**/*.key)", "Read(**/dane/**)",
]
DENY_PUSH = ["Bash(git push --force *)", "Bash(git push -f *)", "Bash(git push *--force*)"]
# `git diff --no-index <plik> NUL` czyta dowolny plik z dysku i omija deny odczytu (git diff * jest w allow)
DENY_DIFF_NO_INDEX = ["Bash(git diff *--no-index*)"]
# zapis dowolnych plikow przez git/pytest (git log/diff/show * w allow obejmuje --output, pytest --basetemp
# czysci katalog, --junitxml nadpisuje plik, -p laduje plugin)
DENY_ZAPIS_PRZEZ_NARZEDZIA = ["Bash(git * --output*)", "Bash(* --basetemp*)", "Bash(* --junitxml*)",
                              "Bash(* pytest * -p *)"]
# wariant dev: agent pracuje na dev; bez przelaczania, scalania, rebase i reset na main i tagach, bez tagow
POLECENIA_GALEZI = ["checkout", "switch", "merge", "rebase", "reset"]
DENY_MAIN_I_TAGI = []
for _c in POLECENIA_GALEZI:
    DENY_MAIN_I_TAGI += [f"Bash(git {_c} *main*)", f"Bash(git {_c} *tags/*)", f"Bash(git {_c} v*)",
                         f"Bash(git {_c} * v*)", f"Bash(git -* {_c} *)"]
DENY_MAIN_I_TAGI += ["Bash(git branch *main*)", "Bash(git tag*)", "Bash(git -* tag*)"]
# pomijanie hooka commit
DENY_POMIJANIE_HOOKA = [
    "Bash(git commit *--no-verify*)", "Bash(git commit *--no-v*)", "Bash(git commit -n*)",
    "Bash(git commit * -n *)", "Bash(git commit * -n)", "Bash(git commit *-an*)", "Bash(git commit *-na*)",
    "Bash(git commit *-qn*)", "Bash(git commit *-nq*)", "Bash(git commit *-sn*)", "Bash(git commit *-ns*)",
    "Bash(git commit *-nm*)", "Bash(git -* commit *)", "Bash(git *hooksPath*)",
]
# polecenia zapisu x sciezki konfiguracji i kontroli. Deny jest ZAWEZONE do polecen zapisu, a nie do samego
# tekstu sciezki: `Bash(*przeglad.py*)` zablokowaloby tez uruchamianie przeglad.py (deny ma pierwszenstwo
# przed allow).
POLECENIA_ZAPISU = ["rm", "rmdir", "mv", "cp", "sed", "touch", "mkdir"]
SCIEZKI_CHRONIONE = ["*.claude/settings*", "*.claude/hooks*", "*.claude/agents*", "*.claude/skills*",
                     "*.git/hooks*", "*.git/config*", "*.githooks*", "*przeglad.py*", "*przeglad_konfig*"]
DENY_ZAPIS_CHRONIONE = [f"Bash({w} {s})" for w in POLECENIA_ZAPISU for s in SCIEZKI_CHRONIONE]

WYMAGANE_DENY = (DENY_NARZEDZIE_POWERSHELL + DENY_ODCZYT + DENY_PUSH + DENY_DIFF_NO_INDEX
                 + DENY_ZAPIS_PRZEZ_NARZEDZIA
                 + (DENY_MAIN_I_TAGI if WARIANT_DEV else []) + DENY_POMIJANIE_HOOKA + DENY_ZAPIS_CHRONIONE)

# --- ask: push, add, commit i edycja plikow konfiguracji i kontroli
WYMAGANE_ASK = [
    "Bash(git push *)", "Bash(git add *)", "Bash(git commit *)",
    "Edit(/.claude/settings.json)", "Edit(/.claude/settings.local.json)", "Edit(/.claude/hooks/**)",
    "Edit(/.claude/agents/**)", "Edit(/.claude/skills/**)", "Edit(/.githooks/**)", "Edit(/tools/przeglad.py)",
    "Edit(/tools/przeglad_konfig.py)", "Edit(/tools/tests/test_settings.py)", "Edit(/.git/**)",
]


def _wczytaj():
    return json.loads(USTAWIENIA.read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def cala():
    return _wczytaj()


@pytest.fixture(scope="module")
def perm(cala):
    return cala["permissions"]


def test_model_i_tryb(cala, perm):
    assert cala["model"] == "sonnet"                    # wykonawca; recenzent ma model w agencie pluginu
    assert perm["defaultMode"] == "acceptEdits"


def test_allow_dokladnie_taki_jak_wymagany(perm):
    assert sorted(perm["allow"]) == sorted(WYMAGANE_ALLOW)


def test_allow_bez_golych_narzedzi_i_zapisu(perm):
    for r in perm["allow"]:
        assert r.startswith("Bash("), r
    for zakazane in ("git push", "git add", "git commit", "git reset", "git checkout", "git switch", "git merge",
                     "git rebase", "git tag", "git stash"):
        assert not [r for r in perm["allow"] if zakazane in r], zakazane
    assert not [r for r in perm["allow"] if "powershell" in r.lower()]


def test_git_branch_tylko_dokladne_formy_odczytu(perm):
    branch = [r for r in perm["allow"] if r.startswith("Bash(git branch")]
    assert sorted(branch) == sorted(f"Bash({b})" for b in GIT_BRANCH_DOKLADNIE)
    for r in branch:
        assert "*" not in r


def test_deny_dokladnie_taki_jak_wymagany(perm):
    assert sorted(perm["deny"]) == sorted(WYMAGANE_DENY)
    assert len(perm["deny"]) == len(set(perm["deny"]))   # bez duplikatow


def test_deny_zapisu_to_komplet_polecen_i_sciezek():
    assert len(DENY_ZAPIS_CHRONIONE) == len(POLECENIA_ZAPISU) * len(SCIEZKI_CHRONIONE)


def test_deny_zapisu_nie_blokuje_uruchamiania_przegladu(perm):
    """Deny ma pierwszenstwo przed allow: regula deny z nazwa pliku kontroli musi zaczynac sie od polecenia zapisu
    (inaczej `python tools/przeglad.py` i `git add` padna)."""
    for r in perm["deny"]:
        if "przeglad" in r or ".githooks" in r or ".claude/" in r:
            assert r.startswith("Bash("), r
            assert r[len("Bash("):-1].split()[0] in POLECENIA_ZAPISU, r


def test_deny_odczytu_sekretow_komplet(perm):
    for fragment in (".env", "sqlite", "*.db", "*.pem", "*.key", "dane/"):
        assert [r for r in perm["deny"] if r.startswith("Read(") and fragment in r], fragment


def test_deny_odczytu_wariantow_env_i_konfiguracji_lokalnej(perm):
    for r in ("Read(**/.env.secrets*)", "Read(**/.env.ci*)", "Read(**/lokalne.yaml)",
              "Read(**/settings.local.json)"):
        assert r in perm["deny"], r


def test_deny_git_diff_no_index(perm):
    """`git diff --no-index` omija deny odczytu (czyta dowolny plik), a `git diff *` jest w allow."""
    assert "Bash(git diff *--no-index*)" in perm["deny"]


def test_env_example_nie_jest_blokowany(perm):
    """Wzorce Read(.env...) nie moga obejmowac .env.example (sledzony szablon bez sekretow)."""
    for r in perm["deny"]:
        if r.startswith("Read(") and ".env" in r:
            assert "example" not in r
            assert r not in ("Read(**/.env*)", "Read(**/.env.*)")


def test_deny_push_i_pomijania_hooka(perm):
    for r in DENY_PUSH + DENY_POMIJANIE_HOOKA + DENY_ZAPIS_PRZEZ_NARZEDZIA:
        assert r in perm["deny"], r


def test_narzedzie_powershell_jest_w_deny(perm):
    assert "PowerShell" in perm["deny"]
    assert not [r for r in perm["deny"] if "powershell.exe" in r.lower()]


def test_deny_main_i_tagi_zalezy_od_wariantu(perm):
    obecne = [r for r in DENY_MAIN_I_TAGI if r in perm["deny"]]
    assert len(DENY_MAIN_I_TAGI) == 5 * len(POLECENIA_GALEZI) + 3
    assert (len(obecne) == len(DENY_MAIN_I_TAGI)) if WARIANT_DEV else (not obecne)


def test_ask_dokladnie_taki_jak_wymagany(perm):
    assert sorted(perm["ask"]) == sorted(WYMAGANE_ASK)
    assert "Edit(/.git/**)" in perm["ask"] and "Edit(/.git/hooks/**)" not in perm["ask"]


def test_settings_local_to_pusty_obiekt_albo_brak():
    """settings.local.json (ignorowany przez git) nie poszerza uprawnien: pusty obiekt albo brak pliku."""
    if USTAWIENIA_LOKALNE.exists():
        assert json.loads(USTAWIENIA_LOKALNE.read_text(encoding="utf-8")) == {}


def test_blokada_zdalnych_serwerow_mcp(cala, perm):
    assert cala.get("deniedMcpServers") == [{"serverUrl": "*://*/*"}]
    assert "deniedMcpServers" not in perm            # klucz najwyzszego poziomu
    for klucz in ("allowedMcpServers", "managedMcpServers", "enabledMcpjsonServers", "enableAllProjectMcpServers"):
        assert klucz not in cala
    assert not [r for r in perm["allow"] if r.startswith("mcp__")]


def test_plugin_kuznia_z_publicznego_github(cala):
    assert cala["extraKnownMarketplaces"] == {
        "kuznia-kodu": {"source": {"source": "github", "repo": "belkot78/kuznia-kodu"}}}
    assert cala["enabledPlugins"] == {"kuznia@kuznia-kodu": True}


def test_hooki_pochodza_z_pluginu_a_nie_z_ustawien_projektu(cala):
    assert "hooks" not in cala
