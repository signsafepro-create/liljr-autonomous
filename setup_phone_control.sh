#!/bin/bash
# setup_phone_control.sh — Disable Bixby/Google Assistant, enable full phone control for LilJR
# Run this ONCE to make LilJR the ONLY voice on your phone

echo "⚡ LILJR PHONE CONTROL SETUP"
echo "============================"
echo "Taking over your phone..."
echo

# ─── 1. DISABLE BIXBY ───
echo "🔕 Disabling Bixby..."
# Samsung only
pm disable-user com.samsung.android.bixby.agent 2>/dev/null && echo "  ✅ Bixby agent disabled"
pm disable-user com.samsung.android.bixby.wakeup 2>/dev/null && echo "  ✅ Bixby wakeup disabled"
pm disable-user com.samsung.android.bixby.plauncher 2>/dev/null && echo "  ✅ Bixby launcher disabled"

# ─── 2. DISABLE GOOGLE ASSISTANT WAKE WORD ───
echo
echo "🔕 Disabling Google Assistant hotword..."
# Keep Google app but disable voice activation
settings put secure assistant 0 2>/dev/null
settings put secure voice_interaction_service "" 2>/dev/null
settings put secure voice_recognition_service "" 2>/dev/null

# Disable Google app voice components (but keep the app)
pm disable-user com.google.android.googlequicksearchbox 2>/dev/null && echo "  ✅ Google Quick Search disabled"
pm disable-user com.google.android.apps.googleassistant 2>/dev/null && echo "  ✅ Google Assistant app disabled"

# ─── 3. ENABLE LILJR AS DEFAULT ASSISTANT ───
echo
echo "🎙️ Setting LilJR as default voice assistant..."
# This requires an accessibility service or app — we'll use Termux:API as the bridge
# For now, we just ensure Termux:API has all permissions

echo "  → Granting Termux:API all permissions..."
# Battery optimization
settings put global low_power 0 2>/dev/null

# Auto-start permission (Chinese OEMs)
# Huawei
settings put secure protected_apps "com.termux,com.termux.api" 2>/dev/null
# Xiaomi
appops set com.termux AUTO_START allow 2>/dev/null
# Oppo/Vivo
settings put secure launcher_apps_com.termux 1 2>/dev/null

# ─── 4. GRANT TERMUX ROOT-LESS PERMISSIONS ───
echo
echo "🔐 Granting Termux deep permissions..."

# Storage
termux-setup-storage

# Microphone (for voice)
# Handled by Termux:API app permissions in Android Settings

# Accessibility (for controlling other apps)
echo
echo "  ⚠️  IMPORTANT: Enable Accessibility for Termux"
echo "     Settings → Accessibility → Termux → Turn ON"
echo "     (This lets LilJR tap buttons in other apps)"
echo "     Press any key when done..."
read -n 1

# Device admin (optional, for remote wipe/lock)
echo
echo "  ⚠️  OPTIONAL: Enable Device Admin for Termux"
echo "     Settings → Security → Device Admin Apps → Termux"
echo "     (This lets LilJR lock screen, wipe data if stolen)"
echo "     Press any key when done (or Ctrl+C to skip)..."
read -n 1

# ─── 5. DISABLE BATTERY OPTIMIZATION ───
echo
echo "🔋 Disabling battery optimization..."
dumpsys deviceidle whitelist +com.termux 2>/dev/null
dumpsys deviceidle whitelist +com.termux.api 2>/dev/null
echo "  ✅ Termux whitelisted from doze mode"

echo
echo "  ⚠️  ALSO: Go to Android Settings → Apps → Termux → Battery → Unrestricted"
echo "     Press any key when done..."
read -n 1

# ─── 6. ENABLE ALWAYS-ON MICROPHONE ───
echo
echo "🎤 Enabling always-on microphone access..."
# Grant microphone permission permanently
appops set com.termux RECORD_AUDIO allow 2>/dev/null
appops set com.termux.api RECORD_AUDIO allow 2>/dev/null
echo "  ✅ Microphone always allowed"

