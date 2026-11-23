# Porządki: odłożone uwagi

Uwagi nieblokujące z recenzji pakietów, jedna linia na uwagę, w sekcji „Z PK-XX”. Format: `[WAGA] plik:linia: problem i konsekwencja (status)`. Numer w nawiasie to numer uwagi w raporcie recenzenta PK-M0.

## Z PK-M0 (23.11.2026)

- [DECYZJA PAWŁA] instaluj/windows.ps1:231,238 (#2): blokady na plikach w profilu agenta i w pluginie można obejść, bo agent ma FullControl na katalogu nadrzędnym (prawo „usuń podfoldery i pliki” pozwala usunąć lub przemianować zablokowany obiekt); `-Sprawdz` pokaże mimo to „OK”. Potrzebne: kontrola w `-Sprawdz` praw agenta na katalogach nadrzędnych (`tools\`, `tools\tests\`, `.git\`, korzeń repo, `~\.claude`, `plugins\cache`) i decyzja, jak chronić profil bez blokowania zapisów samego Claude Code (otwarta).
- [UWAGA] szablon/.claude/settings.json:8 (#4): `Bash(git diff *)` przepuszcza `git diff --no-index <plik> NUL` i omija deny odczytu `.env`; propozycja deny `Bash(git diff *--no-index*)` i asercja w `test_settings.py` (otwarta).
- [UWAGA] szablon/tools/tests/test_settings.py:66 (#5): `SCIEZKI_CHRONIONE` nie obejmuje `tools/tests/test_settings.py`; wzorce deny zapisu łatwo ominąć wariantem ścieżki (`./.claude//settings.json`, `cd .claude && cp`); realną barierą jest warstwa systemowa (otwarta).
- [UWAGA] szablon/tools/przeglad.py (#6): filtr `--diff-filter=ACM` pomija pliki przemianowane (R) i zmiany typu (T) w indeksie, więc plik przemianowany z dopisanym sekretem omija pre-commit (pre-push złapie go później); dodać `R` i `T` (otwarta).
- [UWAGA] instaluj/windows.ps1:129-132 (#7): `Set-Acl` z obiektem z `Get-Acl` w PowerShell 5.1 próbuje zapisać też właściciela i po `icacls /setowner` może zgłosić błąd, co przerwie skrypt w połowie; bezpieczniej `GetAccessControl('Access')` i `SetAccessControl()`; składni nie sprawdzono parserem (otwarta, sprawdzić przy pierwszym `-Sprawdz`).
- [UWAGA] instaluj/windows.ps1:188,169 (#8): (a) „folder bez blokady” uznaje tylko jawny Deny z odczytem, a odmowa może wynikać z braku Allow; (b) wynik testu jako agent czytany bez kodowania, więc polskie znaki w nazwach folderów dadzą fałszywy `[BLAD]`; (c) brak opisu, że blokada katalogu pluginu uniemożliwia agentowi aktualizację pluginu (otwarta).
- [UWAGA] hooks/hooks.json:9,20 (#9): hooki wywołują `python`, a zlecenie mówi o przenośnym wyborze `python3`/`python`; na Linuksie bez `python` kontrola cicho nie działa (opisane w README; otwarta, wymaga małego launchera).
- [UWAGA] szablon/tools/tests/test_hooki.py:83 (#10): test braku interpretera buduje PATH z katalogu `sh`; na Linuksie jest tam `python3`, więc test zależy od środowiska (otwarta).
- [UWAGA] docs/po-pk-m0.patch (#11): łącznik zostawia na dysku kopię `.claude/agents/recenzent.md` (po usunięciu wpisu z `.gitignore` staje się plikiem nieśledzonym o treści specyficznej dla projektu), a w instrukcji dla Pawła brak kroku „najpierw usuń kopię”; marketplace jest z GitHuba, nie z lokalnej kopii (zlecenie: „z tego repo”) (krok dopisany do raportu; otwarta).
- [DECYZJA PAWŁA] docs/prywatne/inwentaryzacja.md (#12): zlecenie wymaga `docs/inwentaryzacja.md`, a z decyzji Pawła plik jest poza gitem (`docs/prywatne/`); kryterium „inwentaryzacja kompletna” nie jest weryfikowalne przez recenzenta (potwierdzone w poleceniu Pawła, odnotowane w raporcie).
- [SUGESTIA] szablon/.claude/settings.json:26-35 (#13): wyliczone warianty `.env.*` nie obejmują np. `.env.secrets` i `.env.ci`; łącznik zawęża w tym repo wcześniejsze `Read(**/.env*)` i usuwa deny na plik lokalnej konfiguracji; zakaz pomijania hooka nie łapie `git commit -vn` (łagodzi `ask` na commit) (otwarta).
- [SUGESTIA] testy/test_instaluj.py (#14): zliczanie nawiasów to słaba namiastka parsera; zamiast tego krok Pawła `Parser::ParseFile` przed pierwszym uruchomieniem (otwarta).
- [UWAGA] testy/test_publiczne.py:39-42 (runda 2, #1): `pliki_repo()` woła `git ls-files -co` bez `-z` i dzieli po liniach, więc plik z polskimi znakami w nazwie wypada po cichu z kontroli repo publicznego (ten sam błąd, który w `przeglad.py` poprawiono); poprawka: `-z`, `split("\0")` i UTF-8 (otwarta, do następnego pakietu).
- [SUGESTIA] szablon/tools/tests/test_przeglad.py (runda 2, #2): test z polską nazwą nie obejmuje `nowe_pliki` (poprawka jest, nic jej nie pilnuje) (otwarta).
- [SUGESTIA] szablon/tools/tests/test_przeglad.py:173-175 (runda 2, #3): helper `git` nie ustawia `-c core.quotePath=true`; przy globalnym `quotePath=false` test z polską nazwą przestaje łapać regresję (otwarta).

### Statusy po PK-M0.1

Zlecenie PK-M0.1, etap 4. Numeracja jak wyżej (numer w raporcie recenzenta PK-M0, „r2” = runda 2).

- #2 (DECYZJA PAWŁA): ZAMKNIĘTA. Rozstrzyga METODA 0.4, sekcja 8: wykrywanie zamiast zapobiegania. Katalog pluginu i `.claude\CLAUDE.md` agenta nie są blokowane, `-Sprawdz` i `-TestAgenta` porównują skróty z repo (`windows.ps1`, etap 2). Nie blokujemy też `.claude\CLAUDE.md`: blokada pliku nie chroni, gdy agent ma pełne prawa do katalogu nadrzędnego.
- #4: POPRAWIONA. `Bash(git diff *--no-index*)` w deny szablonu, asercja w `test_settings.py`, łatka `docs/pakiety/PK-M0.1-claude.patch` dla `.claude/` tego repo (czeka na Pawła).
- #5: ZAMKNIĘTA z uzasadnieniem. Wzorce deny zapisu zawsze da się ominąć wariantem ścieżki; realną barierą jest blokada systemowa (METODA sekcja 8), a `test_settings.py` jest plikiem kontrolnym z blokadą NTFS. Dopisanie kolejnej ścieżki do wzorców nie zmienia tej oceny.
- #6: POPRAWIONA. `--diff-filter=ACMRT` w `pliki_z_indeksu` i `nowe_pliki` (`przeglad.py`), testy: przemianowany plik z sekretem w indeksie, filtry R i T.
- #7: POPRAWIONA. Blokady przez `GetAccessControl('Access')` i `SetAccessControl()`, bez `Set-Acl` i `Get-Acl` (test statyczny). Składni nadal nie sprawdzono parserem (patrz #14).
- #8: (a) ZAMKNIĘTA: `-Sprawdz` podaje tylko wskazówkę o braku Deny z odczytem, a rozstrzyga `-TestAgenta` (odmowa z braku Allow też jest „odmowa”); (b) POPRAWIONA: test jako agent działa w tym samym procesie (bez odczytu pliku z wynikiem), a wynik programów zewnętrznych czytany jest z `OutputEncoding` UTF-8; (c) ZAMKNIĘTA: katalog pluginu nie jest już blokowany.
- #9: POPRAWIONA. `hooks/uruchom.sh` wybiera `python3`, `python` albo `py`; `hooks.json` wywołuje `sh "${CLAUDE_PLUGIN_ROOT}/hooks/uruchom.sh"`. Ograniczenie (FACT z dokumentacji): na Windows bez Git Bash polecenie idzie przez PowerShell i `sh` nie istnieje; brak polecenia (kod 127) jest błędem nieblokującym, więc kontrola nie działa po cichu. Na maszynach metody Git Bash jest.
- #10: POPRAWIONA. `path_bez_pythona` w `test_hooki.py` buduje PATH bez Pythona także na Linuksie (dowiązania do `sh`, `git`, `basename`, `dirname`). Gałąź Linuksa nie była tu uruchamiana (OPEN QUESTION: sprawdzić na maszynie z Linuksem).
- #11: ZAMKNIĘTA. `docs/po-pk-m0.patch` usunięty w etapie 5 (łącznik nałożony).
- #12 (DECYZJA PAWŁA): ZAMKNIĘTA. Rozstrzyga METODA 0.4: inwentaryzacja jest poza gitem (`docs/prywatne/`), nie jest kryterium recenzji.
- #13: CZĘŚCIOWO. POPRAWIONE: warianty `.env.secrets*` i `.env.ci*` oraz `lokalne.yaml` i `settings.local.json` w deny odczytu. ZAMKNIĘTE z uzasadnieniem: `git commit -vn` (nie łapie go wzorzec deny): commit jest w `ask`, a pomięty hook pre-commit nadrabia pre-push uruchamiany przez Pawła.
- #14: ZAMKNIĘTA. Zliczanie nawiasów zostaje jako siatka; krok Pawła w raporcie: `[System.Management.Automation.Language.Parser]::ParseFile` na `windows.ps1` przed pierwszym uruchomieniem.
- r2 #1: POPRAWIONA. `git ls-files -z` i dekodowanie UTF-8 w `test_publiczne.py`, test regresji z polską nazwą pliku.
- r2 #2: POPRAWIONA. Test `nowe_pliki` z polskimi nazwami (zmieniony i nowy plik).
- r2 #3: POPRAWIONA. Helper `git` w `test_przeglad.py` ustawia `-c core.quotePath=true`.
