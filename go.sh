#!/bin/bash
# go.sh — One script. No setup. Just run and talk.

cd ~

# Make sure files exist
if [ ! -f ~/liljr_conversation.py ]; then
    cp ~/liljr-autonomous/liljr_conversation.py ~/liljr_conversation.py 2>/dev/null || echo "Need to pull first"
fi

echo "🎙️ LILJR IS LISTENING"
echo "====================="
echo "Just speak. No typing."
echo ""
echo "Say: yo junior"
echo ""

python3 ~/liljr_conversation.py
