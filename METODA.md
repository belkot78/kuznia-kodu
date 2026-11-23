# METODA — jak prowadzę projekty z Claude Code

Wersja: 0.3 (23.11.2026, szkic przed PK-M0)
Źródło prawdy: publiczne repo `belkot78/kuznia-kodu`, plik `METODA.md` (po PK-M0). Kopia w Projekcie claude.ai służy czatom.
Oznaczenia: `FACT` (sprawdzone w praktyce), `PROPOSED` (do potwierdzenia przy wdrożeniu), `OTWARTE` (decyzja Pawła).
Nazwy: repo **`kuznia-kodu`**, plugin Claude Code **`kuznia`**, plik zasad **`METODA.md`**.

---

## 0. Dla czatu, który to czyta

To jest **ustalona** metoda pracy Pawła. Obowiązuje we wszystkich projektach i na wszystkich komputerach.
- Nie projektuj jej od nowa i nie proponuj innego podziału modeli. Wykonawcą jest Sonnet, recenzentem Opus. To jest już rozstrzygnięte.
- Twoja rola w projekcie: planista. Piszesz zlecenia pakietów (`docs/pakiety/PK-XX-*.md`), pomagasz Pawłowi ocenić plan i raport, wypełniasz części specyficzne dla projektu (sekcja 6).
- Jeśli coś w metodzie nie pasuje do projektu, nie obchodź tego. Zapisz to jako **„Propozycja do METODA”**: co, dlaczego i z którego projektu. Paweł przeniesie to do repo `kuznia-kodu` w kroku retro.

---

## 1. Role

| Rola | Kto | Co robi | Czego nie robi |
|---|---|---|---|
| Właściciel | Paweł | decyzje, „dalej”, `git push`, zmiany plików kontrolnych, zmiany metody | — |
| Planista | czat Projektu claude.ai | zlecenia pakietów, przegląd planu i raportu, ADR, kontrakty | nie ma dostępu do repo ani maszyn |
| Wykonawca | Claude Code, **Sonnet** | plan, kod, testy, bramka końcowa, log, raport | push, zmiany plików kontrolnych, decyzje architektoniczne |
| Recenzent | subagent Claude Code, **Opus**, tylko odczyt | ocena zmian pakietu | nie poprawia, nie uruchamia poleceń |

Gdzie zapisano modele:
- **Sonnet** jest ustawiany w `.claude/settings.json` każdego repo jako `"model": "sonnet"`. Ręczne `/model sonnet` przestaje być potrzebne.
- **Opus** jest przypięty w nagłówku agenta recenzenta jako `model: opus`.

## 2. Cykl pakietu

1. Planista pisze `docs/pakiety/PK-XX-<nazwa>.md` w stałym formacie: stan dziś, cel, zakres, testy, ograniczenia, kryteria, wdrożenie, pytania, log.
2. Paweł wprowadza zlecenie do repo. Otwiera nową sesję Claude Code i wpisuje `/status`, a potem `/pakiet PK-XX`.
3. Wykonawca przedstawia plan. Paweł go przegląda (z czatem) i pisze „dalej”.
4. Wykonawca realizuje cały zakres i po każdym etapie robi commit lokalny.
5. **Bramka końcowa:**
   1. Testy offline i `tools/przeglad.py` muszą dać PASS.
   2. Recenzent ocenia zmiany `origin/main..HEAD`.
   3. Blokery z listy klas (sekcja 3) wykonawca poprawia i woła recenzenta ponownie. **Najwyżej jedna dodatkowa runda.**
   4. Pozostałe uwagi idą do `docs/porzadki.md` (jedna linia na uwagę, sekcja „Z PK-XX”). Ta sama nazwa pliku obowiązuje we wszystkich projektach.
6. Wykonawca uzupełnia log w pakiecie i `docs/stan.md`, potem pisze raport: werdykt, odłożone uwagi, `git diff --stat`, komenda push.
7. Paweł czyta raport i robi `git push` (hook pre-push uruchamia kontrole).

Powrót do planisty jest obowiązkowy, gdy:
- po dodatkowej rundzie nadal są blokery;
- potrzebna jest decyzja architektoniczna lub kontraktowa;
- warunek wstępny pakietu nie jest spełniony.

## 3. Recenzja

- **Kiedy:** raz na pakiet, w bramce końcowej. Na żądanie Pawła także w innym momencie.
- **Kto woła:** wykonawca, z poziomu skilla `/pakiet`.
- **Wejście:** diff `origin/main..HEAD`, zlecenie pakietu, `docs/recenzja-projekt.md`.
  - `PROPOSED`: diff trafia do pliku `.recenzja/diff.patch` (w `.gitignore`), a recenzent czyta go narzędziem Read. Wklejanie diffu w polecenie grozi tym, że przy dużym pakiecie recenzent dostanie tylko część zmian.
