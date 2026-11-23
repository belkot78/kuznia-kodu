---
name: status
description: Krótki raport stanu projektu (pakiet bieżący i następny, decyzje Pawła, commity do pushu, ryzyka z datami)
disable-model-invocation: true
---

Robisz raport stanu bieżącego projektu. Tylko odczyt: nie edytujesz plików, nie robisz commitów, nie uruchamiasz testów ani niczego poza poleceniami gita niżej.

## Co zrobić
1. Przeczytaj `docs/stan.md` oraz plik pakietu oznaczonego tam jako „następny” (z `docs/pakiety/`). Nie czytaj `.env*`, kluczy, baz, `dane/` ani niczego z sekretami.
2. Uruchom: `git status --short`, `git log --oneline -10`, `git log --oneline @{upstream}..HEAD` (gdy gałąź nie ma upstreamu, napisz „brak upstreamu” zamiast zgadywać).
3. **Kolejność kluczy w `.claude/settings.json`:** jeśli `git status --short` pokazuje ten plik jako zmieniony, porównaj go z wersją z gita (`git show HEAD:.claude/settings.json`). Gdy zawartość jest ta sama i różni się tylko kolejnością kluczy (typowy skutek `claude plugin install`), ostrzeż i podaj polecenie `git checkout -- .claude/settings.json` (nie wykonujesz go sam). Gdy różnią się wartości, napisz to osobno i nie nazywaj tego kolejnością.
4. **Wersja pluginu:** odczytaj `${CLAUDE_PLUGIN_ROOT}/.claude-plugin/plugin.json` (wersja w cache, czyli ta uruchomiona). Jeśli da się to ustalić bez sieci, porównaj z `.claude-plugin/plugin.json` w lokalnej kopii marketplace (`~/.claude/plugins/marketplaces/kuznia-kodu/`, `PROPOSED`: ścieżka nie jest potwierdzona dokumentacją) albo w repo kuźni, jeśli jest dostępne. Gdy wersja w cache jest starsza, ostrzeż: zaktualizuj plugin (README `kuznia-kodu`, sekcja „Aktualizacja”). Gdy nie możesz tego ustalić (brak pliku albo dostępu), napisz „wersja pluginu: nie wiem”, bez zgadywania.

## Raport (10-15 linii, po polsku, bez ozdobników)
- Pakiet bieżący (ostatnio wykonany) i następny, z jednozdaniowym stanem.
- Otwarte decyzje i pytania Pawła (z oznaczeniem `FACT` / `PROPOSED` / `OPEN QUESTION` / `IDEA`).
- Commity czekające na push (lista z `@{upstream}..HEAD`; jeśli pusta, napisz to) oraz czy drzewo robocze jest czyste.
- Ostrzeżenia z punktów 3 i 4 (kolejność kluczy w settings, wersja pluginu), jeśli dotyczą.
- Ryzyka z datą (np. terminy, blokady do założenia), tylko te, które mają termin lub dotyczą najbliższych dni.
- Jedno sugerowane polecenie na teraz (np. `/kuznia:pakiet PK-XX`), z jednym zdaniem uzasadnienia.

Jeśli czegoś nie wiesz z plików lub gita, napisz „nie wiem”, nie zgaduj.
