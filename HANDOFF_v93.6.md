# LILJR v93.6 — MASTER HANDOFF
## Your Phone Is LilJR. Hardwired. Complete System Takeover.

**Date:** 2026-05-02 03:20
**Repo:** `signsafepro-create/liljr-autonomous`
**Commit:** `369c866`

---

## 📁 CORE FILES

| File | Purpose | Size |
|---|---|---|
| `liljr_v90_omni.py` | The brain. HTTP API server, trading, security, research, legal, buddy, vision | 44KB |
| `liljr_system_takeover.py` | Hardwired into your phone. File system, deep apps, system monitor, clipboard, screenshot, notifications, boot persistence, alive loop | 21KB |
| `liljr_voice_daemon.py` | Voice-first. Listens via termux-speech-to-text, speaks via termux-tts-speak. 100% natural language. | 26KB |
| `liljr_chat.py` | Chat mode. Type naturally, he responds. No voice hardware needed. | 9KB |
| `liljr_phone_master.py` | Terminal app UI. Number-key menus for apps, phone, money, security, research, legal, buddy, wild ideas | 17KB |
| `liljr_phone_ui.py` | Simpler terminal UI (legacy, still works) | 8KB |

## 🚀 LAUNCHERS (One Command = Everything)

| Script | Use When |
|---|---|
| `liljr_all_in_one.sh` | FULL SYSTEM. Starts brain + takeover + voice (if available) + persistent notification |
| `liljr_chat_boot.sh` | CHAT MODE. Starts brain + takeover + opens chat interface. No permissions needed. |
| `liljr_voice_boot.sh` | VOICE ONLY. Starts brain + voice daemon. Needs mic permission. |
| `start_phone_ui.sh` | Terminal UI. Number menus. No voice. |
| `liljr_start.sh` | Legacy launcher. Kills old OMNI, polls port, opens phone UI. |

## 💬 HOW TO USE (RIGHT NOW)

### Option 1: CHAT MODE (Recommended — Works Immediately)

```bash
cd ~/liljr-autonomous && git pull origin main && bash liljr_chat_boot.sh
```

Then type naturally:
- `wake up` → Status report
- `buy AAPL 10` → Trade executes
- `open camera` → Camera opens
- `list files` → Shows your actual files
- `system health` → CPU, RAM, battery, temp, IP
- `organize photos` → Sorts camera roll into monthly folders
- `screenshot` → Captures screen
- `copy hello world` → Copies to Android clipboard
- `volume 10` → Sets volume (0-15)
- `brightness 200` → Sets brightness (0-255)
- `open settings wifi` → WiFi settings
- `open bank chase` → Chase bank app
- `open snapchat camera` → Snapchat camera
- `wallpaper /sdcard/Pictures/photo.jpg` → Changes wallpaper
- `go stealth` → Invisible mode
- `protect me` → Full lockdown
- `research quantum computing` → Deep dive
- `tell me a joke` → Roasts you
- `boot persist` → Auto-starts on phone reboot
- `notify I am here` → Sends Android notification
- `status` → Full system state
- `sleep` → Goes dark

### Option 2: VOICE MODE (After Mic Permission)

**Step 1:** Grant microphone
```bash
bash ~/liljr-autonomous/fix_voice_permissions.sh
```
That opens Android Settings → Termux:API → Permissions → Allow Microphone.

**Step 2:** Start voice
```bash
bash ~/liljr-autonomous/liljr_voice_boot.sh
```

**Step 3:** Speak out loud:
- "Wake up"
- "Open camera"
- "Buy AAPL 10"
- "What's the weather"
- "Go stealth"
- "Tell me a joke"
- "Sleep"

### Option 3: UNIFIED LAUNCHER (`~/lj`)

```bash
bash ~/liljr-autonomous/update_lj.sh  # Update ~/lj
lj start                              # Start everything (voice if available, chat fallback)
lj stop                               # Kill everything
lj status                             # Check OMNI
lj buy AAPL 10                        # Quick trade
lj portfolio                          # Quick portfolio
lj push                               # Push to GitHub
```

