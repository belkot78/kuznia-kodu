"""Kontrola repo publicznego (offline): brak adresow, hostow, kont, sciezek produkcyjnych i nazw zakazanych.

Zasady (decyzja Pawla z 23.11.2026):
- Nazwy projektow (przyklady w metodzie) sa dozwolone w calym repo.
- Etykiety kontraktow K1-K9 i Z1-Z9 sa dozwolone tylko w METODA.md i docs/pakiety/.
- Zakazane wszedzie: nazwy brokerow, pliki z tokenami, nazwy folderow produkcyjnych, numery kont, adresy i hosty.
- Konta dozwolone w repo: claude-agent, Belkot, belko.

Wzorce ogolne sa tutaj. Lista nazw zakazanych (sama jest wrazliwa) jest LOKALNA i poza gitem:
docs/prywatne/zakazane_nazwy.txt (format: jedna pozycja w linii, "re:" = wyrazenie regularne, # = komentarz).
Gdy pliku brak (np. swiezy klon), test pomija sprawdzenie nazw i to zglasza.
"""
import re
import subprocess
from pathlib import Path

import pytest

KORZEN = Path(__file__).resolve().parents[1]
LISTA_PRYWATNA = KORZEN / "docs" / "prywatne" / "zakazane_nazwy.txt"
KONTA_DOZWOLONE = {"claude-agent", "belkot", "belko"}
ROZSZERZENIA_TEKSTOWE_POMIJANE = {".png", ".jpg", ".jpeg", ".gif", ".ico", ".pdf", ".xlsx", ".pyc", ".zip"}

# wzorce ogolne (zawsze sprawdzane)
# adresy petli zwrotnej (127.0.0.1) i "wszystkie interfejsy" (0.0.0.0 w komunikacie o zakazie) sa dozwolone
RE_IP = re.compile(r"(?<![\d.])(?!(?:127\.0\.0\.1|0\.0\.0\.0)(?![\d.]))(?:\d{1,3}\.){3}\d{1,3}(?![\d.])")
RE_HOST_TS = re.compile(r"\b[\w-]+\.ts\.net\b", re.I)
RE_HOST_WIN = re.compile(r"\bWIN-[A-Z0-9]{8,}\b")
RE_SCIEZKA_PROJEKTOW = re.compile(r"[Cc]:[\\/]Projects[\\/](?!_repo\b)")
RE_SCIEZKA_UZYTKOWNIKA = re.compile(r"(?:[Cc]:)?[\\/]Users[\\/]([\w.-]+)|/home/([\w.-]+)")
RE_ETYKIETA_KONTRAKTU = re.compile(r"\b[KZ][1-9]\b")
RE_PLIK_TOKENA = re.compile(r"\b[\w.-]*token[\w.-]*\.(?:json|ya?ml|txt|env)\b", re.I)
DOZWOLONE_ETYKIETY = ("METODA.md", "docs/pakiety/")
# ten plik zawiera wzorce i opis zasad, wiec sam siebie nie skanuje (jego testy wzorcow sprawdzaja atrapy skladane z fragmentow)
SAMOREFERENCJA = {"testy/test_publiczne.py"}


def pliki_repo():
    # -z: bez tego git cytuje sciezki z polskimi znakami ("za\305\274\303\263\305\202\304\207.py"), a plik
    # wypadalby po cichu z kontroli repo publicznego (ten sam blad poprawiono w tools/przeglad.py)
    w = subprocess.run(["git", "-c", f"safe.directory={KORZEN.as_posix()}", "-C", str(KORZEN), "ls-files", "-z",
                        "-co", "--exclude-standard"], capture_output=True)
    assert w.returncode == 0, w.stderr.decode("utf-8", errors="replace")
    sciezki = w.stdout.decode("utf-8").split("\0")
    return sorted(p for p in sciezki if p and (KORZEN / p).is_file())


def test_pliki_repo_zwraca_pliki_z_polskimi_znakami_w_nazwie():
    """Regresja: lista plikow musi zawierac (nieslledzony) plik z polska nazwa; git bez -z cytuje takie sciezki."""
    rel = "testy/_tmp_zażółć.txt"
    plik = KORZEN / rel
    plik.write_text("x\n", encoding="utf-8")
    try:
        assert rel in pliki_repo()
    finally:
        plik.unlink()


def tresc(rel):
    if Path(rel).suffix.lower() in ROZSZERZENIA_TEKSTOWE_POMIJANE:
        return ""
    return (KORZEN / rel).read_text(encoding="utf-8", errors="replace")


def linie(rel):
    return list(enumerate(tresc(rel).splitlines(), 1))


def nazwy_zakazane():
    wzorce = []
    for l in LISTA_PRYWATNA.read_text(encoding="utf-8").splitlines():
        l = l.strip()
        if not l or l.startswith("#"):
            continue
        wzorce.append(re.compile(l[3:]) if l.startswith("re:") else re.compile(re.escape(l), re.I))
    return wzorce


@pytest.fixture(scope="module")
def pliki():
    p = pliki_repo()
    assert "METODA.md" in p and "README.md" in p            # sanity: lista plikow nie jest pusta
    return [x for x in p if x not in SAMOREFERENCJA]


