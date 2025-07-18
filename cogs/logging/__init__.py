"""
Enhanced Logging Module Coordinator - cogs/logging/__init__.py
Coordinates all logging modules with flexible event-to-channel routing
"""

import discord
from discord.ext import commands
import logging
from typing import List, Dict, Any
import time

# Import all logging modules
from .message_logs import MessageLogs
from .member_logs import MemberLogs
from .attachment_logs import AttachmentLogs
from .admin_commands import LoggingAdmin
from .voice_logs import VoiceLogs
from datetime import timedelta

logger = logging.getLogger(__name__)

class ConfigurableLogging(commands.Cog):
    """Enhanced main logging cog with flexible event-to-channel routing"""

    def __init__(self, bot):
        self.bot = bot
        self.modules = []

        # FIXED: Proper event loop prevention
        self._processed_messages = set()
        self._last_cleanup = time.time()

        # Initialize all logging modules
        self.message_logs = MessageLogs(bot)
        self.member_logs = MemberLogs(bot)
        self.attachment_logs = AttachmentLogs(bot)
        self.admin_commands = LoggingAdmin(bot)
        self.voice_logs = VoiceLogs(bot)

        # Register modules for coordination
        self.modules = [
            self.message_logs,
            self.member_logs,
            self.attachment_logs,
            self.admin_commands,
            self.voice_logs
        ]

        logger.info("Initialized enhanced logging system with {} modules".format(len(self.modules)))

    def cog_check(self, ctx):
        """Check if logging module is enabled"""
        return self.bot.config.MODULES_ENABLED.get('logging', False)

    async def cog_load(self):
        """Called when the cog is loaded"""
        logger.info("Loading enhanced modular logging system...")

        # Setup all modules
        for module in self.modules:
            if hasattr(module, 'setup'):
                await module.setup()
                logger.debug(f"Setup module: {module.__class__.__name__}")

        logger.info("✅ Enhanced modular logging system loaded successfully")

    async def cog_unload(self):
        """Called when the cog is unloaded"""
        logger.info("Unloading enhanced modular logging system...")

        # Teardown all modules
        for module in self.modules:
            if hasattr(module, 'teardown'):
                await module.teardown()
                logger.debug(f"Teardown module: {module.__class__.__name__}")

    # ==================== EVENT FORWARDING ====================
    # Forward Discord events to appropriate modules

    @commands.Cog.listener()
    async def on_message(self, message):
        """Forward message events to attachment logger"""
        await self.attachment_logs.on_message(message)

    @commands.Cog.listener()
    async def on_message_delete(self, message):
        """Forward message delete events with proper loop prevention"""
        # FIXED: Simple cleanup every 5 minutes
        current_time = time.time()
        if current_time - self._last_cleanup > 300:  # 5 minutes
            self._processed_messages.clear()
            self._last_cleanup = current_time

        # FIXED: Proper loop prevention
        if message.id in self._processed_messages:
            return
        self._processed_messages.add(message.id)

        try:
            if message.attachments:
                await self.attachment_logs.on_message_delete(message)
            else:
                await self.message_logs.on_message_delete(message)
        except Exception as e:
            logger.error(f"Error in message delete forwarding: {e}")

    @commands.Cog.listener()
    async def on_message_edit(self, before, after):
        """Forward message edit events to message logger"""
        # CHANGE: Add loop prevention
        if hasattr(before, '_fenrir_forwarded'):
            return

        before._fenrir_forwarded = True
        after._fenrir_forwarded = True

        try:
            await self.message_logs.on_message_edit(before, after)
        except Exception as e:
            logger.error(f"Error in message edit forwarding: {e}")
        finally:
            for msg in [before, after]:
                if hasattr(msg, '_fenrir_forwarded'):
                    delattr(msg, '_fenrir_forwarded')

    @commands.Cog.listener()
    async def on_member_join(self, member):
        """Forward member join events to member logger"""
        await self.member_logs.on_member_join(member)

    @commands.Cog.listener()
    async def on_member_remove(self, member):
        """Forward member remove events to member logger"""
        await self.member_logs.on_member_remove(member)

    @commands.Cog.listener()
    async def on_member_ban(self, guild, user):
        """Forward member ban events to member logger"""
        await self.member_logs.on_member_ban(guild, user)

    @commands.Cog.listener()
    async def on_member_unban(self, guild, user):
        """Forward member unban events to member logger"""
        await self.member_logs.on_member_unban(guild, user)

    # ==================== VOICE EVENT FORWARDING ====================

    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        """Forward voice state updates to voice logger"""
        await self.voice_logs.on_voice_state_update(member, before, after)

    # ==================== ENHANCED ADMIN COMMAND FORWARDING ====================
    # Forward admin commands to admin module with all new functionality

    @discord.app_commands.command(name="log_config", description="Configure basic logging for this server (Admin only)")
    @discord.app_commands.describe(
        channel="Channel to send logs to",
        enabled="Enable or disable logging"
    )
    async def log_config(self, interaction: discord.Interaction, channel: discord.TextChannel = None, enabled: bool = None):
        """Forward to admin commands module"""
        await self.admin_commands.log_config(interaction, channel, enabled)

    @discord.app_commands.command(name="log_events", description="Configure which events to log (Admin only)")
    @discord.app_commands.describe(
        event="Event type to configure",
        enabled="Enable or disable this event"
    )
    @discord.app_commands.choices(event=[
        discord.app_commands.Choice(name="Message Deletions", value="message_delete"),
        discord.app_commands.Choice(name="Message Edits", value="message_edit"),
        discord.app_commands.Choice(name="Image/File Uploads", value="image_send"),
        discord.app_commands.Choice(name="Image/File Deletions", value="image_delete"),
        discord.app_commands.Choice(name="Member Joins", value="member_join"),
        discord.app_commands.Choice(name="Member Leaves", value="member_leave"),
        discord.app_commands.Choice(name="Member Bans", value="member_ban"),
        discord.app_commands.Choice(name="Member Unbans", value="member_unban"),
        discord.app_commands.Choice(name="Voice Channel Joins", value="voice_join"),
        discord.app_commands.Choice(name="Voice Channel Leaves", value="voice_leave"),
        discord.app_commands.Choice(name="Voice Channel Moves", value="voice_move"),
        discord.app_commands.Choice(name="Voice Mute/Unmute", value="voice_mute"),
        discord.app_commands.Choice(name="Voice Deafen/Undeafen", value="voice_deafen"),
        discord.app_commands.Choice(name="Voice Streaming", value="voice_stream"),
        discord.app_commands.Choice(name="Voice Video/Camera", value="voice_video"),
    ])
    async def log_events(self, interaction: discord.Interaction, event: str, enabled: bool):
        """Forward to admin commands module"""
        await self.admin_commands.log_events(interaction, event, enabled)

    @discord.app_commands.command(name="log_status", description="View current logging configuration")
    async def log_status(self, interaction: discord.Interaction):
        """Forward to admin commands module"""
        await self.admin_commands.log_status(interaction)

    # ==================== NEW: ADVANCED SETUP COMMANDS ====================

    @discord.app_commands.command(name="log_setup_granular", description="🎯 Create individual channels for each event type (15+ channels)")
    async def log_setup_granular(self, interaction: discord.Interaction):
        """Set up granular logging with individual channels for each event"""
        await self.admin_commands.log_setup_granular(interaction)

    @discord.app_commands.command(name="log_setup_grouped", description="📋 Create grouped channels for related events (4-6 channels)")
    async def log_setup_grouped(self, interaction: discord.Interaction):
        """Set up grouped logging with channels for related event types"""
        await self.admin_commands.log_setup_grouped(interaction)

    # ==================== NEW: ADVANCED CONFIGURATION COMMANDS ====================

    @discord.app_commands.command(name="log_channel", description="🎯 Map a specific event to a specific channel")
    @discord.app_commands.describe(
        event="Event type to configure",
        channel="Channel to send this event's logs to"
    )
    @discord.app_commands.choices(event=[
        discord.app_commands.Choice(name="Message Deletions", value="message_delete"),
        discord.app_commands.Choice(name="Message Edits", value="message_edit"),
        discord.app_commands.Choice(name="Image/File Uploads", value="image_send"),
        discord.app_commands.Choice(name="Image/File Deletions", value="image_delete"),
        discord.app_commands.Choice(name="Member Joins", value="member_join"),
        discord.app_commands.Choice(name="Member Leaves", value="member_leave"),
        discord.app_commands.Choice(name="Member Bans", value="member_ban"),
        discord.app_commands.Choice(name="Member Unbans", value="member_unban"),
        discord.app_commands.Choice(name="Voice Channel Joins", value="voice_join"),
        discord.app_commands.Choice(name="Voice Channel Leaves", value="voice_leave"),
        discord.app_commands.Choice(name="Voice Channel Moves", value="voice_move"),
        discord.app_commands.Choice(name="Voice Mute/Unmute", value="voice_mute"),
        discord.app_commands.Choice(name="Voice Deafen/Undeafen", value="voice_deafen"),
        discord.app_commands.Choice(name="Voice Streaming", value="voice_stream"),
        discord.app_commands.Choice(name="Voice Video/Camera", value="voice_video"),
    ])
    async def log_channel(self, interaction: discord.Interaction, event: str, channel: discord.TextChannel):
        """Map a specific event to a specific channel"""
        await self.admin_commands.log_channel(interaction, event, channel)

    @discord.app_commands.command(name="log_group", description="📋 Map multiple events to one channel")
    @discord.app_commands.describe(
        events="Comma-separated list of event types (e.g., message_delete,message_edit)",
        channel="Channel to send these events' logs to"
    )
    async def log_group(self, interaction: discord.Interaction, events: str, channel: discord.TextChannel):
        """Map multiple events to a single channel"""
        await self.admin_commands.log_group(interaction, events, channel)

    # ==================== NEW: MANAGEMENT COMMANDS ====================

    @discord.app_commands.command(name="log_channels_list", description="📊 Show all current event-to-channel mappings")
    async def log_channels_list(self, interaction: discord.Interaction):
        """Display comprehensive channel mapping information"""
        await self.admin_commands.log_channels_list(interaction)

    @discord.app_commands.command(name="log_channels_test", description="🧪 Send test messages to all configured log channels")
    async def log_channels_test(self, interaction: discord.Interaction):
        """Send test messages to verify channel configuration"""
        await self.admin_commands.log_channels_test(interaction)

    @discord.app_commands.command(name="log_channels_reset", description="🔄 Reset all event channel mappings (CAUTION)")
    async def log_channels_reset(self, interaction: discord.Interaction):
        """Reset all event channel mappings"""
        await self.admin_commands.log_channels_reset(interaction)

    # ==================== VOICE STATISTICS COMMANDS ====================

    @discord.app_commands.command(name="voice_stats", description="🎵 Show voice channel activity statistics")
    @discord.app_commands.describe(days="Number of days to analyze (default: 7)")
    async def voice_stats(self, interaction: discord.Interaction, days: int = 7):
        """Show voice activity statistics"""
        await interaction.response.send_message("📊 Gathering voice statistics...", ephemeral=True)

        try:
            # Check permissions
            if not interaction.user.guild_permissions.administrator:
                await interaction.edit_original_response(
                    content="❌ You need administrator permissions to view voice statistics."
                )
                return

            guild_id = str(interaction.guild.id)
            stats = await self.voice_logs.get_voice_statistics(guild_id, days)

            # Create statistics embed
            embed = discord.Embed(
                title="🎵 Voice Activity Statistics",
                description=f"Voice channel activity for the last {days} day{'s' if days != 1 else ''}",
                color=discord.Color.blue()
            )

            # Basic statistics
            embed.add_field(
                name="📊 Activity Summary",
                value=f"**Joins:** {stats['joins_tracked']}\n"
                      f"**Leaves:** {stats['leaves_tracked']}\n"
                      f"**Moves:** {stats['moves_tracked']}\n"
                      f"**Currently Active:** {stats['currently_active']} users",
                inline=True
            )

            embed.add_field(
                name="👥 User Activity",
                value=f"**Unique Users:** {stats['active_users']}\n"
                      f"**Active Sessions:** {stats['currently_active']}\n"
                      f"**Average per Day:** {stats['joins_tracked'] / max(days, 1):.1f}",
                inline=True
            )

            # Show active sessions if any
            active_sessions = self.voice_logs.get_active_sessions_info()
            if active_sessions:
                session_info = []
                for session in active_sessions[:5]:  # Show top 5
                    session_info.append(f"• {session['member'].display_name}: {session['duration']} in {session['channel'].name}")

                embed.add_field(
                    name="🔴 Currently Active Sessions",
                    value="\n".join(session_info),
                    inline=False
                )

                if len(active_sessions) > 5:
                    embed.add_field(
                        name="",
                        value=f"... and {len(active_sessions) - 5} more active sessions",
                        inline=False
                    )

            embed.set_footer(text=f"Statistics for {interaction.guild.name}")

            await interaction.edit_original_response(content=None, embed=embed)

        except Exception as e:
            logger.error(f"Error in voice_stats command: {e}")
            await interaction.edit_original_response(content="❌ Error gathering voice statistics")

    @discord.app_commands.command(name="voice_sessions", description="🎵 Show currently active voice sessions")
    async def voice_sessions(self, interaction: discord.Interaction):
        """Show currently active voice sessions"""
        await interaction.response.send_message("🎵 Getting active voice sessions...", ephemeral=True)

        try:
            # Check permissions
            if not interaction.user.guild_permissions.manage_guild:
                await interaction.edit_original_response(
                    content="❌ You need 'Manage Server' permissions to view voice sessions."
                )
                return

            active_sessions = self.voice_logs.get_active_sessions_info()

            if not active_sessions:
                embed = discord.Embed(
                    title="🎵 Active Voice Sessions",
                    description="No users are currently in voice channels.",
                    color=discord.Color.blue()
                )
                await interaction.edit_original_response(content=None, embed=embed)
                return

            # Create sessions embed
            embed = discord.Embed(
                title="🎵 Active Voice Sessions",
                description=f"Currently tracking {len(active_sessions)} active voice sessions",
                color=discord.Color.green()
            )

            # Show sessions (limit to 10 for embed size)
            for i, session in enumerate(active_sessions[:10]):
                member = session['member']
                channel = session['channel']
                duration = session['duration']
                moves = session['moves']

                move_text = f" ({moves} moves)" if moves > 0 else ""

                embed.add_field(
                    name=f"👤 {member.display_name}",
                    value=f"🔊 {channel.name}\n⏱️ {duration}{move_text}",
                    inline=True
                )

            if len(active_sessions) > 10:
                embed.add_field(
                    name="",
                    value=f"... and {len(active_sessions) - 10} more active sessions",
                    inline=False
                )

            # Add summary
            total_time = sum(s['duration_seconds'] for s in active_sessions)
            avg_time = total_time / len(active_sessions)

            embed.add_field(
                name="📊 Session Summary",
                value=f"**Total Active Time:** {self.voice_logs.format_duration(timedelta(seconds=total_time))}\n"
                      f"**Average Session:** {self.voice_logs.format_duration(timedelta(seconds=avg_time))}\n"
                      f"**Longest Session:** {active_sessions[0]['duration']} ({active_sessions[0]['member'].display_name})",
                inline=False
            )

            await interaction.edit_original_response(content=None, embed=embed)

        except Exception as e:
            logger.error(f"Error in voice_sessions command: {e}")
            await interaction.edit_original_response(content="❌ Error getting voice sessions")

    # ==================== DEBUGGING COMMANDS ====================

    @discord.app_commands.command(name="log_events_list", description="📋 Show all available event types for configuration")
    async def log_events_list(self, interaction: discord.Interaction):
        """Display all available event types and their descriptions"""
        await self.admin_commands.log_events_list(interaction)

    @discord.app_commands.command(name="log_debug", description="🔧 Debug logging configuration (Admin only)")
    async def log_debug(self, interaction: discord.Interaction):
        """Debug logging configuration and routing"""
        await interaction.response.send_message("🔧 Running logging diagnostics...", ephemeral=True)

        try:
            if not interaction.user.guild_permissions.administrator:
                await interaction.edit_original_response(
                    content="❌ You need administrator permissions to debug logging."
                )
                return

            guild_id = str(interaction.guild.id)

            # Get debugging information from base logger
            debug_info = await self.admin_commands.get_routing_debug_info(guild_id)

            # Test a few key event types
            test_events = ['message_delete', 'member_join', 'voice_join']
            test_results = []

            for event_type in test_events:
                test_result = await self.admin_commands.base.test_channel_routing(interaction.guild, event_type)
                test_results.append({
                    'event': event_type,
                    'success': test_result['success'],
                    'channel': test_result.get('resolved_channel', {}).get('name', 'None'),
                    'type': test_result.get('resolved_channel', {}).get('type', 'None')
                })

            embed = discord.Embed(
                title="🔧 Logging Debug Report",
                description="Comprehensive logging system diagnostics",
                color=discord.Color.blue()
            )

            # Add routing info
            embed.add_field(
                name="🔍 Routing Information",
                value=debug_info,
                inline=False
            )

            # Add test results
            test_summary = []
            for result in test_results:
                status = "✅" if result['success'] else "❌"
                test_summary.append(f"{status} **{result['event']}**: {result['channel']} ({result['type']})")

            embed.add_field(
                name="🧪 Channel Resolution Tests",
                value="\n".join(test_summary),
                inline=False
            )

            # Add module status
            module_status = []
            for module in self.modules:
                module_name = module.__class__.__name__
                module_status.append(f"✅ {module_name}")

            embed.add_field(
                name="🔧 Loaded Modules",
                value="\n".join(module_status),
                inline=False
            )

            embed.set_footer(text="Use this information to troubleshoot logging issues")

            await interaction.edit_original_response(content=None, embed=embed)

        except Exception as e:
            logger.error(f"Error in log_debug command: {e}")
            await interaction.edit_original_response(content="❌ Error running debug diagnostics")

    # ==================== MODULE MANAGEMENT ====================

    def get_module_status(self) -> Dict[str, Any]:
        """Get status of all logging modules"""
        status = {
            'total_modules': len(self.modules),
            'modules': {}
        }

        for module in self.modules:
            module_name = module.__class__.__name__
            status['modules'][module_name] = {
                'loaded': True,
                'type': type(module).__name__,
                'events': getattr(module, 'event_types', [])
            }

        return status

    def get_supported_events(self) -> List[str]:
        """Get list of all supported event types across modules"""
        events = []
        for module in self.modules:
            if hasattr(module, 'event_types'):
                events.extend(module.event_types.keys())
        return sorted(list(set(events)))

    def get_advanced_features(self) -> Dict[str, bool]:
        """Get status of advanced features"""
        return {
            'flexible_routing': True,
            'granular_setup': True,
            'grouped_setup': True,
            'voice_analytics': True,
            'channel_testing': True,
            'debug_diagnostics': True,
            'auto_setup': True,
            'migration_support': True
        }

# Setup function for the cog
async def setup(bot):
    """Setup function for the enhanced modular logging cog"""
    await bot.add_cog(ConfigurableLogging(bot))
    logger.info("✅ Enhanced modular logging cog loaded successfully with flexible routing")