# AI Launcher Pro

<p align="center">
  <img src="https://img.shields.io/badge/version-2.11.v-blue?style=flat-square">
  <img src="https://img.shields.io/badge/Linux-red?style=flat-square">
  <img src="https://img.shields.io/badge/Windows-blue?style=flat-square">
  <img src="https://img.shields.io/badge/Termux-green?style=flat-square">
  <img src="https://img.shields.io/badge/python-3.8%2B-yellow?style=flat-square">
  <img src="https://img.shields.io/badge/license-MIT-lightgrey?style=flat-square">
</p>

Menu interactivo con 18 IAs para programar. Estilo consola retro.

```bash
curl -fsSL https://raw.githubusercontent.com/Adriyache32/AI-Launcher-Pro/main/install.sh | sh
```

## Plataformas

| Plataforma | Estado |
|------------|--------|
| Linux      | Funciona |
| Windows    | Funciona (PowerShell/Cmd) |
| Termux     | Funciona (`pkg install python python-curses`) |

## Como usar

```bash
open-ai           # Linux / Termux
python run.ps1    # Windows PowerShell
run.bat           # Windows CMD
```

| Tecla | Accion |
|-------|--------|
| `↑↓` | Navegar categorias |
| `→` | Entrar al grid de IAs |
| `↑↓←→` | Moverte entre IAs |
| `Enter` | Lanzar IA en terminal nueva |
| `←` | Volver a sidebar |
| `q` | Salir |

## Instalar en Termux

```bash
pkg update && pkg install python python-curses git
curl -fsSL https://raw.githubusercontent.com/Adriyache32/AI-Launcher-Pro/main/install.sh | sh
```

## Desinstalar

```bash
curl -fsSL https://raw.githubusercontent.com/Adriyache32/AI-Launcher-Pro/main/uninstall.sh | sh
```

Repo: https://github.com/Adriyache32/AI-Launcher-Pro
