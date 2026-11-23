# Recenzja: część specyficzna dla projektu {{NAZWA}}

Ten plik czyta agent `recenzent` na starcie każdej recenzji. To jedyne miejsce, w którym dostaje wiedzę o tym projekcie. Wypełnia go planista razem z Pawłem w PK-00 projektu. Część ogólna recenzji jest w agencie (plugin `kuznia`).

## Poziom dostępu

**{{POZIOM}}** (P0: tylko kod i dane syntetyczne; P1: odczyt żywych systemów, wąski token tylko do odczytu; P2: sterowanie żywym systemem, osobne środowisko). Zmiana poziomu wymaga decyzji Pawła.

## Kontrakty i zasady architektury

{{DOPISZ: kontrakty (nazwa, wersja, gdzie zapisane) i zasady architektury, które recenzent ma egzekwować. Przykład brzmienia: „kontrakt z wersją powstaje przed kodem”, „aplikacja nasłuchuje tylko na 127.0.0.1”.}}

## Pliki i katalogi, których recenzent nigdy nie czyta

Poza ogólnymi (`.env*`, klucze, bazy, `dane/`):

{{DOPISZ: lista, np. pliki konfiguracji z kluczami, katalogi produkcyjne, kopie zapasowe}}

## Dodatkowe klasy blokerów

Ogólne klasy (sekret; dostęp do danych poza zakresem projektu; zapis lub akcja na żywym systemie; złamanie kontraktu lub ADR) obowiązują zawsze. Dla tego projektu dochodzą:

{{DOPISZ: klasy specyficzne, np. „żadne pole z bazy danych osobowych nie trafia do bazy głównej, logów ani komunikatów”}}

## Pliki kontrolne (zmiany tylko za zgodą Pawła)

`.claude/`, `.githooks/`, `.git/config`, `tools/przeglad.py`, `tools/przeglad_konfig.py`, `tools/tests/test_settings.py`. Zmiana tych plików poza zakresem pakietu to uwaga BLOKUJĄCA.
