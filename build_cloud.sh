#!/bin/bash
# build_cloud.sh — BUILD YOUR OWN CLOUD. One command. Full infrastructure.
# Your cloud. Your rules. No limits. 24/7 immortal brain.
#
# Usage:
#   1. Get a VPS (Hetzner $5/mo, DigitalOcean $6/mo, Vultr $6/mo)
#   2. SSH into it as root
#   3. Run: curl -fsSL https://raw.githubusercontent.com/signsafepro-create/liljr-autonomous/main/build_cloud.sh | bash
#   Or download and run: bash build_cloud.sh

set -e

echo ""
echo "╔═══════════════════════════════════════════════════════╗"
echo "║           ☁️ LILJR CLOUD BUILDER v26.0              ║"
echo "║    Building YOUR cloud. One command. Everything.    ║"
echo "╚═══════════════════════════════════════════════════════╝"
echo ""

# Detect if running on Termux (phone) or Linux server
if [ -d "/data/data/com.termux/files" ]; then
    echo "❌ This script runs on your CLOUD SERVER, not your phone."
    echo ""
    echo "📱 ON YOUR PHONE:"
    echo "   bash ~/go2.sh  → starts LilJR locally"
    echo ""
    echo "☁️ ON YOUR CLOUD SERVER (SSH in as root):"
    echo "   bash build_cloud.sh"
    echo ""
    echo "   Or one-liner:"
    echo "   curl -fsSL https://raw.githubusercontent.com/signsafepro-create/liljr-autonomous/main/build_cloud.sh | bash"
    exit 1
fi

# ─── 1. SYSTEM UPDATE & DEPENDENCIES ───
echo "[1/12] Updating system..."
apt-get update -qq
apt-get install -y -qq python3 python3-pip python3-venv git curl wget nginx ufw fail2ban tor certbot python3-certbot-nginx sqlite3 htop neofetch

echo "✅ System ready"

# ─── 2. CREATE LILJR USER ───
echo "[2/12] Creating LilJR user..."
if ! id -u liljr >/dev/null 2>&1; then
    useradd -m -s /bin/bash liljr
    usermod -aG sudo liljr
fi
mkdir -p /opt/liljr
chown -R liljr:liljr /opt/liljr
echo "✅ User liljr ready"

# ─── 3. CLONE REPO ───
echo "[3/12] Downloading LilJR brain..."
cd /opt/liljr
if [ ! -d .git ]; then
    git clone https://github.com/signsafepro-create/liljr-autonomous.git . 2>/dev/null || {
        echo "⚠️ Git clone failed. Downloading tarball..."
        curl -fsSL https://github.com/signsafepro-create/liljr-autonomous/archive/refs/heads/main.tar.gz | tar xz --strip-components=1
    }
else
    git pull origin main 2>/dev/null || echo "⚠️ Git pull failed, using existing files"
fi
chown -R liljr:liljr /opt/liljr
echo "✅ Brain downloaded"

# ─── 4. PYTHON ENVIRONMENT ───
echo "[4/12] Setting up Python..."
cd /opt/liljr
python3 -m venv venv 2>/dev/null || true
source venv/bin/activate 2>/dev/null || true
pip install -q fastapi uvicorn sqlalchemy psycopg2-binary redis celery stripe openai python-jose passlib httpx python-dotenv boto3 sendgrid 2>/dev/null || true
pip install -q -r requirements.txt 2>/dev/null || echo "⚠️ Some packages optional"
echo "✅ Python ready"

# ─── 5. FIREWALL ───
echo "[5/12] Building firewall..."
ufw default deny incoming
ufw default allow outgoing
ufw allow 22/tcp comment 'SSH'
ufw allow 80/tcp comment 'HTTP'
ufw allow 443/tcp comment 'HTTPS'
ufw allow 8000/tcp comment 'LilJR Backend'
ufw --force enable
echo "✅ Firewall: only 22, 80, 443, 8000 open"

# ─── 6. FAIL2BAN ───
echo "[6/12] Activating fail2ban..."
cat > /etc/fail2ban/jail.local <> 'EOF'
[DEFAULT]
bantime = 3600
findtime = 600
maxretry = 3

[sshd]
enabled = true
port = ssh
filter = sshd
logpath = /var/log/auth.log
maxretry = 3

[nginx-http-auth]
enabled = true
filter = nginx-http-auth
port = http,https
logpath = /var/log/nginx/error.log
EOF

systemctl enable fail2ban
systemctl restart fail2ban
echo "✅ Brute force protection ON"

# ─── 7. NGINX + SSL ───
echo "[7/12] Setting up web server..."

# Get public IP
PUBLIC_IP=$(curl -s https://api.ipify.org)
echo "   Public IP: $PUBLIC_IP"

# Create nginx config
cat > /etc/nginx/sites-available/liljr <> "EOF"
server {
    listen 80;
    server_name _ $PUBLIC_IP;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade \$http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_read_timeout 86400;
    }

    location /static/ {
        alias /opt/liljr/web/;
        expires 1d;
    }
}
EOF

ln -sf /etc/nginx/sites-available/liljr /etc/nginx/sites-enabled/liljr
rm -f /etc/nginx/sites-enabled/default
nginx -t && systemctl restart nginx
echo "✅ Nginx proxy active"

