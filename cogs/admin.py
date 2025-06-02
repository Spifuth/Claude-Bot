"""
Admin Commands Cog
Commands for bot administration and management
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
    
    async def sync_commands_to_guild(self, guild_id: int = None):
        """Sync commands to a specific guild or globally"""
        try:
            if guild_id:
                guild = discord.Object(id=guild_id)
                synced = await self.bot.tree.sync(guild=guild)
                return f"Synced {len(synced)} commands to guild {guild_id}"
            else:
                synced = await self.bot.tree.sync()
                return f"Synced {len(synced)} commands globally"
        except Exception as e:
            return f"Failed to sync: {str(e)}"
    
    async def clear_commands_from_guild(self, guild_id: int = None):
        """Clear all commands from a guild or globally"""
        try:
            if guild_id:
                guild = discord.Object(id=guild_id)
                self.bot.tree.clear_commands(guild=guild)
                await self.bot.tree.sync(guild=guild)
                return f"Cleared commands from guild {guild_id}"
            else:
                self.bot.tree.clear_commands(guild=None)
                await self.bot.tree.sync()
                return "Cleared global commands"
        except Exception as e:
            return f"Failed to clear commands: {str(e)}"
    
    @app_commands.command(name="sync_commands", description="Sync slash commands (Admin only)")
    @app_commands.describe(
        scope="Where to sync commands: 'global', 'guild', 'clear_global', 'clear_guild'"
    )
    async def sync_commands(self, interaction: discord.Interaction, scope: str = "guild"):
        """Sync slash commands - useful for updating command list"""
        
        # Check if user has administrator permissions
        if not interaction.user.guild_permissions.administrator:
            embed = EmbedBuilder.error(
                "Permission Denied",
                "You need administrator permissions to use this command."
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        await interaction.response.defer(ephemeral=True)
        
        try:
            if scope.lower() == "global":
                result = await self.sync_commands_to_guild(None)
                embed = EmbedBuilder.success("Global Command Sync", result)
                embed.add_field(
                    name="Note", 
                    value="Global commands may take up to 1 hour to update across all servers.", 
                    inline=False
                )
                
            elif scope.lower() == "guild":
                guild_id = interaction.guild_id
                result = await self.sync_commands_to_guild(guild_id)
                embed = EmbedBuilder.success("Guild Command Sync", result)
                embed.add_field(
                    name="Note", 
                    value="Guild commands update immediately in this server.", 
                    inline=False
                )
                
            elif scope.lower() == "clear_global":
                result = await self.clear_commands_from_guild(None)
                embed = EmbedBuilder.warning("Global Commands Cleared", result)
                embed.add_field(
                    name="Warning", 
                    value="All global commands have been removed. Use 'global' scope to re-add them.", 
                    inline=False
                )
                
            elif scope.lower() == "clear_guild":
                guild_id = interaction.guild_id
                result = await self.clear_commands_from_guild(guild_id)
                embed = EmbedBuilder.warning("Guild Commands Cleared", result)
                embed.add_field(
                    name="Warning", 
                    value="All guild commands have been removed. Use 'guild' scope to re-add them.", 
                    inline=False
                )
                
            else:
                embed = EmbedBuilder.error(
                    "Invalid Scope",
                    "Valid options: `global`, `guild`, `clear_global`, `clear_guild`"
                )
            
            await interaction.followup.send(embed=embed)
            
        except Exception as e:
            embed = EmbedBuilder.error("Command Sync Error", f"An error occurred: {str(e)}")
            await interaction.followup.send(embed=embed)
    
    @app_commands.command(name="list_commands", description="List all registered slash commands")
    async def list_commands(self, interaction: discord.Interaction):
        """List all currently registered slash commands"""
        
        embed = discord.Embed(
            title="📝 Registered Slash Commands",
            color=discord.Color.purple()
        )
        
        # Get guild commands
        guild_commands = self.bot.tree.get_commands(guild=interaction.guild)
        if guild_commands:
            guild_cmd_list = [f"• `/{cmd.name}` - {cmd.description}" for cmd in guild_commands]
            embed.add_field(
                name=f"🏠 Guild Commands ({len(guild_commands)})",
                value="\n".join(guild_cmd_list) if guild_cmd_list else "None",
                inline=False
            )
        
        # Get global commands
        global_commands = self.bot.tree.get_commands(guild=None)
        if global_commands:
            global_cmd_list = [f"• `/{cmd.name}` - {cmd.description}" for cmd in global_commands]
            embed.add_field(
                name=f"🌍 Global Commands ({len(global_commands)})",
                value="\n".join(global_cmd_list) if global_cmd_list else "None",
                inline=False
            )
        
        if not guild_commands and not global_commands:
            embed.description = "No commands are currently registered."
        
        embed.add_field(
            name="💡 Tip",
            value="Use `/sync_commands` to update the command list if you see outdated commands.",
            inline=False
        )
        
        await interaction.response.send_message(embed=embed, ephemeral=True)

async def setup(bot):
    """Setup function for the cog"""
    await bot.add_cog(AdminCommands(bot))
    logger.info("Admin commands cog loaded")