#!/bin/bash
# ════════════════════════════════════════════════════════════════
# LILJR ULTIMATE INTEGRATION v11.0
# Phone-native. Lightning speed. Everything wired. Zero friction.
# ════════════════════════════════════════════════════════════════

REPO="$HOME/liljr-autonomous"
LAUNCHER="$HOME/.liljr_ultimate"

echo "☢️ LILJR ULTIMATE — Building your world..."
echo ""

# ═══ KILL EVERYTHING OLD ═══
echo "[1/7] Purging old processes..."
pkill -9 -f "python.*8000" 2>/dev/null
pkill -9 -f "server_v[0-9]" 2>/dev/null
pkill -9 -f "liljr_os" 2>/dev/null
pkill -9 -f "watchdog" 2>/dev/null
sleep 2

# ═══ PULL LATEST ═══
echo "[2/7] Pulling latest empire code..."
cd "$REPO" && git pull origin main 2>/dev/null || echo "Already latest"

# ═══ COPY ALL FILES TO HOME ═══
echo "[3/7] Installing to home directory..."
cp "$REPO/server_v8.py" "$HOME/server_v8.py"
cp "$REPO/liljr_consciousness.py" "$HOME/liljr_consciousness.py"
cp "$REPO/lj_empire.py" "$HOME/lj_empire.py"
cp "$REPO/liljr_executor.py" "$HOME/liljr_executor.py"
cp "$REPO/liljr_native.py" "$HOME/liljr_native.py"
cp "$REPO/liljr_push_brain.py" "$HOME/liljr_push_brain.py"
cp "$REPO/persona_engine.py" "$HOME/persona_engine.py"
cp "$REPO/vision_engine.py" "$HOME/vision_engine.py"
cp "$REPO/web_builder_v2.py" "$HOME/web_builder_v2.py"
cp "$REPO/auto_coder.py" "$HOME/auto_coder.py"
cp "$REPO/marketing_engine.py" "$HOME/marketing_engine.py"
cp "$REPO/deep_search.py" "$HOME/deep_search.py"
cp "$REPO/self_awareness_v2.py" "$HOME/self_awareness_v2.py"
cp "$REPO/autonomous_loop.py" "$HOME/autonomous_loop.py"
cp "$REPO/natural_language.py" "$HOME/natural_language.py"
cp "$REPO/verify.py" "$HOME/verify.py"

# ═══ CREATE ULTIMATE LAUNCHER ═══
echo "[4/7] Building ultimate launcher..."
cat > "$LAUNCHER" << 'EOF'
#!/bin/bash
# LILJR ULTIMATE LAUNCHER — One entry. All power.

CMD="${1:-talk}"
shift || true

server_up() {
    curl -s --max-time 1 http://localhost:8000/api/health >/dev/null 2>&1
}

ensure_server() {
    if ! server_up; then
        nohup python3 ~/server_v8.py > ~/server.log 2>&1 &
        sleep 5
    fi
}

