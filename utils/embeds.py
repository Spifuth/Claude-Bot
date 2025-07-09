"""
Discord Embed Utilities
Common embed templates and utilities
"""

import discord
from typing import Dict, Any, Optional

class EmbedBuilder:
    """Utility class for building Discord embeds"""
    
    @staticmethod
    def success(title: str, description: str = None) -> discord.Embed:
        """Create a success embed"""
        embed = discord.Embed(
            title=f"✅ {title}",
            description=description,
            color=discord.Color.green()
        )
        return embed
    
    @staticmethod
    def error(title: str, description: str = None) -> discord.Embed:
        """Create an error embed"""
        embed = discord.Embed(
            title=f"❌ {title}",
            description=description,
            color=discord.Color.red()
        )
        return embed
    
    @staticmethod
    def warning(title: str, description: str = None) -> discord.Embed:
        """Create a warning embed"""
        embed = discord.Embed(
            title=f"⚠️ {title}",
            description=description,
            color=discord.Color.orange()
        )
        return embed
    
    @staticmethod
    def info(title: str, description: str = None, color: discord.Color = discord.Color.blue()) -> discord.Embed:
        """Create an info embed"""
        embed = discord.Embed(
            title=title,
            description=description,
            color=color
        )
        return embed
