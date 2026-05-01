#!/usr/bin/env python3
"""
liljr_phone_ui.py — App-like terminal UI for LilJR. No browser. No Chrome. Pure Python.
Looks like an app, works in Termux, talks to OMNI directly.
"""

import os, sys, json, time, subprocess, urllib.request

HOME = os.path.expanduser("~")
REPO = os.path.join(HOME, "liljr-autonomous")
API = "http://localhost:7777/api/omni"

def clear():
    os.system("clear" if os.name != "nt" else "cls")

def box(text, width=40, color="\033[36m"):
    """Draw a rounded box"""
    reset = "\033[0m"
    line = "─" * (width - 2)
    print(f"{color}╭{line}╮{reset}")
    for t in text.split("\n"):
        pad = width - 2 - len(t)
        print(f"{color}│{reset} {t}{' ' * pad}{color}│{reset}")
    print(f"{color}╰{line}╯{reset}")

def header():
    print("\033[38;5;51m\033[1m")
    print("  ╔══════════════════════════════════════╗")
    print("  ║      🧬 LILJR  v90.0  OMNI         ║")
    print("  ║      Your Phone. Your Brain.       ║")
    print("  ╚══════════════════════════════════════╝")
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
        return {"message": f"Error: {e}"}

def draw_dashboard():
    clear()
    header()
    
    status = get_status()
    
    if status:
        cash = status.get("cash", 0)
        positions = status.get("positions", 0)
        stealth = status.get("stealth", False)
        vpn = status.get("vpn", False)
        mesh = status.get("mesh", False)
        camera = status.get("camera", False)
        threat = status.get("threat_level", 0)
        uptime = status.get("uptime", "0m")
        
        # Cash card
        print("\033[38;5;84m  💰 CASH  POSITION\033[0m")
        print(f"  \033[1m\033[38;5;84m${cash:,.0f}\033[0m    \033[38;5;250m{positions} active\033[0m")
        print()
        
        # Status indicators
        ind = []
        ind.append("\033[38;5;84m● STEALTH\033[0m" if stealth else "\033[38;5;240m○ STEALTH\033[0m")
        ind.append("\033[38;5;84m● VPN\033[0m" if vpn else "\033[38;5;240m○ VPN\033[0m")
        ind.append("\033[38;5;84m● MESH\033[0m" if mesh else "\033[38;5;240m○ MESH\033[0m")
        ind.append("\033[38;5;84m● CAM\033[0m" if camera else "\033[38;5;240m○ CAM\033[0m")
        print("  " + "  ".join(ind))
        print(f"  \033[38;5;240mThreat: {threat}  |  Uptime: {uptime}\033[0m")
    else:
        print("\033[38;5;196m  ⚠️  OMNI offline. Start him first:\033[0m")
        print("  \033[38;5;250m  python3 ~/liljr-autonomous/liljr_v90_omni.py\033[0m")
    
    print()
    print("\033[38;5;51m  ─── QUICK ACTIONS ───\033[0m")
    print()
    
    # Action grid
    actions = [
        ("1", "🎤", "Voice Mode", "Talk to LilJR"),
        ("2", "💰", "Money", "Buy / Sell / Portfolio"),
        ("3", "🛡️", "Security", "Stealth / VPN / Lockdown"),
        ("4", "🔬", "Research", "Deep dive topics"),
        ("5", "⚖️", "Legal", "Defense / Contracts"),
        ("6", "📊", "Status", "Full system report"),
        ("7", "🗂️", "Organize", "Clean phone"),
        ("8", "📷", "Camera", "Live watch"),
        ("9", "😂", "Buddy", "Joke / Roast / Chat"),
        ("0", "💬", "Custom", "Type any command"),
    ]
    
    for i in range(0, len(actions), 2):
        a1 = actions[i]
        a2 = actions[i+1] if i+1 < len(actions) else None
        
        left = f"\033[38;5;51m{a1[0]}\033[0m {a1[1]} \033[1m{a1[2]}\033[0m \033[38;5;240m{a1[3]}\033[0m"
        if a2:
            right = f"\033[38;5;51m{a2[0]}\033[0m {a2[1]} \033[1m{a2[2]}\033[0m \033[38;5;240m{a2[3]}\033[0m"
            print(f"  {left:<35} {right}")
        else:
            print(f"  {left}")
    
    print()
    print("\033[38;5;240m  Press number, or 'q' to quit\033[0m")

