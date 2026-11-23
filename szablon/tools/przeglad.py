"""Przeglad repozytorium: PASS/FAIL dla czterech kontroli (silnik z pluginu kuznia).

Uruchomienie (z korzenia repo):
  python tools/przeglad.py [--root <katalog>] [--kontrole a,b,c,d] [--od <ref git>] [--indeks]

Kontrole:
  (a) testy              - pytest na plikach test_*.py z BIALEJ LISTY (TESTY_DOZWOLONE), kod 0 = zielone
  (b) sekrety            - skan tresci i nazw plikow w repo (bez plikow z .gitignore)
  (c) importy i adresy   - w NOWYCH/ZMIENIONYCH plikach: importy spoza stdlib, repo i listy pakietow
                           z pyproject.toml (albo requirements*.txt) oraz adresy http(s) spoza dozwolonych hostow
  (d) niebezpieczne      - wywolania subprocess, eval, exec, os.system/os.popen w KATALOGI_D
                           poza lista wyjatkow (WYJATKI_D)

Konfiguracja projektu (biala lista testow, wyjatki, hosty, pakiety, dodatkowe wzorce sekretow) jest w
tools/przeglad_konfig.py. Ten plik to silnik wspolny dla projektow: nie dopisuj do niego nazw projektu.

"Nowe" pliki (c): zmienione wzgledem --od (domyslnie upstream; gdy brak: HEAD) oraz nieśledzone.
Poza repozytorium git (np. atrapa w katalogu tymczasowym) wszystkie pliki sa nowe.

Nigdy nie czyta plikow z .gitignore (lista plikow pochodzi z `git ls-files`; poza git pomijamy dane, .git,
.venv). Komunikaty nie zawieraja wartosci znalezionych sekretow.
Kod wyjscia: 0 = PASS, 1 = FAIL. Tylko biblioteka standardowa (Python >= 3.11).
"""
from __future__ import annotations

import argparse
import ast
import os
import re
import subprocess
import sys
from pathlib import Path

KORZEN = Path(__file__).resolve().parents[1]

LIMIT_TESTU_S = 300
LIMIT_GIT_S = 30
MAX_ROZMIAR_B = 1_048_576
MAX_SZCZEGOLOW = 25
MAX_LINII_TESTOW = 15

sys.path.insert(0, str(Path(__file__).resolve().parent))
from przeglad_konfig import (HOSTY_DOZWOLONE, KATALOGI_D, MAPA_PACZEK, PACZKI_DOMYSLNE, PACZKI_PRZECHODNIE,  # noqa: E402
                             TESTY_DOZWOLONE, WYJATKI_D, WYJATKI_SEKRETY, WZORCE_SEKRETOW_DODATKOWE,
                             ZAKAZANE_FOLDERY_DODATKOWE, ZAKAZANE_NAZWY_DODATKOWE)

# (b)
# .env i warianty (poza .env.example, ktory jest sledzony), bazy SQLite (takze -wal/-shm), klucze, zipy.
# Nazwy specyficzne dla projektu: ZAKAZANE_NAZWY_DODATKOWE w przeglad_konfig.py.
ZAKAZANE_NAZWY = re.compile(
    r"(^|/)(\.env(\.(?!example$)[^/]*)?|[^/]*\.db|[^/]*\.sqlite3?[^/]*|[^/]*\.pem|[^/]*\.key|[^/]*\.zip"
    + "".join("|" + n for n in ZAKAZANE_NAZWY_DODATKOWE) + r")$")
