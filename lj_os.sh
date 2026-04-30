#!/bin/bash
# LILJR OS CLI — Wrapper that falls back to Python if curl is missing
# Usage: bash ~/lj_os <cmd> [args]

if command -v curl >/dev/null 2>&1; then
    # Use curl version (fast)
    BASE="http://localhost:8000"
    
    case "$1" in
      start)
        echo "🚀 Starting LilJR OS..."
        pkill -f "python.*server" 2>/dev/null
        pkill -f "liljr_os.py" 2>/dev/null
        sleep 1
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
      rule)
        curl -s -X POST "$BASE/api/rules" -H "Content-Type: application/json" -d "{\"symbol\":\"$2\",\"condition\":\"$3\",\"target_price\":$4,\"action\":\"$5\",\"qty\":${6:-1}}" && echo ""
        ;;
      rules)
        curl -s "$BASE/api/rules" && echo ""
        ;;
      run)
        curl -s -X POST "$BASE/api/rules/run" && echo ""
        ;;
      ai)
        shift; MSG="$*"
        curl -s -X POST "$BASE/api/ai/chat" -H "Content-Type: application/json" -d "{\"message\":\"$MSG\"}" && echo ""
        ;;
      search)
        shift; QUERY="$*"
        curl -s -X POST "$BASE/api/search" -H "Content-Type: application/json" -d "{\"query\":\"$QUERY\",\"count\":5}" && echo ""
        ;;
      fetch)
        curl -s -X POST "$BASE/api/fetch" -H "Content-Type: application/json" -d "{\"url\":\"$2\"}" && echo ""
        ;;
      learn)
        curl -s -X POST "$BASE/api/learn" -H "Content-Type: application/json" -d "{\"topic\":\"$2\",\"fact\":\"$3\"}" && echo ""
        ;;
      query)
        shift; QUESTION="$*"
        curl -s -X POST "$BASE/api/query" -H "Content-Type: application/json" -d "{\"question\":\"$QUESTION\"}" && echo ""
        ;;
      knowledge)
        curl -s "$BASE/api/knowledge" && echo ""
        ;;
      plugin)
        if [ -f "$3" ]; then CODE=$(cat "$3"); NAME="$2"; else NAME="$2"; echo "Enter code (Ctrl+D):"; CODE=$(cat); fi
        curl -s -X POST "$BASE/api/plugin/create" -H "Content-Type: application/json" -d "{\"name\":\"$NAME\",\"code\":\"$CODE\"}" && echo ""
        ;;
      run-plugin)
        curl -s -X POST "$BASE/api/plugin/run" -H "Content-Type: application/json" -d "{\"name\":\"$2\",\"args\":[$3]}" && echo ""
        ;;
      plugins)
        curl -s "$BASE/api/plugins" && echo ""
        ;;
      connect)
        NAME="$2"; URL="$3"; AUTH_TYPE="${4:-none}"; AUTH_TOKEN="${5:-}"
        curl -s -X POST "$BASE/api/connect/register" -H "Content-Type: application/json" -d "{\"name\":\"$NAME\",\"url\":\"$URL\",\"auth_type\":\"$AUTH_TYPE\",\"auth_token\":\"$AUTH_TOKEN\"}" && echo ""
        ;;
      disconnect)
        curl -s -X POST "$BASE/api/connect/remove" -H "Content-Type: application/json" -d "{\"name\":\"$2\"}" && echo ""
        ;;
      connections)
        curl -s "$BASE/api/connections" && echo ""
        ;;
      send)
        NAME="$2"; PATH="$3"; METHOD="${4:-GET}"; DATA="${5:-{}}"
        curl -s -X POST "$BASE/api/connect/send" -H "Content-Type: application/json" -d "{\"name\":\"$NAME\",\"path\":\"$PATH\",\"method\":\"$METHOD\",\"data\":$DATA}" && echo ""
        ;;
      discover)
        TARGET="$2"; [[ $TARGET == http* ]] || TARGET="http://$TARGET"
        ENCODED=$(python3 -c "import urllib.parse; print(urllib.parse.quote('$TARGET'))")
        curl -s "$BASE/api/connect/discover/$ENCODED" && echo ""
        ;;
      platform-connect)
        PLATFORM="$2"; CREDENTIALS="$3"
        curl -s -X POST "$BASE/api/platform/connect" -H "Content-Type: application/json" -d "{\"platform\":\"$PLATFORM\",\"credentials\":$CREDENTIALS}" && echo ""
        ;;
      post)
        PLATFORM="$2"; CONTENT="$3"; EXTRA="${4:-{}}"
        curl -s -X POST "$BASE/api/platform/post" -H "Content-Type: application/json" -d "{\"platform\":\"$PLATFORM\",\"content\":\"$CONTENT\",\"extra\":$EXTRA}" && echo ""
        ;;
      cross-post)
        CONTENT="$2"; PLATFORMS="$3"
        IFS=',' read -ra ARR <<< "$PLATFORMS"
        JSON_PLATFORMS="[$(printf '\"%s",' "${ARR[@]}" | sed 's/,$//')]"
        curl -s -X POST "$BASE/api/platform/cross-post" -H "Content-Type: application/json" -d "{\"content\":\"$CONTENT\",\"platforms\":$JSON_PLATFORMS}" && echo ""
        ;;
      platforms)
        curl -s "$BASE/api/platform/list" && echo ""
        ;;
      save)
        curl -s "$BASE/api/health" && echo ""
        ;;
      help|"")
        echo "LilJR OS — curl available. Use: bash ~/lj_os <cmd>"
        echo "Or use Python CLI: python3 ~/lj_os.py <cmd>"
        ;;
      *)
        echo "Unknown: $1"; echo "Run: bash ~/lj_os help"
        ;;
    esac
else
    # No curl — use Python CLI instead
    python3 ~/lj_os.py "$@"
fi
