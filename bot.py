#!/usr/bin/env python3
"""
Fenrir - Modular Discord Bot
Main bot file with automatic cog loading
"""

import discord
from discord.ext import commands
import asyncio
import os
import logging
from pathlib import Path

from config import BotConfig
from utils.api_client import HomelabClient

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
        
        super().__init__(
            command_prefix=BotConfig.PREFIX,
            intents=intents,
            help_command=None  # We'll create our own
        )
        
        # Initialize API client
        self.homelab_client = HomelabClient(
            base_url=BotConfig.HOMELAB_BASE_URL,
            api_key=BotConfig.HOMELAB_API_KEY
        )
        
        # Store configuration
        self.config = BotConfig
        
    async def setup_hook(self):
        """Called when the bot is starting up"""
        logger.info("🐺 Fenrir is awakening...")
        
        # Load all cogs
        await self.load_cogs()
        
        # Sync commands
        await self.tree.sync()
        logger.info(f"Synced slash commands for {self.user}")

    async def load_cogs(self):
        """Load all cog files from the cogs directory"""
        cogs_dir = Path("cogs")
        
        # Always load core and admin cogs
        core_cogs = ["cogs.core", "cogs.admin"]
        
        for cog in core_cogs:
            try:
                await self.load_extension(cog)
                logger.info(f"✅ Loaded {cog}")
            except Exception as e:
                logger.error(f"❌ Failed to load {cog}: {e}")
        
        # Load optional cogs based on configuration
        optional_cogs = {
            "cogs.homelab": BotConfig.MODULES_ENABLED.get("homelab", False),
            # Add more optional cogs here
            # "cogs.music": BotConfig.MODULES_ENABLED.get("music", False),
        }
        
        for cog, enabled in optional_cogs.items():
            if enabled:
                try:
                    await self.load_extension(cog)
                    logger.info(f"✅ Loaded optional cog: {cog}")
                except Exception as e:
                    logger.error(f"❌ Failed to load optional cog {cog}: {e}")
            else:
                logger.info(f"⏭️ Skipped disabled cog: {cog}")

    async def on_ready(self):
        """Called when the bot is ready"""
        logger.info(f'🐺 Fenrir has awakened and connected to Discord!')
        logger.info(f'Bot: {self.user} (ID: {self.user.id})')
        logger.info(f'Guilds: {len(self.guilds)}')
        
        # Log enabled modules
        enabled_modules = [name for name, enabled in BotConfig.MODULES_ENABLED.items() if enabled]
        if enabled_modules:
            logger.info(f'✅ Enabled modules: {", ".join(enabled_modules)}')
        else:
            logger.info('📝 No optional modules enabled')

    async def on_command_error(self, ctx, error):
        """Handle command errors"""
        if isinstance(error, commands.CommandNotFound):
            return  # Ignore unknown commands
        
        logger.error(f"Command error: {error}")

# Bot instance
bot = FenrirBot()

async def main():
    """Main function to run the bot"""
    try:
        # Create logs directory if it doesn't exist
        os.makedirs("logs", exist_ok=True)
        
        await bot.start(BotConfig.DISCORD_TOKEN)
    except KeyboardInterrupt:
        logger.info("🛑 Bot stopped by user")
    except Exception as e:
        logger.error(f"❌ Bot crashed: {e}")
    finally:
        await bot.close()

if __name__ == "__main__":
    asyncio.run(main())