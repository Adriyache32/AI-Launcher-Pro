#!/bin/bash
set -e

BOLD='\033[1m'
GREEN='\033[0;32m'
CYAN='\033[0;36m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BOLD}  AI Launcher Pro - Instalador${NC}"
echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

OS="linux"
if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "cygwin" || "$OSTYPE" == "win32" ]]; then
    OS="windows"
fi

DEST="$HOME/AI's Programs"
mkdir -p "$DEST"
cd "$DEST"

echo -e "${YELLOW}[1/4]${NC} Descargando AI Launcher..."
curl -fsSL "https://raw.githubusercontent.com/Adriyache32/AI-Launcher-Pro/main/launcher.py" -o launcher.py
curl -fsSL "https://raw.githubusercontent.com/Adriyache32/AI-Launcher-Pro/main/run.sh" -o run.sh
curl -fsSL "https://raw.githubusercontent.com/Adriyache32/AI-Launcher-Pro/main/run.ps1" -o run.ps1
curl -fsSL "https://raw.githubusercontent.com/Adriyache32/AI-Launcher-Pro/main/run.bat" -o run.bat
chmod +x launcher.py run.sh 2>/dev/null

echo -e "${YELLOW}[2/4]${NC} Creando comando open-ai..."
for BIN in "$HOME/.local/bin" "$HOME/.opencode/bin"; do
    mkdir -p "$BIN"
    rm -f "$BIN/open-ai"
    cat > "$BIN/open-ai" << EOF
#!/bin/bash
"$DEST/run.sh"
EOF
    chmod +x "$BIN/open-ai"
done

echo -e "${YELLOW}[3/4]${NC} Verificando Python..."
PY=""
if command -v python3 &>/dev/null; then
    PY="python3"
elif command -v python &>/dev/null; then
    PY="python"
fi
if [[ -z "$PY" ]]; then
    echo -e "${YELLOW}Python no encontrado. Instala Python 3.14+ primero.${NC}"
    echo -e "${YELLOW}  https://python.org/downloads/${NC}"
fi

echo -e "${YELLOW}[4/4]${NC} Creando acceso directo..."
if [[ "$OS" == "linux" ]]; then
    DEST_ESCAPED=$(echo "$DEST" | sed 's/ /\\ /g')
    mkdir -p "$HOME/.local/share/applications"
    cat > "$HOME/.local/share/applications/AI_Launcher.desktop" << EOF
[Desktop Entry]
Name=AI Launcher Pro
Comment=Menu de IAs para programar
Exec=$DEST_ESCAPED/run.sh
Icon=utilities-terminal
Terminal=true
Type=Application
Categories=Development;
EOF
    cp "$HOME/.local/share/applications/AI_Launcher.desktop" "$HOME/Escritorio/" 2>/dev/null || true
    chmod +x "$HOME/.local/share/applications/AI_Launcher.desktop" 2>/dev/null || true
    chmod +x "$HOME/Escritorio/AI_Launcher.desktop" 2>/dev/null || true
elif [[ "$OS" == "windows" ]]; then
    echo -e "  Crea un acceso directo a: $DEST\\run.bat"
fi

echo ""
echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}  Instalacion completada!${NC}"
echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""
echo -e "  Corre el launcher:"
echo -e "    ${BOLD}open-ai${NC}"
echo ""
echo -e "  Cada IA la instalas por separado cuando la necesites."
echo -e "  El launcher te muestra ○ que falta y ● que esta listo."
echo ""
