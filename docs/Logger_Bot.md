# 🤖 Fenrir Bot Interaction Logging Setup Guide

## 📁 File Structure
After implementing the logging system, your bot structure will be:

```
Claude-Bot/
├── bot.py                    # Updated with logging integration
├── config.py                 # Enhanced configuration
├── requirements.txt          # Updated dependencies
├── cogs/
│   ├── core.py              # Updated with logging
│   ├── admin.py
│   ├── utility.py
│   └── logging.py
├── utils/
│   ├── bot_logger.py        # NEW: Interaction logging system
│   ├── database.py
│   └── embeds.py
└── logs/                    # Auto-created log directory
    ├── fenrir.log          # Basic bot logs
    ├── bot_interactions.log # All bot interactions
    ├── discord_api.log     # Discord API calls
    ├── command_execution.log # Command executions
    └── bot_errors.log      # Error logs
```

## 🔧 Configuration Updates

### 1. Update your `.env` file:
```env
# Existing configuration
DISCORD_BOT_TOKEN=your_bot_token_here
BOT_PREFIX=!
ENABLE_LOGGING=true

# NEW: Interaction logging configuration
BOT_LOG_LEVEL=INFO
ENABLE_INTERACTION_LOGGING=true
ENABLE_API_LOGGING=true
ENABLE_COMMAND_TIMING=true

# Optional: Performance monitoring
ENABLE_MEMORY_MONITORING=true
```

### 2. Update your `config.py`:
```python
"""
Enhanced Fenrir Bot Configuration with Interaction Logging
"""

import os
from dotenv import load_dotenv

load_dotenv()

class BotConfig:
    """Enhanced bot configuration class"""
    
    # Existing Discord Configuration
    DISCORD_TOKEN = os.getenv('DISCORD_BOT_TOKEN')
    PREFIX = os.getenv('BOT_PREFIX', '!')
    
    # Existing Database Configuration
    DATABASE_PATH = os.getenv('DATABASE_PATH', './data/fenrir.db')
    
    # Enhanced Logging Configuration
    LOG_LEVEL = os.getenv('BOT_LOG_LEVEL', 'INFO').upper()
    ENABLE_INTERACTION_LOGGING = os.getenv('ENABLE_INTERACTION_LOGGING', 'true').lower() == 'true'
    ENABLE_API_LOGGING = os.getenv('ENABLE_API_LOGGING', 'true').lower() == 'true'
    ENABLE_COMMAND_TIMING = os.getenv('ENABLE_COMMAND_TIMING', 'true').lower() == 'true'
    ENABLE_MEMORY_MONITORING = os.getenv('ENABLE_MEMORY_MONITORING', 'false').lower() == 'true'
    
    # Enhanced Module Configuration
    MODULES_ENABLED = {
        'logging': os.getenv('ENABLE_LOGGING', 'false').lower() == 'true',
        'interaction_logging': ENABLE_INTERACTION_LOGGING,
        'api_logging': ENABLE_API_LOGGING,
        'command_timing': ENABLE_COMMAND_TIMING,
    }
    
    # Existing Bot Settings
    AUTO_SYNC_COMMANDS = os.getenv('AUTO_SYNC_COMMANDS', 'false').lower() == 'true'
    REQUEST_TIMEOUT = int(os.getenv('REQUEST_TIMEOUT', '30'))
    MAX_EMBED_FIELDS = int(os.getenv('MAX_EMBED_FIELDS', '25'))
    
    @classmethod
    def validate(cls):
        """Enhanced validation"""
        if not cls.DISCORD_TOKEN:
            raise ValueError("DISCORD_BOT_TOKEN environment variable is required!")
        
        # Validate log level
        valid_levels = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
        if cls.LOG_LEVEL not in valid_levels:
            raise ValueError(f"BOT_LOG_LEVEL must be one of: {', '.join(valid_levels)}")
        
        return True

# Validate configuration on import
BotConfig.validate()
```

### 3. Update `requirements.txt`:
```txt
discord.py>=2.3.0
python-dotenv>=1.0.0
qrcode[pil]>=7.4.2
Pillow>=9.5.0
aiosqlite>=0.19.0
psutil>=5.9.0  # NEW: For memory monitoring
```

## 🚀 Installation & Setup

### 1. Install the new logger file:
Save the `bot_logger.py` code to `utils/bot_logger.py`

### 2. Update your existing files:
- Replace `bot.py` with the enhanced version
- Update your `cogs/core.py` (or any other cogs you want enhanced logging for)
- Update `config.py` with the new configuration options

### 3. Install new dependencies:
```bash
# Activate your virtual environment
source Discord_Bot/bin/activate  # Linux/Mac
# OR
Discord_Bot\Scripts\activate     # Windows

# Install new dependencies
pip install psutil>=5.9.0
```

### 4. Update your environment:
```bash
# Add new environment variables to your .env file
echo "BOT_LOG_LEVEL=INFO" >> .env
echo "ENABLE_INTERACTION_LOGGING=true" >> .env
echo "ENABLE_API_LOGGING=true" >> .env
echo "ENABLE_COMMAND_TIMING=true" >> .env
echo "ENABLE_MEMORY_MONITORING=true" >> .env
```

## 📊 What You'll See

