#!/usr/bin/env python3
"""
LILJR FULL SYSTEM DIAGNOSTIC
Checks everything. Finds the problem.
"""
import os, sys, json, subprocess, glob, socket

BASE = os.path.expanduser('~/liljr-autonomous')
HOME = os.path.expanduser('~')

def run(cmd):
    try:
        return subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=10).stdout.strip()
    except Exception as e:
        return f"ERROR: {e}"

def check_port(port=8000):
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(2)
        result = s.connect_ex(('127.0.0.1', port))
        s.close()
        return result == 0
    except:
        return False

def check_processes():
    ps = run("ps -ef | grep -E 'python.*8000|server_v|liljr_os|watchdog' | grep -v grep")
    return ps if ps else "No LilJR processes found"

def check_files():
    files = {}
    for name in ['server_v8.py', 'lj_empire.py', 'bulletproof_start.sh', 'immortal_watchdog.sh']:
        path = os.path.join(BASE, name)
        if os.path.exists(path):
            files[name] = f"EXISTS ({os.path.getsize(path)} bytes)"
        else:
            files[name] = "MISSING"
    return files

def check_logs():
    logs = {}
    for name in ['liljr.log', 'liljr_health.log', 'liljr_bulletproof.log', 'liljr_immortal.log']:
        path = os.path.join(HOME, name)
        if os.path.exists(path):
            with open(path, 'r') as f:
                lines = f.readlines()
            logs[name] = {
                "lines": len(lines),
                "last_5": [l.strip() for l in lines[-5:]]
            }
        else:
            logs[name] = "NOT FOUND"
    return logs

def check_state():
    states = {}
    for name in ['liljr_state.json', 'liljr_empire.db']:
        path = os.path.join(HOME, name)
        if os.path.exists(path):
            states[name] = f"EXISTS ({os.path.getsize(path)} bytes)"
        else:
            states[name] = "MISSING"
    return states

def check_git():
    status = run(f"cd {BASE} && git status --short")
    log = run(f"cd {BASE} && git log --oneline -3")
    return {"status": status if status else "clean", "last_commits": log}

def find_weird_messages():
    """Search for any unusual shutdown/stop messages."""
    results = []
    for root, _, files in os.walk(BASE):
        for f in files:
            if f.endswith(('.py', '.sh', '.json')):
                path = os.path.join(root, f)
                try:
                    with open(path, 'r') as file:
                        content = file.read()
                    # Look for stop/shutdown/restart messages
                    for pattern in ['stop', 'shutdown', 'killed', 'terminated', 'exit', 'restart']:
                        if pattern in content.lower():
                            lines = content.split('\n')
                            for i, line in enumerate(lines):
                                if pattern in line.lower() and ('print' in line or 'log' in line or 'print(' in line):
                                    results.append(f"{path}:{i+1}: {line.strip()}")
                                    if len(results) > 20:
                                        return results[:20]
                except:
                    pass
    return results[:20]

def main():
    print("═══════════════════════════════════════════")
    print("  LILJR FULL SYSTEM DIAGNOSTIC")
    print("═══════════════════════════════════════════\n")
    
    print("[1] PORT 8000:")
    print(f"    Listening: {check_port(8000)}")
    print()
    
    print("[2] PROCESSES:")
    print(f"    {check_processes()}")
    print()
    
    print("[3] FILES:")
    for k, v in check_files().items():
        print(f"    {k}: {v}")
    print()
    
    print("[4] STATE/DB:")
    for k, v in check_state().items():
        print(f"    {k}: {v}")
    print()
    
    print("[5] GIT:")
    git_info = check_git()
    print(f"    Status: {git_info['status']}")
    print(f"    Last commits:\n{git_info['last_commits']}")
    print()
    
    print("[6] LOGS:")
    for k, v in check_logs().items():
        if isinstance(v, dict):
            print(f"    {k}: {v['lines']} lines")
            for line in v['last_5']:
                print(f"        {line}")
        else:
            print(f"    {k}: {v}")
    print()
    
    print("[7] WEIRD MESSAGES (stop/shutdown/exit in code):")
    weird = find_weird_messages()
    if weird:
        for w in weird:
            print(f"    {w}")
    else:
        print("    None found")
    print()
    
    print("[8] SEARCH FOR 'NERO/CIRCUITS/RECHARGED':")
    search = run(f"grep -ri 'nero\\|circuits\\|recharged\\|recharge' {BASE} 2>/dev/null || echo 'NOT FOUND IN REPO'")
    print(f"    {search}")
    print()
    
    print("═══════════════════════════════════════════")
    print("  END DIAGNOSTIC")
    print("═══════════════════════════════════════════")

if __name__ == '__main__':
    main()
