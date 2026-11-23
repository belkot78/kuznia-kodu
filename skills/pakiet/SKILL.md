---
name: pakiet
description: Wykonaj cały pakiet PK-XX z docs/pakiety zgodnie z metodą (plan, praca, bramka końcowa z recenzentem, log, raport)
argument-hint: PK-XX
disable-model-invocation: true
---

Wykonujesz pakiet $ARGUMENTS w bieżącym repo. Jeśli nie podano numeru pakietu, zapytaj o niego i nic nie rób. Wykonawcą jest Sonnet, recenzentem agent `recenzent` (Opus). Nie zmieniasz zasad metody; zmiany metody idą przez `/kuznia:retro`.

## 0. Start
- `git status` i `git log --oneline -10`. Drzewo musi być czyste; jeśli nie jest, zatrzymaj się i opisz.
- Przeczytaj: `CLAUDE.md`, `docs/stan.md`, `docs/recenzja-projekt.md`, plik `docs/pakiety/$ARGUMENTS-*.md` oraz pliki, które pakiet wskazuje.
- Gałąź robocza i interpreter bierz z `CLAUDE.md` (sekcje „Git” i „Konto agenta”). Jeśli CLAUDE.md wskazuje gałąź roboczą, pracujesz tylko na niej (`git branch --show-current`); na innej zatrzymaj się.
- Nigdy nie czytaj plików i katalogów oznaczonych w `CLAUDE.md` i `docs/recenzja-projekt.md` jako zakazane (m.in. `.env*`, klucze, bazy, `dane/`).
- Sprawdź warunki wstępne z pakietu i `docs/stan.md`. Jeśli któryś nie jest spełniony, zatrzymaj się i napisz który (to powrót do planisty).
- Sprawdź log pakietu i `git log`: nie powtarzaj tego, co już zrobiono.

## 1. Plan (jedyna bramka na starcie)
Pokaż krótki plan: etapy, pliki do zmiany, co uruchomisz, w których momentach będzie potrzebny Paweł. Czekaj na „dalej”.

## 2. Praca
- Po „dalej” wykonujesz cały zakres bez zatrzymywania się po etapach. Nic ponad zakres.
- Commit lokalny po każdym etapie. Opis po polsku **bez polskich liter (ASCII)**. Nigdy `--no-verify`, `git push`, `git stash`, `git tag`.
- Interpreter: venv konta agenta `~/.venvs/<nazwa-repo>` (Windows: `Scripts\python.exe`, Linux: `bin/python`), nie `.venv` repo. Instalujesz tylko pakiety z plików zależności repo i tylko do tego venv; o każdą inną instalację pytasz.
- Zatrzymujesz się TYLKO, gdy:
  a) potrzebna jest decyzja, której pakiet ani dokumenty nie rozstrzygają: podaj opcje z rekomendacją;
  b) krok wymaga sekretów, logowania, żywego systemu albo danych spoza zakresu: podaj Pawłowi gotową komendę z etykietą okna;
  c) potrzebna jest zmiana poza zakresem pakietu albo w plikach kontrolnych (`.claude/`, hooki git, `tools/przeglad.py`, skan sekretów, `test_settings.py`);
  d) ten sam błąd nie ustępuje po 2 próbach naprawy;
  e) coś wygląda na incydent (np. przypadkowe uruchomienie czegoś na żywym systemie): natychmiast, z opisem, bez prób naprawy.
- Zmiana pliku kontrolnego zablokowanego przez system (błąd EPERM): przygotuj `docs/pakiety/$ARGUMENTS-<plik>.patch` i zatrzymaj się; Paweł zrobi `git apply --check`, `git apply`, `git diff` i ponownie założy blokadę, potem robisz commit.

## 3. Bramka końcowa
1. Testy offline i `python tools/przeglad.py` (interpreter agenta): oba muszą dać PASS.
2. Przygotuj wejście dla recenzenta: katalog `.recenzja/` (jest w `.gitignore`) i diff bazy `origin/…` ze zmianami: `git diff @{upstream}..HEAD > .recenzja/diff.patch`. Gdy gałąź nie ma upstreamu, podaj bazę jawnie (commit startowy pakietu). Jeśli przekierowanie do pliku zostanie odrzucone przez uprawnienia, NIE poszerzaj allow: wklej diff w polecenie dla recenzenta (przy dużym diffie po etapach) i odnotuj to w raporcie jako ograniczenie.
3. Wywołaj agenta `recenzent` (z pluginu `kuznia`; typ w Agent tool: `kuznia:recenzent`, a gdy go nie ma na liście, `recenzent`). Podaj mu: zlecenie pakietu, `docs/recenzja-projekt.md` i ścieżkę `.recenzja/diff.patch`. Recenzent nie ma narzędzi do uruchamiania poleceń; to, czego nie da się sprawdzić bez uruchomienia, sprawdzasz Ty.
4. Uwagi BLOKUJĄCE klas: sekret; dostęp do danych poza zakresem projektu; zapis lub akcja na żywym systemie zewnętrznym; złamanie kontraktu lub ADR; klasy dopisane w `docs/recenzja-projekt.md`. Poprawiasz i wołasz recenzenta jeszcze raz. **Najwyżej jedna dodatkowa runda**; jeśli po niej nadal są blokery, zatrzymujesz się i opisujesz, bez dalszego łatania. Inne blokery opisujesz w raporcie; decyzja należy do Pawła.
5. Pozostałe uwagi nie wracają do poprawek: dopisujesz każdą jedną linią do `docs/porzadki.md`, w sekcji „Z $ARGUMENTS” (utwórz sekcję, jeśli jej nie ma).

## 4. Zamknięcie
- Dopisz log na dole pakietu: co zrobiono, decyzje, werdykt recenzenta, co odłożono.
- Zaktualizuj `docs/stan.md`: status pakietu, testy, ryzyka, otwarte pytania, kolejny pakiet.
- Commit lokalny.
- Raport końcowy dla Pawła: co zmieniono, wyniki testów i `przeglad.py`, werdykt recenzenta, odłożone uwagi, `git diff --stat @{upstream}..HEAD` i komenda push (według `CLAUDE.md`). Dodaj, że po zmianie ustawień, hooków lub skilli Paweł restartuje sesję Claude Code (nowe reguły działają dopiero w nowej sesji).
- Oznaczaj stwierdzenia: `FACT`, `PROPOSED`, `OPEN QUESTION`, `IDEA`.
