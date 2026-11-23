---
name: nowy-projekt
description: Utwórz w pustym repo układ projektu według metody (CLAUDE.md, ustawienia, dokumenty, narzędzia kontrolne) z szablonu, zainstaluj plugin i poprowadź Pawła przez blokady i testy
argument-hint: [nazwa-projektu]
disable-model-invocation: true
---

Zakładasz układ projektu według `METODA.md` (sekcje 4 i 10) w bieżącym, **pustym** repo. Szablon leży w katalogu pluginu: `${CLAUDE_PLUGIN_ROOT}/szablon/`. Nie zmieniasz szablonu, tylko kopiujesz z niego pliki.

Kolejność jest stała (METODA sekcja 10): **plugin, potem `git checkout -- .claude/settings.json`, potem commit, blokady i testy**. Blokady idą na końcu, bo instalator pluginu zapisuje `.claude/settings.json`, a po założeniu blokad zapis nie byłby możliwy.

## 0. Sprawdź stan
- `git status` i `ls`. Jeśli w repo są już pliki projektu (poza `.git`, `README.md`, `LICENSE`, `.gitignore`), zatrzymaj się i zapytaj, czy kontynuować; nie nadpisuj istniejących plików.
- Jeśli `git status` zgłasza „dubious ownership”, zatrzymaj się i podaj Pawłowi krok `safe.directory` (patrz punkt 5, krok 1). To zmiana globalnej konfiguracji gita konta agenta, której nie robisz sam.
- Jeśli `${CLAUDE_PLUGIN_ROOT}/szablon/` nie istnieje, zatrzymaj się i napisz, że plugin `kuznia` nie jest poprawnie zainstalowany.

## 1. Zapytaj Pawła (jedno pytanie z kilkoma polami)
1. Nazwa projektu (domyślnie: $ARGUMENTS albo nazwa katalogu repo). Dozwolone: małe litery, cyfry, myślnik.
2. Poziom dostępu: **P0** (tylko kod i dane syntetyczne; domyślny), **P1** (odczyt żywych systemów, wąski token tylko do odczytu), **P2** (sterowanie żywym systemem, osobne środowisko). Dla P1 i P2 zaznacz, że wymaga decyzji Pawła i uzupełnienia `docs/recenzja-projekt.md`.
3. Gałąź robocza: `main` (domyślnie) albo `dev` (wariant: agent pracuje na `dev`, a `main` zostaje dla wydań).
4. Ścieżka repo na tej maszynie i nazwa venv agenta (domyślnie `~/.venvs/<nazwa>`).

## 2. Skopiuj i uzupełnij
- Skopiuj pliki z `szablon/` do repo, zachowując układ katalogów. Zamień znaczniki we wszystkich kopiowanych plikach (także w `.claude/settings.json` i `tools/tests/test_settings.py`, które muszą zostać zgodne): `{{NAZWA}}`, `{{POZIOM}}`, `{{GALAZ}}`, `{{VENV_PYTHON}}` (pełna ścieżka interpretera venv agenta, w settings w formie z `/`, np. `/c/Users/claude-agent/.venvs/<nazwa>/Scripts/python.exe`), `{{KOMENDA_PUSH}}` (komenda push dla Pawła na tej maszynie). Pozostałe znaczniki `{{...}}` (opis projektu, kontrakty, katalogi zakazane) zostaw: wypełnia je planista z Pawłem w PK-00 projektu. Nie kopiuj `docs/pakiety/_szablon-pakietu.md` pod inną nazwą; zostaje jako wzór dla planisty.
- Skopiuj też `.gitattributes` z szablonu (`* text=auto eol=lf`): bez niego git na koncie agenta może zapisać pliki pluginu z CRLF i Claude Code nie odczyta nagłówka recenzenta.
- Dla wariantu `dev` dodaj do `deny` w `.claude/settings.json` reguły dla gałęzi: `git checkout|switch|merge|rebase|reset` z `main` i tagami oraz `git tag*`; dla `main` ich nie dodawaj. Zaktualizuj `tools/tests/test_settings.py` tak, by pilnował tego samego zestawu.
- W `CLAUDE.md` wpisz poziom dostępu i gałąź roboczą (te dwie wartości czytają skille `pakiet` i `status`).
- Nie twórz `.env`, baz ani żadnych plików z danymi.

