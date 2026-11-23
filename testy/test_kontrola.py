"""Testy hooka hooks/kontrola.py na danych syntetycznych (offline; bez prawdziwych testow projektu)."""
import importlib.util
import io
import json
import subprocess
import sys
from pathlib import Path
from types import SimpleNamespace

import pytest

KORZEN = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("kontrola", KORZEN / "hooks" / "kontrola.py")
kontrola = importlib.util.module_from_spec(spec)
spec.loader.exec_module(kontrola)


def zapisz(katalog, rel, tresc=b"x"):
    p = Path(katalog) / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_bytes(tresc if isinstance(tresc, bytes) else tresc.encode())
    return p


# ---- post
def test_post_poprawny_python_i_json(tmp_path):
    assert kontrola.kontrola_pliku(zapisz(tmp_path, "a.py", "x = 1\n")) is None
    assert kontrola.kontrola_pliku(zapisz(tmp_path, "a.json", '{"a": 1}')) is None


def test_post_blad_skladni_python(tmp_path):
    blad = kontrola.kontrola_pliku(zapisz(tmp_path, "zly.py", "def f(:\n"))
    assert blad and "BLAD SKLADNI" in blad and "zly.py" in blad


def test_post_blad_json(tmp_path):
    blad = kontrola.kontrola_pliku(zapisz(tmp_path, "zly.json", "{"))
    assert blad and "BLAD JSON" in blad


def test_post_json_z_bom_jest_poprawny(tmp_path):
    assert kontrola.kontrola_pliku(zapisz(tmp_path, "bom.json", b"\xef\xbb\xbf{}")) is None


def test_post_inne_rozszerzenia_i_brak_pliku_sa_pomijane(tmp_path):
    assert kontrola.kontrola_pliku(zapisz(tmp_path, "a.md", "def f(:")) is None
    assert kontrola.kontrola_pliku(tmp_path / "brak.py") is None


def test_post_kody_wyjscia(tmp_path):
    zly = zapisz(tmp_path, "zly.py", "def f(:\n")
    assert kontrola.kontrola_post({"tool_input": {"file_path": str(zly)}})[0] == 2
    assert kontrola.kontrola_post({"tool_input": {}}) == (0, "")
    assert kontrola.kontrola_post({}) == (0, "")


# ---- interpreter
def test_interpreter_venv_agenta_wedlug_nazwy_repo(tmp_path):
    repo = tmp_path / "repo" / "moj-projekt"
    repo.mkdir(parents=True)
    home = tmp_path / "home"
    agent_py = zapisz(home, ".venvs/moj-projekt/Scripts/python.exe")
    zapisz(repo, ".venv/Scripts/python.exe")
    assert kontrola.wybierz_interpreter(home, repo) == str(agent_py)


def test_interpreter_linux_bin_i_kolejnosc(tmp_path):
    repo = tmp_path / "proj"
    repo.mkdir()
    home = tmp_path / "home"
    assert kontrola.wybierz_interpreter(home, repo) == sys.executable
    repo_py = zapisz(repo, ".venv/bin/python")
    assert kontrola.wybierz_interpreter(home, repo) == str(repo_py)
    agent_py = zapisz(home, ".venvs/proj/bin/python")
    assert kontrola.wybierz_interpreter(home, repo) == str(agent_py)


def test_korzen_z_zmiennej_srodowiskowej(tmp_path):
    assert kontrola.korzen_projektu({"CLAUDE_PROJECT_DIR": str(tmp_path)}) == tmp_path
    assert kontrola.korzen_projektu({}, cwd=tmp_path) == tmp_path


# ---- stop
def git_atrapa(wyjscie, kod=0):
    return lambda *a, **k: SimpleNamespace(returncode=kod, stdout=wyjscie, stderr=b"")


def repo_z_przegladem(tmp_path):
    zapisz(tmp_path, "tools/przeglad.py", "")
    return tmp_path


