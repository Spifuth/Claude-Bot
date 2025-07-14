"""
Core Commands Cog - Enhanced with Interaction Logging
Immediate response with comprehensive logging of all interactions
"""

import discord
from discord.ext import commands
from discord import app_commands
import logging
import asyncio
import time

from utils.embeds import EmbedBuilder
from utils.bot_logger import log_command, log_error, log_event, debug_dump, get_bot_logger

logger = logging.getLogger(__name__)

class CoreCommands(commands.Cog):
    """Core bot commands with comprehensive interaction logging"""

    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="ping", description="Check if Fenrir is alive")
    async def ping(self, interaction: discord.Interaction):
        """Simple ping command with detailed logging"""
        start_time = time.time()

        # Log command start
        log_event("ping_command_started", {
            'user': f"{interaction.user} ({interaction.user.id})",
            'guild': f"{interaction.guild.name} ({interaction.guild.id})" if interaction.guild else "DM"
        })

        # IMMEDIATE response - no processing before this
        await interaction.response.send_message("🏓 Pong! Calculating latency...", ephemeral=True)

        try:
            # Calculate latencies
            websocket_latency = round(self.bot.latency * 1000)
            api_start = time.time()

            # Create enhanced embed with more info
            embed = EmbedBuilder.success("Pong!", f"🏓 WebSocket Latency: {websocket_latency}ms")

            # Calculate API response time
            api_response_time = round((time.time() - api_start) * 1000)
            embed.add_field(name="API Response", value=f"{api_response_time}ms", inline=True)

            # Add bot info
            embed.add_field(name="Status", value="🟢 Online", inline=True)
            embed.add_field(name="Guilds", value=len(self.bot.guilds), inline=True)

            # Update the response
            await interaction.edit_original_response(content=None, embed=embed)

            # Calculate total execution time
            execution_time = time.time() - start_time

            # Log successful command execution with detailed metrics
            log_command(interaction, "ping", {
                'websocket_latency_ms': websocket_latency,
                'api_response_time_ms': api_response_time,
                'total_guilds': len(self.bot.guilds)
            }, execution_time)

            # Log additional ping metrics
            log_event("ping_metrics", {
                'websocket_latency': websocket_latency,
                'api_response_time': api_response_time,
                'execution_time_ms': round(execution_time * 1000, 2),
                'bot_guilds': len(self.bot.guilds),
                'bot_users': len(self.bot.users)
            })

        except Exception as e:
            logger.error(f"Error in ping command: {e}")
            log_error(e, "Ping command execution failed", interaction)
            await interaction.edit_original_response(content="❌ Error calculating latency")

    @app_commands.command(name="status", description="Check Fenrir's detailed status")
    async def status(self, interaction: discord.Interaction):
        """Enhanced status command with comprehensive logging"""
        start_time = time.time()

        # Log status command initiation
        log_event("status_command_started", {
            'user': f"{interaction.user} ({interaction.user.id})",
            'requested_from': f"{interaction.guild.name}" if interaction.guild else "DM"
        })

        # IMMEDIATE response
        await interaction.response.send_message("🔄 Gathering comprehensive bot status...", ephemeral=True)

        try:
            # Gather detailed bot statistics
            bot_stats = {
                'guilds': len(self.bot.guilds),
                'users': len(self.bot.users),
                'channels': sum(len(guild.channels) for guild in self.bot.guilds),
                'commands': len(self.bot.tree.get_commands()),
                'cogs_loaded': len(self.bot.cogs),
                'latency_ms': round(self.bot.latency * 1000),
                'memory_usage': self._get_memory_usage()
            }

            # Log collected statistics
            debug_dump(bot_stats, "Bot Status Statistics")

            embed = discord.Embed(
                title="🐺 Fenrir Comprehensive Status",
                description="Complete bot health and statistics",
                color=discord.Color.blue()
            )

            # Basic status
            embed.add_field(name="🔋 Bot Status", value="🟢 Online & Responsive", inline=True)
            embed.add_field(name="📊 Latency", value=f"{bot_stats['latency_ms']}ms", inline=True)
            embed.add_field(name="💾 Memory", value=f"{bot_stats['memory_usage']:.1f} MB", inline=True)

            # Scale information
            embed.add_field(name="🏰 Guilds", value=bot_stats['guilds'], inline=True)
            embed.add_field(name="👥 Users", value=f"{bot_stats['users']:,}", inline=True)
            embed.add_field(name="📺 Channels", value=f"{bot_stats['channels']:,}", inline=True)

            # Bot capabilities
            embed.add_field(name="⚡ Commands", value=bot_stats['commands'], inline=True)
            embed.add_field(name="🔧 Loaded Cogs", value=bot_stats['cogs_loaded'], inline=True)

            # Session statistics (if available)
            bot_logger = get_bot_logger()
            if bot_logger:
                session_stats = bot_logger.stats
                embed.add_field(
                    name="📈 Session Stats",
                    value=f"Commands: {session_stats['commands_executed']}\n"
                          f"Events: {session_stats['events_received']}\n"
                          f"Errors: {session_stats['errors_encountered']}",
                    inline=True
                )

            # Show enabled modules
            enabled_modules = []
            for module, enabled in self.bot.config.MODULES_ENABLED.items():
                status_emoji = "🟢" if enabled else "🔴"
                enabled_modules.append(f"{status_emoji} {module.title()}")

            if enabled_modules:
                embed.add_field(
                    name="🔧 Modules",
                    value="\n".join(enabled_modules),
                    inline=False
                )

            # Add performance indicator
            if bot_stats['latency_ms'] < 100:
                performance = "🟢 Excellent"
            elif bot_stats['latency_ms'] < 200:
                performance = "🟡 Good"
            else:
                performance = "🔴 Needs Attention"

            embed.add_field(name="⚡ Performance", value=performance, inline=True)

            # Add bot avatar
            if self.bot.user.avatar:
                embed.set_thumbnail(url=self.bot.user.avatar.url)

            # Calculate execution time
            execution_time = time.time() - start_time
            embed.set_footer(text=f"Status generated in {execution_time:.2f}s")

            await interaction.edit_original_response(content=None, embed=embed)

            # Log successful status command with all gathered data
            log_command(interaction, "status", bot_stats, execution_time)

            log_event("status_metrics_collected", {
                **bot_stats,
                'execution_time_ms': round(execution_time * 1000, 2),
                'performance_rating': performance
            })

        except Exception as e:
            logger.error(f"Error in status command: {e}")
            log_error(e, "Status command execution failed", interaction)
            await interaction.edit_original_response(content="❌ Error getting bot status")

    @app_commands.command(name="bot_info", description="Get detailed information about Fenrir")
    async def info_command(self, interaction: discord.Interaction):
        """Enhanced bot info with logging"""
        start_time = time.time()

        log_event("bot_info_requested", {
            'user': f"{interaction.user} ({interaction.user.id})",
            'guild': f"{interaction.guild.name} ({interaction.guild.id})" if interaction.guild else "DM"
        })

        await interaction.response.send_message("📊 Gathering comprehensive bot information...", ephemeral=True)

        try:
            # Collect comprehensive bot information
            bot_info = {
                'name': self.bot.user.name,
                'id': self.bot.user.id,
                'discriminator': self.bot.user.discriminator,
                'created_at': self.bot.user.created_at.isoformat(),
                'avatar_url': str(self.bot.user.avatar.url) if self.bot.user.avatar else None,
                'guild_count': len(self.bot.guilds),
                'user_count': len(self.bot.users),
                'command_count': len(self.bot.tree.get_commands()),
                'cog_count': len(self.bot.cogs),
                'latency_ms': round(self.bot.latency * 1000),
                'discord_py_version': discord.__version__,
                'python_version': f"{__import__('sys').version_info.major}.{__import__('sys').version_info.minor}",
                'uptime_seconds': (time.time() - getattr(self.bot, '_start_time', time.time()))
            }

            # Log the collected information
            debug_dump(bot_info, "Comprehensive Bot Information")

            embed = discord.Embed(
                title="🐺 Fenrir Bot - Complete Information",
                description="Comprehensive bot details and statistics",
                color=discord.Color.gold()
            )

            # Bot identity
            embed.add_field(name="🤖 Bot Name", value=bot_info['name'], inline=True)
            embed.add_field(name="🆔 Bot ID", value=bot_info['id'], inline=True)
            embed.add_field(name="📊 Latency", value=f"{bot_info['latency_ms']}ms", inline=True)

            # Scale metrics
            embed.add_field(name="🏰 Guilds", value=f"{bot_info['guild_count']:,}", inline=True)
            embed.add_field(name="👥 Users", value=f"{bot_info['user_count']:,}", inline=True)
            embed.add_field(name="⚡ Commands", value=bot_info['command_count'], inline=True)

            # Technical details
            embed.add_field(name="🐍 Python", value=bot_info['python_version'], inline=True)
            embed.add_field(name="📦 Discord.py", value=bot_info['discord_py_version'], inline=True)
            embed.add_field(name="🔧 Loaded Cogs", value=bot_info['cog_count'], inline=True)

            # Module status
            enabled_modules = []
            for module, enabled in self.bot.config.MODULES_ENABLED.items():
                status_emoji = "🟢" if enabled else "🔴"
                enabled_modules.append(f"{status_emoji} {module.title()}")

            if enabled_modules:
                embed.add_field(
                    name="🔧 Modules Status",
                    value="\n".join(enabled_modules),
                    inline=False
                )

            # Loaded cogs details
            loaded_cogs = []
            for cog_name, cog in self.bot.cogs.items():
                command_count = len([cmd for cmd in cog.get_app_commands()])
                loaded_cogs.append(f"• {cog_name}: {command_count} commands")

            if loaded_cogs:
                embed.add_field(
                    name="📦 Cog Details",
                    value="\n".join(loaded_cogs),
                    inline=False
                )

            # Session statistics
            bot_logger = get_bot_logger()
            if bot_logger:
                session_stats = bot_logger.stats
                session_duration = time.time() - session_stats['session_start'].timestamp()
                embed.add_field(
                    name="📈 Current Session",
                    value=f"⏰ Uptime: {self._format_duration(session_duration)}\n"
                          f"⚡ Commands Run: {session_stats['commands_executed']}\n"
                          f"📡 Events Received: {session_stats['events_received']}\n"
                          f"📤 API Calls: {session_stats['api_calls_sent']}\n"
                          f"💥 Errors: {session_stats['errors_encountered']}",
                    inline=False
                )

            # Add bot avatar
            if self.bot.user.avatar:
                embed.set_thumbnail(url=self.bot.user.avatar.url)

            execution_time = time.time() - start_time
            embed.set_footer(text=f"Information gathered in {execution_time:.2f}s • Discord.py v{discord.__version__}")

            await interaction.edit_original_response(content=None, embed=embed)

            # Log the successful info command
            log_command(interaction, "bot_info", {
                'info_collected': True,
                'data_points': len(bot_info),
                'modules_checked': len(self.bot.config.MODULES_ENABLED),
                'cogs_analyzed': len(self.bot.cogs)
            }, execution_time)

        except Exception as e:
            logger.error(f"Error in bot_info command: {e}")
            log_error(e, "Bot info command execution failed", interaction)
            await interaction.edit_original_response(content="❌ Error getting bot information")

    @app_commands.command(name="help", description="Get help with Fenrir commands")
    async def help_command(self, interaction: discord.Interaction):
        """Enhanced help command with logging"""
        start_time = time.time()

        log_event("help_requested", {
            'user': f"{interaction.user} ({interaction.user.id})",
            'guild': f"{interaction.guild.name} ({interaction.guild.id})" if interaction.guild else "DM"
        })

        await interaction.response.send_message("📚 Loading comprehensive help information...", ephemeral=True)

        try:
            # Collect help information
            help_data = {
                'total_cogs': len(self.bot.cogs),
                'total_commands': 0,
                'cog_commands': {}
            }

            embed = discord.Embed(
                title="🐺 Fenrir Help & Commands",
                description="Complete command reference organized by category",
                color=discord.Color.blue()
            )

            # Group commands by cog
            for cog_name, cog in self.bot.cogs.items():
                commands = [cmd for cmd in cog.get_app_commands()]
                if commands:
                    help_data['cog_commands'][cog_name] = len(commands)
                    help_data['total_commands'] += len(commands)

                    command_list = [f"`/{cmd.name}` - {cmd.description}" for cmd in commands]

                    # Split long lists to avoid embed limits
                    if len(command_list) <= 5:
                        embed.add_field(
                            name=f"{cog_name} Commands ({len(commands)})",
                            value="\n".join(command_list),
                            inline=False
                        )
                    else:
                        # Show first 5 commands
                        embed.add_field(
                            name=f"{cog_name} Commands ({len(commands)})",
                            value="\n".join(command_list[:5]),
                            inline=False
                        )
                        embed.add_field(
                            name="",
                            value=f"... and {len(command_list) - 5} more commands",
                            inline=False
                        )

            # Add usage statistics
            embed.add_field(
                name="📊 Command Statistics",
                value=f"Total Commands: {help_data['total_commands']}\n"
                      f"Command Categories: {help_data['total_cogs']}\n"
                      f"Available Modules: {len([m for m, e in self.bot.config.MODULES_ENABLED.items() if e])}",
                inline=False
            )

            embed.set_footer(text="💡 Use /bot_info for detailed bot information • Use /status for health metrics")

            execution_time = time.time() - start_time

            await interaction.edit_original_response(content=None, embed=embed)

            # Log help command with collected data
            log_command(interaction, "help", help_data, execution_time)

            log_event("help_data_generated", {
                **help_data,
                'execution_time_ms': round(execution_time * 1000, 2)
            })

        except Exception as e:
            logger.error(f"Error in help command: {e}")
            log_error(e, "Help command execution failed", interaction)
            await interaction.edit_original_response(content="❌ Error loading help information")

    def _get_memory_usage(self) -> float:
        """Get current memory usage in MB"""
        try:
            import psutil
            import os
            process = psutil.Process(os.getpid())
            return process.memory_info().rss / 1024 / 1024
        except ImportError:
            return 0.0

    def _format_duration(self, seconds: float) -> str:
        """Format duration in human readable format"""
        if seconds < 60:
            return f"{int(seconds)}s"
        elif seconds < 3600:
            return f"{int(seconds // 60)}m {int(seconds % 60)}s"
        else:
            hours = int(seconds // 3600)
            minutes = int((seconds % 3600) // 60)
            return f"{hours}h {minutes}m"

async def setup(bot):
    """Setup function for the cog"""
    await bot.add_cog(CoreCommands(bot))
    logger.info("Enhanced core commands cog loaded with interaction logging")

    # Log cog loading
    log_event("cog_loaded", {
        'cog_name': 'CoreCommands',
        'commands_added': len([cmd for cmd in CoreCommands(bot).get_app_commands()]),
        'enhanced_logging': True
    })