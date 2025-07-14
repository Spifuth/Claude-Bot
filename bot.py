#!/usr/bin/env python3
"""
Fenrir - Modular Discord Bot with Comprehensive Interaction Logging
Main bot file with automatic cog loading, database support, and complete interaction tracking
"""

import discord
from discord.ext import commands
import asyncio
import os
import logging
import time
from pathlib import Path
from typing import Any, Dict

from config import BotConfig
from utils.bot_logger import init_bot_logger, get_bot_logger, log_command, log_event, log_error, log_message, \
    log_member, log_guild

# Create logs and data directories if they don't exist
os.makedirs("logs", exist_ok=True)
os.makedirs("data", exist_ok=True)

# Set up basic logging (this is separate from our interaction logging)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/fenrir.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class LoggingBot(commands.Bot):
    """Enhanced bot with comprehensive interaction logging"""

    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        intents.members = True  # Required for member join/leave events

        super().__init__(
            command_prefix=BotConfig.PREFIX,
            intents=intents,
            help_command=None  # We'll create our own
        )

        # Store configuration
        self.config = BotConfig

        # Initialize bot interaction logger
        self.bot_logger = init_bot_logger("Fenrir", BotConfig.LOG_LEVEL)

        # Track command execution times
        self.command_start_times = {}

    async def setup_hook(self):
        """Called when the bot is starting up"""
        logger.info("🐺 Fenrir is awakening...")

        # CHANGE: Add comprehensive startup validation
        try:
            # Validate bot permissions and configuration
            await self._validate_startup_requirements()

            # Initialize database if logging is enabled
            if self.config.MODULES_ENABLED.get('logging', False):
                from utils.database import init_database
                await init_database(self.config.DATABASE_PATH)
                logger.info("Database initialized")

            # Load all cogs
            await self.load_cogs()

            # Sync commands only if needed (prevent rate limiting)
            if not os.path.exists('.command_sync_done') or self.config.AUTO_SYNC_COMMANDS:
                try:
                    synced = await self.tree.sync()
                    logger.info(f"Synced slash commands: {len(synced)} commands")
                    # Mark sync as completed
                    with open('.command_sync_done', 'w') as f:
                        f.write(str(datetime.now()))
                except discord.HTTPException as e:
                    if e.status == 429:  # Rate limited
                        logger.warning("Command sync rate limited, skipping this startup")
                    else:
                        logger.error(f"Failed to sync commands: {e}")
            else:
                logger.info("Skipping command sync (already done recently)")

        except Exception as e:
            logger.error(f"Critical error during bot setup: {e}")
            raise

    async def _validate_startup_requirements(self):
        """Validate bot startup requirements"""
        # CHANGE: Add startup validation method
        logger.info("Validating startup requirements...")

        # Check if bot has basic permissions
        if not self.user:
            raise RuntimeError("Bot user not available during startup")

        # Validate file permissions
        required_dirs = ['logs', 'data']
        for dir_name in required_dirs:
            try:
                os.makedirs(dir_name, exist_ok=True)
                # Test write permissions
                test_file = os.path.join(dir_name, '.write_test')
                with open(test_file, 'w') as f:
                    f.write('test')
                os.remove(test_file)
            except Exception as e:
                raise RuntimeError(f"Cannot write to {dir_name} directory: {e}")

        logger.info("✅ Startup requirements validated")

    async def load_cogs(self):
        """Load all cog files"""
        # Always load core cogs
        core_cogs = ["cogs.core", "cogs.admin", "cogs.utility"]

        # Optional cogs based on configuration
        if self.config.MODULES_ENABLED.get('logging', False):
            core_cogs.append("cogs.logging")  # This now loads the modular system

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

        # Log bot startup with interaction logger
        self.bot_logger.log_bot_startup(self)

        # Log enabled modules
        enabled_modules = [name for name, enabled in self.config.MODULES_ENABLED.items() if enabled]
        if enabled_modules:
            logger.info(f'✅ Enabled modules: {", ".join(enabled_modules)}')
            log_event("bot_modules_loaded", {"enabled_modules": enabled_modules})
        else:
            logger.info('📝 No optional modules enabled')

    async def on_command_error(self, ctx, error):
        """Handle command errors"""
        if isinstance(error, commands.CommandNotFound):
            return  # Ignore unknown commands

        logger.error(f"Command error: {error}")
        log_error(error, f"Command error in {ctx.command}", getattr(ctx, 'interaction', None))

    # ==================== ENHANCED EVENT LOGGING ====================

    async def on_interaction(self, interaction: discord.Interaction):
        """Log all interactions and track command timing"""
        # Record start time for commands
        if interaction.type == discord.InteractionType.application_command:
            self.command_start_times[interaction.id] = time.time()

        # Log the interaction
        interaction_data = {
            'type': str(interaction.type),
            'user': f"{interaction.user} ({interaction.user.id})",
            'guild': f"{interaction.guild.name} ({interaction.guild.id})" if interaction.guild else "DM",
            'channel': str(interaction.channel) if interaction.channel else "Unknown"
        }

        if hasattr(interaction, 'command') and interaction.command:
            interaction_data['command'] = interaction.command.name

        log_event("interaction_received", interaction_data)

        # Process the interaction
        await super().on_interaction(interaction)

    async def on_application_command_completion(self, interaction: discord.Interaction, command):
        """Log completed application commands with execution time"""
        # Calculate execution time
        execution_time = None
        if interaction.id in self.command_start_times:
            execution_time = time.time() - self.command_start_times[interaction.id]
            del self.command_start_times[interaction.id]

        # Get command arguments if available
        args = {}
        if hasattr(interaction, 'data') and 'options' in interaction.data:
            for option in interaction.data['options']:
                args[option['name']] = option['value']

        # Log the command execution
        log_command(interaction, command.name, args, execution_time)

    async def on_message(self, message):
        """Log message events"""
        # Skip bot messages for basic logging (unless it's our own bot for API tracking)
        if message.author.bot and message.author != self.user:
            return

        # Log message data
        message_data = {
            'author': f"{message.author} ({message.author.id})",
            'guild': f"{message.guild.name} ({message.guild.id})" if message.guild else "DM",
            'channel': str(message.channel),
            'content_length': len(message.content) if message.content else 0,
            'attachments': len(message.attachments),
            'embeds': len(message.embeds)
        }

        # Only log non-bot messages or our own bot's messages
        if message.author == self.user:
            log_message(message, "sent_by_bot", f"Content: {message.content[:100]}...")
        else:
            log_event("message_received", message_data)

    async def on_message_delete(self, message):
        """Log message deletions"""
        if message.author.bot:
            return

        log_message(message, "deleted", f"Content was: {message.content[:100]}...")

    async def on_message_edit(self, before, after):
        """Log message edits"""
        if before.author.bot or before.content == after.content:
            return

        log_message(before, "edited", f"Before: {before.content[:50]}... | After: {after.content[:50]}...")

    async def on_member_join(self, member):
        """Log member joins"""
        member_data = {
            'account_age_days': (member.joined_at - member.created_at).days if member.joined_at else None,
            'guild_member_count': member.guild.member_count
        }
        log_member(member, "join", member_data)

    async def on_member_remove(self, member):
        """Log member leaves"""
        member_data = {
            'roles': [role.name for role in member.roles[1:]],  # Skip @everyone
            'guild_member_count': member.guild.member_count
        }
        log_member(member, "leave", member_data)

    async def on_member_ban(self, guild, user):
        """Log member bans"""
        log_event("member_banned", {
            'user': f"{user} ({user.id})",
            'guild': f"{guild.name} ({guild.id})"
        })

    async def on_member_unban(self, guild, user):
        """Log member unbans"""
        log_event("member_unbanned", {
            'user': f"{user} ({user.id})",
            'guild': f"{guild.name} ({guild.id})"
        })

    async def on_guild_join(self, guild):
        """Log when bot joins a guild"""
        guild_data = {
            'member_count': guild.member_count,
            'owner': f"{guild.owner} ({guild.owner.id})" if guild.owner else "Unknown",
            'features': guild.features,
            'verification_level': str(guild.verification_level)
        }
        log_guild(guild, "join", guild_data)

    async def on_guild_remove(self, guild):
        """Log when bot leaves a guild"""
        guild_data = {
            'member_count': guild.member_count
        }
        log_guild(guild, "leave", guild_data)

    async def on_error(self, event, *args, **kwargs):
        """Log uncaught errors"""
        logger.error(f"Uncaught error in {event}")
        import traceback
        traceback.print_exc()

        # Log with our system
        log_event("uncaught_error", {
            'event': event,
            'args': str(args)[:500],
            'kwargs': str(kwargs)[:500]
        })

    async def close(self):
        """Log session stats before closing"""
        if self.bot_logger:
            self.bot_logger.log_session_stats()

        logger.info("🛑 Fenrir is going to sleep...")
        await super().close()


# Bot instance
bot = LoggingBot()


async def main():
    """Main function to run the bot"""
    try:
        await bot.start(BotConfig.DISCORD_TOKEN)
    except KeyboardInterrupt:
        logger.info("🛑 Bot stopped by user")
        get_bot_logger().interaction_logger.info("🛑 Bot stopped by user (KeyboardInterrupt)")
    except Exception as e:
        logger.error(f"❌ Bot crashed: {e}")
        log_error(e, "Bot crash in main()")
    finally:
        await bot.close()


if __name__ == "__main__":
    asyncio.run(main())