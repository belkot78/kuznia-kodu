# Changelog

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