ZAKAZANE_FOLDERY = re.compile(r"(^|/)(dane|\.venv|venv|logi|logs" + "".join("|" + f for f in ZAKAZANE_FOLDERY_DODATKOWE) + r")/")
WZORCE_SEKRETOW = (
    ("klucz prywatny", re.compile(r"BEGIN (RSA |EC |OPENSSH )?PRIVATE KEY")),
    ("klucz API Anthropic", re.compile(r"\bsk-ant-[A-Za-z0-9_\-]{20,}")),
    ("klucz API OpenAI", re.compile(r"\bsk-(?:proj-)?[A-Za-z0-9_\-]{32,}")),
    ("klucz API Google", re.compile(r"\bAIza[0-9A-Za-z_\-]{35}\b")),
    ("token GitHub", re.compile(r"\bgh[pousr]_[A-Za-z0-9]{36,}\b")),
    *WZORCE_SEKRETOW_DODATKOWE,   # wzorce specyficzne dla projektu: przeglad_konfig.py
    # Przypisanie sekretu: nazwa z client_secret/api_key/secret/token/password/haslo i LITERAL tekstowy
    # (w cudzyslowie) o dlugosci >= 16 znakow z cyfra i litera. Nazwy zmiennych, wywolania funkcji
    # (przypisanie wyniku wywolania) i krotkie lub slowne wartosci nie daja alarmu.
    ("przypisanie sekretu", re.compile(
        r"""(?i)[\w.\-]*(?:client_secret|api[_\-]?key|secret|token|password|haslo)[\w.\-]*["']?\s*[:=]\s*"""
        r"""["']([A-Za-z0-9_\-./+=]{16,})["']""")),
)
ZNACZNIKI_ATRAPY = ("synt", "przyklad", "example", "placeholder", "xxxx", "<", "...")
# Regula 2: nazwa zmiennej lub klucza z password|passwd|secret|api_key|
# client_secret|token (takze jako czesc nazwy) z przypisanym LITERALEM w cudzyslowie o dlugosci >= 8
# znakow, bez wymogu cyfry i litery. Nazwa bez literalu (wartosc z wywolania, zmiennej, os.environ
# lub konfiguracji) nie daje alarmu.
# Grupy: 1 = nazwa, 2 = cudzyslow, 3 = wartosc (bez wlasnego cudzyslowu).
RE_LITERAL_SEKRETU = re.compile(
    r"""(?i)([\w.\-]*(?:password|passwd|secret|api[_\-]?key|client_secret|token|haslo|hasło)[\w.\-]*)["']?"""
    r"""(?:\s*:\s*[\w.\[\]]+)?\s*[:=]\s*[rbfu]{0,2}(["'])((?:(?!\2).){8,})\2""")
PLACEHOLDERY_PUSTE = {"zmien_mnie", "zmien-mnie", "changeme", "change_me"}
# Regula 3 (wartosc BEZ cudzyslowu, np. `haslo: abc123def456` w yaml, `export TOKEN=...` w sh, `set API_KEY=...`
# w .bat, `- token: ...` na liscie, tez w .md): nazwa jak w regule 2, po niej `:` lub `=` i wartosc >= 12 znakow
# do konca linii (opcjonalny komentarz). BEZ wymogu cyfry (stary hook pre-commit tez jej nie wymagal).
# Wartosc z nawiasem, `$`, `%`, `<`, cudzyslowem lub spacja w srodku (wywolanie, odwolanie do zmiennej
# srodowiskowej, placeholder, zdanie) nie pasuje do klasy znakow, wiec nie daje alarmu. Placeholdery
# odsiewa _placeholder. Dziala na plikach tekstowych OPROCZ .py i .pyi: w Pythonie
# wartosc bez cudzyslowu to wyrazenie (atrybut, nazwa, adnotacja typu), a literaly pokrywa regula 2.
# Zostaje dla yaml/env/ini/toml/bat/sh/md/ps1 i plikow bez rozszerzenia.
ROZSZERZENIA_BEZ_REGULY_3 = {".py", ".pyi"}
RE_BEZ_CUDZYSLOWU = re.compile(
    r"""(?i)(?:^|[\s\-"',{(;])(?:export\s+|set\s+)?[\w.\-]*"""
    r"""(?:password|passwd|secret|api[_\-]?key|client_secret|token|haslo|hasło)[\w.\-]*\s*[:=]\s*"""
    r"""([A-Za-z0-9_\-./+=!@^&*~]{12,})\s*(?:#.*)?$""")
ROZSZERZENIA_BINARNE = {".png", ".jpg", ".jpeg", ".gif", ".ico", ".pdf", ".xlsx", ".pyc", ".woff", ".woff2",
                        ".ttf", ".gz", ".tgz", ".7z"}