## 3. Plugin (przed blokadami)
1. Dodaj skopiowane pliki do indeksu (`git add` tylko plików szablonu, nie ignorowanych). To warunek kroku 3: `git checkout -- .claude/settings.json` przywraca plik z indeksu albo z commita, więc plik nieśledzony zostałby z przestawioną kolejnością kluczy.
2. Raz na konto (sprawdź `claude plugin marketplace list`): `claude plugin marketplace add belkot78/kuznia-kodu`. Potem w tym repo: `claude plugin install kuznia@kuznia-kodu --scope project`. Wpisy `extraKnownMarketplaces` i `enabledPlugins` w `settings.json` tylko włączają plugin, nie instalują go.
3. Instalator przestawia kolejność kluczy w `.claude/settings.json`. Przywróć plik: `git checkout -- .claude/settings.json`. Sprawdź `git diff --stat`: dla tego pliku nie ma być różnic.
4. Jeśli instalacja pluginu wymaga zgody, której nie masz, albo `claude` nie jest dostępne w PATH, zatrzymaj się i podaj Pawłowi to polecenie w układzie z punktu 5.

## 4. Sprawdź
- Uruchom `python tools/przeglad.py` i testy w `tools/tests/` interpreterem agenta. Muszą dać PASS.
- Jeśli brakuje venv agenta lub `pytest`, podaj Pawłowi komendy do uruchomienia (nie instaluj niczego poza venv agenta, tylko z plików zależności repo).

## 5. Zostaw Pawłowi (nie robisz tego sam)
Wypisz kroki w stałym układzie. Każdy krok ma **▶ WKLEJ** (blok do wklejenia, zawsze z nazwą konta i okna) i **👁 POWINIENEŚ ZOBACZYĆ** (zwykły tekst z oczekiwanym wynikiem, nigdy do wklejania). Przy rozbieżności Paweł zatrzymuje się i wkleja wynik. Polecenia sesji (`/exit` itp.) wpisuje Paweł.

1. **`safe.directory`** (tylko gdy git zgłasza „dubious ownership”; konto claude-agent, okno PowerShell): `git config --global --add safe.directory <ścieżka repo z ukośnikami />`. 👁 `git status` w repo działa bez błędu.
2. **Commit początkowy i push** (konto Belkot, okno z repo): `git add`, `git commit` (opis ASCII), `git push`. 👁 gałąź na GitHubie ma pliki projektu.
3. **Hooki git** (konto Belkot): `git config core.hooksPath .githooks`. 👁 `git config core.hooksPath` wypisuje `.githooks`.
4. **Katalog projektów** (raz na maszynę, konto administratora): `powershell -ExecutionPolicy Bypass -File instaluj\windows.ps1 -InstalujKatalogProjektow`. 👁 `[OK]` przy zakazie na katalogu projektów i Modify na `_repo`.
5. **Blokady** (konto administratora): `powershell -ExecutionPolicy Bypass -File instaluj\windows.ps1 -Repo <ścieżka repo>`. 👁 `[OK]` przy każdym pliku kontrolnym i przypomnienie o `-TestAgenta`.
6. **Test jako agent** (zalogowany jako claude-agent, czerwony znak zachęty `[AGENT@<MASZYNA>]`): `powershell -ExecutionPolicy Bypass -File instaluj\windows.ps1 -TestAgenta`. 👁 `whoami` pokazuje konto agenta, zapisy w plikach kontrolnych kończą się „odmowa”, a podsumowanie ma 0 błędów.
7. **Nowa sesja Claude Code w repo** (konto claude-agent): `/status` (👁 model Sonnet), sprawdzenie recenzenta z METODA sekcja 3 (👁 opis „Niezalezny recenzent kodu…” i `(Tools: Read, Grep, Glob)`), `/kuznia:status`, potem `/kuznia:pakiet PK-00`.
8. **PK-00 projektu** u planisty: wypełnienie `docs/recenzja-projekt.md` i `CLAUDE.md`.

Oznaczaj stwierdzenia: `FACT`, `PROPOSED`, `OPEN QUESTION`, `IDEA`.
