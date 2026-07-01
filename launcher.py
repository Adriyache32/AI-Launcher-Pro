#!/usr/bin/env python3
import curses, time, subprocess, os, shutil, shlex, platform
from pathlib import Path

HOME = Path.home()
W = os.name == "nt"
NPX = "npx.cmd" if W else "npx"
VERSION = "2.12.v"
GIT_VER_URL = "https://raw.githubusercontent.com/Adriyache32/AI-Launcher-Pro/main/version.txt"

def check_version():
    import urllib.request
    try:
        r = urllib.request.urlopen(GIT_VER_URL, timeout=3)
        latest = r.read().decode("utf-8").strip()
        return latest if latest != VERSION else None
    except: return None

def detect_specs():
    s = {"os": platform.system().lower(), "arch": platform.machine(), "cpu_name":"desconocido","cpu_cores":0,"ram_gb":0}
    try:
        c = Path("/proc/cpuinfo").read_text().split("\n")
        for l in c:
            if "model name" in l: s["cpu_name"]=l.split(":")[1].strip(); break
        s["cpu_cores"] = sum(1 for l in c if "processor" in l)
    except: pass
    try:
        for l in Path("/proc/meminfo").read_text().split("\n"):
            if "MemTotal" in l: s["ram_gb"]=int(l.split()[1])//1048576; break
    except: pass
    if W:
        import winreg
        try:
            k=winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE,r"HARDWARE\DESCRIPTION\System\CentralProcessor\0")
            s["cpu_name"]=winreg.QueryValueEx(k,"ProcessorNameString")[0].strip()
            winreg.CloseKey(k)
        except: pass
    return s

def compatible(specs, reqs):
    if specs["arch"] != "x86_64" and reqs.get("arch","x86_64")=="x86_64":
        return (False, f"Arq: {specs['arch']} no compatible")
    if reqs.get("ram",0) > 0 and specs["ram_gb"] < reqs["ram"]:
        return (False, f"RAM: {specs['ram_gb']}GB < {reqs['ram']}GB")
    if reqs.get("cpu_cores",0) > 0 and specs["cpu_cores"] < reqs["cpu_cores"]:
        return (False, f"CPU: {specs['cpu_cores']} nucleos < {reqs['cpu_cores']}")
    return (True, "OK")

SP = detect_specs()

CATS = [
    ("TOP TIER", "★★★★★", [
        ("Claude Code",     ["~/.claude","cmd:npx"],          "LIMITADA",  {"ram":8,"cpu_cores":4},   [NPX,"@anthropic-ai/claude-code"]),
        ("opencode",        ["~/.opencode"],                   "GRATIS",    {"ram":0,"cpu_cores":0},   [str(HOME/".opencode/bin/opencode")]),
    ]),
    ("BEST VALUE", "★★★★☆", [
        ("OpenAI",          ["~/.openai","cmd:openai"],       "PAGA",      {"ram":0,"cpu_cores":0},   ["openai"]),
        ("Gemini-CLI",      ["~/.gemini","cmd:gemini-cli"],   "GRATIS",    {"ram":0,"cpu_cores":0},   ["gemini-cli"]),
        ("xAI (Grok)",      ["cmd:grok"],                      "LIMITADA",  {"ram":0,"cpu_cores":0},   ["grok"]),
        ("Ollama",          ["~/.ollama","cmd:ollama"],       "GRATIS",    {"ram":8,"cpu_cores":4},   ["ollama","run","llama3.1"]),
    ]),
    ("SOLID", "★★★☆☆", [
        ("Cline",          ["~/.vscode/extensions/saoudrizwan.claude-dev*","cmd:code"],  "GRATIS",  {"ram":0,"cpu_cores":0},  ["code","--install-extension","saoudrizwan.claude-dev"]),
        ("GitHub Copilot", ["~/.vscode/extensions/github.copilot*","cmd:gh"],             "PAGA",    {"ram":0,"cpu_cores":0},  ["gh","copilot"]),
        ("Kilo Code",      ["~/.vscode/extensions/kilocode.kilocode*","cmd:code"],        "GRATIS",  {"ram":0,"cpu_cores":0},  ["code","--install-extension","kilocode.kilocode"]),
        ("Cursor IDE",     ["~/.cursor","cmd:cursor"],        "PAGA",    {"ram":0,"cpu_cores":0},  ["cursor","."]),
        ("OpenRouter",     ["cmd:openrouter"],                  "PAGA",    {"ram":0,"cpu_cores":0},  ["openrouter"]),
        ("Kiro AI",        ["cmd:kiro"],                        "PAGA",    {"ram":0,"cpu_cores":0},  ["kiro"]),
        ("Vertex AI",      ["~/.config/gcloud","cmd:gcloud"], "PAGA",    {"ram":0,"cpu_cores":0},  ["gcloud"]),
    ]),
    ("NICHE", "★★☆☆☆", [
        ("Nvidia NIM",     ["~/.nim","cmd:docker"],           "LIMITADA",  {"ram":16,"cpu_cores":8},  ["docker"]),
        ("Cloudflare AI",  ["~/.cloudflare","cmd:wrangler"],  "GRATIS",    {"ram":0,"cpu_cores":0},  ["wrangler"]),
        ("Qoder",          ["cmd:qoder"],                      "GRATIS",    {"ram":0,"cpu_cores":0},  ["qoder"]),
        ("Antigravity",    ["cmd:antigravity"],                "GRATIS",    {"ram":0,"cpu_cores":0},  ["antigravity"]),
        ("BytePlus",       ["cmd:byteplus"],                   "PAGA",      {"ram":0,"cpu_cores":0},  ["byteplus"]),
    ]),
]

