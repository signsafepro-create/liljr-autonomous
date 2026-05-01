#!/bin/bash
# jr.sh — Home screen shortcut. Tap = Kill old → Start LilJR.
pkill -9 -f "python.*liljr" 2>/dev/null
pkill -9 -f "termux-speech" 2>/dev/null
sleep 1
cd ~/liljr-autonomous
git pull origin main 2>/dev/null
cp liljr_silent.py ~/liljr_silent.py 2>/dev/null
python3 ~/liljr_silent.py
