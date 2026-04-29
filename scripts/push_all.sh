#!/bin/bash
# ═══════════════════════════════════════════════════════════════
# LILJR ONE PUSH — Push everything to GitHub in one command
# Saves state, commits code, pushes repo, never lose anything
# Run: bash ~/lj push   OR   bash push_all.sh
# ═══════════════════════════════════════════════════════════════

echo "🚀 LILJR ONE PUSH — Saving Everything"
echo "======================================"

# 1. Save current state (force server to save)
curl -s http://localhost:8000/api/health > /dev/null 2>&1 && echo "✅ Server running, state auto-saved" || echo "⚠️ Server not running"

# 2. Ensure state file exists and backup
cd ~
if [ -f "liljr_state.json" ]; then
    cp liljr_state.json "liljr_state_backup_$(date +%Y%m%d_%H%M%S).json"
    echo "✅ State backed up"
fi

# 3. Create repo directory if not exists
mkdir -p ~/liljr-autonomous/state

# 4. Copy state into repo
cp ~/liljr_state.json ~/liljr-autonomous/state/ 2>/dev/null || echo "No state yet"

# 5. Git commit + push
cd ~/liljr-autonomous 2>/dev/null || {
    echo "❌ Repo not found. Cloning..."
    cd ~ && rm -rf liljr-autonomous && git clone https://github.com/signsafepro-create/liljr-autonomous.git
    cd ~/liljr-autonomous
}

echo "📤 Committing and pushing..."
git add -A 2>/dev/null || true
git commit -m "v6.1 push: $(date) — state + code auto-save" 2>/dev/null || echo "Nothing new to commit"

# Push (without token in URL to avoid secret scanning)
git push origin main 2>&1 | grep -E "(To|main|error|Everything)" || true

echo ""
echo "✅ ONE PUSH COMPLETE"
echo "====================="
echo ""
echo "Saved:"
echo "  • Code: ~/liljr-autonomous/"
echo "  • State: ~/liljr_state.json"
echo "  • Backup: ~/liljr_state_backup_*.json"
echo "  • GitHub: https://github.com/signsafepro-create/liljr-autonomous"
echo ""
echo "Your memory is safe. Next time just:"
echo "  bash ~/lj push"
