"""
Bot Interaction Logger - Fixed Version with Corrected Formatting
Logs all interactions between the bot and Discord for debugging and monitoring
"""

import logging
import json
import discord
import asyncio
from datetime import datetime
from typing import Any, Dict, Optional, Union
from pathlib import Path
import inspect

class BotInteractionLogger:
    """Comprehensive logger for Discord bot interactions - Fixed Version"""

    def __init__(self, bot_name: str = "Fenrir", log_level: str = "INFO"):
        self.bot_name = bot_name
        self.setup_loggers(log_level)

        # Track interaction counts
        self.stats = {
            'commands_executed': 0,
            'events_received': 0,
            'api_calls_sent': 0,
            'errors_encountered': 0,
            'session_start': datetime.now()
        }

    def setup_loggers(self, log_level: str):
        """Setup specialized loggers for different types of interactions - FIXED"""

        # Ensure logs directory exists
        Path("logs").mkdir(exist_ok=True)

        # Create simple, safe formatters
        safe_formatter = logging.Formatter(
            fmt='%(asctime)s | %(name)s | %(levelname)s | %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )

        console_formatter = logging.Formatter(
            fmt='%(asctime)s | %(levelname)s | %(message)s',
            datefmt='%H:%M:%S'
        )

        # === MAIN BOT INTERACTION LOGGER ===
        self.interaction_logger = logging.getLogger(f'{self.bot_name}.interactions')
        self.interaction_logger.setLevel(getattr(logging, log_level.upper()))

        # Clear any existing handlers to avoid conflicts
        self.interaction_logger.handlers.clear()

        # File handler for interactions
        try:
            interaction_file = logging.FileHandler('logs/bot_interactions.log', encoding='utf-8')
            interaction_file.setLevel(logging.DEBUG)
            interaction_file.setFormatter(safe_formatter)
            self.interaction_logger.addHandler(interaction_file)
        except Exception as e:
            print(f"Warning: Could not create interaction log file: {e}")

        # Console handler for interactions
        try:
            interaction_console = logging.StreamHandler()
            interaction_console.setLevel(getattr(logging, log_level.upper()))
            interaction_console.setFormatter(console_formatter)
            self.interaction_logger.addHandler(interaction_console)
        except Exception as e:
            print(f"Warning: Could not create interaction console handler: {e}")

        # === DISCORD API LOGGER ===
        self.api_logger = logging.getLogger(f'{self.bot_name}.discord_api')
        self.api_logger.setLevel(logging.DEBUG)
        self.api_logger.handlers.clear()

        # File handler for API calls
        try:
            api_file = logging.FileHandler('logs/discord_api.log', encoding='utf-8')
            api_file.setLevel(logging.DEBUG)
            api_file.setFormatter(safe_formatter)
            self.api_logger.addHandler(api_file)
        except Exception as e:
            print(f"Warning: Could not create API log file: {e}")

        # === COMMAND EXECUTION LOGGER ===
        self.command_logger = logging.getLogger(f'{self.bot_name}.commands')
        self.command_logger.setLevel(logging.INFO)
        self.command_logger.handlers.clear()

        # File handler for commands
        try:
            command_file = logging.FileHandler('logs/command_execution.log', encoding='utf-8')
            command_file.setLevel(logging.INFO)
            command_file.setFormatter(safe_formatter)
            self.command_logger.addHandler(command_file)
        except Exception as e:
            print(f"Warning: Could not create command log file: {e}")

        # Console handler for commands
        try:
            command_console = logging.StreamHandler()
            command_console.setLevel(logging.INFO)
            command_console.setFormatter(console_formatter)
            self.command_logger.addHandler(command_console)
        except Exception as e:
            print(f"Warning: Could not create command console handler: {e}")

        # === ERROR LOGGER ===
        self.error_logger = logging.getLogger(f'{self.bot_name}.errors')
        self.error_logger.setLevel(logging.WARNING)
        self.error_logger.handlers.clear()

        # File handler for errors
        try:
            error_file = logging.FileHandler('logs/bot_errors.log', encoding='utf-8')
            error_file.setLevel(logging.WARNING)
            error_file.setFormatter(safe_formatter)
            self.error_logger.addHandler(error_file)
        except Exception as e:
            print(f"Warning: Could not create error log file: {e}")

        # Console handler for errors
        try:
            error_console = logging.StreamHandler()
            error_console.setLevel(logging.WARNING)
            error_console.setFormatter(console_formatter)
            self.error_logger.addHandler(error_console)
        except Exception as e:
            print(f"Warning: Could not create error console handler: {e}")

    def safe_log(self, logger, level, message):
        """Safe logging method that handles any formatting errors"""
        try:
            if hasattr(logger, level):
                getattr(logger, level)(message)
            else:
                logger.info(message)
        except Exception as e:
            # Fallback to print if logging fails
            print(f"[LOGGING ERROR] {datetime.now()}: {message}")
            print(f"[LOGGING ERROR] Exception: {e}")

    def log_bot_startup(self, bot: discord.Client):
        """Log bot startup information - SAFE VERSION"""
        try:
            startup_info = {
                'bot_id': bot.user.id if bot.user else 'Unknown',
                'bot_name': bot.user.name if bot.user else 'Unknown',
                'guilds_count': len(bot.guilds),
                'user_count': sum(guild.member_count for guild in bot.guilds if guild.member_count),
                'intents': str(bot.intents),
                'discord_py_version': discord.__version__
            }

            self.safe_log(self.interaction_logger, 'info', "🚀 BOT STARTUP COMPLETE")

            # Safe JSON serialization
            try:
                startup_json = json.dumps(startup_info, indent=2, default=str)
                self.safe_log(self.interaction_logger, 'info', f"📊 Startup Info: {startup_json}")
            except Exception as json_error:
                self.safe_log(self.interaction_logger, 'info', f"📊 Startup Info: {startup_info}")

        except Exception as e:
            print(f"Error in log_bot_startup: {e}")
            print("🚀 BOT STARTUP COMPLETE (fallback logging)")

    def log_command_execution(self, interaction: discord.Interaction, command_name: str,
                            args: Dict[str, Any] = None, execution_time: float = None):
        """Log slash command execution - SAFE VERSION"""
        try:
            self.stats['commands_executed'] += 1

            user_info = f"{interaction.user} ({interaction.user.id})" if interaction.user else "Unknown User"
            guild_info = f"{interaction.guild.name} ({interaction.guild.id})" if interaction.guild else "DM"
            channel_info = f"#{interaction.channel}" if hasattr(interaction.channel, 'name') else str(interaction.channel)

            self.safe_log(self.command_logger, 'info', f"⚡ COMMAND EXECUTED: /{command_name}")
            self.safe_log(self.command_logger, 'info', f"   👤 User: {user_info}")
            self.safe_log(self.command_logger, 'info', f"   🏰 Guild: {guild_info}")

            if args:
                try:
                    args_json = json.dumps(args, default=str)
                    self.safe_log(self.command_logger, 'info', f"   📝 Args: {args_json}")
                except:
                    self.safe_log(self.command_logger, 'info', f"   📝 Args: {args}")

            if execution_time:
                exec_time_ms = round(execution_time * 1000, 2)
                self.safe_log(self.command_logger, 'info', f"   ⏱️  Time: {exec_time_ms}ms")

        except Exception as e:
            print(f"Error in log_command_execution: {e}")

    def log_discord_event(self, event_name: str, event_data: Dict[str, Any] = None):
        """Log Discord events received by the bot - SAFE VERSION"""
        try:
            self.stats['events_received'] += 1

            self.safe_log(self.interaction_logger, 'debug', f"📡 DISCORD EVENT: {event_name}")

            if event_data:
                try:
                    data_json = json.dumps(event_data, default=str, indent=2)
                    self.safe_log(self.interaction_logger, 'debug', f"   📋 Data: {data_json}")
                except:
                    self.safe_log(self.interaction_logger, 'debug', f"   📋 Data: {event_data}")

        except Exception as e:
            print(f"Error in log_discord_event: {e}")

    def log_api_request(self, method: str, endpoint: str, data: Any = None,
                       status_code: int = None, response_time: float = None):
        """Log Discord API requests sent by the bot - SAFE VERSION"""
        try:
            self.stats['api_calls_sent'] += 1

            status_emoji = "✅" if status_code and 200 <= status_code < 300 else "❌" if status_code else "📤"

            self.safe_log(self.api_logger, 'info', f"{status_emoji} API REQUEST: {method} {endpoint}")

            if status_code:
                self.safe_log(self.api_logger, 'info', f"   📊 Status: {status_code}")

            if response_time:
                response_time_ms = round(response_time * 1000, 2)
                self.safe_log(self.api_logger, 'info', f"   ⏱️  Time: {response_time_ms}ms")

            if data and method.upper() in ['POST', 'PUT', 'PATCH']:
                try:
                    data_json = json.dumps(data, default=str)
                    self.safe_log(self.api_logger, 'debug', f"   📤 Sent: {data_json}")
                except:
                    self.safe_log(self.api_logger, 'debug', f"   📤 Sent: {data}")

        except Exception as e:
            print(f"Error in log_api_request: {e}")

    def log_message_interaction(self, message: discord.Message, action: str, details: str = None):
        """Log message-related interactions - SAFE VERSION"""
        try:
            author_info = f"{message.author} ({message.author.id})" if message.author else "Unknown Author"
            channel_info = f"#{message.channel}" if hasattr(message.channel, 'name') else str(message.channel)
            guild_info = f"{message.guild.name} ({message.guild.id})" if message.guild else "DM"

            self.safe_log(self.interaction_logger, 'info', f"💬 MESSAGE {action.upper()}: {message.id}")
            self.safe_log(self.interaction_logger, 'info', f"   👤 Author: {author_info}")
            self.safe_log(self.interaction_logger, 'info', f"   📍 Location: {guild_info} > {channel_info}")

            if details:
                self.safe_log(self.interaction_logger, 'info', f"   ℹ️  Details: {details}")

        except Exception as e:
            print(f"Error in log_message_interaction: {e}")

    def log_error(self, error: Exception, context: str = None, interaction: discord.Interaction = None):
        """Log errors with context - SAFE VERSION"""
        try:
            self.stats['errors_encountered'] += 1

            error_type = type(error).__name__
            error_message = str(error)

            self.safe_log(self.error_logger, 'error', f"💥 ERROR: {error_type}")
            self.safe_log(self.error_logger, 'error', f"   📝 Message: {error_message}")

            if context:
                self.safe_log(self.error_logger, 'error', f"   🔍 Context: {context}")

            if interaction:
                try:
                    user_info = f"{interaction.user} ({interaction.user.id})" if interaction.user else "Unknown User"
                    guild_info = f"{interaction.guild.name} ({interaction.guild.id})" if interaction.guild else "DM"

                    self.safe_log(self.error_logger, 'error', f"   👤 User: {user_info}")
                    self.safe_log(self.error_logger, 'error', f"   🏰 Guild: {guild_info}")
                except:
                    pass

        except Exception as e:
            print(f"Error in log_error: {e}")

    def log_member_action(self, member: discord.Member, action: str, details: Dict[str, Any] = None):
        """Log member-related actions - SAFE VERSION"""
        try:
            action_emoji = {
                'join': '👋',
                'leave': '👋',
                'ban': '🔨',
                'unban': '🔓',
                'update': '✏️'
            }.get(action.lower(), '👤')

            member_info = f"{member} ({member.id})" if member else "Unknown Member"
            guild_info = f"{member.guild.name} ({member.guild.id})" if member and member.guild else "Unknown Guild"

            self.safe_log(self.interaction_logger, 'info', f"{action_emoji} MEMBER {action.upper()}: {member}")
            self.safe_log(self.interaction_logger, 'info', f"   🏰 Guild: {guild_info}")

            if details:
                try:
                    details_json = json.dumps(details, default=str)
                    self.safe_log(self.interaction_logger, 'info', f"   📋 Details: {details_json}")
                except:
                    self.safe_log(self.interaction_logger, 'info', f"   📋 Details: {details}")

        except Exception as e:
            print(f"Error in log_member_action: {e}")

    def log_guild_action(self, guild: discord.Guild, action: str, details: Dict[str, Any] = None):
        """Log guild-related actions - SAFE VERSION"""
        try:
            action_emoji = {
                'join': '🏰',
                'leave': '👋',
                'update': '✏️',
                'create': '🆕',
                'delete': '🗑️'
            }.get(action.lower(), '🏰')

            guild_info = f"{guild.name} ({guild.id})" if guild else "Unknown Guild"

            self.safe_log(self.interaction_logger, 'info', f"{action_emoji} GUILD {action.upper()}: {guild.name}")

            if guild and hasattr(guild, 'member_count'):
                self.safe_log(self.interaction_logger, 'info', f"   👥 Members: {guild.member_count}")

            if details:
                try:
                    details_json = json.dumps(details, default=str)
                    self.safe_log(self.interaction_logger, 'info', f"   📋 Details: {details_json}")
                except:
                    self.safe_log(self.interaction_logger, 'info', f"   📋 Details: {details}")

        except Exception as e:
            print(f"Error in log_guild_action: {e}")

    def log_session_stats(self):
        """Log current session statistics - SAFE VERSION"""
        try:
            session_duration = datetime.now() - self.stats['session_start']

            self.safe_log(self.interaction_logger, 'info', "📈 SESSION STATISTICS")
            self.safe_log(self.interaction_logger, 'info', f"   ⏰ Duration: {session_duration}")
            self.safe_log(self.interaction_logger, 'info', f"   ⚡ Commands: {self.stats['commands_executed']}")
            self.safe_log(self.interaction_logger, 'info', f"   📡 Events: {self.stats['events_received']}")
            self.safe_log(self.interaction_logger, 'info', f"   📤 API Calls: {self.stats['api_calls_sent']}")
            self.safe_log(self.interaction_logger, 'info', f"   💥 Errors: {self.stats['errors_encountered']}")

        except Exception as e:
            print(f"Error in log_session_stats: {e}")

    def debug_dump(self, data: Any, title: str = "DEBUG DUMP"):
        """Dump any data structure for debugging - SAFE VERSION"""
        try:
            self.safe_log(self.interaction_logger, 'debug', f"🔧 {title}")

            try:
                data_json = json.dumps(data, default=str, indent=2)
                self.safe_log(self.interaction_logger, 'debug', f"   {data_json}")
            except:
                self.safe_log(self.interaction_logger, 'debug', f"   {data}")

        except Exception as e:
            print(f"Error in debug_dump: {e}")

# Global logger instance
bot_logger: Optional[BotInteractionLogger] = None

def init_bot_logger(bot_name: str = "Fenrir", log_level: str = "INFO") -> BotInteractionLogger:
    """Initialize the global bot logger - SAFE VERSION"""
    global bot_logger
    try:
        bot_logger = BotInteractionLogger(bot_name, log_level)
        return bot_logger
    except Exception as e:
        print(f"Error initializing bot logger: {e}")
        return None

def get_bot_logger() -> Optional[BotInteractionLogger]:
    """Get the global bot logger instance"""
    return bot_logger

# Convenience functions for easier usage - SAFE VERSIONS
def log_command(interaction: discord.Interaction, command_name: str, args: Dict[str, Any] = None, execution_time: float = None):
    """Quick function to log command execution"""
    if bot_logger:
        try:
            bot_logger.log_command_execution(interaction, command_name, args, execution_time)
        except Exception as e:
            print(f"Error logging command: {e}")

def log_event(event_name: str, data: Dict[str, Any] = None):
    """Quick function to log Discord events"""
    if bot_logger:
        try:
            bot_logger.log_discord_event(event_name, data)
        except Exception as e:
            print(f"Error logging event: {e}")

def log_error(error: Exception, context: str = None, interaction: discord.Interaction = None):
    """Quick function to log errors"""
    if bot_logger:
        try:
            bot_logger.log_error(error, context, interaction)
        except Exception as e:
            print(f"Error logging error: {e}")

def log_api(method: str, endpoint: str, data: Any = None, status_code: int = None, response_time: float = None):
    """Quick function to log API requests"""
    if bot_logger:
        try:
            bot_logger.log_api_request(method, endpoint, data, status_code, response_time)
        except Exception as e:
            print(f"Error logging API request: {e}")

def log_message(message: discord.Message, action: str, details: str = None):
    """Quick function to log message interactions"""
    if bot_logger:
        try:
            bot_logger.log_message_interaction(message, action, details)
        except Exception as e:
            print(f"Error logging message: {e}")

def log_member(member: discord.Member, action: str, details: Dict[str, Any] = None):
    """Quick function to log member actions"""
    if bot_logger:
        try:
            bot_logger.log_member_action(member, action, details)
        except Exception as e:
            print(f"Error logging member action: {e}")

def log_guild(guild: discord.Guild, action: str, details: Dict[str, Any] = None):
    """Quick function to log guild actions"""
    if bot_logger:
        try:
            bot_logger.log_guild_action(guild, action, details)
        except Exception as e:
            print(f"Error logging guild action: {e}")

def debug_dump(data: Any, title: str = "DEBUG DUMP"):
    """Quick function to debug dump data"""
    if bot_logger:
        try:
            bot_logger.debug_dump(data, title)
        except Exception as e:
            print(f"Error in debug dump: {e}")