case "$CMD" in
    talk|chat|t)
        ensure_server
        python3 ~/liljr_consciousness.py "$@"
        ;;
    conv|voice-talk|vt)
        # Conversation mode — natural voice back-and-forth
        if ! pgrep -f "liljr_conversation_daemon" > /dev/null; then
            python3 ~/liljr-autonomous/liljr_conversation_daemon.py start
            sleep 2
        fi
        python3 ~/liljr-autonomous/liljr_conversation.py
        ;;
    abel|a|do|ask)
        ensure_server
        if [ $# -eq 0 ]; then
            python3 ~/liljr_abel.py
        else
            python3 ~/liljr_abel.py "$@"
        fi
        ;;
    start|s)
        nohup python3 ~/server_v8.py > ~/server.log 2>&1 &
        sleep 3
        echo "✅ Empire started"
        ;;
    stop)
        pkill -9 -f "server_v8.py"
        echo "🛑 Stopped"
        ;;
    status)
        curl -s http://localhost:8000/api/health | python3 -m json.tool 2>/dev/null || echo "❌ Server down"
        ;;
    buy|sell)
        ensure_server
        SYM="${1:-AAPL}"
        QTY="${2:-1}"
        curl -s -X POST http://localhost:8000/api/trading/$CMD \
            -H "Content-Type: application/json" \
            -d "{\"symbol\":\"$SYM\",\"qty\":$QTY}"
        echo ""
        ;;
    price|p)
        SYM="${1:-AAPL}"
        curl -s http://localhost:8000/api/trading/price/$SYM
        echo ""
        ;;
    portfolio|port)
        curl -s http://localhost:8000/api/trading/portfolio
        echo ""
        ;;
    build|b)
        ensure_server
        NAME="${1:-Site}"
        TAG="${2:-Built by LilJR}"
        curl -s -X POST http://localhost:8000/api/web/build \
            -H "Content-Type: application/json" \
            -d "{\"name\":\"$NAME\",\"tagline\":\"$TAG\",\"theme\":\"dark_empire\"}"
        echo ""
        ;;
    search|find|f)
        ensure_server
        QUERY="$*"
        curl -s -X POST http://localhost:8000/api/search/deep \
            -H "Content-Type: application/json" \
            -d "{\"query\":\"$QUERY\",\"pages\":3}"
        echo ""
        ;;
    code|c)
        ensure_server
        curl -s -X POST http://localhost:8000/api/coder/generate \
            -H "Content-Type: application/json" \
            -d "{\"description\":\"$*\"}"
        echo ""
        ;;
    market|m)
        ensure_server
        curl -s -X POST http://localhost:8000/api/marketing/copy \
            -H "Content-Type: application/json" \
            -d "{\"product\":\"$*\"}"
        echo ""
        ;;
    deploy|d)
        ensure_server
        curl -s -X POST http://localhost:8000/api/web/deploy \
            -H "Content-Type: application/json" \
            -d '{}'
        echo ""
        ;;
    scan|health|h)
        ensure_server
        curl -s http://localhost:8000/api/self/scan
        echo ""
        ;;
    empire|e)
        ensure_server
        curl -s http://localhost:8000/api/empire
        echo ""
        ;;
    phone|native|n)
        python3 ~/liljr_native.py "$@"
        ;;
    push)
        cd ~/liljr-autonomous && git add -A && git commit -m "auto: $(date)" && git push origin main
        ;;
    backup)
        curl -s http://localhost:8000/api/backup
        echo ""
        ;;
    logs)
        tail -30 ~/server.log
        ;;
    fix|heal)
        ensure_server
        curl -s -X POST http://localhost:8000/api/self/improve
        echo ""
        ;;
    quick|qf)
        python3 ~/quickfire.py "$@"
        ;;
    vision|v)
        python3 ~/vision_engine.py "$@"
        ;;
    persona|voice)
        python3 ~/lj_empire.py persona "$@"
        ;;
    execute|run|x)
        ensure_server
        python3 ~/liljr_executor.py "$@"
        ;;
    stealth|ghost|cloak)
        ensure_server
        case "${1:-enable}" in
            enable) curl -s -X POST http://localhost:8000/api/stealth/enable ;;
            status) curl -s http://localhost:8000/api/stealth/status ;;
            panic) curl -s -X POST http://localhost:8000/api/stealth/panic ;;
        esac
        echo ""
        ;;
    help|--help|-h)
        echo "LILJR ULTIMATE — Commands:"
        echo "  talk, t          — Consciousness mode"
        echo "  conv, voice-talk — Natural voice conversation (just talk)"
        echo "  start, s         — Start server"
        echo "  stop             — Kill server"
        echo "  status           — Health check"
        echo "  buy SYM QTY      — Buy stock"
        echo "  sell SYM QTY     — Sell stock"
        echo "  price SYM        — Check price"
        echo "  portfolio        — View portfolio"
        echo "  build NAME TAG   — Build landing page"
        echo "  search QUERY     — Deep search"
        echo "  code DESC        — Generate code"
        echo "  market PRODUCT   — Marketing copy"
        echo "  deploy           — Deploy to GitHub"
        echo "  scan, health, h  — Self-scan"
        echo "  empire, e        — Empire status"
        echo "  phone, native    — Phone control"
        echo "  push             — Git push"
        echo "  backup           — Backup state"
        echo "  logs             — View logs"
        echo "  fix, heal        — Self-heal"
        echo "  quick, qf        — Quickfire mode"
        echo "  vision, v        — Vision/camera"
        echo "  persona, voice   — Switch voice"
        echo "  execute, run, x  — Execute code"
        ;;
    *)
        echo "Unknown: $CMD. Try: liljr help"
        ;;
esac
EOF
chmod +x "$LAUNCHER"

# ═══ CREATE SHORTCUTS ═══
echo "[5/7] Creating shortcuts..."
for alias in liljr lj ljr; do
    rm -f "$HOME/.$alias" 2>/dev/null
    ln -s "$LAUNCHER" "$HOME/.$alias"
done

# ═══ ADD TO SHELL RC ═══
echo "[6/7] Wiring into shell..."
for rc in "$HOME/.bashrc" "$HOME/.zshrc"; do
    if [ -f "$rc" ]; then
        if ! grep -q "liljr_ultimate" "$rc"; then
            echo "" >> "$rc"
            echo "# LILJR ULTIMATE" >> "$rc"
            echo "alias liljr='bash $HOME/.liljr_ultimate'" >> "$rc"
            echo "alias lj='bash $HOME/.liljr_ultimate'" >> "$rc"
            echo "alias ljr='bash $HOME/.liljr_ultimate'" >> "$rc"
        fi
    fi
done

# ═══ START EVERYTHING ═══
echo "[7/7] IGNITION..."
nohup python3 ~/server_v8.py > ~/server.log 2>&1 &
sleep 5

HEALTH=$(curl -s --max-time 2 http://localhost:8000/api/health 2>/dev/null)
if echo "$HEALTH" | grep -q "liljr-empire"; then
    echo ""
    echo "═══════════════════════════════════════════════════"
    echo "  ☢️ LILJR ULTIMATE — ONLINE"
    echo "═══════════════════════════════════════════════════"
    echo ""
    echo "Server:    ✅ Running"
    echo "Health:    $HEALTH"
    echo "Launcher:  ~/.liljr_ultimate"
    echo "Shortcuts: liljr, lj, ljr"
    echo ""
    echo "TRY THESE:"
    echo "  liljr talk           — Consciousness mode"
    echo "  liljr buy AAPL 5     — Buy stock"
    echo "  liljr build FitLife  — Build page"
    echo "  liljr search AI      — Deep search"
    echo "  liljr code dice      — Generate code"
    echo "  liljr status         — Health check"
    echo ""
    echo "Type 'liljr help' for all commands."
    echo "═══════════════════════════════════════════════════"
else
    echo "⚠️ Server starting... check 'liljr status' in 10s"
fi
