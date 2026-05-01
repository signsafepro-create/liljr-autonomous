#!/bin/bash
# start_phone_ui.sh — Launch the app-like terminal UI for LilJR

cd ~/liljr-autonomous

# Pull latest
git pull origin main

# Check if OMNI is running
if ! pgrep -f "liljr_v90_omni" > /dev/null 2>&1; then
    echo "🧬 Starting OMNI brain..."
    # CRITICAL: redirect stdin from /dev/null so OMNI knows it's backgrounded
    # and skips the input() loop. Just runs the HTTP server.
    python3 liljr_v90_omni.py < /dev/null > ~/liljr_omni.log 2>&1 &
    sleep 3
fi

# Start the phone UI
echo "📱 Starting LilJR Phone UI..."
python3 liljr_phone_ui.py
