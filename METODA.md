# METODA — jak prowadzę projekty z Claude Code

Wersja: 0.4 (23.11.2026)
Źródło prawdy: publiczne repo `belkot78/kuznia-kodu`, plik `METODA.md`. Kopia w Projektach claude.ai służy czatom.
Nazwy: repo **`kuznia-kodu`**, plugin Claude Code **`kuznia`**, plik zasad **`METODA.md`**.
Etykiety (wszędzie, także w dokumentach projektów): `FACT` (sprawdzone), `PROPOSED` (do potwierdzenia), `OPEN QUESTION` (decyzja do podjęcia), `IDEA` (pomysł na później).

---

## 0. Dla czatu, który to czyta

To jest **ustalona** metoda pracy Pawła. Obowiązuje we wszystkich projektach i na wszystkich komputerach.
- Nie projektuj jej od nowa i nie proponuj innego podziału modeli. Wykonawcą jest Sonnet, recenzentem Opus. To jest już rozstrzygnięte.
- Twoja rola w projekcie: planista. Piszesz zlecenia pakietów (`docs/pakiety/PK-XX-*.md`), pomagasz Pawłowi ocenić plan i raport, wypełniasz części specyficzne dla projektu (sekcja 6).
- Jeśli coś w metodzie nie pasuje do projektu, nie obchodź tego. Zapisz to jako **„Propozycja do METODA”**: co, dlaczego i z którego projektu. Paweł przeniesie to do repo `kuznia-kodu` w kroku retro.
- **Instrukcje dla Pawła piszesz w stałym układzie:**
  - **▶ WKLEJ**: blok kodu do wklejenia (PowerShell albo Claude Code), zawsze z informacją, które konto;
  - **👁 POWINIENEŚ ZOBACZYĆ**: zwykły tekst z oczekiwanym wynikiem, nigdy do wklejania.

  Przy rozbieżności Paweł zatrzymuje się i wkleja wynik. Polecenia `/exit` i inne polecenia sesji wpisuje Paweł, nie wkłada się ich do poleceń dla agenta.

---

## 1. Role

| Rola | Kto | Co robi | Czego nie robi |
|---|---|---|---|
| Właściciel | Paweł | decyzje, „dalej”, `git push`, zmiany plików kontrolnych, blokady, zmiany metody | — |
| Planista | czat Projektu claude.ai | zlecenia pakietów, przegląd planu i raportu, ADR, kontrakty, przegląd kodu uruchamianego przez administratora | nie ma dostępu do repo ani maszyn |
| Wykonawca | Claude Code, **Sonnet** | plan, kod, testy, bramka końcowa, log, raport | push, zmiany plików kontrolnych, decyzje architektoniczne, zmiany metody |
| Recenzent | subagent `kuznia:recenzent`, **Opus**, tylko odczyt | ocena zmian pakietu | nie poprawia, nie uruchamia poleceń |

Gdzie zapisano modele:
- **Sonnet** jest ustawiany w `.claude/settings.json` każdego repo jako `"model": "sonnet"`, więc `/model` nie jest potrzebne.
- **Opus** jest przypięty w nagłówku agenta recenzenta w pluginie jako `model: opus`.

## 2. Cykl pakietu

1. Planista pisze `docs/pakiety/PK-XX-<nazwa>.md` według `docs/pakiety/_szablon-pakietu.md`: stan dziś, cel, zakres, testy, ograniczenia, kryteria, wdrożenie, pytania, log.
2. Paweł wprowadza zlecenie do repo (commit). Nowa sesja Claude Code **w katalogu repo projektu**, potem `/kuznia:status` i `/kuznia:pakiet PK-XX`. Skille wywołuje człowiek, bo model ich nie widzi (`disable-model-invocation`).
3. Wykonawca przedstawia plan. Paweł przegląda go (z czatem) i pisze „dalej”. Przy pakietach z decyzjami po drodze planista może wpisać przystanek, np. „po etapie 1 pokaż wynik i czekaj”.
4. Wykonawca realizuje zakres. Po każdym etapie robi commit lokalny, z opisem **po polsku bez polskich liter (ASCII)**.
5. **Bramka końcowa:**
   1. Testy offline i `tools/przeglad.py` muszą dać PASS.
   2. Recenzent ocenia zmiany `@{upstream}..HEAD`.
   3. Blokery z listy klas (sekcja 3) wykonawca poprawia i woła recenzenta ponownie. **Najwyżej jedna dodatkowa runda.**
   4. Pozostałe uwagi idą do `docs/porzadki.md` (jedna linia na uwagę, sekcja „Z PK-XX”).
