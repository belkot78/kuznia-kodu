---
name: status
description: Krótki raport stanu projektu (pakiet bieżący i następny, decyzje Pawła, commity do pushu, ryzyka z datami)
disable-model-invocation: true
---

Robisz raport stanu bieżącego projektu. Tylko odczyt: nie edytujesz plików, nie robisz commitów, nie uruchamiasz testów ani niczego poza trzema poleceniami gita niżej.

## Co zrobić
1. Przeczytaj `docs/stan.md` oraz plik pakietu oznaczonego tam jako „następny” (z `docs/pakiety/`). Nie czytaj `.env*`, kluczy, baz, `dane/` ani niczego z sekretami.
2. Uruchom: `git status --short`, `git log --oneline -10`, `git log --oneline @{upstream}..HEAD` (gdy gałąź nie ma upstreamu, napisz „brak upstreamu” zamiast zgadywać).

## Raport (10-15 linii, po polsku, bez ozdobników)
- Pakiet bieżący (ostatnio wykonany) i następny, z jednozdaniowym stanem.
- Otwarte decyzje i pytania Pawła (z oznaczeniem `FACT` / `PROPOSED` / `OPEN QUESTION` / `IDEA`).
- Commity czekające na push (lista z `@{upstream}..HEAD`; jeśli pusta, napisz to) oraz czy drzewo robocze jest czyste.
- Ryzyka z datą (np. terminy, blokady do założenia), tylko te, które mają termin lub dotyczą najbliższych dni.
- Jedno sugerowane polecenie na teraz (np. `/kuznia:pakiet PK-XX`), z jednym zdaniem uzasadnienia.

Jeśli czegoś nie wiesz z plików lub gita, napisz „nie wiem”, nie zgaduj.
