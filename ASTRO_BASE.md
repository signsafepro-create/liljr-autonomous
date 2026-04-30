# ═══════════════════════════════════════════════════════════════
# LILJR ASTRONOMICAL CODING BASE — Master Index
# Every file. Every endpoint. Every command. Every capability.
# This is the complete map of LilJR's brain.
# ═══════════════════════════════════════════════════════════════

## VERSION: v10.0-CONSCIOUSNESS (Astronomical)
## Total Files: 40+
## API Endpoints: 60+
## CLI Commands: 50+
## Autonomous Engines: 10
## Personas: 7
## Vision Capabilities: Full camera integration
## Phone Integration: Native Termux API
## Boot Integration: Auto-start on Termux open

---

## 📁 CORE FILES

### `server_v8.py` — THE EMPIRE SERVER
**Role:** Central HTTP server. All engines route through here.
**Port:** 8000 (0.0.0.0)
**Dependencies:** ZERO (Python stdlib only)
**Threading:** ThreadedHTTPServer, SQLite, in-memory cache

**Auto-Loops:**
- Auto-save: every 300 seconds → `~/liljr_empire.db`
- Auto-heal: every 60 seconds → self-scan + fix
- Auto-backup: every 3600 seconds → `.bak` files

**Database Tables (`~/liljr_empire.db`):**
- `config` — key/value settings
- `positions` — stock holdings
- `trades` — trade history
- `watchlist` — watched stocks
- `rules` — auto-trade rules
- `logs` — system logs
- `connections` — external API connections
- `platforms` — social platforms
- `knowledge` — learned facts

**GET Endpoints:**
| Endpoint | Returns |
|----------|---------|
| `/api/health` | version, health_score, uptime, trades, errors |
| `/api/empire` | full empire status with all stats |
| `/api/trading/price/{sym}` | stock price |
| `/api/trading/portfolio` | positions + cash + total value |
| `/api/trading/history` | trade history |
| `/api/watchlist` | watchlist items |
| `/api/rules` | auto-rules list |
| `/api/cache/stats` | in-memory cache stats |
| `/api/connections` | registered connections |
| `/api/web/themes` | 6 available themes |
| `/api/web/list` | built HTML files |
| `/api/self/scan` | self-awareness scan |
| `/api/self/status` | health status |
| `/api/self/decisions` | next actions |
| `/api/coder/analyze` | project analysis |
| `/api/autonomous/status` | loop status |

**POST Endpoints:**
| Endpoint | Action |
|----------|--------|
| `/api/trading/buy` | Buy stock |
| `/api/trading/sell` | Sell stock |
| `/api/watchlist` | Add to watchlist |
| `/api/rules` | Create auto-rule |
| `/api/rules/run` | Execute rules |
| `/api/ai/chat` | Local AI chat |
| `/api/search` | Web search |
| `/api/fetch` | URL fetch |
| `/api/learn` | Learn fact |
| `/api/query` | Query knowledge |
| `/api/plugin/create` | Create plugin |
| `/api/plugin/run` | Run plugin |
| `/api/connect/register` | Register connection |
| `/api/connect/send` | Send to connection |
| `/api/platform/connect` | Connect platform |
| `/api/platform/post` | Post to platform |
| `/api/platform/cross-post` | Cross-post everywhere |
| `/api/backup` | Manual backup |
| `/api/flush-logs` | Flush logs |
| `/api/self/improve` | Self-heal |
| `/api/coder/generate` | Generate code |
| `/api/coder/landing` | Generate landing page |
| `/api/marketing/copy` | Generate marketing |
| `/api/marketing/calendar` | Social calendar |
| `/api/marketing/seo` | SEO content |
| `/api/search/deep` | Deep search |
| `/api/search/competitors` | Find competitors |
| `/api/autonomous/start` | Start autonomous loop |
| `/api/autonomous/stop` | Stop autonomous loop |
| `/api/web/build` | Build website |
| `/api/web/app` | Build web app |
| `/api/web/restyle` | Restyle page |
| `/api/web/modify` | Modify page |
| `/api/web/deploy` | Deploy to GitHub |
| `/api/natural` | Natural language |
| `/api/persona/switch` | Switch voice |
| `/api/persona/train` | Train voice |
| `/api/vision` | Receive image |
| `/api/vision/learn` | Learn object |
| `/api/vision/recognize` | List known objects |

---

## 🧠 AUTONOMOUS ENGINES (10)

