#!/bin/bash
# update_lj.sh — Update the ~/lj command to launch voice mode by default

echo "Updating ~/lj launcher..."

cat > ~/lj << 'EOF'
#!/bin/bash
# ~/lj — LilJR Unified Launcher (v92.0 VOICE)

export PATH="$HOME/.local/bin:$PATH"
REPO="$HOME/liljr-autonomous"

if [ ! -d "$REPO" ]; then
    echo "Cloning LilJR repo..."
    cd "$HOME"
    git clone https://github.com/signsafepro-create/liljr-autonomous.git "$REPO"
fi

cd "$REPO"

case "$1" in
    voice|talk|speak|live)
        bash liljr_voice_boot.sh
        ;;
    start|boot|wake)
        bash liljr_voice_boot.sh
        ;;
    server)
        python3 liljr_v90_omni.py --server
        ;;
    status)
        curl -s http://localhost:7777/api/omni/status 2>/dev/null | python3 -m json.tool 2>/dev/null || echo "OMNI offline"
        ;;
    stop|kill)
        pkill -f "liljr_v90_omni"
        pkill -f "liljr_voice_daemon"
        echo "LilJR stopped."
        ;;
    buy)
        shift
        curl -s -X POST http://localhost:7777/api/omni/command -H "Content-Type: application/json" -d "{\"command\":\"buy $*\"}" 2>/dev/null | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('message','Done'))" 2>/dev/null
        ;;
    sell)
        shift
        curl -s -X POST http://localhost:7777/api/omni/command -H "Content-Type: application/json" -d "{\"command\":\"sell $*\"}" 2>/dev/null | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('message','Done'))" 2>/dev/null
        ;;
    price)
        shift
        curl -s -X POST http://localhost:7777/api/omni/command -H "Content-Type: application/json" -d "{\"command\":\"price $*\"}" 2>/dev/null | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('message','Done'))" 2>/dev/null
        ;;
    portfolio)
        curl -s -X POST http://localhost:7777/api/omni/command -H "Content-Type: application/json" -d '{"command":"portfolio"}' 2>/dev/null | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('message','Done'))" 2>/dev/null
        ;;
    push)
        cd "$REPO" && git add -A && git commit -m "Auto-save $(date)" && git push origin main
        ;;
    *)
        echo "🧬 LILJR v92.0 — VOICE LIFE"
        echo ""
        echo "Usage: lj <command>"
        echo ""
        echo "  lj start        → Wake up LilJR (voice mode)"
        echo "  lj voice        → Same as start"
        echo "  lj server       → Run OMNI server only"
        echo "  lj status       → Check OMNI status"
        echo "  lj stop         → Kill everything"
        echo "  lj buy AAPL 10  → Buy stock"
        echo "  lj sell all     → Sell everything"
        echo "  lj portfolio    → View positions"
        echo "  lj push         → Push to GitHub"
        echo ""
        echo "Just say: 'lj start' and talk to him."
        ;;
esac
EOF

chmod +x ~/lj
echo "✅ ~/lj updated to v92.0 VOICE"
