#!/bin/bash
# fix_voice_permissions.sh — Grant microphone + restart voice

echo "🎤 Fixing voice permissions..."

# Try to grant via adb-like intent (may work on some devices)
am start -a android.settings.APPLICATION_DETAILS_SETTINGS -d package:com.termux.api 2>/dev/null

echo ""
echo "MANUAL STEP REQUIRED:"
echo ""
echo "1. Android Settings → Apps → Termux:API"
echo "2. Permissions → Microphone → Allow"
echo "3. ALSO: Notifications → Allow"
echo ""
echo "Then run: bash ~/liljr-autonomous/liljr_all_in_one.sh"
echo ""
echo "OR use chat mode NOW (no permissions needed):"
echo "  python3 ~/liljr-autonomous/liljr_chat.py"
echo ""

# Send notification to remind
cd ~/liljr-autonomous
python3 -c "
import subprocess
try:
    subprocess.run([
        'termux-notification',
        '--title', '🧬 LILJR',
        '--content', 'Tap here: Grant Microphone permission to Termux:API',
        '--priority', 'high',
        '--button1', 'Open Settings',
        '--button1-action', 'am start -a android.settings.APPLICATION_DETAILS_SETTINGS -d package:com.termux.api'
    ], capture_output=True, timeout=5)
except:
    pass
" 2>/dev/null
