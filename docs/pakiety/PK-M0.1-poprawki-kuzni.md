# PK-M0.1 — poprawki kuźni po pierwszym użyciu

Repo: `C:\Projects\_repo\kuznia-kodu`. Wykonawca: Sonnet. Recenzent: `kuznia:recenzent` (plugin w wersji 0.3.0 z cache).
Uruchomienie: `/kuznia:pakiet PK-M0.1`. To pierwsze użycie skilla `pakiet` z pluginu.
Normatyw: `METODA.md` **0.4** (podmieniona przez Pawła przed tym pakietem).

## Stan dziś
- PK-M0 wykonany. Plugin działa w `kuznia-kodu` i w PathChaserze (PK-M2 PathChasera zakończony 23.11).
- Przy pierwszym użyciu wyszły problemy opisane w `METODA.md` 0.4 (sekcje 5, 8, 10 i 12):
  - CRLF psujący nagłówek agenta;
  - instalacja pluginu potrzebna w każdym projekcie i wymagająca zapisu w `.claude`;
  - przestawianie kolejności w `settings.json`;
  - blokady znikające po łatce;
  - „dubious ownership”;
  - test „jako agent” niedziałający przez SSH.
- `docs/porzadki.md` ma 15 pozycji „Z PK-M0”.
- `docs/stan.md` jest nieaktualny (podaje 8 commitów; po połączeniu był jeden).

## Cel
Kolejny projekt (Elektroklub) zakłada się według `METODA.md` 0.4, sekcja 10, bez ręcznych obejść z 23.11.

## Zakres

**Etap 1: szablon projektu.**
- `szablon/.gitattributes`: `* text=auto eol=lf`, przy zachowaniu obecnych reguł.
- `szablon/.claude/settings.json`:
  - zakazy odczytu `.env` jak w PathChaserze po PK-M2 (wyliczone warianty plus `.env.secrets*` i `.env.ci*`; `.env.example` dozwolony);
  - zakaz odczytu pliku lokalnej konfiguracji z konwencji szablonu i `settings.local.json`;
  - `Bash(git diff *--no-index*)` w deny;
  - asercje w `test_settings.py`.
- `szablon/CLAUDE.md`: sekcja „Metoda” ze skillami `/kuznia:…`, etykiety z METODA 0.4, zasada ASCII w commitach.
- `szablon/.gitignore`: `.recenzja/` i `docs/prywatne/`.