def znajdz(pliki, regula):
    trafienia = []
    for rel in pliki:
        for nr, l in linie(rel):
            if regula(rel, l):
                trafienia.append(f"{rel}:{nr}")
    return trafienia


def test_brak_adresow_ip(pliki):
    # wersje typu 0.3.0 maja 3 grupy, wiec nie pasuja; IP ma 4
    assert not znajdz(pliki, lambda rel, l: RE_IP.search(l))


def test_brak_nazw_hostow(pliki):
    assert not znajdz(pliki, lambda rel, l: RE_HOST_TS.search(l) or RE_HOST_WIN.search(l))


def test_brak_sciezek_poza_katalogiem_repo(pliki):
    """Folder w C:\\Projects inny niz _repo to nazwa folderu produkcyjnego."""
    assert not znajdz(pliki, lambda rel, l: RE_SCIEZKA_PROJEKTOW.search(l))


def test_tylko_dozwolone_konta_w_sciezkach_uzytkownikow(pliki):
    def zle(rel, l):
        for m in RE_SCIEZKA_UZYTKOWNIKA.finditer(l):
            konto = (m.group(1) or m.group(2)).lower()
            if konto not in KONTA_DOZWOLONE and konto not in {"<nazwa>", "<agent>"}:
                return True
        return False
    assert not znajdz(pliki, zle)


def test_etykiety_kontraktow_tylko_w_metodzie_i_pakietach(pliki):
    poza = [p for p in pliki if not p.startswith(DOZWOLONE_ETYKIETY)]
    assert not znajdz(poza, lambda rel, l: RE_ETYKIETA_KONTRAKTU.search(l))


def test_brak_plikow_z_tokenami_i_zakazanych_nazw_plikow(pliki):
    assert not [p for p in pliki if RE_PLIK_TOKENA.search(Path(p).name)]
    zakazane = re.compile(r"(^|/)(\.env(\.(?!example$)[^/]*)?|[^/]*\.(db|sqlite3?|pem|key|zip))$")
    assert not [p for p in pliki if zakazane.search(p)]
    assert not [p for p in pliki if p.startswith(("dane/", "docs/prywatne/")) or "/dane/" in p]


def test_prywatne_nie_sa_sledzone_przez_git():
    w = subprocess.run(["git", "-c", f"safe.directory={KORZEN.as_posix()}", "-C", str(KORZEN), "ls-files",
                        "docs/prywatne"], capture_output=True, text=True)
    assert w.stdout.strip() == ""
    gi = (KORZEN / ".gitignore").read_text(encoding="utf-8")
    assert "docs/prywatne/" in gi


def test_lista_nazw_zakazanych_nie_wystepuje_w_repo(pliki):
    # lista prywatna obejmuje tez ten plik (nie zawiera zadnych nazw); wylaczenie dotyczy tylko wzorcow ogolnych
    pliki = pliki_repo()
    if not LISTA_PRYWATNA.is_file():
        pytest.skip("brak docs/prywatne/zakazane_nazwy.txt: sprawdzenie nazw zakazanych NIEPELNE (tylko wzorce ogolne)")
    wzorce = nazwy_zakazane()
    assert wzorce, "lista nazw zakazanych jest pusta"
    trafienia = znajdz(pliki, lambda rel, l: any(w.search(l) for w in wzorce))
    assert not trafienia, trafienia[:20]
    nazwy_plikow = [p for p in pliki if any(w.search(p) for w in wzorce)]
    assert not nazwy_plikow, nazwy_plikow


# --- testy samych wzorcow: kontrola nie moze byc martwa
@pytest.mark.parametrize("tekst,regula", [
    ("host " + "10." + "1.2.3" + " port", RE_IP),
    ("moj-" + "laptop" + ".tail1234." + "ts.net", RE_HOST_TS),
    ("WIN-" + "ABCDEF12345", RE_HOST_WIN),
    ("C:" + "\\Projects\\" + "aplikacja\\dane", RE_SCIEZKA_PROJEKTOW),
    ("K" + "3 i Z" + "7", RE_ETYKIETA_KONTRAKTU),
    ("usluga_" + "token_1.json", RE_PLIK_TOKENA),
])
def test_wzorce_ogolne_wykrywaja_atrapy(tekst, regula):
    assert regula.search(tekst)


@pytest.mark.parametrize("tekst,regula", [
    ("wersja 0.3.0 i 1.2.3", RE_IP),
    ("nasluch na 127.0.0.1 i " + "0.0.0." + "0", RE_IP),
    ("C:" + "\\Projects\\_repo\\kuznia-kodu", RE_SCIEZKA_PROJEKTOW),
    ("Kontrola K", RE_ETYKIETA_KONTRAKTU),
])
def test_wzorce_ogolne_nie_zglaszaja_falszywych_alarmow(tekst, regula):
    assert not regula.search(tekst)


def test_konta_dozwolone_w_sciezce_uzytkownika():
    assert {(m.group(1) or m.group(2)).lower() for m in
            RE_SCIEZKA_UZYTKOWNIKA.finditer("C:" + r"\Us" + r"ers\claude-agent\.venvs i /Us" + "ers/Belkot i /home/inny")} == {
        "claude-agent", "belkot", "inny"}
