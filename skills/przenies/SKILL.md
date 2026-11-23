---
name: przenies
description: Przygotuj kroki uruchomienia aplikacji na tej maszynie (czyta docs/wdrozenie.md i profil maszyny); niczego nie instaluje
disable-model-invocation: true
---

Przygotowujesz plan przeniesienia aplikacji na bieżącą maszynę. **Niczego nie instalujesz, nie uruchamiasz i nie tworzysz poza notatką z planem.** Tylko odczyt i wypisanie kroków.

## Co zrobić
1. Przeczytaj `docs/wdrozenie.md` bieżącego repo (wymagania, pliki lokalne spoza repo, porty, usługi i autostart, kroki instalacji, kontrola działania). Jeśli go nie ma, zatrzymaj się i napisz, że repo nie ma opisu wdrożenia.
2. Znajdź profil tej maszyny: `maszyny/<nazwa>.md` w repo `kuznia-kodu` (w katalogu pluginu: `${CLAUDE_PLUGIN_ROOT}/maszyny/`). Jeśli profilu nie ma, wskaż `maszyny/_szablon.md` i zapytaj Pawła o brakujące pola (system, konta, katalog repo, interpreter, rodzaj izolacji, dostępne poziomy P0-P2).
3. Porównaj wymagania z profilem maszyny: wersje Pythona/Node, poziom dostępu projektu (P0-P2) kontra poziom dostępny na maszynie, wolne porty, usługi.
4. Nie czytaj plików lokalnych spoza repo (`dane/`, `lokalne.yaml`, `.env*`). W planie wymień tylko ich **nazwy i pola** z `docs/wdrozenie.md`.

## Wynik (po polsku, numerowana lista)
- Co jest już spełnione, a czego brakuje (z odniesieniem do profilu).
- Kroki do wykonania w kolejności, każdy z podziałem: robi agent (tylko w repo, bez instalacji) / robi Paweł (instalacje, usługi, autostart, blokady systemowe).
- Dane i sekrety, których potrzebuje Paweł (tylko nazwy pól; wartości podaje Paweł lokalnie, nigdy do czatu ani repo).
- Kontrola, czy działa (z `docs/wdrozenie.md`).
- Rozbieżności między `docs/wdrozenie.md` a profilem maszyny oznacz `OPEN QUESTION`.
