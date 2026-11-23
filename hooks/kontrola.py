"""Hooki Claude Code pluginu kuznia: lekka kontrola po edycji i testy na koniec tury.

Uzycie (z hooks/hooks.json; dane hooka przychodza jako JSON na stdin):
  python hooks/kontrola.py post   # PostToolUse: skladnia .py (compile) i poprawnosc .json
  python hooks/kontrola.py stop   # Stop: gdy zmienily sie pliki .py, tools/przeglad.py --kontrole a

Kody wyjscia: 0 = ok, 2 = blad, ktory Claude Code pokazuje modelowi (stderr). Inne = blad nieblokujacy.
Stop nie blokuje drugi raz, gdy stop_hook_active = true (zabezpieczenie przed petla).
Katalog projektu: zmienna CLAUDE_PROJECT_DIR (skrypt lezy w pluginie, nie w repo projektu), a gdy jej brak,
biezacy katalog. Uruchamiane jest wylacznie przeglad.py z kontrola (a), czyli testy z BIALEJ LISTY projektu.
Interpreter testow: venv agenta <home>/.venvs/<nazwa-repo>, potem .venv repo, na koncu interpreter hooka.
Tylko biblioteka standardowa, bez PowerShella. Nie czyta sekretow ani danych, nie wypisuje tresci plikow.
"""
import json
import os
import subprocess
import sys
from pathlib import Path

LIMIT_STOP_S = 240
MAX_LINII_BLEDU = 30


def korzen_projektu(env=None, cwd=None):
    env = os.environ if env is None else env
    return Path(env.get("CLAUDE_PROJECT_DIR") or cwd or os.getcwd())


def _pythony_w_venv(katalog):
    """Mozliwe interpretery w venv: Windows (Scripts) i Linux/macOS (bin)."""
    katalog = Path(katalog)
    return (katalog / "Scripts" / "python.exe", katalog / "bin" / "python")


def wybierz_interpreter(home, korzen):
    """Venv agenta (<home>/.venvs/<nazwa-repo>), potem .venv repo, na koncu interpreter, ktory uruchomil hook."""
    kandydaci = (*_pythony_w_venv(Path(home) / ".venvs" / Path(korzen).name),
                 *_pythony_w_venv(Path(korzen) / ".venv"))
    for kandydat in kandydaci:
        if kandydat.is_file():
            return str(kandydat)
    return sys.executable


def kontrola_pliku(sciezka):
    """Zwraca komunikat bledu albo None. Tylko .py (skladnia) i .json (poprawnosc)."""
    p = Path(sciezka)
    rozszerzenie = p.suffix.lower()
    if rozszerzenie not in (".py", ".json"):
        return None
    if not p.is_file():
        return None
    try:
        surowe = p.read_bytes()
    except OSError as e:
        return f"{p.name}: nie mozna odczytac pliku ({e.__class__.__name__})"
    if rozszerzenie == ".py":
        try:
            compile(surowe, str(p), "exec", dont_inherit=True)
        except SyntaxError as e:
            return f"BLAD SKLADNI {p.name}, linia {e.lineno}: {e.msg}"
        except ValueError as e:   # np. znak NUL w zrodle
            return f"BLAD SKLADNI {p.name}: {e}"
        return None
    try:
        json.loads(surowe.decode("utf-8-sig"))
    except (ValueError, UnicodeDecodeError) as e:
        return f"BLAD JSON {p.name}: {e}"
    return None


def kontrola_post(dane):
    wejscie = dane.get("tool_input") or {}
    sciezka = wejscie.get("file_path") or wejscie.get("path")
    if not sciezka:
        return 0, ""
    blad = kontrola_pliku(sciezka)
    return (2, blad) if blad else (0, "")


def zmienione_pliki_py(korzen, uruchom=subprocess.run):
    """Pliki .py zmienione wzgledem HEAD (zmodyfikowane, dodane, nowe (untracked)). None, gdy git zawiedzie."""
    try:
        w = uruchom(["git", "-C", str(korzen), "status", "--porcelain", "-z", "-uall"],
                    capture_output=True, timeout=30)
    except (OSError, subprocess.TimeoutExpired):
        return None
    if w.returncode != 0:
        return None
    wpisy = w.stdout.decode("utf-8", errors="replace").split("\0")
    pliki, i = [], 0
    while i < len(wpisy):
        wpis = wpisy[i]
        i += 1
        if len(wpis) < 4:
            continue
        kod, sciezka = wpis[:2], wpis[3:]
        if "R" in kod or "C" in kod:
            i += 1    # nastepny wpis to stara nazwa
        if "D" in kod:
            continue
        if sciezka.lower().endswith(".py"):
            pliki.append(sciezka)
    return pliki


def kontrola_stop(dane, korzen=None, home=None, uruchom=subprocess.run, uruchom_git=None):
    if dane.get("stop_hook_active"):
        return 0, ""
    korzen = Path(korzen) if korzen else korzen_projektu()
    przeglad = korzen / "tools" / "przeglad.py"
    if not przeglad.is_file():
        return 0, ""   # projekt bez narzedzi kontrolnych (np. przed /nowy-projekt): nic do uruchomienia
    pliki = zmienione_pliki_py(korzen, uruchom_git or subprocess.run)
    if pliki is None:
        return 1, "hook Stop: nie mozna odczytac stanu gita, testy pominiete"
    if not pliki:
        return 0, ""
    home = home or os.environ.get("USERPROFILE") or os.environ.get("HOME") or str(Path.home())
    python = wybierz_interpreter(home, korzen)
    polecenie = [python, str(przeglad), "--kontrole", "a"]
    try:
        w = uruchom(polecenie, cwd=str(korzen), capture_output=True, timeout=LIMIT_STOP_S)
    except subprocess.TimeoutExpired:
        return 2, f"hook Stop: testy (przeglad.py --kontrole a) przekroczyly {LIMIT_STOP_S} s"
    except OSError as e:
        return 2, f"hook Stop: nie mozna uruchomic interpretera {python} ({e.__class__.__name__})"
    if w.returncode == 0:
        return 0, ""
    tekst = (w.stdout or b"").decode("utf-8", errors="replace") + (w.stderr or b"").decode("utf-8", errors="replace")
    linie = [l.rstrip() for l in tekst.splitlines() if l.strip()]
    return 2, "Testy z bialej listy: FAIL (zmienione .py: %s)\n%s" % (
        ", ".join(pliki[:10]), "\n".join(linie[-MAX_LINII_BLEDU:]))


def main(argv=None, stdin=None):
    argv = sys.argv[1:] if argv is None else argv
    if len(argv) != 1 or argv[0] not in ("post", "stop"):
        print("uzycie: kontrola.py post|stop", file=sys.stderr)
        return 1
    try:
        dane = json.loads((stdin or sys.stdin).read() or "{}")
    except ValueError:
        dane = {}
    kod, komunikat = kontrola_post(dane) if argv[0] == "post" else kontrola_stop(dane)
    if komunikat:
        sys.stderr.buffer.write((komunikat + "\n").encode("utf-8", errors="replace"))
        sys.stderr.flush()
    return kod


if __name__ == "__main__":
    sys.exit(main())
