"""
Member Logging Module - cogs/logging/member_logs.py
Handles member join/leave/ban/unban events
"""

import discord
from discord.ext import commands
import logging
from datetime import datetime

from .base import LoggingModule
from utils.bot_logger import log_member, log_event

logger = logging.getLogger(__name__)


class MemberLogs(LoggingModule):
    """Handles member-related logging events"""

    def __init__(self, bot):
        super().__init__(bot)

        # Define event types this module handles
        self.event_types = {
            'member_join': 'Member Joins',
            'member_leave': 'Member Leaves',
            'member_ban': 'Member Bans',
            'member_unban': 'Member Unbans'
        }

    async def setup(self):
        """Setup method called when module is loaded"""
        logger.info("Member logging module initialized")

    async def on_member_join(self, member):
        """Log member joins"""
        guild_id = str(member.guild.id)

        # Check if logging is enabled for this event
        if not await self.base.check_logging_enabled(guild_id, 'member_join'):
            return

        logger.info(f"👋 Processing member join: {member} in {member.guild.name}")

        # Create embed for member join
        embed = discord.Embed(
            title="👋 Member Joined",
            color=discord.Color.green()
        )

        # Add member information
        self.base.add_user_info(embed, member, "Member")

        # Add account creation info
        account_age = datetime.utcnow() - member.created_at
        embed.add_field(
            name="Account Created",
            value=f"<t:{int(member.created_at.timestamp())}:R>\n({account_age.days} days ago)",
            inline=True
        )

        # Add member count
        embed.add_field(
            name="Member Count",
            value=f"#{member.guild.member_count:,}",
            inline=True
        )

        # Add join timestamp
        embed.add_field(
            name="🕒 Joined At",
            value=f"<t:{int(datetime.utcnow().timestamp())}:F>",
            inline=True
        )

        # Check for potential spam accounts (very new accounts)
        if account_age.days < 7:
            embed.add_field(
                name="⚠️ Notice",
                value=f"Account is only {account_age.days} days old",
                inline=False
            )

        # Add user ID for easy copying
        embed.add_field(
            name="User ID",
            value=f"`{member.id}`",
            inline=True
        )

        # Add avatar if enabled
        add_avatar = self.base.add_guild_avatar(embed, member, guild_id)
        await add_avatar()

        # Send log
        await self.base.send_log(member.guild, 'member_join', embed)

        # Log to interaction logger
        log_member(member, "join", {
            'account_age_days': account_age.days,
            'guild_member_count': member.guild.member_count,
            'is_new_account': account_age.days < 7
        })

    async def on_member_remove(self, member):
        """Log member leaves"""
        guild_id = str(member.guild.id)

        # Check if logging is enabled for this event
        if not await self.base.check_logging_enabled(guild_id, 'member_leave'):
            return

        logger.info(f"👋 Processing member leave: {member} from {member.guild.name}")

        # Create embed for member leave
        embed = discord.Embed(
            title="👋 Member Left",
            color=discord.Color.red()
        )

        # Add member information (use string since member might be partial)
        embed.add_field(
            name="Member",
            value=f"{member} (ID: {member.id})",
            inline=True
        )

        # Add join date if available
        if member.joined_at:
            time_in_server = datetime.utcnow() - member.joined_at
            embed.add_field(
                name="Joined",
                value=f"<t:{int(member.joined_at.timestamp())}:R>\n({time_in_server.days} days ago)",
                inline=True
            )
        else:
            embed.add_field(
                name="Joined",
                value="Unknown",
                inline=True
            )

        # Add member count
        embed.add_field(
            name="Member Count",
            value=f"#{member.guild.member_count:,}",
            inline=True
        )

        # Add leave timestamp
        embed.add_field(
            name="🕒 Left At",
            value=f"<t:{int(datetime.utcnow().timestamp())}:F>",
            inline=True
        )

        # Add roles if member had any (excluding @everyone)
        if hasattr(member, 'roles') and len(member.roles) > 1:
            roles = [role.name for role in member.roles[1:]]  # Skip @everyone
            if len(roles) <= 5:
                roles_text = ", ".join(roles)
            else:
                roles_text = ", ".join(roles[:5]) + f" and {len(roles) - 5} more"

            embed.add_field(
                name="Had Roles",
                value=roles_text,
                inline=False
            )

        # Add user ID for easy copying
        embed.add_field(
            name="User ID",
            value=f"`{member.id}`",
            inline=True
        )

        # Add avatar if enabled
        add_avatar = self.base.add_guild_avatar(embed, member, guild_id)
        await add_avatar()

        # Send log
        await self.base.send_log(member.guild, 'member_leave', embed)

        # Log to interaction logger
        log_member(member, "leave", {
            'roles': [role.name for role in member.roles[1:]] if hasattr(member, 'roles') else [],
            'guild_member_count': member.guild.member_count,
            'time_in_server_days': (datetime.utcnow() - member.joined_at).days if member.joined_at else None
        })

    async def on_member_ban(self, guild, user):
        """Log member bans"""
        guild_id = str(guild.id)

        # Check if logging is enabled for this event
        if not await self.base.check_logging_enabled(guild_id, 'member_ban'):
            return

        logger.info(f"🔨 Processing member ban: {user} from {guild.name}")

        # Create embed for member ban
        embed = discord.Embed(
            title="🔨 Member Banned",
            color=discord.Color.dark_red()
        )

        # Add user information
        embed.add_field(
            name="Member",
            value=f"{user} (ID: {user.id})",
            inline=True
        )

        # Add ban timestamp
        embed.add_field(
            name="🕒 Banned At",
            value=f"<t:{int(datetime.utcnow().timestamp())}:F>",
            inline=True
        )

        # Try to get ban reason from audit logs
        try:
            async for entry in guild.audit_logs(action=discord.AuditLogAction.ban, limit=10):
                if entry.target.id == user.id:
                    embed.add_field(
                        name="Banned By",
                        value=f"{entry.user.mention} ({entry.user})",
                        inline=True
                    )
                    if entry.reason:
                        embed.add_field(
                            name="Reason",
                            value=entry.reason,
                            inline=False
                        )
                    break
        except discord.Forbidden:
            # Bot doesn't have permission to view audit logs
            pass

        # Add user ID for easy copying
        embed.add_field(
            name="User ID",
            value=f"`{user.id}`",
            inline=True
        )

        # Add avatar if enabled
        add_avatar = self.base.add_guild_avatar(embed, user, guild_id)
        await add_avatar()

        # Send log
        await self.base.send_log(guild, 'member_ban', embed)

        # Log to interaction logger
        log_event("member_banned", {
            'user': f"{user} ({user.id})",
            'guild': f"{guild.name} ({guild.id})",
            'timestamp': datetime.utcnow().isoformat()
        })

    async def on_member_unban(self, guild, user):
        """Log member unbans"""
        guild_id = str(guild.id)

        # Check if logging is enabled for this event
        if not await self.base.check_logging_enabled(guild_id, 'member_unban'):
            return

        logger.info(f"🔓 Processing member unban: {user} from {guild.name}")

        # Create embed for member unban
        embed = discord.Embed(
            title="🔓 Member Unbanned",
            color=discord.Color.green()
        )

        # Add user information
        embed.add_field(
            name="Member",
            value=f"{user} (ID: {user.id})",
            inline=True
        )

        # Add unban timestamp
        embed.add_field(
            name="🕒 Unbanned At",
            value=f"<t:{int(datetime.utcnow().timestamp())}:F>",
            inline=True
        )

        # Try to get unban moderator from audit logs
        try:
            async for entry in guild.audit_logs(action=discord.AuditLogAction.unban, limit=10):
                if entry.target.id == user.id:
                    embed.add_field(
                        name="Unbanned By",
                        value=f"{entry.user.mention} ({entry.user})",
                        inline=True
                    )
                    if entry.reason:
                        embed.add_field(
                            name="Reason",
                            value=entry.reason,
                            inline=False
                        )
                    break
        except discord.Forbidden:
            # Bot doesn't have permission to view audit logs
            pass

        # Add user ID for easy copying
        embed.add_field(
            name="User ID",
            value=f"`{user.id}`",
            inline=True
        )

        # Add avatar if enabled
        add_avatar = self.base.add_guild_avatar(embed, user, guild_id)
        await add_avatar()

        # Send log
        await self.base.send_log(guild, 'member_unban', embed)

        # Log to interaction logger
        log_event("member_unbanned", {
            'user': f"{user} ({user.id})",
            'guild': f"{guild.name} ({guild.id})",
            'timestamp': datetime.utcnow().isoformat()
        })

    async def get_member_statistics(self, guild_id: str, days: int = 7):
        """Get member join/leave statistics for a guild"""
        # This method can be expanded when we add analytics in future weeks
        stats = {
            'joins_tracked': 0,
            'leaves_tracked': 0,
            'bans_tracked': 0,
            'unbans_tracked': 0,
            'period_days': days
        }

        # TODO: Query database for actual statistics
        # This will be implemented when we add the analytics features

        return stats