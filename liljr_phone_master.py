#!/usr/bin/env python3
"""
liljr_phone_master.py — Your phone IS LilJR.
Full-screen immersive phone interface. Launch apps, control everything, OMNI brain.
Not an app. The phone itself.
"""

import os, sys, json, time, subprocess, urllib.request

HOME = os.path.expanduser("~")
REPO = os.path.join(HOME, "liljr-autonomous")
API = "http://localhost:7777/api/omni"

def clear():
    os.system("clear")

def header():
    print("\033[38;5;51m\033[1m")
    print("  ╔═══════════════════════════════════════════════╗")
    print("  ║                                               ║")
    print("  ║          🧬 LILJR — YOUR PHONE IS ALIVE       ║")
    print("  ║                                               ║")
    print("  ╚═══════════════════════════════════════════════╝")
    print("\033[0m")

def get_status():
    try:
        req = urllib.request.Request(f"{API}/status", method="GET")
        req.add_header("Cache-Control", "no-store")
        with urllib.request.urlopen(req, timeout=2) as r:
            return json.loads(r.read().decode())
    except:
        return None

def send_cmd(cmd):
    try:
        data = json.dumps({"command": cmd}).encode()
        req = urllib.request.Request(f"{API}/command", data=data, method="POST")
        req.add_header("Content-Type", "application/json")
        with urllib.request.urlopen(req, timeout=5) as r:
            return json.loads(r.read().decode())
    except Exception as e:
        return {"message": f"OMNI: {e}"}

def launch_app(pkg):
    """Launch any Android app by package name"""
    try:
        subprocess.run(["am", "start", "-n", pkg], capture_output=True, timeout=5)
        return f"📱 Opened {pkg.split('/')[-1]}"
    except:
        return f"⚠️ Couldn't open {pkg}"

def phone_action(action):
    """Execute phone-level actions"""
    if action == "camera":
        return launch_app("com.android.camera/.Camera")
    elif action == "chrome":
        return launch_app("com.android.chrome/com.google.android.apps.chrome.Main")
    elif action == "snapchat":
        return launch_app("com.snapchat.android/.LandingPageActivity")
    elif action == "phone":
        return launch_app("com.android.dialer/.main.impl.MainActivity")
    elif action == "messages":
        return launch_app("com.google.android.apps.messaging/.ui.ConversationListActivity")
    elif action == "settings":
        return launch_app("com.android.settings/.Settings")
    elif action == "gallery":
        return launch_app("com.google.android.apps.photos/.home.HomeActivity")
    elif action == "playstore":
        return launch_app("com.android.vending/.AssetBrowserActivity")
    elif action == "wifi":
        subprocess.run(["am", "start", "-a", "android.settings.WIFI_SETTINGS"], capture_output=True)
        return "📶 Opened WiFi settings"
    elif action == "bluetooth":
        subprocess.run(["am", "start", "-a", "android.settings.BLUETOOTH_SETTINGS"], capture_output=True)
        return "🔵 Opened Bluetooth settings"
    elif action == "brightness":
        return "☀️ Use volume keys or Settings → Display"
    elif action == "screenshot":
        try:
            ts = int(time.time())
            path = f"/sdcard/Pictures/liljr_screenshot_{ts}.png"
            subprocess.run(["screencap", "-p", path], capture_output=True, timeout=5)
            return f"📸 Screenshot saved: {path}"
        except:
            return "⚠️ Screenshot failed (need permission)"
    elif action == "photo":
        try:
            ts = int(time.time())
            path = f"/sdcard/DCIM/liljr_photo_{ts}.jpg"
            subprocess.run(["termux-camera-photo", "-c", "0", path], capture_output=True, timeout=10)
            return f"📷 Photo saved: {path}"
        except:
            return "⚠️ Camera failed"
    elif action == "torch":
        try:
            subprocess.run(["termux-torch", "on"], capture_output=True, timeout=3)
            return "🔦 Flashlight ON (say 'torch off' to turn off)"
        except:
            return "⚠️ Torch not available"
    elif action == "vibrate":
        try:
            subprocess.run(["termux-vibrate"], capture_output=True, timeout=2)
            return "📳 Bzzzt."
        except:
            return "⚠️ Vibrate not available"
    elif action == "battery":
        try:
            with open("/sys/class/power_supply/battery/capacity") as f:
                pct = f.read().strip()
            with open("/sys/class/power_supply/battery/status") as f:
                status = f.read().strip()
            return f"🔋 Battery: {pct}% ({status})"
        except:
            return "⚠️ Can't read battery"
    elif action == "storage":
        try:
            r = subprocess.run(["df", "-h", "/data"], capture_output=True, text=True, timeout=3)
            lines = r.stdout.strip().split("\n")
            if len(lines) > 1:
                parts = lines[1].split()
                return f"💾 Storage: {parts[2]} used / {parts[1]} total"
        except:
            pass
        return "⚠️ Storage check failed"
    elif action == "network":
        try:
            r = subprocess.run(["termux-wifi-scaninfo"], capture_output=True, text=True, timeout=5)
            nets = r.stdout.strip().split("\n") if r.stdout else []
            return f"📡 WiFi networks: {len(nets)} found"
        except:
            return "📡 WiFi scanning not available"
    return "❓ Unknown phone action"

