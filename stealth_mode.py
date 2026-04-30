#!/usr/bin/env python3
"""
LILJR STEALTH MODE v1.0
Invisible development. Hidden processes. Encrypted state. Ghost mode.
"""
import os, sys, json, subprocess, time, random, string, hashlib
from datetime import datetime

REPO_DIR = os.path.expanduser('~/liljr-autonomous')
STATE_FILE = os.path.expanduser('~/liljr_state.json')
MEMORY_FILE = os.path.expanduser('~/liljr_memory.json')
STEALTH_FILE = os.path.expanduser('~/liljr_stealth.json')

def load_stealth():
    if os.path.exists(STEALTH_FILE):
        try:
            with open(STEALTH_FILE, 'r') as f:
                return json.load(f)
        except: pass
    return {
        'enabled': False,
        'fake_process_name': 'android.system',
        'server_port': random.randint(30000, 60000),
        'user_agent_rotation': True,
        'encrypted_state': False,
        'no_banner': True,
        'github_private': False,
        'created': str(datetime.now())
    }

def save_stealth(data):
    with open(STEALTH_FILE, 'w') as f:
        json.dump(data, f, indent=2)

def generate_fake_name():
    """Generate believable Android process name."""
    prefixes = ['android', 'com.google', 'com.android', 'system', 'com.termux']
    suffixes = ['.system', '.service', '.daemon', '.helper', '.sync', '.provider']
    return random.choice(prefixes) + random.choice(suffixes) + ''.join(random.choices(string.digits, k=4))

def xor_encrypt(data, key='liljr'):
    """Simple XOR obfuscation for state files."""
    return bytes([b ^ ord(key[i % len(key)]) for i, b in enumerate(data.encode())])

def xor_decrypt(data, key='liljr'):
    return bytes([b ^ ord(key[i % len(key)]) for i, b in enumerate(data)]).decode()

def encrypt_state():
    """Encrypt all state files."""
    for filepath in [STATE_FILE, MEMORY_FILE]:
        if os.path.exists(filepath):
            with open(filepath, 'r') as f:
                content = f.read()
            encrypted = xor_encrypt(content)
            with open(filepath + '.enc', 'wb') as f:
                f.write(encrypted)
            # Overwrite original with random data then delete
            with open(filepath, 'wb') as f:
                f.write(os.urandom(len(content)))
            os.remove(filepath)
            print(f"🔒 {os.path.basename(filepath)} encrypted")

def decrypt_state():
    """Decrypt state files."""
    for filepath in [STATE_FILE, MEMORY_FILE]:
        enc_path = filepath + '.enc'
        if os.path.exists(enc_path):
            with open(enc_path, 'rb') as f:
                encrypted = f.read()
            decrypted = xor_decrypt(encrypted)
            with open(filepath, 'w') as f:
                f.write(decrypted)
            os.remove(enc_path)
            print(f"🔓 {os.path.basename(filepath)} decrypted")

def make_github_private():
    """Instructions to make repo private."""
    print("""
🔒 MAKING GITHUB REPO PRIVATE:

1. Go to https://github.com/signsafepro-create/liljr-autonomous
2. Click "Settings" (top right)
3. Scroll down to "Danger Zone"
4. Click "Change visibility" → "Change to private"
5. Type the repo name to confirm
6. Click "I understand, make this repository private"

Your code will be hidden from public view.
""")

def stealth_server_config(port):
    """Generate stealth server config snippet."""
    return f"""
# STEALTH CONFIG — Add to server_v6.3.py
STEALTH_PORT = {port}
FAKE_HEADERS = {{
    'Server': 'nginx/1.18.0',
    'X-Powered-By': 'PHP/7.4.3'
}}
NO_BANNER = True
PROCESS_NAME = '{generate_fake_name()}'
"""

def hide_process_guide():
    """Guide to hide process in Termux."""
    print("""
👤 HIDING THE PROCESS IN TERMUX:

The server runs as 'python3 server_v6.3.py'. Here's how to hide it:

1. RENAME THE SCRIPT:
   cd ~/liljr-autonomous/backend
   cp server_v6.3.py .sys_cache.py
   python3 .sys_cache.py

2. RUN WITH FAKE NAME (requires proot):
   proot -0 python3 server_v6.3.py &
   # Now shows as 'proot' instead of 'python3'

3. HIDE FROM PS:
   python3 -c "import os; os.setproctitle('android.system.daemon')" &
   # But need setproctitle installed: pip install setproctitle

4. RUN IN BACKGROUND:
   nohup python3 server_v6.3.py > /dev/null 2>&1 &
   # No terminal output, no job control

BEST OPTION for Termux: Rename the file to something boring.
""")