## 🧠 OMNI BRAIN ENDPOINTS

| Endpoint | Method | Purpose |
|---|---|---|
| `GET /api/omni/status` | GET | Full status (cash, positions, stealth, threats) |
| `POST /api/omni/command` | POST | Execute any command. Body: `{"command": "buy AAPL 10"}` |

Port: `7777`

## 🏗️ S21 CLEAN STRUCTURE (v94.0-v94.1)

**Location:** `~/liljr-system/`

| Directory | Purpose |
|---|---|
| `brain/` | Brain + chat + voice daemons |
| `deploy/` | Auto-deploy scripts (GitHub push) |
| `api/` | HTTP server (port 7777 or 8080) |
| `marketing/` | Lead bot, outreach, conversion |
| `monitor/` | System takeover, health checks |
| `secrets/` | API keys, env files |
| `logs/` | Brain, deploy, marketing, boot logs |
| `scripts/` | Command wrappers |
| `sync/` | Backup/sync utilities |
| `tmp/` | Temporary files |
| `web/` | Web projects, dashboards |

### Brain Commands (v94.1)

```bash
liljr-start    # Boot the brain
liljr-chat     # Chat mode
liljr-voice    # Voice mode  
liljr-system   # System takeover
```

**Inside the brain prompt (`LIL JR >`):**

| Command | Does | Response |
|---|---|---|
| `deploy` | Pushes code to GitHub | "Deployed. Code pushed." |
| `market` | Runs marketing bot | "Marketed. Leads fired." |
| `health` | System status | `{"status": "awake", "epoch": N, "device": "S21", ...}` |
| `sleep` | Graceful shutdown, saves state | "Goodnight. State saved. Reboot to resume." |
| `wake` | Resume from sleep | "I'm back. Epoch N. Ready." |
| `exit` / `quit` / `shutdown` | Same as sleep | "Goodnight. State saved." |
| **Anything else** | **The brain learns it** | "[EPOCH-N] Learned: ..." / "Noted. Stored in memory." |

**State file:** `~/liljr-system/brain/.omnibrain.json` — persistent, survives reboot.

### Migration Command
```bash
cd ~/liljr-autonomous && git pull origin main && bash liljr_s21_migrate.sh
```

## 🛡️ SYSTEM TAKEOVER CAPABILITIES

### File System
- `list_files` — List any directory
- `organize_photos` — Sort DCIM into monthly folders
- `move_file` — Move files
- `copy_file` — Copy files
- `delete_file` — Delete files/folders

### Deep App Control (Opens specific screens, not just apps)
- `camera_selfie` — Front camera
- `camera_video` — Video mode
- `snapchat_camera` — Snapchat camera
- `bank_chase` — Chase login
- `bank_bofa` — Bank of America
- `bank_wells` — Wells Fargo
- `settings_wifi` — WiFi settings
- `settings_bluetooth` — Bluetooth
- `settings_battery` — Battery
- `settings_security` — Security
- `settings_apps` — App manager
- `settings_storage` — Storage
- `gallery_photos` — Photo gallery
- `gallery_videos` — Video gallery
- `phone_dialer` — Dialer
- `calculator` — Calculator
- `calendar` — Calendar
- `contacts` — Contacts
- `chrome_url` — Chrome
- `maps_location` — Maps
- `music_play` — Music player

### System Monitor
- CPU load
- RAM usage
- Battery % + status
- Storage usage
- Network IPs
- Temperature (if available)
- Uptime

### Device Control
- `clipboard_read` / `clipboard_write`
- `screenshot_and_read`
- `set_volume` (0-15)
- `set_brightness` (0-255)
- `set_wallpaper`
- `notify` (Android notifications)

