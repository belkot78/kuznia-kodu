# {{NAZWA}}: zasady pracy dla Claude Code

Projekt prowadzony metodą `kuznia-kodu` (plugin `kuznia`): wykonawca Sonnet, recenzent Opus (agent `recenzent`), właściciel Paweł. Zasady metody są w pluginie i w repo `kuznia-kodu` (`METODA.md`); tu jest tylko to, co dotyczy tego projektu.

## Kontekst projektu

- {{OPIS: czym jest aplikacja, dla kogo, stos technologiczny, układ repo, gdzie działa}}
- Dokumentacja robocza: `docs/` (`stan.md`, `pakiety/`, `porzadki.md`, `recenzja-projekt.md`, `wdrozenie.md`, `adr/`).
- Poziom dostępu projektu: **{{POZIOM}}** (P0: tylko kod i dane syntetyczne; P1: odczyt żywych systemów; P2: sterowanie żywym systemem). Zmiana poziomu wymaga decyzji Pawła.

## Bezpieczeństwo (najważniejsze)

- Nigdy nie czytaj, nie wypisuj, nie kopiuj i nie wklejaj do odpowiedzi: `.env*` (poza `.env.example`), kluczy (`*.pem`, `*.key`), tokenów i haseł, baz (`*.db`, `*.sqlite*`), `dane/`, logów z danymi, {{DOPISZ: pliki i katalogi zakazane w tym projekcie}}.
- Nie twórz `.env`, baz ani plików z prawdziwą treścią. Testy używają katalogów tymczasowych i danych syntetycznych.
- Pracuj tylko w tym repozytorium. Nie wchodź do katalogów działających aplikacji, Dokumentów ani OneDrive.
- Jeśli zadanie wymaga prawdziwych danych, kluczy lub żywego systemu, zatrzymaj się i poproś Pawła o wynik polecenia bez sekretów.
- Zdalne serwery MCP są zablokowane w `.claude/settings.json` (`deniedMcpServers`). Nie próbuj tego obchodzić.

## Konto agenta

- Claude Code działa jako konto bez uprawnień administratora (`claude-agent`). Granice dostępu pilnuje system operacyjny, a reguły w `.claude/settings.json` są drugą warstwą.
- Brak dostępu do czegoś spoza repo jest oczekiwany. Nie obchodź tego: zatrzymaj się i podaj Pawłowi komendę z etykietą okna.
- Interpreter: `{{VENV_PYTHON}}`. Instalacje tylko z plików zależności repo i tylko do tego venv.
- Brak poświadczeń GitHub: `fetch`, `pull` i `push` robi Paweł.
- Pliki kontrolne (`.claude/`, `.githooks/`, `.git/config`, `tools/przeglad.py`, `tools/przeglad_konfig.py`, `tools/tests/test_settings.py`) mają blokadę zapisu. Zmianę przygotuj jako `docs/pakiety/PK-XX-<plik>.patch` i zatrzymaj się; nakłada ją Paweł.

## Git

- Gałąź robocza: **{{GALAZ}}**. Baza do porównań (`git log @{upstream}..HEAD`) to gałąź śledzona (upstream).
- Commit po zakończonym etapie. **Opis po polsku, ale bez polskich liter (ASCII)** (kodowanie znaków przy przekazywaniu z konsoli Windows do gita). Przed commitem `git status`; nie dodawaj plików z `.gitignore`.
- `git push` tylko po wyraźnym „tak” Pawła. Nigdy `--force`. Komenda push dla Pawła: {{KOMENDA_PUSH}}.
- Nie omijaj kontroli sekretów (hook pre-commit): bez `--no-verify`. Fałszywy alarm rozwiąż zmianą kodu (np. nazwy zmiennej) albo wyjątkiem w `tools/przeglad_konfig.py` (przez Pawła).

## Styl pracy

- Odpowiadaj po polsku, krótko. Po zadaniu napisz: co zmieniono, co sprawdzono, co zostało.
- Nie zgaduj. W dokumentach oznaczaj stwierdzenia: `FACT`, `PROPOSED`, `OPEN QUESTION`, `IDEA`.
- Zakres i kolejność pakietów wg `docs/pakiety/`; nie rozbudowuj zakresu na własną rękę.

## Metoda

Skille pluginu `kuznia` wywołuje człowiek (model ich nie widzi), zawsze z przedrostkiem:
- `/kuznia:status`: stan repo i środowiska, na początku sesji;
- `/kuznia:pakiet PK-XX`: wykonanie pakietu (plan, praca, bramka końcowa z recenzentem, log, raport);
- `/kuznia:nowy-projekt`: założenie projektu według `METODA.md` sekcja 10;
- `/kuznia:przenies`: przeniesienie aplikacji na inną maszynę (według `docs/wdrozenie.md`);
- `/kuznia:retro`: wnioski do zmiany metody (zmiany zasad idą tylko tą drogą).

Zasady:
- Etykiety stwierdzeń (w dokumentach i raportach): `FACT` (sprawdzone), `PROPOSED` (do potwierdzenia), `OPEN QUESTION` (decyzja do podjęcia), `IDEA` (pomysł na później).
- Opisy commitów po polsku, **tylko ASCII** (bez polskich liter).
- Zmian zasad metody nie robisz sam: dopisz „Propozycję do METODA” w logu pakietu.
- Kroki dla Pawła piszesz w stałym układzie: **▶ WKLEJ** (blok do wklejenia, z nazwą konta i okna) i **👁 POWINIENEŚ ZOBACZYĆ** (oczekiwany wynik, zwykły tekst).
- Po zmianie ustawień, hooków lub skilli Paweł restartuje sesję Claude Code (nowe reguły działają dopiero w nowej sesji).

## Jak zaczynać sesję

- Na początku sesji uruchom `/kuznia:status`. Pakiet uruchamia `/kuznia:pakiet PK-XX`.
- Rób tylko zakres tego pakietu. Na końcu dopisz log na dole pakietu i zaktualizuj `docs/stan.md`.
- Commit lokalnie, bez `git push` (push robi Paweł po przeczytaniu raportu).