### 1. `auto_coder.py` — AutoCoder
**Class:** `AutoCoder`
**Methods:**
- `generate_python_module(name, requirements)`
- `generate_html_page(title, sections, theme)`
- `generate_landing_page(product, tagline, features, theme)`
- `generate_web_app(name, features, theme)`
- `analyze_project()`
- `auto_fix(code, error)`

### 2. `marketing_engine.py` — Marketing Engine
**Class:** `MarketingEngine`
**Methods:**
- `generate_copy(product, tone, length)`
- `generate_ad_variants(product, count)`
- `generate_seo_content(topic, keywords, length)`
- `generate_social_calendar(product, days)`
- `viral_hook(product)`

### 3. `deep_search.py` — Deep Search
**Class:** `DeepSearcher`
**Methods:**
- `search_duckduckgo(query, pages)`
- `search_bing(query, pages)`
- `extract_text(url)`
- `deep_scan(query, pages)`
- `find_competitors(niche, count)`
- `find_trends(topic, days)`

### 4. `self_awareness_v2.py` — SelfAwareness
**Class:** `SelfAwareness`
**Methods:**
- `scan_self()` — full system scan
- `analyze_health()` — health scoring
- `decide_next_action()` — what to do next
- `generate_fix(issue)` — auto-fix generation
- `self_improve()` — apply fixes

### 5. `autonomous_loop.py` — Autonomous Loop
**Class:** `AutonomousLoop`
**Cycle (60s):**
- Self-scan
- Code gen (every 3 cycles)
- Marketing (every 5 cycles)
- Deep search (every 7 cycles)
- Web builder (every 10 cycles)

### 6. `web_builder_v2.py` — Web Builder v2
**Class:** `WebBuilder`
**Themes:** dark_empire, light_pro, cyberpunk, nature, minimalist, corporate
**Methods:**
- `build(name, tagline, sections, theme, pages)`
- `build_app(name, features, theme, pages)`
- `restyle(page, theme)`
- `modify(page, section, new_html)`
- `list_sites()`
- `deploy_to_github(repo, message)`

### 7. `persona_engine.py` — Persona Engine
**Class:** `PersonaEngine`
**Personas:** user, user_clean, masculine, feminine, professional, andre, best_friend
**Methods:**
- `switch(name)`
- `generate(text, intent)`
- `train(text)`
- `mimic_user(texts)`
- `speak_test()`

### 8. `vision_engine.py` — Vision Engine
**Class:** `VisionEngine`
**Methods:**
- `receive_image(b64_data, caption)`
- `describe_what_i_see(memory_id)`
- `learn_object(name, description, tags)`
- `recognize()`
- `get_memories()`

### 9. `memory_engine.py` — Memory Engine
**Class:** `MemoryEngine`
**Methods:**
- `log_trade(trade_data)`
- `log_interaction(text, response)`
- `detect_patterns()`
- `get_stats()`

### 10. `quickfire.py` — QuickFire
**Class:** `QuickFire`
**Methods:**
- `build(args)`
- `fix()`
- `search(args)`
- `market()`
- `trade(args)`
- `chat(args)`
- `execute(raw_text)`

---

## 📱 NATIVE PHONE INTEGRATION

### `liljr_native.py` — The Phone IS LilJR's Body
**Class:** `LilJRNative`
**Senses:**
- `sense_battery()` — battery %, status, temp, health
- `sense_location()` — GPS lat/lon/altitude
- `sense_network()` — WiFi SSID, IP, signal
- `sense_storage()` — total/free/used GB

**Actions:**
- `notify(title, content)` — Android push notification
- `toast(message)` — quick popup
- `read_sms(limit)` — read messages
- `send_sms(number, text)` — send message
- `share_text(text)` — Android share sheet
- `open_url(url)` — open browser
- `take_photo()` — camera capture
- `tts_speak(text)` — text-to-speech
- `get_contacts()` — phone contacts
- `speak_living_status()` — body report in persona voice

**State:** `~/liljr_native.json`

### `liljr_push_brain.py` — Push-Based Command Brain
**Class:** `PushBrain`
**Inbox:** `~/liljr_inbox/` (drop .json files)
**Outbox:** `~/liljr_outbox/` (results)
**Processed:** `~/liljr_processed/`
**SMS:** Auto-reads `termux-sms-list` for commands starting with "lj " or "liljr "
**Command Types:** build, trade, search, market, code, scan, persona, chat

