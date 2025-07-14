"""
Enhanced Logging Admin Commands Module - cogs/logging/admin_commands.py
Comprehensive administrative interface for flexible logging configuration
"""

import discord
from discord.ext import commands
from discord import app_commands
import logging
from datetime import datetime
from typing import Optional, List

from .base import LoggingModule
from utils.database import (
    get_guild_config, is_logging_enabled, is_event_enabled,
    update_guild_config, set_event_enabled, db_manager,
    set_event_channel, set_events_channel, get_event_channel,
    get_all_event_channels, get_channel_mapping_summary,
    clear_all_event_channels, remove_event_channel, get_channel_events
)
from utils.embeds import EmbedBuilder
from utils.channel_manager import get_channel_manager

logger = logging.getLogger(__name__)

class LoggingAdmin(LoggingModule):
    """Enhanced administrative commands for flexible logging configuration"""

    def __init__(self, bot):
        super().__init__(bot)
        self.channel_manager = get_channel_manager(bot)

        # Available event types for configuration
        self.event_types = {
            'message_delete': 'Message Deletions',
            'message_edit': 'Message Edits',
            'image_send': 'Image/File Uploads',
            'image_delete': 'Image/File Deletions',
            'member_join': 'Member Joins',
            'member_leave': 'Member Leaves',
            'member_ban': 'Member Bans',
            'member_unban': 'Member Unbans',
            'voice_join': 'Voice Channel Joins',
            'voice_leave': 'Voice Channel Leaves',
            'voice_move': 'Voice Channel Moves',
            'voice_mute': 'Voice Mute/Unmute',
            'voice_deafen': 'Voice Deafen/Undeafen',
            'voice_stream': 'Voice Streaming',
            'voice_video': 'Voice Video/Camera'
        }

    async def verify_bot_permissions(self, guild: discord.Guild, channel: discord.TextChannel = None) -> dict:
        """Verify bot has required permissions for logging"""
        # CHANGE: Add comprehensive permission checking
        if channel:
            # Check specific channel permissions
            perms = channel.permissions_for(guild.me)
            missing_perms = []

            required_permissions = {
                'send_messages': 'Send Messages',
                'embed_links': 'Embed Links',
                'attach_files': 'Attach Files',
                'read_message_history': 'Read Message History',
                'use_external_emojis': 'Use External Emojis'
            }

            for perm, display_name in required_permissions.items():
                if not getattr(perms, perm, False):
                    missing_perms.append(display_name)

            return {
                'valid': len(missing_perms) == 0,
                'missing_permissions': missing_perms,
                'channel': channel.name
            }
        else:
            # Check general guild permissions
            perms = guild.me.guild_permissions
            missing_perms = []

            if not perms.manage_channels:
                missing_perms.append('Manage Channels (for auto-setup)')
            if not perms.view_audit_log:
                missing_perms.append('View Audit Log (for advanced logging)')

            return {
                'valid': len(missing_perms) == 0,
                'missing_permissions': missing_perms,
                'channel': 'Guild-wide'
            }

    async def setup(self):
        """Setup method called when module is loaded"""
        logger.info("Enhanced logging admin commands module initialized")

    def check_admin_permissions(self, user: discord.Member) -> bool:
        """Check if user has administrator permissions"""
        return user.guild_permissions.administrator

    def check_module_enabled(self) -> bool:
        """Check if logging module is enabled globally"""
        return self.bot.config.MODULES_ENABLED.get('logging', False)

    # ==================== AUTO-SETUP COMMANDS ====================

    async def log_setup_granular(self, interaction: discord.Interaction):
        """Set up granular logging with individual channels for each event"""
        await interaction.response.send_message("🔧 Setting up granular logging channels...", ephemeral=True)

        try:
            # CHANGE: Add permission validation before setup
            perm_check = await self.verify_bot_permissions(interaction.guild)
            if not perm_check['valid']:
                await interaction.edit_original_response(
                    content=f"❌ Missing required permissions: {', '.join(perm_check['missing_permissions'])}\n"
                            f"Please ensure the bot has these permissions and try again."
                )
                return

            if not self.check_admin_permissions(interaction.user):
                await interaction.edit_original_response(
                    content="❌ You need administrator permissions to configure logging."
                )
                return

            if not self.check_module_enabled():
                await interaction.edit_original_response(
                    content="❌ The logging module is not enabled on this bot."
                )
                return

            # Set up granular channels
            results = await self.channel_manager.setup_granular_channels(interaction.guild)

            if results['success']:
                # Enable logging if not already enabled
                guild_id = str(interaction.guild.id)
                config = await get_guild_config(guild_id) or {}
                config['logging_enabled'] = True
                config['guild_name'] = interaction.guild.name
                await update_guild_config(guild_id, config)

                # Enable all events
                for event_type in self.event_types.keys():
                    await set_event_enabled(guild_id, event_type, True)

                # Send welcome messages
                await self.channel_manager.send_welcome_messages(results, "granular")

                # Create success embed
                embed = EmbedBuilder.success(
                    "🎯 Granular Logging Setup Complete!",
                    f"Created {len(results['channels_created'])} new channels for maximum logging detail."
                )

                embed.add_field(
                    name="📊 Setup Summary",
                    value=f"**Category:** {results['category'].name if results['category'] else 'Failed'}\n"
                          f"**New Channels:** {len(results['channels_created'])}\n"
                          f"**Existing Channels:** {len(results['channels_existing'])}\n"
                          f"**Events Mapped:** {len(results['events_mapped'])}\n"
                          f"**Total Events:** {len(self.event_types)}",
                    inline=False
                )

                if results['channels_created']:
                    channel_list = [f"• {ch.name}" for ch in results['channels_created'][:10]]
                    if len(results['channels_created']) > 10:
                        channel_list.append(f"... and {len(results['channels_created']) - 10} more")

                    embed.add_field(
                        name="🆕 New Channels Created",
                        value="\n".join(channel_list),
                        inline=False
                    )

                embed.add_field(
                    name="🔧 What's Next?",
                    value="• Use `/log_channels_list` to see all mappings\n"
                          "• Use `/log_channel` to modify specific mappings\n"
                          "• Test logging by posting messages, joining voice, etc.",
                    inline=False
                )

            else:
                embed = EmbedBuilder.error(
                    "Setup Failed",
                    "Failed to set up granular logging channels."
                )
                if results['errors']:
                    embed.add_field(
                        name="Errors",
                        value="\n".join(results['errors'][:5]),
                        inline=False
                    )

            await interaction.edit_original_response(content=None, embed=embed)

        except Exception as e:
            logger.error(f"Error in log_setup_granular: {e}")
            await interaction.edit_original_response(content="❌ Error setting up granular logging")

    async def log_setup_grouped(self, interaction: discord.Interaction):
        """Set up grouped logging with channels for related event types"""
        await interaction.response.send_message("🔧 Setting up grouped logging channels...", ephemeral=True)

        try:
            if not self.check_admin_permissions(interaction.user):
                await interaction.edit_original_response(
                    content="❌ You need administrator permissions to configure logging."
                )
                return

            if not self.check_module_enabled():
                await interaction.edit_original_response(
                    content="❌ The logging module is not enabled on this bot."
                )
                return

            # Set up grouped channels
            results = await self.channel_manager.setup_grouped_channels(interaction.guild)

            if results['success']:
                # Enable logging if not already enabled
                guild_id = str(interaction.guild.id)
                config = await get_guild_config(guild_id) or {}
                config['logging_enabled'] = True
                config['guild_name'] = interaction.guild.name
                await update_guild_config(guild_id, config)

                # Enable all events
                for event_type in self.event_types.keys():
                    await set_event_enabled(guild_id, event_type, True)

                # Send welcome messages
                await self.channel_manager.send_welcome_messages(results, "grouped")

                # Create success embed
                embed = EmbedBuilder.success(
                    "📋 Grouped Logging Setup Complete!",
                    f"Created {len(results['channels_created'])} new grouped channels for organized logging."
                )

                embed.add_field(
                    name="📊 Setup Summary",
                    value=f"**Category:** {results['category'].name if results['category'] else 'Failed'}\n"
                          f"**New Channels:** {len(results['channels_created'])}\n"
                          f"**Existing Channels:** {len(results['channels_existing'])}\n"
                          f"**Groups Mapped:** {len(results['groups_mapped'])}\n"
                          f"**Total Events:** {sum(g['event_count'] for g in results['groups_mapped'])}",
                    inline=False
                )

                if results['groups_mapped']:
                    group_list = []
                    for group in results['groups_mapped']:
                        group_list.append(f"• **{group['channel']}**: {group['event_count']} events")

                    embed.add_field(
                        name="📋 Channel Groups",
                        value="\n".join(group_list),
                        inline=False
                    )

                embed.add_field(
                    name="🔧 What's Next?",
                    value="• Use `/log_channels_list` to see detailed mappings\n"
                          "• Use `/log_group` to modify group mappings\n"
                          "• Use `/log_channel` for individual event changes",
                    inline=False
                )

            else:
                embed = EmbedBuilder.error(
                    "Setup Failed",
                    "Failed to set up grouped logging channels."
                )
                if results['errors']:
                    embed.add_field(
                        name="Errors",
                        value="\n".join(results['errors'][:5]),
                        inline=False
                    )

            await interaction.edit_original_response(content=None, embed=embed)

        except Exception as e:
            logger.error(f"Error in log_setup_grouped: {e}")
            await interaction.edit_original_response(content="❌ Error setting up grouped logging")

    # ==================== MANUAL CONFIGURATION COMMANDS ====================

    async def log_channel(self, interaction: discord.Interaction, event: str, channel: discord.TextChannel):
        """Map a specific event to a specific channel"""
        await interaction.response.send_message("⚙️ Configuring event channel mapping...", ephemeral=True)

        try:
            if not self.check_admin_permissions(interaction.user):
                await interaction.edit_original_response(
                    content="❌ You need administrator permissions to configure logging."
                )
                return

            guild_id = str(interaction.guild.id)

            # Check if logging is enabled
            if not await is_logging_enabled(guild_id):
                await interaction.edit_original_response(
                    content="❌ Please use `/log_config` to enable logging first!"
                )
                return

            # Set the event-channel mapping
            await set_event_channel(guild_id, event, str(channel.id), channel.name)

            # Enable the event if not already enabled
            await set_event_enabled(guild_id, event, True)

            event_name = self.event_types.get(event, event)

            embed = EmbedBuilder.success(
                "🎯 Event Channel Configured",
                f"**{event_name}** logs will now be sent to {channel.mention}"
            )

            embed.add_field(
                name="📋 Configuration Details",
                value=f"**Event:** {event_name}\n"
                      f"**Channel:** {channel.mention}\n"
                      f"**Event Enabled:** ✅ Yes\n"
                      f"**Channel ID:** `{channel.id}`",
                inline=False
            )

            # Show other events in the same channel
            other_events = await get_channel_events(guild_id, str(channel.id))
            other_events = [e for e in other_events if e != event]

            if other_events:
                other_names = [self.event_types.get(e, e) for e in other_events]
                embed.add_field(
                    name="🔗 Other Events in This Channel",
                    value="\n".join([f"• {name}" for name in other_names[:5]]),
                    inline=False
                )

            embed.add_field(
                name="🔧 Management Commands",
                value="• `/log_channels_list` - View all mappings\n"
                      "• `/log_group` - Map multiple events to one channel\n"
                      "• `/log_channels_test` - Test the configuration",
                inline=False
            )

            await interaction.edit_original_response(content=None, embed=embed)

        except Exception as e:
            logger.error(f"Error in log_channel: {e}")
            await interaction.edit_original_response(content="❌ Error configuring event channel")

    async def log_group(self, interaction: discord.Interaction, events: str, channel: discord.TextChannel):
        """Map multiple events to a single channel"""
        await interaction.response.send_message("⚙️ Configuring event group mapping...", ephemeral=True)

        try:
            if not self.check_admin_permissions(interaction.user):
                await interaction.edit_original_response(
                    content="❌ You need administrator permissions to configure logging."
                )
                return

            guild_id = str(interaction.guild.id)

            # Check if logging is enabled
            if not await is_logging_enabled(guild_id):
                await interaction.edit_original_response(
                    content="❌ Please use `/log_config` to enable logging first!"
                )
                return

            # Parse and validate events
            event_list = [e.strip() for e in events.split(',')]
            valid_events = []
            invalid_events = []

            for event in event_list:
                if event in self.event_types:
                    valid_events.append(event)
                else:
                    invalid_events.append(event)

            if not valid_events:
                await interaction.edit_original_response(
                    content="❌ No valid event types provided. Use `/log_events_list` to see available events."
                )
                return

            # Set the events-channel mapping
            await set_events_channel(guild_id, valid_events, str(channel.id), channel.name)

            # Enable all events
            for event in valid_events:
                await set_event_enabled(guild_id, event, True)

            embed = EmbedBuilder.success(
                "📋 Event Group Configured",
                f"**{len(valid_events)} events** will now be sent to {channel.mention}"
            )

            embed.add_field(
                name="✅ Mapped Events",
                value="\n".join([f"• {self.event_types[e]}" for e in valid_events]),
                inline=False
            )

            if invalid_events:
                embed.add_field(
                    name="❌ Invalid Events (Ignored)",
                    value="\n".join([f"• {e}" for e in invalid_events]),
                    inline=False
                )

            embed.add_field(
                name="📋 Configuration Details",
                value=f"**Channel:** {channel.mention}\n"
                      f"**Events Mapped:** {len(valid_events)}\n"
                      f"**All Events Enabled:** ✅ Yes\n"
                      f"**Channel ID:** `{channel.id}`",
                inline=False
            )

            await interaction.edit_original_response(content=None, embed=embed)

        except Exception as e:
            logger.error(f"Error in log_group: {e}")
            await interaction.edit_original_response(content="❌ Error configuring event group")

    # ==================== STATUS AND MANAGEMENT COMMANDS ====================

    async def log_channels_list(self, interaction: discord.Interaction):
        """Display comprehensive channel mapping information"""
        await interaction.response.send_message("📊 Getting channel mappings...", ephemeral=True)

        try:
            guild_id = str(interaction.guild.id)
            config = await get_guild_config(guild_id)

            if not config or not config.get('logging_enabled', False):
                embed = EmbedBuilder.warning(
                    "Logging Not Enabled",
                    "Logging is not enabled for this server."
                )
                embed.add_field(
                    name="🚀 Get Started",
                    value="Use `/log_setup_granular` or `/log_setup_grouped` to set up logging!",
                    inline=False
                )
                await interaction.edit_original_response(content=None, embed=embed)
                return

            # Get mapping summary
            summary = await get_channel_mapping_summary(guild_id)

            embed = discord.Embed(
                title="📊 Event Channel Mappings",
                description=f"Complete logging configuration for {interaction.guild.name}",
                color=discord.Color.blue()
            )

            # Summary statistics
            embed.add_field(
                name="📈 Summary",
                value=f"**Total Channels:** {summary['total_channels']}\n"
                      f"**Events Mapped:** {summary['total_events_mapped']}\n"
                      f"**Available Events:** {len(self.event_types)}\n"
                      f"**Logging Status:** ✅ Enabled",
                inline=False
            )

            # Show channel mappings
            if summary['channels']:
                for channel_info in summary['channels'][:10]:  # Limit to avoid embed size limits
                    channel = interaction.guild.get_channel(int(channel_info['channel_id']))
                    channel_mention = channel.mention if channel else f"#{channel_info['channel_name']}"

                    event_names = [self.event_types.get(e, e) for e in channel_info['events']]
                    events_text = "\n".join([f"• {name}" for name in event_names[:8]])
                    if len(event_names) > 8:
                        events_text += f"\n• ... and {len(event_names) - 8} more"

                    embed.add_field(
                        name=f"📋 {channel_mention} ({channel_info['event_count']} events)",
                        value=events_text,
                        inline=True
                    )

                if len(summary['channels']) > 10:
                    embed.add_field(
                        name="",
                        value=f"... and {len(summary['channels']) - 10} more channels",
                        inline=False
                    )

            # Show unmapped events
            all_mapped_events = set()
            for channel_info in summary['channels']:
                all_mapped_events.update(channel_info['events'])

            unmapped_events = set(self.event_types.keys()) - all_mapped_events
            if unmapped_events:
                unmapped_names = [self.event_types[e] for e in unmapped_events]
                embed.add_field(
                    name="⚠️ Unmapped Events",
                    value="\n".join([f"• {name}" for name in unmapped_names[:5]]),
                    inline=False
                )
                if len(unmapped_names) > 5:
                    embed.add_field(
                        name="",
                        value=f"... and {len(unmapped_names) - 5} more unmapped events",
                        inline=False
                    )

            embed.add_field(
                name="🔧 Management Commands",
                value="• `/log_channel` - Map individual events\n"
                      "• `/log_group` - Map multiple events to one channel\n"
                      "• `/log_channels_test` - Test your configuration\n"
                      "• `/log_channels_reset` - Reset all mappings",
                inline=False
            )

            await interaction.edit_original_response(content=None, embed=embed)

        except Exception as e:
            logger.error(f"Error in log_channels_list: {e}")
            await interaction.edit_original_response(content="❌ Error getting channel mappings")

    async def log_channels_test(self, interaction: discord.Interaction):
        """Send test messages to verify channel configuration"""
        await interaction.response.send_message("🧪 Testing channel configuration...", ephemeral=True)

        try:
            if not self.check_admin_permissions(interaction.user):
                await interaction.edit_original_response(
                    content="❌ You need administrator permissions to test logging."
                )
                return

            guild_id = str(interaction.guild.id)
            summary = await get_channel_mapping_summary(guild_id)

            if not summary['channels']:
                await interaction.edit_original_response(
                    content="❌ No channels configured. Use `/log_setup_granular` or `/log_setup_grouped` first!"
                )
                return

            test_results = {
                'success': 0,
                'failed': 0,
                'channels_tested': []
            }

            # Send test message to each configured channel
            for channel_info in summary['channels']:
                channel = interaction.guild.get_channel(int(channel_info['channel_id']))
                if not channel:
                    test_results['failed'] += 1
                    continue

                try:
                    test_embed = discord.Embed(
                        title="🧪 Logging Test Message",
                        description="This is a test message to verify logging configuration.",
                        color=discord.Color.green()
                    )

                    test_embed.add_field(
                        name="📋 Channel Configuration",
                        value=f"**Events:** {channel_info['event_count']}\n"
                              f"**Channel:** {channel.mention}\n"
                              f"**Test Time:** <t:{int(interaction.created_at.timestamp())}:F>",
                        inline=False
                    )

                    mapped_events = [self.event_types.get(e, e) for e in channel_info['events'][:5]]
                    test_embed.add_field(
                        name="🎯 Mapped Events",
                        value="\n".join([f"• {name}" for name in mapped_events]),
                        inline=False
                    )

                    test_embed.set_footer(text="Fenrir Logging Test • This message can be safely deleted")

                    await channel.send(embed=test_embed)
                    test_results['success'] += 1
                    test_results['channels_tested'].append(channel.name)

                except Exception as e:
                    logger.error(f"Failed to send test message to {channel.name}: {e}")
                    test_results['failed'] += 1

            # Report results
            if test_results['success'] > 0:
                embed = EmbedBuilder.success(
                    "🧪 Test Messages Sent",
                    f"Successfully sent test messages to {test_results['success']} channels."
                )

                if test_results['channels_tested']:
                    channels_list = ", ".join([f"#{name}" for name in test_results['channels_tested'][:8]])
                    if len(test_results['channels_tested']) > 8:
                        channels_list += f" and {len(test_results['channels_tested']) - 8} more"

                    embed.add_field(
                        name="✅ Channels Tested",
                        value=channels_list,
                        inline=False
                    )

                if test_results['failed'] > 0:
                    embed.add_field(
                        name="⚠️ Failed Tests",
                        value=f"{test_results['failed']} channels could not receive test messages",
                        inline=False
                    )

            else:
                embed = EmbedBuilder.error(
                    "Test Failed",
                    "Could not send test messages to any configured channels."
                )

            await interaction.edit_original_response(content=None, embed=embed)

        except Exception as e:
            logger.error(f"Error in log_channels_test: {e}")
            await interaction.edit_original_response(content="❌ Error testing channel configuration")

    async def log_channels_reset(self, interaction: discord.Interaction):
        """Reset all event channel mappings"""
        await interaction.response.send_message("⚠️ Resetting channel mappings...", ephemeral=True)

        try:
            if not self.check_admin_permissions(interaction.user):
                await interaction.edit_original_response(
                    content="❌ You need administrator permissions to reset logging."
                )
                return

            guild_id = str(interaction.guild.id)

            # Get current mapping count
            summary = await get_channel_mapping_summary(guild_id)

            if not summary['channels']:
                await interaction.edit_original_response(
                    content="❌ No channel mappings to reset."
                )
                return

            # Clear all mappings
            removed_count = await clear_all_event_channels(guild_id)

            embed = EmbedBuilder.warning(
                "🔄 Channel Mappings Reset",
                f"Cleared {removed_count} event-to-channel mappings."
            )

            embed.add_field(
                name="💡 What's Next?",
                value="• Use `/log_setup_granular` for individual event channels\n"
                      "• Use `/log_setup_grouped` for grouped channels\n"
                      "• Use `/log_channel` to manually configure events\n"
                      "• Logging events are still enabled, just not mapped to channels",
                inline=False
            )

            embed.add_field(
                name="⚠️ Note",
                value="The logging channels still exist - only the event mappings were cleared.",
                inline=False
            )

            await interaction.edit_original_response(content=None, embed=embed)

        except Exception as e:
            logger.error(f"Error in log_channels_reset: {e}")
            await interaction.edit_original_response(content="❌ Error resetting channel mappings")

    # ==================== INFORMATION COMMANDS ====================

    async def log_events_list(self, interaction: discord.Interaction):
        """Display all available event types and their descriptions"""
        await interaction.response.send_message("📋 Loading available events...", ephemeral=True)

        try:
            embed = discord.Embed(
                title="📋 Available Event Types",
                description="Complete list of events that can be logged by Fenrir",
                color=discord.Color.blue()
            )

            # Group events by category
            event_groups = {
                'Message Events': ['message_delete', 'message_edit'],
                'File Events': ['image_send', 'image_delete'],
                'Member Events': ['member_join', 'member_leave', 'member_ban', 'member_unban'],
                'Voice Events': ['voice_join', 'voice_leave', 'voice_move', 'voice_mute', 'voice_deafen', 'voice_stream', 'voice_video']
            }

            for group_name, events in event_groups.items():
                event_list = []
                for event in events:
                    event_name = self.event_types.get(event, event)
                    event_list.append(f"• **{event}**: {event_name}")

                embed.add_field(
                    name=f"{group_name} ({len(events)})",
                    value="\n".join(event_list),
                    inline=False
                )

            # Add usage examples
            embed.add_field(
                name="💡 Usage Examples",
                value="• `/log_channel event:message_delete channel:#deletions`\n"
                      "• `/log_group events:member_join,member_leave channel:#members`\n"
                      "• `/log_setup_granular` - Creates channels for all events\n"
                      "• `/log_setup_grouped` - Creates grouped channels",
                inline=False
            )

            embed.add_field(
                name="📊 Statistics",
                value=f"**Total Events:** {len(self.event_types)}\n"
                      f"**Event Groups:** {len(event_groups)}\n"
                      f"**Categories:** Message, File, Member, Voice",
                inline=False
            )

            embed.set_footer(text="Use these event names with /log_channel and /log_group commands")

            await interaction.edit_original_response(content=None, embed=embed)

        except Exception as e:
            logger.error(f"Error in log_events_list: {e}")
            await interaction.edit_original_response(content="❌ Error loading event types")

    # ==================== LEGACY SUPPORT COMMANDS ====================

    async def log_config(self, interaction: discord.Interaction,
                        channel: Optional[discord.TextChannel] = None,
                        enabled: Optional[bool] = None):
        """Configure basic logging settings (legacy support)"""
        await interaction.response.send_message("⚙️ Configuring basic logging settings...", ephemeral=True)

        try:
            if not self.check_admin_permissions(interaction.user):
                await interaction.edit_original_response(
                    content="❌ You need administrator permissions to configure logging."
                )
                return

            if not self.check_module_enabled():
                await interaction.edit_original_response(
                    content="❌ The logging module is not enabled on this bot."
                )
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
            await update_guild_config(guild_id, config)

            embed = EmbedBuilder.success(
                "⚙️ Basic Logging Configuration Updated",
                "Your basic logging settings have been saved."
            )

            # Show current configuration
            if config.get('log_channel_id'):
                log_channel = interaction.guild.get_channel(int(config['log_channel_id']))
                embed.add_field(
                    name="📍 Default Log Channel",
                    value=log_channel.mention if log_channel else "Channel not found",
                    inline=True
                )
            else:
                embed.add_field(
                    name="📍 Default Log Channel",
                    value="Not set",
                    inline=True
                )

            embed.add_field(
                name="🔄 Logging Status",
                value="✅ Enabled" if config.get('logging_enabled', False) else "❌ Disabled",
                inline=True
            )

            # Advanced setup recommendations
            embed.add_field(
                name="🚀 Advanced Setup Options",
                value="• `/log_setup_granular` - Individual channels per event\n"
                      "• `/log_setup_grouped` - Organized channel groups\n"
                      "• `/log_channels_list` - View current mappings",
                inline=False
            )

            await interaction.edit_original_response(content=None, embed=embed)

        except Exception as e:
            logger.error(f"Error in log_config: {e}")
            await interaction.edit_original_response(content="❌ Error configuring basic logging")

    async def log_events(self, interaction: discord.Interaction, event: str, enabled: bool):
        """Configure which events to log (legacy support)"""
        await interaction.response.send_message("⚙️ Configuring event logging...", ephemeral=True)

        try:
            if not self.check_admin_permissions(interaction.user):
                await interaction.edit_original_response(
                    content="❌ You need administrator permissions to configure logging."
                )
                return

            guild_id = str(interaction.guild.id)

            # Check if logging is enabled
            if not await is_logging_enabled(guild_id):
                await interaction.edit_original_response(
                    content="❌ Please use `/log_config` to enable logging first!"
                )
                return

            # Update event configuration
            await set_event_enabled(guild_id, event, enabled)

            event_name = self.event_types.get(event, event)
            action = "enabled" if enabled else "disabled"

            embed = EmbedBuilder.success(
                f"✅ {event_name} Logging {action.title()}",
                f"{event_name} logging has been {action}."
            )

            # Check if event has a specific channel mapping
            event_channel_id = await get_event_channel(guild_id, event)
            if event_channel_id:
                event_channel = interaction.guild.get_channel(int(event_channel_id))
                embed.add_field(
                    name="📍 Specific Channel",
                    value=event_channel.mention if event_channel else "Channel not found",
                    inline=True
                )
            else:
                config = await get_guild_config(guild_id)
                if config and config.get('log_channel_id'):
                    default_channel = interaction.guild.get_channel(int(config['log_channel_id']))
                    embed.add_field(
                        name="📍 Default Channel",
                        value=default_channel.mention if default_channel else "Channel not found",
                        inline=True
                    )

            embed.add_field(
                name="🔧 Advanced Options",
                value=f"• `/log_channel event:{event}` - Set specific channel\n"
                      "• `/log_channels_list` - View all mappings\n"
                      "• `/log_setup_granular` - Full granular setup",
                inline=False
            )

            await interaction.edit_original_response(content=None, embed=embed)

        except Exception as e:
            logger.error(f"Error in log_events: {e}")
            await interaction.edit_original_response(content="❌ Error configuring event logging")

    async def log_status(self, interaction: discord.Interaction):
        """View current logging configuration (enhanced)"""
        await interaction.response.send_message("📊 Getting comprehensive logging status...", ephemeral=True)

        try:
            guild_id = str(interaction.guild.id)
            config = await get_guild_config(guild_id)

            if not config:
                embed = EmbedBuilder.warning(
                    "Logging Not Configured",
                    "❌ Logging has not been configured for this server."
                )
                embed.add_field(
                    name="🚀 Quick Setup Options",
                    value="• `/log_setup_granular` - Individual channels per event\n"
                          "• `/log_setup_grouped` - Organized channel groups\n"
                          "• `/log_config` - Basic single-channel setup",
                    inline=False
                )
                await interaction.edit_original_response(content=None, embed=embed)
                return

            # Create comprehensive status embed
            embed = discord.Embed(
                title="📊 Comprehensive Logging Status",
                description="Complete logging configuration for this server",
                color=discord.Color.blue() if config.get('logging_enabled', False) else discord.Color.red()
            )

            # Basic configuration
            status_emoji = "🟢" if config.get('logging_enabled', False) else "🔴"
            embed.add_field(
                name="🔄 Logging Status",
                value=f"{status_emoji} {'Enabled' if config.get('logging_enabled', False) else 'Disabled'}",
                inline=True
            )

            # Default log channel
            if config.get('log_channel_id'):
                log_channel = interaction.guild.get_channel(int(config['log_channel_id']))
                channel_text = log_channel.mention if log_channel else "⚠️ Channel not found"
            else:
                channel_text = "❌ Not set"

            embed.add_field(
                name="📍 Default Log Channel",
                value=channel_text,
                inline=True
            )

            # Channel mapping summary
            summary = await get_channel_mapping_summary(guild_id)
            embed.add_field(
                name="🎯 Event Channels",
                value=f"**Mapped Channels:** {summary['total_channels']}\n"
                      f"**Mapped Events:** {summary['total_events_mapped']}\n"
                      f"**Setup Type:** {'Granular' if summary['total_channels'] > 8 else 'Grouped' if summary['total_channels'] > 1 else 'Basic'}",
                inline=True
            )

            # Module status
            embed.add_field(
                name="🔧 Module Status",
                value=f"✅ Enabled" if self.check_module_enabled() else "❌ Disabled",
                inline=True
            )

            # Show enabled events if logging is on
            if config.get('logging_enabled', False) and db_manager:
                enabled_events = await db_manager.get_all_enabled_events(guild_id)
                if enabled_events:
                    event_names = [self.event_types.get(event, event) for event in enabled_events[:8]]
                    events_text = "\n".join([f"✅ {name}" for name in event_names])
                    if len(enabled_events) > 8:
                        events_text += f"\n... and {len(enabled_events) - 8} more"

                    embed.add_field(
                        name="📝 Enabled Events",
                        value=events_text,
                        inline=False
                    )
                else:
                    embed.add_field(
                        name="📝 Enabled Events",
                        value="❌ No events enabled\nUse `/log_events` to enable specific events!",
                        inline=False
                    )

            # Quick actions
            embed.add_field(
                name="⚡ Quick Actions",
                value="• `/log_channels_list` - View detailed mappings\n"
                      "• `/log_channels_test` - Test your configuration\n"
                      "• `/log_setup_granular` - Upgrade to granular logging\n"
                      "• `/log_setup_grouped` - Switch to grouped logging",
                inline=False
            )

            await interaction.edit_original_response(content=None, embed=embed)

        except Exception as e:
            logger.error(f"Error in log_status: {e}")
            await interaction.edit_original_response(content="❌ Error getting logging status")

    # ==================== UTILITY METHODS ====================

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
            for event, channel_id in list(routing_info['event_mappings'].items())[:8]:
                debug_lines.append(f"  • {event} → {channel_id}")
            if len(routing_info['event_mappings']) > 8:
                debug_lines.append(f"  • ... and {len(routing_info['event_mappings']) - 8} more")

        return "\n".join(debug_lines)