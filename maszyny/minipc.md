# Profil maszyny: minipc

Stan z 23.11.2026. Źródło: opis konta agenta w `CLAUDE.md` projektów i doświadczenia z PK-00 pierwszych projektów. Bez adresów, nazw hostów i ścieżek z danymi.

| Pole | Wartość |
|---|---|
| System i wersja | Windows 11 Pro `FACT` |
| Rola maszyny | maszyna robocza agenta Claude Code; na niej działają też aplikacje właściciela (poza repozytoriami) |
| Konto agenta | `claude-agent`: zwykły użytkownik, bez uprawnień administratora `FACT` |
| Konto właściciela / administratora | `Belkot` (właściciel plików kontrolnych, robi `fetch`, `pull`, `push`), `belko` (administrator, tylko człowiek) `FACT` |
| Katalog repozytoriów | `C:\Projects\_repo`; `claude-agent` ma na nim jawne `Modify`, które nowe podfoldery i repo dziedziczą jako `(M)` (w `icacls` widać `(OI)(CI)(M)`) `FACT`. Po założeniu klonu przez konto właściciela sprawdź, że agent dziedziczy `(M)` (`icacls <repo>`, METODA sekcja 10, krok 2) |
| Katalog projektów | `C:\Projects`: dla agenta dziedziczony zakaz `FullControl` tylko w dół (`(OI)(CI)(IO)`, w `icacls` jako `(N)`) i zakaz zakładania czegokolwiek bezpośrednio w katalogu; jawne `Modify` na `_repo` wygrywa z odziedziczonym zakazem. Wynik testu dostępu jako agent z 23.11.2026: wszystkie pozostałe podkatalogi `C:\Projects` dają odmowę, a `_repo` dostęp `FACT` (wzorzec z Legiona; w `icacls` `(N)` oznacza pełny zakaz, nie puste zezwolenie). Zakładanie wzorca: `instaluj\windows.ps1 -InstalujKatalogProjektow` `PROPOSED`: tryb `-InstalujKatalogProjektow` nie był jeszcze uruchomiony (skrypt napisany w PK-M0.1) |
| Interpreter dla agenta | `C:\Users\claude-agent\.venvs\<nazwa-repo>\Scripts\python.exe` (Python 3.12) `FACT`. Python 3.12 jest zainstalowany dla wszystkich użytkowników; Python z profilu właściciela jest dla agenta niewidoczny |
| Instalacja Pythona/Node | tylko w instalacji dla wszystkich użytkowników, inaczej konto agenta jej nie widzi `FACT` |
| Rodzaj izolacji | blokady NTFS: granicą jest system, reguły `settings.json` to druga warstwa `FACT`. Pliki kontrolne mają blokadę zapisu dla agenta, a właścicielem jest `Belkot` |
| Instalator | `instaluj/windows.ps1` (uruchamia `Belkot` lub administrator; `-Repo` wymagane w instalacji, `-Sprawdz` tylko raportuje, `-InstalujKatalogProjektow` zamyka katalog projektów, `-TestAgenta` uruchamia się zalogowanym jako `claude-agent`). Kolejność w nowym projekcie: plugin, commit, blokady, `-TestAgenta` (METODA sekcja 10) |
| Dostępne poziomy dostępu | P0: tak. P1: tak, z wąskim tokenem tylko do odczytu, decyzja właściciela per projekt. P2: nie (wymaga osobnego środowiska, np. VM Linux) |
| Poświadczenia GitHub | brak na koncie agenta; `fetch`, `pull`, `push` robi właściciel |
| Uwagi | Git zgłasza „dubious ownership” dla repozytoriów, których właścicielem jest grupa Administrators `FACT`. Rozwiązanie z 23.11.2026: wyjątek `safe.directory` w konfiguracji konta agenta, dla każdego repo osobno: `git config --global --add safe.directory <repo z ukośnikami />`, wykonywane w oknie konta `claude-agent` (robi Paweł albo skrypt, agent nie zmienia konfiguracji globalnej sam); brak wpisu wykrywa `-TestAgenta`. Pliki pluginu w cache agenta muszą mieć końcówki LF (`.gitattributes` z `eol=lf`); konto agenta ma `autocrlf=true` `FACT`. Test jako agent robimy tylko w oknie z czerwonym znakiem zachęty `[AGENT@<MASZYNA>]` (wzór: `szablon-uzytkownika/profile.ps1`) |