6. Wykonawca uzupełnia log pakietu i `docs/stan.md`, potem pisze raport: werdykt, odłożone uwagi, `git diff --stat`, kroki dla Pawła.
7. Paweł czyta raport i robi `git push` (hook pre-push uruchamia kontrole). Jeśli lokalnych commitów jest wiele, a w historii jest coś, czego nie wolno publikować, najpierw łączy je w jeden (`git reset --soft @{upstream}` i commit).

Powrót do planisty jest obowiązkowy, gdy:
- po dodatkowej rundzie nadal są blokery;
- potrzebna jest decyzja architektoniczna lub kontraktowa;
- warunek wstępny nie jest spełniony.

Gałąź robocza: domyślnie `main`, wariant `dev` wybierany przy zakładaniu projektu. Bazę porównań zawsze bierze się z gałęzi śledzonej (`@{upstream}`).

## 3. Recenzja

- **Kiedy:** raz na pakiet, w bramce końcowej. Na żądanie Pawła także w innym momencie.
- **Kto woła:** wykonawca, z poziomu skilla `/kuznia:pakiet`.
- **Wejście:** diff `@{upstream}..HEAD` w pliku `.recenzja/diff.patch` (katalog w `.gitignore`), zlecenie pakietu i `docs/recenzja-projekt.md`. Jeśli zapis diffu do pliku zostanie odrzucony przez uprawnienia, wykonawca wkleja diff w polecenie, a przy dużym diffie robi to w częściach. `allow` nie jest wtedy poszerzane.
- **Wyjście:** werdykt `ZATWIERDZAM` / `ZATWIERDZAM Z UWAGAMI` / `ODRZUCAM`, potem uwagi. Każda uwaga ma wagę, `plik:linia`, problem i konsekwencję.
- **Wagi:**
  - **BLOKUJĄCE**: zasady, kontrakt albo realny błąd;
  - **UWAGA**: ryzyko, decyduje autor;
  - **SUGESTIA**: drobna poprawa.
- **Klasy blokerów poprawianych w pakiecie:** sekret; dostęp do danych poza zakresem projektu; zapis lub akcja na żywym systemie zewnętrznym; złamanie kontraktu lub ADR; klasy dopisane w `docs/recenzja-projekt.md`. Inne blokery wykonawca opisuje w raporcie, a decyzja należy do Pawła.
- **Narzędzia recenzenta:** `Read, Grep, Glob`. Uzasadnienie: niezależność od ocenianego kodu, brak drogi do żywych źródeł i danych. Koszt tej decyzji: czego nie da się sprawdzić bez uruchomienia, sprawdza wykonawca albo Paweł.
- **Zasada recenzenta:** „brak uwag” jest poprawną odpowiedzią. Recenzent nie chwali na zapas i nie wymyśla uwag.
- **Sprawdzenie, czy recenzent jest prawdziwy** (po instalacji i po każdej aktualizacji pluginu), w sesji Claude Code:
  > Nie czytaj zadnych plikow. Przepisz doslownie opis i narzedzia agenta kuznia:recenzent z listy typow agentow narzedzia Agent.

  Dobrze: opis „Niezalezny recenzent kodu…” i `(Tools: Read, Grep, Glob)`. Źle: „Agent from kuznia plugin” albo brak ograniczenia narzędzi, co oznacza, że nagłówek nie został odczytany. Pytanie „opisz agenta” niczego nie dowodzi, bo model może po prostu przeczytać plik.

## 4. Standardowy układ repo projektu

