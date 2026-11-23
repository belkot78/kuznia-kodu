# PK-M0 — repo `kuznia-kodu`: plugin `kuznia`, szablon, profile maszyn

Wykonawca: Claude Code (Sonnet) na miniPC, konto `claude-agent`. Recenzent: Opus (agent `recenzent` skopiowany tymczasowo z ekosystemu).
Normatyw: `METODA.md` w wersji 0.3 (w repo w katalogu głównym).

## Warunki wstępne (Paweł)
1. ✅ Repo `belkot78/kuznia-kodu` założone (publiczne, `main`, README). Sprawdzone 23.11.2026.
2. Sklonowane do `C:\Projects\_repo\kuznia-kodu`, `claude-agent` ma prawo zapisu (dziedziczone z `_repo`).
3. Pliki startowe w repo (commit i push przez Pawła, żeby `origin/main` zawierał punkt startu):
   - `METODA.md`;
   - `docs/pakiety/PK-M0-kuznia-kodu.md` (to zlecenie);
   - `.claude/agents/recenzent.md` (kopia z `ekosystem`, tymczasowa);
   - `.claude/settings.json` (minimalny, startowy);
   - `.gitignore`.

## Start bez `/pakiet` (tylko w tym pakiecie)
W tym repo nie ma jeszcze skilla `/pakiet` ani `tools/przeglad.py`, a hooki z ekosystemu szukałyby nieistniejących plików. Dlatego:
- Paweł otwiera sesję Claude Code w repo i wpisuje: `Przeczytaj METODA.md i docs/pakiety/PK-M0-kuznia-kodu.md. Przedstaw plan realizacji PK-M0 i czekaj na „dalej”.`
- **Bramka końcowa tego pakietu:**
  - testy powstałe w pakiecie (sekcja Testy) dają PASS;
  - agent `recenzent` ocenia `origin/main..HEAD`, z diffem wklejonym w polecenie, a przy dużym diffie w częściach, po etapach;
  - zasady blokerów i rund według `METODA.md` sekcja 3;
  - uwagi odłożone do `docs/porzadki.md`.
- Recenzent z ekosystemu ma w treści odwołania do ekosystemu (K1–K7, `ecosystem-docs`). W tym repo stosuje tylko części ogólne. To nie jest błąd pakietu.

## Stan dziś
- Metoda istnieje w dwóch kopiach: `C:\Projects\_repo\ekosystem` (wzorzec, PK-00…PK-11) i `C:\Projects\_repo\pathchaser-studio` (kopia z 20.11.2026, już z różnicami).
- Część ogólna i specyficzna są wymieszane, zwłaszcza w treści recenzenta.
- Model wykonawcy nie jest nigdzie zapisany.

## Cel
Jedno źródło metody, z którego korzystają wszystkie projekty i maszyny (Windows i Linux).

## Zakres

**Etap 1: inwentaryzacja (tylko odczyt).**
Porównaj w `ekosystem` i `pathchaser-studio`: agenta, skille, `settings.json`, `settings.local.json`, hooki Claude Code, `przeglad.py`, skan sekretów, `test_settings.py`, hooki git, `CLAUDE.md`.
Wynik zapisz w `docs/inwentaryzacja.md`. Każdy element dostaje kategorię:
- **OGÓLNE**: idzie do pluginu lub szablonu;
- **SPECYFICZNE**: zostaje w projekcie;
- **ROZBIEŻNOŚĆ**: opisz obie wersje i zaproponuj jedną.
Nie zmieniaj niczego w `ekosystem` ani `pathchaser-studio`.

**Etap 2: plugin `kuznia`** (marketplace w tym repo). Zawartość:
- `.claude-plugin/marketplace.json` i plugin `kuznia` z `plugin.json` (sprawdź składnię w oficjalnej dokumentacji Claude Code, tak jak w PK-00 ekosystemu).
- `agents/recenzent.md`: część ogólna recenzenta (zakres, kontrakty i ADR w ogólnym brzmieniu, bezpieczeństwo, poprawność, testy, styl, format odpowiedzi, wagi). Recenzent zawsze czyta `docs/recenzja-projekt.md` i wejście z `.recenzja/diff.patch`. `model: opus`, `tools: Read, Grep, Glob`.
- `skills/pakiet`: bramka według `METODA.md` sekcja 2–3. Diff przekazywany plikiem `.recenzja/diff.patch`, jeśli uda się to zrobić bez poszerzania allow. Jeśli nie, zostaw wklejanie i opisz ograniczenie. Odłożone uwagi zawsze do `docs/porzadki.md`. Zachowaj `disable-model-invocation: true`.
- `skills/status`: przeniesiony z ekosystemu, ogólny.
- `skills/nowy-projekt`: tworzy w pustym repo układ z `METODA.md` sekcja 4 z `szablon/` i pyta o nazwę, poziom P0–P2 oraz ścieżki.
- `skills/przenies`: czyta `docs/wdrozenie.md` i profil maszyny, wypisuje kroki (sam niczego nie instaluje).
- `skills/retro`: zbiera wnioski z logów pakietów i `docs/porzadki.md`, proponuje diff do `METODA.md` i wpis `CHANGELOG.md`.
- `hooks/`: odpowiednik `kontrola.py` (`PostToolUse` składnia, `Stop` testy). **Tylko Python, bez PowerShella.** Interpreter wybierany przenośnie: venv agenta, `.venv` repo, `python3`/`python`.
- Sprawdź, jak wywołuje się skille pluginu (z przedrostkiem `kuznia:` czy bez) i zapisz to w `README.md`.

