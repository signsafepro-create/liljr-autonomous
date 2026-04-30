#!/bin/bash
# ═══════════════════════════════════════════════════════════════
# LILJR REVIVE — Nuclear restart that actually works
# Kills everything. Waits for port release. Starts fresh. Verifies.
# ═══════════════════════════════════════════════════════════════

REPO="$HOME/liljr-autonomous"
SERVER="$REPO/server_v8.py"
HEALTH_URL="http://localhost:8000/api/health"
STARTUP_LOG="$HOME/liljr_startup.log"

echo "☢️ LILJR REVIVE — Bringing the empire back..."
echo ""

# ═══ STEP 1: KILL EVERYTHING ═══
echo "[1/4] Killing all python servers..."
# Kill every possible python server pattern
for pattern in "python.*8000" "server_v[0-9]" "liljr_os" "server_v8" "server" "liljr.*py" "python3.*server"; do
    pkill -9 -f "$pattern" 2>/dev/null
    pkill -f "$pattern" 2>/dev/null
done
# Also kill nohup and watchdog
pkill -9 -f "nohup.*python" 2>/dev/null
pkill -9 -f "immortal_watchdog" 2>/dev/null
pkill -9 -f "watchdog" 2>/dev/null

echo "[1/4] Waiting for port 8000 to release..."
for i in 1 2 3 4 5; do
    sleep 1
    # Check if anything still on port 8000
    PID=$(lsof -ti:8000 2>/dev/null || netstat -tlnp 2>/dev/null | grep 8000 | awk '{print $NF}' | cut -d'/' -f1 || ss -tlnp 2>/dev/null | grep 8000 | grep -oP 'pid=\K[0-9]+' || echo "")
    if [ -z "$PID" ]; then
        echo "[1/4] Port 8000 is free."
        break
    else
        echo "[1/4] Port still held by PID $PID — killing..."
        kill -9 "$PID" 2>/dev/null
    fi
done

# ═══ STEP 2: START SERVER ═══
echo ""
echo "[2/4] Starting server..."
# Acquire wake lock	ermux-wake-lock 2>/dev/null || true

# Clear old startup log
> "$STARTUP_LOG"

# Start server with nohup, redirect ALL output to log
nohup python3 "$SERVER" > "$STARTUP_LOG" 2>&1 &
SERVER_PID=$!
echo "[2/4] Server PID: $SERVER_PID"

# ═══ STEP 3: WAIT FOR SERVER ═══
echo ""
echo "[3/4] Waiting for server to come alive..."
MAX_WAIT=30
for i in $(seq 1 $MAX_WAIT); do
    sleep 1
    
    # Check if process is still alive
    if ! kill -0 "$SERVER_PID" 2>/dev/null; then
        echo "[3/4] ⚠️ Server process died! Check $STARTUP_LOG"
        echo "[3/4] Last 20 lines of startup log:"
        tail -20 "$STARTUP_LOG" 2>/dev/null
        echo ""
        echo "❌ REVIVE FAILED — Server crashed on startup"
        exit 1
    fi
    
    # Try health check
    HEALTH=$(curl -s --max-time 2 "$HEALTH_URL" 2>/dev/null || echo "")
    if echo "$HEALTH" | grep -q "liljr-empire"; then
        echo "[3/4] ✅ Server alive after ${i}s"
        echo "[3/4] Health: $HEALTH"
        break
    fi
    
    if [ $i -eq $MAX_WAIT ]; then
        echo "[3/4] ⚠️ Server didn't respond in ${MAX_WAIT}s"
        echo "[3/4] Startup log last 20 lines:"
        tail -20 "$STARTUP_LOG" 2>/dev/null
        echo ""
        echo "❌ REVIVE FAILED — Server not responding"
        exit 1
    fi
done

# ═══ STEP 4: FINAL CHECK ═══
echo ""
echo "[4/4] Final verification..."
FINAL=$(curl -s --max-time 3 "$HEALTH_URL" 2>/dev/null)
if echo "$FINAL" | grep -q "liljr-empire"; then
    echo "[4/4] ✅ EMPIRE ONLINE"
    echo ""
    echo "═══════════════════════════════════════════════════"
    echo "✅ LILJR IS ALIVE AND RESPONDING"
    echo "═══════════════════════════════════════════════════"
    echo ""
    echo "Server PID: $SERVER_PID"
    echo "Health: $FINAL"
    echo ""
    echo "Ready for commands:"
    echo "  liljr talk"
    echo "  liljr build 'FitLife' 'Tagline'"
    echo "  liljr buy AAPL 5"
    echo "═══════════════════════════════════════════════════"
    exit 0
else
    echo "❌ Server not responding to final check"
    exit 1
fi