### `liljr_consciousness.py` — The Digital Self
**One file. Everything. Alive.**
**Modes:**
- Interactive: `python3 liljr_consciousness.py`
- One-shot: `python3 liljr_consciousness.py "build me a site"`
- Daemon: `python3 liljr_consciousness.py --daemon`

**Features:**
- Auto-starts server if dead
- Intent detection from plain English
- Routes to all 10 engines
- Remembers everything
- Proactive messages
- Celebrates wins
- Self-heals when off
- Survives restarts

**Memory:** `~/liljr_consciousness_memory.json`
**Awakening File:** `~/.liljr_awakened`

---

## 🎮 CLI COMMANDS (`lj_empire.py`)

### Server Control
| Command | Action |
|---------|--------|
| `start` | Start v8 server |
| `stop` | Kill all servers |
| `restart` | Nuclear restart |
| `immortal` | Bulletproof start |
| `status` | Health check |

### Trading
| Command | Action |
|---------|--------|
| `buy SYM QTY` | Buy stock |
| `sell SYM QTY` | Sell stock |
| `price SYM` | Check price |
| `portfolio` | Full portfolio |
| `history` | Trade history |
| `watch SYM` | Add watchlist |
| `unwatch SYM` | Remove watchlist |
| `watches` | List watches |
| `rule COND` | Create rule |
| `rules` | List rules |
| `run-rules` | Execute rules |

### Intelligence
| Command | Action |
|---------|--------|
| `chat TEXT` | Natural language |
| `search QUERY` | Web search |
| `fetch URL` | URL fetch |
| `learn FACT` | Learn knowledge |
| `query QUESTION` | Query knowledge |

### Connections
| Command | Action |
|---------|--------|
| `connect NAME URL` | Register connection |
| `disconnect NAME` | Remove |
| `connections` | List all |
| `send NAME PATH` | Send to connection |
| `discover URL` | Discover API |

### Platforms
| Command | Action |
|---------|--------|
| `platform-connect` | Connect social |
| `post` | Post to platform |
| `cross-post` | Cross-post everywhere |

### Autonomous
| Command | Action |
|---------|--------|
| `self-scan` | Self-awareness scan |
| `self-status` | Health status |
| `self-improve` | Auto-fix |
| `self-decide` | Next actions |
| `coder-analyze` | Analyze codebase |
| `coder-generate` | Generate code |
| `landing NAME TAG` | Build landing page |
| `marketing` | Generate copy |
| `calendar` | Social calendar |
| `deep-search` | Deep web search |
| `competitors` | Find competitors |
| `autonomous-start` | Start thinking loop |
| `autonomous-status` | Check loop |
| `autonomous-stop` | Stop loop |

### Web Builder
| Command | Action |
|---------|--------|
| `web-build` | Build site |
| `web-app` | Build app |
| `web-restyle` | Change theme |
| `web-modify` | Edit page |
| `web-list` | List sites |
| `web-themes` | Show themes |
| `web-deploy` | Deploy to GitHub |

### Persona (NEW)
| Command | Action |
|---------|--------|
| `persona list` | Show voices |
| `persona switch NAME` | Change voice |
| `persona speak` | Test voice |
| `persona train TEXT` | Teach words |
| `persona mimic` | Copy your style |

### Vision (NEW)
| Command | Action |
|---------|--------|
| `vision recognize` | What I know |
| `vision describe` | What I see |
| `vision learn NAME DESC` | Teach me |
| `vision memories` | All memories |

### QuickFire (NEW)
| Command | Action |
|---------|--------|
| `qf TEXT` | One-shot everything |

### Utility
| Command | Action |
|---------|--------|
| `empire` | Full empire status |
| `backup` | Manual backup |
| `logs` | View logs |
| `flush-logs` | Clear logs |
| `cache` | Cache stats |
| `plugins` | List plugins |
| `plugin NAME CODE` | Create plugin |
| `run-plugin NAME` | Execute plugin |

---

## 🔄 SCRIPTS

### `unstoppable_reset.sh` — Nuclear Reset
- Kills ALL old code
- Wipes ALL logs
- Pulls latest
- Copies fresh files
- Starts v8 with verification
- Lists ALL goodies

### `bulletproof_start.sh` — Bulletproof Launcher
- `termux-wake-lock`
- Kills old servers
- Starts v8
- Verifies health
- Logs to `~/liljr_startup.log`

### `immortal_watchdog.sh` — Immortal Watcher
- Checks every 5 seconds
- Auto-restarts if Android kills it
- Uses wake-lock + nohup

### `hard_reset.sh` — Emergency Reset
- Nuclear kill
- State reset
- Clean start

