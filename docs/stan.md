# Stan repo kuznia-kodu

Oznaczenia: `FACT`, `PROPOSED`, `OPEN QUESTION`, `IDEA`. Aktualizuje wykonawca na końcu pakietu.

## Pakiety
| Pakiet | Stan | Uwagi |
|---|---|---|
| PK-M0 | wykonany lokalnie, czeka na push | recenzja: ZATWIERDZAM Z UWAGAMI (runda 2); log w pakiecie |

## Testy
- `python -m pytest testy`: 79 passed, 1 skipped (zgodność ustawień repo po nałożeniu `docs/po-pk-m0.patch`).

## Otwarte decyzje i pytania (Paweł)
- `OPEN QUESTION`: ochrona profilu agenta i pluginu przed obejściem blokad (`docs/porzadki.md`, „Z PK-M0”, pierwsza pozycja).
- `OPEN QUESTION`: pierwsza instalacja pluginu z publicznego GitHuba (kryterium PK-M0) i forma wywołania skilli bez przedrostka.
- `OPEN QUESTION`: czy `instaluj/windows.ps1` przechodzi parser i `-Sprawdz` (nie uruchamiano).

## Czeka na push
- 8 commitów lokalnych (`git log --oneline @{upstream}..HEAD`).
