# AI-Launcher-Pro 🤖

> Menú interactivo con **19+ IAs** para programar. Multiplataforma (7 versiones), auto-actualizador, local-first.

## ✨ Características

- **19+ IAs integradas**: ChatGPT, Claude, Gemini, Ollama, CodeLlama, WizardCoder, Phind, DeepSeek, StarCoder, y más
- **7 versiones multiplataforma**: Linux, Windows, macOS, Termux/Android, Web, Portable, Docker
- **Auto-actualizador**: Verifica y descarga la última versión al iniciar
- **Modo offline**: Funciona con Ollama 100% local (sin API keys)
- **Interfaz TUI**: Navegación por teclado, búsqueda fuzzy, historial
- **Plugins**: Sistema de extensiones para añadir IAs personalizadas

## 🚀 Instalación rápida

```bash
# Linux / macOS / WSL
curl -fsSL https://raw.githubusercontent.com/Adriyache32/AI-Launcher-Pro/main/install.sh | bash

# Windows (PowerShell)
irm https://raw.githubusercontent.com/Adriyache32/AI-Launcher-Pro/main/install.ps1 | iex

# Termux / Android
pkg install python && curl -fsSL https://raw.githubusercontent.com/Adriyache32/AI-Launcher-Pro/main/termux-setup.sh | bash

# Docker
docker run -it --rm adriyache32/ai-launcher-pro
```

## 📸 Demo

![AI-Launcher-Pro Demo](assets/demo.gif)

## ⌨️ Uso

```bash
ai-launcher          # Menú principal
ai-launcher --chat   # Chat directo
ai-launcher --code   # Modo código
ai-launcher --local  # Solo modelos locales (Ollama)
```

## 🏗️ Arquitectura

```
launcher.py                 # Entry point
├── core/
│   ├── config.py          # Configuración YAML + env vars
│   ├── providers/         # 19+ proveedores de IA
│   │   ├── openai.py
│   │   ├── anthropic.py
│   │   ├── ollama.py      # Local-first
│   │   └── ...
│   ├── ui/
│   │   ├── tui.py         # Textual TUI
│   │   ├── menu.py        # Menú interactivo
│   │   └── fuzzy.py       # Búsqueda fuzzy
│   └── updater.py         # Auto-updater
├── plugins/               # Sistema de plugins
└── packaging/             # 7 builds multiplataforma
```

## 🔧 Configuración

```yaml
# ~/.config/ai-launcher/config.yaml
providers:
  ollama:
    enabled: true
    host: "http://localhost:11434"
    models: ["codellama:13b", "wizardcoder:15b"]
  openai:
    enabled: true
    api_key: "${OPENAI_API_KEY}"
  anthropic:
    enabled: true
    api_key: "${ANTHROPIC_API_KEY}"
```

## 🤝 Contribuir

Ver [CONTRIBUTING.md](CONTRIBUTING.md)

## 📄 Licencia

MIT — ver [LICENSE](LICENSE)

---

**¿Te gusta? ¡Dale una ⭐!** Ayuda a que más devs lo encuentren.