```
CLAUDE.md                          kontekst, bezpieczeństwo, git, styl, konto agenta, sekcja „Metoda”
.gitattributes                     * text=auto eol=lf (wszystkie pliki tekstowe zawsze LF)
.gitignore                         m.in. .recenzja/, docs/prywatne/, settings.local.json, sekrety
.claude/settings.json              model, uprawnienia, plugin kuznia (sekcja 5)
.githooks/pre-commit, pre-push     hooki git (core.hooksPath .githooks, włącza Paweł)
docs/recenzja-projekt.md           część specyficzna dla recenzenta (sekcja 6)
docs/wdrozenie.md                  jak uruchomić aplikację na dowolnej maszynie (sekcja 9)
docs/stan.md                       stan projektu
docs/porzadki.md                   odłożone uwagi
docs/pakiety/_szablon-pakietu.md   wzór zlecenia
docs/pakiety/PK-XX-*.md            zlecenia i logi pakietów
docs/adr/                          decyzje
tools/przeglad.py                  wspólny silnik kontroli (skan sekretów, testy, kontrole)
tools/przeglad_konfig.py           konfiguracja kontroli dla projektu
tools/tests/test_settings.py       pilnuje uprawnień w settings.json
```

Agent recenzenta, skille i hooki Claude Code **nie są kopiowane do repo**. Przychodzą z pluginu `kuznia`.

## 5. Narzędzia: plugin, szablon, instalacja

- **Repo `belkot78/kuznia-kodu` jest publiczne** (konto agenta nie ma poświadczeń GitHub) i zawiera:
  - `METODA.md`;
  - plugin `kuznia`, czyli całe repo: marketplace wskazuje katalog główny, bo skille potrzebują `szablon/` i `maszyny/`;
  - `szablon/`, `szablon-uzytkownika/`, `maszyny/`, `instaluj/`, `CHANGELOG.md`.
- **Co wolno w publicznym repo:**
  - nazwy projektów jako przykłady;
  - etykiety kontraktów `K`/`Z` tylko w `METODA.md` i `docs/pakiety/`.

  Zakazane wszędzie: nazwy brokerów, pliki z tokenami, nazwy folderów produkcyjnych, numery kont, adresy i hosty. Lista nazw zakazanych leży lokalnie w `docs/prywatne/` (poza gitem), a test repo publicznego czyta ją, gdy istnieje.
- **Plugin instaluje się poleceniem, w każdym projekcie osobno** (konto agenta, w katalogu repo):
  - raz na konto: `claude plugin marketplace add belkot78/kuznia-kodu`;
  - w każdym projekcie: `claude plugin install kuznia@kuznia-kodu --scope project`.

  Wpisy `extraKnownMarketplaces` i `enabledPlugins` w `settings.json` tylko włączają plugin; nie instalują go.
- **Instalator zapisuje `.claude/settings.json`**, a przy okazji przestawia kolejność kluczy. Dlatego:
  - instalacja idzie przed założeniem blokad;
  - po instalacji: `git checkout -- .claude/settings.json`.
- **Każda zmiana pluginu oznacza podbicie wersji** w `plugin.json`. Przy niezmienionej wersji cache u agenta się nie odświeża. Awaryjnie: `claude plugin marketplace remove kuznia-kodu`, potem `add` i `install`.
- **Uprawnień** (`allow`/`deny`/`ask`) plugin nie przenosi. Zostają w `settings.json` repo i powstają z szablonu. W szablonie:
  - `git push`, `git add`, `git commit` są w `ask`;
  - wzorce piszemy ze spacją (`git status *`).
- `~/.claude/CLAUDE.md` konta agenta (z `szablon-uzytkownika/`) mówi Claude Code o metodzie także poza repo projektu.

## 6. Część specyficzna projektu: `docs/recenzja-projekt.md`

To jedyne miejsce, w którym recenzent dostaje wiedzę o konkretnym projekcie:
- poziom dostępu projektu (sekcja 7);
- kontrakty i zasady architektury;
- pliki i katalogi, których recenzent nigdy nie czyta;
- dodatkowe klasy blokerów (np. dla PII: „żadne pole z bazy PII nie trafia do bazy głównej, logów ani komunikatów”);
- zasady techniczne projektu, które sprawdzał dotychczasowy recenzent (przy migracji nic nie może zginąć).

