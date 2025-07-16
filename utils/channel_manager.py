"""
Channel Management Utility - utils/channel_manager.py
Handles automatic creation of logging channels and categories
"""

import discord
from discord.ext import commands
import logging
from typing import Dict, List, Optional, Any, Tuple
import asyncio

from utils.database import set_event_channel, set_events_channel

logger = logging.getLogger(__name__)


class ChannelManager:
    """Manages automatic creation and configuration of logging channels"""

    def __init__(self, bot):
        self.bot = bot

        # Event type definitions with organized groupings
        self.event_definitions = {
            'message_delete': {
                'name': 'message-deletions',
                'emoji': '🗑️',
                'description': 'Deleted messages',
                'group': 'message'
            },
            'message_edit': {
                'name': 'message-edits',
                'emoji': '✏️',
                'description': 'Edited messages',
                'group': 'message'
            },
            'member_join': {
                'name': 'member-joins',
                'emoji': '👋',
                'description': 'Members joining',
                'group': 'member'
            },
            'member_leave': {
                'name': 'member-leaves',
                'emoji': '👋',
                'description': 'Members leaving',
                'group': 'member'
            },
            'member_ban': {
                'name': 'member-bans',
                'emoji': '🔨',
                'description': 'Member bans',
                'group': 'member'
            },
            'member_unban': {
                'name': 'member-unbans',
                'emoji': '🔓',
                'description': 'Member unbans',
                'group': 'member'
            },
            'image_send': {
                'name': 'file-uploads',
                'emoji': '📤',
                'description': 'File uploads',
                'group': 'file'
            },
            'image_delete': {
                'name': 'file-deletions',
                'emoji': '🗑️',
                'description': 'File deletions',
                'group': 'file'
            },
            'voice_join': {
                'name': 'voice-joins',
                'emoji': '🎵',
                'description': 'Voice channel joins',
                'group': 'voice'
            },
            'voice_leave': {
                'name': 'voice-leaves',
                'emoji': '🎵',
                'description': 'Voice channel leaves',
                'group': 'voice'
            },
            'voice_move': {
                'name': 'voice-moves',
                'emoji': '🔄',
                'description': 'Voice channel moves',
                'group': 'voice'
            },
            'voice_mute': {
                'name': 'voice-mutes',
                'emoji': '🔇',
                'description': 'Voice mute changes',
                'group': 'voice'
            },
            'voice_deafen': {
                'name': 'voice-deafens',
                'emoji': '🔇',
                'description': 'Voice deafen changes',
                'group': 'voice'
            },
            'voice_stream': {
                'name': 'voice-streaming',
                'emoji': '📹',
                'description': 'Voice streaming',
                'group': 'voice'
            },
            'voice_video': {
                'name': 'voice-video',
                'emoji': '📷',
                'description': 'Voice video/camera',
                'group': 'voice'
            }
        }

        # Grouped channel definitions
        self.grouped_channels = {
            'message-logs': {
                'emoji': '💬',
                'description': 'All message events',
                'events': ['message_delete', 'message_edit']
            },
            'member-logs': {
                'emoji': '👥',
                'description': 'All member events',
                'events': ['member_join', 'member_leave', 'member_ban', 'member_unban']
            },
            'file-logs': {
                'emoji': '📎',
                'description': 'All file events',
                'events': ['image_send', 'image_delete']
            },
            'voice-logs': {
                'emoji': '🎵',
                'description': 'All voice events',
                'events': ['voice_join', 'voice_leave', 'voice_move', 'voice_mute', 'voice_deafen', 'voice_stream',
                           'voice_video']
            }
        }

    async def create_logs_category(self, guild: discord.Guild, category_name: str = "📋 Logs") -> Optional[
        discord.CategoryChannel]:
        """Create the main logs category"""
        try:
            # Check if category already exists
            existing_category = discord.utils.get(guild.categories, name=category_name)
            if existing_category:
                logger.info(f"Using existing category: {category_name}")
                return existing_category

            # Create new category
            category = await guild.create_category(
                name=category_name,
                reason="Fenrir logging setup - main logs category"
            )

            # Set permissions (bot can read/write, everyone can read)
            overwrites = {
                guild.default_role: discord.PermissionOverwrite(
                    send_messages=False,
                    add_reactions=False
                ),
                guild.me: discord.PermissionOverwrite(
                    send_messages=True,
                    manage_messages=True,
                    embed_links=True,
                    attach_files=True
                )
            }

            await category.edit(overwrites=overwrites)
            logger.info(f"Created logs category: {category_name}")
            return category

        except discord.Forbidden:
            logger.error("Missing permissions to create category")
            return None
        except Exception as e:
            logger.error(f"Error creating category: {e}")
            return None

    async def create_log_channel(self, guild: discord.Guild, channel_name: str,
                                 description: str, category: Optional[discord.CategoryChannel] = None) -> Optional[
        discord.TextChannel]:
        """Create a single log channel with proper permissions"""
        try:
            # Check if channel already exists
            existing_channel = discord.utils.get(guild.text_channels, name=channel_name)
            if existing_channel:
                logger.info(f"Using existing channel: {channel_name}")
                return existing_channel

            # Set permissions for the channel
            overwrites = {
                guild.default_role: discord.PermissionOverwrite(
                    send_messages=False,
                    add_reactions=False,
                    read_messages=True
                ),
                guild.me: discord.PermissionOverwrite(
                    send_messages=True,
                    manage_messages=True,
                    embed_links=True,
                    attach_files=True,
                    read_messages=True
                )
            }

            # Create channel
            channel = await guild.create_text_channel(
                name=channel_name,
                category=category,
                topic=f"🤖 Fenrir Logs: {description}",
                overwrites=overwrites,
                reason="Fenrir logging setup - automated channel creation"
            )

            logger.info(f"Created log channel: {channel_name}")
            return channel

        except discord.Forbidden:
            logger.error(f"Missing permissions to create channel: {channel_name}")
            return None
        except Exception as e:
            logger.error(f"Error creating channel {channel_name}: {e}")
            return None

    async def setup_granular_channels(self, guild: discord.Guild) -> Dict[str, Any]:
        """Create individual channels for each event type"""
        guild_id = str(guild.id)
        results = {
            'success': True,
            'category': None,
            'channels_created': [],
            'channels_existing': [],
            'events_mapped': [],
            'errors': []
        }

        try:
            # Create main category
            category = await self.create_logs_category(guild)
            if not category:
                results['success'] = False
                results['errors'].append("Failed to create logs category")
                return results

            results['category'] = category

            # Create individual channels for each event
            for event_type, event_info in self.event_definitions.items():
                channel_name = f"{event_info['emoji']}-{event_info['name']}"
                description = event_info['description']

                channel = await self.create_log_channel(guild, channel_name, description, category)

                if channel:
                    # Map event to channel in database
                    await set_event_channel(guild_id, event_type, str(channel.id), channel.name)

                    if channel.name in [c.name for c in results['channels_existing']]:
                        results['channels_existing'].append(channel)
                    else:
                        results['channels_created'].append(channel)

                    results['events_mapped'].append({
                        'event': event_type,
                        'channel': channel.name,
                        'channel_id': channel.id
                    })
                else:
                    results['errors'].append(f"Failed to create channel for {event_type}")
                    results['success'] = False

            # Add a small delay to prevent rate limiting
            if results['channels_created']:
                await asyncio.sleep(1)

        except Exception as e:
            logger.error(f"Error in setup_granular_channels: {e}")
            results['success'] = False
            results['errors'].append(str(e))

        return results

    async def setup_grouped_channels(self, guild: discord.Guild) -> Dict[str, Any]:
        """Create grouped channels for related events"""
        guild_id = str(guild.id)
        results = {
            'success': True,
            'category': None,
            'channels_created': [],
            'channels_existing': [],
            'groups_mapped': [],
            'errors': []
        }

        try:
            # Create main category
            category = await self.create_logs_category(guild)
            if not category:
                results['success'] = False
                results['errors'].append("Failed to create logs category")
                return results

            results['category'] = category

            # Create grouped channels
            for channel_name, group_info in self.grouped_channels.items():
                full_channel_name = f"{group_info['emoji']}-{channel_name}"
                description = group_info['description']

                channel = await self.create_log_channel(guild, full_channel_name, description, category)

                if channel:
                    # Map all events in this group to the channel
                    await set_events_channel(guild_id, group_info['events'], str(channel.id), channel.name)

                    if channel.name in [c.name for c in results['channels_existing']]:
                        results['channels_existing'].append(channel)
                    else:
                        results['channels_created'].append(channel)

                    results['groups_mapped'].append({
                        'group': channel_name,
                        'events': group_info['events'],
                        'channel': channel.name,
                        'channel_id': channel.id,
                        'event_count': len(group_info['events'])
                    })
                else:
                    results['errors'].append(f"Failed to create channel for group {channel_name}")
                    results['success'] = False

            # Add a small delay
            if results['channels_created']:
                await asyncio.sleep(1)

        except Exception as e:
            logger.error(f"Error in setup_grouped_channels: {e}")
            results['success'] = False
            results['errors'].append(str(e))

        return results

    async def setup_custom_channels(self, guild: discord.Guild, custom_mapping: Dict[str, List[str]]) -> Dict[str, Any]:
        """Create custom channel mapping based on user specification"""
        guild_id = str(guild.id)
        results = {
            'success': True,
            'category': None,
            'channels_created': [],
            'channels_existing': [],
            'custom_mappings': [],
            'errors': []
        }

        try:
            # Create main category
            category = await self.create_logs_category(guild)
            if not category:
                results['success'] = False
                results['errors'].append("Failed to create logs category")
                return results

            results['category'] = category

            # Create channels based on custom mapping
            # Format: {"channel-name": ["event1", "event2", ...]}
            for channel_name, event_types in custom_mapping.items():
                # Validate event types
                valid_events = [e for e in event_types if e in self.event_definitions]
                if not valid_events:
                    results['errors'].append(f"No valid events for channel {channel_name}")
                    continue

                # Determine emoji based on primary event group
                primary_group = self.event_definitions[valid_events[0]]['group']
                emoji_map = {
                    'message': '💬',
                    'member': '👥',
                    'file': '📎',
                    'voice': '🎵'
                }
                emoji = emoji_map.get(primary_group, '📋')

                full_channel_name = f"{emoji}-{channel_name}"
                description = f"Custom logs: {', '.join(valid_events)}"

                channel = await self.create_log_channel(guild, full_channel_name, description, category)

                if channel:
                    # Map events to channel
                    await set_events_channel(guild_id, valid_events, str(channel.id), channel.name)

                    if channel.name in [c.name for c in results['channels_existing']]:
                        results['channels_existing'].append(channel)
                    else:
                        results['channels_created'].append(channel)

                    results['custom_mappings'].append({
                        'channel': channel.name,
                        'channel_id': channel.id,
                        'events': valid_events,
                        'event_count': len(valid_events)
                    })
                else:
                    results['errors'].append(f"Failed to create channel {channel_name}")
                    results['success'] = False

        except Exception as e:
            logger.error(f"Error in setup_custom_channels: {e}")
            results['success'] = False
            results['errors'].append(str(e))

        return results

    async def send_welcome_messages(self, results: Dict[str, Any], setup_type: str):
        """Send welcome messages to newly created channels"""
        try:
            created_channels = results.get('channels_created', [])

            for channel in created_channels:
                embed = discord.Embed(
                    title="🤖 Fenrir Logging Channel",
                    description=f"This channel has been set up for {setup_type} logging.",
                    color=discord.Color.blue()
                )

                embed.add_field(
                    name="📋 Purpose",
                    value=channel.topic or "Automated logging",
                    inline=False
                )

                embed.add_field(
                    name="⚙️ Setup Type",
                    value=setup_type.title(),
                    inline=True
                )

                embed.add_field(
                    name="🔧 Management",
                    value="Use `/log_channels_list` to see all mappings",
                    inline=True
                )

                embed.set_footer(text="Fenrir Advanced Logging System")

                try:
                    await channel.send(embed=embed)
                    await asyncio.sleep(0.5)  # Small delay between messages
                except:
                    logger.warning(f"Could not send welcome message to {channel.name}")

        except Exception as e:
            logger.error(f"Error sending welcome messages: {e}")

    def get_available_events(self) -> List[str]:
        """Get list of all available event types"""
        return list(self.event_definitions.keys())

    def get_event_info(self, event_type: str) -> Optional[Dict[str, Any]]:
        """Get information about a specific event type"""
        return self.event_definitions.get(event_type)

    def get_grouped_mapping(self) -> Dict[str, List[str]]:
        """Get the default grouped channel mapping"""
        return {name: info['events'] for name, info in self.grouped_channels.items()}

    def validate_custom_mapping(self, custom_mapping: Dict[str, List[str]]) -> Dict[str, Any]:
        """Validate a custom channel mapping"""
        validation = {
            'valid': True,
            'errors': [],
            'warnings': [],
            'total_channels': len(custom_mapping),
            'total_events': 0,
            'unmapped_events': []
        }

        available_events = set(self.event_definitions.keys())
        mapped_events = set()

        for channel_name, events in custom_mapping.items():
            if not events:
                validation['errors'].append(f"Channel '{channel_name}' has no events")
                validation['valid'] = False
                continue

            for event in events:
                if event not in available_events:
                    validation['errors'].append(f"Unknown event type: {event}")
                    validation['valid'] = False
                else:
                    mapped_events.add(event)

            validation['total_events'] += len(events)

        # Check for unmapped events
        validation['unmapped_events'] = list(available_events - mapped_events)
        if validation['unmapped_events']:
            validation['warnings'].append(f"Unmapped events: {', '.join(validation['unmapped_events'])}")

        return validation


# Global instance
channel_manager = None


def get_channel_manager(bot) -> ChannelManager:
    """Get or create the global channel manager instance"""
    global channel_manager
    if channel_manager is None:
        channel_manager = ChannelManager(bot)
    return channel_manager