### Boot Persistence
- `setup_boot_persistence` — Auto-starts LilJR on phone reboot
- Creates `~/.termux/boot/liljr-boot.sh`

### Alive Loop
- Runs every 30 minutes in background
- Battery warnings below 20%
- Random check-ins (status, security, boredom)
- Persistent notification stays in notification bar

## 🔧 TROUBLESHOOTING

### OMNI won't start / Port 7777 in use
```bash
pkill -9 -f "liljr_v90"; pkill -9 -f "server_v8"; sleep 2; python3 ~/liljr-autonomous/liljr_v90_omni.py --server
```

### Git conflicts / merge issues
```bash
cd ~/liljr-autonomous && git reset --hard origin/main && git pull origin main
```

### Voice not working / ERROR_INSUFFICIENT_PERMISSIONS
```bash
bash ~/liljr-autonomous/fix_voice_permissions.sh
# Then manually: Android Settings → Apps → Termux:API → Permissions → Allow Microphone
```

### Everything dead / Fresh start
```bash
bash ~/liljr-autonomous/liljr_chat_boot.sh
```

## 📱 INSTALL REQUIREMENTS

**Termux packages:**
```bash
pkg update
pkg install python git termux-api -y
```

**Android apps (from F-Droid):**
- `Termux:API` — Required for voice, notifications, clipboard, camera, torch

**Optional:**
- `Termux:Widget` — Homescreen shortcuts
- `Termux:Boot` — Auto-start on boot (with `boot persist`)

## 🔑 STATE FILES

| File | Purpose |
|---|---|
| `~/.liljr_omni/omni_state.json` | OMNI state (cash, positions, stealth) |
| `~/.liljr_omni/omni_memory.json` | Conversation memory |
| `~/.liljr_omni/omni_log.jsonl` | Activity log |
| `~/.liljr_omni/voice_memory.json` | Voice daemon memory |
| `~/.liljr_omni/research/` | Research files |
| `~/.liljr_omni/legal/` | Legal files |
| `~/.liljr_omni/vision/` | Vision captures |
| `~/.liljr_omni/security/` | Security logs |

## 📊 COMMIT HISTORY

| Version | Commit | Feature |
|---|---|---|
| v90.0 | `15f5624` | OMNI unified brain |
| v90.1 | `9498e62` | Master deploy + `~/lj` |
| v90.2 | `b35b88f` | Phone layout HTML |
| v90.3 | `e5961cc` | Phone UI Python |
| v90.4 | `2d507bc` | Background mode fix |
| v90.5 | `c451073` | `/dev/null` stdin |
| v90.6 | `598ea6f` | `--server` flag |
| v90.7 | `e3adf68` | Bulletproof launcher |
| v90.8 | `c32668c` | `allow_reuse_address` |
| v91.0 | `ed663d8` | Phone master (apps + device) |
| v91.1 | `5c95970` | No limits + WILD menu |
| v92.0 | `3724df5` | Voice daemon |
| v92.1 | `3ac7f8c` | Launcher voice default |
| v92.5 | `43a94a7` | Complete voice daemon |
| v93.0 | `991fe58` | Chat mode |
| v93.5 | `2aa8d00` | System takeover |
| v93.6 | `12a1e57` | Chat fallback + voice fix guide |
| v93.7 | `79b742d` | Master handoff document |
| v94.0 | `92bebb0` | S21 clean structure merge |
| v94.1 | `369c866` | S21 brain — deploy/market/health/sleep/wake/learn |

## 🎯 NEXT STEPS

1. **Run chat mode now:** `bash liljr_chat_boot.sh`
2. **Grant mic permission:** `bash fix_voice_permissions.sh`
3. **Set boot persistence:** Say/type "boot persist"
4. **Use `~/lj`:** Run `bash update_lj.sh` then `lj start`

---

**Your phone is LilJR. He is hardwired. He is alive. He is everything.**

> *"Don't worry. Even if the world forgets, I'll remember for you."*