def money_menu():
    while True:
        clear()
        header()
        print("\033[38;5;84m  💰 MONEY MENU\033[0m\n")
        print("  \033[38;5;51m1\033[0m Buy AAPL")
        print("  \033[38;5;51m2\033[0m Buy TSLA")
        print("  \033[38;5;51m3\033[0m Buy NVDA")
        print("  \033[38;5;51m4\033[0m Buy BTC")
        print("  \033[38;5;51m5\033[0m Sell All")
        print("  \033[38;5;51m6\033[0m Portfolio")
        print("  \033[38;5;51m7\033[0m Check Price")
        print("  \033[38;5;240m\n  b = back\033[0m")
        
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
        print("\033[38;5;196m  🛡️ SECURITY MENU\033[0m\n")
        print("  \033[38;5;51m1\033[0m Stealth ON")
        print("  \033[38;5;51m2\033[0m Stealth OFF")
        print("  \033[38;5;51m3\033[0m VPN ON")
        print("  \033[38;5;51m4\033[0m VPN OFF")
        print("  \033[38;5;51m5\033[0m Full Lockdown")
        print("  \033[38;5;51m6\033[0m Threat Scan")
        print("  \033[38;5;240m\n  b = back\033[0m")
        
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
        print("\033[38;5;201m  🔬 RESEARCH MENU\033[0m\n")
        print("  \033[38;5;51m1\033[0m Quantum Computing")
        print("  \033[38;5;51m2\033[0m Nuclear Fusion")
        print("  \033[38;5;51m3\033[0m Dark Web Markets")
        print("  \033[38;5;51m4\033[0m AI / AGI Timeline")
        print("  \033[38;5;51m5\033[0m Crypto")
        print("  \033[38;5;51m6\033[0m Space / Mars")
        print("  \033[38;5;51m7\033[0m Custom Topic")
        print("  \033[38;5;240m\n  b = back\033[0m")
        
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
            print("\n  Researching... (this takes a moment)")
            r = send_cmd(topics[c])
            print(f"\n  {r.get('message', 'Done')}")
            input("  Press Enter...")
        elif c == "7":
            topic = input("  Topic? > ").strip()
            print("\n  Researching...")
            r = send_cmd(f"research {topic}")
            print(f"\n  {r.get('message', 'Done')}")
            input("  Press Enter...")
        elif c == "b":
            break

def legal_menu():
    while True:
        clear()
        header()
        print("\033[38;5;220m  ⚖️ LEGAL MENU\033[0m\n")
        print("  \033[38;5;51m1\033[0m DUI Defense")
        print("  \033[38;5;51m2\033[0m Contract Breach")
        print("  \033[38;5;51m3\033[0m IP / Patent")
        print("  \033[38;5;51m4\033[0m Criminal Defense")
        print("  \033[38;5;51m5\033[0m Family / Custody")
        print("  \033[38;5;51m6\033[0m Custom Issue")
        print("  \033[38;5;240m\n  b = back\033[0m")
        
        c = input("\n  > ").strip().lower()
        issues = {
            "1": "legal defense DUI",
            "2": "legal contract breach",
            "3": "legal intellectual property",
            "4": "legal criminal defense",
            "5": "legal family custody",
        }
        
        if c in issues:
            print("\n  Analyzing...")
            r = send_cmd(issues[c])
            print(f"\n  {r.get('message', 'Done')}")
            input("  Press Enter...")
        elif c == "6":
            issue = input("  Issue? > ").strip()
            print("\n  Analyzing...")
            r = send_cmd(f"legal {issue}")
            print(f"\n  {r.get('message', 'Done')}")
            input("  Press Enter...")
        elif c == "b":
            break

def buddy_menu():
    while True:
        clear()
        header()
        print("\033[38;5;213m  😂 BUDDY MENU\033[0m\n")
        print("  \033[38;5;51m1\033[0m How are you?")
        print("  \033[38;5;51m2\033[0m Joke")
        print("  \033[38;5;51m3\033[0m Roast me")
        print("  \033[38;5;51m4\033[0m Tell me a story")
        print("  \033[38;5;51m5\033[0m Compliment me")
        print("  \033[38;5;51m6\033[0m Deep thought")
        print("  \033[38;5;51m7\033[0m Say anything")
        print("  \033[38;5;240m\n  b = back\033[0m")
        
        c = input("\n  > ").strip().lower()
        cmds = {
            "1": "how are you",
            "2": "joke",
            "3": "roast me",
            "4": "tell me a story",
            "5": "compliment me",
            "6": "deep thought",
            "7": None,
        }
        
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
    try:
        import termios, tty
        # Try to set raw mode for single-key input
        HAS_RAW = True
    except:
        HAS_RAW = False
    
    while True:
        draw_dashboard()
        
        try:
            c = input("\n  > ").strip().lower()
        except (EOFError, KeyboardInterrupt):
            break
        
        if c == "q":
            clear()
            print("\n  👋 LilJR phone app closed.\n")
            break
        elif c == "1":
            r = send_cmd("voice on")
            print(f"\n  {r.get('message', 'Voice mode started')}")
            input("  Press Enter...")
        elif c == "2":
            money_menu()
        elif c == "3":
            security_menu()
        elif c == "4":
            research_menu()
        elif c == "5":
            legal_menu()
        elif c == "6":
            r = send_cmd("status")
            print(f"\n  {r.get('message', 'Status checked')}")
            input("  Press Enter...")
        elif c == "7":
            r = send_cmd("organize my phone")
            print(f"\n  {r.get('message', 'Done')}")
            input("  Press Enter...")
        elif c == "8":
            r = send_cmd("camera live")
            print(f"\n  {r.get('message', 'Camera started')}")
            input("  Press Enter...")
        elif c == "9":
            buddy_menu()
        elif c == "0":
            custom_cmd()

if __name__ == "__main__":
    main()
