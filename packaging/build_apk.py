#!/usr/bin/env python3
"""
AI Launcher Pro — Build APK for Android 10-16
===============================================
Requires: buildozer, python-for-android
Run this on: Linux with Android SDK or Termux

Usage:
  python build_apk.py         # Build APK
  python build_apk.py install  # Build + install on device
"""

import os, sys, subprocess, shutil, json
from pathlib import Path

HERE = Path(__file__).parent
VERSION = "2.11.v"
PKG = "com.ailauncher.pro"
NAME = "AI Launcher Pro"

SPEC = f"""[app]
title = {NAME}
package.name = ailauncher
package.domain = com
source.dir = .
source.include_exts = py,png,jpg,kv,atlas
version = {VERSION}
requirements = python3, curses
orientation = portrait
osx.python_version = 3
osx.kivy_version = 2.1.0
fullscreen = 1
android.api = 33
android.minapi = 29
android.ndk = 25b
android.sdk = 33
android.gradle_dependencies = 'androidx.legacy:legacy-support-v4:1.0.0'
android.enable_androidx = True
android.add_activity = com.termux.app.TermuxActivity
presplash.filename = %(source.dir)s/presplash.png
icon.filename = %(source.dir)s/icon.png
"""

def build_apk():
    print("🔧 Building APK...")

    # Write buildozer.spec
    with open(HERE / "buildozer.spec", "w") as f:
        f.write(SPEC)

    # Check buildozer
    if not shutil.which("buildozer"):
        print("❌ buildozer not found. Install:")
        print("   pip install buildozer")
        print("   Or run in Termux:")
        print("   pkg install buildozer")
        return False

    # Launch buildozer
    cmd = ["buildozer", "-v", "android", "debug"]
    if len(sys.argv) > 1 and sys.argv[1] == "install":
        cmd = ["buildozer", "-v", "android", "debug", "deploy", "run"]

    print(f"   {' '.join(cmd)}")
    subprocess.run(cmd, cwd=str(HERE))
    return True

if __name__ == "__main__":
    build_apk()
