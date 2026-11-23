# Changelog

## 0.4.0 (23.11.2026)

Poprawki po pierwszym użyciu (PK-M0.1). Treść metody: `METODA.md` 0.4.

- **Szablon:** `.gitattributes` z `* text=auto eol=lf` (CRLF psuł nagłówek agenta pluginu); deny odczytu dla `.env.secrets*`, `.env.ci*`, `lokalne.yaml` i `settings.local.json`; deny `git diff *--no-index*`; asercje w `test_settings.py`; sekcja „Metoda” w `CLAUDE.md` (skille z przedrostkiem `/kuznia:`, etykiety, ASCII w commitach, układ ▶/👁); `.gitignore` z `docs/prywatne/` i `lokalne.yaml`.
- **`instaluj/windows.ps1`:**
  - blokady przez `GetAccessControl('Access')` i `SetAccessControl()` zamiast `Set-Acl`;
  - instalacja wymaga `-Repo` (bez niego niczego nie zmienia);
  - katalog pluginu i `.claude\CLAUDE.md` agenta nie są blokowane: tryby kontrolne porównują skróty z repo;
  - `-Sprawdz` bez fałszywego ostrzeżenia o „pustych wpisach (N)”;
  - nowy `-InstalujKatalogProjektow` (dziedziczony zakaz na `C:\Projects` plus jawne `Modify` na `_repo`);
  - nowy `-TestAgenta` na koncie agenta: foldery na `C:\`, podfoldery `C:\Projects`, `deniedMcpServers`, zapis w plikach kontrolnych, CRLF i skróty pluginu, `CLAUDE.md` agenta, `safe.directory`;
  - test przez `Start-Process -Credential` usunięty, wynik programów zewnętrznych czytany jako UTF-8.
- **Plugin:** wersja 0.4.0; `hooks/uruchom.sh` (przenośny wybór `python3`/`python`/`py`); skille `nowy-projekt` (kolejność: plugin, `git checkout`, commit, blokady, testy; kroki ▶ WKLEJ / 👁 POWINIENEŚ ZOBACZYĆ), `status` (ostrzeżenia o kolejności kluczy w settings i o starszej wersji pluginu), `pakiet` (kroki Pawła w układzie ▶/👁, łatka na pliki kontrolne z blokadami i `-TestAgenta`).
- **Silnik `przeglad.py`:** filtr `ACMRT` (przemianowany plik z sekretem nie omija już pre-commit); testy z polskimi nazwami plików dla `nowe_pliki` i z `core.quotePath=true`; test braku interpretera niezależny od systemu.
- **Testy repo:** `git ls-files -z` w teście repo publicznego.
- **Profil agenta:** `szablon-uzytkownika/settings.json` (blokada konektorów) i `profile.ps1` (czerwony znak zachęty).
- **Dokumentacja:** `README.md` (instalacja, sprawdzenie recenzenta, aktualizacja pluginu), `CLAUDE.md` i `docs/recenzja-projekt.md` samej kuźni (P0, repo publiczne), `maszyny/minipc.md`, usunięty nałożony `docs/po-pk-m0.patch`.

## 0.3.0 (23.11.2026)

Pierwsze wydanie repo i pluginu (PK-M0). Treść metody: `METODA.md` 0.3.

- Plugin `kuznia` (marketplace `kuznia-kodu`): agent `recenzent` (Opus, tylko odczyt), skille `pakiet`, `status`, `nowy-projekt`, `przenies`, `retro`, hooki w Pythonie (`PostToolUse`: składnia, `Stop`: testy z białej listy).
- `szablon/`: `CLAUDE.md`, `.claude/settings.json` (model `sonnet`, `acceptEdits`, `deniedMcpServers`, plugin z GitHuba), dokumenty (`recenzja-projekt`, `wdrozenie`, `stan`, `porzadki`, szablon pakietu), `tools/przeglad.py` (silnik) i `tools/przeglad_konfig.py` (konfiguracja projektu), `tools/tests/`, hooki git w `sh` (`.githooks/`, skan sekretów w Pythonie).
- `szablon-uzytkownika/CLAUDE.md` dla konta agenta.
- `maszyny/`: `minipc`, `legion` (szkic), `_szablon`.
- `instaluj/windows.ps1` (blokady NTFS metodą .NET, zmiana właściciela, tryb `-Sprawdz` z testem dostępu jako agent), `instaluj/linux.sh` (szkic `PROPOSED`).
- Ujednolicenie rozbieżności między dwoma pierwszymi projektami (R1-R17): `pytest` i `tools/tests/`, katalog `docs/`, odłożone uwagi w `docs/porzadki.md`, gałąź bazowa z upstreamu (domyślnie `main`, wariant `dev`), opisy commitów w ASCII, etykiety `FACT` / `PROPOSED` / `OPEN QUESTION` / `IDEA`.
- Poprawka silnika `przeglad.py`: w repo bez commitów wszystkie pliki liczą się jako nowe (kontrola importów nie kończy się FAIL).
- Testy repo publicznego: ogólne wzorce (IP, hosty, konta, ścieżki, etykiety kontraktów) i lokalna lista nazw zakazanych.