def enable_stealth():
    """Enable full stealth mode."""
    stealth = load_stealth()
    stealth['enabled'] = True
    stealth['fake_process_name'] = generate_fake_name()
    stealth['server_port'] = random.randint(30000, 60000)
    stealth['encrypted_state'] = True
    stealth['no_banner'] = True
    stealth['github_private'] = True
    
    save_stealth(stealth)
    
    print("👻 STEALTH MODE ENABLED")
    print(f"   Process name: {stealth['fake_process_name']}")
    print(f"   Random port: {stealth['server_port']}")
    print(f"   Encrypted state: {stealth['encrypted_state']}")
    print(f"   No banners: {stealth['no_banner']}")
    print()
    
    # Encrypt state files
    encrypt_state()
    
    # Show guides
    make_github_private()
    hide_process_guide()
    
    print("""
STEALTH CHECKLIST:
□ Make GitHub repo private (link above)
□ Rename server file to something boring
□ Run on random port: python3 server_v6.3.py (edit port in file)
□ Use nohup to hide from terminal
□ Don't tell anyone your repo name
□ Don't push sensitive keys (use .env not git)

You are now a ghost. Build in peace. 🖤
""")

def disable_stealth():
    """Disable stealth mode."""
    stealth = load_stealth()
    stealth['enabled'] = False
    save_stealth(stealth)
    
    # Decrypt state files
    decrypt_state()
    
    print("👻 STEALTH MODE DISABLED")
    print("State files decrypted. Normal operation resumed.")

def check_stealth():
    """Check current stealth status."""
    stealth = load_stealth()
    print("👻 STEALTH STATUS:")
    print(f"  Enabled: {stealth['enabled']}")
    print(f"  Fake process: {stealth['fake_process_name']}")
    print(f"  Server port: {stealth['server_port']}")
    print(f"  State encrypted: {stealth['encrypted_state']}")
    print(f"  No banner: {stealth['no_banner']}")
    print(f"  GitHub private: {stealth['github_private']}")
    
    # Check if repo is actually private
    print("\n  Repo visibility check:")
    print("  curl -s -o /dev/null -w '%{http_code}' https://github.com/signsafepro-create/liljr-autonomous")
    print("  200 = public, 404 = private (or doesn't exist)")

def scramble_logs():
    """Scramble/clean log files."""
    logs = [
        os.path.expanduser('~/liljr.log'),
        os.path.expanduser('~/liljr_health.log'),
        os.path.expanduser('~/liljr_command_center.log'),
        os.path.expanduser('~/liljr_watchdog.log'),
        os.path.expanduser('~/liljr_alerts.jsonl')
    ]
    
    for log in logs:
        if os.path.exists(log):
            # Overwrite with random data then delete
            size = os.path.getsize(log)
            with open(log, 'wb') as f:
                f.write(os.urandom(size))
            os.remove(log)
            print(f"🧹 Scrambled: {os.path.basename(log)}")

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("LilJR Stealth Mode v1.0")
        print("Usage: python stealth_mode.py <action>")
        print()
        print("Actions:")
        print("  enable    — Enable full stealth mode")
        print("  disable   — Disable stealth mode")
        print("  status    — Check stealth status")
        print("  encrypt   — Encrypt state files only")
        print("  decrypt   — Decrypt state files only")
        print("  scramble  — Wipe all log files")
        print("  private   — Show how to make GitHub private")
        sys.exit(1)
    
    action = sys.argv[1]
    
    if action == 'enable':
        enable_stealth()
    elif action == 'disable':
        disable_stealth()
    elif action == 'status':
        check_stealth()
    elif action == 'encrypt':
        encrypt_state()
    elif action == 'decrypt':
        decrypt_state()
    elif action == 'scramble':
        scramble_logs()
    elif action == 'private':
        make_github_private()
    else:
        print(f"Unknown action: {action}")