- **Wyjście:** werdykt `ZATWIERDZAM` / `ZATWIERDZAM Z UWAGAMI` / `ODRZUCAM`, potem uwagi. Każda uwaga ma wagę, `plik:linia`, problem i konsekwencję.
- **Wagi:**
  - **BLOKUJĄCE**: zasady, kontrakt albo realny błąd;
  - **UWAGA**: ryzyko, decyduje autor;
  - **SUGESTIA**: drobna poprawa.
- **Klasy blokerów poprawianych w pakiecie:**
  - sekret;
  - dostęp do danych poza zakresem projektu;
  - zapis lub akcja na żywym systemie zewnętrznym;
  - złamanie kontraktu lub ADR;
  - klasy dopisane w `docs/recenzja-projekt.md`.
  Inne blokery wykonawca opisuje w raporcie, a decyzję podejmuje Paweł.
- **Narzędzia recenzenta:** `Read, Grep, Glob`. Uzasadnienie: niezależność od ocenianego kodu, brak drogi do żywych źródeł i danych. Koszt tej decyzji: czego nie da się sprawdzić bez uruchomienia, sprawdza wykonawca albo Paweł.
- **Zasada recenzenta:** „brak uwag” jest poprawną odpowiedzią. Recenzent nie chwali na zapas i nie wymyśla uwag.

## 4. Standardowy układ repo projektu

```
CLAUDE.md                     kontekst, bezpieczeństwo, git, styl, konto agenta
.claude/settings.json         model, uprawnienia, plugin kuznia (sekcja 5)
docs/recenzja-projekt.md      część specyficzna dla recenzenta (sekcja 6)
docs/wdrozenie.md             jak uruchomić aplikację na dowolnej maszynie (sekcja 9)
docs/stan.md                  stan projektu
docs/porzadki.md              odłożone uwagi (nazwa wspólna dla wszystkich projektów)
docs/pakiety/PK-XX-*.md       zlecenia i logi pakietów
docs/adr/                     decyzje
tools/przeglad.py             kontrole przed pushem
tools/tests/test_settings.py  pilnuje uprawnień w settings.json
.githooks/ lub hooki git      pre-commit (sekrety), pre-push (przeglad.py)
```

Agent recenzenta, skille (`/pakiet`, `/status`, `/nowy-projekt`, `/przenies`, `/retro`) i hooki Claude Code **nie są kopiowane do repo**. Przychodzą z pluginu `kuznia`.

## 5. Narzędzia: plugin i szablon

- **Publiczne** repo `belkot78/kuznia-kodu` zawiera `METODA.md`, plugin `kuznia` (marketplace), `szablon/`, `szablon-uzytkownika/`, `maszyny/`, `instaluj/` i `CHANGELOG.md`. Jest publiczne, bo konto agenta nie ma poświadczeń GitHub, a metoda nie zawiera sekretów, adresów ani danych. Wszystko, co specyficzne i wrażliwe, zostaje w repo projektów.
- `.claude/settings.json` każdego projektu wskazuje plugin przez `extraKnownMarketplaces` i `enabledPlugins`. Dzięki temu otwarcie repo na nowej maszynie (w zaufanym folderze) samo instaluje metodę.
- `~/.claude/CLAUDE.md` konta agenta (z `szablon-uzytkownika/`) mówi Claude Code o metodzie także poza repo projektu, np. w pustym folderze przed `/nowy-projekt`.
- `FACT`: uprawnień (`allow`/`deny`/`ask`) plugin nie przenosi. Zostają w `settings.json` repo i powstają z szablonu.

## 6. Część specyficzna projektu: `docs/recenzja-projekt.md`

To jedyne miejsce, w którym recenzent dostaje wiedzę o konkretnym projekcie:
- kontrakty i zasady architektury (np. K1–K7, Z1–Z9);
- pliki i katalogi, których recenzent nigdy nie czyta;
- dodatkowe klasy blokerów (np. dla PII: „żadne pole z bazy PII nie trafia do bazy głównej, logów ani komunikatów”);
- poziom dostępu projektu (sekcja 7).

Wypełnia ją planista razem z Pawłem w PK-00 projektu.

## 7. Poziomy dostępu projektu

| Poziom | Co agent może | Przykłady | Środowisko |
|---|---|---|---|
| **P0** | tylko kod i dane syntetyczne | ekosystem, PathChaser, Elektroklub | konto `claude-agent` |
| **P1** | odczyt żywych systemów | odczyt API bez zapisu | konto `claude-agent` + wąski token tylko do odczytu |
| **P2** | sterowanie żywym systemem | Home Assistant | osobne środowisko (np. VM Linux) + wąski token; decyzja przy projekcie |

Poziom zapisuje się w `docs/recenzja-projekt.md` i w `CLAUDE.md`. Zmiana poziomu wymaga decyzji Pawła.

