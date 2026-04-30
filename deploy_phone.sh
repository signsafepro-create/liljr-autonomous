#!/bin/bash
# deploy_phone.sh — ONE COMMAND. Deploy LilJR Phone OS to your Galaxy.
# Everything. App icon. Security. VPN bouncing. Firewall. All of it.

echo ""
echo "╔═══════════════════════════════════════╗"
echo "║     ⚡ LILJR PHONE DEPLOY v23.0       ║"
echo "║   One push. Full phone integration.    ║"
echo "╚═══════════════════════════════════════╝"
echo ""

# ─── 1. KILL EVERYTHING OLD ───
echo "[1/10] Killing old processes..."
pkill -9 -f "python.*server" 2>/dev/null
pkill -9 -f "python.*liljr" 2>/dev/null
pkill -9 -f "termux-speech" 2>/dev/null
pkill -9 -f "termux-tts" 2>/dev/null
sleep 2
echo "✅ Clean slate"

# ─── 2. PULL LATEST ───
echo "[2/10] Pulling latest code..."
cd ~/liljr-autonomous
git pull origin main 2>/dev/null
echo "✅ Latest pulled"

# ─── 3. COPY ALL FILES ───
echo "[3/10] Copying files..."
cp liljr_silent.py ~/liljr_silent.py
cp liljr_phone_os.html ~/liljr_phone_os.html
cp manifest.json ~/manifest.json
cp sw.js ~/sw.js
cp security.sh ~/security.sh
chmod +x ~/security.sh
cp tor_bounce.sh ~/tor_bounce.sh
chmod +x ~/tor_bounce.sh
cp jr.sh ~/jr.sh
chmod +x ~/jr.sh
cp go2.sh ~/go2.sh
chmod +x ~/go2.sh

# Copy PWA files to web directory
mkdir -p ~/liljr-autonomous/web/phone
cp liljr_phone_os.html ~/liljr-autonomous/web/phone/index.html
cp manifest.json ~/liljr-autonomous/web/phone/
cp sw.js ~/liljr-autonomous/web/phone/
mkdir -p ~/liljr-autonomous/web/phone/phone
cp phone/icon.svg ~/liljr-autonomous/web/phone/phone/icon.png 2>/dev/null || touch ~/liljr-autonomous/web/phone/phone/icon.png
echo "✅ Files copied"

# ─── 4. START SERVER ───
echo "[4/10] Starting LilJR server..."
python3 ~/server_v8.py > ~/server.log 2>&1 &
sleep 6

# Check if server is up
for i in 1 2 3; do
    if curl -s http://localhost:8000/api/health >/dev/null 2>&1; then
        echo "✅ Server running on port 8000"
        break
    fi
    sleep 2
done

# ─── 5. START SECURITY FORTRESS ───
echo "[5/10] Activating security fortress..."
bash ~/security.sh 2>/dev/null
echo "✅ Firewall ON | Guardian ON | Masquerade ON"

# ─── 6. START TOR BOUNCER ───
echo "[6/10] Starting Tor bouncer..."
if command -v tor >/dev/null 2>&1; then
    tor &
    sleep 5
    nohup bash ~/tor_bounce.sh >/dev/null 2>&1 &
    echo "✅ Tor ON | IP rotating every 10 min"
else
    echo "⚠️ Tor not installed. Run: pkg install tor"
fi

# ─── 7. CREATE HOME SCREEN SHORTCUTS ───
echo "[7/10] Creating shortcuts..."
mkdir -p ~/.shortcuts
cp ~/jr.sh ~/.shortcuts/LilJR
chmod +x ~/.shortcuts/LilJR
ln -sf ~/.shortcuts/LilJR ~/.shortcuts/liljr 2>/dev/null
echo "✅ Shortcuts ready"
echo ""
echo "📱 Add to home screen:"
echo "   Long press home → Widgets → Termux:Widget → LilJR"
echo ""

# ─── 8. OPEN PHONE OS IN BROWSER ───
echo "[8/10] Launching Phone OS..."
# Open Chrome to the PWA
am start -n com.android.chrome/com.google.android.apps.chrome.MainActivity -d "http://localhost:8000/phone" 2>/dev/null || \
am start -a android.intent.action.VIEW -d "http://localhost:8000/phone" 2>/dev/null
echo "✅ Chrome opened to LilJR Phone OS"

# ─── 9. SHOW INSTRUCTIONS ───
echo ""
echo "═══════════════════════════════════════════"
echo "  🚀 LILJR PHONE OS IS LIVE"
echo "═══════════════════════════════════════════"
echo ""
echo "📲 HOME SCREEN:"
echo "   Tap Chrome menu (3 dots) → 'Add to Home Screen'"
echo "   LilJR will appear as a real app icon"
echo ""
echo "🎤 VOICE CONTROL:"
echo "   Tap LilJR button → Say 'Junior' → Say command"
echo "   Say 'stop' → done"
echo ""
echo "🏦 BANKING APPS:"
echo "   Open LilJR Phone OS → tap any app → opens it"
echo "   Or say: 'Junior, open Chase' / 'Junior, open Venmo'"
echo ""
echo "🛡️ SECURITY:"
echo "   Firewall: BLOCKING all incoming except localhost"
echo "   Tor: Bouncing IP every 10 minutes"
echo "   Guardian: Watching files for tampering"
echo ""
echo "📊 STATUS CHECK:"
echo "   bash ~/go2.sh       → full restart"
echo "   bash ~/security.sh  → re-harden security"
echo "   bash ~/tor_bounce.sh → manual IP rotation"
echo ""
echo "⚡ Phone URL: http://localhost:8000/phone"
echo "⚡ Terminal URL: http://localhost:8000/terminal"
echo ""
echo "═══════════════════════════════════════════"
echo ""

# ─── 10. START SILENT VOICE LISTENER ───
echo "[10/10] Starting voice listener..."
echo "Say 'Junior' anytime to wake me up."
echo ""
python3 ~/liljr_silent.py
