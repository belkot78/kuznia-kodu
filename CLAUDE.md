# kuznia-kodu: zasady pracy dla Claude Code

To jest repo samej metody (`METODA.md`), pluginu Claude Code `kuznia`, szablonów, profili maszyn i instalatorów. Repo jest **publiczne** (`belkot78/kuznia-kodu`). Prowadzone jest własną metodą: wykonawca Sonnet, recenzent Opus (agent `recenzent`), właściciel Paweł.

## Kontekst projektu

- Zawartość: patrz `README.md` (tabela „Co jest w repo”). Plugin to cały katalog główny repo, więc `szablon/`, `maszyny/` i `instaluj/` są częścią pluginu.
- Dokumentacja robocza: `docs/` (`stan.md`, `pakiety/`, `porzadki.md`, `recenzja-projekt.md`). Normatyw: `METODA.md`; **treść `METODA.md` zmienia Paweł** (z czatem), ty najwyżej dopisujesz sekcję „Propozycje do METODA”.
- Poziom dostępu projektu: **P0** (tylko kod i dane syntetyczne). Zmiana poziomu wymaga decyzji Pawła.
- Testy: `python -m pytest testy` (plugin, szablon z jego własnymi testami, instalatory, kontrola repo publicznego) oraz `python -m pytest szablon/tools/tests`. W repo kuźni nie ma `tools/przeglad.py`; silnik kontroli jest w `szablon/tools/` i działa na szablonie.

## Repo publiczne: czego nie wolno

- Zakazane wszędzie: nazwy brokerów, pliki z tokenami, nazwy folderów produkcyjnych, numery kont, adresy i hosty, ścieżki spoza `C:\Projects\_repo` (poza nazwami kont `claude-agent`, `Belkot`, `belko`).
- Nazwy projektów wolno tylko jako przykłady. Etykiety kontraktów `K`/`Z` tylko w `METODA.md` i `docs/pakiety/`.
- Lista nazw zakazanych jest lokalna i poza gitem (`docs/prywatne/`, w `.gitignore`). Nigdy jej nie czytaj, nie kopiuj i nie wklejaj; test `testy/test_publiczne.py` czyta ją sam, a gdy jej brak, zgłasza niepełną kontrolę (to oczekiwane na tej maszynie).
- Atrapy sekretów w testach składaj z fragmentów, inaczej skan sekretów je zgłasza.

## Bezpieczeństwo (najważniejsze)

- Nigdy nie czytaj, nie wypisuj, nie kopiuj i nie wklejaj do odpowiedzi: `.env*` (poza `.env.example`), kluczy (`*.pem`, `*.key`), tokenów i haseł, baz (`*.db`, `*.sqlite*`), `dane/`, `docs/prywatne/`, `lokalne.yaml`, `.claude/settings.local.json`.
- Nie twórz `.env`, baz ani plików z prawdziwą treścią.
- Pracuj tylko w tym repozytorium. Nie wchodź do katalogów działających aplikacji, Dokumentów ani OneDrive.
- Jeśli zadanie wymaga prawdziwych danych, kluczy lub żywego systemu, zatrzymaj się i poproś Pawła o wynik polecenia bez sekretów.
- **Kod uruchamiany przez administratora** (`instaluj/*`, łatki na pliki kontrolne) piszesz, ale nie uruchamiasz; najpierw czyta go ktoś inny niż agent (Paweł albo czat).
- Zdalne serwery MCP są zablokowane w `.claude/settings.json` (`deniedMcpServers`). Nie próbuj tego obchodzić.

## Konto agenta

- Claude Code działa jako konto bez uprawnień administratora (`claude-agent`). Granice dostępu pilnuje system operacyjny, a reguły w `.claude/settings.json` są drugą warstwą.
- Brak dostępu do czegoś spoza repo jest oczekiwany. Nie obchodź tego: zatrzymaj się i podaj Pawłowi komendę z etykietą okna.
- Interpreter: `~/.venvs/kuznia-kodu` (Windows: `C:\Users\claude-agent\.venvs\kuznia-kodu\Scripts\python.exe`). Instalacje tylko z plików zależności repo (`szablon/tools/requirements-dev.txt`) i tylko do tego venv.
- Brak poświadczeń GitHub: `fetch`, `pull` i `push` robi Paweł.
- Pliki kontrolne (`.claude/`, `.githooks/`, `.git/config`) mają blokadę zapisu. Zmianę przygotuj jako `docs/pakiety/PK-XX-<plik>.patch` i zatrzymaj się; nakłada ją Paweł. Zmiany w `szablon/` nie są zmianami plików kontrolnych tego repo.

## Git

- Gałąź robocza: **main**. Baza do porównań (`git log @{upstream}..HEAD`) to gałąź śledzona (upstream).
- Commit po zakończonym etapie. **Opis po polsku, ale bez polskich liter (ASCII)**. Przed commitem `git status`; nie dodawaj plików z `.gitignore`.
- `git push` tylko po wyraźnym „tak” Pawła. Nigdy `--force`. Komenda push dla Pawła (konto Belkot, okno z repo): `git push origin main`.
- Bez `--no-verify`. Fałszywy alarm rozwiąż zmianą kodu, nie omijaniem kontroli.

## Styl pracy

- Odpowiadaj po polsku, krótko. Po zadaniu napisz: co zmieniono, co sprawdzono, co zostało.
- Nie zgaduj. W dokumentach oznaczaj stwierdzenia: `FACT`, `PROPOSED`, `OPEN QUESTION`, `IDEA`.
- Zakres i kolejność pakietów wg `docs/pakiety/`; nie rozbudowuj zakresu na własną rękę.

## Metoda

Skille pluginu `kuznia` wywołuje człowiek (model ich nie widzi), zawsze z przedrostkiem: `/kuznia:status`, `/kuznia:pakiet PK-XX`, `/kuznia:nowy-projekt`, `/kuznia:przenies`, `/kuznia:retro`. Zmiany zasad metody idą tylko przez `/kuznia:retro` i Pawła.

- Kroki dla Pawła pisz w układzie: **▶ WKLEJ** (blok do wklejenia, z nazwą konta i okna) i **👁 POWINIENEŚ ZOBACZYĆ** (oczekiwany wynik, zwykły tekst).
- Każda zmiana pluginu oznacza podbicie wersji w `.claude-plugin/plugin.json` i wpis w `CHANGELOG.md`.
- Po zmianie ustawień, hooków lub skilli Paweł restartuje sesję Claude Code (nowe reguły działają dopiero w nowej sesji).

## Jak zaczynać sesję

- Na początku sesji uruchom `/kuznia:status`. Pakiet uruchamia `/kuznia:pakiet PK-XX`.
- Rób tylko zakres tego pakietu. Na końcu dopisz log na dole pakietu i zaktualizuj `docs/stan.md`.
- Commit lokalnie, bez `git push` (push robi Paweł po przeczytaniu raportu).