## 8. Konta i izolacja

- **Claude Code zawsze pracuje na koncie bez administratora** (`claude-agent`) na każdej maszynie. Konto administratora (Belkot, belko) służy tylko człowiekowi.
- **Granicą jest system operacyjny, nie `settings.json`.** Na Windowsie: blokady NTFS, właściciel plików kontrolnych to Paweł. Na Linuksie: osobny użytkownik i uprawnienia plików. Reguły `settings.json` to druga warstwa (siatka).
- **Pliki kontrolne** (`.claude/`, hooki git, `.git/config`, `tools/przeglad.py`, skan sekretów, `test_settings.py`, katalog pluginu i `~/.claude/CLAUDE.md` w profilu agenta) mają blokadę zapisu dla agenta. Zmiany przygotowuje agent jako `.patch`, a nakłada je Paweł.
- Każda maszyna ma profil w `maszyny/<nazwa>.md`: system, konta, katalog repo, interpreter, rodzaj izolacji, dostępne poziomy P0–P2.

## 9. Przenoszenie aplikacji między maszynami

- Każde repo ma `docs/wdrozenie.md` w stałym formacie:
  - wymagania (Python/Node, wersje);
  - pliki lokalne spoza repo (`dane/`, `lokalne.yaml`; tylko nazwy i opis pól, bez wartości);
  - porty;
  - usługi i autostart;
  - kroki instalacji;
  - kontrola, czy działa.
- `/przenies` na maszynie docelowej czyta `docs/wdrozenie.md` i profil maszyny, przygotowuje kroki, a od Pawła potrzebuje tylko danych i sekretów.

## 10. Doskonalenie metody

- Źródłem zmian są:
  - „Propozycje do METODA” z czatów;
  - wnioski z logów pakietów;
  - uwagi powtarzające się w `porzadki.md` różnych projektów.
- Raz na kilka pakietów albo na koniec projektu Paweł uruchamia `/retro`. Wykonawca zbiera wnioski i proponuje zmianę w repo `kuznia-kodu`, czyli diff i wpis do `CHANGELOG.md`.
- Zmiany w `kuznia-kodu` zatwierdza i wypycha tylko Paweł. Agent nie zmienia zasad, według których sam jest oceniany.
- Po zmianie metody: nowa wersja pluginu, aktualizacja kopii `METODA.md` w Projektach claude.ai.

## 11. Lekcje, z których wynikają zasady (`FACT`)

- **Max 1 dodatkowa runda recenzji:** w PK-00 ekosystemu były 4 rundy `ODRZUCAM` z rzędu, bo każda poprawka listy uprawnień otwierała nową furtkę.
- **Uwagi nieblokujące poza pakietem:** dzięki temu zakres pakietu się nie rozrasta.
- **`ask` nie działa przy `acceptEdits`:** zapis pliku kontrolnego zatrzymał dopiero Windows. Stąd zasada, że granicą jest system.
- **Wzorce `*` w deny dopasowują cały tekst polecenia:** odrzucały uczciwe opisy commitów z nazwami flag. Deny pisać wąsko.
- **Deny dotyczy Basha, nie PowerShella:** narzędzie PowerShell agenta jest wyłączone.
- **Gołe `Glob`/`Grep` w allow przeszukują poza repo:** nie dawać ich w allow.
- **`icacls /deny` z prawami w nawiasie potrafi zablokować odczyt (SYNCHRONIZE):** blokady zakładać skryptem .NET.
- **Właściciel pliku może zdjąć blokadę:** najpierw zmiana właściciela na Pawła.
- **Git zapisuje plik od nowa i blokada znika:** po `pull` zmieniającym plik kontrolny założyć ją ponownie.
- **`settings.local.json` potrafi trzymać stare szerokie allow:** kontrolować go w `test_settings.py`.
- **Python/Node tylko w instalacji dla wszystkich użytkowników:** inaczej konto agenta ich nie widzi.
- **Kopiowanie konfiguracji między repo rozjeżdża się w ciągu dni** (ekosystem vs PathChaser, w tym różne pliki odłożonych uwag). Stąd plugin z jednego źródła i wspólne nazwy plików.
- **Czat bez tej metody projektuje wszystko od nowa** (Elektroklub). Stąd ten plik w każdym Projekcie i wzmianka w instrukcjach konta claude.ai.

## 12. Changelog

- 0.3 (23.11.2026): nazwa repo `kuznia-kodu` (utworzone, publiczne), plugin `kuznia`; `szablon-uzytkownika/CLAUDE.md` dla konta agenta.
- 0.2 (23.11.2026): decyzje Pawła: repo publiczne; odłożone uwagi wszędzie w `docs/porzadki.md`.
- 0.1 (23.11.2026): pierwszy szkic na podstawie ekosystemu (PK-00…PK-11) i PathChasera (PK-00…PK-03).