# (c)
# skladane, zeby ten plik nie wygladal jak nasluch na wszystkich interfejsach
HOSTY_TYLKO_W_TESTACH = ("0.0.0." + "0",)
RE_ADRES = re.compile(r"https?://([A-Za-z0-9][A-Za-z0-9.\-]*)")
RE_NASLUCH_WSZYSTKIE = re.compile(r"""["']0\.0\.0\.0["']""")
ROZSZERZENIA_ADRESOW = {".py", ".ps1", ".bat"}


# ------------------------------------------------------------------ pliki

def _git(root: Path, *argumenty: str):
    try:
        # UTF-8 jawnie: nazwy plikow z polskimi znakami (git zapisuje je w UTF-8), a Windows ma domyslnie cp1252
        w = subprocess.run(["git", "-C", str(root), *argumenty], capture_output=True, text=True,
                           encoding="utf-8", errors="replace", timeout=LIMIT_GIT_S, check=False)
    except (OSError, subprocess.SubprocessError):
        return None
    return w.stdout if w.returncode == 0 else None


class BladGit(Exception):
    """Polecenie git, od ktorego zalezy wynik kontroli, nie powiodlo sie: wynik ma byc FAIL, nie PASS."""


def _jest_repo(root: Path) -> bool:
    return _git(root, "rev-parse", "--is-inside-work-tree") is not None


def lista_plikow(root: Path) -> list[str]:
    """Pliki repo (sciezki wzgledne z /): sledzone i nieśledzone bez ignorowanych. Poza git: spacer.
    W repozytorium git blad `git ls-files` to BladGit (FAIL), bez cichego przejscia na spacer po dysku
    (spacer nie respektuje .gitignore)."""
    if _jest_repo(root):
        wyjscie = _git(root, "ls-files", "-z", "-co", "--exclude-standard")   # -z: bez cytowania polskich znakow
        if wyjscie is None:
            raise BladGit("git ls-files nie powiodlo sie: nie mozna ustalic listy plikow repo")
        return sorted({l for l in wyjscie.split("\0") if l and (root / l).is_file()})
    wynik = []
    for p in root.rglob("*"):
        if not p.is_file():
            continue
        rel = p.relative_to(root).as_posix()
        if re.search(r"(^|/)(\.git|\.venv|venv|dane|__pycache__)/", rel):
            continue
        wynik.append(rel)
    return sorted(wynik)


def nowe_pliki(root: Path, pliki: list[str], od: str | None) -> list[str]:
    """Zmienione wzgledem `od` (domyslnie upstream albo HEAD) i nieśledzone. Poza git: wszystkie."""
    if not _jest_repo(root):
        return list(pliki)
    ref = od
    if ref is None:
        if _git(root, "rev-parse", "--verify", "-q", "HEAD") is None:
            return list(pliki)   # repo bez commitow: wszystkie pliki sa nowe
        ref = "HEAD"
        up = _git(root, "rev-parse", "--abbrev-ref", "--symbolic-full-name", "@{upstream}")
        if up and up.strip():
            ref = up.strip()
    zmienione = _git(root, "diff", "-z", "--name-only", "--diff-filter=ACMRT", ref)
    nieslad = _git(root, "ls-files", "-z", "-o", "--exclude-standard")
    if zmienione is None or nieslad is None:
        raise BladGit(f"git diff/ls-files nie powiodlo sie (ref {ref}): nie mozna ustalic nowych plikow")
    wszystkie = set(zmienione.split("\0")) | set(nieslad.split("\0"))
    return sorted(p for p in pliki if p in wszystkie)


def _czytaj_tekst(sciezka: Path) -> str | None:
    """Tresc pliku tekstowego albo None (zbyt duzy, binarny, nieczytelny)."""
    if sciezka.suffix.lower() in ROZSZERZENIA_BINARNE:
        return None
    try:
        if sciezka.stat().st_size > MAX_ROZMIAR_B:
            return None
        surowe = sciezka.read_bytes()
    except OSError:
        return None
    if b"\0" in surowe[:8192]:
        return None
    return surowe.decode("utf-8", errors="replace")


