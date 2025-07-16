# 🐺 Fenrir - Advanced Discord Logging & Analytics Bot

A professional, feature-rich Discord bot for comprehensive server monitoring, logging, and analytics with modular architecture and advanced database management.

## ✨ **Key Features**

### 🎯 **Advanced Logging System (15+ Event Types)**
- **📝 Message Tracking** - Deletions, edits with content preservation
- **👥 Member Management** - Joins, leaves, bans, unbans with detailed analytics
- **📎 Enhanced Attachment Logging** - File upload/deletion with URL preservation and metadata
- **🎵 Voice Activity Monitoring** - Complete voice channel tracking with session analytics
- **🔧 Configurable Events** - Enable/disable specific logging types per server

### 🗃️ **Professional Database Management**
- **📊 Organized Schema Files** - Clean SQL files with automatic migration tracking
- **🔄 Version Control** - Database schema versioning and safe updates  
- **📈 Analytics-Ready** - Tables prepared for advanced statistics and reporting
- **⚡ Performance Optimized** - Comprehensive indexing for fast queries

### 🎛️ **Modular Architecture**
- **🧩 Plug & Play Modules** - Easy to add/remove features
- **🔧 Hot-Swappable Components** - Modify individual logging types independently
- **📦 Clean Separation** - Each feature in dedicated, maintainable modules
- **🚀 Future-Ready** - Architecture designed for easy expansion

### 🎵 **Voice Activity Analytics**
- **⏱️ Session Duration Tracking** - Precise voice time monitoring
- **🔄 Channel Movement Detection** - Track user movement between channels
- **🔇 State Change Monitoring** - Mute, deafen, streaming, video detection
- **📊 Real-time Statistics** - Live voice activity analytics
- **👥 User Behavior Analysis** - Voice usage patterns and insights

## 🚀 **Quick Start**

### **Prerequisites**
- Python 3.8+
- Discord Bot Token
- Administrative permissions in target Discord server

### **Installation**

```bash
# 1. Clone and setup
git clone https://github.com/yourusername/fenrir-bot.git
cd fenrir-bot

# 2. Create virtual environment
python -m venv Discord_Bot
source Discord_Bot/bin/activate  # Linux/Mac
# Discord_Bot\Scripts\activate    # Windows

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure environment
cp .env.example .env
# Edit .env with your Discord bot token

# 5. Run Fenrir
python bot.py
```

