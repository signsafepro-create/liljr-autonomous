#!/bin/bash
# start_phone_app.sh — Launch OMNI + Phone Dashboard as one app experience

echo "🧬 LILJR PHONE APP — Starting..."

# Step 1: Make sure OMNI is running
if ! pgrep -f "liljr_v90_omni" > /dev/null 2>&1; then
    echo "[1] Starting OMNI brain..."
    cd ~/liljr-autonomous && nohup python3 liljr_v90_omni.py > ~/liljr_omni.log 2>&1 &
    sleep 2
else
    echo "[1] OMNI already running ✅"
fi

# Step 2: Start mini web server for dashboard
PORT=8888
if ! lsof -i:$PORT > /dev/null 2>&1; then
    echo "[2] Starting phone dashboard server on port $PORT..."
    cd ~/liljr-autonomous && nohup python3 -m http.server $PORT > ~/liljr_dashboard.log 2>&1 &
    sleep 1
else
    echo "[2] Dashboard server already running ✅"
fi

# Step 3: Open Chrome to the dashboard
echo "[3] Opening Chrome..."
am start -a android.intent.action.VIEW -d "http://localhost:$PORT/liljr_phone_layout.html" -t text/html -n com.android.chrome/com.google.android.apps.chrome.Main 2>/dev/null || \
am start -a android.intent.action.VIEW -d "http://localhost:$PORT/liljr_phone_layout.html" -t text/html 2>/dev/null || \
echo "⚠️ Open Chrome manually: http://localhost:$PORT/liljr_phone_layout.html"

echo ""
echo "╔══════════════════════════════════════════════════════════════════╗"
echo "║                                                                  ║"
echo "║     📱 PHONE APP ACTIVE                                          ║"
echo "║                                                                  ║"
echo "║     OMNI Brain:    http://localhost:7777                         ║"
echo "║     Dashboard:     http://localhost:$PORT/liljr_phone_layout.html ║"
echo "║                                                                  ║"
echo "║     Tap dashboard buttons to control OMNI.                       ║"
echo "║     Type in text box to talk to him.                             ║"
echo "║                                                                  ║"
echo "╚══════════════════════════════════════════════════════════════════╝"
echo ""
echo "To stop: pkill -f 'http.server' && pkill -f 'liljr_v90_omni'"
