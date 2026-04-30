#!/bin/bash
# go2.sh — Start the TRUE conversational soul
# Just talk. No commands. No wake word repetition.

cd ~/liljr-autonomous
git pull origin main 2>/dev/null
cp liljr_conversational.py ~/liljr_conversational.py

echo "⚡ Starting LilJR Conversational Soul..."
echo "Just talk. Interrupt me. Curse at me. I get it."
echo "Say 'yo junior' or just start talking."
echo "Say 'that's enough' to chill."
echo ""

python3 ~/liljr_conversational.py