ALL = [(c, s, a) for cat, star, items in CATS for a in items for c, s in [[cat, star]]]

def ready(checks):
    for c in checks:
        if c.startswith("cmd:"):
            if shutil.which(c[4:]) is not None: return True
        elif "*" in c:
            p = Path(c).expanduser()
            try:
                for _ in p.parent.glob(p.name): return True
            except: pass
        else:
            if Path(c).expanduser().exists(): return True
    return False

def find_term():
    if W: return None
    if "com.termux" in os.environ.get("PREFIX","") or os.environ.get("TERMUX_VERSION"):
        return ("sh", ["-c"])
    terms = [("x-terminal-emulator",["-e"]),("gnome-terminal",["--","bash","-c"]),
             ("konsole",["--hold","-e"]),("xfce4-terminal",["-e"]),("lxterminal",["-e"]),
             ("urxvt",["-e"]),("xterm",["-e"]),("alacritty",["-e"]),("kitty",["-e"]),
             ("foot",["-e"]),("wezterm",["-e"])]
    for e, f in terms:
        if shutil.which(e): return (e, f)
    return None

def sa(scr, y, x, t, *a):
    try:
        my, mx = scr.getmaxyx()
        if y<0 or y>=my or x<0 or x>=mx: return
        if x+len(t)>mx: t = t[:mx-x]
        if t: scr.addstr(y, x, t, *a)
    except: pass

def lt(cmd):
    if not cmd: return False
    s = " ".join(shlex.quote(str(c)) for c in cmd)
    if W: subprocess.Popen(["start","cmd","/c",s],shell=True); return True
    t = find_term()
    if t: subprocess.Popen([t[0]]+t[1]+[s],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL); return True
    return False

def popup(scr, msg):
    h,w = scr.getmaxyx()
    mh = 7; mw = 52
    y = h//2 - mh//2; x = w//2 - mw//2
    win = curses.newwin(mh, mw, y, x)
    win.box()
    win.addstr(1,2,"⚠  AI Launcher Pro",curses.A_BOLD)
    for i, m in enumerate(msg.split("\n")):
        win.addstr(2+i, 2, m[:mw-4])
    win.addstr(mh-2, 2, "Presiona cualquier tecla", curses.A_BLINK)
    win.refresh()
    scr.getch()
    del win
    scr.touchwin(scr)
    scr.refresh()

