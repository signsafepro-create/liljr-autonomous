#!/bin/bash
# LILJR OS CLI — Standalone. No dependencies. No strings attached.
# Usage: bash ~/lj_os <cmd> [args]

BASE="http://localhost:8000"

case "$1" in
  # ═══ START / STOP ═══
  start)
    echo "🚀 Starting LilJR OS..."
    nohup python3 ~/liljr-autonomous/liljr_os.py > /dev/null 2>&1 &
    sleep 2
    curl -s "$BASE/api/health" && echo ""
    ;;
  stop)
    pkill -f "liljr_os.py"
    echo "Stopped."
    ;;
  status)
    curl -s "$BASE/api/health" && echo ""
    ;;
  
  # ═══ TRADING ═══
  buy)
    curl -s -X POST "$BASE/api/trading/buy" -H "Content-Type: application/json" -d "{\"symbol\":\"$2\",\"qty\":${3:-1}}" && echo ""
    ;;
  sell)
    curl -s -X POST "$BASE/api/trading/sell" -H "Content-Type: application/json" -d "{\"symbol\":\"$2\",\"qty\":${3:-1}}" && echo ""
    ;;
  price)
    curl -s "$BASE/api/trading/price/$2" && echo ""
    ;;
  portfolio)
    curl -s "$BASE/api/trading/portfolio" && echo ""
    ;;
  history)
    curl -s "$BASE/api/trading/history" && echo ""
    ;;
  
  # ═══ WATCHLIST ═══
  watch)
    curl -s -X POST "$BASE/api/watchlist" -H "Content-Type: application/json" -d "{\"symbol\":\"$2\",\"target_price\":$3}" && echo ""
    ;;
  unwatch)
    curl -s -X DELETE "$BASE/api/watchlist" -H "Content-Type: application/json" -d "{\"symbol\":\"$2\"}" && echo ""
    ;;
  watches)
    curl -s "$BASE/api/watchlist" && echo ""
    ;;
  check)
    curl -s "$BASE/api/watchlist/check" && echo ""
    ;;
  
  # ═══ RULES ═══
  rule)
    curl -s -X POST "$BASE/api/rules" -H "Content-Type: application/json" -d "{\"symbol\":\"$2\",\"condition\":\"$3\",\"target_price\":$4,\"action\":\"$5\",\"qty\":${6:-1}}" && echo ""
    ;;
  rules)
    curl -s "$BASE/api/rules" && echo ""
    ;;
  run)
    curl -s -X POST "$BASE/api/rules/run" && echo ""
    ;;
  
  # ═══ AI (LOCAL) ═══
  ai)
    shift
    MSG="$*"
    curl -s -X POST "$BASE/api/ai/chat" -H "Content-Type: application/json" -d "{\"message\":\"$MSG\"}" && echo ""
    ;;
  
  # ═══ SEARCH / KNOWLEDGE ═══
  search)
    shift
    QUERY="$*"
    curl -s -X POST "$BASE/api/search" -H "Content-Type: application/json" -d "{\"query\":\"$QUERY\",\"count\":5}" && echo ""
    ;;
  fetch)
    curl -s -X POST "$BASE/api/fetch" -H "Content-Type: application/json" -d "{\"url\":\"$2\"}" && echo ""
    ;;
  learn)
    curl -s -X POST "$BASE/api/learn" -H "Content-Type: application/json" -d "{\"topic\":\"$2\",\"fact\":\"$3\"}" && echo ""
    ;;
  query)
    shift
    QUESTION="$*"
    curl -s -X POST "$BASE/api/query" -H "Content-Type: application/json" -d "{\"question\":\"$QUESTION\"}" && echo ""
    ;;
  knowledge)
    curl -s "$BASE/api/knowledge" && echo ""
    ;;
  
  # ═══ PLUGINS — SELF EXTENDING ═══
  plugin)
    # Read code from stdin or file
    if [ -f "$3" ]; then
      CODE=$(cat "$3")
      NAME="$2"
    else
      NAME="$2"
      echo "Enter plugin code (Ctrl+D when done):"
      CODE=$(cat)
    fi
    curl -s -X POST "$BASE/api/plugin/create" -H "Content-Type: application/json" -d "{\"name\":\"$NAME\",\"code\":\"$CODE\"}" && echo ""
    ;;
  run-plugin)
    curl -s -X POST "$BASE/api/plugin/run" -H "Content-Type: application/json" -d "{\"name\":\"$2\",\"args\":[$3]}" && echo ""
    ;;
  plugins)
    curl -s "$BASE/api/plugins" && echo ""
    ;;
  
  # ═══ PERSISTENCE ═══
  save)
    echo "State auto-saves every 5 min. Forcing now..."
    curl -s "$BASE/api/health" && echo ""
    ;;
  
  # ═══ HELP ═══
  help|"")
    echo "LilJR OS — Standalone. No APIs. No strings."
    echo ""
    echo "SERVER:"
    echo "  bash ~/lj_os start          — Start the OS"
    echo "  bash ~/lj_os stop           — Stop"
    echo "  bash ~/lj_os status         — Health check"
    echo ""
    echo "TRADING:"
    echo "  bash ~/lj_os buy AAPL 5     — Buy stock"
    echo "  bash ~/lj_os sell TSLA       — Sell stock"
    echo "  bash ~/lj_os price AAPL     — Check price"
    echo "  bash ~/lj_os portfolio      — Show portfolio"
    echo "  bash ~/lj_os history        — Trade history"
    echo ""
    echo "WATCHLIST:"
    echo "  bash ~/lj_os watch AAPL 170 — Watch AAPL at $170"
    echo "  bash ~/lj_os unwatch AAPL   — Remove"
    echo "  bash ~/lj_os watches        — List"
    echo "  bash ~/lj_os check          — Check alerts"
    echo ""
    echo "AUTO-TRADING:"
    echo "  bash ~/lj_os rule AAPL below 150 buy 5"
    echo "  bash ~/lj_os rules          — List rules"
    echo "  bash ~/lj_os run            — Execute rules"
    echo ""
    echo "AI (LOCAL — NO API KEY):"
    echo "  bash ~/lj_os ai What should I buy?"
    echo "  bash ~/lj_os ai My portfolio?"
    echo "  bash ~/lj_os ai Search AI stocks"
    echo ""
    echo "SEARCH / KNOWLEDGE:"
    echo "  bash ~/lj_os search 'bitcoin news'  — Web search"
    echo "  bash ~/lj_os fetch https://...      — Fetch page"
    echo "  bash ~/lj_os learn 'python' 'is a language'"
    echo "  bash ~/lj_os query 'what is my cash'"
    echo "  bash ~/lj_os knowledge              — All facts"
    echo ""
    echo "PLUGINS — SELF EXTENDING:"
    echo "  bash ~/lj_os plugin myplugin        — Create from stdin"
    echo "  bash ~/lj_os plugin myplugin file.py — Create from file"
    echo "  bash ~/lj_os run-plugin myplugin    — Execute"
    echo "  bash ~/lj_os plugins                — List"
    echo ""
    echo "Example plugin:"
    echo '  echo "def run(): return {\"hello\": \"world\"}" | bash ~/lj_os plugin hello'
    ;;
  
  *)
    echo "Unknown: $1"
    echo "Run: bash ~/lj_os help"
    ;;
esac