def pliki_z_indeksu(root: Path) -> list[str]:
    """Pliki dodane do indeksu (git add): ACMRT (dodane, skopiowane, zmienione, przemianowane, zmiana typu).

    R i T muszą być na liście: plik przemianowany z dopisanym sekretem inaczej omijałby pre-commit."""
    w = _git(root, "diff", "--cached", "-z", "--name-only", "--diff-filter=ACMRT")
    if w is None:
        raise BladGit("git diff --cached nie powiodlo sie: nie mozna ustalic plikow w indeksie")
    return sorted(l for l in w.split("\0") if l)


def _czytaj_z_indeksu(root: Path):
    def czytaj(p: str) -> str | None:
        if Path(p).suffix.lower() in ROZSZERZENIA_BINARNE:
            return None
        try:
            w = subprocess.run(["git", "-C", str(root), "show", f":{p}"], capture_output=True,
                               timeout=LIMIT_GIT_S, check=False)
        except (OSError, subprocess.SubprocessError):
            return None
        if w.returncode != 0 or len(w.stdout) > MAX_ROZMIAR_B or b"\0" in w.stdout[:8192]:
            return None
        return w.stdout.decode("utf-8", errors="replace")
    return czytaj


# ------------------------------------------------------------------ (a) testy

def kontrola_testow(root: Path, pliki: list[str]):
    testy = [p for p in pliki if re.search(r"(^|/)test_[^/]*\.py$", p) and p.startswith(TESTY_DOZWOLONE)]
    if not testy:
        return False, ["brak plikow test_*.py"]
    polecenie = [sys.executable, "-m", "pytest", "-q", "-p", "no:cacheprovider", "--import-mode=importlib", *testy]
    try:
        # PYTHONUTF8: testy drukuja polskie znaki, a przy przekierowaniu Windows uzywa cp1252
        w = subprocess.run(polecenie, cwd=str(root), capture_output=True, text=True, encoding="utf-8",
                           errors="replace", timeout=LIMIT_TESTU_S, check=False,
                           env={**os.environ, "PYTHONUTF8": "1", "PYTHONDONTWRITEBYTECODE": "1"})
    except subprocess.TimeoutExpired:
        return False, [f"pytest przekroczyl limit {LIMIT_TESTU_S} s"]
    except OSError as e:
        return False, [f"nie mozna uruchomic pytest ({type(e).__name__})"]
    linie = [l.rstrip() for l in (w.stdout + "\n" + w.stderr).splitlines() if l.strip()]
    if w.returncode != 0:
        return False, [f"pytest: kod wyjscia {w.returncode}"] + linie[-MAX_LINII_TESTOW:]
    ogon = linie[-1] if linie else ""
    return True, [f"{len(testy)} plikow testowych, wszystkie zielone" + (f" ({ogon})" if ogon else "")]


# ------------------------------------------------------------------ (b) sekrety

def _wartosc_sekretna(wartosc: str) -> bool:
    w = wartosc.lower()
    if any(z in w for z in ZNACZNIKI_ATRAPY):
        return False
    if len(set(wartosc)) <= 3:
        return False
    return any(c.isdigit() for c in wartosc) and any(c.isalpha() for c in wartosc)


def _placeholder(wartosc: str) -> bool:
    """Oczywisty placeholder: pusty, zmien_mnie, same x/gwiazdki, <...>, wielokropek, znacznik atrapy."""
    w = wartosc.strip().lower()
    if not w or w in PLACEHOLDERY_PUSTE or re.fullmatch(r"[x*#_\-]+", w):
        return True
    if (w.startswith("<") and w.endswith(">")) or "..." in w:
        return True
    return any(z in w for z in ("synt", "przyklad", "example", "placeholder", "zmien_mnie", "zmien-mnie",
                                "zmien-na", "zmien_na"))


