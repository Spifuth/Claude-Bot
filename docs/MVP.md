# Fenrir Web Configuration Interface - Updated MVP

## 🎯 Goal
Add a web configuration interface to your existing clean Fenrir Discord bot for guild-specific logging and display settings.

## 📊 Current State Analysis

### ✅ What You Have (Solid Foundation)
- **Clean Discord Bot**: Core, admin, and utility commands working
- **Modular Architecture**: Proper cog system with clean separation
- **Configuration Management**: Environment-based config system
- **Embed System**: Professional Discord embed utilities
- **Logging Infrastructure**: File and console logging setup
- **No Complexity**: Removed unnecessary homelab API dependencies

### 🔄 What We'll Add
- **Database Layer**: SQLite for guild-specific settings
- **Logging Cog**: Configurable event logging that reads from database
- **Web Backend**: FastAPI for configuration management
- **Web Frontend**: React dashboard for easy configuration
- **Discord OAuth**: Secure authentication for guild management

## 🏗️ Updated Architecture

### Tech Stack
```
Frontend: React + Tailwind CSS + TypeScript
Backend: FastAPI (Python) - matches your existing Python bot
Database: SQLite (simple, no server needed)
Authentication: Discord OAuth 2.0
Bot: Your existing Fenrir (discord.py)
```

### File Structure
```
fenrir-project/
├── bot/                          # Your existing bot (slightly modified)
│   ├── bot.py
│   ├── config.py                 # Enhanced with database config
│   ├── cogs/
│   │   ├── core.py
│   │   ├── admin.py
│   │   ├── utility.py
│   │   └── logging.py            # NEW: Configurable logging
│   ├── utils/
│   │   ├── embeds.py
│   │   └── database.py           # NEW: Database operations
│   └── requirements.txt
├── web-backend/                  # NEW: Configuration API
│   ├── main.py
│   ├── models/
│   │   ├── database.py
│   │   └── schemas.py
│   ├── routes/
│   │   ├── auth.py
│   │   ├── guilds.py
│   │   └── config.py
│   └── requirements.txt
├── web-frontend/                 # NEW: React dashboard
│   ├── src/
│   │   ├── components/
│   │   ├── pages/
│   │   └── utils/
│   └── package.json
├── shared/
│   └── fenrir.db                # SQLite database
└── docker-compose.yml          # Complete deployment
```

## 💾 Database Schema (SQLite)

### `guild_configs`
```sql
CREATE TABLE guild_configs (
    guild_id TEXT PRIMARY KEY,
    guild_name TEXT,
    
    -- Logging Settings
    logging_enabled BOOLEAN DEFAULT 0,
    log_channel_id TEXT,
    log_format TEXT DEFAULT 'embed', -- 'embed', 'text'
    
    -- Display Settings
    show_avatars BOOLEAN DEFAULT 1,
    show_timestamps BOOLEAN DEFAULT 1,
    embed_color TEXT DEFAULT '#3498db',
    
    -- Timestamps
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### `log_events`
```sql
CREATE TABLE log_events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    guild_id TEXT,
    event_type TEXT, -- 'message_delete', 'member_join', etc.
    enabled BOOLEAN DEFAULT 0,
    
    FOREIGN KEY (guild_id) REFERENCES guild_configs (guild_id),
    UNIQUE(guild_id, event_type)
);
```

## 🤖 Enhanced Bot Components

### 1. Updated `config.py`
```python
"""
Enhanced Fenrir Bot Configuration
"""

import os
from dotenv import load_dotenv

load_dotenv()

class BotConfig:
    # Existing configuration...
    DISCORD_TOKEN = os.getenv('DISCORD_BOT_TOKEN')
    PREFIX = os.getenv('BOT_PREFIX', '!')
    
    # NEW: Database Configuration
    DATABASE_PATH = os.getenv('DATABASE_PATH', './shared/fenrir.db')
    
    # NEW: Web Configuration  
    ENABLE_WEB_CONFIG = os.getenv('ENABLE_WEB_CONFIG', 'false').lower() == 'true'
    WEB_BACKEND_URL = os.getenv('WEB_BACKEND_URL', 'http://localhost:8000')
    
    # Enhanced Module Configuration
    MODULES_ENABLED = {
        'logging': os.getenv('ENABLE_LOGGING', 'false').lower() == 'true',
        'web_config': os.getenv('ENABLE_WEB_CONFIG', 'false').lower() == 'true',
    }
    
    # Existing settings...
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO').upper()
    REQUEST_TIMEOUT = int(os.getenv('REQUEST_TIMEOUT', '30'))
    
    @classmethod
    def validate(cls):
        if not cls.DISCORD_TOKEN:
            raise ValueError("DISCORD_BOT_TOKEN environment variable is required!")
        return True

