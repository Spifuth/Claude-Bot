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
        """Enhanced validation"""
        if not cls.DISCORD_TOKEN:
            raise ValueError("DISCORD_BOT_TOKEN environment variable is required!")

        # Validate log level
        valid_levels = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
        if cls.LOG_LEVEL not in valid_levels:
            raise ValueError(f"BOT_LOG_LEVEL must be one of: {', '.join(valid_levels)}")

        return True

# Validate configuration on import
BotConfig.validate()