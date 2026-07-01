#!/bin/bash
# Build .deb package for Termux / Debian / Ubuntu
set -e

DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$DIR"

VERSION="2.12.v"
PKG_NAME="ai-launcher-pro"
ARCH="all"

# Clean
rm -rf build
mkdir -p build/DEBIAN
mkdir -p build/usr/bin
mkdir -p build/usr/share/ai-launcher
mkdir -p build/usr/share/applications

# Copy launcher
cp "../launcher.py" build/usr/share/ai-launcher/
chmod 755 build/usr/share/ai-launcher/launcher.py

# Create launcher script
cat > build/usr/bin/open-ai << 'EOF'
#!/bin/sh
exec python3 /usr/share/ai-launcher/launcher.py
EOF
chmod 755 build/usr/bin/open-ai

# Desktop entry
cat > build/usr/share/applications/ai-launcher-pro.desktop << 'EOF'
[Desktop Entry]
Name=AI Launcher Pro
Comment=18 IAs para programar
Exec=open-ai
Terminal=true
Type=Application
Categories=Development;Utility;
EOF

# Control file
cat > build/DEBIAN/control << 'CONTROL'
Package: ai-launcher-pro
Version: 2.11.v
Architecture: all
Maintainer: Adriyache32 <adriyache32@users.noreply.github.com>
Description: Menu interactivo con 18 IAs para programar
 Estilo consola retro con curses.
 .
 Soporta: Linux, Windows, Termux
 .
 Incluye: Claude Code, opencode, OpenAI, Gemini-CLI,
 Grok, Ollama, Cline, Copilot, Kilo Code, Cursor IDE,
 OpenRouter, Kiro AI, Vertex AI, Nvidia NIM,
 Cloudflare AI, Qoder, Antigravity, BytePlus
Depends: python3
Recommends: python3-curses
CONTROL

# Post-install
cat > build/DEBIAN/postinst << 'POST'
#!/bin/sh
echo "✅ AI Launcher Pro instalado!"
echo "Corre: open-ai"
POST
chmod 755 build/DEBIAN/postinst

# Build .deb
fakeroot dpkg-deb --build build "${PKG_NAME}_${VERSION}_${ARCH}.deb"
echo ""
echo "📦 Package: ${PKG_NAME}_${VERSION}_${ARCH}.deb"
echo ""
echo "Instalar en Termux / Debian / Ubuntu:"
echo "  sudo apt install ./${PKG_NAME}_${VERSION}_${ARCH}.deb"
echo ""
echo "O en Termux:"
echo "  apt install ./${PKG_NAME}_${VERSION}_${ARCH}.deb"
