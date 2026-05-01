#!/bin/bash
# ═══════════════════════════════════════════════════════════════
# LILJR TEST BUILD — One script, no thinking, just works
# ═══════════════════════════════════════════════════════════════

echo "☢️ LILJR TEST — Building FitLife landing page..."
echo ""

# Make sure server is running
HEALTH=$(curl -s --max-time 2 http://localhost:8000/api/health 2>/dev/null)
if ! echo "$HEALTH" | grep -q "liljr-empire"; then
    echo "Server not running. Starting..."
    python3 ~/server_v8.py > ~/server_direct.log 2>&1 &
    sleep 10
fi

# Build the page
echo "Building..."
RESULT=$(curl -s --max-time 15 -X POST http://localhost:8000/api/web/build \
    -H "Content-Type: application/json" \
    -d '{"name":"FitLife","tagline":"Guaranteed results, no subscription maze","theme":"dark_empire"}' 2>/dev/null)

echo ""
echo "═══════════════════════════════════════════════════"
echo "RESULT:"
echo "$RESULT" | python3 -m json.tool 2>/dev/null || echo "$RESULT"
echo "═══════════════════════════════════════════════════"

# Show the file
if echo "$RESULT" | grep -q "saved"; then
    echo ""
    echo "✅ PAGE BUILT SUCCESSFULLY"
    echo ""
    echo "File saved. Listing web directory:"
    ls -la ~/liljr-autonomous/web/*.html 2>/dev/null || ls -la ~/web/*.html 2>/dev/null || echo "Check web/ directory"
fi