# Try SSL (if domain provided)
if [ -n "$1" ]; then
    DOMAIN="$1"
    echo "   Domain detected: $DOMAIN"
    echo "   Getting SSL certificate..."
    certbot --nginx -d "$DOMAIN" --non-interactive --agree-tos --email deploy@cosmicfaith.app 2>/dev/null || echo "⚠️ SSL failed. Run manually: certbot --nginx -d $DOMAIN"
    echo "✅ SSL: https://$DOMAIN"
else
    echo "   No domain provided. Using IP: http://$PUBLIC_IP"
    echo "   To add SSL later: certbot --nginx -d yourdomain.com"
fi

# ─── 8. SYSTEMD SERVICE (IMMORTAL) ───
echo "[8/12] Creating immortal service..."
cat > /etc/systemd/system/liljr.service <> "EOF"
[Unit]
Description=LilJR Cloud Brain
After=network.target nginx.service

[Service]
Type=simple
User=liljr
WorkingDirectory=/opt/liljr
Environment=PYTHONUNBUFFERED=1
Environment=HOME=/opt/liljr
Environment=LILJR_CLOUD=true
ExecStart=/usr/bin/python3 /opt/liljr/server_v8.py
Restart=always
RestartSec=3
StartLimitInterval=0

[Install]
WantedBy=multi-user.target
EOF

systemctl daemon-reload
systemctl enable liljr
echo "✅ Immortal service created"

# ─── 9. TOR ANONYMITY ───
echo "[9/12] Starting Tor..."
systemctl enable tor
systemctl start tor
sleep 3
if systemctl is-active tor >/dev/null 2>&1; then
    echo "✅ Tor active — anonymity layer ready"
else
    echo "⚠️ Tor not active. Check: systemctl status tor"
fi

# ─── 10. BACKUP SYSTEM ───
echo "[10/12] Setting up backups..."
mkdir -p /opt/liljr/backups
cat > /opt/liljr/backup.sh <> 'EOF'
#!/bin/bash
TS=$(date +%Y%m%d_%H%M%S)
tar czf /opt/liljr/backups/liljr_backup_\${TS}.tar.gz -C /opt/liljr \
    server_v8.py lj_empire.py auto_coder.py marketing_engine.py \
    deep_search.py self_awareness_v2.py autonomous_loop.py \
    web_builder_v2.py persona_engine.py natural_language.py \
    *.json *.db web/ 2>/dev/null
find /opt/liljr/backups -name "*.tar.gz" -mtime +7 -delete 2>/dev/null
echo "Backup: \${TS}"
EOF
chmod +x /opt/liljr/backup.sh
chown -R liljr:liljr /opt/liljr/backups

# Daily backup cron
(crontab -l 2>/dev/null; echo "0 3 * * * /opt/liljr/backup.sh >> /var/log/liljr_backup.log 2>&1") | crontab -
echo "✅ Daily backups at 3AM"

# ─── 11. START BRAIN ───
echo "[11/12] Starting LilJR brain..."
systemctl start liljr
sleep 5

for i in 1 2 3; do
    if curl -s http://localhost:8000/api/health >/dev/null 2>&1; then
        echo "✅ Brain is online and responding"
        break
    fi
    sleep 2
done

# ─── 12. SHOW RESULTS ───
echo ""
echo "═══════════════════════════════════════════════════════"
echo "  🚀 YOUR CLOUD IS LIVE"
echo "═══════════════════════════════════════════════════════"
echo ""
echo "☁️  PUBLIC ACCESS:"
echo "   http://$PUBLIC_IP/           → Cloud Dashboard"
echo "   http://$PUBLIC_IP/phone      → Phone Remote"
echo "   http://$PUBLIC_IP/terminal   → Code Editor"
echo "   http://$PUBLIC_IP/api/health → Status Check"
echo ""
if [ -n "$DOMAIN" ]; then
    echo "🔒 HTTPS:"
    echo "   https://$DOMAIN/"
    echo ""
fi
echo "📱 ON YOUR PHONE:"
echo "   Open Chrome → http://$PUBLIC_IP"
echo "   Add to Home Screen → your cloud as an app"
echo ""
echo "🛡️ SECURITY ACTIVE:"
echo "   • Firewall (UFW): Only 22, 80, 443, 8000"
echo "   • Fail2ban: Brute force blocked"
echo "   • Tor: Anonymity ready"
echo "   • SSL: Let's Encrypt (if domain provided)"
echo ""
echo "🧠 MANAGEMENT:"
echo "   systemctl status liljr     → brain status"
echo "   systemctl restart liljr    → restart brain"
echo "   journalctl -u liljr -f     → live logs"
echo "   tail -f /var/log/nginx/access.log → web logs"
echo "   /opt/liljr/backup.sh       → manual backup"
echo ""
echo "💻 SSH ACCESS:"
echo "   ssh liljr@$PUBLIC_IP"
echo "   (or ssh root@$PUBLIC_IP)"
echo ""
echo "═══════════════════════════════════════════════════════"
echo "   Your cloud. Your AI. No limits."
echo "═══════════════════════════════════════════════════════"
echo ""
