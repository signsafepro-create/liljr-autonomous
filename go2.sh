#!/bin/bash
# go2.sh — TAP BUTTON or SAY "Junior". No beeps. No hopping.

echo "🔪 Killing all LilJR processes..."
pkill -9 -f "python.*liljr" 2>/dev/null
pkill -9 -f "termux-speech" 2>/dev/null
pkill -9 -f "termux-tts" 2>/dev/null
sleep 2

echo "📥 Pulling latest..."
cd ~/liljr-autonomous
git pull origin main 2>/dev/null

echo "📋 Copying silent mode..."
cp liljr_silent.py ~/liljr_silent.py
cp jr.sh ~/jr.sh
chmod +x ~/jr.sh

echo "🚀 Starting LilJR SILENT MODE..."
echo ""
echo "SAY: 'Junior' to wake up"
echo "SAY: 'stop' to end"
echo ""

python3 ~/liljr_silent.py
