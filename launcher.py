#!/usr/bin/env python3
import curses
import time
import subprocess
import os
import shutil
import shlex
from pathlib import Path

HOME = Path.home()
W = os.name == "nt"
NPX = "npx.cmd" if W else "npx"

CATS = [
    ("TOP TIER", "★★★★★", [
        ("Claude Code",      "npx",              [NPX, "@anthropic-ai/claude-code"]),
        ("TU (opencode)",    str(HOME/".opencode/bin/opencode"), [str(HOME/".opencode/bin/opencode")]),
        ("Free Claude Code", "free-claude-code", ["free-claude-code"]),
    ]),
    ("BEST VALUE", "★★★★☆", [
        ("OpenAI",           "openai",           ["openai"]),
        ("Gemini-CLI",       "gemini-cli",       ["gemini-cli"]),
        ("xAI (Grok)",       "grok",             ["grok"]),
        ("Ollama",           "ollama",           ["ollama","run","llama3.1"]),
    ]),
    ("SOLID", "★★★☆☆", [
        ("Cline",            "code",             ["code","--install-extension","saoudrizwan.claude-dev"]),
        ("GitHub Copilot",   "gh",               ["gh","copilot"]),
        ("Kilo Code",        "code",             ["code","--install-extension","kilocode.kilocode"]),
        ("Cursor IDE",       "cursor",           ["cursor","."]),
        ("OpenRouter",       "openrouter",       ["openrouter"]),
        ("Kiro AI",          "kiro",             ["kiro"]),
        ("Vertex AI",        "gcloud",           ["gcloud"]),
    ]),
    ("NICHE", "★★☆☆☆", [
        ("Nvidia NIM",       "docker",           ["docker"]),
        ("Cloudflare AI",    "wrangler",         ["wrangler"]),
        ("Qoder",            "qoder",            ["qoder"]),
        ("Antigravity",      "antigravity",      ["antigravity"]),
        ("BytePlus",         "byteplus",         ["byteplus"]),
    ]),
]

ALL = [(c, s, a) for cat, star, items in CATS for a in items for c, s in [[cat, star]]]

def ready(check):
    if check.startswith(str(HOME)):
        return Path(check).exists()
    return shutil.which(check) is not None

def find_terminal():
    if W:
        return None
    terms = [
        ("x-terminal-emulator", ["-e"]), ("gnome-terminal", ["--","bash","-c"]),
        ("konsole",["--hold","-e"]), ("xfce4-terminal",["-e"]),
        ("lxterminal",["-e"]), ("urxvt",["-e"]), ("xterm",["-e"]),
        ("alacritty",["-e"]), ("kitty",["-e"]), ("foot",["-e"]), ("wezterm",["-e"]),
    ]
    for exe, flags in terms:
        if shutil.which(exe):
            return (exe, flags)
    return None

def s(scr, y, x, text, *args):
    try:
        my, mx = scr.getmaxyx()
        if y < 0 or y >= my or x < 0 or x >= mx:
            return
        if x + len(text) > mx:
            text = text[:mx - x]
        if text:
            scr.addstr(y, x, text, *args)
    except:
        pass

