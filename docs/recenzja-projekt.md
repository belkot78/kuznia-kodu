# Recenzja: część specyficzna dla projektu kuznia-kodu

Ten plik czyta agent `recenzent` na starcie każdej recenzji. To jedyne miejsce, w którym dostaje wiedzę o tym projekcie. Część ogólna recenzji jest w agencie (plugin `kuznia`). Projekt to repo samej metody (publiczne), więc recenzent ocenia także zgodność zmian z `METODA.md`.

## Poziom dostępu

**P0** (tylko kod i dane syntetyczne). Zmiana poziomu wymaga decyzji Pawła.

## Kontrakty i zasady architektury

- `METODA.md` jest normatywna. Zmiana jej treści należy do Pawła (sekcja 11); wykonawca najwyżej dopisuje sekcję „Propozycje do METODA”. Zmiana zasad metody w innym pliku (skill, szablon, README) bez odpowiednika w `METODA.md` albo wbrew niej to uwaga BLOKUJĄCA.
- Plugin to cały katalog główny repo (marketplace wskazuje `./`). Każda zmiana pluginu (agent, skille, hooki, szablony) wymaga podbicia wersji w `.claude-plugin/plugin.json` i wpisu w `CHANGELOG.md`.
- Szablon i jego testy muszą być spójne: lista `allow`/`deny`/`ask` w `szablon/.claude/settings.json` jest DOKŁADNIE taka jak w `szablon/tools/tests/test_settings.py`, a `.claude/settings.json` tego repo jest zgodny z szablonem (`testy/test_settings_repo.py`).
- Uprawnień plugin nie przenosi (METODA sekcja 5): żadnego `settings.json` w katalogu głównym pluginu, żadnych `permissions` w manifeście ani `hooks.json`.
- Skille mają `disable-model-invocation: true`. Recenzent ma narzędzia `Read, Grep, Glob` i model `opus`; zmiana któregokolwiek z tych ustawień to uwaga BLOKUJĄCA.
- `instaluj/windows.ps1` jest uruchamiany przez administratora, a pisze go agent: nie wolno w nim dodawać tworzenia kont, zmiany polityki wykonywania, pobierania z sieci ani poszerzania uprawnień agenta. Blokady wyłącznie metodą .NET (`GetAccessControl('Access')` i `SetAccessControl()`), plik wyłącznie ASCII. Skryptu nie uruchamia się w testach, a recenzent nie ma narzędzia do jego uruchomienia: ocena jest statyczna, a składnię sprawdza Paweł parserem.
- Hooki pluginu przechodzą przez `hooks/uruchom.sh` (przenośny wybór interpretera); `hooks.json` nie wywołuje `python` wprost.
- Pliki tekstowe zawsze z LF (`.gitattributes`); `instaluj/*.sh` i `hooks/*.sh` bez CRLF.

## Pliki i katalogi, których recenzent nigdy nie czyta

Poza ogólnymi (`.env*`, klucze, bazy, `dane/`):

- `docs/prywatne/` (lokalne listy nazw i inwentaryzacja, poza gitem),
- `lokalne.yaml`, `.claude/settings.local.json`.

## Dodatkowe klasy blokerów

Ogólne klasy (sekret; dostęp do danych poza zakresem projektu; zapis lub akcja na żywym systemie; złamanie kontraktu lub ADR) obowiązują zawsze. Dla tego projektu dochodzi:

- **Złamanie zasad repo publicznego z METODA sekcja 5.** Zakazane wszędzie: nazwy brokerów, pliki z tokenami, nazwy folderów produkcyjnych, numery kont, adresy i hosty (także w przykładach, testach i logach pakietów). Dozwolone: nazwy projektów jako przykłady; etykiety kontraktów `K`/`Z` tylko w `METODA.md` i `docs/pakiety/`; konta `claude-agent`, `Belkot`, `belko`; ścieżki w `C:\Projects\_repo`. Zawartość `docs/prywatne/` w gicie albo w diffie to bloker.
- **Wycieczka z lokalnej listy nazw zakazanych**: recenzent nie ma do niej dostępu, więc pilnuje wzorców ogólnych; pełną kontrolę nazw robi test lokalnie, gdy lista istnieje.

## Pliki kontrolne (zmiany tylko za zgodą Pawła)

`.claude/`, `.githooks/`, `.git/config`. W tym repo plikiem kontrolnym nie jest `tools/przeglad.py` (silnik leży w `szablon/tools/` i jest częścią szablonu). Zmiana plików kontrolnych poza zakresem pakietu to uwaga BLOKUJĄCA; zmiana w `.claude/` ma iść jako łatka `docs/pakiety/PK-XX-claude.patch`.
