"""
Smart Routing Base Logging Infrastructure - cogs/logging/base.py
Enhanced shared functionality with flexible event-to-channel routing
"""

import discord
from discord.ext import commands
import logging
from datetime import datetime
from typing import Optional, Dict, Any

from utils.database import (
    get_guild_config, is_logging_enabled, is_event_enabled,
    get_event_channel, get_all_event_channels
)

logger = logging.getLogger(__name__)


class BaseLogger:
    """Enhanced base class with smart channel routing for all logging modules"""

    def __init__(self, bot):
        self.bot = bot

        # File type categorization
        self.file_types = {
            'images': {'.png', '.jpg', '.jpeg', '.gif', '.webp', '.bmp', '.svg', '.tiff', '.ico'},
            'documents': {'.pdf', '.doc', '.docx', '.txt', '.rtf', '.odt', '.xls', '.xlsx', '.ppt', '.pptx'},
            'videos': {'.mp4', '.avi', '.mov', '.wmv', '.flv', '.webm', '.mkv', '.m4v'},
            'audio': {'.mp3', '.wav', '.flac', '.aac', '.ogg', '.wma', '.m4a'},
            'archives': {'.zip', '.rar', '.7z', '.tar', '.gz', '.bz2'},
            'code': {'.py', '.js', '.html', '.css', '.java', '.cpp', '.c', '.php', '.rb', '.go'}
        }

    def get_file_type_emoji(self, filename: str) -> str:
        """Get appropriate emoji for file type"""
        filename_lower = filename.lower()

        if any(filename_lower.endswith(ext) for ext in self.file_types['images']):
            return "🖼️"
        elif any(filename_lower.endswith(ext) for ext in self.file_types['documents']):
            return "📄"
        elif any(filename_lower.endswith(ext) for ext in self.file_types['videos']):
            return "🎥"
        elif any(filename_lower.endswith(ext) for ext in self.file_types['audio']):
            return "🎵"
        elif any(filename_lower.endswith(ext) for ext in self.file_types['archives']):
            return "📦"
        elif any(filename_lower.endswith(ext) for ext in self.file_types['code']):
            return "💻"
        else:
            return "📎"

    def is_image_file(self, filename: str) -> bool:
        """Check if a file is an image based on extension"""
        return any(filename.lower().endswith(ext) for ext in self.file_types['images'])

    def categorize_file(self, filename: str) -> str:
        """Categorize file by extension"""
        filename_lower = filename.lower()
        for category, extensions in self.file_types.items():
            if any(filename_lower.endswith(ext) for ext in extensions):
                return category
        return 'other'

    async def get_log_channel(self, guild: discord.Guild, event_type: str) -> Optional[discord.TextChannel]:
        """
        Enhanced channel resolution with validation and cleanup
        """
        guild_id = str(guild.id)

        try:
            # Level 1: Try to get event-specific channel
            event_channel_id = await get_event_channel(guild_id, event_type)
            if event_channel_id:
                event_channel = guild.get_channel(int(event_channel_id))
                if event_channel and isinstance(event_channel, discord.TextChannel):
                    # CHANGE: Add permission validation
                    bot_perms = event_channel.permissions_for(guild.me)
                    if bot_perms.send_messages and bot_perms.embed_links:
                        logger.debug(f"Using event-specific channel {event_channel.name} for {event_type}")
                        return event_channel
                    else:
                        logger.warning(f"Missing permissions in event channel {event_channel.name}")
                        # Clean up invalid mapping
                        try:
                            from utils.database import remove_event_channel
                            await remove_event_channel(guild_id, event_type)
                        except Exception as cleanup_error:
                            logger.error(f"Failed to cleanup invalid channel mapping: {cleanup_error}")
                else:
                    logger.warning(f"Event-specific channel {event_channel_id} not found for {event_type}")
                    # Clean up stale mapping
                    try:
                        from utils.database import remove_event_channel
                        await remove_event_channel(guild_id, event_type)
                    except Exception as cleanup_error:
                        logger.error(f"Failed to cleanup stale channel mapping: {cleanup_error}")

            # Level 2: Fall back to default guild log channel with validation
            config = await get_guild_config(guild_id)
            if config and config.get('log_channel_id'):
                default_channel = guild.get_channel(int(config['log_channel_id']))
                if default_channel and isinstance(default_channel, discord.TextChannel):
                    # CHANGE: Add permission validation for default channel too
                    bot_perms = default_channel.permissions_for(guild.me)
                    if bot_perms.send_messages and bot_perms.embed_links:
                        logger.debug(f"Using default log channel {default_channel.name} for {event_type}")
                        return default_channel
                    else:
                        logger.warning(f"Missing permissions in default log channel {default_channel.name}")
                else:
                    logger.warning(f"Default log channel {config['log_channel_id']} not found")

            # Level 3: No valid channels configured
            logger.warning(f"No valid log channel configured for {event_type} in guild {guild.name}")
            return None

        except Exception as e:
            logger.error(f"Error resolving log channel for {event_type}: {e}")
            return None

    async def send_log(self, guild: discord.Guild, event_type: str, embed: discord.Embed):
        """Enhanced send log with smart channel routing"""
        try:
            # Get the appropriate channel for this event type
            log_channel = await self.get_log_channel(guild, event_type)
            if not log_channel:
                logger.warning(f"No log channel available for {event_type} in guild {guild.name}")
                return

            guild_id = str(guild.id)
            config = await get_guild_config(guild_id)

            # Apply guild-specific styling
            if config and config.get('embed_color'):
                try:
                    embed.color = discord.Color(int(config['embed_color'].replace('#', ''), 16))
                except:
                    pass  # Keep default color if invalid

            # Add timestamp if enabled
            if config and config.get('show_timestamps', True):
                embed.timestamp = datetime.utcnow()

            # Send the log message
            await log_channel.send(embed=embed)

            logger.debug(f"Sent {event_type} log to {log_channel.name} in {guild.name}")

        except discord.Forbidden:
            logger.error(f"Missing permissions to send log to channel in guild {guild.name}")
        except discord.HTTPException as e:
            logger.error(f"HTTP error sending log message: {e}")
        except Exception as e:
            logger.error(f"Unexpected error sending log message: {e}")

    async def check_logging_enabled(self, guild_id: str, event_type: str) -> bool:
        """Check if logging is enabled for guild and specific event type"""
        try:
            # Check if general logging is enabled
            if not await is_logging_enabled(guild_id):
                logger.debug(f"Logging disabled for guild {guild_id}")
                return False

            # Check if specific event logging is enabled
            if not await is_event_enabled(guild_id, event_type):
                logger.debug(f"Event {event_type} disabled for guild {guild_id}")
                return False

            return True

        except Exception as e:
            logger.error(f"Error checking logging enabled for {event_type}: {e}")
            return False

    def create_base_embed(self, title: str, color: discord.Color, guild: discord.Guild) -> discord.Embed:
        """Create a base embed with consistent styling"""
        embed = discord.Embed(title=title, color=color)
        return embed

    def add_user_info(self, embed: discord.Embed, user: discord.User, field_name: str = "User"):
        """Add user information to embed"""
        embed.add_field(
            name=field_name,
            value=f"{user.mention} ({user})",
            inline=True
        )

    def add_guild_avatar(self, embed: discord.Embed, user: discord.User, guild_id: str):
        """Add user avatar to embed if enabled in guild settings"""

        async def _add_avatar():
            try:
                config = await get_guild_config(guild_id)
                if config and config.get('show_avatars', True) and user.avatar:
                    embed.set_thumbnail(url=user.avatar.url)
            except Exception as e:
                logger.debug(f"Error adding avatar: {e}")

        # This is a sync method, so we'll handle avatar addition in the calling async method
        return _add_avatar

    def format_content(self, content: str, max_length: int = 1000) -> str:
        """Format content for embed with length limits"""
        if not content:
            return "*(No content)*"

        if len(content) > max_length:
            return content[:max_length] + "..."
        return content

    def create_jump_link_field(self, embed: discord.Embed, message: discord.Message):
        """Add jump link field to embed"""
        embed.add_field(
            name="Jump to Message",
            value=f"[Click here]({message.jump_url})",
            inline=True
        )

    async def get_routing_info(self, guild_id: str) -> Dict[str, Any]:
        """Get comprehensive routing information for debugging"""
        try:
            config = await get_guild_config(guild_id)
            event_channels = await get_all_event_channels(guild_id)

            routing_info = {
                'guild_id': guild_id,
                'logging_enabled': config.get('logging_enabled', False) if config else False,
                'default_channel': config.get('log_channel_id') if config else None,
                'event_specific_channels': len(event_channels),
                'event_mappings': event_channels,
                'has_fallback': bool(config and config.get('log_channel_id'))
            }

            return routing_info

        except Exception as e:
            logger.error(f"Error getting routing info: {e}")
            return {}

    async def test_channel_routing(self, guild: discord.Guild, event_type: str) -> Dict[str, Any]:
        """Test channel routing for a specific event type (for debugging)"""
        guild_id = str(guild.id)

        test_result = {
            'event_type': event_type,
            'guild_id': guild_id,
            'logging_enabled': await is_logging_enabled(guild_id),
            'event_enabled': await is_event_enabled(guild_id, event_type),
            'resolved_channel': None,
            'resolution_path': [],
            'success': False
        }

        try:
            # Test the resolution path

            # Check event-specific channel
            event_channel_id = await get_event_channel(guild_id, event_type)
            if event_channel_id:
                test_result['resolution_path'].append(f"Found event-specific channel: {event_channel_id}")
                event_channel = guild.get_channel(int(event_channel_id))
                if event_channel:
                    test_result['resolved_channel'] = {
                        'id': event_channel.id,
                        'name': event_channel.name,
                        'type': 'event_specific'
                    }
                    test_result['success'] = True
                    test_result['resolution_path'].append("✅ Event-specific channel found and accessible")
                    return test_result
                else:
                    test_result['resolution_path'].append("❌ Event-specific channel not accessible")

            # Check default channel
            config = await get_guild_config(guild_id)
            if config and config.get('log_channel_id'):
                test_result['resolution_path'].append(f"Checking default channel: {config['log_channel_id']}")
                default_channel = guild.get_channel(int(config['log_channel_id']))
                if default_channel:
                    test_result['resolved_channel'] = {
                        'id': default_channel.id,
                        'name': default_channel.name,
                        'type': 'default'
                    }
                    test_result['success'] = True
                    test_result['resolution_path'].append("✅ Default channel found and accessible")
                    return test_result
                else:
                    test_result['resolution_path'].append("❌ Default channel not accessible")

            test_result['resolution_path'].append("❌ No channels configured or accessible")

        except Exception as e:
            test_result['resolution_path'].append(f"❌ Error during resolution: {str(e)}")
            logger.error(f"Error testing channel routing: {e}")

        return test_result


