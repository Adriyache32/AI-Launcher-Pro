#!/usr/bin/env python3
import curses, time, subprocess, os, shutil, shlex, platform, sys, json
import importlib, zipfile, urllib.request
from pathlib import Path

if sys.version_info < (3, 7):
    print("Python 3.7+ required"); sys.exit(1)

HOME = Path.home()
W = os.name == "nt"
NPX = "npx.cmd" if W else "npx"
VERSION = "2.19.v"
GIT_VER_URL = "https://raw.githubusercontent.com/Adriyache32/AI-Launcher-Pro/main/version.txt"
GIT_LAUNCHER_URL = "https://raw.githubusercontent.com/Adriyache32/AI-Launcher-Pro/main/launcher.py"

def _ver_tuple(v):
    return tuple(int(x) for x in v.strip("v").rstrip(".").split(".") if x.isdigit())

def check_version():
    import urllib.request
    try:
        r = urllib.request.urlopen(GIT_VER_URL, timeout=3)
        latest = r.read().decode("utf-8").strip()
        return latest if _ver_tuple(latest) > _ver_tuple(VERSION) else None
    except: return None

def do_update(scr):
    import urllib.request
    h,w = scr.getmaxyx(); m = h//2
    scr.clear()
    sa(scr,m-2,w//2-15,"  Actualizando AI Launcher Pro...",curses.color_pair(3)|curses.A_BOLD)
    sa(scr,m,w//2-12,"Descargando nueva version",curses.color_pair(2))
    scr.refresh()
    try:
        r = urllib.request.urlopen(GIT_LAUNCHER_URL, timeout=10)
        new_code = r.read().decode("utf-8")
        this_file = Path(sys.argv[0]).resolve()
        backup = this_file.with_suffix(".py.bak")
        if backup.exists(): backup.unlink()
        this_file.rename(backup)
        this_file.write_text(new_code)
        scr.clear()
        sa(scr,m-2,w//2-12,"  Actualizacion exitosa!",curses.color_pair(2)|curses.A_BOLD)
        sa(scr,m,w//2-20,"Reinicia el launcher para aplicar cambios",curses.color_pair(3))
        sa(scr,m+2,w//2-15,"Presiona cualquier tecla",curses.color_pair(3)|curses.A_BLINK)
        scr.refresh(); scr.getch()
        return True
    except Exception as e:
        scr.clear()
        sa(scr,m-2,w//2-12,"  Error al actualizar",curses.color_pair(1)|curses.A_BOLD)
        sa(scr,m,w//2-len(str(e))//2,str(e)[:40],curses.color_pair(3))
        sa(scr,m+2,w//2-15,"Presiona cualquier tecla",curses.color_pair(3)|curses.A_BLINK)
        scr.refresh(); scr.getch()
        return False

def detect_specs():
    s = {"os": platform.system().lower(), "arch": platform.machine(),
         "cpu_name":"desconocido","cpu_cores":0,"ram_gb":0,
         "termux": False, "ios": False, "android": False}
    s["termux"] = "com.termux" in os.environ.get("PREFIX","") or bool(os.environ.get("TERMUX_VERSION"))
    try:
        if "iPhone" in platform.platform() or "iPad" in platform.platform():
            s["ios"] = True; s["arch"] = "aarch64"
    except: pass
    try:
        if "android" in platform.platform().lower():
            s["android"] = True
    except: pass
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
        try:
            import winreg
            k=winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE,r"HARDWARE\DESCRIPTION\System\CentralProcessor\0")
            s["cpu_name"]=winreg.QueryValueEx(k,"ProcessorNameString")[0].strip()
            winreg.CloseKey(k)
        except: pass
    if s["os"] == "darwin":
        try:
            s["arch"] = subprocess.check_output(["uname","-m"],text=True).strip()
        except: pass
    return s

def compatible(specs, reqs):
    if "arch" in reqs and specs["arch"] != reqs["arch"]:
        return (False, f"Arq: {specs['arch']} no compatible")
    warns = []
    if reqs.get("ram",0) > 0 and specs["ram_gb"] < reqs["ram"]:
        warns.append(f"RAM min {reqs['ram']}GB")
    if reqs.get("cpu_cores",0) > 0 and specs["cpu_cores"] < reqs["cpu_cores"]:
        warns.append(f"CPU min {reqs['cpu_cores']} nucleos")
    if warns:
        return (True, "⚠ " + ", ".join(warns))
    return (True, "OK")

SP = detect_specs()
RATINGS_FILE = HOME / ".config" / "ai-launcher" / "ratings.json"

def load_ratings():
    try: import json; return json.loads(RATINGS_FILE.read_text())
    except: return {}

def save_ratings(r):
    import json
    RATINGS_FILE.parent.mkdir(parents=True, exist_ok=True)
    RATINGS_FILE.write_text(json.dumps(r))

RATINGS = load_ratings()

CATS = [
    ("TOP TIER", "★★★★★", [
        ("Claude Code",     ["~/.claude","cmd:npx"],          "LIMITADA",  {"ram":8,"cpu_cores":4},   ["programar","estudiar","diario"],       [NPX,"@anthropic-ai/claude-code"],            ["npm install -g @anthropic-ai/claude-code"]),
        ("opencode",        ["cmd:opencode"],                    "GRATIS",    {"ram":0,"cpu_cores":0},   ["programar","estudiar"],               ["opencode"],          ["curl -fsSL https://opencode.ai/install.sh | sh"]),
    ]),
    ("BEST VALUE", "★★★★☆", [
        ("OpenAI",          ["~/.openai","cmd:openai"],       "PAGA",      {"ram":0,"cpu_cores":0},   ["programar","estudiar","diario","general"],  ["openai"],       ["pip install openai"]),
        ("Gemini-CLI",      ["~/.gemini","cmd:gemini-cli"],   "GRATIS",    {"ram":0,"cpu_cores":0},   ["programar","estudiar","diario","general"],  ["gemini-cli"],   ["npm install -g @google/generative-ai"]),
        ("xAI (Grok)",      ["cmd:grok"],                      "LIMITADA",  {"ram":0,"cpu_cores":0},   ["estudiar","diario","general"],         ["grok"],         ["pip install grok"]),
        ("Ollama",          ["~/.ollama","cmd:ollama"],       "GRATIS",    {"ram":8,"cpu_cores":4},   ["programar","estudiar"],               ["ollama","run","llama3.1"],                  ["curl -fsSL https://ollama.com/install.sh | sh"]),
    ]),
    ("SOLID", "★★★☆☆", [
        ("Cline",          ["~/.vscode/extensions/saoudrizwan.claude-dev*","cmd:code"],  "GRATIS",  {"ram":0,"cpu_cores":0},  ["programar"],  ["code","--install-extension","saoudrizwan.claude-dev"],  ["code --install-extension saoudrizwan.claude-dev"]),
        ("GitHub Copilot", ["~/.vscode/extensions/github.copilot*","cmd:gh"],             "PAGA",    {"ram":0,"cpu_cores":0},  ["programar","estudiar"],  ["gh","copilot"],  ["code --install-extension github.copilot"]),
        ("Kilo Code",      ["~/.vscode/extensions/kilocode.kilocode*","cmd:code"],        "GRATIS",  {"ram":0,"cpu_cores":0},  ["programar"],  ["code","--install-extension","kilocode.kilocode"],  ["code --install-extension kilocode.kilocode"]),
        ("Cursor IDE",     ["~/.cursor","cmd:cursor"],        "PAGA",    {"ram":0,"cpu_cores":0},  ["programar"],  ["cursor","."],  ["curl -fsSL https://cursor.sh/install | sh"]),
        ("OpenRouter",     ["cmd:openrouter"],                  "PAGA",    {"ram":0,"cpu_cores":0},  ["programar","general"],  ["openrouter"],  ["npm install -g openrouter"]),
        ("Kiro AI",        ["cmd:kiro"],                        "PAGA",    {"ram":0,"cpu_cores":0},  ["programar"],  ["kiro"],  ["pip install kiro-ai"]),
        ("Vertex AI",      ["~/.config/gcloud","cmd:gcloud"], "PAGA",    {"ram":0,"cpu_cores":0},  ["programar"],  ["gcloud"],  ["pip install google-cloud-aiplatform"]),
    ]),
    ("NICHE", "★★☆☆☆", [
        ("Nvidia NIM",     ["~/.nim","cmd:docker"],           "LIMITADA",  {"ram":16,"cpu_cores":8},  ["programar"],  ["docker"],  ["pip install nvidia-nim"]),
        ("Cloudflare AI",  ["~/.cloudflare","cmd:wrangler"],  "GRATIS",    {"ram":0,"cpu_cores":0},  ["programar"],  ["wrangler"],  ["npm install -g @cloudflare/ai"]),
        ("Qoder",          ["cmd:qoder"],                      "GRATIS",    {"ram":0,"cpu_cores":0},  ["programar"],  ["qoder"],  ["pip install qoder"]),
        ("Antigravity",    ["cmd:antigravity"],                "GRATIS",    {"ram":0,"cpu_cores":0},  ["programar","estudiar","general"],  ["antigravity"],  ["pip install antigravity"]),
        ("BytePlus",       ["cmd:byteplus"],                   "PAGA",      {"ram":0,"cpu_cores":0},  ["programar"],  ["byteplus"],  ["pip install byteplus"]),
    ]),
]

ALL = [(c, s, a) for cat, star, items in CATS for a in items for c, s in [[cat, star]]]

def ready(checks):
    for c in checks:
        if c.startswith("import:"):
            try:
                importlib.import_module(c[7:])
                return True
            except: pass
        elif c.startswith("cmd:"):
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
    if SP.get("termux") or SP.get("ios"): return None
    if SP["os"] == "darwin":
        mac_terms = [("Terminal","bash"),("iTerm2","bash")]
        for app, shell in mac_terms:
            p = f"/Applications/{app}.app"
            if os.path.isdir(p):
                return ("open",["-a",app,"--args",shell,"-c"])
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

def check_pkg_mgrs(install_cmds):
    mgrs = {"pip": shutil.which("pip") or shutil.which("pip3"),
            "npm": shutil.which("npm"),
            "curl": shutil.which("curl"),
            "brew": shutil.which("brew"),
            "apt": shutil.which("apt") if not W else None}
    missing = []
    for c in (install_cmds or []):
        for m in mgrs:
            if c.startswith(m) and not mgrs[m]:
                missing.append(m)
                break
    return missing

PKG_BASE = "https://github.com/Adriyache32/AI-Launcher-Pro/releases/download/packages/"

def detect_package_need():
    if SP.get("ios"):
        return ("iOS", "🍏 iOS (proximamente)", PKG_BASE + f"AI-Launcher-iOS-{VERSION}.zip",
                "iOS detectado. Package para iPhone/iPad en desarrollo.")
    if SP.get("termux"):
        return ("Termux", "📱 Termux setup", PKG_BASE + f"AI-Launcher-Termux-{VERSION}.zip",
                "Package oficial para Termux. Instala dependencias y deja 'open-ai' listo.")
    if W:
        try:
            import importlib as _il
            _il.import_module('curses')
        except:
            return ("Windows", "🪟 Windows + curses", PKG_BASE + f"AI-Launcher-Windows-{VERSION}.zip",
                    "Windows sin curses detectado. El package instala Python y windows-curses automaticamente.")
    if SP["ram_gb"] < 1 or SP["cpu_cores"] < 2:
        return ("Legacy", "🖥️ Old PC / Legacy", PKG_BASE + f"AI-Launcher-Legacy-{VERSION}.zip",
                f"PC con pocos recursos (RAM: {SP['ram_gb']}GB, CPU: {SP['cpu_cores']} nucleos). Package Legacy optimizado.")
    if SP["arch"] in ("armv7l","armv6l","i586","i686"):
        return ("Legacy", "🖥️ Old PC / Legacy", PKG_BASE + f"AI-Launcher-Legacy-{VERSION}.zip",
                f"Arquitectura {SP['arch']} detectada. Package Legacy para hardware antiguo.")
    return None

def download_install_package(scr, url, label):
    h,w = scr.getmaxyx(); m = h//2
    tmp = Path("/tmp") / f"ai-launcher-pkg"
    tmp.mkdir(parents=True, exist_ok=True)
    zip_path = tmp / "package.zip"
    scr.clear()
    sa(scr,m-2,w//2-18,"  Descargando package...",curses.color_pair(3)|curses.A_BOLD)
    sa(scr,m,w//2-20,f"{label}",curses.color_pair(2))
    scr.refresh()
    try:
        urllib.request.urlretrieve(url, zip_path)
        sa(scr,m+1,w//2-15,"Extrayendo...",curses.color_pair(2))
        scr.refresh()
        extract_to = tmp / "extracted"
        if extract_to.exists(): shutil.rmtree(extract_to)
        with zipfile.ZipFile(zip_path) as z:
            z.extractall(extract_to)
        scripts = list(extract_to.glob("install.sh")) + list(extract_to.glob("setup.sh")) + list(extract_to.glob("*.sh"))
        if scripts:
            sa(scr,m+2,w//2-18,"Ejecutando instalador...",curses.color_pair(2))
            scr.refresh()
            shell = "bash" if shutil.which("bash") else "sh"
            r = subprocess.run([shell, str(scripts[0])], cwd=extract_to)
            if r.returncode != 0:
                raise RuntimeError(f"Instalador fallo (codigo {r.returncode})")
        else:
            dst = HOME/".ai-launcher-pkg"
            dst.mkdir(parents=True, exist_ok=True)
            for f in extract_to.iterdir():
                shutil.copy2(f, dst/f.name)
        sa(scr,m+3,w//2-14,"Package instalado!",curses.color_pair(2)|curses.A_BOLD)
        sa(scr,m+5,w//2-15,"Presiona cualquier tecla",curses.color_pair(3)|curses.A_BLINK)
        scr.refresh(); scr.getch()
        return True
    except Exception as e:
        scr.clear()
        sa(scr,m-2,w//2-15,"  Error al descargar",curses.color_pair(1)|curses.A_BOLD)
        sa(scr,m,w//2-len(str(e))//2,str(e)[:50],curses.color_pair(3))
        sa(scr,m+2,w//2-15,"Presiona cualquier tecla",curses.color_pair(3)|curses.A_BLINK)
        scr.refresh(); scr.getch()
        return False

PKG_EXTRAS = []
if SP["os"] == "linux":
    PKG_EXTRAS.append(("🐧 Linux Enhancement", PKG_BASE + f"AI-Launcher-Linux-Enhancement-{VERSION}.zip",
                       "Mejoras opcionales: desktop, auto-completion, aliases, temas, systemd, comandos extra"))
    PKG_EXTRAS.append(("🪟 Windows", PKG_BASE + f"AI-Launcher-Windows-{VERSION}.zip",
                       "Instalador para Windows con Python + curses automatico"))
    PKG_EXTRAS.append(("📱 Termux", PKG_BASE + f"AI-Launcher-Termux-{VERSION}.zip",
                       "Setup para Termux (Android)"))
    PKG_EXTRAS.append(("🖥️ Legacy", PKG_BASE + f"AI-Launcher-Legacy-{VERSION}.zip",
                       "PC viejos, modo texto sin curses"))
    PKG_EXTRAS.append(("🍏 iOS", PKG_BASE + f"AI-Launcher-iOS-{VERSION}.zip",
                       "Package para iPhone/iPad (proximamente)"))

def lt(cmd):
    if not cmd: return False
    s = " ".join(shlex.quote(str(c)) for c in cmd)
    if W: subprocess.Popen(['cmd','/c','start','"AI Launcher Pro"','cmd','/c',s]); return True
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

def info_popup(scr, name, tags, rating, ratings_dict, ready_status, install_cmds):
    h,w = scr.getmaxyx()
    mh = 14; mw = 50
    y = h//2 - mh//2; x = w//2 - mw//2
    win = curses.newwin(mh, mw, y, x)
    win.box()
    win.addstr(1, 2, f" {name} ", curses.A_BOLD)
    tags_str = ", ".join(tags)
    win.addstr(2, 2, f" Tags: {tags_str}")
    sep = "─"*(mw-6)
    win.addstr(3, 2, f" {sep}")
    stars = "★"*rating + "☆"*(5-rating) if rating > 0 else "☆☆☆☆☆"
    win.addstr(4, 2, f" Rating: {stars}  ({rating}/5)")
    win.addstr(5, 2, f" {sep}")
    if not ready_status and install_cmds:
        win.addstr(6, 2, " Instalar:", curses.A_BOLD)
        for j, c in enumerate(install_cmds):
            if 7+j < mh-3:
                win.addstr(7+j, 4, c[:mw-8])
    else:
        win.addstr(6, 2, " 1-5: calificar")
        win.addstr(7, 2, " 0: quitar rating")
    win.addstr(mh-3, 2, " ENTER: lanzar  q: cerrar")
    win.refresh()
    new_rating = rating
    while True:
        k = win.getch()
        if k in (ord('q'), 27):
            del win; scr.touchwin(scr); scr.refresh()
            return (new_rating, "close")
        if k == ord('\n'):
            del win; scr.touchwin(scr); scr.refresh()
            return (new_rating, "launch")
        if ord('0') <= k <= ord('5'):
            new_rating = k - ord('0')
            ratings_dict[name] = new_rating
            save_ratings(ratings_dict)
            stars = "★"*new_rating + "☆"*(5-new_rating) if new_rating > 0 else "☆☆☆☆☆"
            win.addstr(4, 2, f" Rating: {stars}  ({new_rating}/5)")
            win.refresh()

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
        curses.endwin(); subprocess.run(cmd)
        try: curses.reset_prog_mode(); scr.refresh()
        except: pass
    else:
        sa(scr,m+2,w//2-15,"Lanzado",curses.color_pair(2))
        scr.refresh(); time.sleep(0.5)

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
    logo = ["┌─┐┌─┐  ┌─┐┌─┐┬ ┬┌─┐┌┐┌┌─┐┬─┐┌─┐┌─┐",
            "│ ┬│ │  ├─┤│ ││ │├─┤│││├┤ ├┬┘├┤ └─┐",
            "└─┘└─┘  ┴ ┴└─┘└─┘┴ ┴┘└┘└─┘┴└─└─┘└─┘"]
    for i in range(4):
        scr.clear()
        for y,l in enumerate(logo):
            sa(scr,h//2-2+y,w//2-25,l[:len(l)//4*(i+1)],curses.color_pair(1)|curses.A_BOLD)
        t = "AI LAUNCHER PRO"
        sa(scr,h//2+2,w//2-len(t)//2,t,curses.color_pair(2)|curses.A_BOLD)
        sa(scr,h//2+2,w//2+len(t)//2+2,VERSION,curses.color_pair(3))
        scr.refresh(); time.sleep(0.05)
    sa(scr,h//2+3,w//2-4,f"{len(ALL)} TOOLS",curses.color_pair(3))
    sa(scr,h-2,w//2-15,"Presiona cualquier tecla",curses.color_pair(3)|curses.A_BLINK)
    scr.refresh(); scr.getch()

    update_avail = check_version()
    pkg_need = detect_package_need()
    idx = 0; scroll = 0
    bw = 26; stride = bw + 1  # card box width, step between cols
    while True:
        scr.clear(); h,w = scr.getmaxyx()
        R = curses.color_pair(1); G = curses.color_pair(2); Y = curses.color_pair(3); B = curses.A_BOLD
        topy = 3; boty = h-4; vh = boty - topy + 1

        for i in range(w): sa(scr,0,i,"─",R)
        tit = f"  🤖 AI LAUNCHER PRO  {VERSION}  "
        sa(scr,1,(w-len(tit))//2,tit,R|B)
        sa(scr,1,2,f"⚡ {len(ALL)} TOOLS",G)
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
                for i0, (name, check, _, _, _, _, _) in enumerate(items):
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
                    sa(scr,sy2+2,2,f"│{'─'*lw}│",R)
                if sy2-1 >= topy and sy2-1 <= boty and sy2 > topy:
                    sa(scr,sy2-1,2,"─"*lw,R)
            else:
                gi += n
            sy += bh + 1

        # cards
        gi = 0
        for _,_,items in CATS:
            for i, (name, check, price, reqs, tags, cmd, _) in enumerate(items):
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
                if compat_ok and compat_reason != "OK":
                    compat_icon = "⚠"; compat_cp = Y
                elif compat_ok:
                    compat_icon = "✓"; compat_cp = G
                else:
                    compat_icon = "✗"; compat_cp = R
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
        pkg_tag = f" [p] {pkg_need[1]}" if pkg_need else ""
        ext_tag = " [e] extras" if PKG_EXTRAS else ""
        upd = f" ▲ {update_avail}" if update_avail else ""
        sa(scr,h-2,2,f"↑↓ ENTER i:info u:update{pkg_tag}{ext_tag} q salir  {VERSION}{upd}",G)
        for i in range(w): sa(scr,h-1,i,"═",R)
        scr.refresh()
        k = scr.getch()
        if k == curses.KEY_UP and idx > 0: idx -= 1
        elif k == curses.KEY_DOWN and idx < len(ALL)-1: idx += 1
        elif k == ord('i'):
            cat, star, (name, check, price, reqs, tags, cmd, install_cmds) = ALL[idx]
            old = RATINGS.get(name, 0)
            new_r, action = info_popup(scr, name, tags, old, RATINGS, ready(check), install_cmds)
            if action == "launch":
                cm, reason = compatible(SP, reqs)
                if not cm:
                    popup(scr, f"{name}\n{reason}")
                elif not ready(check):
                    lines = [f"{name} - Instalacion:"]
                    for c in (install_cmds or ["pip install "+name.lower().replace(" ","")]):
                        lines.append(f"  $ {c}")
                    missing = check_pkg_mgrs(install_cmds)
                    if missing:
                        lines.append("")
                        lines.append(f"⚠ Faltan: {', '.join(missing)}")
                    popup(scr, "\n".join(lines))
                else:
                    dl(scr, name, check, cmd)
        elif k == ord('\n'):
            cat, star, (name, check, price, reqs, tags, cmd, install_cmds) = ALL[idx]
            cm, reason = compatible(SP, reqs)
            if not cm:
                popup(scr, f"{name}\n{reason}")
            elif not ready(check):
                lines = [f"{name} - Instalacion:"]
                for c in (install_cmds or ["pip install "+name.lower().replace(" ","")]):
                    lines.append(f"  $ {c}")
                missing = check_pkg_mgrs(install_cmds)
                if missing:
                    lines.append("")
                    lines.append(f"⚠ Faltan: {', '.join(missing)}")
                popup(scr, "\n".join(lines))
            else:
                dl(scr, name, check, cmd)
        elif k == ord('p') and pkg_need:
            _, label, url, reason = pkg_need
            lines = [f"📦 Package recomendado: {label}"]
            lines.append("")
            lines.append(f" {reason}")
            lines.append("")
            lines.append(f" {url}")
            lines.append("")
            lines.append(" d: descargar e instalar")
            lines.append(" q: cerrar")
            h2,w2 = scr.getmaxyx()
            mh = 4 + len(lines); mw = 60
            y2 = h2//2 - mh//2; x2 = w2//2 - mw//2
            win = curses.newwin(mh, mw, y2, x2)
            win.box()
            for i, txt in enumerate(lines):
                if 1+i < mh-1:
                    win.addstr(1+i, 2, txt[:mw-4])
            win.refresh()
            while True:
                k2 = win.getch()
                if k2 == ord('d'):
                    del win; scr.touchwin(scr); scr.refresh()
                    download_install_package(scr, url, label)
                    break
                if k2 in (ord('q'), 27):
                    break
            del win; scr.touchwin(scr); scr.refresh()
        elif k == ord('e') and PKG_EXTRAS:
            lines = ["📦 Packages opcionales:"]
            for i, (label, url, desc) in enumerate(PKG_EXTRAS):
                lines.append("")
                lines.append(f" {i+1}. {label}")
                lines.append(f"    {desc}")
                lines.append(f"    {url}")
            lines.append("")
            lines.append(" [1-5] descargar   q: cerrar")
            h2,w2 = scr.getmaxyx()
            mh = 4 + len(lines); mw = 64
            y2 = h2//2 - mh//2; x2 = w2//2 - mw//2
            win = curses.newwin(mh, mw, y2, x2)
            win.box()
            for i, txt in enumerate(lines):
                if 1+i < mh-1:
                    win.addstr(1+i, 2, txt[:mw-4])
            win.refresh()
            while True:
                k2 = win.getch()
                if ord('1') <= k2 <= ord('9'):
                    n = k2 - ord('1')
                    if n < len(PKG_EXTRAS):
                        elabel, eurl, edesc = PKG_EXTRAS[n]
                        del win; scr.touchwin(scr); scr.refresh()
                        download_install_package(scr, eurl, elabel)
                        break
                if k2 in (ord('q'), 27):
                    break
            del win; scr.touchwin(scr); scr.refresh()
        elif k == ord('u'):
            if do_update(scr): return
        elif k == ord('q'): break

def console_mode():
    plat_icon = {"linux":"🐧","darwin":"🍎","windows":"🪟"}
    icon = plat_icon.get(SP["os"],"💻")
    print(f"\n  {icon} AI LAUNCHER PRO {VERSION} — Modo texto")
    print(f"  {'='*40}")
    print(f"  {icon} OS: {platform.system()} | Arch: {SP['arch']} | CPU: {SP['cpu_name']} | RAM: {SP['ram_gb']}GB")
    if SP["termux"]:  print("  📱 Terminal: Termux")
    if SP["ios"]:     print("  🍏 Terminal: iOS")
    if SP["android"]: print("  🤖 Terminal: Android")
    if W:             print("  🪟 Terminal: Windows")
    print(f"  {'='*40}\n")
    items = []
    for cat, star, group in CATS:
        for item in group:
            name, check, price, reqs, tags, cmd, install_cmds = item
            rdy = "●" if ready(check) else "○"
            items.append((cat, star, name, rdy, install_cmds, cmd, check, price, reqs, tags))
    while True:
        print(f"\n  {'#':>2} {'Status':<7} {'IA':<22} {'Categoria':<14}")
        print(f"  {'-'*50}")
        for i, (cat, star, name, rdy, _, _, _, _, _, _) in enumerate(items):
            print(f"  {i+1:>2}  {rdy:<6} {name:<22} {cat:<14}")
        print(f"\n  [1-{len(items)}] info/instalar  [q] salir  ", end="")
        try:
            inp = input().strip()
        except (EOFError, KeyboardInterrupt):
            break
        if inp.lower() in ("q","quit","exit",""): break
        try:
            n = int(inp)-1
            if n < 0 or n >= len(items): continue
            cat, star, name, rdy, install_cmds, cmd, check, price, reqs, tags = items[n]
            cm, reason = compatible(SP, reqs)
            if not cm:
                input(f"\n  {name}: {reason}\n  Enter...")
            elif not ready(check):
                print(f"\n  {name} — Instalacion:")
                for c in (install_cmds or ["pip install "+name.lower().replace(" ","")]):
                    print(f"    $ {c}")
                input("  Enter...")
            else:
                print(f"\n  Lanzando {name}...")
                subprocess.run(cmd)
                input("\n  Enter para volver...")
        except (ValueError, IndexError): pass

def mw():
    try:
        if W:
            try:
                import importlib as _il
                _il.import_module('curses')
            except:
                console_mode(); return
        curses.wrapper(main)
    except Exception as e:
        en = type(e).__name__.lower()
        if "curses" in en or "no module" in str(e).lower():
            console_mode()
        else:
            print("\n"+"="*50); print(f"ERROR: {type(e).__name__}: {e}")
            print("="*50); input("\nEnter para salir...")
    except KeyboardInterrupt: print("\nSaliste.")
if __name__ == "__main__": mw()
