"""
Utility Commands Cog - ULTRA FIXED VERSION
Basic utility commands with immediate responses
"""

import discord
from discord.ext import commands
from discord import app_commands
import logging
from typing import Optional

from utils.embeds import EmbedBuilder

logger = logging.getLogger(__name__)

class UtilityCommands(commands.Cog):
    """Various utility commands"""
    
    def __init__(self, bot):
        self.bot = bot
    
    @app_commands.command(name="avatar", description="Display a user's avatar")
    @app_commands.describe(user="The user whose avatar you want to see")
    async def avatar(self, interaction: discord.Interaction, user: discord.Member = None):
        """Display a user's avatar"""
        # IMMEDIATE response
        await interaction.response.send_message("🖼️ Getting avatar...", ephemeral=True)
        
        try:
            target_user = user or interaction.user
            
            embed = discord.Embed(
                title=f"{target_user.display_name}'s Avatar",
                color=discord.Color.blue()
            )
            
            # Get avatar URL
            if target_user.avatar:
                avatar_url = target_user.avatar.url
                embed.set_image(url=avatar_url)
                embed.add_field(
                    name="Download Links",
                    value=f"[PNG]({avatar_url}?format=png) | [JPG]({avatar_url}?format=jpg) | [WEBP]({avatar_url}?format=webp)",
                    inline=False
                )
            else:
                # Default avatar
                default_avatar = target_user.default_avatar.url
                embed.set_image(url=default_avatar)
                embed.add_field(
                    name="Note",
                    value="This user is using Discord's default avatar",
                    inline=False
                )
            
            await interaction.edit_original_response(content=None, embed=embed)
            
        except Exception as e:
            logger.error(f"Error in avatar command: {e}")
            await interaction.edit_original_response(content="❌ Error getting avatar")
    
    @app_commands.command(name="server_info", description="Display server information")
    async def server_info(self, interaction: discord.Interaction):
        """Display detailed server information"""
        # IMMEDIATE response
        await interaction.response.send_message("🏰 Getting server info...", ephemeral=True)
        
        try:
            guild = interaction.guild
            
            embed = discord.Embed(
                title=f"{guild.name} Server Information",
                color=discord.Color.green()
            )
            
            # Basic info
            embed.add_field(name="Server ID", value=guild.id, inline=True)
            embed.add_field(name="Owner", value=guild.owner.mention if guild.owner else "Unknown", inline=True)
            embed.add_field(name="Created", value=f"<t:{int(guild.created_at.timestamp())}:F>", inline=True)
            
            # Counts
            embed.add_field(name="Members", value=guild.member_count, inline=True)
            embed.add_field(name="Channels", value=len(guild.channels), inline=True)
            embed.add_field(name="Roles", value=len(guild.roles), inline=True)
            
            # Server icon
            if guild.icon:
                embed.set_thumbnail(url=guild.icon.url)
            
            # Verification level
            verification_levels = {
                discord.VerificationLevel.none: "None",
                discord.VerificationLevel.low: "Low",
                discord.VerificationLevel.medium: "Medium",
                discord.VerificationLevel.high: "High",
                discord.VerificationLevel.highest: "Highest"
            }
            embed.add_field(
                name="Verification Level",
                value=verification_levels.get(guild.verification_level, "Unknown"),
                inline=True
            )
            
            await interaction.edit_original_response(content=None, embed=embed)
            
        except Exception as e:
            logger.error(f"Error in server_info command: {e}")
            await interaction.edit_original_response(content="❌ Error getting server information")
    
    @app_commands.command(name="user_info", description="Display information about a user")
    @app_commands.describe(user="The user to get information about")
    async def user_info(self, interaction: discord.Interaction, user: discord.Member = None):
        """Display detailed user information"""
        # IMMEDIATE response
        await interaction.response.send_message("👤 Getting user info...", ephemeral=True)
        
        try:
            target_user = user or interaction.user
            
            embed = discord.Embed(
                title=f"User Information: {target_user.display_name}",
                color=target_user.color if target_user.color != discord.Color.default() else discord.Color.blue()
            )
            
            # Basic info
            embed.add_field(name="Username", value=str(target_user), inline=True)
            embed.add_field(name="User ID", value=target_user.id, inline=True)
            embed.add_field(name="Bot", value="Yes" if target_user.bot else "No", inline=True)
            
            # Dates
            embed.add_field(
                name="Account Created",
                value=f"<t:{int(target_user.created_at.timestamp())}:F>",
                inline=False
            )
            
            if target_user.joined_at:
                embed.add_field(
                    name="Joined Server",
                    value=f"<t:{int(target_user.joined_at.timestamp())}:F>",
                    inline=False
                )
            
            # Roles (limit to avoid embed limits)
            if len(target_user.roles) > 1:  # Exclude @everyone
                roles = [role.mention for role in target_user.roles[1:]]  # Skip @everyone
                roles_text = ", ".join(roles[:10])  # Limit to 10 roles
                if len(target_user.roles) > 11:
                    roles_text += f" and {len(target_user.roles) - 11} more..."
                embed.add_field(name="Roles", value=roles_text, inline=False)
            
            # Permissions
            if target_user.guild_permissions.administrator:
                embed.add_field(name="Permissions", value="🔑 Administrator", inline=True)
            
            # Avatar
            if target_user.avatar:
                embed.set_thumbnail(url=target_user.avatar.url)
            
            await interaction.edit_original_response(content=None, embed=embed)
            
        except Exception as e:
            logger.error(f"Error in user_info command: {e}")
            await interaction.edit_original_response(content="❌ Error getting user information")
    
    @app_commands.command(name="channel_info", description="Display information about a channel")
    @app_commands.describe(channel="The channel to get information about")
    async def channel_info(
        self, 
        interaction: discord.Interaction, 
        channel: discord.TextChannel = None
    ):
        """Display detailed channel information"""
        # IMMEDIATE response
        await interaction.response.send_message("📺 Getting channel info...", ephemeral=True)
        
        try:
            target_channel = channel or interaction.channel
            
            embed = discord.Embed(
                title=f"Channel Information: #{target_channel.name}",
                color=discord.Color.purple()
            )
            
            # Basic info
            embed.add_field(name="Channel ID", value=target_channel.id, inline=True)
            embed.add_field(name="Type", value=str(target_channel.type).title(), inline=True)
            embed.add_field(name="Position", value=target_channel.position, inline=True)
            
            # Creation date
            embed.add_field(
                name="Created",
                value=f"<t:{int(target_channel.created_at.timestamp())}:F>",
                inline=False
            )
            
            # Topic (if exists)
            if hasattr(target_channel, 'topic') and target_channel.topic:
                topic = target_channel.topic[:500] + "..." if len(target_channel.topic) > 500 else target_channel.topic
                embed.add_field(name="Topic", value=topic, inline=False)
            
            # Category
            if target_channel.category:
                embed.add_field(name="Category", value=target_channel.category.name, inline=True)
            
            # NSFW status
            if hasattr(target_channel, 'nsfw'):
                embed.add_field(name="NSFW", value="Yes" if target_channel.nsfw else "No", inline=True)
            
            await interaction.edit_original_response(content=None, embed=embed)
            
        except Exception as e:
            logger.error(f"Error in channel_info command: {e}")
            await interaction.edit_original_response(content="❌ Error getting channel information")

async def setup(bot):
    """Setup function for the cog"""
    await bot.add_cog(UtilityCommands(bot))
    logger.info("Utility commands cog loaded")