Wypełnia ją planista razem z Pawłem w PK-00 projektu.

## 7. Poziomy dostępu projektu

| Poziom | Co agent może | Przykłady | Środowisko |
|---|---|---|---|
| **P0** | tylko kod i dane syntetyczne | ekosystem, PathChaser, Elektroklub | konto `claude-agent` |
| **P1** | odczyt żywych systemów | odczyt API bez zapisu | konto `claude-agent` + wąski token tylko do odczytu |
| **P2** | sterowanie żywym systemem | Home Assistant | osobne środowisko (np. VM Linux) + wąski token; decyzja przy projekcie |

Poziom zapisuje się w `docs/recenzja-projekt.md` i w `CLAUDE.md`. Zmiana poziomu wymaga decyzji Pawła.

## 8. Konta, izolacja, blokady

- **Claude Code zawsze pracuje na koncie bez administratora** (`claude-agent`) na każdej maszynie. Konto administratora (Belkot, belko) służy tylko człowiekowi.
- **Granicą jest system operacyjny, nie `settings.json`.** Na Windowsie: blokady NTFS, właściciel plików kontrolnych to Paweł. Na Linuksie: osobny użytkownik i uprawnienia plików. Reguły `settings.json` to druga warstwa (siatka).
- **Katalog projektów** (`C:\Projects`): agent ma dostęp tylko do `_repo`. Wzorzec z Legiona (23.11) zamiast blokady każdego folderu osobno:
  - na `C:\Projects` zakaz `FullControl` dla agenta, dziedziczony tylko w dół (`(OI)(CI)(IO)`), plus zakaz zakładania czegokolwiek bezpośrednio w `C:\Projects`;
  - na `_repo` jawne `Modify`, które wygrywa z odziedziczonym zakazem.

  Każdy nowy folder w `C:\Projects` jest od razu zamknięty. W `icacls` zakaz pełnego dostępu wyświetla się jako `(N)` (bez dopisku `(DENY)`); `(DENY)` widać tylko przy zakazie części praw.