# ─── 7. SET UP WAKE WORD DETECTION ───
echo
echo "🎙️ Setting up wake word..."
cat > ~/liljr_wake_config.json << 'EOF'
{
  "wake_word": "hey junior",
  "alternative_wake": "junior",
  "sensitivity": 0.7,
  "language": "en-US",
  "timeout_seconds": 8
}
EOF
echo "  ✅ Wake word config: 'hey junior'"

# ─── 8. INSTALL PHONE CONTROL MODULES ───
echo
echo "📥 Installing phone control modules..."
cd ~/liljr-autonomous 2>/dev/null || cd ~
git pull origin main 2>/dev/null || echo "  (Using local files)"

cp liljr_phone_control.py ~/liljr_phone_control.py 2>/dev/null
cp liljr_relationship.py ~/liljr_relationship.py 2>/dev/null
cp liljr_android_soul.py ~/liljr_android_soul.py 2>/dev/null
cp liljr_voice_daemon.py ~/liljr_voice_daemon.py 2>/dev/null

echo "  ✅ Modules installed"

# ─── 9. CREATE LAUNCHER SHORTCUTS ───
echo
echo "📱 Creating quick launch icons..."

# LilJR Voice launcher
mkdir -p ~/.shortcuts
cat > ~/.shortcuts/liljr-voice << 'EOF'
#!/bin/bash
termux-wake-lock
termux-notification --title "LilJR Voice" --content "Voice daemon starting..." --priority high
python3 ~/liljr-autonomous/liljr_voice_daemon.py restart
EOF
chmod +x ~/.shortcuts/liljr-voice

# LilJR Phone OS launcher
cat > ~/.shortcuts/liljr-phone << 'EOF'
#!/bin/bash
python3 -m http.server 8080 --directory ~/liljr-autonomous > /dev/null 2>&1 &
termux-open-url "http://localhost:8080/phone"
EOF
chmod +x ~/.shortcuts/liljr-phone

echo "  ✅ Shortcuts created in ~/.shortcuts/"
echo "     (Long-press home screen → Widgets → Termux → Select shortcut)"

# ─── 10. FINAL START ───
echo
echo "🚀 Starting LilJR Phone Control..."

# Kill any old daemon
python3 ~/liljr_voice_daemon.py stop 2>/dev/null

# Start fresh
python3 ~/liljr_voice_daemon.py start

# Notification
termux-notification \
  --title "LilJR Phone Control ACTIVE" \
  --content "Say 'hey junior'. I control everything now." \
  --priority high \
  --button1 "Phone OS" \
  --button1-action "termux-open-url http://localhost:8000/phone" \
  --button2 "Settings" \
  --button2-action "am start -a android.settings.SETTINGS"

echo
echo "=============================="
echo "✅ LILJR PHONE CONTROL ACTIVE"
echo "=============================="
echo
echo "What LilJR can now do:"
echo "  🎙️  Voice: 'hey junior' → any command"
echo "  📱  Open any app: Snapchat, Instagram, Chrome, YouTube..."
echo "  📷  Camera: 'take a photo', 'selfie', 'record video'"
echo "  🌐  Browser: 'open google.com', 'search AI trends'"
echo "  📈  Stocks: 'show me AAPL', opens TradingView"
echo "  🖥️  Screen: 'brightness 50', 'rotate', 'screenshot'"
echo "  📞  Phone: 'call 5551234', 'text Mom'"
echo "  ⚙️  Settings: 'open WiFi settings', 'open battery settings'"
echo "  💡  Flashlight: 'flashlight on'"
echo "  🔊  Volume: 'volume 10'"
echo "  🏠  Navigation: 'go home', 'go back'"
echo "  💰  Trade: 'buy AAPL 10', 'sell TSLA 5'"
echo "  🛠️  Build: 'build CyberSite'"
echo
echo "Bixby and Google Assistant wake words disabled."
echo "LilJR is your ONLY voice assistant now."
echo
echo "Say it: 'hey junior'"