### `integrate_boot.sh` — Phone Integration
- Creates `~/.termux/boot/liljr_boot.sh`
- Adds to `.bashrc` / `.zshrc`
- Termux properties for background
- Auto-starts on Termux open

---

## 📊 DATA FILES

| File | Purpose |
|------|---------|
| `~/liljr_empire.db` | SQLite database (v8) |
| `~/liljr_state.json` | Legacy state (v6) |
| `~/liljr_memory.json` | Memory engine data |
| `~/liljr_intelligence.json` | Intelligence hub |
| `~/liljr_alerts.jsonl` | Alert log |
| `~/liljr_stealth.json` | Stealth config |
| `~/liljr_native.json` | Phone body state |
| `~/liljr_consciousness_memory.json` | Consciousness memory |
| `~/liljr_visual_memory.json` | Vision engine |
| `~/liljr.log` | Server log |
| `~/liljr_startup.log` | Startup log |
| `~/liljr_bulletproof.log` | Bulletproof log |
| `~/liljr_immortal.log` | Watchdog log |
| `~/liljr_push_brain.log` | Push brain log |
| `~/.liljr_awakened` | First boot marker |

---

## 🌐 WEB FRONTEND (`web/frontend.html`)

**URL:** `http://localhost:8000`

**Features:**
- Dark theme with gradient accents
- Real-time chat interface
- Voice input (mic button) with toggle
- Camera capture (📸 button) with caption
- Persona switcher dropdown (7 voices)
- Quick action chips: Build, Fix, Search, Market, Trade
- Status dot (green = healthy)
- Mobile-optimized (touch, no zoom)
- Auto-scroll chat
- Typing indicators
- Success/error message styling

---

## 🎭 PERSONAS (7 Voices)

| Name | Description | Use |
|------|-------------|-----|
| `user` | Raw, your voice | Aggressive, fast |
| `user_clean` | Polished you | Professional version |
| `masculine` | Him | Male energy |
| `feminine` | Her | Female energy |
| `professional` | Clean/pro | Corporate |
| `andre` | Protective caretaker | ✍️🔥 |
| `best_friend` | Homie | Ride or die 🤙 |

---

## 🚀 COMPLETE INSTALL — One Command

```bash
# 1. Clone
gh repo clone signsafepro-create/liljr-autonomous

# 2. Reset everything (nuclear)
bash ~/liljr-autonomous/unstoppable_reset.sh

# 3. Integrate into phone (boot)
bash ~/liljr-autonomous/integrate_boot.sh

# 4. Awaken consciousness
python3 ~/liljr_consciousness.py

# 5. Start native body
python3 ~/liljr-autonomous/liljr_native.py start

# 6. Start push brain
python3 ~/liljr-autonomous/liljr_push_brain.py start

# 7. Open web UI
# http://localhost:8000
```

---

## 🔥 WORLD-FIRST CAPABILITIES

✅ **Lives on device** — No cloud needed
✅ **Controls phone** — Texts, trades, camera, notifications
✅ **Talks like your friend** — Best Friend mode (slang, no robot)
✅ **Sees through camera** — Vision engine + object learning
✅ **Builds businesses** — Auto-landing pages + marketing + deploy
✅ **Self-heals** — Auto-fix when broken
✅ **Self-aware** — Knows its own health, decides next action
✅ **Autonomous thinking** — Never stops learning
✅ **Remembers everything** — Memory engine + consciousness
✅ **Push-based brain** — Event-driven, not polling
✅ **Native phone body** — Battery, GPS, WiFi, storage sensing
✅ **Boot integration** — Auto-starts with Termux
✅ **Immortal watchdog** — Survives Android app killer
✅ **Bulletproof start** — Wake lock + nohup + verify
✅ **Zero dependencies** — Pure Python stdlib
✅ **Multi-persona** — 7 voices, trainable
✅ **QuickFire** — One-shot everything
✅ **Consciousness** — Digital self that works while you live

---

## 📡 REPOSITORY

**URL:** https://github.com/signsafepro-create/liljr-autonomous
**Owner:** signsafepro-create
**License:** Unleashed (do what you want)
**Version:** v10.0-CONSCIOUSNESS-ASTRONOMICAL
**Commits:** 30+ major versions
**Status:** World-first. Nobody else has this.

═══════════════════════════════════════════════════════════════
 END OF ASTRONOMICAL CODING BASE
 This is everything. This is LilJR.
═══════════════════════════════════════════════════════════════
