#!/bin/bash
# === Termux Setup for AI Launcher Pro ===
# Run this in Termux on Android 10-16
# No root required

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  AI Launcher Pro - Termux Setup"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Check Termux
if [ -z "$TERMUX_VERSION" ] && [ ! -d /data/data/com.termux ]; then
    echo "❌ Esto solo corre en Termux"
    exit 1
fi

echo "📦 Instalando dependencias..."
pkg update -y
pkg install -y python python-curses git curl

echo "📥 Descargando AI Launcher Pro..."
curl -fsSL "https://raw.githubusercontent.com/Adriyache32/AI-Launcher-Pro/main/launcher.py" -o "$PREFIX/bin/ai-launcher.py"
chmod +x "$PREFIX/bin/ai-launcher.py"

cat > "$PREFIX/bin/open-ai" << 'BIN'
#!/bin/sh
exec python3 "$PREFIX/bin/ai-launcher.py"
BIN
chmod +x "$PREFIX/bin/open-ai"

echo ""
echo "✅ Instalacion completada!"
echo ""
echo "Corre el launcher:"
echo "  open-ai"
echo ""
echo "Cada IA la instalas por separado cuando la necesites."
echo "El launcher te muestra ○ que falta y ● que esta listo."
echo ""
echo "🧹 Para desinstalar:"
echo "  rm $PREFIX/bin/ai-launcher.py $PREFIX/bin/open-ai"
