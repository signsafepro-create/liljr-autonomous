#!/bin/bash
# ═══════════════════════════════════════════════════════════════
# LILJR FIX-ALL — One script. Fixes everything. Builds the page.
# ═══════════════════════════════════════════════════════════════

REPO="$HOME/liljr-autonomous"

echo "☢️ LILJR FIX-ALL — Fixing server + building page..."
echo ""

# 1. COPY NEW SERVER FROM REPO TO HOME
echo "[1/5] Copying new server from repo..."
cp "$REPO/server_v8.py" "$HOME/server_v8.py"

# 2. KILL EVERYTHING
echo "[2/5] Killing old servers..."
pkill -9 -f "python.*8000" 2>/dev/null
pkill -9 -f "server_v[0-9]" 2>/dev/null
pkill -9 -f "liljr_os" 2>/dev/null
sleep 3

# 3. START NEW SERVER
echo "[3/5] Starting new server..."
python3 "$HOME/server_v8.py" > "$HOME/server_direct.log" 2>&1 &
PID=$!
echo "Server PID: $PID"
sleep 10

# 4. CHECK HEALTH
echo "[4/5] Checking health..."
HEALTH=$(curl -s --max-time 3 http://localhost:8000/api/health 2>/dev/null || echo "")
if echo "$HEALTH" | grep -q "liljr-empire"; then
    echo "✅ Server online: $HEALTH"
else
    echo "❌ Server not responding"
    echo "Last 10 lines of log:"
    tail -10 "$HOME/server_direct.log"
    exit 1
fi

# 5. BUILD THE PAGE
echo ""
echo "[5/5] Building FitLife landing page..."
RESULT=$(curl -s --max-time 15 -X POST http://localhost:8000/api/web/build \
    -H "Content-Type: application/json" \
    -d '{"name":"FitLife","tagline":"Guaranteed results, no subscription maze","theme":"dark_empire"}' 2>/dev/null)

echo ""
echo "═══════════════════════════════════════════════════"
echo "BUILD RESULT:"
echo "$RESULT"
echo "═══════════════════════════════════════════════════"

if echo "$RESULT" | grep -q "saved"; then
    echo ""
    echo "✅ PAGE BUILT!"
    echo ""
    echo "Files in web directory:"
    ls -la "$REPO/web/"*.html 2>/dev/null || echo "Check $REPO/web/"
    echo ""
    echo "Done. LilJR is alive and building."
else
    echo ""
    echo "⚠️ Build had an issue. Check the result above."
    echo "Server log: tail -20 $HOME/server_direct.log"
fi