**Etap 2: `instaluj/windows.ps1`.**
Przed zmianami przeczytaj sekcję 8 METODY i pozycje #2, #7 i #8 z `porzadki.md`. Zmiany:
- **Blokady** zakładane przez `GetAccessControl('Access')` / `SetAccessControl()` zamiast `Set-Acl`. Ta metoda zadziałała przy ręcznym przywracaniu blokad PathChasera 23.11. Lista praw bez zmian.
- **Instalacja wymaga `-Repo`** (jednego albo kilku). Bez tego parametru kończy się komunikatem i niczego nie zmienia.
- **Katalog pluginu nie jest blokowany.** Zamiast tego tryby kontrolne porównują skróty plików pluginu w cache i `~/.claude/CLAUDE.md` z wersją z repo. Różnica to `[BLAD]`.
- **Tryby:**
  - `-Sprawdz` (Paweł, konto Belkot, bez zmian): właściciele, blokady, foldery w katalogu projektów bez blokady. **Usuń ostrzeżenie o „pustych wpisach (N)”**, bo opierało się na pomyłce: `(N)` w `icacls` to pełny zakaz (METODA 0.4, sekcja 12). Ostrzegaj tylko o regułach `Allow` z zerowymi prawami, jeśli w ogóle;
  - **nowy tryb instalacji katalogu projektów** według wzorca z Legiona (METODA sekcja 8): dziedziczony zakaz na `C:\Projects` (`InheritOnly`) plus jawne `Modify` na `_repo`, zamiast blokady każdego folderu osobno;
  - **nowy `-TestAgenta`** (Paweł uruchamia **zalogowany jako `claude-agent`**, niczego nie zmienia):
    - `whoami` na początku i przerwanie, jeśli to nie konto agenta;
    - test dostępu do **wszystkich** folderów na `C:\` (lista dozwolonych folderów systemowych w parametrze, reszta ma dać „odmowa”) i do podfolderów `C:\Projects` (tylko `_repo` ma DOSTEP);
    - obecność `deniedMcpServers` w `~/.claude/settings.json` agenta;
    - test zapisu plików kontrolnych każdego repo (`[IO.File]::Open(..., 'Open', 'Write')` i utworzenie pliku w `.claude`; ma być „odmowa”);
    - CRLF w plikach pluginu w cache;
    - zgodność skrótów pluginu z repo;
    - obecność `safe.directory` dla repo; przy braku wypisuje gotowe polecenie.

  Test przez `Start-Process -Credential` usuń.
- **Wynik testu** odczytuj z kodowaniem UTF-8 (#8b).
- **Komunikaty:** po instalacji przypomnienie o teście `-TestAgenta`. W pomocy skryptu kolejność z METODY sekcja 10: plugin przed blokadami.

**Etap 3: plugin.**
- `skills/nowy-projekt`: prowadzi według METODY sekcja 10. Kroki Pawła wypisuje w konwencji ▶ WKLEJ / 👁 POWINIENEŚ ZOBACZYĆ, z podanym kontem. Kolejność: plugin, potem `git checkout -- .claude/settings.json`, potem commit, blokady i testy.
- `skills/status`: ostrzega, gdy `.claude/settings.json` różni się od wersji w gicie tylko kolejnością kluczy (podaje `git checkout`), i gdy wersja pluginu w cache jest starsza niż w `plugin.json` repo kuźni (jeśli da się to ustalić bez sieci).
- `skills/pakiet`: baza `@{upstream}`, raport z krokami Pawła w konwencji ▶/👁. Jeśli łatka dotyczy plików kontrolnych, raport zawiera ponowne założenie blokad i `-TestAgenta`.
- `hooks/`: przenośny wybór interpretera (#9). Sprawdź w dokumentacji Claude Code, jak hook `command` jest uruchamiany na Windows, i dobierz rozwiązanie działające na Windows i Linuksie.
- `.claude-plugin/plugin.json`: wersja **0.4.0**.

**Etap 4: pozostałe pozycje z `docs/porzadki.md` („Z PK-M0”).**
Każdą pozycję albo poprawiasz, albo zamykasz z uzasadnieniem. Pozycje „[DECYZJA PAWŁA]” rozstrzyga METODA 0.4: #2 to wykrywanie zamiast zapobiegania, #12 to inwentaryzacja poza gitem. Obowiązkowo:
- #4: `--no-index`;
- #6: filtr `R` i `T` w `przeglad.py`;
- runda 2 #1: `git ls-files -z` w `test_publiczne.py`;
- runda 2 #2–#3: testy polskich nazw.

**Etap 5: dokumentacja kuźni.**
- `README.md`: instalacja według METODY sekcja 5 i 10, sprawdzenie recenzenta (sekcja 3), aktualizacja pluginu (podbicie wersji; awaryjnie `remove`/`add`).
- `CHANGELOG.md`: 0.4.0.
- `docs/stan.md`: aktualny.
- Usuń `docs/po-pk-m0.patch`, bo jest już nałożony.
- `maszyny/minipc.md`: `safe.directory`, dziedziczenie `(M)` w `_repo`, wynik testu dostępu z 23.11.
- `szablon-uzytkownika/CLAUDE.md`: skille z przedrostkiem `/kuznia:`.
- `szablon-uzytkownika/`: także wzór `~/.claude/settings.json` agenta z `deniedMcpServers` oraz wzór profilu PowerShell agenta (czerwony `[AGENT@<MASZYNA>]`, `Set-Location $HOME`). Instalacja i porównanie w `-TestAgenta`.
- `maszyny/legion.md`: uzupełnij z `metoda/legion-profil.md` z Projektu claude.ai (Paweł wgra plik do `docs/prywatne/` albo wklei treść; nazwy folderów prywatnych nie trafiają do repo publicznego).

## Testy
- Wszystkie testy kuźni i szablonu PASS, a test publicznego repo także z prywatną listą nazw.
- Nowe testy statyczne dla `windows.ps1`: brak `Set-Acl` w ścieżce blokad, `-Repo` wymagane w trybie instalacji, brak blokowania katalogu pluginu, obecność `-TestAgenta`.
- Testy szablonu: `.gitattributes` z LF, nowe deny.

## Ograniczenia
- `instaluj/*` piszesz, ale **nie uruchamiasz** (parser też nie, bo PowerShell masz zablokowany).
- Zmiany w `.claude/` **tego** repo tylko jako łatka `docs/pakiety/PK-M0.1-claude.patch`, o ile będą potrzebne.
- Treści `METODA.md` nie zmieniasz, dopisujesz najwyżej sekcję „Propozycje do METODA” na końcu.
- Repo jest publiczne: obowiązują zasady z METODY sekcja 5.

## Kryteria
- Testy PASS.
- Recenzent bez blokerów po najwyżej jednej dodatkowej rundzie.
- Każda pozycja „Z PK-M0” z `porzadki.md` ma status.

## Kroki Pawła po raporcie (przypomnienie dla raportu)
1. Push (jeśli w historii jest coś niedozwolonego, najpierw połączenie commitów).
2. Przegląd `instaluj/windows.ps1` przez czat (sekcja 8: kod uruchamiany przez administratora).
3. Aktualizacja pluginu u agenta do 0.4.0 i sprawdzenie recenzenta (sekcja 3).
4. Pierwsza prawdziwa instalacja blokad w `kuznia-kodu`: `windows.ps1 -Repo C:\Projects\_repo\kuznia-kodu`, potem `-TestAgenta` na koncie agenta.

## Log
(uzupełnia wykonawca)

### Wykonanie (23.11.2026, Sonnet)

**Zrobiono (5 etapów, commity lokalne):**
1. Szablon: `.gitattributes` z LF, deny (`.env.secrets*`, `.env.ci*`, `lokalne.yaml`, `settings.local.json`, `git diff *--no-index*`), asercje w `test_settings.py`, sekcja „Metoda” w `CLAUDE.md`, `.gitignore`. Łatka `docs/pakiety/PK-M0.1-claude.patch` dla `.claude/settings.json` tego repo (plik kontrolny, czeka na Pawła).
2. `instaluj/windows.ps1` przepisany: `GetAccessControl('Access')`/`SetAccessControl()`, `-Repo` wymagane, plugin i `CLAUDE.md` agenta bez blokady (wykrywanie skrótów), `-Sprawdz` bez ostrzeżenia o `(N)`, `-InstalujKatalogProjektow`, `-TestAgenta`, bez `Start-Process -Credential`, UTF-8. Skryptu nie uruchamiano ani nie parsowano.
3. Plugin 0.4.0: `hooks/uruchom.sh` (launcher `python3`/`python`/`py`), skille `nowy-projekt`, `status`, `pakiet`.
4. Pozycje z `porzadki.md`: wszystkie mają status (sekcja „Statusy po PK-M0.1”); poprawione m.in. #4, #6 (`ACMRT`), r2 #1-#3, #7, #9, #10.
5. Dokumentacja: `README.md`, `CHANGELOG.md` (0.4.0), `docs/stan.md`, `maszyny/minipc.md`, `szablon-uzytkownika/` (CLAUDE.md, `settings.json`, `profile.ps1`), `CLAUDE.md` i `docs/recenzja-projekt.md` kuźni, usunięty `docs/po-pk-m0.patch`.

**Decyzje wykonawcy:**
- `.claude\CLAUDE.md` agenta też bez blokady (METODA 0.4 sekcja 8: blokada pliku nie chroni przy pełnych prawach do katalogu nadrzędnego); zlecenie wymieniało wprost tylko katalog pluginu.
- `settings.json` i profil PowerShell agenta instalator kopiuje tylko, gdy ich brak (nie nadpisuje); `-TestAgenta` wymaga `deniedMcpServers` (BLAD) i zgodności `CLAUDE.md` (BLAD), a profilu tylko ostrzega.
- Hooki: shell form `sh "${CLAUDE_PLUGIN_ROOT}/hooks/uruchom.sh"`; wybór oparty na dokumentacji (Windows: Git Bash, bez niego PowerShell; kod 127 nieblokujący).
- `nowy-projekt`: pliki szablonu trzeba dodać do indeksu (`git add`) przed instalacją pluginu, inaczej `git checkout -- .claude/settings.json` nie ma do czego wrócić.
- Z polecenia Pawła: `CLAUDE.md` i `docs/recenzja-projekt.md` kuźni założone w etapie 5 (poza zleceniem); `maszyny/legion.md` pominięty (OPEN QUESTION w `stan.md`); lista nazw zakazanych nie istnieje, test publiczny zgłasza niepełną kontrolę.

**Testy:** `python -m pytest testy`: 102 passed, 2 skipped (lista nazw zakazanych; zgodność `.claude/settings.json` do nałożenia łatki). `python -m pytest szablon/tools/tests`: 86 passed. `przeglad.py` na repo kuźni: (b) sekrety PASS, (d) PASS, (c) FAIL z powodu atrapy `obcy.invalid` w istniejącym teście (fałszywy alarm, w `porzadki.md`).

**Recenzja:** runda 1: ODRZUCAM (bloker: `Test-Blokada` liczył reguły odziedziczone, przy wzorcu katalogu projektów dawał fałszywe OK; poprawione). Runda 2: ZATWIERDZAM Z UWAGAMI (nowe uwagi w `porzadki.md`, sekcja „Z PK-M0.1”: m.in. fałszywe `[BLAD]` od `szablon\.pytest_cache`).

**Odłożono:** uwagi w `docs/porzadki.md`, sekcja „Z PK-M0.1”; `maszyny/legion.md`; parser i przegląd `windows.ps1` przez Pawła/czat.

**Propozycje do METODA:** (1) sekcja 10 krok 5: przed `claude plugin install` pliki szablonu muszą być w indeksie, inaczej `git checkout -- .claude/settings.json` nie zadziała; (2) `-TestAgenta` wymaga polityki wykonywania pozwalającej wczytać profil, by czerwony znak zachęty działał (`OPEN QUESTION`).