class LoggingModule:
    """Enhanced base class for logging modules with smart routing"""

    def __init__(self, bot):
        self.bot = bot
        self.base = BaseLogger(bot)

    def cog_check(self, ctx):
        """Check if logging module is enabled"""
        return self.bot.config.MODULES_ENABLED.get('logging', False)

    async def setup(self):
        """Setup method called when module is loaded"""
        pass

    async def teardown(self):
        """Teardown method called when module is unloaded"""
        pass

    async def get_routing_debug_info(self, guild_id: str) -> str:
        """Get formatted routing debug information"""
        routing_info = await self.base.get_routing_info(guild_id)

        debug_lines = [
            f"🔍 **Routing Debug for Guild {guild_id}**",
            f"📊 Logging Enabled: {'✅' if routing_info.get('logging_enabled') else '❌'}",
            f"📍 Default Channel: {routing_info.get('default_channel', 'None')}",
            f"🎯 Event-Specific Channels: {routing_info.get('event_specific_channels', 0)}",
            f"🔄 Has Fallback: {'✅' if routing_info.get('has_fallback') else '❌'}"
        ]

        if routing_info.get('event_mappings'):
            debug_lines.append("\n📋 **Event Mappings:**")
            for event, channel_id in routing_info['event_mappings'].items():
                debug_lines.append(f"  • {event} → {channel_id}")

        return "\n".join(debug_lines)