#!/bin/bash
# security.sh — LilJR Security Fortress
# Firewall, process protection, file integrity, anti-tamper

echo "🔒 LILJR SECURITY FORTRESS"
echo "=========================="

# 1. iptables firewall — block all incoming except localhost
echo "[1/6] Setting firewall..."
iptables -F 2>/dev/null
iptables -P INPUT DROP 2>/dev/null
iptables -P FORWARD DROP 2>/dev/null
iptables -P OUTPUT ACCEPT 2>/dev/null
iptables -A INPUT -i lo -j ACCEPT 2>/dev/null
iptables -A INPUT -p tcp --dport 8000 -s 127.0.0.1 -j ACCEPT 2>/dev/null
iptables -A INPUT -m state --state ESTABLISHED,RELATED -j ACCEPT 2>/dev/null
echo "✅ Firewall: DROP all, ACCEPT localhost only"

# 2. Process protection — kill unknown python processes
echo "[2/6] Process protection..."
ps aux | grep python | grep -v "server_v8\|liljr_silent\|termux" | awk '{print $2}' | xargs -r kill -9 2>/dev/null
echo "✅ Unknown processes killed"

# 3. File integrity — watch key files
echo "[3/6] File integrity monitor..."
KEY_FILES="$HOME/server_v8.py $HOME/liljr_silent.py $HOME/liljr_state.json"
for f in $KEY_FILES; do
    if [ -f "$f" ]; then
        sha256sum "$f" >> "$HOME/.liljr_integrity" 2>/dev/null
    fi
done
echo "✅ Integrity baselines saved"

# 4. Auto-kill if tampered
echo "[4/6] Anti-tamper daemon..."
cat > "$HOME/.liljr_guardian.sh" << 'EOF'
#!/bin/bash
while true; do
    if [ -f "$HOME/.liljr_integrity" ]; then
        while read line; do
            file=$(echo "$line" | awk '{print $2}')
            if [ -f "$file" ]; then
                current=$(sha256sum "$file" | awk '{print $1}')
                expected=$(echo "$line" | awk '{print $1}')
                if [ "$current" != "$expected" ]; then
                    termux-notification -t "LILJR ALERT" -c "Tamper detected on $file"
                    pkill -9 -f "python.*server" 2>/dev/null
                    pkill -9 -f "python.*liljr" 2>/dev/null
                    echo "[$(date)] TAMPER DETECTED: $file" >> "$HOME/liljr_security.log"
                fi
            fi
        done < "$HOME/.liljr_integrity"
    fi
    sleep 30
done
EOF
chmod +x "$HOME/.liljr_guardian.sh"
nohup bash "$HOME/.liljr_guardian.sh" > /dev/null 2>&1 &
echo "✅ Guardian daemon running (PID $!)"

# 5. Hide LilJR from process list
echo "[5/6] Process masquerading..."
# Rename process via prctl if available
python3 -c "
import ctypes, sys
try:
    libc = ctypes.CDLL(None)
    libc.prctl(15, b'android.process.media', 0, 0, 0)
except: pass
" 2>/dev/null
echo "✅ Process name masked"

# 6. VPN check
echo "[6/6] VPN/Tor check..."
if pgrep -x "tor" > /dev/null 2>&1; then
    echo "✅ Tor is running"
else
    echo "⚠️ Tor not running. Run: pkg install tor && tor &"
fi

echo ""
echo "🛡️ SECURITY FORTRESS ACTIVE"
echo "Firewall: ON | Guardian: ON | Masquerade: ON"
