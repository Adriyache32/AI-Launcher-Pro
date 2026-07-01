#!/usr/bin/env python3
import curses
import time
import subprocess
import os
import shutil
import shlex
import platform
from pathlib import Path

HOME = Path.home()
W = os.name == "nt"
PY = "python" if W else "python3"
NPX = "npx.cmd" if W else "npx"
OP = str(HOME / ".opencode/bin/opencode")

CATS = [
    ("TOP TIER", [
        ("Claude Code",    "npx",              [NPX, "@anthropic-ai/claude-code"],         "Contexto enorme, el mas potente"),
        ("TU (opencode)",  OP,                 [OP],                                        "CLI local, multi-modelo, liviano"),
        ("Free Claude Code","free-claude-code", ["free-claude-code"],                       "Proxy con 18 providers, gratis"),
    ]),
    ("BEST VALUE", [
        ("OpenAI",         "openai",           ["openai"],                                  "GPT-4o, lider en generacion"),
        ("Gemini-CLI",     "gemini-cli",        ["gemini-cli"],                              "Google 1M tokens, gratis"),
        ("xAI (Grok)",     "grok",              ["grok"],                                    "Rapido, directo, sin rodeos"),
        ("Ollama",         "ollama",           ["ollama","run","llama3.1"],                  "100% local, privado, open-source"),
    ]),
    ("SOLID", [
        ("Cline",          "code",             ["code","--install-extension","saoudrizwan.claude-dev"], "Agente autonomo VS Code"),
        ("GitHub Copilot", "gh",               ["gh","copilot"],                            "Autocompletado en el IDE"),
        ("Kilo Code",      "code",             ["code","--install-extension","kilocode.kilocode"], "Codigo rapido VS Code"),
        ("Cursor IDE",     "cursor",           ["cursor","."],                              "IDE con AI integrada"),
        ("OpenRouter",     "openrouter",       ["openrouter"],                              "Un API para muchos modelos"),
        ("Kiro AI",        "kiro",             ["kiro"],                                    "CLI minimalista"),
        ("Vertex AI",      "gcloud",           ["gcloud"],                                  "Google Cloud enterprise"),
    ]),
    ("NICHE", [
        ("Nvidia NIM",     "docker",           ["docker"],                                  "Microservicios IA en GPU"),
        ("Cloudflare AI",  "wrangler",         ["wrangler"],                                "Modelos en el edge"),
        ("Qoder",          "qoder",            ["qoder"],                                   "Asistente ligero"),
        ("Antigravity",    "antigravity",      ["antigravity"],                             "IA claim con Python"),
        ("BytePlus",       "byteplus",         ["byteplus"],                                "Modelos ByteDance"),
    ]),
]

def ready(check):
    if check.startswith(str(HOME)):
        return Path(check).exists()
    return shutil.which(check) is not None

def s_addstr(std, y, x, s, *args):
    try:
        max_y, max_x = std.getmaxyx()
        if y < 0 or y >= max_y or x < 0 or x >= max_x:
            return
        if x + len(s) > max_x:
            s = s[:max_x - x]
        if s:
            std.addstr(y, x, s, *args)
    except:
        pass

def find_terminal():
    if W:
        return None
    terms = [
        ("x-terminal-emulator", ["-e"]),
        ("gnome-terminal",      ["--", "bash", "-c"]),
        ("konsole",             ["--hold", "-e"]),
        ("xfce4-terminal",      ["-e"]),
        ("lxterminal",          ["-e"]),
        ("urxvt",               ["-e"]),
        ("xterm",               ["-e"]),
        ("alacritty",           ["-e"]),
        ("kitty",               ["-e"]),
        ("foot",                ["-e"]),
        ("wezterm",             ["-e"]),
    ]
    for exe, flags in terms:
        if shutil.which(exe):
            return (exe, flags)
    return None

