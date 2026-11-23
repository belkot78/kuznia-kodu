# kuznia-kodu

Metoda budowania aplikacji z AI: Sonnet wykonuje, Opus recenzuje. Repo zawiera zasady (`METODA.md`), plugin Claude Code `kuznia`, szablon projektu, profile maszyn i instalatory. Jest **publiczne**: nie ma tu sekretów, adresów, nazw hostów ani danych. Wszystko, co specyficzne i wrażliwe, zostaje w repo projektów.

Normatyw: [`METODA.md`](METODA.md) (wersja 0.3). Zmiany: [`CHANGELOG.md`](CHANGELOG.md).

## Co jest w repo

| Ścieżka | Zawartość |
|---|---|
| `METODA.md` | zasady pracy: role, cykl pakietu, recenzja, układ repo, poziomy dostępu P0-P2 |
| `.claude-plugin/` | marketplace `kuznia-kodu` i manifest pluginu `kuznia` (plugin = cały katalog główny repo) |
| `agents/recenzent.md` | recenzent (Opus, `Read, Grep, Glob`), część ogólna |
| `skills/` | `pakiet`, `status`, `nowy-projekt`, `przenies`, `retro` |
| `hooks/` | `kontrola.py` (PostToolUse: składnia, Stop: testy z białej listy), tylko Python |
| `szablon/` | układ repo projektu: `CLAUDE.md`, `.claude/settings.json`, `docs/`, `tools/`, `.githooks/` |
| `szablon-uzytkownika/` | `CLAUDE.md` do profilu konta agenta (`~/.claude/CLAUDE.md`) |
| `maszyny/` | profile maszyn (`minipc`, `legion` jako szkic, `_szablon`) |
| `instaluj/` | `windows.ps1` (blokady NTFS, tryb `-Sprawdz`), `linux.sh` (szkic `PROPOSED`) |
| `testy/` | testy tego repo (pluginu, szablonu, instalatorów, kontrola repo publicznego) |

## Jak podłączyć projekt

1. **Nowy projekt.** W pustym repo, w sesji Claude Code z zainstalowanym pluginem: `/kuznia:nowy-projekt`. Skill pyta o nazwę, poziom (P0-P2) i gałąź roboczą, kopiuje `szablon/` i podaje Pawłowi listę kroków.
2. **Instalacja pluginu (robi Paweł).** `FACT` (dokumentacja Claude Code, 23.11.2026): wpis `enabledPlugins` w `.claude/settings.json` projektu **sam nie instaluje** pluginu z zewnętrznego źródła; Claude Code instaluje go tylko, gdy włączenie pochodzi z ustawień użytkownika, `settings.local.json` albo flagi `--settings`. Dlatego w każdym projekcie i na każdej maszynie:
   ```
   claude plugin marketplace add belkot78/kuznia-kodu
   claude plugin install kuznia@kuznia-kodu --scope project
   ```
   Wpis `extraKnownMarketplaces` w szablonie podpowiada marketplace po zaufaniu folderu. Po instalacji nowa sesja widzi agenta `recenzent` i skille. `OPEN QUESTION`: poprawność tej procedury potwierdzi pierwsza instalacja z publicznego GitHuba po pushu.
3. **Hooki git (robi Paweł, raz na klon):** `git config core.hooksPath .githooks`.
4. **Blokady systemowe (Paweł, administrator):** `instaluj\windows.ps1` (najpierw `-Sprawdz`), potem restart sesji Claude Code.

## Wywoływanie

- Skille pluginu mają przedrostek `kuznia:`: `/kuznia:pakiet PK-XX`, `/kuznia:status`, `/kuznia:nowy-projekt`, `/kuznia:przenies`, `/kuznia:retro` `FACT` (dokumentacja pokazuje zawsze formę z przedrostkiem). Forma bez przedrostka (`/pakiet`) `PROPOSED`: nie zakładać, sprawdzić w menu `/`.
- Agent: `kuznia:recenzent` `PROPOSED` (forma `plugin:agent` z dokumentacji; skill `pakiet` próbuje też samej nazwy `recenzent`).
- Skille mają `disable-model-invocation: true`: uruchamia je tylko człowiek.

## Ograniczenia (stan 0.3)

- **Diff dla recenzenta.** `/kuznia:pakiet` zapisuje go do `.recenzja/diff.patch` (katalog w `.gitignore`) poleceniem `git diff @{upstream}..HEAD > .recenzja/diff.patch`. `OPEN QUESTION`: czy przekierowanie do pliku przechodzi przy samych regułach `allow` z szablonu (`Bash(git diff *)`) nie zostało potwierdzone; próba na tej maszynie przeszła, ale przy poleceniu spoza allow. Gdy uprawnienia odmówią, skill **nie poszerza allow**, tylko wkleja diff w polecenie dla recenzenta (przy dużym diffie po etapach).
- **Hooki pluginu wywołują `python`** z PATH. Konto agenta widzi go tylko, gdy Python jest zainstalowany dla wszystkich użytkowników. Do testów w hooku Stop wybierany jest przenośnie: `~/.venvs/<nazwa-repo>`, `.venv` repo, interpreter hooka.
- **Uprawnień plugin nie przenosi.** Listy `allow`/`deny`/`ask` powstają z szablonu i zostają w `.claude/settings.json` projektu; pilnuje ich `tools/tests/test_settings.py`.
- **`instaluj/windows.ps1` jest napisany, ale nie był uruchamiany** (ani parsowany przez PowerShell na tej maszynie). Pierwsze uruchomienie: tryb `-Sprawdz`.
- **`instaluj/linux.sh`** to szkic `PROPOSED`.

## Testy

```
python -m pytest testy                       # plugin, szablon (z jego własnymi testami), instalatory, repo publiczne
python -m pytest szablon/tools/tests         # tylko szablon
```

Test repo publicznego (`testy/test_publiczne.py`) szuka adresów IP, nazw hostów, ścieżek poza `C:\Projects\_repo`, kont innych niż `claude-agent`, `Belkot`, `belko` oraz etykiet kontraktów `K`/`Z` poza `METODA.md` i `docs/pakiety/`. Lista nazw zakazanych (brokerzy, pliki z tokenami, katalogi produkcyjne) jest **lokalna i poza gitem** (`docs/prywatne/zakazane_nazwy.txt`); bez niej test sprawdza tylko wzorce ogólne i zgłasza, że sprawdzenie jest niepełne.