### 1. Terminal Output (Real-time):
```
2025-01-08 14:30:15 | INFO | 🚀 BOT STARTUP COMPLETE
2025-01-08 14:30:16 | INFO | ⚡ COMMAND EXECUTED: /ping
2025-01-08 14:30:16 | INFO |    👤 User: User#1234 (123456789)
2025-01-08 14:30:16 | INFO |    🏰 Guild: My Server (987654321)
2025-01-08 14:30:16 | INFO |    ⏱️  Time: 45.2ms
2025-01-08 14:30:20 | INFO | 📡 DISCORD EVENT: message_received
2025-01-08 14:30:25 | INFO | 💬 MESSAGE DELETED: 123456789012345
```

### 2. Log Files Generated:

#### `logs/bot_interactions.log` - All bot interactions:
```
2025-01-08 14:30:15 | Fenrir.interactions | INFO | 🚀 BOT STARTUP COMPLETE
2025-01-08 14:30:15 | Fenrir.interactions | INFO | 📊 Startup Info: {
  "bot_id": 123456789,
  "bot_name": "Fenrir",
  "guilds_count": 5,
  "user_count": 1250,
  "intents": "<Intents value=3276799>",
  "python_version": "2.3.2"
}
```

#### `logs/command_execution.log` - Command tracking:
```
2025-01-08 14:30:16 | Fenrir.commands | INFO | ⚡ COMMAND EXECUTED: /ping
2025-01-08 14:30:16 | Fenrir.commands | INFO |    👤 User: User#1234 (123456789)
2025-01-08 14:30:16 | Fenrir.commands | INFO |    🏰 Guild: My Server (987654321)
2025-01-08 14:30:16 | Fenrir.commands | INFO |    📝 Args: {"target": "google.com"}
2025-01-08 14:30:16 | Fenrir.commands | INFO |    ⏱️  Time: 45.2ms
```

#### `logs/discord_api.log` - API calls:
```
2025-01-08 14:30:16 | Fenrir.discord_api | INFO | ✅ API REQUEST: POST /interactions/{id}/{token}/callback
2025-01-08 14:30:16 | Fenrir.discord_api | INFO |    📊 Status: 204
2025-01-08 14:30:16 | Fenrir.discord_api | INFO |    ⏱️  Time: 89.3ms
```

#### `logs/bot_errors.log` - Error tracking:
```
2025-01-08 14:35:22 | Fenrir.errors | ERROR | 💥 ERROR: CommandInvokeError
2025-01-08 14:35:22 | Fenrir.errors | ERROR |    📝 Message: Command raised an exception: HTTPException: 404 Not Found
2025-01-08 14:35:22 | Fenrir.errors | ERROR |    🔍 Context: Ping command execution failed
2025-01-08 14:35:22 | Fenrir.errors | ERROR |    👤 User: User#1234 (123456789)
```

## 🎛️ Logging Controls

### Enable/Disable Logging:
```python
# In your bot code, you can control logging:
from utils.bot_logger import get_bot_logger

# Get the logger instance
logger = get_bot_logger()

# Log session statistics
logger.log_session_stats()

# Debug dump any data
logger.debug_dump({"test": "data"}, "My Debug Info")
```

### Log Levels:
- `DEBUG`: Everything (very verbose)
- `INFO`: Standard operations (recommended)
- `WARNING`: Warnings and errors only
- `ERROR`: Errors only
- `CRITICAL`: Critical errors only

### Quick Log Functions:
```python
from utils.bot_logger import log_command, log_event, log_error, log_message

# Log a command execution
log_command(interaction, "my_command", {"arg1": "value"}, 0.123)

# Log a Discord event
log_event("custom_event", {"data": "value"})

# Log an error
log_error(exception, "What went wrong", interaction)

# Log a message interaction
log_message(message, "processed", "Additional details")
```

## 📈 Monitoring Your Bot

### Real-time Monitoring:
```bash
# Watch all interactions live
tail -f logs/bot_interactions.log

# Watch only commands
tail -f logs/command_execution.log

# Watch errors
tail -f logs/bot_errors.log

# Watch everything
tail -f logs/*.log
```

### Session Statistics:
Your bot will automatically log session statistics including:
- Commands executed
- Events received  
- API calls made
- Errors encountered
- Session duration

## 🎯 Benefits

1. **Complete Transparency**: See everything your bot does
2. **Performance Monitoring**: Track command execution times
3. **Error Tracking**: Comprehensive error logging with context
4. **User Activity**: Monitor how users interact with your bot
5. **API Usage**: Track Discord API calls and response times
6. **Debugging**: Easily identify issues with detailed logs
7. **Statistics**: Monitor bot usage and performance over time

## 🔧 Customization

You can customize the logging by modifying the `BotInteractionLogger` class:

- Add new log types
- Change log formats
- Add custom metrics
- Create specialized loggers
- Modify output destinations

## 🚨 Important Notes

1. **Log File Size**: Monitor log file sizes in production
2. **Performance**: Logging adds minimal overhead but monitor in high-traffic scenarios
3. **Privacy**: Be mindful of what data you log (avoid logging sensitive information)
4. **Storage**: Log files will grow over time - consider log rotation
5. **Debugging**: Use DEBUG level only for development - it's very verbose

## 🎉 Quick Test

After setup, run these commands to test:

1. Start your bot: `python bot.py`
2. Use `/ping` in Discord
3. Check the logs: `ls -la logs/`
4. View interactions: `cat logs/bot_interactions.log`

You should see comprehensive logging of all bot interactions!