def boot_screen(std):
    h, w = std.getmaxyx()
    logo = [
        "  █████  ██      ██       █████  ██    ██ ███    ██  ██████  ██   ██ ███████ ██████  ",
        " ██   ██ ██      ██      ██   ██ ██    ██ ████   ██ ██       ██  ██  ██      ██   ██ ",
        " ███████ ██      ██      ███████ ██    ██ ██ ██  ██ ██       █████   █████   ██████  ",
        " ██   ██ ██      ██      ██   ██ ██    ██ ██  ██ ██ ██       ██  ██  ██      ██   ██ ",
        " ██   ██ ███████ ███████ ██   ██  ██████  ██   ████  ██████  ██   ██ ███████ ██   ██ ",
    ]
    sub = "  AI LAUNCHER PRO  v2.0  —  19 TOOLS"
    line = "  ─────────────────────────────────────────────"

    for i in range(6):
        std.clear()
        for y, l in enumerate(logo):
            for x, ch in enumerate(l):
                if ch != ' ':
                    if i < 5 and x > i * 4:
                        continue
                    s_addstr(std, h//2-7+y, w//2-30+x, ch, curses.color_pair(1) | curses.A_BOLD)
        std.attron(curses.color_pair(2) | curses.A_BOLD)
        s_addstr(std, h//2-1, w//2-len(sub)//2, sub[:len(sub)//6*i+6])
        std.attroff(curses.color_pair(2) | curses.A_BOLD)
        std.attron(curses.color_pair(1))
        s_addstr(std, h//2, w//2-len(line)//2, line[:len(line)//6*i+6])
        std.attroff(curses.color_pair(1))
        std.refresh()
        time.sleep(0.05)

    std.attron(curses.color_pair(3) | curses.A_BLINK)
    s_addstr(std, h-2, w//2-12, "  PRESIONE CUALQUIER TECLA  ")
    std.attroff(curses.color_pair(3) | curses.A_BLINK)
    std.refresh()
    std.getch()

def draw_header(std):
    h, w = std.getmaxyx()
    title = "██╗  ██╗██╗      █████╗ ██╗   ██╗███╗   ██╗ ██████╗██╗  ██╗███████╗██████╗"
    sub   = "██║  ██║██║     ██╔══██╗██║   ██║████╗  ██║██╔════╝██║  ██║██╔════╝██╔══██╗"
    sub2  = "███████║██║     ███████║██║   ██║██╔██╗ ██║██║     ███████║█████╗  ██████╔╝"
    sub3  = "██╔══██║██║     ██╔══██║██║   ██║██║╚██╗██║██║     ██╔══██║██╔══╝  ██╔══██╗"
    sub4  = "██║  ██║███████╗██║  ██║╚██████╔╝██║ ╚████║╚██████╗██║  ██║███████╗██║  ██║"
    ver   = "v2.0  —  19 TOOLS"
    sep   = "══════════════════════════════════════════════════════════════════════════════"

    for y, line in enumerate([title, sub, sub2, sub3, sub4]):
        std.attron(curses.color_pair(1) | curses.A_BOLD)
        s_addstr(std, y, 2, line)
        std.attroff(curses.color_pair(1) | curses.A_BOLD)

    std.attron(curses.color_pair(2))
    s_addstr(std, 5, w-len(ver)-2, ver)
    std.attroff(curses.color_pair(2))
    std.attron(curses.color_pair(1))
    s_addstr(std, 6, 0, sep[:w-1])
    std.attroff(curses.color_pair(1))

def draw_sidebar(std, cat_idx, focus):
    h, w = std.getmaxyx()
    y0 = 8
    std.attron(curses.color_pair(1))
    s_addstr(std, y0, 2, "┌────────────────────┐")
    s_addstr(std, y0+1, 2, "│  [ NAVEGACION ]    │")
    s_addstr(std, y0+2, 2, "├────────────────────┤")
    for i, (cat, _) in enumerate(CATS):
        x = 2
        yy = y0 + 3 + i
        if yy >= h-2:
            break
        if i == cat_idx and focus == "sidebar":
            std.attron(curses.color_pair(2) | curses.A_BOLD)
            s_addstr(std, yy, x, "│ ")
            s_addstr(std, yy, x+2, f"> {cat}")
            s_addstr(std, yy, x+2+len(cat)+1, "  │")
            std.attroff(curses.color_pair(2) | curses.A_BOLD)
        else:
            std.attron(curses.color_pair(3))
            s_addstr(std, yy, x, f"│   {cat}  │")
            std.attroff(curses.color_pair(3))
    std.attron(curses.color_pair(1))
    s_addstr(std, y0+3+len(CATS), 2, "└────────────────────┘")
    std.attroff(curses.color_pair(1))

def draw_grid(std, cat_idx, sel_idx, focus):
    h, w = std.getmaxyx()
    items = CATS[cat_idx][1]
    cols = 3
    bw = 22
    bh = 4
    gap = 2
    start_x = 28
    start_y = 7

    for gi, (name, check, cmd, desc) in enumerate(items):
        col = gi % cols
        row = gi // cols
        xx = start_x + col * (bw + gap)
        yy = start_y + row * (bh + 1)
        selected = (gi == sel_idx and focus == "grid")
        num = gi + sum(len(CATS[i][1]) for i in range(cat_idx)) + 1
        rdy = ready(check)

        for y in range(bh):
            if xx + bw > w-1 or yy + y >= h-1:
                continue
            if y == 0:
                pair = curses.color_pair(2) if selected else curses.color_pair(3)
                std.attron(pair | (curses.A_BOLD if selected else 0))
                s_addstr(std, yy, xx, f"┌────────────────────┐")
                std.attroff(pair | (curses.A_BOLD if selected else 0))
            elif y == 1:
                if selected:
                    std.attron(curses.color_pair(2) | curses.A_BOLD)
                    s_addstr(std, yy+1, xx, f"│ {num:2d} {name:15s} │")
                    std.attroff(curses.color_pair(2) | curses.A_BOLD)
                else:
                    s_addstr(std, yy+1, xx, f"│ {num:2d} {name:15s} │")
            elif y == 2:
                stars = "★★★★★" if num <= 3 else "★★★★☆" if num <= 7 else "★★★☆☆" if num <= 14 else "★★☆☆☆"
                pair = curses.color_pair(2) if selected else curses.color_pair(3)
                std.attron(pair | (curses.A_BOLD if selected else 0))
                s_addstr(std, yy+2, xx, f"│ {stars}         │")
                std.attroff(pair | (curses.A_BOLD if selected else 0))
            elif y == 3:
                dot = "●" if rdy else "○"
                col_dot = 2 if rdy else 3
                label = "LISTO" if rdy else "FALTA"
                if selected:
                    std.attron(curses.color_pair(2) | curses.A_BOLD)
                    s_addstr(std, yy+3, xx, f"│ {dot} {label}           │")
                    std.attroff(curses.color_pair(2) | curses.A_BOLD)
                else:
                    std.attron(curses.color_pair(col_dot))
                    s_addstr(std, yy+3, xx, f"│ {dot} {label}           │")
                    std.attroff(curses.color_pair(col_dot))

def draw_footer(std, focus, cat_idx, sel_idx):
    h, w = std.getmaxyx()
    sep = "══════════════════════════════════════════════════════════════════════════════"
    std.attron(curses.color_pair(1))
    s_addstr(std, h-3, 0, sep[:w-1])
    std.attroff(curses.color_pair(1))

    if focus == "sidebar":
        txt = "  ↑↓ navegar  → entrar al grid  q salir"
    else:
        items = CATS[cat_idx][1]
        name = items[sel_idx][0]
        txt = f"  ↑↓←→ mover  ENTER lanzar {name} en terminal nueva  ← volver  q salir"

    std.attron(curses.color_pair(2))
    s_addstr(std, h-2, 2, txt)
    std.attroff(curses.color_pair(2))

def launch_in_terminal(cmd_list):
    if not cmd_list:
        return False
    cmd_str = " ".join(shlex.quote(str(c)) for c in cmd_list)

    if W:
        subprocess.Popen(["start", "cmd", "/c", cmd_str], shell=True)
        return True

    term = find_terminal()
    if term:
        exe, flags = term
        subprocess.Popen([exe] + flags + [cmd_str],
                         stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return True
    return False

def launch(std, item):
    name, check, cmd, desc = item
    h, w = std.getmaxyx()

    if not cmd or (len(cmd) == 1 and cmd[0] in (PY, "python", "python3")):
        std.clear()
        std.attron(curses.color_pair(1) | curses.A_BOLD)
        s_addstr(std, h//2-4, w//2-len(f"▶ {name}")//2, f"▶ {name}")
        std.attroff(curses.color_pair(1) | curses.A_BOLD)
        std.attron(curses.color_pair(3))
        s_addstr(std, h//2-1, w//2-len(desc)//2, desc)
        std.attroff(curses.color_pair(3))
        std.attron(curses.color_pair(2))
        pip_name = name.lower().replace(" ","").replace("(","").replace(")","")
        s_addstr(std, h//2+1, w//2-18, f"pip install {pip_name}   (si aplica)")
        std.attroff(curses.color_pair(2))
        std.attron(curses.color_pair(3) | curses.A_BLINK)
        s_addstr(std, h-2, w//2-15, "Presione cualquier tecla")
        std.attroff(curses.color_pair(3) | curses.A_BLINK)
        std.refresh()
        std.getch()
        return

    std.clear()
    pair = curses.color_pair(1) if True else curses.color_pair(2)
    std.attron(curses.color_pair(1) | curses.A_BOLD)
    mid = h // 2
    s_addstr(std, mid-2, w//2 - len(f"▶ Abriendo {name}")//2, f"▶ Abriendo {name}")
    std.attron(curses.color_pair(3))
    s_addstr(std, mid, w//2 - len(desc)//2, desc)
    std.attroff(curses.color_pair(3))
    std.attron(curses.color_pair(2))
    s_addstr(std, mid+1, w//2-12, "Nueva terminal independiente")
    std.attroff(curses.color_pair(2))
    std.refresh()
    time.sleep(0.5)

    opened = launch_in_terminal(cmd)
    if not opened:
        curses.endwin()
        subprocess.run(cmd)
        curses.doupdate()
    else:
        std.attron(curses.color_pair(2))
        s_addstr(std, mid+3, w//2-15, "Terminal lanzada, volviendo al menu...")
        std.attroff(curses.color_pair(2))
        std.refresh()
        time.sleep(0.5)

def main(std):
    curses.curs_set(0)
    curses.use_default_colors()
    curses.init_pair(1, curses.COLOR_RED, -1)
    curses.init_pair(2, curses.COLOR_GREEN, -1)
    curses.init_pair(3, curses.COLOR_YELLOW, -1)

    boot_screen(std)

    cat_idx = 0
    sel_idx = 0
    focus = "sidebar"

    while True:
        std.clear()
        draw_header(std)
        draw_sidebar(std, cat_idx, focus)
        draw_grid(std, cat_idx, sel_idx, focus)
        draw_footer(std, focus, cat_idx, sel_idx)
        std.refresh()

        k = std.getch()

        if focus == "sidebar":
            if k == curses.KEY_UP and cat_idx > 0:
                cat_idx -= 1
                sel_idx = 0
            elif k == curses.KEY_DOWN and cat_idx < len(CATS) - 1:
                cat_idx += 1
                sel_idx = 0
            elif k == curses.KEY_RIGHT or k == ord('\t') or k == ord('\n'):
                focus = "grid"
                sel_idx = 0
            elif k == ord('q'):
                break
        elif focus == "grid":
            items = CATS[cat_idx][1]
            cols = 3
            rows = (len(items) + cols - 1) // cols
            rr = sel_idx // cols
            if k == curses.KEY_UP and rr > 0:
                sel_idx -= cols
            elif k == curses.KEY_DOWN and rr < rows - 1:
                n = sel_idx + cols
                if n < len(items):
                    sel_idx = n
            elif k == curses.KEY_LEFT:
                if sel_idx % cols > 0:
                    sel_idx -= 1
                else:
                    focus = "sidebar"
            elif k == curses.KEY_RIGHT and sel_idx % cols < cols - 1:
                n = sel_idx + 1
                if n < len(items):
                    sel_idx = n
            elif k == ord('\n'):
                item = items[sel_idx]
                launch(std, item)
            elif k == ord('q'):
                break

def main_wrapper():
    try:
        curses.wrapper(main)
    except Exception as e:
        print("\n" + "="*50)
        print("ERROR en AI Launcher Pro:")
        print(f"  {type(e).__name__}: {e}")
        print("="*50)
        input("\nPresiona Enter para salir...")
    except KeyboardInterrupt:
        print("\nSaliste.")

if __name__ == "__main__":
    main_wrapper()
