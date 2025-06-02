"""
Core Commands Cog
Basic commands that are always available
"""

import discord
from discord.ext import commands
from discord import app_commands
import logging

from utils.embeds import EmbedBuilder

logger = logging.getLogger(__name__)

class CoreCommands(commands.Cog):
    """Core bot commands"""
    
    def __init__(self, bot):
        self.bot = bot
    
    @app_commands.command(name="ping", description="Check if Fenrir is alive")
    async def ping(self, interaction: discord.Interaction):
        """Simple ping command"""
        latency = round(self.bot.latency * 1000)
        embed = EmbedBuilder.success(
            "Pong!",
            f"🏓 Latency: {latency}ms"
        )
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="status", description="Check Fenrir's status and available modules")
    async def status(self, interaction: discord.Interaction):
        """Check bot status and enabled modules"""
        embed = discord.Embed(
            title="🐺 Fenrir Status",
            color=discord.Color.blue()
        )
        
        # Basic bot info
        embed.add_field(name="Bot Status", value="🟢 Online", inline=True)
        embed.add_field(name="Latency", value=f"{round(self.bot.latency * 1000)}ms", inline=True)
        embed.add_field(name="Guilds", value=len(self.bot.guilds), inline=True)
        
        # Show enabled modules
        modules_status = []
        for module, enabled in self.bot.config.MODULES_ENABLED.items():
            status_emoji = "🟢" if enabled else "🔴"
            modules_status.append(f"{status_emoji} {module.title()}")
        
        embed.add_field(name="Modules", value="\n".join(modules_status), inline=False)
        
        # Add bot avatar
        if self.bot.user.avatar:
            embed.set_thumbnail(url=self.bot.user.avatar.url)
        
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="bot_info", description="Get detailed information about Fenrir")
    async def info_command(self, interaction: discord.Interaction):
        """Get detailed bot information"""
        embed = discord.Embed(
            title="🐺 Fenrir Bot Information",
            color=discord.Color.gold()
        )
        
        # Basic info
        embed.add_field(name="Bot Name", value=self.bot.user.name, inline=True)
        embed.add_field(name="Bot ID", value=self.bot.user.id, inline=True)
        embed.add_field(name="Latency", value=f"{round(self.bot.latency * 1000)}ms", inline=True)
        
        # Server info
        embed.add_field(name="Guilds", value=len(self.bot.guilds), inline=True)
        embed.add_field(name="Users", value=len(self.bot.users), inline=True)
        embed.add_field(name="Commands", value=len(self.bot.tree.get_commands()), inline=True)
        
        # Module status
        modules_status = []
        for module, enabled in self.bot.config.MODULES_ENABLED.items():
            status_emoji = "🟢" if enabled else "🔴"
            modules_status.append(f"{status_emoji} {module.title()}")
        
        embed.add_field(name="Modules", value="\n".join(modules_status), inline=False)
        
        # Loaded cogs
        loaded_cogs = [cog for cog in self.bot.cogs.keys()]
        embed.add_field(name="Loaded Cogs", value=", ".join(loaded_cogs), inline=False)
        
        # Add bot avatar
        if self.bot.user.avatar:
            embed.set_thumbnail(url=self.bot.user.avatar.url)
        
        embed.set_footer(text=f"Discord.py version: {discord.__version__}")
        
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="help", description="Get help with Fenrir commands")
    async def help_command(self, interaction: discord.Interaction):
        """Custom help command"""
        embed = discord.Embed(
            title="🐺 Fenrir Help",
            description="Available commands organized by category",
            color=discord.Color.blue()
        )
        
        # Group commands by cog
        for cog_name, cog in self.bot.cogs.items():
            commands = [cmd for cmd in cog.get_app_commands()]
            if commands:
                command_list = [f"`/{cmd.name}` - {cmd.description}" for cmd in commands]
                embed.add_field(
                    name=f"{cog_name} Commands",
                    value="\n".join(command_list[:5]),  # Limit to avoid embed limits
                    inline=False
                )
                
                if len(command_list) > 5:
                    embed.add_field(
                        name="",
                        value=f"... and {len(command_list) - 5} more",
                        inline=False
                    )
        
        embed.set_footer(text="Use /bot_info for detailed bot information")
        
        await interaction.response.send_message(embed=embed, ephemeral=True)

async def setup(bot):
    """Setup function for the cog"""
    await bot.add_cog(CoreCommands(bot))
    logger.info("Core commands cog loaded")