**Etap 3: szablony.**
`szablon/` (repo projektu) zawiera:
- `CLAUDE.md` ze znacznikami do uzupełnienia;
- `.claude/settings.json` z `"model": "sonnet"`, `defaultMode`, allow/deny/ask z ekosystemu po ujednoliceniu, `deniedMcpServers` z PathChasera, `extraKnownMarketplaces` (źródło: GitHub `belkot78/kuznia-kodu`) i `enabledPlugins` dla `kuznia`;
- `docs/recenzja-projekt.md` (szablon sekcji 6 METODY);
- `docs/wdrozenie.md` (szablon sekcji 9);
- `docs/stan.md`, `docs/porzadki.md`, szablon pakietu;
- `tools/przeglad.py`, `tools/tests/test_settings.py`;
- hooki git, w tym skan sekretów przeniesiony z PowerShella do Pythona.

`szablon-uzytkownika/CLAUDE.md` (do `~/.claude/CLAUDE.md` konta agenta): kilka zdań, że obowiązuje metoda z `kuznia-kodu`, wykonawca to Sonnet, recenzent pochodzi z pluginu `kuznia`, a w repo bez pluginu należy zaproponować `/nowy-projekt` zamiast pracy według własnych zasad.

**Etap 4: maszyny i instalacja.**
- `maszyny/minipc.md`: na podstawie `CLAUDE.md` („Konto agenta”) i przewodnika PathChasera.
- `maszyny/legion.md`: szkic z polami do uzupełnienia, bo konto agenta jeszcze nie istnieje.
- `maszyny/_szablon.md`.
- `instaluj/windows.ps1` do uruchomienia przez Pawła jako administrator. Robi:
  - sprawdzenie, czy jest konto `claude-agent` (nie tworzy go);
  - skopiowanie `szablon-uzytkownika/CLAUDE.md` do profilu agenta;
  - blokady NTFS na plikach kontrolnych repo, katalogu pluginu i `~/.claude/CLAUDE.md` w profilu agenta, metodą .NET (nie `icacls /deny` z nawiasami);
  - zmianę właściciela na Pawła;
  - tryb `-Sprawdz`, który tylko raportuje stan. Zawiera test dostępu wykonywany jako `claude-agent`: każdy folder w `C:\Projects` poza `_repo` ma dać „odmowa”, a `_repo` „DOSTEP” (wzór: test z 23.11.2026 na miniPC, wynik poprawny). Ostrzega też o pustych wpisach `(N)` dla `claude-agent` (zezwolenie bez praw, a nie zakaz) i o folderach w `C:\Projects` bez blokady, np. nowo założonych.
- `instaluj/linux.sh`: szkic na później (P2 / Home Assistant), z oznaczeniem `PROPOSED`.

**Etap 5: dokumentacja i domknięcie startu.**
- `README.md`: co to jest i jak podłączyć projekt.
- `CHANGELOG.md` z wersją 0.3.
- Dopisz do `METODA.md` tylko wyniki rozbieżności z etapu 1 jako „Propozycje do METODA”. Treści metody nie zmieniaj samodzielnie.
- Przygotuj `docs/po-pk-m0.patch`, który zamienia tymczasowe `.claude/` tego repo na docelowe: `settings.json` z szablonu, z pluginem `kuznia` ładowanym z tego repo, bez kopii recenzenta. Nakłada go Paweł po pushu.

## Testy
- Offline: `test_settings.py` na `szablon/.claude/settings.json`.
- Walidacja JSON pluginu i marketplace.
- Test hooków na danych syntetycznych.
- Test skanu sekretów na sztucznym sekrecie w pliku tymczasowym.
- **Repo jest publiczne:** kontrola, że nie ma w nim adresów IP, nazw hostów, ścieżek z danymi ani nazw kont poza `claude-agent`, `Belkot`, `belko`.

## Ograniczenia
- Żadnych zmian w innych repo. Żadnych sekretów, adresów ani nazw kont poza `claude-agent`, `Belkot`, `belko`.
- `instaluj/*` agent pisze, ale **nie uruchamia**.
- Push, założenie blokad i instalacja pluginu: tylko Paweł.

## Kryteria
- Inwentaryzacja kompletna, każda rozbieżność opisana.
- Plugin instaluje się na koncie agenta z publicznego GitHuba bez poświadczeń i w nowej sesji widać agenta `recenzent` oraz skille.
- Szablon przechodzi własne testy.

## Log
(uzupełnia wykonawca)