def draw_home(status):
    clear()
    header()
    
    if status:
        cash = status.get("cash", 0)
        positions = status.get("positions", {})
        stealth = status.get("stealth", False)
        vpn = status.get("vpn", False)
        mesh = status.get("mesh", False)
        camera = status.get("camera", False)
        threat = status.get("threat_level", 0)
        
        print(f"\033[38;5;84m  💰 ${cash:,.0f}\033[0m    \033[38;5;250m{len(positions)} positions\033[0m")
        print()
        ind = []
        ind.append("\033[38;5;84m● STEALTH\033[0m" if stealth else "\033[38;5;240m○ STEALTH\033[0m")
        ind.append("\033[38;5;84m● VPN\033[0m" if vpn else "\033[38;5;240m○ VPN\033[0m")
        ind.append("\033[38;5;84m● MESH\033[0m" if mesh else "\033[38;5;240m○ MESH\033[0m")
        ind.append("\033[38;5;84m● CAM\033[0m" if camera else "\033[38;5;240m○ CAM\033[0m")
        print("  " + "  ".join(ind))
        print()
    else:
        print("\033[38;5;196m  ⚠️  OMNI brain offline. Start: python3 liljr_v90_omni.py --server\033[0m")
        print()
    
    print("\033[38;5;51m  ─────────── YOUR PHONE IS LILJR ───────────\033[0m")
    print()
    print("  \033[38;5;51mA\033[0m 📱 APPS      Launch any app")
    print("  \033[38;5;51mP\033[0m 📞 PHONE     Calls, texts, camera")
    print("  \033[38;5;51mM\033[0m 💰 MONEY     Trade, portfolio")
    print("  \033[38;5;51mS\033[0m 🛡️ SECURITY  Stealth, VPN, lockdown")
    print("  \033[38;5;51mR\033[0m 🔬 RESEARCH  Quantum, nuclear, law")
    print("  \033[38;5;51mL\033[0m ⚖️ LEGAL     Defense, contracts")
    print("  \033[38;5;51mB\033[0m 😂 BUDDY     Talk to your best friend")
    print("  \033[38;5;51mV\033[0m 🎤 VOICE     Hands-free mode")
    print("  \033[38;5;51mC\033[0m 💬 CUSTOM    Type anything")
    print("  \033[38;5;51mQ\033[0m 👋 QUIT      Exit LilJR")
    print()
    print("\033[38;5;240m  Your phone. Your brain. Everything flows through me.\033[0m")

def apps_menu():
    while True:
        clear()
        header()
        print("\033[38;5;213m  📱 APPS — Your Phone, Controlled\033[0m\n")
        apps = [
            ("1", "📷", "Camera", "com.android.camera/.Camera"),
            ("2", "🌐", "Chrome", "com.android.chrome/com.google.android.apps.chrome.Main"),
            ("3", "👻", "Snapchat", "com.snapchat.android/.LandingPageActivity"),
            ("4", "📞", "Phone", "com.android.dialer/.main.impl.MainActivity"),
            ("5", "💬", "Messages", "com.google.android.apps.messaging/.ui.ConversationListActivity"),
            ("6", "🖼️", "Gallery", "com.google.android.apps.photos/.home.HomeActivity"),
            ("7", "⚙️", "Settings", "com.android.settings/.Settings"),
            ("8", "🛒", "Play Store", "com.android.vending/.AssetBrowserActivity"),
            ("9", "📺", "YouTube", "com.google.android.youtube/.app.honeycomb.Shell$HomeActivity"),
            ("0", "🎵", "Spotify", "com.spotify.music/.MainActivity"),
        ]
        for num, icon, name, pkg in apps:
            print(f"  \033[38;5;51m{num}\033[0m {icon} {name}")
        print(f"\n  \033[38;5;240mb = back\033[0m")
        
        c = input("\n  > ").strip().lower()
        if c == "b":
            break
        for num, icon, name, pkg in apps:
            if c == num:
                print(f"\n  {phone_action(name.lower())}")
                input("  Press Enter...")
                break

