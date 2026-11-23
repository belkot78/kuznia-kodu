# kuznia-kodu

Metoda budowania aplikacji z AI: Sonnet wykonuje, Opus recenzuje. Repo zawiera zasady (`METODA.md`), plugin Claude Code `kuznia`, szablon projektu, profile maszyn i instalatory. Jest **publiczne**: nie ma tu sekretów, adresów, nazw hostów ani danych. Wszystko, co specyficzne i wrażliwe, zostaje w repo projektów.

Normatyw: [`METODA.md`](METODA.md) (wersja 0.4). Zmiany: [`CHANGELOG.md`](CHANGELOG.md). Wersja pluginu: 0.4.0.

## Co jest w repo

| Ścieżka | Zawartość |
|---|---|
| `METODA.md` | zasady pracy: role, cykl pakietu, recenzja, układ repo, poziomy dostępu P0-P2 |
| `CLAUDE.md`, `docs/` | zasady pracy i dokumentacja samej kuźni (`recenzja-projekt.md`, `stan.md`, `porzadki.md`, `pakiety/`) |
| `.claude-plugin/` | marketplace `kuznia-kodu` i manifest pluginu `kuznia` (plugin = cały katalog główny repo) |
| `agents/recenzent.md` | recenzent (Opus, `Read, Grep, Glob`), część ogólna |
| `skills/` | `pakiet`, `status`, `nowy-projekt`, `przenies`, `retro` |
| `hooks/` | `uruchom.sh` (przenośny wybór interpretera) i `kontrola.py` (PostToolUse: składnia, Stop: testy z białej listy) |
| `szablon/` | układ repo projektu: `CLAUDE.md`, `.claude/settings.json`, `.gitattributes`, `docs/`, `tools/`, `.githooks/` |
| `szablon-uzytkownika/` | profil konta agenta: `CLAUDE.md` (`~/.claude/CLAUDE.md`), `settings.json` (blokada konektorów, `~/.claude/settings.json`), `profile.ps1` (czerwony znak zachęty `[AGENT@<MASZYNA>]`) |
| `maszyny/` | profile maszyn (`minipc`, `legion` jako szkic, `_szablon`) |
| `instaluj/` | `windows.ps1` (blokady NTFS, `-Sprawdz`, `-TestAgenta`, `-InstalujKatalogProjektow`), `linux.sh` (szkic `PROPOSED`) |
| `testy/` | testy tego repo (plugin, szablon, instalatory, kontrola repo publicznego) |

## Jak podłączyć projekt

Pełna kolejność jest w `METODA.md`, sekcja 10. Skrót:

1. **Paweł, GitHub i Belkot:** nowe repo, klon do `C:\Projects\_repo\<nazwa>`, `safe.directory` dla konta agenta (`git config --global --add safe.directory <repo>` na koncie agenta).
2. **Agent, w katalogu repo:** `/kuznia:nowy-projekt` kopiuje `szablon/`, a potem instaluje plugin (punkt niżej) i podaje Pawłowi kroki.
3. **Instalacja pluginu (konto agenta, w każdym projekcie osobno).** `FACT` (dokumentacja Claude Code): wpis `enabledPlugins` w `.claude/settings.json` projektu **sam nie instaluje** pluginu z zewnętrznego źródła.
   ```
   claude plugin marketplace add belkot78/kuznia-kodu      # raz na konto
   claude plugin install kuznia@kuznia-kodu --scope project
   git checkout -- .claude/settings.json                   # instalator przestawia kolejność kluczy
   ```
   Pliki szablonu muszą wcześniej być w indeksie (`git add`), inaczej `git checkout` nie ma do czego wrócić. Instalacja idzie **przed** założeniem blokad, bo zapisuje `.claude/settings.json`.
4. **Paweł:** commit, push, `git config core.hooksPath .githooks`.
5. **Blokady (Paweł, administrator):** raz na maszynę `instaluj\windows.ps1 -InstalujKatalogProjektow`, potem dla każdego repo `instaluj\windows.ps1 -Repo C:\Projects\_repo\<nazwa>`. Bez `-Repo` instalator nic nie zmienia. Katalog pluginu nie jest blokowany; obroną jest wykrywanie zmian (`-Sprawdz`, `-TestAgenta`).
6. **Test jako agent (zalogowany jako `claude-agent`):** `instaluj\windows.ps1 -TestAgenta`. Blokada znika, gdy git zapisze plik od nowa (łatka, `pull`, `checkout`): po każdej takiej zmianie zakładasz blokady ponownie i powtarzasz test.
7. **Nowa sesja Claude Code:** `/status` (model Sonnet), sprawdzenie recenzenta (niżej), `/kuznia:status`, potem `/kuznia:pakiet PK-00`.

