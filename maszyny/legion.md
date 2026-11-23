# Profil maszyny: legion (szkic)

Stan z 23.11.2026: konto agenta na tej maszynie jeszcze nie istnieje, więc pola oznaczone `OPEN QUESTION` czekają na uzupełnienie przez właściciela. Do tego czasu na tej maszynie nie uruchamia się Claude Code jako agent.

| Pole | Wartość |
|---|---|
| System i wersja | `OPEN QUESTION` (do uzupełnienia) |
| Rola maszyny | `OPEN QUESTION` (np. laptop właściciela; bez aplikacji produkcyjnych?) |
| Konto agenta | `OPEN QUESTION`: konto bez uprawnień administratora, np. `claude-agent` (jak na `minipc`) |
| Konto właściciela / administratora | `OPEN QUESTION` |
| Katalog repozytoriów | `OPEN QUESTION` (proponowane: osobny katalog z prawem zapisu tylko dla agenta, jak `C:\Projects\_repo` na `minipc`) |
| Interpreter dla agenta | `PROPOSED`: `~/.venvs/<nazwa-repo>` na koncie agenta, Python zainstalowany dla wszystkich użytkowników |
| Instalacja Pythona/Node | `OPEN QUESTION` |
| Rodzaj izolacji | `PROPOSED`: jak na `minipc` (blokady NTFS plus druga warstwa w `settings.json`) |
| Instalator | `instaluj/windows.ps1` po założeniu konta agenta; tryb `-Sprawdz` do weryfikacji |
| Dostępne poziomy dostępu | `PROPOSED`: P0 |
| Uwagi | Kolejność uruchomienia: konto agenta, katalog repo, Python dla wszystkich, `instaluj/windows.ps1 -Sprawdz`, instalacja pluginu, blokady |
