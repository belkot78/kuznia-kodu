#!/bin/sh
# PROPOSED: szkic instalatora metody kuznia-kodu dla Linuksa (np. osobne srodowisko P2). NIE jest przetestowany
# i nie jest uzywany. Agent Claude Code tego skryptu tylko pisze, nigdy go nie uruchamia. Uruchamia Pawel jako root.
#
# Odpowiednik instaluj/windows.ps1: granica to osobny uzytkownik systemowy i uprawnienia plikow (nie settings.json).
#   1. sprawdza, czy istnieje uzytkownik agenta (NIE tworzy go),
#   2. kopiuje szablon-uzytkownika/CLAUDE.md do ~agent/.claude/CLAUDE.md,
#   3. ustawia wlasciciela plikow kontrolnych na wlasciciela (Pawla) i odbiera agentowi zapis (chmod, chattr +i).
# Tryb --sprawdz tylko raportuje. Pliki kontrolne: .claude/, .githooks/, .git/config, .git/hooks/,
# tools/przeglad.py, tools/przeglad_konfig.py, tools/tests/test_settings.py.
#
# OPEN QUESTION: czy blokada ma byc przez chown root/wlasciciel + chmod go-w, czy przez chattr +i (wymaga
# uprawnien root i utrudnia aktualizacje przez git pull). Do rozstrzygniecia przy pierwszym projekcie P2.
set -eu

AGENT="${AGENT:-claude-agent}"
WLASCICIEL="${WLASCICIEL:-}"          # OPEN QUESTION: konto wlasciciela; brak domyslnej wartosci
KATALOG_REPO="${KATALOG_REPO:-}"      # OPEN QUESTION: katalog z repozytoriami na tej maszynie
SPRAWDZ=0
[ "${1:-}" = "--sprawdz" ] && SPRAWDZ=1

if ! id "$AGENT" >/dev/null 2>&1; then
    echo "BLAD: brak uzytkownika $AGENT (skrypt go nie tworzy; zaloz go bez uprawnien administratora)" >&2
    exit 1
fi
if [ -z "$WLASCICIEL" ] || [ -z "$KATALOG_REPO" ]; then
    echo "BLAD: ustaw WLASCICIEL i KATALOG_REPO (szkic PROPOSED, brak wartosci domyslnych)" >&2
    exit 1
fi

KONTROLNE=".claude .githooks .git/config .git/hooks tools/przeglad.py tools/przeglad_konfig.py tools/tests/test_settings.py"
BLEDY=0
for repo in "$KATALOG_REPO"/*/; do
    [ -d "$repo/.git" ] || continue
    for plik in $KONTROLNE; do
        sciezka="$repo$plik"
        [ -e "$sciezka" ] || { echo "UWAGA: brak $sciezka"; continue; }
        if [ "$SPRAWDZ" -eq 0 ]; then
            chown -R "$WLASCICIEL" "$sciezka"
            chmod -R go-w "$sciezka"
        fi
        # agent nie moze pisac, jesli nie jest wlascicielem i brak prawa zapisu dla grupy/innych
        if [ "$(stat -c %U "$sciezka")" != "$WLASCICIEL" ] || [ -n "$(find "$sciezka" -maxdepth 0 -perm /022)" ]; then
            echo "BLAD: brak blokady zapisu: $sciezka"; BLEDY=$((BLEDY + 1))
        else
            echo "OK: $sciezka"
        fi
    done
done

if [ "$SPRAWDZ" -eq 0 ]; then
    domowy=$(getent passwd "$AGENT" | cut -d: -f6)
    mkdir -p "$domowy/.claude"
    cp "$(dirname "$0")/../szablon-uzytkownika/CLAUDE.md" "$domowy/.claude/CLAUDE.md"
    chown "$WLASCICIEL" "$domowy/.claude/CLAUDE.md"
    chmod go-w "$domowy/.claude/CLAUDE.md"
fi

[ "$BLEDY" -eq 0 ] || exit 1
