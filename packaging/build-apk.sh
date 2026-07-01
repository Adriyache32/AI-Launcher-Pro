#!/bin/bash
# Build APK for Android 10-16
# Requires: buildozer, python-for-android, Android SDK
# Run on: Linux or Termux
set -e

DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$DIR"

VERSION="2.12.v"
PKG_NAME="ai-launcher-pro"
LAUNCHER="../launcher.py"

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  AI Launcher Pro - APK Builder"
echo "  v${VERSION} for Android 10-16"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

if [ ! -f "$LAUNCHER" ]; then
    echo "❌ launcher.py not found"
    exit 1
fi

# Create buildozer.spec
cat > buildozer.spec << SPEC
[app]
title = AI Launcher Pro
package.name = ailauncher
package.domain = com.ailauncher
source.dir = .
source.include_exts = py
version = ${VERSION}
version.regex = 
version.filename = %(source.dir)s/src/version.txt
requirements = python3, curses, shutil, shlex, pathlib
orientation = landscape
osx.python_version = 3
fullscreen = 1

# Android
android.api = 33
android.minapi = 29
android.ndk = 27b
android.sdk = 33
android.ndk_path = 
android.sdk_path = 
android.gradle_dependencies = 'androidx.legacy:legacy-support-v4:1.0.0'
android.enable_androidx = True
android.manifest_intent_filters = 
android.add_activity = com.termux.app.TermuxActivity
android.archs = arm64-v8a, armeabi-v7a, x86_64
android.permissions = INTERNET
android.entrypoint = launcher.py

# Python-for-android
p4a.branch = develop
p4a.source_dir = 
p4a.local_recipes = 
p4a.hooks = 
p4a.hook = 
p4a.requirements = python3, curses, shutil, shlex, pathlib
p4a.orientation = landscape
p4a.window_size = 800x600

# Build
requirements = python3
presplash.filename = 
icon.filename = 
SPEC

# Create source directory structure
mkdir -p src
cp "$LAUNCHER" src/launcher.py
echo "$VERSION" > src/version.txt

cat > src/main.py << 'MAIN'
#!/usr/bin/env python3
"""Entry point for Android APK"""
import os, sys
# Ensure we're in the right directory
os.chdir(os.path.dirname(os.path.abspath(__file__)))
import launcher
MAIN

# Check buildozer
if command -v buildozer &>/dev/null; then
    echo "🔧 buildozer found, building APK..."
    buildozer android debug
    echo "✅ APK generated in bin/"
else
    echo "❌ buildozer not found"
    echo ""
    echo "Install buildozer:"
    echo "  pip install buildozer"
    echo ""
    echo "Or on Termux:"
    echo "  pkg install buildozer"
    echo "  pip install --user python-for-android"
    echo ""
    echo "Then run:"
    echo "  buildozer android debug"
    echo ""
    echo "APK will be in: bin/AILauncherPro-${VERSION}-arm64-v8a-debug.apk"
fi

echo ""
echo "📦 Para compilar APK manualmente:"
echo "  1. Instalar Termux desde F-Droid"
echo "  2. pkg update && pkg install python python-curses git"
echo "  3. git clone https://github.com/Adriyache32/AI-Launcher-Pro"
echo "  4. cd AI-Launcher-Pro/packaging"
echo "  5. bash build-apk.sh"
echo ""
echo "O instalar directo en Termux:"
echo "  curl -fsSL https://raw.githubusercontent.com/Adriyache32/AI-Launcher-Pro/main/termux-setup.sh | sh"
