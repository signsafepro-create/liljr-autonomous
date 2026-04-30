#!/usr/bin/env python3
"""
LILJR VERIFICATION SCRIPT
Checks that v8 is running and no old servers are interfering.
"""
import urllib.request, json, subprocess, sys

def check():
    print("🔍 LILJR VERIFICATION")
    print("=" * 40)
    
    # 1. Check what's on port 8000
    try:
        req = urllib.request.Request("http://localhost:8000/api/health")
        with urllib.request.urlopen(req, timeout=5) as resp:
            health = json.loads(resp.read())
        ver = health.get("version", "UNKNOWN")
        print(f"[1] Server version: {ver}")
        if "liljr-empire-8.0" in ver:
            print("    ✅ v8 is running")
        else:
            print(f"    ❌ WRONG VERSION: {ver}")
            print("    Run: pkill -9 python; bash ~/liljr-autonomous/bulletproof_start.sh")
            return False
    except Exception as e:
        print(f"[1] Server not responding: {e}")
        print("    Run: bash ~/liljr-autonomous/bulletproof_start.sh")
        return False
    
    # 2. Check for old processes
    ps = subprocess.run("ps -ef | grep -E 'server_v6|server_termux|server\.py' | grep -v grep",
                       shell=True, capture_output=True, text=True)
    if ps.stdout.strip():
        print("[2] OLD SERVERS FOUND:")
        for line in ps.stdout.strip().split('\n')[:5]:
            print(f"    ⚠️ {line.strip()}")
        print("    Run: pkill -9 python")
        return False
    else:
        print("[2] No old servers detected ✅")
    
    # 3. Check key endpoints
    endpoints = [
        ("/api/empire", "Empire status"),
        ("/api/web/themes", "Web builder"),
        ("/api/self/scan", "Self-awareness"),
        ("/api/coder/analyze", "Auto-coder"),
        ("/api/marketing/copy", "Marketing"),
        ("/api/search/deep", "Deep search"),
    ]
    
    print("[3] Endpoint checks:")
    all_ok = True
    for path, name in endpoints:
        try:
            req = urllib.request.Request(f"http://localhost:8000{path}", 
                                        data=b'{}', 
                                        headers={'Content-Type': 'application/json'})
            with urllib.request.urlopen(req, timeout=5) as resp:
                data = json.loads(resp.read())
            if "error" in data and "not available" in str(data.get("error", "")):
                print(f"    ⚠️ {name}: module not loaded")
            else:
                print(f"    ✅ {name}")
        except Exception as e:
            print(f"    ❌ {name}: {e}")
            all_ok = False
    
    print("=" * 40)
    if all_ok:
        print("✅ ALL CHECKS PASSED — LilJR v8 is unstoppable")
    else:
        print("❌ Some checks failed. See above.")
    return all_ok

if __name__ == '__main__':
    ok = check()
    sys.exit(0 if ok else 1)