- **Własne dane tylko w `C:\Projects` albo w profilu Pawła.** Foldery zakładane bezpośrednio na `C:\` są domyślnie otwarte dla każdego konta, także agenta. Profil `C:\Users\<Paweł>` jest domyślnie zamknięty (nie do „Dokumentów”, jeśli synchronizuje je OneDrive). To, co musi zostać na `C:\`, dostaje zakaz dla agenta. Test jako agent obejmuje **wszystkie** foldery na `C:\`.
- **Konektory claude.ai (Gmail, Dysk, Notion, ClickUp…)** są blokowane na poziomie konta agenta: `deniedMcpServers` w `~/.claude/settings.json`. Działa to także poza repo; repo ma tę samą blokadę w swoim `settings.json`.
- **Pliki kontrolne repo** (blokada zapisu dla agenta, właściciel Paweł):
  - `.claude/`, `.githooks/`, `.git/config`, `.git/hooks/`;
  - `tools/przeglad.py`, `tools/przeglad_konfig.py`, `tools/tests/test_settings.py`.

  Zmiany w nich agent przygotowuje jako `.patch`, a nakłada je Paweł. Blokada blokuje tylko agenta, więc Paweł nie musi jej zdejmować do `git apply`.
- **Blokada znika, gdy git zapisze plik od nowa** (łatka, `pull`, `checkout`). Po każdej takiej zmianie Paweł zakłada blokady ponownie i robi **test zapisu jako agent**: otwarcie każdego pliku kontrolnego do zapisu i utworzenie pliku w `.claude` mają dać „odmowa”.
- **Profil agenta** (`~/.claude/`, katalog pluginu, `~/.claude/CLAUDE.md`): agent ma tam pełne prawa, więc blokada pliku nie chroni. Zasada: **wykrywanie zamiast zapobiegania**. `-Sprawdz` porównuje te pliki z wersją z repo. Hooki pluginu działają z uprawnieniami agenta, więc ich podmiana nie daje mu nowych praw. Prawdziwe zabezpieczenia to hooki git uruchamiane przez Pawła i blokady w repo.
- **„dubious ownership”**: repo zakładane przez konto administratora należą do grupy Administrators. Konto agenta dostaje `git config --global --add safe.directory <repo>` (robi to Paweł albo skrypt, nie agent).
- **Kod napisany przez agenta, który uruchamia administrator, czyta najpierw ktoś inny niż agent**: Paweł albo czat. Dotyczy skryptów instalacyjnych, łatek na pliki kontrolne i zmian uprawnień.
- Każda maszyna ma profil w `maszyny/<nazwa>.md`: system, konta, katalog repo, interpreter (`~/.venvs/<nazwa-repo>`), rodzaj izolacji, dostępne poziomy P0–P2.

## 9. Przenoszenie aplikacji między maszynami

- Każde repo ma `docs/wdrozenie.md` w stałym formacie:
  - wymagania (Python/Node, wersje);
  - pliki lokalne spoza repo (`dane/`, plik lokalnej konfiguracji; tylko nazwy i opis pól, bez wartości);
  - porty;
  - usługi i autostart;
  - kroki instalacji;
  - kontrola, czy działa.
- `/kuznia:przenies` na maszynie docelowej czyta `docs/wdrozenie.md` i profil maszyny, przygotowuje kroki, a od Pawła potrzebuje tylko danych i sekretów.

## 10. Nowy projekt: kolejność

1. **Paweł, GitHub:** nowe repo z README (żeby istniała gałąź), prywatne albo publiczne według treści.
2. **Paweł, Belkot:** klon do `C:\Projects\_repo\<nazwa>`, sprawdzenie, że `claude-agent` dziedziczy `(M)`.
3. **Paweł:** `safe.directory` dla konta agenta.
4. **Agent, w katalogu repo:** `/kuznia:nowy-projekt`, potem dokumenty od planisty (`docs/recenzja-projekt.md`, PK-00).
5. **Agent:** `claude plugin install kuznia@kuznia-kodu --scope project`, potem `git checkout -- .claude/settings.json`.
6. **Paweł:** commit, push, `git config core.hooksPath .githooks`.
7. **Paweł:** blokady (`instaluj/windows.ps1 -Repo <repo>`), test zapisu jako agent, test dostępu do `C:\Projects` jako agent.
8. **Nowa sesja:**
   - `/status`: model Sonnet;
   - sprawdzenie recenzenta (sekcja 3);
   - `/kuznia:status`;
   - potem `/kuznia:pakiet PK-00`.

## 11. Doskonalenie metody

- Źródłem zmian są:
  - „Propozycje do METODA” z czatów i pakietów;
  - wnioski z logów pakietów;
  - uwagi powtarzające się w `porzadki.md` różnych projektów.
- Raz na kilka pakietów albo na koniec projektu Paweł uruchamia `/kuznia:retro`. Wykonawca zbiera wnioski i proponuje zmianę w `kuznia-kodu`, czyli diff i wpis do `CHANGELOG.md`.
- Treść `METODA.md` zmienia Paweł (z czatem). Wykonawca dopisuje tylko propozycje. Agent nie zmienia zasad, według których sam jest oceniany.
- Po zmianie metody: nowa wersja pluginu, aktualizacja kopii `METODA.md` w Projektach claude.ai.

## 12. Lekcje, z których wynikają zasady (`FACT`)

- **Max 1 dodatkowa runda recenzji:** w PK-00 ekosystemu były 4 rundy `ODRZUCAM` z rzędu, bo każda poprawka listy uprawnień otwierała nową furtkę.
- **Uwagi nieblokujące poza pakietem:** dzięki temu zakres pakietu się nie rozrasta.
- **`ask` nie działa przy `acceptEdits`:** zapis pliku kontrolnego zatrzymał dopiero Windows.
- **Wzorce `*` w deny dopasowują cały tekst polecenia.** Deny pisać wąsko.
- **Deny dotyczy Basha, nie PowerShella:** narzędzie PowerShell agenta jest wyłączone (`deny: PowerShell`).
- **Gołe `Glob`/`Grep` w allow przeszukują poza repo:** nie dawać ich w allow.
- **`icacls /deny` z prawami w nawiasie potrafi zablokować odczyt (SYNCHRONIZE):** blokady zakładać metodą .NET (`GetAccessControl('Access')` / `SetAccessControl()`), z jawną listą praw zapisu.
- **Właściciel pliku może zdjąć blokadę:** właścicielem plików kontrolnych jest Paweł.
- **Git zapisuje plik od nowa i blokada znika:** po każdej łatce i `pull` blokady ponownie i test zapisu.
- **`settings.local.json` potrafi trzymać stare szerokie allow:** jest pusty i pilnowany testem.
- **Python/Node tylko w instalacji dla wszystkich użytkowników.**
- **Kopiowanie konfiguracji między repo rozjeżdża się w ciągu dni** (17 rozbieżności między dwoma pierwszymi projektami po trzech dniach). Stąd plugin z jednego źródła.
- **Czat bez tej metody projektuje wszystko od nowa.** Stąd ten plik w każdym Projekcie i wzmianka w instrukcjach konta claude.ai.
- **CRLF psuje plugin:** git na koncie agenta (`autocrlf=true`) pobrał pliki pluginu z windowsowymi końcami linii i Claude Code nie odczytał nagłówka recenzenta. Ten działał wtedy bez Opusa i ze wszystkimi narzędziami. Stąd `.gitattributes` z `eol=lf` i sprawdzenie recenzenta z sekcji 3.
- **Historia gita w publicznym repo:** poprawka usuwa treść z najnowszej wersji, ale nie z historii. Przed pierwszym pushem łączymy commity, jeśli wcześniejszy zawierał coś niedozwolonego.
- **Atrapy sekretów w testach** składamy z fragmentów, inaczej skan sekretów je zgłasza.
- **`(N)` w `icacls` to pełny zakaz, nie puste zezwolenie** (pomyłka czatu na miniPC, sprostowana na Legionie). Rozstrzyga zawsze test jako agent, nie odczyt `icacls`.
- **Test jako agent musi naprawdę być na koncie agenta:** czerwony znak zachęty `[AGENT@<MASZYNA>]` w profilu PowerShella agenta i `whoami` na początku każdego testu. Test w oknie administratora daje fałszywe „DOSTEP”.
- **Instalator Claude Code na koncie agenta** (`irm https://claude.ai/install.ps1 | iex`, Legion 23.11) nie dopisał `~\.local\bin` do PATH; trzeba to zrobić ręcznie.
- **Recenzja działa:** w PK-M0 pierwsza runda złapała nazwę brokera w publicznym pliku i dziurę w skanie sekretów (pliki z polskimi znakami w nazwie były pomijane).