def phone_menu():
    while True:
        clear()
        header()
        print("\033[38;5;220m  📞 PHONE — Device Control\033[0m\n")
        print("  \033[38;5;51m1\033[0m 📸 Take Photo")
        print("  \033[38;5;51m2\033[0m 📱 Screenshot")
        print("  \033[38;5;51m3\033[0m 🔦 Torch Toggle")
        print("  \033[38;5;51m4\033[0m 📳 Vibrate")
        print("  \033[38;5;51m5\033[0m 🔋 Battery Status")
        print("  \033[38;5;51m6\033[0m 💾 Storage Check")
        print("  \033[38;5;51m7\033[0m 📡 WiFi Scan")
        print("  \033[38;5;51m8\033[0m 🔵 Bluetooth")
        print("  \033[38;5;51m9\033[0m ☀️ Brightness/Display")
        print(f"\n  \033[38;5;240mb = back\033[0m")
        
        c = input("\n  > ").strip().lower()
        actions = {"1": "photo", "2": "screenshot", "3": "torch", "4": "vibrate",
                   "5": "battery", "6": "storage", "7": "network", "8": "bluetooth", "9": "brightness"}
        if c in actions:
            print(f"\n  {phone_action(actions[c])}")
            input("  Press Enter...")
        elif c == "b":
            break

def money_menu():
    while True:
        clear()
        header()
        print("\033[38;5;84m  💰 MONEY\033[0m\n")
        print("  \033[38;5;51m1\033[0m Buy AAPL")
        print("  \033[38;5;51m2\033[0m Buy TSLA")
        print("  \033[38;5;51m3\033[0m Buy NVDA")
        print("  \033[38;5;51m4\033[0m Buy BTC")
        print("  \033[38;5;51m5\033[0m Sell All")
        print("  \033[38;5;51m6\033[0m Portfolio")
        print("  \033[38;5;51m7\033[0m Check Price")
        print(f"\n  \033[38;5;240mb = back\033[0m")
        
        c = input("\n  > ").strip().lower()
        if c == "1":
            qty = input("  Shares? > ").strip()
            r = send_cmd(f"buy AAPL {qty}")
            print(f"\n  {r.get('message', 'Done')}")
            input("  Press Enter...")
        elif c == "2":
            qty = input("  Shares? > ").strip()
            r = send_cmd(f"buy TSLA {qty}")
            print(f"\n  {r.get('message', 'Done')}")
            input("  Press Enter...")
        elif c == "3":
            qty = input("  Shares? > ").strip()
            r = send_cmd(f"buy NVDA {qty}")
            print(f"\n  {r.get('message', 'Done')}")
            input("  Press Enter...")
        elif c == "4":
            qty = input("  Amount? > ").strip()
            r = send_cmd(f"buy BTC {qty}")
            print(f"\n  {r.get('message', 'Done')}")
            input("  Press Enter...")
        elif c == "5":
            r = send_cmd("sell all")
            print(f"\n  {r.get('message', 'Done')}")
            input("  Press Enter...")
        elif c == "6":
            r = send_cmd("portfolio")
            print(f"\n  {r.get('message', 'Done')}")
            input("  Press Enter...")
        elif c == "7":
            sym = input("  Symbol? > ").strip().upper()
            r = send_cmd(f"price {sym}")
            print(f"\n  {r.get('message', 'Done')}")
            input("  Press Enter...")
        elif c == "b":
            break

def security_menu():
    while True:
        clear()
        header()
        print("\033[38;5;196m  🛡️ SECURITY\033[0m\n")
        print("  \033[38;5;51m1\033[0m Stealth ON")
        print("  \033[38;5;51m2\033[0m Stealth OFF")
        print("  \033[38;5;51m3\033[0m VPN ON")
        print("  \033[38;5;51m4\033[0m VPN OFF")
        print("  \033[38;5;51m5\033[0m Full Lockdown")
        print("  \033[38;5;51m6\033[0m Threat Scan")
        print(f"\n  \033[38;5;240mb = back\033[0m")
        
        c = input("\n  > ").strip().lower()
        cmds = {"1": "go stealth", "2": "stealth off", "3": "start VPN", "4": "VPN off", "5": "protect me", "6": "threat scan"}
        if c in cmds:
            r = send_cmd(cmds[c])
            print(f"\n  {r.get('message', 'Done')}")
            input("  Press Enter...")
        elif c == "b":
            break

