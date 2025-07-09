"""
Message Logging Module - cogs/logging/message_logs.py
Handles message deletion and editing events
"""

import discord
from discord.ext import commands
import logging
from datetime import datetime

from .base import LoggingModule
from utils.bot_logger import log_message, log_event

logger = logging.getLogger(__name__)


class MessageLogs(LoggingModule):
    """Handles message-related logging events"""

    def __init__(self, bot):
        super().__init__(bot)

        # Define event types this module handles
        self.event_types = {
            'message_delete': 'Message Deletions',
            'message_edit': 'Message Edits'
        }

    async def setup(self):
        """Setup method called when module is loaded"""
        logger.info("Message logging module initialized")

    async def on_message_delete(self, message):
        """Log message deletions (text only, no attachments)"""
        # Skip bot messages
        if message.author.bot:
            return

        # Skip if no guild (DMs, etc.)
        if not message.guild:
            return

        # Skip if message has attachments (handled by attachment_logs)
        if message.attachments:
            return

        guild_id = str(message.guild.id)

        # Check if logging is enabled for this event
        if not await self.base.check_logging_enabled(guild_id, 'message_delete'):
            return

        logger.info(f"🗑️ Processing text message deletion in {message.guild.name}")

        # Create embed for deleted message
        embed = discord.Embed(
            title="🗑️ Message Deleted",
            color=discord.Color.red()
        )

        # Add user information
        self.base.add_user_info(embed, message.author, "Author")

        # Add channel information
        embed.add_field(
            name="Channel",
            value=message.channel.mention,
            inline=True
        )

        # Add message ID
        embed.add_field(
            name="Message ID",
            value=str(message.id),
            inline=True
        )

        # Add message content if any
        if message.content:
            content = self.base.format_content(message.content, 1000)
            embed.add_field(
                name="Content",
                value=f"```{content}```",
                inline=False
            )
        else:
            embed.add_field(
                name="Content",
                value="*(No text content)*",
                inline=False
            )

        # Add deletion timestamp
        embed.add_field(
            name="🕒 Deleted At",
            value=f"<t:{int(datetime.utcnow().timestamp())}:F>",
            inline=True
        )

        # Add avatar if enabled
        add_avatar = self.base.add_guild_avatar(embed, message.author, guild_id)
        await add_avatar()

        # Send log
        await self.base.send_log(message.guild, 'message_delete', embed)

        # Log to interaction logger
        log_message(message, "deleted", f"Content: {message.content[:50]}..." if message.content else "No content")

    async def on_message_edit(self, before, after):
        """Log message edits"""
        # Skip bot messages
        if before.author.bot:
            return

        # Skip if no guild (DMs, interaction responses, etc.)
        if not before.guild:
            return

        # Skip if content didn't actually change
        if before.content == after.content:
            return

        guild_id = str(before.guild.id)

        # Check if logging is enabled for this event
        if not await self.base.check_logging_enabled(guild_id, 'message_edit'):
            return

        logger.info(f"📝 Processing message edit in {before.guild.name}")

        # Create embed for edited message
        embed = discord.Embed(
            title="📝 Message Edited",
            color=discord.Color.orange()
        )

        # Add user information
        self.base.add_user_info(embed, before.author, "Author")

        # Add channel information
        embed.add_field(
            name="Channel",
            value=before.channel.mention,
            inline=True
        )

        # Add jump link
        self.base.create_jump_link_field(embed, after)

        # Before content
        if before.content:
            before_content = self.base.format_content(before.content, 500)
            embed.add_field(
                name="Before",
                value=f"```{before_content}```",
                inline=False
            )
        else:
            embed.add_field(
                name="Before",
                value="*(No text content)*",
                inline=False
            )

        # After content
        if after.content:
            after_content = self.base.format_content(after.content, 500)
            embed.add_field(
                name="After",
                value=f"```{after_content}```",
                inline=False
            )
        else:
            embed.add_field(
                name="After",
                value="*(No text content)*",
                inline=False
            )

        # Add edit timestamp
        embed.add_field(
            name="🕒 Edited At",
            value=f"<t:{int(datetime.utcnow().timestamp())}:F>",
            inline=True
        )

        # Show character count change
        before_len = len(before.content) if before.content else 0
        after_len = len(after.content) if after.content else 0
        length_change = after_len - before_len

        if length_change != 0:
            change_text = f"+{length_change}" if length_change > 0 else str(length_change)
            embed.add_field(
                name="📊 Length Change",
                value=f"{before_len} → {after_len} ({change_text} chars)",
                inline=True
            )

        # Add avatar if enabled
        add_avatar = self.base.add_guild_avatar(embed, before.author, guild_id)
        await add_avatar()

        # Send log
        await self.base.send_log(before.guild, 'message_edit', embed)

        # Log to interaction logger
        log_message(before, "edited", f"Before: {before.content[:50]}... | After: {after.content[:50]}...")

        # Log edit event details
        log_event("message_edited", {
            'guild_id': str(before.guild.id),
            'channel_id': str(before.channel.id),
            'message_id': str(before.id),
            'author_id': str(before.author.id),
            'before_length': before_len,
            'after_length': after_len,
            'length_change': length_change
        })

    async def get_message_statistics(self, guild_id: str, days: int = 7):
        """Get message deletion/edit statistics for a guild"""
        # This method can be expanded when we add analytics in future weeks
        stats = {
            'deletes_tracked': 0,
            'edits_tracked': 0,
            'period_days': days
        }

        # TODO: Query database for actual statistics
        # This will be implemented when we add the analytics features

        return stats