BotConfig.validate()
```

### 2. New `utils/database.py`
```python
"""
Database utilities for guild configuration
"""

import aiosqlite
import logging
from pathlib import Path
from typing import Dict, List, Optional, Any

logger = logging.getLogger(__name__)

class DatabaseManager:
    def __init__(self, db_path: str):
        self.db_path = db_path
        # Ensure directory exists
        Path(db_path).parent.mkdir(parents=True, exist_ok=True)
    
    async def initialize(self):
        """Initialize database with required tables"""
        async with aiosqlite.connect(self.db_path) as db:
            # Create guild_configs table
            await db.execute('''
                CREATE TABLE IF NOT EXISTS guild_configs (
                    guild_id TEXT PRIMARY KEY,
                    guild_name TEXT,
                    logging_enabled BOOLEAN DEFAULT 0,
                    log_channel_id TEXT,
                    log_format TEXT DEFAULT 'embed',
                    show_avatars BOOLEAN DEFAULT 1,
                    show_timestamps BOOLEAN DEFAULT 1,
                    embed_color TEXT DEFAULT '#3498db',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Create log_events table
            await db.execute('''
                CREATE TABLE IF NOT EXISTS log_events (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    guild_id TEXT,
                    event_type TEXT,
                    enabled BOOLEAN DEFAULT 0,
                    FOREIGN KEY (guild_id) REFERENCES guild_configs (guild_id),
                    UNIQUE(guild_id, event_type)
                )
            ''')
            
            await db.commit()
            logger.info("Database initialized successfully")
    
    async def get_guild_config(self, guild_id: str) -> Optional[Dict[str, Any]]:
        """Get configuration for a guild"""
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute(
                "SELECT * FROM guild_configs WHERE guild_id = ?", 
                (guild_id,)
            ) as cursor:
                row = await cursor.fetchone()
                return dict(row) if row else None
    
    async def create_or_update_guild_config(self, guild_id: str, config: Dict[str, Any]):
        """Create or update guild configuration"""
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute('''
                INSERT OR REPLACE INTO guild_configs 
                (guild_id, guild_name, logging_enabled, log_channel_id, log_format, 
                 show_avatars, show_timestamps, embed_color, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
            ''', (
                guild_id,
                config.get('guild_name'),
                config.get('logging_enabled', False),
                config.get('log_channel_id'),
                config.get('log_format', 'embed'),
                config.get('show_avatars', True),
                config.get('show_timestamps', True),
                config.get('embed_color', '#3498db')
            ))
            await db.commit()
    
    async def get_log_events(self, guild_id: str) -> List[Dict[str, Any]]:
        """Get enabled log events for a guild"""
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute(
                "SELECT * FROM log_events WHERE guild_id = ? AND enabled = 1",
                (guild_id,)
            ) as cursor:
                rows = await cursor.fetchall()
                return [dict(row) for row in rows]
    
    async def set_log_event(self, guild_id: str, event_type: str, enabled: bool):
        """Enable or disable a log event for a guild"""
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute('''
                INSERT OR REPLACE INTO log_events (guild_id, event_type, enabled)
                VALUES (?, ?, ?)
            ''', (guild_id, event_type, enabled))
            await db.commit()

# Global database manager instance
db_manager = None

async def init_database(db_path: str):
    """Initialize the global database manager"""
    global db_manager
    db_manager = DatabaseManager(db_path)
    await db_manager.initialize()

async def get_guild_config(guild_id: str) -> Optional[Dict[str, Any]]:
    """Get guild configuration"""
    if db_manager:
        return await db_manager.get_guild_config(str(guild_id))
    return None

async def is_logging_enabled(guild_id: str) -> bool:
    """Check if logging is enabled for a guild"""
    config = await get_guild_config(str(guild_id))
    return config and config.get('logging_enabled', False)

async def is_event_enabled(guild_id: str, event_type: str) -> bool:
    """Check if specific event logging is enabled"""
    if db_manager:
        events = await db_manager.get_log_events(str(guild_id))
        return any(event['event_type'] == event_type for event in events)
    return False
```

### 3. New `cogs/logging.py`
```python
"""
Configurable Logging Cog
Database-driven event logging with web configuration support
"""

import discord
from discord.ext import commands
from discord import app_commands
import logging
from datetime import datetime
from typing import Optional

from utils.database import get_guild_config, is_logging_enabled, is_event_enabled
from utils.embeds import EmbedBuilder

logger = logging.getLogger(__name__)

class ConfigurableLogging(commands.Cog):
    """Configurable event logging for guilds"""
    
    def __init__(self, bot):
        self.bot = bot
    
    def cog_check(self, ctx):
        """Check if logging module is enabled"""
        return self.bot.config.MODULES_ENABLED.get('logging', False)
    
    async def send_log(self, guild: discord.Guild, event_type: str, embed: discord.Embed):
        """Send log message to configured channel"""
        try:
            config = await get_guild_config(str(guild.id))
            if not config or not config.get('log_channel_id'):
                return
            
            log_channel = guild.get_channel(int(config['log_channel_id']))
            if not log_channel:
                logger.warning(f"Log channel not found for guild {guild.id}")
                return
            
            # Apply guild-specific styling
            if config.get('embed_color'):
                try:
                    embed.color = discord.Color(int(config['embed_color'].replace('#', ''), 16))
                except:
                    pass  # Keep default color if invalid
            
            # Add timestamp if enabled
            if config.get('show_timestamps', True):
                embed.timestamp = datetime.utcnow()
            
            await log_channel.send(embed=embed)
            
        except Exception as e:
            logger.error(f"Failed to send log message: {e}")
    
    # ==================== EVENT LISTENERS ====================
    
    @commands.Cog.listener()
    async def on_message_delete(self, message):
        """Log message deletions"""
        if message.author.bot:
            return
        
        if not await is_logging_enabled(str(message.guild.id)):
            return
        
        if not await is_event_enabled(str(message.guild.id), 'message_delete'):
            return
        
        embed = discord.Embed(
            title="🗑️ Message Deleted",
            color=discord.Color.red()
        )
        
        embed.add_field(
            name="Author",
            value=f"{message.author.mention} ({message.author})",
            inline=True
        )
        
        embed.add_field(
            name="Channel",
            value=message.channel.mention,
            inline=True
        )
        
        if message.content:
            content = message.content[:1000] + "..." if len(message.content) > 1000 else message.content
            embed.add_field(
                name="Content",
                value=f"```{content}```",
                inline=False
            )
        
        # Add avatar if enabled
        config = await get_guild_config(str(message.guild.id))
        if config and config.get('show_avatars', True) and message.author.avatar:
            embed.set_thumbnail(url=message.author.avatar.url)
        
        await self.send_log(message.guild, 'message_delete', embed)
    
    @commands.Cog.listener()
    async def on_message_edit(self, before, after):
        """Log message edits"""
        if before.author.bot or before.content == after.content:
            return
        
        if not await is_logging_enabled(str(before.guild.id)):
            return
        
        if not await is_event_enabled(str(before.guild.id), 'message_edit'):
            return
        
        embed = discord.Embed(
            title="📝 Message Edited",
            color=discord.Color.orange()
        )
        
        embed.add_field(
            name="Author",
            value=f"{before.author.mention} ({before.author})",
            inline=True
        )
        
        embed.add_field(
            name="Channel",
            value=before.channel.mention,
            inline=True
        )
        
        embed.add_field(
            name="Jump to Message",
            value=f"[Click here]({after.jump_url})",
            inline=True
        )
        
        # Before content
        if before.content:
            before_content = before.content[:500] + "..." if len(before.content) > 500 else before.content
            embed.add_field(
                name="Before",
                value=f"```{before_content}```",
                inline=False
            )
        
        # After content
        if after.content:
            after_content = after.content[:500] + "..." if len(after.content) > 500 else after.content
            embed.add_field(
                name="After",
                value=f"```{after_content}```",
                inline=False
            )
        
        config = await get_guild_config(str(before.guild.id))
        if config and config.get('show_avatars', True) and before.author.avatar:
            embed.set_thumbnail(url=before.author.avatar.url)
        
        await self.send_log(before.guild, 'message_edit', embed)
    
    @commands.Cog.listener()
    async def on_member_join(self, member):
        """Log member joins"""
        if not await is_logging_enabled(str(member.guild.id)):
            return
        
        if not await is_event_enabled(str(member.guild.id), 'member_join'):
            return
        
        embed = discord.Embed(
            title="👋 Member Joined",
            color=discord.Color.green()
        )
        
        embed.add_field(
            name="Member",
            value=f"{member.mention} ({member})",
            inline=True
        )
        
        embed.add_field(
            name="Account Created",
            value=f"<t:{int(member.created_at.timestamp())}:R>",
            inline=True
        )
        
        embed.add_field(
            name="Member Count",
            value=str(member.guild.member_count),
            inline=True
        )
        
        config = await get_guild_config(str(member.guild.id))
        if config and config.get('show_avatars', True) and member.avatar:
            embed.set_thumbnail(url=member.avatar.url)
        
        await self.send_log(member.guild, 'member_join', embed)
    
    @commands.Cog.listener()
    async def on_member_remove(self, member):
        """Log member leaves"""
        if not await is_logging_enabled(str(member.guild.id)):
            return
        
        if not await is_event_enabled(str(member.guild.id), 'member_leave'):
            return
        
        embed = discord.Embed(
            title="👋 Member Left",
            color=discord.Color.red()
        )
        
        embed.add_field(
            name="Member",
            value=f"{member} (ID: {member.id})",
            inline=True
        )
        
        embed.add_field(
            name="Joined",
            value=f"<t:{int(member.joined_at.timestamp())}:R>" if member.joined_at else "Unknown",
            inline=True
        )
        
        embed.add_field(
            name="Member Count",
            value=str(member.guild.member_count),
            inline=True
        )
        
        config = await get_guild_config(str(member.guild.id))
        if config and config.get('show_avatars', True) and member.avatar:
            embed.set_thumbnail(url=member.avatar.url)
        
        await self.send_log(member.guild, 'member_leave', embed)
    
    # ==================== ADMIN COMMANDS ====================
    
    @app_commands.command(name="log_config", description="Configure logging for this server (Admin only)")
    @app_commands.describe(
        channel="Channel to send logs to",
        enabled="Enable or disable logging"
    )
    async def log_config(
        self, 
        interaction: discord.Interaction, 
        channel: Optional[discord.TextChannel] = None,
        enabled: Optional[bool] = None
    ):
        """Configure logging settings for the guild"""
        
        if not interaction.user.guild_permissions.administrator:
            embed = EmbedBuilder.error(
                "Permission Denied",
                "You need administrator permissions to configure logging."
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        if not self.bot.config.MODULES_ENABLED.get('logging', False):
            embed = EmbedBuilder.error(
                "Logging Disabled",
                "The logging module is not enabled on this bot."
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        guild_id = str(interaction.guild.id)
        config = await get_guild_config(guild_id) or {}
        
        # Update configuration
        if channel is not None:
            config['log_channel_id'] = str(channel.id)
        if enabled is not None:
            config['logging_enabled'] = enabled
        
        config['guild_name'] = interaction.guild.name
        
        # Save to database
        from utils.database import db_manager
        if db_manager:
            await db_manager.create_or_update_guild_config(guild_id, config)
        
        embed = EmbedBuilder.success(
            "Logging Configuration Updated",
            "Your logging settings have been saved."
        )
        
        if config.get('log_channel_id'):
            log_channel = interaction.guild.get_channel(int(config['log_channel_id']))
            embed.add_field(
                name="Log Channel",
                value=log_channel.mention if log_channel else "Not set",
                inline=True
            )
        
        embed.add_field(
            name="Logging Enabled",
            value="Yes" if config.get('logging_enabled', False) else "No",
            inline=True
        )
        
        embed.add_field(
            name="💡 Tip",
            value="Use the web dashboard for advanced configuration options!",
            inline=False
        )
        
        await interaction.response.send_message(embed=embed, ephemeral=True)

async def setup(bot):
    """Setup function for the cog"""
    await bot.add_cog(ConfigurableLogging(bot))
    logger.info("Configurable logging cog loaded")
```

### 4. Updated `bot.py`
```python
#!/usr/bin/env python3
"""
Fenrir - Modular Discord Bot
Main bot file with automatic cog loading and database support
"""

import discord
from discord.ext import commands
import asyncio
import os
import logging
from pathlib import Path

from config import BotConfig
from utils.database import init_database

# Create logs directory if it doesn't exist
os.makedirs("logs", exist_ok=True)

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/fenrir.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class FenrirBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        intents.members = True  # Required for member join/leave events
        
        super().__init__(
            command_prefix=BotConfig.PREFIX,
            intents=intents,
            help_command=None
        )
        
        self.config = BotConfig
        
    async def setup_hook(self):
        """Called when the bot is starting up"""
        logger.info("🐺 Fenrir is awakening...")
        
        # Initialize database if logging is enabled
        if self.config.MODULES_ENABLED.get('logging', False):
            await init_database(self.config.DATABASE_PATH)
            logger.info("Database initialized")
        
        # Load all cogs
        await self.load_cogs()
        
        # Sync commands
        await self.tree.sync()
        logger.info(f"Synced slash commands for {self.user}")

    async def load_cogs(self):
        """Load all cog files"""
        # Always load core cogs
        core_cogs = ["cogs.core", "cogs.admin", "cogs.utility"]
        
        # Optional cogs based on configuration
        if self.config.MODULES_ENABLED.get('logging', False):
            core_cogs.append("cogs.logging")
        
        for cog in core_cogs:
            try:
                await self.load_extension(cog)
                logger.info(f"✅ Loaded {cog}")
            except Exception as e:
                logger.error(f"❌ Failed to load {cog}: {e}")

    async def on_ready(self):
        """Called when the bot is ready"""
        logger.info(f'🐺 Fenrir has awakened and connected to Discord!')
        logger.info(f'Bot: {self.user} (ID: {self.user.id})')
        logger.info(f'Guilds: {len(self.guilds)}')
        
        # Log enabled modules
        enabled_modules = [name for name, enabled in self.config.MODULES_ENABLED.items() if enabled]
        if enabled_modules:
            logger.info(f'✅ Enabled modules: {", ".join(enabled_modules)}')

# Rest of bot.py remains the same...
```

## 🌐 Web Backend (FastAPI)

### `web-backend/main.py`
```python
from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer
import os

app = FastAPI(title="Fenrir Configuration API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
from routes import auth, guilds, config
app.include_router(auth.router, prefix="/auth")
app.include_router(guilds.router, prefix="/api/guilds") 
app.include_router(config.router, prefix="/api/config")

@app.get("/")
async def root():
    return {"message": "Fenrir Configuration API"}

@app.get("/health")
async def health():
    return {"status": "healthy"}
```

## 📋 Implementation Timeline

### Week 1: Database Foundation
1. **Add database utilities** to your bot
2. **Create the logging cog** with basic events
3. **Update bot.py** to initialize database
4. **Test logging** with manual commands

### Week 2: Web Backend
1. **Setup FastAPI** with Discord OAuth
2. **Create database models** and CRUD operations
3. **Build authentication** middleware
4. **Add configuration endpoints**

### Week 3: Web Frontend
1. **Create React app** with login flow
2. **Build guild selector** component
3. **Add configuration panels** for logging
4. **Implement real-time preview**

### Week 4: Integration & Polish
1. **Connect all components** together
2. **Add error handling** and loading states
3. **Deploy with Docker**
4. **Test full workflow**

## 🚀 Quick Start Commands

### 1. Enable Logging Module
```bash
# Add to your .env file
echo "ENABLE_LOGGING=true" >> .env
echo "DATABASE_PATH=./shared/fenrir.db" >> .env
```

### 2. Install New Dependencies
```bash
pip install aiosqlite fastapi uvicorn
```

### 3. Test Database
```python
# Test database initialization
python -c "
import asyncio
from utils.database import init_database
asyncio.run(init_database('./shared/fenrir.db'))
print('Database created successfully!')
"
```

### 4. Restart Bot
```bash
python bot.py
```

This MVP builds directly on your existing clean foundation and adds exactly what you need: database-driven logging with web configuration. Each component can be implemented and tested independently!

Would you like me to start with any specific component, such as:
- **Database setup** and logging cog implementation?
- **FastAPI backend** structure?
- **React frontend** components?
- **Docker deployment** configuration?