def launch_in_terminal(cmd_list):
    if not cmd_list:
        return False
    cmd_str = " ".join(shlex.quote(str(c)) for c in cmd_list)
    if W:
        subprocess.Popen(["start","cmd","/c",cmd_str], shell=True)
        return True
    term = find_terminal()
    if term:
        exe, flags = term
        subprocess.Popen([exe]+flags+[cmd_str], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return True
    return False

def launch(scr, name, check, cmd):
    h, w = scr.getmaxyx()
    mid = h // 2

    if not cmd or (len(cmd) == 1 and cmd[0] in ("python","python3")):
        scr.clear()
        s(scr, mid-1, w//2-len(f"> {name}")//2, f"> {name}", curses.color_pair(1)|curses.A_BOLD)
        pip = name.lower().replace(" ","").replace("(","").replace(")","")
        s(scr, mid+1, w//2-18, f"Instala con: pip install {pip}")
        s(scr, h-2, w//2-15, "Presiona cualquier tecla", curses.color_pair(3)|curses.A_BLINK)
        scr.refresh()
        scr.getch()
        return

    scr.clear()
    s(scr, mid-1, w//2-len(f"> Abriendo {name}")//2, f"> Abriendo {name}", curses.color_pair(1)|curses.A_BOLD)
    s(scr, mid+1, w//2-12, "Nueva terminal independiente", curses.color_pair(2))
    scr.refresh()
    time.sleep(0.5)

    opened = launch_in_terminal(cmd)
    if not opened:
        curses.endwin()
        subprocess.run(cmd)
        curses.doupdate()
    else:
        s(scr, mid+2, w//2-15, "Terminal lanzada, volviendo...", curses.color_pair(2))
        scr.refresh()
        time.sleep(0.5)

def main(scr):
    curses.curs_set(0)
    curses.use_default_colors()
    curses.init_pair(1, curses.COLOR_RED, -1)
    curses.init_pair(2, curses.COLOR_GREEN, -1)
    curses.init_pair(3, curses.COLOR_YELLOW, -1)

    scr.nodelay(1)
    for _ in range(10):
        scr.clear()
        scr.refresh()
        time.sleep(0.02)
    scr.nodelay(0)

    h, w = scr.getmaxyx()
    anim = ["██╗  ██╗██╗      █████╗ ██╗   ██╗███╗   ██╗ ██████╗██╗  ██╗███████╗██████╗",
            "██║  ██║██║     ██╔══██╗██║   ██║████╗  ██║██╔════╝██║  ██║██╔════╝██╔══██╗",
            "███████║██║     ███████║██║   ██║██╔██╗ ██║██║     ███████║█████╗  ██████╔╝",
            "██╔══██║██║     ██╔══██║██║   ██║██║╚██╗██║██║     ██╔══██║██╔══╝  ██╔══██╗",
            "██║  ██║███████╗██║  ██║╚██████╔╝██║ ╚████║╚██████╗██║  ██║███████╗██║  ██║"]
    for i in range(6):
        scr.clear()
        for y, line in enumerate(anim):
            reveal = line[:len(line)//6*(i+1)]
            s(scr, h//2-5+y, w//2-36, reveal, curses.color_pair(1)|curses.A_BOLD)
        s(scr, h//2+1, w//2-10, "AI LAUNCHER PRO  v2.0", curses.color_pair(2)|curses.A_BOLD)
        scr.refresh()
        time.sleep(0.05)
    s(scr, h-2, w//2-15, "Presiona cualquier tecla", curses.color_pair(3)|curses.A_BLINK)
    scr.refresh()
    scr.getch()

    idx = 0
    while True:
        scr.clear()
        h, w = scr.getmaxyx()

        s(scr, 0, 2, "AI LAUNCHER PRO  v2.0", curses.color_pair(1)|curses.A_BOLD)
        s(scr, 0, w-12, "19 TOOLS", curses.color_pair(2))
        s(scr, 1, 0, "="*(w-1), curses.color_pair(1))

        yy = 2
        gi = 0
        for cat, star, items in CATS:
            if yy + 1 >= h - 2:
                break

            s(scr, yy, 2, f"  {cat}", curses.color_pair(1)|curses.A_BOLD)
            s(scr, yy, 2+len(cat)+4, star, curses.color_pair(3))
            yy += 1

            cols = min(3, len(items))
            bw = 20
            bh = 3
            gap = 2
            start_x = max(2, (w - (cols * (bw + gap) - gap)) // 2)

            for i, (name, check, cmd) in enumerate(items):
                col = i % cols
                row = i // cols
                xx = start_x + col * (bw + gap)
                yyy = yy + row * (bh + 1)
                selected = (gi == idx)

                if yyy + bh >= h - 2:
                    break

                for ly in range(bh):
                    if ly == 0:
                        pair = curses.color_pair(2) if selected else curses.color_pair(1)
                        s(scr, yyy, xx, "┌──────────────────┐", pair|(curses.A_BOLD if selected else 0))
                    elif ly == 1:
                        num = gi + 1
                        txt = f"│ {num:2d} {name:14s}│"
                        pair = curses.color_pair(2) if selected else 0
                        s(scr, yyy+1, xx, txt, pair|(curses.A_BOLD if selected else 0))
                    elif ly == 2:
                        rdy = ready(check)
                        dot = "●" if rdy else "○"
                        st = "LISTO" if rdy else "FALTA"
                        pair = curses.color_pair(2) if selected else (curses.color_pair(2) if rdy else curses.color_pair(3))
                        s(scr, yyy+2, xx, f"│ ★★★★★ {dot} {st}    │", pair|(curses.A_BOLD if selected else 0))

                gi += 1

            yy += ((len(items) + cols - 1) // cols) * (bh + 1) + 1

        s(scr, h-2, 0, "─"*(w-1), curses.color_pair(1))
        s(scr, h-1, 2, "↑↓ mover  ENTER lanzar  q salir", curses.color_pair(2))
        scr.refresh()

        key = scr.getch()
        if key == curses.KEY_UP and idx > 0:
            idx -= 1
        elif key == curses.KEY_DOWN and idx < len(ALL) - 1:
            idx += 1
        elif key == curses.KEY_LEFT and idx > 0:
            idx -= 1
        elif key == curses.KEY_RIGHT and idx < len(ALL) - 1:
            idx += 1
        elif key == ord('\n'):
            cat, star, (name, check, cmd) = ALL[idx]
            launch(scr, name, check, cmd)
        elif key == ord('q'):
            break

def main_wrapper():
    try:
        curses.wrapper(main)
    except Exception as e:
        print("\n" + "="*50)
        print(f"ERROR: {type(e).__name__}: {e}")
        print("="*50)
        input("\nPresiona Enter para salir...")
    except KeyboardInterrupt:
        print("\nSaliste.")

if __name__ == "__main__":
    main_wrapper()
