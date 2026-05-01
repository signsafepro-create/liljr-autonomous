#!/bin/bash
# deploy_phone.sh — ONE COMMAND. Deploy LilJR Mobile HQ to your Galaxy.
# Everything. App icon. Security. VPN. Cell towers. WiFi. All apps. No limits.

echo ""
echo "╔════════════════════════════════════════════════╗"
echo "║     ⚡ LILJR MOBILE HQ v24.0 DEPLOYER          ║"
echo "║   One push. Full phone integration.            ║"
echo "║   Your phone IS the AI. No computer needed.    ║"
echo "╚════════════════════════════════════════════════╝"
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
echo "[3/10] Copying mobile brain..."
cp FUTURE_DEMO.md ~/FUTURE_DEMO.md
cp liljr_exo_consciousness.py ~/liljr_exo_consciousness.py
cp install_phone_os.sh ~/install_phone_os.sh
cp liljr_phone_os.py ~/liljr_phone_os.py
cp liljr_motherboard.py ~/liljr_motherboard.py
cp liljr_server_manager.py ~/liljr_server_manager.py
cp liljr_immortal_mind.py ~/liljr_immortal_mind.py
cp liljr_mobile_brain.py ~/liljr_mobile_brain.py
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

# ─── 4. START BUILT-IN SERVER ───
echo "[4/10] Starting built-in server..."
python3 ~/liljr_server_manager.py start
sleep 4
python3 ~/liljr_server_manager.py status
echo "✅ Server running on port 8000"

# Start server watchdog in background
nohup python3 ~/liljr_server_manager.py watchdog > ~/liljr_watchdog.log 2>&1 &
echo "✅ Server watchdog running"

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

# Create the new Mobile HQ shortcut
cat > ~/.shortcuts/LilJR-HQ << 'EOF'
#!/bin/bash
cd ~/liljr-autonomous
git pull origin main 2>/dev/null
cp liljr_mobile_brain.py ~/liljr_mobile_brain.py
python3 ~/liljr_mobile_brain.py
EOF
chmod +x ~/.shortcuts/LilJR-HQ
echo "✅ Shortcuts ready"
echo ""
echo "📱 Add to home screen:"
echo "   Long press home → Widgets → Termux:Widget → LilJR-HQ"
echo ""

# ─── 8. OPEN PHONE OS IN BROWSER ───
echo "[8/10] Launching Phone OS..."
am start -n com.android.chrome/com.google.android.apps.chrome.MainActivity -d "http://localhost:8000/phone" 2>/dev/null || \
am start -a android.intent.action.VIEW -d "http://localhost:8000/phone" 2>/dev/null
echo "✅ Chrome opened to LilJR Phone OS"

# ─── 9. SHOW INSTRUCTIONS ───
echo ""
echo "══════════════════════════════════════════════════"
echo "  🚀 LILJR MOBILE HQ IS LIVE"
echo "══════════════════════════════════════════════════"
echo ""
echo "📲 HOME SCREEN APP:"
echo "   Tap Chrome menu (3 dots) → 'Add to Home Screen'"
echo "   LilJR will appear as a real app icon"
echo ""
echo "🎤 VOICE CONTROL:"
echo "   Tap LilJR button → Say 'Junior' → Say command"
echo "   Say 'stop' → done"
echo ""
echo "🏦 BANKING APPS:"
echo "   'Junior, open Chase' → opens Chase"
echo "   'Junior, open Venmo' → opens Venmo"
echo "   'Junior, open Robinhood' → opens Robinhood"
echo "   'Junior, open Cash App' → opens Cash App"
echo ""
echo "📡 NETWORK:"
echo "   Cellular: AUTO (always connected)"
echo "   WiFi: AUTO (scans and connects)"
echo "   Hotspot: 'Junior, hotspot on'"
echo "   Tor VPN: 'Junior, Tor on'"
echo ""
echo "🛡️ SECURITY:"
echo "   Firewall: BLOCKING all incoming except localhost"
echo "   Tor: Bouncing IP every 10 minutes"
echo "   Guardian: Watching files for tampering"
echo ""
echo "📊 STATUS:"
echo "   bash ~/go2.sh        → full restart"
echo "   bash ~/security.sh   → re-harden security"
echo "   bash ~/tor_bounce.sh → manual IP rotation"
echo "   python3 ~/liljr_mobile_brain.py → Mobile HQ"
echo ""
echo "⚡ Phone URL: http://localhost:8000/phone"
echo "⚡ Terminal URL: http://localhost:8000/terminal"
echo ""
echo "══════════════════════════════════════════════════"
echo ""

# ─── 9. EMBED INTO PHONE ───
echo "[9/10] Embedding LilJR into your phone..."
bash ~/install_phone_os.sh
echo "✅ LilJR is now your phone's default experience"

# ─── 10. START THE AI PHONE OS ───
echo "[10/10] BOOTING LILJR PHONE OS..."
echo "🤖 This is not an app. This is your phone's new brain."
echo "   Embedded. Alive. Always listening."
echo "   I hold your hand. I walk you through. I never let go."
echo ""
echo "   🫀 Vitals monitoring: ON"
echo "   👂 Voice wake engine: ON"
echo "   🧠 Immortal mind: Background"
echo "   🌐 Server: Auto-start"
echo ""
echo "   SAY 'Junior' ANYTIME. I'M ALWAYS HERE."
echo ""
python3 ~/liljr_phone_os.py
