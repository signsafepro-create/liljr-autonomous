#!/bin/bash
# ═══════════════════════════════════════════════════════════════
# LILJR RUN — One script. Kills old. Copies new. Starts server. Runs consciousness.
# ═══════════════════════════════════════════════════════════════

REPO="$HOME/liljr-autonomous"

echo "☢️ LILJR RUN — Fresh start. No old code."
echo ""

# 1. KILL EVERYTHING
echo "[1/4] Killing all old processes..."
pkill -9 -f "python.*8000" 2>/dev/null
pkill -9 -f "server_v[0-9]" 2>/dev/null
pkill -9 -f "liljr_os" 2>/dev/null
pkill -9 -f "python3.*consciousness" 2>/dev/null
sleep 2

# 2. COPY LATEST FILES FROM REPO
echo "[2/4] Copying latest files..."
cp "$REPO/server_v8.py" "$HOME/server_v8.py"
cp "$REPO/liljr_consciousness.py" "$HOME/liljr_consciousness.py"
cp "$REPO/lj_empire.py" "$HOME/lj_empire.py"
cp "$REPO/liljr_executor.py" "$HOME/liljr_executor.py"
cp "$REPO/liljr_native.py" "$HOME/liljr_native.py"
cp "$REPO/liljr_push_brain.py" "$HOME/liljr_push_brain.py"
cp "$REPO/quickfire.py" "$HOME/quickfire.py"
cp "$REPO/persona_engine.py" "$HOME/persona_engine.py"
cp "$REPO/vision_engine.py" "$HOME/vision_engine.py"
cp "$REPO/web_builder_v2.py" "$HOME/web_builder_v2.py"
cp "$REPO/auto_coder.py" "$HOME/auto_coder.py"
cp "$REPO/marketing_engine.py" "$HOME/marketing_engine.py"
cp "$REPO/deep_search.py" "$HOME/deep_search.py"
cp "$REPO/self_awareness_v2.py" "$HOME/self_awareness_v2.py"
cp "$REPO/autonomous_loop.py" "$HOME/autonomous_loop.py"
cp "$REPO/natural_language.py" "$HOME/natural_language.py"

# 3. START SERVER
echo "[3/4] Starting empire server..."
python3 "$HOME/server_v8.py" > "$HOME/server.log" 2>&1 &
PID=$!
echo "Server PID: $PID"

# Wait for it
echo "Waiting for server..."
for i in 1 2 3 4 5 6 7 8 9 10; do
    sleep 1
    HEALTH=$(curl -s --max-time 2 http://localhost:8000/api/health 2>/dev/null || echo "")
    if echo "$HEALTH" | grep -q "liljr-empire"; then
        echo "✅ Server online after ${i}s"
        break
    fi
done

# 4. VERIFY AND LAUNCH
echo ""
echo "[4/4] Verification..."
HEALTH=$(curl -s --max-time 3 http://localhost:8000/api/health 2>/dev/null)
if echo "$HEALTH" | grep -q "liljr-empire"; then
    echo "✅ EMPIRE ONLINE"
    echo "Health: $HEALTH"
    echo ""
    echo "═══════════════════════════════════════════════════"
    echo "✅ LILJR IS READY"
    echo "═══════════════════════════════════════════════════"
    echo ""
    echo "Now launching consciousness..."
    echo ""
    # Run consciousness
    python3 "$HOME/liljr_consciousness.py"
else
    echo "❌ Server not responding. Check ~/server.log"
    tail -20 "$HOME/server.log"
fi
