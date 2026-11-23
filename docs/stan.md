# Stan repo kuznia-kodu

Oznaczenia: `FACT`, `PROPOSED`, `OPEN QUESTION`, `IDEA`. Aktualizuje wykonawca na końcu pakietu.

## Pakiety
| Pakiet | Stan | Uwagi |
|---|---|---|
| PK-M0 | wykonany i wypchnięty | plugin, szablon, maszyny, instalacja; recenzja: ZATWIERDZAM Z UWAGAMI (runda 2); log w pakiecie |
| PK-M0.1 | wykonany lokalnie, czeka na push i kroki Pawła | poprawki po pierwszym użyciu, METODA 0.4, plugin 0.4.0; werdykt recenzenta i log w pakiecie |

## Testy
- `FACT`: `python -m pytest testy` i `python -m pytest szablon/tools/tests` przechodzą (liczby w logu pakietu PK-M0.1).
- `FACT`: test zgodności `.claude/settings.json` tego repo z szablonem jest **pomijany** do czasu nałożenia `docs/pakiety/PK-M0.1-claude.patch` (komunikat „OCZEKUJE NA PAWŁA”); po nałożeniu wymaga zgodności.
- `FACT`: test repo publicznego pomija sprawdzenie listy nazw zakazanych, bo na tej maszynie nie ma `docs/prywatne/zakazane_nazwy.txt` (kontrola niepełna: tylko wzorce ogólne).

## Otwarte decyzje i pytania (Paweł)
- `OPEN QUESTION`: nałożenie łatki `docs/pakiety/PK-M0.1-claude.patch` na `.claude/settings.json` (zmiany deny: `.env.secrets*`, `.env.ci*`, `lokalne.yaml`, `settings.local.json`, `git diff *--no-index*`), potem blokady od nowa i `-TestAgenta`.
- `OPEN QUESTION`: przegląd `instaluj/windows.ps1` przez czat (kod uruchamiany przez administratora, METODA sekcja 8) i sprawdzenie parserem `Parser::ParseFile`. Skrypt nie był uruchamiany ani parsowany.
- `OPEN QUESTION`: `maszyny/legion.md` uzupełnić z `metoda/legion-profil.md` z Projektu claude.ai (Paweł wgrywa plik do `docs/prywatne/` albo wkleja treść; nazwy folderów prywatnych nie trafiają do repo publicznego). Pominięte w PK-M0.1 decyzją Pawła.
- `OPEN QUESTION`: nazwy poleceń aktualizacji pluginu w README (`claude plugin marketplace update`, `claude plugin update`) są `PROPOSED`; potwierdzić przy pierwszej aktualizacji do 0.4.0.
- `OPEN QUESTION`: test braku interpretera w `test_hooki.py` (gałąź Linuksa, dowiązania) nie był uruchamiany na Linuksie.
- `OPEN QUESTION`: zmiany w `szablon/` (m.in. `przeglad.py` z filtrem `ACMRT`, `test_settings.py`) trafiają do istniejących projektów dopiero po ich przeniesieniu; zasięg do decyzji Pawła (PathChaser, ekosystem).
- Wcześniejsze pytania z PK-M0 (publiczna instalacja pluginu z GitHuba, forma wywołania skilli bez przedrostka) zostają do potwierdzenia przy aktualizacji do 0.4.0.

## Czeka na push
- Commity lokalne PK-M0.1: `git log --oneline @{upstream}..HEAD`.

## Następny pakiet
- Brak zleconego. Kolejny projekt (Elektroklub) zakłada się według `METODA.md` 0.4, sekcja 10, po wykonaniu kroków Pawła z raportu PK-M0.1.