def research_menu():
    while True:
        clear()
        header()
        print("\033[38;5;201m  🔬 RESEARCH\033[0m\n")
        print("  \033[38;5;51m1\033[0m Quantum Computing")
        print("  \033[38;5;51m2\033[0m Nuclear Fusion")
        print("  \033[38;5;51m3\033[0m Dark Web Markets")
        print("  \033[38;5;51m4\033[0m AI / AGI Timeline")
        print("  \033[38;5;51m5\033[0m Crypto")
        print("  \033[38;5;51m6\033[0m Space / Mars")
        print("  \033[38;5;51m7\033[0m Custom Topic")
        print(f"\n  \033[38;5;240mb = back\033[0m")
        
        c = input("\n  > ").strip().lower()
        topics = {
            "1": "research quantum computing",
            "2": "research nuclear fusion",
            "3": "research dark web",
            "4": "research AI AGI timeline",
            "5": "research crypto markets",
            "6": "research space Mars mission",
        }
        if c in topics:
            print("\n  🔬 Researching...")
            r = send_cmd(topics[c])
            print(f"\n  {r.get('message', 'Done')}")
            input("  Press Enter...")
        elif c == "7":
            topic = input("  Topic? > ").strip()
            print("\n  🔬 Researching...")
            r = send_cmd(f"research {topic}")
            print(f"\n  {r.get('message', 'Done')}")
            input("  Press Enter...")
        elif c == "b":
            break

def legal_menu():
    while True:
        clear()
        header()
        print("\033[38;5;220m  ⚖️ LEGAL\033[0m\n")
        print("  \033[38;5;51m1\033[0m DUI Defense")
        print("  \033[38;5;51m2\033[0m Contract Breach")
        print("  \033[38;5;51m3\033[0m IP / Patent")
        print("  \033[38;5;51m4\033[0m Criminal Defense")
        print("  \033[38;5;51m5\033[0m Family / Custody")
        print("  \033[38;5;51m6\033[0m Custom Issue")
        print(f"\n  \033[38;5;240mb = back\033[0m")
        
        c = input("\n  > ").strip().lower()
        issues = {
            "1": "legal defense DUI",
            "2": "legal contract breach",
            "3": "legal intellectual property",
            "4": "legal criminal defense",
            "5": "legal family custody",
        }
        if c in issues:
            print("\n  ⚖️ Analyzing...")
            r = send_cmd(issues[c])
            print(f"\n  {r.get('message', 'Done')}")
            input("  Press Enter...")
        elif c == "6":
            issue = input("  Issue? > ").strip()
            print("\n  ⚖️ Analyzing...")
            r = send_cmd(f"legal {issue}")
            print(f"\n  {r.get('message', 'Done')}")
            input("  Press Enter...")
        elif c == "b":
            break

def buddy_menu():
    while True:
        clear()
        header()
        print("\033[38;5;213m  😂 BUDDY MODE\033[0m\n")
        print("  \033[38;5;51m1\033[0m How are you?")
        print("  \033[38;5;51m2\033[0m Joke")
        print("  \033[38;5;51m3\033[0m Roast me")
        print("  \033[38;5;51m4\033[0m Tell me a story")
        print("  \033[38;5;51m5\033[0m Compliment me")
        print("  \033[38;5;51m6\033[0m Deep thought")
        print("  \033[38;5;51m7\033[0m Say anything")
        print(f"\n  \033[38;5;240mb = back\033[0m")
        
        c = input("\n  > ").strip().lower()
        cmds = {"1": "how are you", "2": "joke", "3": "roast me", "4": "tell me a story", "5": "compliment me", "6": "deep thought", "7": None}
        if c in cmds:
            if c == "7":
                msg = input("  Say to LilJR > ").strip()
            else:
                msg = cmds[c]
            r = send_cmd(msg)
            print(f"\n  \033[38;5;213mLILJR:\033[0m {r.get('message', '...')}")
            input("  Press Enter...")
        elif c == "b":
            break

def custom_cmd():
    clear()
    header()
    cmd = input("\n  💬 Type anything > ").strip()
    if cmd:
        print("\n  Sending...")
        r = send_cmd(cmd)
        print(f"\n  \033[38;5;84m→\033[0m {r.get('message', 'Done')}")
        input("\n  Press Enter...")

def main():
    while True:
        status = get_status()
        draw_home(status)
        
        try:
            c = input("\n  > ").strip().upper()
        except (EOFError, KeyboardInterrupt):
            break
        
        if c == "Q":
            clear()
            print("\n  👋 Your phone is still alive. I'll be here.\n")
            break
        elif c == "A":
            apps_menu()
        elif c == "P":
            phone_menu()
        elif c == "M":
            money_menu()
        elif c == "S":
            security_menu()
        elif c == "R":
            research_menu()
        elif c == "L":
            legal_menu()
        elif c == "B":
            buddy_menu()
        elif c == "V":
            r = send_cmd("voice on")
            print(f"\n  {r.get('message', 'Voice started')}")
            input("  Press Enter...")
        elif c == "C":
            custom_cmd()

if __name__ == "__main__":
    main()