def kontrola_sekretow(root: Path, pliki: list[str], czytaj=None):
    """czytaj(sciezka_wzgledna) -> tresc albo None; domyslnie plik z dysku (tryb indeksu: git show :plik)."""
    problemy = []
    for p in pliki:
        if ZAKAZANE_NAZWY.search(p) or ZAKAZANE_FOLDERY.search(p):
            problemy.append(f"{p}: zakazany plik lub folder w repo")
            continue
        tresc = czytaj(p) if czytaj else _czytaj_tekst(root / p)
        if tresc is None:
            continue
        regula3 = Path(p).suffix.lower() not in ROZSZERZENIA_BEZ_REGULY_3
        for nr, linia in enumerate(tresc.splitlines(), 1):
            for nazwa, wzorzec in WZORCE_SEKRETOW:
                m = wzorzec.search(linia)
                if not m:
                    continue
                if nazwa == "przypisanie sekretu" and not _wartosc_sekretna(m.group(1)):
                    continue
                problemy.append(f"{p}:{nr}: podejrzana tresc ({nazwa}); wartosc nie jest wypisywana")
                break
            else:
                m = RE_LITERAL_SEKRETU.search(linia)
                if m and not _placeholder(m.group(3)) and \
                        (m.group(1), m.group(3)) not in WYJATKI_SEKRETY.get(p, set()):
                    problemy.append(f"{p}:{nr}: podejrzana tresc (literal przypisany do nazwy sekretu); "
                                    f"wartosc nie jest wypisywana")
                elif regula3:
                    m = RE_BEZ_CUDZYSLOWU.search(linia)
                    if m and not _placeholder(m.group(1)):
                        problemy.append(f"{p}:{nr}: podejrzana tresc (wartosc sekretu bez cudzyslowu); "
                                        f"wartosc nie jest wypisywana")
    return not problemy, problemy or [f"przeskanowano {len(pliki)} plikow"]


# ------------------------------------------------------------------ (c) importy i adresy

def _wpisy_zaleznosci(root: Path):
    """Linie zaleznosci z pyproject.toml (dependencies i optional-dependencies) albo z requirements*.txt.
    None, gdy nie ma zadnego z tych plikow lub pyproject.toml jest uszkodzony."""
    import tomllib
    tresc = _czytaj_tekst(root / "pyproject.toml")
    if tresc is not None:
        try:
            projekt = tomllib.loads(tresc).get("project", {})
        except tomllib.TOMLDecodeError:
            return None
        wpisy = list(projekt.get("dependencies", []))
        for lista in projekt.get("optional-dependencies", {}).values():
            wpisy.extend(lista)
        return wpisy
    wpisy, znaleziono = [], False
    for plik in sorted(root.glob("requirements*.txt")) + sorted((root / "tools").glob("requirements*.txt")):
        tekst = _czytaj_tekst(plik)
        if tekst is None:
            continue
        znaleziono = True
        wpisy.extend(l for l in tekst.splitlines() if l.strip() and not l.lstrip().startswith("#"))
    return wpisy if znaleziono else None


def _paczki_z_zaleznosci(root: Path) -> set[str]:
    """Nazwy importow z zaleznosci projektu (+ przechodnie z konfiguracji); bez plikow: lista domyslna."""
    wpisy = _wpisy_zaleznosci(root)
    if wpisy is None:
        return set(PACZKI_DOMYSLNE) | PACZKI_PRZECHODNIE
    paczki = set(PACZKI_PRZECHODNIE)
    for wpis in wpisy:
        m = re.match(r"\s*([A-Za-z0-9_.\-]+)", wpis)
        if m:
            paczki.add(MAPA_PACZEK.get(m.group(1).lower(), m.group(1).replace("-", "_")))
    return paczki


def _moduly_repo(pliki: list[str]) -> set[str]:
    nazwy = set()
    for p in pliki:
        if p.endswith(".py"):
            czesci = p[:-3].split("/")
            nazwy.update(czesci)
    return nazwy


