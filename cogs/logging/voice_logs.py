"""
Voice Logging Module - cogs/logging/voice_logs.py
Handles voice channel activity tracking with session duration monitoring
"""

import discord
from discord.ext import commands, tasks
import logging
from datetime import datetime, timedelta
from typing import Dict, Optional, Any

from .base import LoggingModule
from utils.bot_logger import log_event, log_member

logger = logging.getLogger(__name__)


class VoiceLogs(LoggingModule):
    """Handles voice channel activity logging and session tracking"""

    def __init__(self, bot):
        super().__init__(bot)

        # Define event types this module handles
        self.event_types = {
            'voice_join': 'Voice Channel Joins',
            'voice_leave': 'Voice Channel Leaves',
            'voice_move': 'Voice Channel Moves',
            'voice_mute': 'Voice Mute/Unmute',
            'voice_deafen': 'Voice Deafen/Undeafen',
            'voice_stream': 'Voice Streaming',
            'voice_video': 'Voice Video/Camera'
        }

        # Track active voice sessions for duration calculation
        self.active_sessions: Dict[int, Dict[str, Any]] = {}

        # Track voice statistics
        self.voice_stats = {
            'total_joins': 0,
            'total_leaves': 0,
            'total_moves': 0,
            'active_users': set()
        }

    async def setup(self):
        """Setup method called when module is loaded"""
        logger.info("Voice logging module initialized")

        # Start cleanup task for stale sessions
        self.cleanup_stale_sessions.start()

    async def teardown(self):
        """Teardown method called when module is unloaded"""
        if self.cleanup_stale_sessions.is_running():
            self.cleanup_stale_sessions.cancel()

        # End all active sessions
        await self.end_all_sessions("Bot shutdown")

    @tasks.loop(minutes=30)
    async def cleanup_stale_sessions(self):
        """Enhanced cleanup with better error handling and validation"""
        try:
            current_time = datetime.utcnow()
            stale_sessions = []
            validation_errors = []

            # CHANGE: Fix the logic flow so all checks can run
            for user_id, session in list(self.active_sessions.items()):
                should_cleanup = False
                cleanup_reason = ""

                try:
                    # Validate session data integrity first
                    if not isinstance(session, dict) or 'start_time' not in session:
                        validation_errors.append(f"Invalid session data for user {user_id}")
                        should_cleanup = True
                        cleanup_reason = "Invalid session data"

                    # Check if session is too old (6 hours) - but don't continue yet
                    elif (current_time - session['start_time']) > timedelta(hours=6):
                        should_cleanup = True
                        cleanup_reason = f"Session too old ({current_time - session['start_time']})"

                    # Only check voice status if session isn't already marked for cleanup
                    elif not should_cleanup:
                        # Validate member still exists and is in voice
                        member = session.get('member')
                        if not member:
                            should_cleanup = True
                            cleanup_reason = "Missing member object"
                        else:
                            # FIXED: This check can now actually run
                            try:
                                if not member.voice or not member.voice.channel:
                                    should_cleanup = True
                                    cleanup_reason = "Member no longer in voice"
                            except AttributeError:
                                # Member object is stale/invalid
                                should_cleanup = True
                                cleanup_reason = "Stale member object"

                    # Add to cleanup list if needed
                    if should_cleanup:
                        stale_sessions.append((user_id, cleanup_reason))

                except Exception as session_error:
                    logger.error(f"Error validating session for user {user_id}: {session_error}")
                    stale_sessions.append((user_id, f"Validation error: {session_error}"))

            # Clean up identified stale sessions
            cleanup_results = {'success': 0, 'errors': 0}
            for user_id, reason in stale_sessions:
                try:
                    await self.end_session(user_id, f"Cleanup: {reason}")
                    cleanup_results['success'] += 1
                    logger.debug(f"Cleaned up session for user {user_id}: {reason}")
                except Exception as cleanup_error:
                    logger.error(f"Error cleaning up session for user {user_id}: {cleanup_error}")
                    cleanup_results['errors'] += 1

            # Log cleanup summary
            if stale_sessions:
                logger.info(
                    f"Session cleanup complete: {cleanup_results['success']} cleaned, {cleanup_results['errors']} errors")

            if validation_errors:
                logger.warning(f"Session validation issues: {len(validation_errors)} problems")

        except Exception as e:
            logger.error(f"Critical error in cleanup_stale_sessions: {e}")

    async def on_voice_state_update(self, member, before, after):
        """Handle all voice state changes"""
        # Skip bot voice state changes (unless it's our own bot for debugging)
        if member.bot and member != self.bot.user:
            return

        guild_id = str(member.guild.id)

        # Handle different voice state transitions
        if before.channel is None and after.channel is not None:
            # User joined voice channel
            await self.handle_voice_join(member, after.channel, guild_id)

        elif before.channel is not None and after.channel is None:
            # User left voice channel
            await self.handle_voice_leave(member, before.channel, guild_id)

        elif before.channel != after.channel and before.channel is not None and after.channel is not None:
            # User moved between voice channels
            await self.handle_voice_move(member, before.channel, after.channel, guild_id)

        # Handle mute state changes
        if before.self_mute != after.self_mute:
            await self.handle_mute_change(member, after.channel, after.self_mute, "self_mute", guild_id)

        if before.mute != after.mute:
            await self.handle_mute_change(member, after.channel, after.mute, "server_mute", guild_id)

        # Handle deafen state changes
        if before.self_deaf != after.self_deaf:
            await self.handle_deafen_change(member, after.channel, after.self_deaf, "self_deafen", guild_id)

        if before.deaf != after.deaf:
            await self.handle_deafen_change(member, after.channel, after.deaf, "server_deafen", guild_id)

        # Handle streaming state changes
        if before.self_stream != after.self_stream:
            await self.handle_stream_change(member, after.channel, after.self_stream, guild_id)

        # Handle video state changes
        if before.self_video != after.self_video:
            await self.handle_video_change(member, after.channel, after.self_video, guild_id)

    async def handle_voice_join(self, member, channel, guild_id):
        """Handle user joining voice channel"""
        if not await self.base.check_logging_enabled(guild_id, 'voice_join'):
            return

        logger.info(f"🎵 {member} joined voice channel {channel.name} in {member.guild.name}")

        # Start tracking session
        await self.start_session(member, channel)

        # Create embed for voice join
        embed = discord.Embed(
            title="🎵 Voice Channel Joined",
            color=discord.Color.green()
        )

        self.base.add_user_info(embed, member, "Member")

        embed.add_field(
            name="Channel",
            value=f"🔊 {channel.name}",
            inline=True
        )

        embed.add_field(
            name="Channel Type",
            value=self.get_channel_type(channel),
            inline=True
        )

        embed.add_field(
            name="Current Users",
            value=f"{len(channel.members)} members",
            inline=True
        )

        # Show other users in channel
        if len(channel.members) > 1:
            other_users = [m.display_name for m in channel.members if m != member]
            if len(other_users) <= 5:
                embed.add_field(
                    name="Also in Channel",
                    value=", ".join(other_users),
                    inline=False
                )
            else:
                embed.add_field(
                    name="Also in Channel",
                    value=f"{', '.join(other_users[:5])} and {len(other_users) - 5} more",
                    inline=False
                )

        # Add join timestamp
        embed.add_field(
            name="🕒 Joined At",
            value=f"<t:{int(datetime.utcnow().timestamp())}:F>",
            inline=True
        )

        # Add avatar if enabled
        add_avatar = self.base.add_guild_avatar(embed, member, guild_id)
        await add_avatar()

        await self.base.send_log(member.guild, 'voice_join', embed)

        # Update statistics
        self.voice_stats['total_joins'] += 1
        self.voice_stats['active_users'].add(member.id)

        # Log to interaction logger
        log_member(member, "voice_join", {
            'channel': channel.name,
            'channel_id': channel.id,
            'channel_members': len(channel.members),
            'channel_type': str(channel.type)
        })

    async def handle_voice_leave(self, member, channel, guild_id):
        """Handle user leaving voice channel"""
        if not await self.base.check_logging_enabled(guild_id, 'voice_leave'):
            return

        logger.info(f"🎵 {member} left voice channel {channel.name} in {member.guild.name}")

        # End session and get duration
        session_data = await self.end_session(member.id, "User left channel")

        # Create embed for voice leave
        embed = discord.Embed(
            title="🎵 Voice Channel Left",
            color=discord.Color.red()
        )

        self.base.add_user_info(embed, member, "Member")

        embed.add_field(
            name="Channel",
            value=f"🔊 {channel.name}",
            inline=True
        )

        embed.add_field(
            name="Remaining Users",
            value=f"{len(channel.members)} members",
            inline=True
        )

        # Add session duration if available
        if session_data and session_data.get('duration'):
            duration = session_data['duration']
            embed.add_field(
                name="⏱️ Session Duration",
                value=self.format_duration(duration),
                inline=True
            )

        # Add leave timestamp
        embed.add_field(
            name="🕒 Left At",
            value=f"<t:{int(datetime.utcnow().timestamp())}:F>",
            inline=True
        )

        # Add avatar if enabled
        add_avatar = self.base.add_guild_avatar(embed, member, guild_id)
        await add_avatar()

        await self.base.send_log(member.guild, 'voice_leave', embed)

        # Update statistics
        self.voice_stats['total_leaves'] += 1
        self.voice_stats['active_users'].discard(member.id)

        # Log to interaction logger
        log_member(member, "voice_leave", {
            'channel': channel.name,
            'channel_id': channel.id,
            'session_duration_seconds': session_data.get('duration_seconds', 0) if session_data else 0,
            'remaining_members': len(channel.members)
        })

    async def handle_voice_move(self, member, from_channel, to_channel, guild_id):
        """Handle user moving between voice channels"""
        if not await self.base.check_logging_enabled(guild_id, 'voice_move'):
            return

        logger.info(f"🎵 {member} moved from {from_channel.name} to {to_channel.name}")

        # Update session with new channel
        if member.id in self.active_sessions:
            self.active_sessions[member.id]['channel'] = to_channel
            self.active_sessions[member.id]['moves'] += 1

        # Create embed for voice move
        embed = discord.Embed(
            title="🎵 Voice Channel Moved",
            color=discord.Color.orange()
        )

        self.base.add_user_info(embed, member, "Member")

        embed.add_field(
            name="From",
            value=f"🔊 {from_channel.name}",
            inline=True
        )

        embed.add_field(
            name="To",
            value=f"🔊 {to_channel.name}",
            inline=True
        )

        embed.add_field(
            name="Move Type",
            value=self.get_move_type(from_channel, to_channel),
            inline=True
        )

        # Show users in destination channel
        embed.add_field(
            name="Users in Destination",
            value=f"{len(to_channel.members)} members",
            inline=True
        )

        # Add move timestamp
        embed.add_field(
            name="🕒 Moved At",
            value=f"<t:{int(datetime.utcnow().timestamp())}:F>",
            inline=True
        )

        # Add avatar if enabled
        add_avatar = self.base.add_guild_avatar(embed, member, guild_id)
        await add_avatar()

        await self.base.send_log(member.guild, 'voice_move', embed)

        # Update statistics
        self.voice_stats['total_moves'] += 1

        # Log to interaction logger
        log_member(member, "voice_move", {
            'from_channel': from_channel.name,
            'to_channel': to_channel.name,
            'from_channel_id': from_channel.id,
            'to_channel_id': to_channel.id
        })

    async def handle_mute_change(self, member, channel, is_muted, mute_type, guild_id):
        """Handle mute/unmute state changes"""
        if not await self.base.check_logging_enabled(guild_id, 'voice_mute'):
            return

        if not channel:  # User not in voice channel
            return

        action = "muted" if is_muted else "unmuted"
        mute_source = "Self" if mute_type.startswith("self") else "Server"

        logger.info(f"🎵 {member} {action} ({mute_type}) in {channel.name}")

        # Create embed for mute change
        embed = discord.Embed(
            title=f"🎵 Voice {mute_source} {action.title()}",
            color=discord.Color.orange() if is_muted else discord.Color.green()
        )

        self.base.add_user_info(embed, member, "Member")

        embed.add_field(
            name="Channel",
            value=f"🔊 {channel.name}",
            inline=True
        )

        embed.add_field(
            name="Action",
            value=f"🔇 {mute_source} {action}",
            inline=True
        )

        embed.add_field(
            name="🕒 Changed At",
            value=f"<t:{int(datetime.utcnow().timestamp())}:F>",
            inline=True
        )

        # Add avatar if enabled
        add_avatar = self.base.add_guild_avatar(embed, member, guild_id)
        await add_avatar()

        await self.base.send_log(member.guild, 'voice_mute', embed)

        # Log to interaction logger
        log_event("voice_mute_change", {
            'user_id': member.id,
            'guild_id': member.guild.id,
            'channel': channel.name,
            'mute_type': mute_type,
            'is_muted': is_muted,
            'action': action
        })

    async def handle_deafen_change(self, member, channel, is_deafened, deafen_type, guild_id):
        """Handle deafen/undeafen state changes"""
        if not await self.base.check_logging_enabled(guild_id, 'voice_deafen'):
            return

        if not channel:  # User not in voice channel
            return

        action = "deafened" if is_deafened else "undeafened"
        deafen_source = "Self" if deafen_type.startswith("self") else "Server"

        logger.info(f"🎵 {member} {action} ({deafen_type}) in {channel.name}")

        # Create embed for deafen change
        embed = discord.Embed(
            title=f"🎵 Voice {deafen_source} {action.title()}",
            color=discord.Color.red() if is_deafened else discord.Color.green()
        )

        self.base.add_user_info(embed, member, "Member")

        embed.add_field(
            name="Channel",
            value=f"🔊 {channel.name}",
            inline=True
        )

        embed.add_field(
            name="Action",
            value=f"🔇 {deafen_source} {action}",
            inline=True
        )

        embed.add_field(
            name="🕒 Changed At",
            value=f"<t:{int(datetime.utcnow().timestamp())}:F>",
            inline=True
        )

        # Add avatar if enabled
        add_avatar = self.base.add_guild_avatar(embed, member, guild_id)
        await add_avatar()

        await self.base.send_log(member.guild, 'voice_deafen', embed)

        # Log to interaction logger
        log_event("voice_deafen_change", {
            'user_id': member.id,
            'guild_id': member.guild.id,
            'channel': channel.name,
            'deafen_type': deafen_type,
            'is_deafened': is_deafened,
            'action': action
        })

    async def handle_stream_change(self, member, channel, is_streaming, guild_id):
        """Handle streaming state changes"""
        if not await self.base.check_logging_enabled(guild_id, 'voice_stream'):
            return

        if not channel:  # User not in voice channel
            return

        action = "started streaming" if is_streaming else "stopped streaming"

        logger.info(f"🎵 {member} {action} in {channel.name}")

        # Create embed for stream change
        embed = discord.Embed(
            title=f"🎵 Voice Streaming {action.split()[-1].title()}",
            color=discord.Color.purple() if is_streaming else discord.Color.blue()
        )

        self.base.add_user_info(embed, member, "Member")

        embed.add_field(
            name="Channel",
            value=f"🔊 {channel.name}",
            inline=True
        )

        embed.add_field(
            name="Action",
            value=f"📹 {action}",
            inline=True
        )

        embed.add_field(
            name="🕒 Changed At",
            value=f"<t:{int(datetime.utcnow().timestamp())}:F>",
            inline=True
        )

        # Add avatar if enabled
        add_avatar = self.base.add_guild_avatar(embed, member, guild_id)
        await add_avatar()

        await self.base.send_log(member.guild, 'voice_stream', embed)

        # Log to interaction logger
        log_event("voice_stream_change", {
            'user_id': member.id,
            'guild_id': member.guild.id,
            'channel': channel.name,
            'is_streaming': is_streaming,
            'action': action
        })

    async def handle_video_change(self, member, channel, is_video, guild_id):
        """Handle video/camera state changes"""
        if not await self.base.check_logging_enabled(guild_id, 'voice_video'):
            return

        if not channel:  # User not in voice channel
            return

        action = "enabled camera" if is_video else "disabled camera"

        logger.info(f"🎵 {member} {action} in {channel.name}")

        # Create embed for video change
        embed = discord.Embed(
            title=f"🎵 Voice Camera {action.split()[-1].title()}",
            color=discord.Color.green() if is_video else discord.Color.red()
        )

        self.base.add_user_info(embed, member, "Member")

        embed.add_field(
            name="Channel",
            value=f"🔊 {channel.name}",
            inline=True
        )

        embed.add_field(
            name="Action",
            value=f"📷 {action}",
            inline=True
        )

        embed.add_field(
            name="🕒 Changed At",
            value=f"<t:{int(datetime.utcnow().timestamp())}:F>",
            inline=True
        )

        # Add avatar if enabled
        add_avatar = self.base.add_guild_avatar(embed, member, guild_id)
        await add_avatar()

        await self.base.send_log(member.guild, 'voice_video', embed)

        # Log to interaction logger
        log_event("voice_video_change", {
            'user_id': member.id,
            'guild_id': member.guild.id,
            'channel': channel.name,
            'is_video': is_video,
            'action': action
        })

    async def start_session(self, member, channel):
        """Start tracking a voice session"""
        self.active_sessions[member.id] = {
            'member': member,
            'channel': channel,
            'start_time': datetime.utcnow(),
            'guild_id': member.guild.id,
            'moves': 0
        }

        logger.debug(f"Started voice session for {member} in {channel.name}")

    async def end_session(self, user_id, reason="Unknown"):
        """End a voice session and return session data"""
        if user_id not in self.active_sessions:
            return None

        session = self.active_sessions.pop(user_id)
        end_time = datetime.utcnow()
        duration = end_time - session['start_time']

        session_data = {
            'duration': duration,
            'duration_seconds': duration.total_seconds(),
            'start_time': session['start_time'],
            'end_time': end_time,
            'channel': session['channel'],
            'moves': session.get('moves', 0),
            'reason': reason
        }

        logger.debug(f"Ended voice session for user {user_id}: {self.format_duration(duration)} ({reason})")

        # Log session data for analytics
        log_event("voice_session_ended", {
            'user_id': user_id,
            'guild_id': session['guild_id'],
            'duration_seconds': duration.total_seconds(),
            'duration_minutes': round(duration.total_seconds() / 60, 1),
            'channel_moves': session.get('moves', 0),
            'reason': reason
        })

        return session_data

    async def end_all_sessions(self, reason="Bot shutdown"):
        """End all active voice sessions"""
        for user_id in list(self.active_sessions.keys()):
            await self.end_session(user_id, reason)

    def get_channel_type(self, channel):
        """Get readable channel type"""
        if channel.type == discord.ChannelType.voice:
            return "Voice Channel"
        elif channel.type == discord.ChannelType.stage_voice:
            return "Stage Channel"
        else:
            return str(channel.type).title()

    def get_move_type(self, from_channel, to_channel):
        """Determine the type of voice channel move"""
        if from_channel.category != to_channel.category:
            return "Category Change"
        elif from_channel.type != to_channel.type:
            return "Channel Type Change"
        else:
            return "Channel Switch"

    def format_duration(self, duration):
        """Format duration in human-readable format"""
        total_seconds = int(duration.total_seconds())
        hours = total_seconds // 3600
        minutes = (total_seconds % 3600) // 60
        seconds = total_seconds % 60

        if hours > 0:
            return f"{hours}h {minutes}m {seconds}s"
        elif minutes > 0:
            return f"{minutes}m {seconds}s"
        else:
            return f"{seconds}s"

    async def get_voice_statistics(self, guild_id: str, days: int = 7):
        """Get voice activity statistics for a guild"""
        # This will be expanded with database queries in future weeks
        stats = {
            'joins_tracked': self.voice_stats['total_joins'],
            'leaves_tracked': self.voice_stats['total_leaves'],
            'moves_tracked': self.voice_stats['total_moves'],
            'currently_active': len(self.active_sessions),
            'active_users': len(self.voice_stats['active_users']),
            'period_days': days
        }

        return stats

    def get_active_sessions_info(self):
        """Get information about currently active voice sessions"""
        sessions_info = []
        current_time = datetime.utcnow()

        for user_id, session in self.active_sessions.items():
            duration = current_time - session['start_time']
            sessions_info.append({
                'user_id': user_id,
                'member': session['member'],
                'channel': session['channel'],
                'duration': self.format_duration(duration),
                'duration_seconds': duration.total_seconds(),
                'moves': session.get('moves', 0)
            })

        return sorted(sessions_info, key=lambda x: x['duration_seconds'], reverse=True)