def dl(scr, name, check, cmd):
    h,w = scr.getmaxyx(); m = h//2
    if not cmd or (len(cmd)==1 and cmd[0] in ("python","python3")):
        scr.clear()
        sa(scr,m-1,w//2-len(f"> {name}")//2,f"> {name}",curses.color_pair(1)|curses.A_BOLD)
        pn = name.lower().replace(" ","").replace("(","").replace(")","")
        sa(scr,m+1,w//2-18,f"pip install {pn}") if 1 else None
        sa(scr,h-2,w//2-15,"Presiona cualquier tecla",curses.color_pair(3)|curses.A_BLINK)
        scr.refresh(); scr.getch(); return
    scr.clear()
    sa(scr,m-1,w//2-len(f"> Abriendo {name}")//2,f"> Abriendo {name}",curses.color_pair(1)|curses.A_BOLD)
    sa(scr,m+1,w//2-12,"Nueva terminal",curses.color_pair(2))
    scr.refresh(); time.sleep(0.3)
    if not lt(cmd):
        curses.endwin(); subprocess.run(cmd); curses.doupdate()
    else:
        sa(scr,m+2,w//2-15,"Lanzado",curses.color_pair(2))
        scr.refresh(); time.sleep(0.3)

def main(scr):
    curses.curs_set(0); curses.use_default_colors()
    curses.init_pair(1, curses.COLOR_RED, -1)
    curses.init_pair(2, curses.COLOR_GREEN, -1)
    curses.init_pair(3, curses.COLOR_YELLOW, -1)
    curses.init_pair(4, curses.COLOR_CYAN, -1)
    curses.init_pair(5, curses.COLOR_MAGENTA, -1)
    curses.init_pair(6, curses.COLOR_BLUE, -1)
    curses.init_pair(7, curses.COLOR_WHITE, -1)
    curses.init_pair(10, curses.COLOR_BLACK, curses.COLOR_RED)
    curses.init_pair(11, curses.COLOR_BLACK, curses.COLOR_GREEN)
    curses.init_pair(12, curses.COLOR_BLACK, curses.COLOR_YELLOW)

    TC = [3,5, 2,6,7,4, 1,3,5,2,6,5,6, 2,3,4,7,2]
    PRICE_PAIR = {"PAGA":10, "GRATIS":11, "LIMITADA":12}
    scr.nodelay(1)
    for _ in range(6): scr.clear(); scr.refresh(); time.sleep(0.02)
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
        t = "AI LAUNCHER PRO"
        sa(scr,h//2+1,w//2-len(t)//2,t,curses.color_pair(2)|curses.A_BOLD)
        sa(scr,h//2+1,w//2+len(t)//2+2,VERSION,curses.color_pair(3))
        scr.refresh(); time.sleep(0.05)
    sa(scr,h//2+2,w//2-4,f"{len(ALL)} TOOLS",curses.color_pair(3))
    sa(scr,h-2,w//2-15,"Presiona cualquier tecla",curses.color_pair(3)|curses.A_BLINK)
    scr.refresh(); scr.getch()

    update_avail = check_version()
    idx = 0; scroll = 0
    bw = 26; stride = bw + 1  # card box width, step between cols
    while True:
        scr.clear(); h,w = scr.getmaxyx()
        R = curses.color_pair(1); G = curses.color_pair(2); Y = curses.color_pair(3); B = curses.A_BOLD
        topy = 3; boty = h-4; vh = boty - topy + 1

        for i in range(w): sa(scr,0,i,"─",R)
        tit = f"  AI LAUNCHER PRO  {VERSION}  "
        sa(scr,1,(w-len(tit))//2,tit,R|B)
        sa(scr,1,2,f"◆ {len(ALL)} TOOLS",G)
        for i in range(w): sa(scr,2,i,"─",R)
        lw = 32; sx = lw+3
        for y in range(topy, boty+1): sa(scr,y,sx,"│",R)
        for y in range(topy, boty+1): sa(scr,y,w-1,"│",R)
        sa(scr,topy,sx+1,"─"*(w-sx-3),R)
        sa(scr,boty,sx+1,"─"*(w-sx-3),R)

        card_y = {}
        vy = topy; gi = 0
        for _,_,items in CATS:
            rows = (len(items)+1)//2
            for i, item in enumerate(items):
                card_y[gi] = vy + (i//2)*6
                gi += 1
            vy += rows*6 + 1

        total_h = vy - topy
        sel_vy = card_y.get(idx, topy)
        if sel_vy - scroll < topy: scroll = sel_vy - topy
        if sel_vy - scroll + 5 > boty: scroll = sel_vy + 5 - boty
        scroll = max(0, min(scroll, total_h - vh)) if total_h > vh else 0

        # sidebar
        sy = topy - scroll; gi = 0
        for cat, star, items in CATS:
            n = len(items); bh = n + 4
            vy2 = sy; sy2 = sy
            if sy2 + bh > topy - 1:
                for i0, (name, check, _, _, _) in enumerate(items):
                    yy = sy2 + 3 + i0
                    if yy < topy or yy > boty: continue
                    r = "●" if ready(check) else "○"
                    sl = curses.A_REVERSE if gi == idx else 0
                    cc = curses.color_pair(TC[gi])
                    rc = cc if ready(check) else Y
                    num = gi + 1
                    txt = f"│ {num:2d} {r} {name:23s}│"
                    sa(scr,yy,2,txt,rc|sl)
                    gi += 1
                if sy2 >= topy and sy2 <= boty:
                    sa(scr,sy2,2,f"│  {cat:28s}│",curses.color_pair(TC[gi])|B)
                if sy2+1 >= topy and sy2+1 <= boty:
                    sa(scr,sy2+1,2,f"│  {star:28s}│",Y)
                if sy2+2 >= topy and sy2+2 <= boty:
                    sa(scr,sy2+2,2,f"│{'─'*28}│",R)
                if sy2-1 >= topy and sy2-1 <= boty and sy2 > topy:
                    sa(scr,sy2-1,2,"─"*lw,R)
            else:
                gi += n
            sy += bh + 1

        # cards
        gi = 0
        for _,_,items in CATS:
            for i, (name, check, price, reqs, cmd) in enumerate(items):
                col = i%2
                vy2 = card_y[gi]
                yy = vy2 - scroll
                if yy < topy - 5 or yy > boty:
                    gi += 1; continue
                sl = curses.A_REVERSE if gi == idx else 0
                cc = curses.color_pair(TC[gi])
                cx = sx + 3 + col*stride
                num = gi+1; rdy = ready(check)
                dot = "●" if rdy else "○"; st = "LISTO" if rdy else "FALTA"
                cm = compatible(SP, reqs)
                compat_ok, compat_reason = cm
                compat_icon = "✓" if compat_ok else "✗"
                compat_cp = G if compat_ok else R
                pp = PRICE_PAIR.get(price, 10)
                price_label = f" {price} "
                plen = len(price_label)
                cpu_txt = SP["cpu_name"] if SP["cpu_name"]!="desconocido" else SP["arch"]
                n2 = name[:bw-6]
                cpu_left = bw-2-plen

                # build each line as exact bw=26 string
                top = "┌"+"─"*(bw-2)+"┐"
                L1 = f"│ {num:2d} {n2:{bw-6}s}│"              # line 1
                L2badge = f"│{price_label}"                     # badge portion
                L2rest = f"{cpu_txt[:cpu_left]:{cpu_left}s}│"   # cpu portion
                L3 = f"│ {star} {dot} {st} │".ljust(bw-1)+"│"  # stars
                l4txt = f"CPU:{compat_icon} {compat_reason[:12]}"
                L4 = f"│{l4txt:^{bw-2}s}│"                     # compat
                L5 = "└"+"─"*(bw-2)+"┘"

                sa(scr,yy,cx,top,cc|sl)
                sa(scr,yy+1,cx,L1,cc|sl)
                sa(scr,yy+2,cx,L2badge,curses.color_pair(pp)|sl)
                sa(scr,yy+2,cx+plen+1,L2rest,cc|sl)
                sa(scr,yy+3,cx,L3,cc|sl)
                sa(scr,yy+4,cx,L4,compat_cp|sl)
                sa(scr,yy+5,cx,L5,cc|sl)
                gi += 1

        for i in range(w): sa(scr,h-3,i,"═",R)
        upd = f"  ▲ {update_avail}" if update_avail else ""
        sa(scr,h-2,2,f"↑↓ mover  ENTER lanzar  q salir  {VERSION}{upd}",G)
        for i in range(w): sa(scr,h-1,i,"═",R)
        scr.refresh()
        k = scr.getch()
        if k == curses.KEY_UP and idx > 0: idx -= 1
        elif k == curses.KEY_DOWN and idx < len(ALL)-1: idx += 1
        elif k == ord('\n'):
            cat, star, (name, check, price, reqs, cmd) = ALL[idx]
            cm, reason = compatible(SP, reqs)
            if not cm:
                popup(scr, f"{name}\n{reason}\nTu PC no cumple los requisitos minimos")
            else:
                dl(scr, name, check, cmd)
        elif k == ord('q'): break

def mw():
    try: curses.wrapper(main)
    except Exception as e:
        print("\n"+"="*50); print(f"ERROR: {type(e).__name__}: {e}")
        print("="*50); input("\nEnter para salir...")
    except KeyboardInterrupt: print("\nSaliste.")
if __name__ == "__main__": mw()
