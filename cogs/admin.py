"""
Admin Commands Cog - ULTRA FIXED VERSION
No double response issues, immediate acknowledgment
"""

import discord
from discord.ext import commands
from discord import app_commands
import logging

from utils.embeds import EmbedBuilder

logger = logging.getLogger(__name__)

class AdminCommands(commands.Cog):
    """Administrative commands for bot management"""
    
    def __init__(self, bot):
        self.bot = bot
    
    @app_commands.command(name="sync_commands", description="Sync slash commands (Admin Only)")
    @app_commands.describe(scope="Sync scope: global, guild, or clear_guild")
    @app_commands.choices(scope=[
        app_commands.Choice(name="Global (slow)", value="global"),
        app_commands.Choice(name="This Guild (fast)", value="guild"),
        app_commands.Choice(name="Clear Guild Commands", value="clear_guild")
    ])
    async def sync_commands(self, interaction: discord.Interaction, scope: str = "guild"):
        """Sync slash commands"""
        # IMMEDIATE response
        await interaction.response.send_message("🔄 Syncing commands...", ephemeral=True)
        
        try:
            # Check if user is bot owner or has admin permissions
            if not await self.is_owner_or_admin(interaction.user):
                await interaction.edit_original_response(content="❌ You need administrator permissions to sync commands.")
                return
            
            if scope == "global":
                synced = await self.bot.tree.sync()
                message = f"✅ Synced {len(synced)} commands globally. May take up to 1 hour to appear."
            elif scope == "guild":
                synced = await self.bot.tree.sync(guild=interaction.guild)
                message = f"✅ Synced {len(synced)} commands for this guild. Should appear immediately."
            elif scope == "clear_guild":
                self.bot.tree.clear_commands(guild=interaction.guild)
                await self.bot.tree.sync(guild=interaction.guild)
                message = "✅ Cleared all guild-specific commands. Global commands remain."
            
            await interaction.edit_original_response(content=message)
            
        except Exception as e:
            logger.error(f"Error in sync_commands: {e}")
            await interaction.edit_original_response(content=f"❌ Sync failed: {str(e)}")
    
    @app_commands.command(name="list_commands", description="List all available commands")
    async def list_commands(self, interaction: discord.Interaction):
        """List all bot commands"""
        await interaction.response.send_message("📋 Loading command list...", ephemeral=True)
        
        try:
            embed = discord.Embed(
                title="📋 Available Commands",
                description="All currently loaded commands",
                color=discord.Color.blue()
            )
            
            # Group commands by cog
            for cog_name, cog in self.bot.cogs.items():
                commands = [cmd for cmd in cog.get_app_commands()]
                if commands:
                    command_names = [f"`/{cmd.name}`" for cmd in commands]
                    embed.add_field(
                        name=f"{cog_name} ({len(commands)})",
                        value=" • ".join(command_names),
                        inline=False
                    )
            
            # Add global commands count
            total_commands = len(self.bot.tree.get_commands())
            embed.set_footer(text=f"Total Commands: {total_commands}")
            
            await interaction.edit_original_response(content=None, embed=embed)
            
        except Exception as e:
            logger.error(f"Error in list_commands: {e}")
            await interaction.edit_original_response(content="❌ Error loading command list")
    
    @app_commands.command(name="stats", description="Display detailed bot statistics")
    async def stats(self, interaction: discord.Interaction):
        """Display comprehensive bot statistics"""
        await interaction.response.send_message("📊 Gathering statistics...", ephemeral=True)
        
        try:
            embed = discord.Embed(
                title="📊 Bot Statistics",
                color=discord.Color.gold()
            )
            
            # Basic stats
            embed.add_field(name="Guilds", value=len(self.bot.guilds), inline=True)
            embed.add_field(name="Users", value=len(self.bot.users), inline=True)
            embed.add_field(name="Commands", value=len(self.bot.tree.get_commands()), inline=True)
            
            # Loaded cogs
            embed.add_field(name="Loaded Cogs", value=len(self.bot.cogs), inline=True)
            embed.add_field(name="Latency", value=f"{round(self.bot.latency * 1000)}ms", inline=True)
            
            # Module status
            enabled_modules = []
            for module, enabled in self.bot.config.MODULES_ENABLED.items():
                status_emoji = "🟢" if enabled else "🔴"
                enabled_modules.append(f"{status_emoji} {module.title()}")
            
            if enabled_modules:
                embed.add_field(name="Modules", value="\n".join(enabled_modules), inline=False)
            
            # Cog details
            cog_info = []
            for cog_name, cog in self.bot.cogs.items():
                command_count = len([cmd for cmd in cog.get_app_commands()])
                cog_info.append(f"• {cog_name}: {command_count} commands")
            
            if cog_info:
                embed.add_field(name="Cog Details", value="\n".join(cog_info), inline=False)
            
            await interaction.edit_original_response(content=None, embed=embed)
            
        except Exception as e:
            logger.error(f"Error in bot_stats: {e}")
            await interaction.edit_original_response(content="❌ Error gathering statistics")
    
    async def is_owner_or_admin(self, user: discord.User) -> bool:
        """Check if user is bot owner or has admin permissions"""
        # Check if user is bot owner
        if await self.bot.is_owner(user):
            return True
        
        # Check if user has admin permissions (for guild-specific commands)
        if hasattr(user, 'guild_permissions') and user.guild_permissions.administrator:
            return True
        
        return False

async def setup(bot):
    """Setup function for the cog"""
    await bot.add_cog(AdminCommands(bot))
    logger.info("Admin commands cog loaded")
