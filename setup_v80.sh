#!/bin/bash
# setup_v80.sh — Install v80.0 LIVE DASHBOARD + Everything Commander
# Run: bash setup_v80.sh

echo "🧬 LILJR v80.0 SETUP — LIVE DASHBOARD"
echo ""

HOME_DIR="$HOME"
REPO="$HOME_DIR/liljr-autonomous"
DASH_HTML="$REPO/liljr_live_dashboard.html"
V80_PY="$REPO/liljr_v80_everything.py"

# 1. Pull latest
echo "[1] Pulling latest code..."
cd "$REPO" && git pull origin main 2>/dev/null || true

# 2. Copy dashboard to web dir for easy access
echo "[2] Installing dashboard..."
mkdir -p "$REPO/web"
cp "$DASH_HTML" "$REPO/web/live.html"

# 3. Create Termux:Widget shortcut for dashboard
echo "[3] Creating homescreen shortcuts..."
mkdir -p "$HOME_DIR/.shortcuts"

# Shortcut: Live Dashboard
cat > "$HOME_DIR/.shortcuts/LilJR-Live" << 'EOF'
#!/bin/bash
# Open live dashboard in Chrome
am start -a android.intent.action.VIEW -d "http://localhost:8765/" -t text/html 2>/dev/null || termux-open "http://localhost:8765/"
EOF
chmod +x "$HOME_DIR/.shortcuts/LilJR-Live"

# Shortcut: Everything Commander (text)
cat > "$HOME_DIR/.shortcuts/LilJR-Text" << 'EOF'
#!/bin/bash
cd ~/liljr-autonomous
python3 liljr_v80_everything.py
EOF
chmod +x "$HOME_DIR/.shortcuts/LilJR-Text"

# Shortcut: Everything Commander (voice)
cat > "$HOME_DIR/.shortcuts/LilJR-Voice" << 'EOF'
#!/bin/bash
cd ~/liljr-autonomous
python3 liljr_v80_everything.py voice
EOF
chmod +x "$HOME_DIR/.shortcuts/LilJR-Voice"

# Shortcut: Organize Phone Now
cat > "$HOME_DIR/.shortcuts/LilJR-Organize" << 'EOF'
#!/bin/bash
cd ~/liljr-autonomous
echo "organize my phone" | python3 liljr_v80_everything.py
EOF
chmod +x "$HOME_DIR/.shortcuts/LilJR-Organize"

# Shortcut: Sync Kid Photos
cat > "$HOME_DIR/.shortcuts/LilJR-Kids" << 'EOF'
#!/bin/bash
cd ~/liljr-autonomous
echo "sync kids" | python3 liljr_v80_everything.py
EOF
chmod +x "$HOME_DIR/.shortcuts/LilJR-Kids"

# 4. Create the "open dashboard" script that launches a small Chrome window
cat > "$HOME_DIR/.shortcuts/LilJR-Popup" << 'EOF'
#!/bin/bash
# Open dashboard in a small popup window (Samsung pop-up view compatible)
am start -a android.intent.action.VIEW -d "http://localhost:8765/" -t text/html --ez create_new_tab true 2>/dev/null || termux-open "http://localhost:8765/"
EOF
chmod +x "$HOME_DIR/.shortcuts/LilJR-Popup"

echo ""
echo "✅ v80.0 SETUP COMPLETE"
echo ""
echo "📱 HOMESCREEN SHORTCUTS CREATED:"
echo "   • LilJR-Live    → Opens live dashboard"
echo "   • LilJR-Text    → Text commander"
echo "   • LilJR-Voice   → Voice commander"
echo "   • LilJR-Organize→ Organize phone now"
echo "   • LilJR-Kids    → Sync kid photos"
echo "   • LilJR-Popup   → Dashboard in popup window"
echo ""
echo "🖥️  LIVE DASHBOARD:"
echo "   1. Run: python3 ~/liljr-autonomous/liljr_v80_everything.py"
echo "   2. Open Chrome → http://localhost:8765/"
echo "   3. Tap menu → 'Add to Home screen'"
echo "   4. Place on your SECOND homescreen slide"
echo "   5. (Samsung) Long press → 'Open in pop-up view' for floating window"
echo ""
echo "📊 DASHBOARD SHOWS (Live, every 2 seconds):"
echo "   • Stealth status • VPN status • Mesh server status"
echo "   • Cash & positions • Photos synced • Storage used"
echo "   • Quick buttons: Buy/Sell/Photo/Screen/Sing/Organize/Vault"
echo ""
echo "🎤 VOICE COMMANDS (say 'Hey Junior' to wake):"
echo "   'buy AAPL 10' | 'organize my phone' | 'sync kids' | 'go stealth'"
echo "   'start VPN' | 'host mesh' | 'sing' | 'status' | 'open Snapchat'"
echo ""
echo "👨‍👩‍👧 FAMILY VAULT:"
echo "   • Kid photos auto-synced to ~/.liljr_v80/family_vault/photos/kids/"
echo "   • Timeline generated at ~/.liljr_v80/family_vault/timeline.json"
echo "   • Backups created on demand"
echo ""
echo "🧬 Everything is live. Everything is precise. Everything is yours."
