---
name: nowy-projekt
description: Utwórz w pustym repo układ projektu według metody (CLAUDE.md, ustawienia, dokumenty, narzędzia kontrolne) z szablonu
argument-hint: [nazwa-projektu]
disable-model-invocation: true
---

Zakładasz układ projektu według `METODA.md` (sekcja 4) w bieżącym, **pustym** repo. Szablon leży w katalogu pluginu: `${CLAUDE_PLUGIN_ROOT}/szablon/`. Nie zmieniasz szablonu, tylko kopiujesz z niego pliki.

## 0. Sprawdź stan
- `git status` i `ls`. Jeśli w repo są już pliki projektu (poza `.git`, `README.md`, `LICENSE`, `.gitignore`), zatrzymaj się i zapytaj, czy kontynuować; nie nadpisuj istniejących plików.
- Jeśli `${CLAUDE_PLUGIN_ROOT}/szablon/` nie istnieje, zatrzymaj się i napisz, że plugin `kuznia` nie jest poprawnie zainstalowany.

## 1. Zapytaj Pawła (jedno pytanie z kilkoma polami)
1. Nazwa projektu (domyślnie: $ARGUMENTS albo nazwa katalogu repo). Dozwolone: małe litery, cyfry, myślnik.
2. Poziom dostępu: **P0** (tylko kod i dane syntetyczne; domyślny), **P1** (odczyt żywych systemów, wąski token tylko do odczytu), **P2** (sterowanie żywym systemem, osobne środowisko). Dla P1 i P2 zaznacz, że wymaga decyzji Pawła i uzupełnienia `docs/recenzja-projekt.md`.
3. Gałąź robocza: `main` (domyślnie) albo `dev` (wariant: agent pracuje na `dev`, a `main` zostaje dla wydań).
4. Ścieżka repo na tej maszynie i nazwa venv agenta (domyślnie `~/.venvs/<nazwa>`).

## 2. Skopiuj i uzupełnij
- Skopiuj pliki z `szablon/` do repo, zachowując układ katalogów. Zamień znaczniki we wszystkich kopiowanych plikach (także w `.claude/settings.json` i `tools/tests/test_settings.py`, które muszą zostać zgodne): `{{NAZWA}}`, `{{POZIOM}}`, `{{GALAZ}}`, `{{VENV_PYTHON}}` (pełna ścieżka interpretera venv agenta, w settings w formie z `/`, np. `/c/Users/claude-agent/.venvs/<nazwa>/Scripts/python.exe`), `{{KOMENDA_PUSH}}` (komenda push dla Pawła na tej maszynie). Pozostałe znaczniki `{{...}}` (opis projektu, kontrakty, katalogi zakazane) zostaw: wypełnia je planista z Pawłem w PK-00 projektu. Nie kopiuj `docs/pakiety/_szablon-pakietu.md` pod inną nazwą; zostaje jako wzór dla planisty.
- Dla wariantu `dev` dodaj do `deny` w `.claude/settings.json` reguły dla gałęzi: `git checkout|switch|merge|rebase|reset` z `main` i tagami oraz `git tag*`; dla `main` ich nie dodawaj. Zaktualizuj `tools/tests/test_settings.py` tak, by pilnował tego samego zestawu.
- W `CLAUDE.md` wpisz poziom dostępu i gałąź roboczą (te dwie wartości czytają skille `pakiet` i `status`).
- Nie twórz `.env`, baz ani żadnych plików z danymi.

## 3. Sprawdź
- Uruchom `python tools/przeglad.py` i testy w `tools/tests/` interpreterem agenta. Muszą dać PASS.
- Jeśli brakuje venv agenta lub `pytest`, podaj Pawłowi komendy do uruchomienia (nie instaluj niczego poza venv agenta).

## 4. Zostaw Pawłowi (nie robisz tego sam)
Wypisz gotową listę kroków:
1. `git add` i commit początkowy (opis ASCII), potem `git push` (robi Paweł).
2. Włączenie hooków git: `git config core.hooksPath .githooks` (zmiana `.git/config` jest zablokowana dla agenta).
3. Instalacja pluginu: `claude plugin install kuznia@kuznia-kodu --scope project` (wpis w `.claude/settings.json` sam nie instaluje pluginu, patrz README `kuznia-kodu`).
4. Założenie blokad systemowych na pliki kontrolne (`instaluj/windows.ps1` z repo `kuznia-kodu`) i restart sesji Claude Code.
5. PK-00 projektu u planisty: wypełnienie `docs/recenzja-projekt.md` i `CLAUDE.md`.

Oznaczaj stwierdzenia: `FACT`, `PROPOSED`, `OPEN QUESTION`, `IDEA`.