def test_stop_nie_blokuje_drugi_raz(tmp_path):
    assert kontrola.kontrola_stop({"stop_hook_active": True}, korzen=tmp_path) == (0, "")


def test_stop_bez_przeglad_py_nic_nie_robi(tmp_path):
    assert kontrola.kontrola_stop({}, korzen=tmp_path) == (0, "")


def test_stop_brak_zmienionych_py(tmp_path):
    repo = repo_z_przegladem(tmp_path)
    assert kontrola.kontrola_stop({}, korzen=repo, uruchom_git=git_atrapa(b" M README.md\0")) == (0, "")


def test_stop_awaria_gita_to_kod_nieblokujacy(tmp_path):
    repo = repo_z_przegladem(tmp_path)
    kod, kom = kontrola.kontrola_stop({}, korzen=repo, uruchom_git=git_atrapa(b"", kod=128))
    assert kod == 1 and "git" in kom


def test_stop_uruchamia_tylko_kontrole_a_i_zwraca_fail(tmp_path):
    repo = repo_z_przegladem(tmp_path)
    wywolania = []

    def uruchom(polecenie, **kw):
        wywolania.append(polecenie)
        return SimpleNamespace(returncode=1, stdout=b"[FAIL] (a) testy\n    tests/test_x.py\n", stderr=b"")

    kod, kom = kontrola.kontrola_stop({}, korzen=repo, home=str(tmp_path / "h"), uruchom=uruchom,
                                      uruchom_git=git_atrapa(b" M src/x.py\0?? tests/test_x.py\0"))
    assert kod == 2 and "FAIL" in kom and "src/x.py" in kom
    assert wywolania[0][-2:] == ["--kontrole", "a"]
    assert wywolania[0][1].endswith("przeglad.py")


def test_stop_pass_gdy_testy_zielone(tmp_path):
    repo = repo_z_przegladem(tmp_path)
    uruchom = lambda p, **kw: SimpleNamespace(returncode=0, stdout=b"", stderr=b"")
    assert kontrola.kontrola_stop({}, korzen=repo, uruchom=uruchom,
                                  uruchom_git=git_atrapa(b" M a.py\0")) == (0, "")


def test_stop_limit_czasu_i_brak_interpretera(tmp_path):
    repo = repo_z_przegladem(tmp_path)

    def za_dlugo(p, **kw):
        raise subprocess.TimeoutExpired(p, 1)

    def brak(p, **kw):
        raise FileNotFoundError("x")

    git = git_atrapa(b" M a.py\0")
    assert "przekroczyly" in kontrola.kontrola_stop({}, korzen=repo, uruchom=za_dlugo, uruchom_git=git)[1]
    assert kontrola.kontrola_stop({}, korzen=repo, uruchom=brak, uruchom_git=git)[0] == 2


def test_zmienione_pliki_py_zmiana_nazwy_i_usuniecie():
    wyjscie = b"R  nowy.py\0stary.py\0 D usuniety.py\0A  dodany.py\0 M opis.md\0"
    assert kontrola.zmienione_pliki_py(".", git_atrapa(wyjscie)) == ["nowy.py", "dodany.py"]


# ---- main
def test_main_uzycie_i_post_przez_stdin(tmp_path, capsys):
    assert kontrola.main(["zle"]) == 1
    zly = zapisz(tmp_path, "zly.py", "def f(:\n")
    stdin = io.StringIO(json.dumps({"tool_input": {"file_path": str(zly)}}))
    assert kontrola.main(["post"], stdin=stdin) == 2
    assert kontrola.main(["post"], stdin=io.StringIO("nie json")) == 0


def test_hook_dziala_jako_proces(tmp_path):
    zly = zapisz(tmp_path, "zly.py", "def f(:\n")
    w = subprocess.run([sys.executable, str(KORZEN / "hooks" / "kontrola.py"), "post"],
                       input=json.dumps({"tool_input": {"file_path": str(zly)}}).encode(),
                       capture_output=True, timeout=30)
    assert w.returncode == 2 and b"BLAD SKLADNI" in w.stderr