### **Discord Bot Setup**
1. Go to [Discord Developer Portal](https://discord.com/developers/applications)
2. Create application → Bot → Copy token to `.env`
3. Enable **Message Content Intent** and **Server Members Intent**
4. Invite with permissions: `Administrator` (or specific: `Send Messages`, `Use Slash Commands`, `View Channels`, `Read Message History`, `Manage Channels`, `View Audit Log`)

## ⚙️ **Configuration**

### **Environment Variables**
```env
# Core Configuration
DISCORD_BOT_TOKEN=your_discord_bot_token_here
BOT_PREFIX=!
ENABLE_LOGGING=true

# Database Configuration  
DATABASE_PATH=./data/fenrir.db

# Enhanced Logging Features
BOT_LOG_LEVEL=INFO
ENABLE_INTERACTION_LOGGING=true
ENABLE_API_LOGGING=true
ENABLE_COMMAND_TIMING=true
ENABLE_MEMORY_MONITORING=false

# Optional: Auto-sync commands on startup
AUTO_SYNC_COMMANDS=false
```

### **Quick Setup Options**

#### 🎯 Option 1: Granular Setup (15+ channels)
##### Creates individual channels for each event type
```bash
/log_setup_granular
```

#### 📋 Option 2: Grouped Setup (4-6 channels)
##### Creates grouped channels for related events
```bash
/log_setup_grouped
```

#### ⚙️ Option 3: Manual Setup
```bash
# 1. Configure logging channel
/log_config channel:#logs enabled:true

# 2. Map specific events to channels
/log_channel event:"Message Deletions" channel:#message-logs
/log_channel event:"Voice Channel Joins" channel:#voice-logs

# 3. Or group multiple events
/log_group events:member_join,member_leave channel:#member-logs

# 4. Check configuration
/log_channels_list
```

## Section 4: Available Commands

## 📊 **Available Commands**

### **Core Commands**
- `/ping` - Check bot responsiveness with detailed metrics
- `/status` - Comprehensive bot health and statistics  
- `/bot_info` - Complete bot information and capabilities
- `/help` - Detailed command reference

### **🔧 Logging Setup Commands**
- `/log_setup_granular` - Auto-create individual channels for each event type
- `/log_setup_grouped` - Auto-create grouped channels for related events
- `/log_config` - Configure basic logging settings
- `/log_channel` - Map specific event to specific channel
- `/log_group` - Map multiple events to one channel

### **📊 Logging Management**
- `/log_channels_list` - View all event-to-channel mappings
- `/log_channels_test` - Send test messages to verify configuration
- `/log_channels_reset` - Reset all channel mappings
- `/log_events` - Enable/disable specific event types
- `/log_events_list` - Show all available event types
- `/log_status` - View current logging configuration

### **🎵 Voice Analytics**
- `/voice_stats` - Voice activity statistics and insights
- `/voice_sessions` - View current active voice sessions

### **👮 Administrative**
- `/sync_commands` - Refresh slash commands (Admin only)
- `/stats` - Detailed bot statistics and performance
- `/db_schema` - Database schema status (Bot Owner only)
- `/list_commands` - List all available commands

### **🔧 Utility Commands**
- `/avatar` - Display user avatars with download links
- `/server_info` - Detailed server information and statistics
- `/user_info` - Comprehensive user profile analysis
- `/channel_info` - Channel details and metadata

### **🔍 Debugging**
- `/log_debug` - Debug logging configuration and routing (Admin only)

## 🏗️ **Architecture Overview**

### **Modular Cog System**
```
cogs/
├── core.py              # Core bot commands with interaction logging
├── admin.py             # Administrative and management commands  
├── utility.py           # Utility commands for users
└── logging/             # Modular logging system
    ├── __init__.py      # Main coordinator and event forwarding
    ├── base.py          # Shared functionality and utilities
    ├── message_logs.py  # Message deletion/edit tracking
    ├── member_logs.py   # Member join/leave/ban monitoring
    ├── attachment_logs.py # File upload/deletion with URL preservation
    ├── voice_logs.py    # Voice activity and session tracking
    └── admin_commands.py # Logging configuration commands
```

### **Smart Channel Routing System**
#### Event → Channel Resolution

1. **Check event-specific channel mapping**
2. **Fallback to default log channel if needed**
3. **Validate channel permissions**
4. **Clean up invalid mappings automatically**

### **Database Schema Organization**
```
data/
├── fenrir.db                    # SQLite database
├── schemas/                     # Organized schema files
│   ├── 001_core_tables.sql     # Guild configs and log events
│   ├── 002_voice_activity.sql  # Voice sessions and analytics
│   ├── 003_analytics.sql       # Advanced analytics tables
│   ├── 004_user_stats.sql      # User behavior analysis
│   ├── 005_event_channel_mapping.sql # Flexible channel routing
│   └── indexes.sql             # Performance optimization
└── migrations/                  # Schema version tracking
└── applied_migrations.txt   # Migration history
```

### **Enhanced Logging Features**
```
utils/
├── bot_logger.py               # Comprehensive interaction logging
├── database.py                 # Schema-based database management
├── embeds.py                   # Professional Discord embeds
├── channel_manager.py          # Automated channel creation
└── enhanced_attachment_logging.py # Advanced file tracking
```

## 📈 **Logging Capabilities**

### **Message Events**
- ✅ **Message Deletions** - Content preservation with metadata
- ✅ **Message Edits** - Before/after comparison with character counts
- ✅ **Attachment Handling** - Separate tracking for media-rich messages

### **Member Events**  
- ✅ **Member Joins** - Account age analysis and spam detection
- ✅ **Member Leaves** - Role preservation and server time tracking
- ✅ **Moderation Actions** - Bans/unbans with audit log integration

### **File & Media Events**
- ✅ **File Uploads** - Complete metadata capture and URL preservation
- ✅ **File Deletions** - Technical details and recovery information
- ✅ **Multi-Image Support** - Enhanced handling for multiple attachments
- ✅ **File Type Detection** - Smart categorization and emoji representation

### **Voice Events** 🎵
- ✅ **Channel Joins/Leaves** - Session duration tracking
- ✅ **Channel Movement** - Inter-channel navigation monitoring  
- ✅ **State Changes** - Mute, deafen, streaming, video detection
- ✅ **Session Analytics** - Real-time statistics and user behavior

## 🎯 **Advanced Features**

### **Professional Database Management**
- **🔄 Automatic Migrations** - Schema files applied automatically
- **📊 Version Tracking** - Complete migration history
- **⚡ Performance Indexes** - Optimized for fast queries
- **🔍 Schema Status Monitoring** - `/db_schema` command for health checks

### **Enhanced Attachment Logging**  
- **🔗 URL Preservation** - Capture attachment URLs before deletion
- **📊 Technical Metadata** - File size, type, dimensions tracking
- **🔍 Debug-Friendly** - Comprehensive logging for troubleshooting
- **📎 Multi-File Support** - Handle complex message attachments

### **Real-Time Voice Analytics**
- **⏱️ Session Duration** - Precise time tracking per user
- **📈 Activity Statistics** - Server-wide voice usage insights
- **👥 User Patterns** - Individual voice behavior analysis
- **🔄 Live Sessions** - Real-time active session monitoring

### **Comprehensive Interaction Logging**
- **📡 API Call Tracking** - Discord API interaction monitoring
- **⚡ Command Timing** - Performance analysis for all commands
- **💥 Error Logging** - Detailed error context and debugging
- **📊 Session Statistics** - Bot performance and usage metrics

## 📋 **Event Types Supported**

| Category | Events | Features |
|----------|--------|----------|
| **Messages** | Deletions, Edits | Content preservation, character diff |
| **Members** | Joins, Leaves, Bans, Unbans | Account analysis, role tracking |  
| **Files** | Uploads, Deletions | URL preservation, metadata capture |
| **Voice** | Joins, Leaves, Moves, Mute, Stream, Video | Session tracking, real-time analytics |

## 🔧 **Development**

### **Adding New Features**

1. **Create Schema File**
```bash
# Add new database tables
cat > data/schemas/005_new_feature.sql << 'EOF'
CREATE TABLE IF NOT EXISTS new_feature_table (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    -- Your table structure
);
EOF
```

2. **Create Logging Module**
```bash
# Add new logging module
touch cogs/logging/new_feature_logs.py
```

3. **Update Coordinator**
```python
# Add to cogs/logging/__init__.py
from .new_feature_logs import NewFeatureLogs
```

### **Database Schema Management**
```bash
# View schema status
/db_schema

# Check applied migrations  
cat data/migrations/applied_migrations.txt

# Database structure inspection
sqlite3 data/fenrir.db ".tables"
sqlite3 data/fenrir.db ".schema guild_configs"
```

## 📊 **Performance & Monitoring**

### **Built-in Monitoring**
- **⚡ Command Execution Times** - Performance tracking for all commands
- **📊 Memory Usage** - Resource consumption monitoring  
- **📡 API Response Times** - Discord API interaction analysis
- **💾 Database Performance** - Query optimization and indexing

### **Log Files Generated**
```
logs/
├── fenrir.log              # General bot operations
├── bot_interactions.log    # All bot interactions
├── command_execution.log   # Command performance tracking
├── discord_api.log        # Discord API call logging
├── bot_errors.log         # Error tracking and debugging
└── attachments.log        # Dedicated attachment tracking
```

## 🛡️ **Security & Privacy**

### **Data Protection**
- **🔐 Environment Variables** - Secure credential storage
- **📊 Metadata Only** - No sensitive content stored (configurable)
- **🔒 Permission Validation** - Admin-only configuration commands
- **⏰ Automatic Cleanup** - Configurable data retention policies

### **Privacy Features**
- **👤 User Anonymization** - Optional user ID obfuscation
- **📝 Content Filters** - Exclude sensitive message content
- **🔍 Audit Trails** - Complete logging of all administrative actions

## 📈 **Roadmap**

### **Coming Soon**
- 🎯 **Advanced Analytics Dashboard** - Web-based insights and reporting
- 🔍 **Message Search System** - Full-text search across message history
- 🤖 **AI-Powered Insights** - Automated pattern detection and alerts
- 📱 **Mobile Dashboard** - Real-time monitoring on mobile devices
- 🌐 **Multi-Server Management** - Centralized control across servers

### **Future Enhancements**
- **Role & Permission Tracking** - Advanced permission audit trails
- **Custom Event Types** - User-defined logging events
- **Integration APIs** - Webhook support for external systems
- **Advanced Visualization** - Charts and graphs for activity patterns

## 🤝 **Contributing**

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open Pull Request

### **Development Setup**
```bash
# Install development dependencies
pip install -r requirements-dev.txt

# Run tests
python -m pytest

# Check code quality
flake8 --max-line-length=100 *.py cogs/ utils/
```

## 📜 **License**

This project is released into the public domain under the [Unlicense](LICENSE). Feel free to use, modify, and distribute as needed.

## 🆘 **Support**

### **Documentation**
- **Setup Guide** - [docs/setup.md](docs/setup.md)
- **Configuration Reference** - [docs/configuration.md](docs/configuration.md)  
- **API Documentation** - [docs/api.md](docs/api.md)
- **Troubleshooting** - [docs/troubleshooting.md](docs/troubleshooting.md)

### **Getting Help**
- 📖 Check the documentation in the `docs/` folder
- 🐛 Open an issue for bugs or feature requests
- 💬 Join our Discord server for community support
- 📧 Email support for private inquiries

### **Common Issues**
- **Bot not responding** → Check token in `.env` and bot permissions
- **Commands not showing** → Run `/sync_commands` or restart bot
- **Database errors** → Check file permissions and schema status with `/db_schema`
- **Voice logging not working** → Ensure bot can see voice channels

---

<div align="center">

**🐺 Fenrir - Professional Discord Server Monitoring**

*Built with Python • Discord.py • SQLite • Love*

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://python.org)
[![Discord.py](https://img.shields.io/badge/Discord.py-2.3+-blue.svg)](https://discordpy.readthedocs.io/)
[![License](https://img.shields.io/badge/License-Unlicense-green.svg)](LICENSE)

</div>
