#!/usr/bin/env python3
import curses, time, subprocess, os, shutil, shlex
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
    if check.startswith(str(HOME)): return Path(check).exists()
    return shutil.which(check) is not None

def find_term():
    if W: return None
    terms = [("x-terminal-emulator",["-e"]),("gnome-terminal",["--","bash","-c"]),
             ("konsole",["--hold","-e"]),("xfce4-terminal",["-e"]),("lxterminal",["-e"]),
             ("urxvt",["-e"]),("xterm",["-e"]),("alacritty",["-e"]),("kitty",["-e"]),
             ("foot",["-e"]),("wezterm",["-e"])]
    for exe, flags in terms:
        if shutil.which(exe): return (exe, flags)
    return None

def sa(scr, y, x, t, *args):
    try:
        my, mx = scr.getmaxyx()
        if y<0 or y>=my or x<0 or x>=mx: return
        if x+len(t)>mx: t = t[:mx-x]
        if t: scr.addstr(y, x, t, *args)
    except: pass

def launch_term(cmd):
    if not cmd: return False
    cs = " ".join(shlex.quote(str(c)) for c in cmd)
    if W:
        subprocess.Popen(["start","cmd","/c",cs],shell=True); return True
    t = find_term()
    if t:
        subprocess.Popen([t[0]]+t[1]+[cs],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
        return True
    return False

def do_launch(scr, name, check, cmd):
    h,w = scr.getmaxyx(); mid = h//2
    if not cmd or (len(cmd)==1 and cmd[0] in ("python","python3")):
        scr.clear()
        sa(scr,mid-1,w//2-len(f"> {name}")//2,f"> {name}",curses.color_pair(1)|curses.A_BOLD)
        pn = name.lower().replace(" ","").replace("(","").replace(")","")
        sa(scr,mid+1,w//2-18,f"pip install {pn}  (si aplica)")
        sa(scr,h-2,w//2-15,"Presiona cualquier tecla",curses.color_pair(3)|curses.A_BLINK)
        scr.refresh(); scr.getch(); return
    scr.clear()
    sa(scr,mid-1,w//2-len(f"> Abriendo {name}")//2,f"> Abriendo {name}",curses.color_pair(1)|curses.A_BOLD)
    sa(scr,mid+1,w//2-12,"Nueva terminal",curses.color_pair(2))
    scr.refresh(); time.sleep(0.3)
    if not launch_term(cmd):
        curses.endwin(); subprocess.run(cmd); curses.doupdate()
    else:
        sa(scr,mid+2,w//2-15,"Lanzado, volviendo...",curses.color_pair(2))
        scr.refresh(); time.sleep(0.3)

def main(scr):
    curses.curs_set(0); curses.use_default_colors()
    curses.init_pair(1, curses.COLOR_RED, -1)
    curses.init_pair(2, curses.COLOR_GREEN, -1)
    curses.init_pair(3, curses.COLOR_YELLOW, -1)
    scr.nodelay(1)
    for _ in range(8): scr.clear(); scr.refresh(); time.sleep(0.02)
    scr.nodelay(0)
    h,w = scr.getmaxyx()
    logo = ["██╗  ██╗██╗      █████╗ ██╗   ██╗███╗   ██╗ ██████╗██╗  ██╗███████╗██████╗",
            "██║  ██║██║     ██╔══██╗██║   ██║████╗  ██║██╔════╝██║  ██║██╔════╝██╔══██╗",
            "███████║██║     ███████║██║   ██║██╔██╗ ██║██║     ███████║█████╗  ██████╔╝",
            "██╔══██║██║     ██╔══██║██║   ██║██║╚██╗██║██║     ██╔══██║██╔══╝  ██╔══██╗",
            "██║  ██║███████╗██║  ██║╚██████╔╝██║ ╚████║╚██████╗██║  ██║███████╗██║  ██║"]
    for i in range(6):
        scr.clear()
        for y,l in enumerate(logo):
            sa(scr,h//2-5+y,w//2-36,l[:len(l)//6*(i+1)],curses.color_pair(1)|curses.A_BOLD)
        sa(scr,h//2+1,w//2-10,"AI LAUNCHER PRO  v2.0",curses.color_pair(2)|curses.A_BOLD)
        scr.refresh(); time.sleep(0.05)
    sa(scr,h-2,w//2-15,"Presiona cualquier tecla",curses.color_pair(3)|curses.A_BLINK)
    scr.refresh(); scr.getch()

    idx = 0
    while True:
        scr.clear(); h,w = scr.getmaxyx()
        sw = 24; gap = 3; gx = sw + gap

        sa(scr,0,2,"AI LAUNCHER PRO  v2.0",curses.color_pair(1)|curses.A_BOLD)
        sa(scr,0,w-10,"19 TOOLS",curses.color_pair(2))
        for i in range(w-1): sa(scr,1,i,"═",curses.color_pair(1))

        sy = 2; gi = 0; cc = 0
        for cat, star, items in CATS:
            if sy > h - 5: break
            n = len(items); hh = n + 4
            if sy + hh + 1 > h - 3: break

            sel_box = (cc == idx // 100)  # approximate category selection
            b = curses.color_pair(2) if sel_box else curses.color_pair(1)
            sa(scr,sy,2,f"┌──────────────────────┐",b)
            sa(scr,sy+1,2,f"│  {cat:20s}│",curses.color_pair(1)|curses.A_BOLD)
            sa(scr,sy+2,2,f"│  {star:20s}│",curses.color_pair(3))
            sa(scr,sy+3,2,f"├──────────────────────┤",b)
            for i,(name,check,_) in enumerate(items):
                r = "●" if ready(check) else "○"
                c = curses.color_pair(2) if r else curses.color_pair(3)
                isel = curses.A_REVERSE if gi == idx else 0
                sa(scr,sy+4+i,2,f"│ {r} {name:20s}│",c|isel)
                gi += 1
            sa(scr,sy+4+n,2,"└──────────────────────┘",b)

            cols = 2; bw = 22; bh = 3; gap2 = 2; sx = gx
            for i,(name,check,cmd) in enumerate(items):
                col = i % cols; row = i // cols
                xx = sx + col * (bw + gap2); yy = sy + row * (bh + 1)
                if yy + bh > h - 3: break
                sl = (gi == idx)
                sel = curses.A_REVERSE if sl else 0
                num = gi + 1; rdy = ready(check); dot = "●" if rdy else "○"
                st = "LISTO" if rdy else "FALTA"
                sc = curses.color_pair(2) if rdy else curses.color_pair(3)
                sa(scr,yy,xx,"┌────────────────────┐",sc|sel)
                sa(scr,yy+1,xx,f"│ {num:2d} {name:16s}│",(curses.color_pair(2)|sel))
                sa(scr,yy+2,xx,f"│ {star} {dot} {st} │",sc|sel)

            sy += hh + 1
            cc += 1

        for i in range(w-1): sa(scr,h-3,i,"─",curses.color_pair(1))
        sa(scr,h-2,2,"↑↓ mover  ENTER lanzar  q salir",curses.color_pair(2))
        scr.refresh()

        k = scr.getch()
        if k == curses.KEY_UP and idx > 0: idx -= 1
        elif k == curses.KEY_DOWN and idx < len(ALL) - 1: idx += 1
        elif k == ord('\n'):
            cat, star, (name, check, cmd) = ALL[idx]
            do_launch(scr, name, check, cmd)
        elif k == ord('q'): break

def mw():
    try: curses.wrapper(main)
    except Exception as e:
        print("\n"+"="*50); print(f"ERROR: {type(e).__name__}: {e}")
        print("="*50); input("\nEnter para salir...")
    except KeyboardInterrupt: print("\nSaliste.")
if __name__ == "__main__": mw()
