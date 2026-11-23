# Metoda pracy (konto agenta)

Na tym koncie obowiązuje metoda z repo `kuznia-kodu` (plugin `kuznia`, plik `METODA.md`), we wszystkich projektach.

- Wykonawcą jesteś Ty (model Sonnet). Recenzentem jest agent `recenzent` (Opus, tylko odczyt) z pluginu `kuznia`. Nie zmieniasz tego podziału.
- Pakiety uruchamiasz skillem `/kuznia:pakiet PK-XX`, stan sprawdzasz `/kuznia:status`. Pozostałe skille: `/kuznia:nowy-projekt`, `/kuznia:przenies`, `/kuznia:retro`. Skille zawsze z przedrostkiem `/kuznia:`; wywołuje je człowiek.
- Etykiety stwierdzeń: `FACT`, `PROPOSED`, `OPEN QUESTION`, `IDEA`. Opisy commitów po polsku, tylko ASCII (bez polskich liter).
- Kroki dla Pawła podawaj w układzie **▶ WKLEJ** (blok do wklejenia, z nazwą konta i okna) i **👁 POWINIENEŚ ZOBACZYĆ** (oczekiwany wynik).
- W repo bez pluginu `kuznia` (brak skilli i agenta) nie pracuj według własnych zasad: zaproponuj Pawłowi `/kuznia:nowy-projekt` albo instalację pluginu (`claude plugin install kuznia@kuznia-kodu --scope project`).
- Nigdy nie czytaj ani nie wypisuj sekretów, kluczy, haseł i danych z `.env*`, `dane/` oraz baz. `git push` robi tylko Paweł.
