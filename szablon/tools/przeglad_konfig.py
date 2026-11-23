"""Konfiguracja projektu dla tools/przeglad.py. Plik kontrolny: zmiany nakłada Pawel (agent przygotowuje .patch).

Silnik (przeglad.py) jest wspolny dla projektow. Wszystko, co zalezy od projektu, jest tutaj.
Kazdy wpis w WYJATKI_* musi miec komentarz z uzasadnieniem (dlaczego to falszywy alarm).
"""

# (a) BIALA LISTA: kontrola (a) uruchamia (pytest) tylko testy z tych sciezek (katalog z "/" na koncu albo plik).
# Kazdy nowy test_*.py w nowym miejscu jest pomijany, dopoki ktos jawnie nie doda go tutaj.
TESTY_DOZWOLONE = (
    "tests/",
    "tools/tests/",
)

# (b) dodatkowe wzorce sekretow: krotki (opis, skompilowane wyrazenie), np. ("token uslugi X", re.compile(r"...")).
WZORCE_SEKRETOW_DODATKOWE: tuple = ()
# dodatkowe zakazane nazwy plikow (fragmenty wyrazenia regularnego, np. r"blocklist\.txt") i foldery (np. r"_to_delete")
ZAKAZANE_NAZWY_DODATKOWE: tuple = ()
ZAKAZANE_FOLDERY_DODATKOWE: tuple = ()
# Znane falszywe alarmy: sciezka wzgledna (z /) -> {(nazwa, dokladny literal)}. Wyjatek dotyczy pliku, nazwy
# I dokladnego literalu, wiec inny literal przypisany do tej samej nazwy w tym samym pliku nadal daje alarm.
WYJATKI_SEKRETY: dict = {
    # "src/pakiet/plik.html": {("nazwa", "literal")},   # FALSZYWY ALARM: <uzasadnienie>
}

# (c) hosty, do ktorych kod moze sie odwolywac (adresy http(s) w nowych plikach .py/.ps1/.bat)
HOSTY_DOZWOLONE = ("localhost", "127.0.0.1", "example.com", "example.org")
# Gdy brak pyproject.toml i requirements*.txt (atrapa) oraz zaleznosci przechodnie, ktorych nie ma w plikach.
PACZKI_DOMYSLNE = {"pytest"}
PACZKI_PRZECHODNIE: set = set()
# nazwa pakietu w pip (male litery) -> nazwa importu, gdy sie rozni
MAPA_PACZEK = {"pyyaml": "yaml", "python-multipart": "multipart"}

# (d) niebezpieczne wywolania: katalogi sprawdzane i wyjatki (sciezka -> dozwolone wywolania)
KATALOGI_D = ("src/", "tools/")
WYJATKI_D = {
    "tools/przeglad.py": {"subprocess.run"},                                  # git i uruchamianie pytest
    "tools/tests/test_przeglad.py": {"subprocess.run"},                       # testy silnika na atrapach (git)
}
