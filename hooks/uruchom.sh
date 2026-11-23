#!/bin/sh
# Launcher hookow pluginu kuznia: wybiera interpreter Pythona dzialajacy na Windows (Git Bash) i na Linuksie.
# Uzycie (z hooks/hooks.json): sh "${CLAUDE_PLUGIN_ROOT}/hooks/uruchom.sh" post|stop
# Dane hooka (JSON na stdin) trafiaja bez zmian do kontrola.py (exec zachowuje stdin).
# Kolejnosc: python3, python, py. Windows ma zwykle python (albo py), Linux zwykle tylko python3.
# Brak interpretera: komunikat na stderr i kod 1 (blad nieblokujacy: Claude Code pokaze powiadomienie).
KATALOG=$(dirname "$0")
for kandydat in python3 python py; do
    if command -v "$kandydat" >/dev/null 2>&1; then
        exec "$kandydat" "$KATALOG/kontrola.py" "$@"
    fi
done
echo "kuznia: brak interpretera Pythona (python3, python, py) w PATH; kontrola hooka pominieta" >&2
exit 1
