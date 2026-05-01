#!/bin/bash
# one_shot_setup.sh — One command. Fixes everything. Installs. Deploys. Runs.

pkg update -y 2>/dev/null
pkg install python git -y 2>/dev/null

cd "$HOME"
[ -d "liljr-autonomous" ] || git clone https://github.com/signsafepro-create/liljr-autonomous.git

cd liljr-autonomous
git pull origin main 2>/dev/null

cp deploy_phone.sh "$HOME/deploy_phone.sh"
bash "$HOME/deploy_phone.sh"
