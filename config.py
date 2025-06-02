"""
Fenrir Bot Configuration
Centralized configuration management
"""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class BotConfig:
    """Bot configuration class"""
    
    # Discord Configuration
    DISCORD_TOKEN = os.getenv('DISCORD_BOT_TOKEN')
    PREFIX = os.getenv('BOT_PREFIX', '!')
    
    # Homelab Configuration
    HOMELAB_BASE_URL = os.getenv('HOMELAB_BASE_URL', 'https://fenrir.nebulahost.tech')
    HOMELAB_API_KEY = os.getenv('HOMELAB_API_KEY', '')
    
    # Module Configuration
    MODULES_ENABLED = {
        'homelab': os.getenv('ENABLE_HOMELAB', 'false').lower() == 'true',
        'music': os.getenv('ENABLE_MUSIC', 'false').lower() == 'true',
        'gaming': os.getenv('ENABLE_GAMING', 'false').lower() == 'true',
        # Add more modules here as you expand
    }
    
    # Bot Settings
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO').upper()
    AUTO_SYNC_COMMANDS = os.getenv('AUTO_SYNC_COMMANDS', 'false').lower() == 'true'
    
    # API Settings
    REQUEST_TIMEOUT = int(os.getenv('REQUEST_TIMEOUT', '30'))
    MAX_EMBED_FIELDS = int(os.getenv('MAX_EMBED_FIELDS', '25'))
    
    # Validation
    @classmethod
    def validate(cls):
        """Validate required configuration"""
        if not cls.DISCORD_TOKEN:
            raise ValueError("DISCORD_BOT_TOKEN environment variable is required!")
        
        if cls.MODULES_ENABLED['homelab'] and not cls.HOMELAB_API_KEY:
            print("⚠️  Warning: Homelab module enabled but no API key provided")
        
        return True

# Validate configuration on import
BotConfig.validate()