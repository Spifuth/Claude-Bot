"""
Enhanced Fenrir Bot Configuration with Interaction Logging
"""

import os
from dotenv import load_dotenv

load_dotenv()

class BotConfig:
    """Enhanced bot configuration class"""

    # Existing Discord Configuration
    DISCORD_TOKEN = os.getenv('DISCORD_BOT_TOKEN')
    PREFIX = os.getenv('BOT_PREFIX', '!')

    # Existing Database Configuration
    DATABASE_PATH = os.getenv('DATABASE_PATH', './data/fenrir.db')

    # Enhanced Logging Configuration
    LOG_LEVEL = os.getenv('BOT_LOG_LEVEL', 'INFO').upper()
    ENABLE_INTERACTION_LOGGING = os.getenv('ENABLE_INTERACTION_LOGGING', 'true').lower() == 'true'
    ENABLE_API_LOGGING = os.getenv('ENABLE_API_LOGGING', 'true').lower() == 'true'
    ENABLE_COMMAND_TIMING = os.getenv('ENABLE_COMMAND_TIMING', 'true').lower() == 'true'
    ENABLE_MEMORY_MONITORING = os.getenv('ENABLE_MEMORY_MONITORING', 'false').lower() == 'true'

    # Enhanced Module Configuration
    MODULES_ENABLED = {
        'logging': os.getenv('ENABLE_LOGGING', 'false').lower() == 'true',
        'interaction_logging': ENABLE_INTERACTION_LOGGING,
        'api_logging': ENABLE_API_LOGGING,
        'command_timing': ENABLE_COMMAND_TIMING,
    }

    # Existing Bot Settings
    AUTO_SYNC_COMMANDS = os.getenv('AUTO_SYNC_COMMANDS', 'false').lower() == 'true'
    REQUEST_TIMEOUT = int(os.getenv('REQUEST_TIMEOUT', '30'))
    MAX_EMBED_FIELDS = int(os.getenv('MAX_EMBED_FIELDS', '25'))

    @classmethod
    def validate(cls):
        """Enhanced validation with better error messages"""
        # CHANGE: Add comprehensive validation with helpful error messages
        missing_vars = []
        invalid_vars = []

        # Check required variables
        if not cls.DISCORD_TOKEN:
            missing_vars.append("DISCORD_BOT_TOKEN")

        # Check if token looks valid (basic format check)
        if cls.DISCORD_TOKEN and len(cls.DISCORD_TOKEN) < 50:
            invalid_vars.append("DISCORD_BOT_TOKEN (too short)")

        # Validate log level
        valid_levels = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
        if cls.LOG_LEVEL not in valid_levels:
            invalid_vars.append(f"BOT_LOG_LEVEL (must be one of: {', '.join(valid_levels)})")

        # Check database path is writable
        try:
            db_dir = os.path.dirname(cls.DATABASE_PATH)
            if db_dir and not os.path.exists(db_dir):
                os.makedirs(db_dir, exist_ok=True)
        except Exception as e:
            invalid_vars.append(f"DATABASE_PATH directory not writable: {e}")

        # Report errors with helpful messages
        if missing_vars or invalid_vars:
            error_msg = "Bot configuration validation failed:\n"
            if missing_vars:
                error_msg += f"❌ Missing required variables: {', '.join(missing_vars)}\n"
            if invalid_vars:
                error_msg += f"⚠️  Invalid variables: {', '.join(invalid_vars)}\n"
            error_msg += "\n💡 Please check your .env file or environment configuration."
            raise ValueError(error_msg)

        return True

# Validate configuration on import
BotConfig.validate()