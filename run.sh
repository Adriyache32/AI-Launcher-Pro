#!/bin/bash
cd "$HOME/AI's Programs" || cd "$(dirname "$0")"
if command -v python3 &>/dev/null; then
    python3 launcher.py
else
    python launcher.py
fi
echo "El launcher se cerro. Presiona Enter para salir..."
read -r