Przed pierwszym uruchomieniem `windows.ps1` sprawdź składnię parserem (konto Belkot, PowerShell): `[System.Management.Automation.Language.Parser]::ParseFile('instaluj\windows.ps1', [ref]$null, [ref]$e)`; lista błędów `$e` ma być pusta.

## Sprawdzenie recenzenta (po instalacji i po każdej aktualizacji pluginu)

W sesji Claude Code wpisz (METODA sekcja 3):

> Nie czytaj zadnych plikow. Przepisz doslownie opis i narzedzia agenta kuznia:recenzent z listy typow agentow narzedzia Agent.

Dobrze: opis „Niezalezny recenzent kodu…” i `(Tools: Read, Grep, Glob)`. Źle: „Agent from kuznia plugin” albo brak ograniczenia narzędzi: nagłówek agenta nie został odczytany (typowa przyczyna: pliki pluginu z CRLF; stąd `.gitattributes` z `eol=lf`). Pytanie „opisz agenta” niczego nie dowodzi, bo model może przeczytać plik.

## Aktualizacja pluginu

- Każda zmiana pluginu oznacza **podbicie wersji** w `.claude-plugin/plugin.json`; przy niezmienionej wersji cache u agenta się nie odświeża.
- Aktualizacja u agenta: `claude plugin marketplace update kuznia-kodu`, potem `claude plugin update kuznia@kuznia-kodu` (`PROPOSED`: nazwy poleceń według `claude plugin --help`), potem nowa sesja i sprawdzenie recenzenta.
- Awaryjnie: `claude plugin marketplace remove kuznia-kodu`, potem `add` i `install` jak wyżej.
- `/kuznia:status` ostrzega, gdy wersja w cache jest starsza (jeśli da się to ustalić bez sieci), a `instaluj\windows.ps1 -Sprawdz` porównuje skróty plików pluginu w cache z repo.

## Wywoływanie

- Skille pluginu mają przedrostek `kuznia:`: `/kuznia:pakiet PK-XX`, `/kuznia:status`, `/kuznia:nowy-projekt`, `/kuznia:przenies`, `/kuznia:retro` `FACT`. Forma bez przedrostka (`/pakiet`) `PROPOSED`: nie zakładać, sprawdzić w menu `/`.
- Agent: `kuznia:recenzent` (skill `pakiet` próbuje też samej nazwy `recenzent`).
- Skille mają `disable-model-invocation: true`: uruchamia je tylko człowiek.

## Ograniczenia (stan 0.4)

- **Diff dla recenzenta.** `/kuznia:pakiet` zapisuje go do `.recenzja/diff.patch` (katalog w `.gitignore`) poleceniem `git diff @{upstream}..HEAD > .recenzja/diff.patch`. Gdy uprawnienia odmówią, skill **nie poszerza allow**, tylko wkleja diff w polecenie dla recenzenta (przy dużym diffie po etapach).
- **Hooki pluginu** idą przez `sh hooks/uruchom.sh`, który wybiera `python3`, `python` albo `py`. `FACT` (dokumentacja Claude Code): na Windows polecenie hooka uruchamia Git Bash, a bez niego PowerShell; wtedy `sh` nie istnieje, polecenie kończy się kodem 127 (błąd nieblokujący, powiadomienie w transkrypcji) i kontrola hooka nie działa. Konto agenta widzi Pythona tylko, gdy jest zainstalowany dla wszystkich użytkowników. Do testów w hooku Stop wybierany jest przenośnie: `~/.venvs/<nazwa-repo>`, `.venv` repo, interpreter hooka.
- **Uprawnień plugin nie przenosi.** Listy `allow`/`deny`/`ask` powstają z szablonu i zostają w `.claude/settings.json` projektu; pilnuje ich `tools/tests/test_settings.py`.
- **`instaluj/windows.ps1` jest napisany, ale nie był uruchamiany** (ani parsowany przez PowerShell przez agenta). Jako kod uruchamiany przez administratora wymaga przeglądu przez człowieka lub czat (METODA sekcja 8). Pierwsze uruchomienie: parser, potem `-Sprawdz`.
- **`instaluj/linux.sh`** to szkic `PROPOSED`.

## Testy

```
python -m pytest testy                       # plugin, szablon (z jego własnymi testami), instalatory, repo publiczne
python -m pytest szablon/tools/tests         # tylko szablon
```

Test repo publicznego (`testy/test_publiczne.py`) szuka adresów IP, nazw hostów, ścieżek poza `C:\Projects\_repo`, kont innych niż `claude-agent`, `Belkot`, `belko` oraz etykiet kontraktów `K`/`Z` poza `METODA.md` i `docs/pakiety/`. Lista nazw zakazanych (brokerzy, pliki z tokenami, katalogi produkcyjne) jest **lokalna i poza gitem** (`docs/prywatne/zakazane_nazwy.txt`); bez niej test sprawdza tylko wzorce ogólne i zgłasza (jako pominięty test), że sprawdzenie jest niepełne.