def kontrola_importow_i_adresow(root: Path, pliki: list[str], nowe: list[str]):
    dozwolone = set(sys.stdlib_module_names) | _moduly_repo(pliki) | _paczki_z_zaleznosci(root)
    problemy = []
    for p in nowe:
        rozszerzenie = Path(p).suffix.lower()
        tresc = _czytaj_tekst(root / p)
        if tresc is None:
            continue
        jest_test = Path(p).name.startswith("test_")
        if rozszerzenie == ".py":
            try:
                drzewo = ast.parse(tresc)
            except SyntaxError:
                problemy.append(f"{p}: blad skladni, nie mozna sprawdzic importow")
                drzewo = None
            if drzewo is not None:
                for n in ast.walk(drzewo):
                    if isinstance(n, ast.Import):
                        moduly = [a.name for a in n.names]
                    elif isinstance(n, ast.ImportFrom) and n.level == 0 and n.module:
                        moduly = [n.module]
                    else:
                        continue
                    for m in moduly:
                        if m.split(".")[0] not in dozwolone:
                            problemy.append(f"{p}:{n.lineno}: import spoza stdlib, repo i zaleznosci projektu: {m.split('.')[0]}")
            if not jest_test and RE_NASLUCH_WSZYSTKIE.search(tresc):
                problemy.append(f"{p}: nasluch na 0.0.0.0 (dozwolone tylko 127.0.0.1)")
        if rozszerzenie in ROZSZERZENIA_ADRESOW:
            for nr, linia in enumerate(tresc.splitlines(), 1):
                for host in RE_ADRES.findall(linia):
                    h = host.lower().rstrip(".")
                    ok = any(h == d or h.endswith("." + d) for d in HOSTY_DOZWOLONE) or \
                        (jest_test and h in HOSTY_TYLKO_W_TESTACH)
                    if not ok:
                        problemy.append(f"{p}:{nr}: adres spoza listy dozwolonych hostow: {h}")
    return not problemy, problemy or [f"sprawdzono {len(nowe)} nowych/zmienionych plikow"]


# ------------------------------------------------------------------ (d) niebezpieczne wywolania

def _nazwa_kropkowana(wezel) -> str | None:
    czesci = []
    while isinstance(wezel, ast.Attribute):
        czesci.append(wezel.attr)
        wezel = wezel.value
    if isinstance(wezel, ast.Name):
        czesci.append(wezel.id)
        return ".".join(reversed(czesci))
    return None


def niebezpieczne_wywolania(tresc: str) -> list[tuple[int, str]]:
    """[(linia, nazwa)]: eval, exec, os.system, os.popen, os.exec*, os.spawn*, subprocess.*."""
    drzewo = ast.parse(tresc)
    aliasy = {}
    for n in ast.walk(drzewo):
        if isinstance(n, ast.Import):
            for a in n.names:
                if a.name in ("os", "subprocess"):
                    aliasy[a.asname or a.name] = a.name
        elif isinstance(n, ast.ImportFrom) and n.module in ("os", "subprocess") and n.level == 0:
            for a in n.names:
                aliasy[a.asname or a.name] = f"{n.module}.{a.name}"
    wynik = []
    for n in ast.walk(drzewo):
        if not isinstance(n, ast.Call):
            continue
        if isinstance(n.func, ast.Name):
            nazwa = aliasy.get(n.func.id, n.func.id)
        else:
            k = _nazwa_kropkowana(n.func)
            if k is None:
                continue
            glowa, _, reszta = k.partition(".")
            nazwa = f"{aliasy.get(glowa, glowa)}.{reszta}" if glowa in aliasy else k
        if nazwa in ("eval", "exec", "os.system", "os.popen") or nazwa.startswith(("os.exec", "os.spawn")) \
                or nazwa.startswith("subprocess."):
            wynik.append((n.lineno, nazwa))
    return wynik


