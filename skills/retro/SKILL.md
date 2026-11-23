---
name: retro
description: Retrospektywa metody - zbierz wnioski z logów pakietów i docs/porzadki.md, zaproponuj diff do METODA.md i wpis do CHANGELOG.md
disable-model-invocation: true
---

Zbierasz wnioski z projektu i przygotowujesz **propozycję** zmiany metody. Zmiany w repo `kuznia-kodu` zatwierdza i wypycha tylko Paweł. Nie zmieniasz zasad, według których sam jesteś oceniany: przygotowujesz diff do przeglądu.

## Co zrobić
1. Przeczytaj logi pakietów (`docs/pakiety/PK-*.md`, sekcja „Log”), `docs/porzadki.md` oraz „Propozycje do METODA” (jeśli są w repo projektu lub podał je Paweł).
2. Wskaż wnioski w trzech grupach:
   - **powtarzające się uwagi** (te same w kilku pakietach lub projektach): kandydaci na zmianę skilla, agenta, szablonu albo kontroli;
   - **rundy i blokery** (ile rund recenzji, które klasy blokerów wracały): czy klasy blokerów lub zakres recenzji wymagają zmiany;
   - **tarcie w pracy** (zatrzymania, niejasne zlecenia, ręczne obejścia): czego brakuje w metodzie.
3. Dla każdego wniosku podaj: co, dlaczego, z którego pakietu lub projektu (`plik:linia` lub numer pakietu), oraz proponowaną zmianę (plik w repo `kuznia-kodu` i treść).
4. Przygotuj (jako tekst w odpowiedzi lub plik `.patch` w katalogu roboczym, nie w repo `kuznia-kodu`):
   - diff do `METODA.md`, z podniesieniem wersji,
   - wpis do `CHANGELOG.md` (wersja, data, lista zmian).
5. Nie nakładaj diffu, nie rób commitu ani pushu w `kuznia-kodu`. Wypisz kroki dla Pawła: nałożenie, przegląd, push, podniesienie wersji pluginu, aktualizacja kopii `METODA.md` w Projektach claude.ai.

Nie przenoś do propozycji nazw projektów, danych, adresów ani sekretów: repo `kuznia-kodu` jest publiczne. Oznaczaj stwierdzenia: `FACT`, `PROPOSED`, `OPEN QUESTION`, `IDEA`.
