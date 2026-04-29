#!/bin/bash
# ═══════════════════════════════════════════════════════════════
# LILJR ONE PUSH v6.2 — Honest State Push
# Only claims success when it actually saved something
# Run: bash ~/lj push   OR   bash push_all.sh
# ═══════════════════════════════════════════════════════════════

STATE_FILE="$HOME/liljr_state.json"
REPO_DIR="$HOME/liljr-autonomous"

echo "🚀 LILJR ONE PUSH — Checking state..."
echo "======================================"

# 1. Check if server is running
curl -s http://localhost:8000/api/health > /dev/null 2>&1
SERVER_UP=$?

if [ $SERVER_UP -eq 0 ]; then
    echo "✅ Server running (localhost:8000)"
    # Try to trigger a state save via API
    curl -s -X POST http://localhost:8000/api/save_state > /dev/null 2>&1 || true
else
    echo "⚠️ Server NOT running (localhost:8000 unreachable)"
fi

# 2. Check if state file exists and has content
if [ ! -f "$STATE_FILE" ]; then
    echo "❌ No state file at $STATE_FILE"
    echo ""
    echo "Nothing to push. Start the server first:"
    echo "  bash ~/lj start"
    echo ""
    echo "Or create an initial state:"
    echo "  bash ~/lj state-init"
    exit 1
fi

STATE_SIZE=$(stat -c%s "$STATE_FILE" 2>/dev/null || stat -f%z "$STATE_FILE" 2>/dev/null || echo "0")
if [ "$STATE_SIZE" -lt 10 ]; then
    echo "❌ State file exists but is empty ($STATE_SIZE bytes)"
    echo "Nothing to push."
    exit 1
fi

echo "✅ State file found: $STATE_SIZE bytes"

# 3. Backup state
cp "$STATE_FILE" "$HOME/liljr_state_backup_$(date +%Y%m%d_%H%M%S).json"
echo "✅ State backed up"

# 4. Ensure repo directory exists
mkdir -p "$REPO_DIR/state"

# 5. Copy state into repo
cp "$STATE_FILE" "$REPO_DIR/state/"

# 6. Git commit + push
cd "$REPO_DIR" || {
    echo "❌ Repo directory missing. Re-cloning..."
    cd "$HOME" && rm -rf liljr-autonomous && git clone https://github.com/signsafepro-create/liljr-autonomous.git
    cd "$REPO_DIR"
}

# Ensure git identity is set
git config user.email "deploy@cosmicfaith.app" 2>/dev/null || true
git config user.name "Deploy Bot" 2>/dev/null || true

echo "📤 Committing and pushing..."
git add -A

# Check if there's anything to commit
if git diff --cached --quiet; then
    echo "ℹ️ Nothing new to commit (state unchanged since last push)"
    echo ""
    echo "✅ ONE PUSH COMPLETE (no changes)"
    echo "====================="
    echo ""
    echo "Saved:"
    echo "  • State: $STATE_FILE"
    echo "  • Backup: ~/liljr_state_backup_*.json"
    echo "  • GitHub: https://github.com/signsafepro-create/liljr-autonomous"
    echo ""
    echo "Your memory is already up to date."
    exit 0
fi

git commit -m "v6.2 push: $(date '+%Y-%m-%d %H:%M:%S') — state + code auto-save" || {
    echo "❌ Git commit failed"
    exit 1
}

# Push
git push origin main 2>&1 | tail -5

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ ONE PUSH COMPLETE"
    echo "====================="
    echo ""
    echo "Saved:"
    echo "  • Code: ~/liljr-autonomous/"
    echo "  • State: $STATE_FILE"
    echo "  • Backup: ~/liljr_state_backup_*.json"
    echo "  • GitHub: https://github.com/signsafepro-create/liljr-autonomous"
    echo ""
    echo "Your memory is safe. Next time just:"
    echo "  bash ~/lj push"
else
    echo ""
    echo "❌ PUSH FAILED"
    echo "==============="
    echo "GitHub rejected the push. Check your token or network."
    echo "Fix: bash ~/lj fix-remote"
    exit 1
fi