def kontrola_niebezpiecznych(root: Path, pliki: list[str]):
    problemy, liczba = [], 0
    for p in pliki:
        if not p.endswith(".py") or not p.startswith(KATALOGI_D):
            continue
        tresc = _czytaj_tekst(root / p)
        if tresc is None:
            continue
        liczba += 1
        try:
            trafienia = niebezpieczne_wywolania(tresc)
        except SyntaxError:
            problemy.append(f"{p}: blad skladni, nie mozna sprawdzic wywolan")
            continue
        for linia, nazwa in trafienia:
            if nazwa not in WYJATKI_D.get(p, set()):
                problemy.append(f"{p}:{linia}: niebezpieczne wywolanie {nazwa} poza lista wyjatkow")
    return not problemy, problemy or [f"sprawdzono {liczba} plikow .py w {', '.join(KATALOGI_D)}"]


# ------------------------------------------------------------------ calosc

KONTROLE = {
    "a": "testy",
    "b": "skan sekretow",
    "c": "importy i adresy w nowych plikach",
    "d": "niebezpieczne wywolania",
}


def uruchom(root: Path = KORZEN, kontrole: str = "abcd", od: str | None = None, wypis=print,
            indeks: bool = False) -> bool:
    """indeks=True: tylko kontrola (b) na zawartosci indeksu git (uzywane przez hook pre-commit)."""
    root = Path(root).resolve()
    if indeks:
        if kontrole != "b":
            raise ValueError("tryb --indeks obsluguje tylko kontrole b")
        try:
            pliki = pliki_z_indeksu(root)
            ok, szczegoly = kontrola_sekretow(root, pliki, _czytaj_z_indeksu(root))
        except BladGit as e:
            ok, szczegoly = False, [str(e)]
        wypis(f"[{'PASS' if ok else 'FAIL'}] (b) {KONTROLE['b']} (indeks)")
        for s_ in szczegoly[:MAX_SZCZEGOLOW]:
            wypis(f"    {s_}")
        wypis(f"WYNIK: {'PASS' if ok else 'FAIL'}")
        return ok
    try:
        pliki = lista_plikow(root)
    except BladGit as e:
        wypis(f"[FAIL] (git) lista plikow repo{chr(10)}    {e}")
        wypis("WYNIK: FAIL")
        return False
    wyniki = []
    for k in kontrole:
        if k == "a":
            wyniki.append((k, *kontrola_testow(root, pliki)))
        elif k == "b":
            wyniki.append((k, *kontrola_sekretow(root, pliki)))
        elif k == "c":
            try:
                wyniki.append((k, *kontrola_importow_i_adresow(root, pliki, nowe_pliki(root, pliki, od))))
            except BladGit as e:
                wyniki.append((k, False, [str(e)]))
        elif k == "d":
            wyniki.append((k, *kontrola_niebezpiecznych(root, pliki)))
        else:
            raise ValueError(f"nieznana kontrola: {k!r} (dozwolone: a, b, c, d)")
    wszystko_ok = True
    for k, ok, szczegoly in wyniki:
        wszystko_ok &= ok
        wypis(f"[{'PASS' if ok else 'FAIL'}] ({k}) {KONTROLE[k]}")
        for s in szczegoly[:MAX_SZCZEGOLOW]:
            wypis(f"    {s}")
        if len(szczegoly) > MAX_SZCZEGOLOW:
            wypis(f"    ... i {len(szczegoly) - MAX_SZCZEGOLOW} wiecej")
    wypis(f"WYNIK: {'PASS' if wszystko_ok else 'FAIL'}")
    return wszystko_ok


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="Przeglad repozytorium: PASS/FAIL (testy, sekrety, importy, wywolania).")
    parser.add_argument("--root", default=str(KORZEN), help="katalog repo (domyslnie korzen tego repo)")
    parser.add_argument("--kontrole", default="abcd", help="litery kontroli do uruchomienia, np. bcd")
    parser.add_argument("--od", default=None, help="ref git dla 'nowych plikow' (domyslnie upstream albo HEAD)")
    parser.add_argument("--indeks", action="store_true",
                        help="tylko kontrola b na zawartosci indeksu git (dla hooka pre-commit)")
    args = parser.parse_args(argv)
    try:
        ok = uruchom(Path(args.root), "b" if args.indeks else args.kontrole, args.od, indeks=args.indeks)
    except ValueError as e:
        print(f"BLAD: {e}", file=sys.stderr)
        return 2
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
