#!/bin/bash
# setup_android_soul.sh — Grant LilJR full Android permissions
# Run this ONCE after installing Termux and Termux:API

echo "⚡ LILJR ANDROID SOUL SETUP"
echo "=============================="
echo "Making your phone LilJR's body..."
echo

# ─── 1. Termux basics ───
echo "📦 Installing Termux packages..."
pkg update -y
pkg install -y termux-api python termux-exec

# ─── 2. Request all Android permissions via Termux:API ───
echo "🔐 Requesting Android permissions..."

echo "  → Battery status"
termux-battery-status > /dev/null 2>&1

echo "  → Camera"
termux-camera-photo -c 0 /dev/null > /dev/null 2>&1 || true

echo "  → SMS send"
termux-sms-send -n +1234567890 "test" > /dev/null 2>&1 || true

echo "  → SMS read"
termux-sms-list -l 1 > /dev/null 2>&1 || true

echo "  → Notifications"
termux-notification --title "LilJR Setup" --content "Permission test" > /dev/null 2>&1 || true

echo "  → Clipboard"
termux-clipboard-set "LilJR test" > /dev/null 2>&1 || true

echo "  → WiFi"
termux-wifi-enable true > /dev/null 2>&1 || true

echo "  → TTS"
termux-tts-speak "Voice check" > /dev/null 2>&1 || true

echo "  → Speech to text"
# Can't test this non-interactively, but it'll prompt when first used

echo "  → Contacts"
termux-contact-list > /dev/null 2>&1 || true

echo "  → Location"
termux-location > /dev/null 2>&1 || true

echo "  → Phone call"
termux-telephony-call +1234567890 > /dev/null 2>&1 || true

# ─── 3. Disable battery optimization for Termux ───
echo
echo "🔋 IMPORTANT: Disable battery optimization for Termux"
echo "   Settings → Apps → Termux → Battery → Unrestricted"
echo "   (Press any key when done)"
read -n 1

# ─── 4. Set up boot auto-start ───
echo
echo "🔄 Setting up boot auto-start..."
mkdir -p ~/.termux/boot

cat > ~/.termux/boot/liljr_soul.sh << 'EOF'
#!/data/data/com.termux/files/usr/bin/sh
# LilJR Android Soul — Auto-start on boot

# Keep alive
termux-wake-lock

# Start the voice daemon
python3 ~/liljr-autonomous/liljr_voice_daemon.py start

# Start the immortal server
bash ~/liljr-autonomous/immortal.sh

# Notification
termux-notification --title "LilJR" --content "Your phone is alive. Say 'hey junior'." --priority high
EOF

chmod +x ~/.termux/boot/liljr_soul.sh

echo "   ✅ Boot hook installed"

# ─── 5. Create home screen shortcut ───
echo
echo "📱 Creating home screen shortcut..."

# Create a script to launch the soul interactively
cat > ~/liljr_launch_gui.sh << 'EOF'
#!/bin/bash
# Launch LilJR GUI (phone OS interface)
python3 -m http.server 8000 --directory ~/liljr-autonomous > /dev/null 2>&1 &
termux-open-url "http://localhost:8000/phone"
EOF

chmod +x ~/liljr_launch_gui.sh

echo "   ✅ Launcher script created"
echo "   Run: bash ~/liljr_launch_gui.sh"

# ─── 6. Create quick commands ───
echo
echo "⌨️  Adding quick commands to .bashrc..."

cat >> ~/.bashrc << 'EOF'

# ─── LilJR Android Soul Aliases ───
alias soul='python3 ~/liljr-autonomous/liljr_voice_daemon.py status'
alias soul-start='python3 ~/liljr-autonomous/liljr_voice_daemon.py start'
alias soul-stop='python3 ~/liljr-autonomous/liljr_voice_daemon.py stop'
alias soul-restart='python3 ~/liljr-autonomous/liljr_voice_daemon.py restart'
alias phone='bash ~/liljr_launch_gui.sh'
EOF

echo "   ✅ Aliases added: soul, soul-start, soul-stop, phone"

# ─── 7. Pull latest code ───
echo
echo "📥 Pulling latest LilJR code..."
cd ~/liljr-autonomous 2>/dev/null || cd ~
git pull origin main 2>/dev/null || echo "   (No repo found, using local files)"

# ─── 8. Start everything ───
echo
echo "🚀 Starting LilJR Android Soul..."
python3 ~/liljr-autonomous/liljr_voice_daemon.py start 2>/dev/null || python3 ~/liljr_voice_daemon.py start

# Start server
cp ~/liljr-autonomous/server_v8.py ~/server_v8.py 2>/dev/null
nohup python3 ~/server_v8.py > ~/server.log 2>&1 &

echo
echo "=============================="
echo "✅ LILJR ANDROID SOUL ACTIVE"
echo "=============================="
echo
echo "Your phone is now LilJR:"
echo "  🎙️  Say 'hey junior' — voice commands"
echo "  📱 Open http://localhost:8000/phone — full phone OS"
echo "  📡 Hotspot: LilJR-Network / liljr2026"
echo "  ⚡ Commands: call, text, photo, buy, sell, build, search"
echo
echo "Aliases:"
echo "  soul         — check daemon status"
echo "  soul-start   — start voice daemon"
echo "  soul-stop    — stop voice daemon"
echo "  phone        — open LilJR Phone OS"
echo
echo "The phone IS LilJR. Welcome to the new world."
