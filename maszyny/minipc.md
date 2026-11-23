# Profil maszyny: minipc

Stan z 23.11.2026. Źródło: opis konta agenta w `CLAUDE.md` projektów i doświadczenia z PK-00 pierwszych projektów. Bez adresów, nazw hostów i ścieżek z danymi.

| Pole | Wartość |
|---|---|
| System i wersja | Windows 11 Pro `FACT` |
| Rola maszyny | maszyna robocza agenta Claude Code; na niej działają też aplikacje właściciela (poza repozytoriami) |
| Konto agenta | `claude-agent`: zwykły użytkownik, bez uprawnień administratora `FACT` |
| Konto właściciela / administratora | `Belkot` (właściciel plików kontrolnych, robi `fetch`, `pull`, `push`), `belko` (administrator, tylko człowiek) `FACT` |
| Katalog repozytoriów | `C:\Projects\_repo`; `claude-agent` ma prawo zapisu (dziedziczone z `_repo`). Wszystkie pozostałe podkatalogi `C:\Projects` mają dla agenta odmowę dostępu `FACT` (test z 23.11.2026) |
| Interpreter dla agenta | `C:\Users\claude-agent\.venvs\<nazwa-repo>\Scripts\python.exe` (Python 3.12) `FACT`. Python 3.12 jest zainstalowany dla wszystkich użytkowników; Python z profilu właściciela jest dla agenta niewidoczny |
| Instalacja Pythona/Node | tylko w instalacji dla wszystkich użytkowników, inaczej konto agenta jej nie widzi `FACT` |
| Rodzaj izolacji | blokady NTFS: granicą jest system, reguły `settings.json` to druga warstwa `FACT`. Pliki kontrolne mają blokadę zapisu dla agenta, a właścicielem jest `Belkot` |
| Instalator | `instaluj/windows.ps1` (uruchamia `Belkot` lub administrator; tryb `-Sprawdz` tylko raportuje) |
| Dostępne poziomy dostępu | P0: tak. P1: tak, z wąskim tokenem tylko do odczytu, decyzja właściciela per projekt. P2: nie (wymaga osobnego środowiska, np. VM Linux) |
| Poświadczenia GitHub | brak na koncie agenta; `fetch`, `pull`, `push` robi właściciel |
| Uwagi | Git zgłasza „dubious ownership” dla repozytoriów, których właścicielem jest grupa Administrators. `PROPOSED`: właściciel dopisuje wyjątek `safe.directory` w konfiguracji konta agenta albo ustawia właściciela repo na `Belkot` (agent nie zmienia konfiguracji globalnej sam) |