## 13. Changelog

- 0.4 (23.11.2026): przeniesione propozycje z PK-M0 i lekcje z pierwszej instalacji pluginu oraz migracji PathChasera:
  - etykiety FACT/PROPOSED/OPEN QUESTION/IDEA;
  - skille z przedrostkiem `/kuznia:`;
  - `@{upstream}`, ASCII w commitach, gałąź `main`/`dev`;
  - instalacja pluginu poleceniem, w każdym projekcie, przed blokadami;
  - podbijanie wersji pluginu;
  - `.gitattributes` z LF;
  - sprawdzenie recenzenta;
  - blokady po każdej łatce i test zapisu;
  - profil agenta: wykrywanie zamiast zapobiegania;
  - `safe.directory`;
  - przegląd kodu uruchamianego przez administratora;
  - kolejność nowego projektu (sekcja 10);
  - konwencja ▶ WKLEJ / 👁 POWINIENEŚ ZOBACZYĆ.
- 0.3 (23.11.2026): nazwa repo `kuznia-kodu`, plugin `kuznia`; `szablon-uzytkownika/CLAUDE.md`.
- 0.2 (23.11.2026): repo publiczne; odłożone uwagi wszędzie w `docs/porzadki.md`.
- 0.1 (23.11.2026): pierwszy szkic na podstawie ekosystemu (PK-00…PK-11) i PathChasera (PK-00…PK-03).
