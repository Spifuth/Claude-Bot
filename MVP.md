# Fenrir (Claude-Bot) MVP

## What is Fenrir?
A modular Discord bot for basic homelab management and monitoring. This MVP covers only the essential features to get the bot running and demonstrate its value.

---

## Core Features (MVP)
- **/ping**: Check if the bot is alive
- **/status**: Show bot status and enabled modules
- **Modular Design**: Easily enable/disable features via config

---

## Quick Start (MVP)

### 1. Prerequisites
- Python 3.8+
- Discord Bot Token

### 2. Setup
```bash
cd /path/to/Claude-Bot
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 3. Configuration
Create a `.env` file in the project root:
```
DISCORD_BOT_TOKEN=your_discord_bot_token_here
```

### 4. Run the Bot
```bash
python bot.py
```

---

## Extending the MVP
- To enable homelab features, set `ENABLE_HOMELAB=true` in `.env` and configure the API server.
- Add new commands by creating cogs in the `cogs/` directory.

---

## Minimal Directory Structure
```
Claude-Bot/
├── bot.py
├── config.py
├── requirements.txt
├── cogs/
│   ├── core.py
│   └── admin.py
├── .env
```

---

## Notes
- For advanced features (Docker, homelab integration, API server), see the full README.
- Keep your Discord bot token secure! 