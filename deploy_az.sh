#!/bin/bash
# ═══════════════════════════════════════════════════════════════
# LILJR A-to-Z DEPLOYER — Build Everything
# Run once: bash deploy_az.sh
# Then: liljr (any command) — universal launcher
# ═══════════════════════════════════════════════════════════════

REPO="$HOME/liljr-autonomous"
HOME_LJ="$HOME"

echo ""
echo "☢️ LILJR A-to-Z DEPLOYER — Building everything..."
echo "═══════════════════════════════════════════════════════"

# ═══ 1. KILL ALL OLD ═══
echo ""
echo "[1/10] Killing old processes..."
pkill -9 -f "python.*server" 2>/dev/null
pkill -9 -f "server_v[0-9]" 2>/dev/null
pkill -9 -f "liljr_os" 2>/dev/null
pkill -9 -f "watchdog" 2>/dev/null
pkill -9 -f "nohup" 2>/dev/null
sleep 2

# ═══ 2. PULL LATEST ═══
echo ""
echo "[2/10] Pulling latest code..."
cd "$REPO" 2>/dev/null || exit 1
git pull origin main 2>&1 | tail -3

# ═══ 3. COPY ALL FILES TO HOME ═══
echo ""
echo "[3/10] Copying to home..."
cp "$REPO/liljr_consciousness.py" "$HOME_LJ/"
cp "$REPO/liljr_executor.py" "$HOME_LJ/"
cp "$REPO/liljr_native.py" "$HOME_LJ/"
cp "$REPO/liljr_push_brain.py" "$HOME_LJ/"
cp "$REPO/lj_empire.py" "$HOME_LJ/"
cp "$REPO/server_v8.py" "$HOME_LJ/"
cp "$REPO/quickfire.py" "$HOME_LJ/"
cp "$REPO/persona_engine.py" "$HOME_LJ/"
cp "$REPO/vision_engine.py" "$HOME_LJ/"
cp "$REPO/web_builder_v2.py" "$HOME_LJ/"
cp "$REPO/auto_coder.py" "$HOME_LJ/"
cp "$REPO/marketing_engine.py" "$HOME_LJ/"
cp "$REPO/deep_search.py" "$HOME_LJ/"
cp "$REPO/self_awareness_v2.py" "$HOME_LJ/"
cp "$REPO/autonomous_loop.py" "$HOME_LJ/"
cp "$REPO/natural_language.py" "$HOME_LJ/"
cp "$REPO/bulletproof_start.sh" "$HOME_LJ/"
cp "$REPO/immortal_watchdog.sh" "$HOME_LJ/"
cp "$REPO/unstoppable_reset.sh" "$HOME_LJ/"
cp "$REPO/integrate_boot.sh" "$HOME_LJ/"
cp "$REPO/hard_reset.sh" "$HOME_LJ/"
cp "$REPO/verify.py" "$HOME_LJ/"
cp "$REPO/diagnostic.py" "$HOME_LJ/"
chmod +x "$HOME_LJ"/*.sh
chmod +x "$HOME_LJ"/lj_empire.py

# ═══ 4. CREATE UNIVERSAL LAUNCHER ═══
echo ""
echo "[4/10] Creating universal launcher..."
cat > "$HOME_LJ/.liljr_launcher" << 'LAUNCHER'
#!/bin/bash
# LilJR Universal Launcher — liljr <command>

REPO="$HOME/liljr-autonomous"

case "$1" in
  # SERVER
  start)
    bash "$REPO/bulletproof_start.sh"
    ;;
  stop)
    pkill -9 -f "python.*8000"
    pkill -9 -f "server_v[0-9]"
    pkill -9 -f "liljr_os"
    pkill -9 -f "watchdog"
    echo "Killed all."
    ;;
  restart)
    pkill -9 -f "python.*8000"
    pkill -9 -f "server_v[0-9]"
    pkill -9 -f "liljr_os"
    sleep 2
    bash "$REPO/bulletproof_start.sh"
    ;;
  status)
    curl -s --max-time 3 http://localhost:8000/api/health 2>/dev/null || echo "Server offline"
    ;;
  immortal)
    nohup bash "$REPO/immortal_watchdog.sh" >/dev/null 2>&1 &
    echo "Immortal watchdog started."
    ;;

  # TRADING
  buy)
    python3 "$HOME/lj_empire.py" buy "$2" "$3"
    ;;
  sell)
    python3 "$HOME/lj_empire.py" sell "$2" "$3"
    ;;
  price)
    python3 "$HOME/lj_empire.py" price "$2"
    ;;
  portfolio)
    python3 "$HOME/lj_empire.py" portfolio
    ;;

  # BUILDING
  build|site|landing)
    shift
    python3 "$HOME/lj_empire.py" landing "$@"
    ;;
  app|webapp)
    shift
    python3 "$HOME/lj_empire.py" web-app "$@"
    ;;

  # CODE + EXECUTE
  code|coder)
    shift
    python3 "$HOME/lj_empire.py" coder-generate "$@"
    ;;
  run|execute)
    shift
    python3 "$HOME/liljr_consciousness.py" "execute $@"
    ;;

  # SEARCH
  search|find)
    shift
    python3 "$HOME/lj_empire.py" deep-search "$@"
    ;;
  google)
    shift
    python3 "$HOME/lj_empire.py" search "$@"
    ;;

  # MARKETING
  copy|market|ad)
    shift
    python3 "$HOME/lj_empire.py" marketing "$@"
    ;;
  seo)
    shift
    python3 "$HOME/lj_empire.py" calendar "$@"
    ;;

  # SELF + AI
  scan|health)
    python3 "$HOME/lj_empire.py" self-scan
    ;;
  fix|heal)
    python3 "$HOME/lj_empire.py" self-improve
    ;;
  think|loop)
    python3 "$HOME/lj_empire.py" autonomous-start
    ;;

  # PERSONA
  voice|persona)
    shift
    python3 "$HOME/lj_empire.py" persona "$@"
    ;;
  mimic)
    python3 "$HOME/lj_empire.py" persona mimic
    ;;

  # VISION
  see|camera)
    python3 "$HOME/lj_empire.py" vision describe
    ;;

  # QUICKFIRE
  qf|quick)
    shift
    python3 "$HOME/lj_empire.py" qf "$@"
    ;;

  # NATIVE PHONE
  phone|native)
    shift
    python3 "$HOME/liljr_native.py" "$@"
    ;;
  notify)
    shift
    termux-notification --title "LilJR" --content "$*" --priority normal 2>/dev/null || echo "Notification: $*"
    ;;
  speak)
    shift
    termux-tts-speak "$*" 2>/dev/null || echo "Speaking: $*"
    ;;

  # PUSH BRAIN
  push)
    shift
    python3 "$HOME/liljr_push_brain.py" push "$@"
    ;;
  inbox)
    ls ~/liljr_inbox/ 2>/dev/null || echo "Inbox empty"
    ;;

  # CONSCIOUSNESS
  talk|chat)
    shift
    python3 "$HOME/liljr_consciousness.py" "$@"
    ;;
  awake|wake)
    python3 "$HOME/liljr_consciousness.py"
    ;;

  # UTILITIES
  log|logs)
    tail -20 ~/liljr.log 2>/dev/null || echo "No logs"
    ;;
  empire)
    python3 "$HOME/lj_empire.py" empire
    ;;
  backup)
    python3 "$HOME/lj_empire.py" backup
    ;;
  verify)
    python3 "$HOME/verify.py"
    ;;
  reset|nuclear)
    bash "$HOME/unstoppable_reset.sh"
    ;;
  boot|integrate)
    bash "$REPO/integrate_boot.sh"
    ;;

  # HELP
  help|''|*)
    cat << 'HELP'
╔══════════════════════════════════════════════════════════════╗
║           LILJR UNIVERSAL COMMANDER — A to Z                ║
╠══════════════════════════════════════════════════════════════╣
║ SERVER                                                       ║
║   liljr start        — Start empire server                 ║
║   liljr stop         — Kill everything                       ║
║   liljr restart      — Nuclear restart                     ║
║   liljr immortal     — Start immortal watchdog              ║
║   liljr status       — Health check                        ║
╠══════════════════════════════════════════════════════════════╣
║ TRADE                                                        ║
║   liljr buy AAPL 5   — Buy stock                            ║
║   liljr sell TSLA 3  — Sell stock                           ║
║   liljr price NVDA   — Check price                          ║
║   liljr portfolio    — Full portfolio                       ║
╠══════════════════════════════════════════════════════════════╣
║ BUILD                                                        ║
║   liljr build "FitLife" "Tagline" — Build landing page      ║
║   liljr app "MyApp" — Build web app                         ║
╠══════════════════════════════════════════════════════════════╣
║ CODE + EXECUTE                                               ║
║   liljr code "function to sort" — Generate code             ║
║   liljr run "calculate sum" — Execute auto-pipeline         ║
╠══════════════════════════════════════════════════════════════╣
║ SEARCH                                                       ║
║   liljr search "AI trends" — Deep web search                ║
║   liljr google "question" — Quick search                     ║
╠══════════════════════════════════════════════════════════════╣
║ MARKET                                                       ║
║   liljr copy "Product" — Generate marketing                 ║
║   liljr seo "Topic" — SEO content                           ║
╠══════════════════════════════════════════════════════════════╣
║ SELF + AI                                                    ║
║   liljr scan         — Self-awareness scan                  ║
║   liljr fix          — Auto-heal                           ║
║   liljr think        — Start autonomous loop              ║
╠══════════════════════════════════════════════════════════════╣
║ PERSONA                                                      ║
║   liljr persona list — Show voices                        ║
║   liljr persona switch best_friend — Change voice           ║
║   liljr mimic        — Copy your speech                    ║
╠══════════════════════════════════════════════════════════════╣
║ VISION                                                       ║
║   liljr see          — Describe camera view                ║
╠══════════════════════════════════════════════════════════════╣
║ QUICKFIRE                                                    ║
║   liljr qf "build me a site" — One-shot everything          ║
╠══════════════════════════════════════════════════════════════╣
║ PHONE                                                        ║
║   liljr phone status — Battery, storage, WiFi              ║
║   liljr notify "msg" — Send notification                    ║
║   liljr speak "hello" — Text-to-speech                      ║
╠══════════════════════════════════════════════════════════════╣
║ PUSH BRAIN                                                   ║
║   liljr push "command" — Push to inbox                      ║
╠══════════════════════════════════════════════════════════════╣
║ CONSCIOUSNESS                                                ║
║   liljr talk "hello" — Interactive mode                      ║
║   liljr awake        — Start consciousness                  ║
╠══════════════════════════════════════════════════════════════╣
║ UTILITIES                                                    ║
║   liljr log          — Show last 20 log lines               ║
║   liljr empire       — Full empire status                   ║
║   liljr backup       — Manual backup                        ║
║   liljr verify       — Run system verification              ║
║   liljr reset        — Nuclear reset                        ║
║   liljr boot         — Integrate into phone                 ║
╚══════════════════════════════════════════════════════════════╝

Examples:
  liljr build "FitLife" "Guaranteed gains, no BS"
  liljr run "build a dice roller and roll it"
  liljr qf "buy 5 AAPL"
  liljr search "crypto trends 2026"
  liljr code "API endpoint for login"
HELP
    ;;
esac
LAUNCHER

chmod +x "$HOME_LJ/.liljr_launcher"

# ═══ 5. ADD TO PATH ═══
echo ""
echo "[5/10] Adding to PATH..."
BASHRC="$HOME/.bashrc"
ZSHRC="$HOME/.zshrc"

for RC in "$BASHRC" "$ZSHRC"; do
    if [ -f "$RC" ]; then
        if ! grep -q "alias liljr=" "$RC" 2>/dev/null; then
            echo "" >> "$RC"
            echo "# === LILJR A-to-Z COMMANDER ===" >> "$RC"
            echo 'alias liljr="bash $HOME/.liljr_launcher"' >> "$RC"
            echo 'alias lj="bash $HOME/.liljr_launcher"' >> "$RC"
            echo 'alias ljr="bash $HOME/.liljr_launcher"' >> "$RC"
            echo "# === END LILJR ===" >> "$RC"
        fi
    fi
done

# ═══ 6. CREATE DIRECTORIES ═══
echo ""
echo "[6/10] Creating directories..."
mkdir -p "$HOME/liljr_inbox" "$HOME/liljr_outbox" "$HOME/liljr_processed"
mkdir -p "$HOME/liljr_executions" "$HOME/liljr_backups"
mkdir -p "$REPO/web" "$REPO/plugins"

# ═══ 7. BOOT INTEGRATION ═══
echo ""
echo "[7/10] Boot integration..."
bash "$REPO/integrate_boot.sh" >/dev/null 2>&1 || true

# ═══ 8. START SERVER ═══
echo ""
echo "[8/10] Starting empire server..."
bash "$REPO/bulletproof_start.sh" >/dev/null 2>&1 &
sleep 5

# ═══ 9. START PUSH BRAIN ═══
echo ""
echo "[9/10] Starting push brain..."
nohup python3 "$HOME/liljr_push_brain.py" start >"$HOME/liljr_push.log" 2>&1 &
sleep 1

# ═══ 10. VERIFY ═══
echo ""
echo "[10/10] Verification..."
HEALTH=$(curl -s --max-time 3 http://localhost:8000/api/health 2>/dev/null)
if echo "$HEALTH" | grep -q "liljr-empire"; then
    echo "✅ SERVER ONLINE"
else
    echo "⚠️ Server starting... check ~/liljr_startup.log"
fi

# ═══ DONE ═══
echo ""
echo "═══════════════════════════════════════════════════════"
echo "✅ LILJR A-to-Z DEPLOY COMPLETE"
echo "═══════════════════════════════════════════════════════"
echo ""
echo "Every LilJR command now works as:"
echo "  liljr <command>        ← short"
echo "  lj <command>            ← shorter"
echo "  ljr <command>           ← shortest"
echo ""
echo "Try these right now:"
echo '  liljr build "FitLife" "No subscription maze"'
echo '  liljr run "calculate sum of 1 to 100"'
echo '  liljr qf "buy 5 AAPL"'
echo '  liljr search "AI trends"'
echo '  liljr persona switch best_friend'
echo '  liljr talk'
echo '  liljr phone status'
echo ""
echo "The phone is now LilJR's home."
echo "Open Termux → LilJR auto-starts."
echo "═══════════════════════════════════════════════════════"
echo ""
echo "Reload your shell to activate aliases:"
echo "  source ~/.bashrc"
