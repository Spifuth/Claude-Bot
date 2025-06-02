"""
Homelab Commands Cog
Commands for managing homelab services and infrastructure
"""

import discord
from discord.ext import commands
from discord import app_commands
import logging

from utils.embeds import EmbedBuilder

logger = logging.getLogger(__name__)

class HomelabCommands(commands.Cog):
    """Homelab management commands"""
    
    def __init__(self, bot):
        self.bot = bot
        self.homelab_client = bot.homelab_client
    
    def cog_check(self, ctx):
        """Check if homelab module is enabled"""
        return self.bot.config.MODULES_ENABLED.get('homelab', False)
    
    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        """Check if homelab module is enabled for slash commands"""
        if not self.bot.config.MODULES_ENABLED.get('homelab', False):
            embed = EmbedBuilder.error(
                "Module Disabled",
                "Homelab module is not enabled."
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return False
        
        if not self.homelab_client.is_configured():
            embed = EmbedBuilder.error(
                "Not Configured",
                "Homelab API is not properly configured. Check your environment variables."
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return False
        
        return True
    
    @app_commands.command(name="homelab_status", description="Check the status of homelab services")
    async def homelab_status(self, interaction: discord.Interaction):
        """Check homelab services status"""
        await interaction.response.defer()
        
        try:
            status_data = await self.homelab_client.get_status()
            
            if 'error' in status_data:
                embed = EmbedBuilder.error(
                    "Homelab Status Error",
                    f"Failed to fetch status: {status_data['error']}"
                )
            else:
                embed = EmbedBuilder.status_embed(status_data, "Homelab Status")
            
            await interaction.followup.send(embed=embed)
            
        except Exception as e:
            embed = EmbedBuilder.error("Error", f"An unexpected error occurred: {str(e)}")
            await interaction.followup.send(embed=embed)
    
    @app_commands.command(name="docker_containers", description="List Docker containers")
    async def docker_containers(self, interaction: discord.Interaction):
        """List running Docker containers"""
        await interaction.response.defer()
        
        try:
            containers_data = await self.homelab_client.get_containers()
            
            if 'error' in containers_data:
                embed = EmbedBuilder.error(
                    "Docker Containers Error",
                    f"Failed to fetch containers: {containers_data['error']}"
                )
            else:
                if isinstance(containers_data, list):
                    embed = EmbedBuilder.container_list_embed(containers_data)
                else:
                    embed = EmbedBuilder.warning(
                        "No Containers",
                        "No containers found or unexpected response format"
                    )
            
            await interaction.followup.send(embed=embed)
            
        except Exception as e:
            embed = EmbedBuilder.error("Error", f"An unexpected error occurred: {str(e)}")
            await interaction.followup.send(embed=embed)
    
    @app_commands.command(name="restart_service", description="Restart a homelab service")
    @app_commands.describe(service_name="Name of the service to restart")
    async def restart_service(self, interaction: discord.Interaction, service_name: str):
        """Restart a specific service"""
        await interaction.response.defer()
        
        try:
            restart_data = await self.homelab_client.restart_service(service_name)
            
            if 'error' in restart_data or restart_data.get('_status_code', 200) != 200:
                embed = EmbedBuilder.error(
                    "Restart Failed",
                    f"Failed to restart {service_name}: {restart_data.get('error', 'Unknown error')}"
                )
            else:
                embed = EmbedBuilder.success(
                    "Service Restarted",
                    f"Successfully restarted `{service_name}`"
                )
            
            await interaction.followup.send(embed=embed)
            
        except Exception as e:
            embed = EmbedBuilder.error("Error", f"An unexpected error occurred: {str(e)}")
            await interaction.followup.send(embed=embed)
    
    @app_commands.command(name="restart_compose", description="Restart a Docker Compose stack")
    @app_commands.describe(stack_name="Name of the compose stack to restart")
    async def restart_compose(self, interaction: discord.Interaction, stack_name: str):
        """Restart a Docker Compose stack"""
        await interaction.response.defer()
        
        try:
            restart_data = await self.homelab_client.restart_compose_stack(stack_name)
            
            if 'error' in restart_data or restart_data.get('_status_code', 200) != 200:
                embed = EmbedBuilder.error(
                    "Restart Failed",
                    f"Failed to restart stack {stack_name}: {restart_data.get('error', 'Unknown error')}"
                )
            else:
                embed = EmbedBuilder.success(
                    "Stack Restarted",
                    f"Successfully restarted compose stack `{stack_name}`"
                )
            
            await interaction.followup.send(embed=embed)
            
        except Exception as e:
            embed = EmbedBuilder.error("Error", f"An unexpected error occurred: {str(e)}")
            await interaction.followup.send(embed=embed)
    
    @app_commands.command(name="system_info", description="Get homelab system information")
    async def system_info(self, interaction: discord.Interaction):
        """Get system information from homelab"""
        await interaction.response.defer()
        
        try:
            system_data = await self.homelab_client.get_system_info()
            
            if 'error' in system_data:
                embed = EmbedBuilder.error(
                    "System Info Error",
                    f"Failed to fetch system info: {system_data['error']}"
                )
            else:
                embed = EmbedBuilder.system_info_embed(system_data)
            
            await interaction.followup.send(embed=embed)
            
        except Exception as e:
            embed = EmbedBuilder.error("Error", f"An unexpected error occurred: {str(e)}")
            await interaction.followup.send(embed=embed)

async def setup(bot):
    """Setup function for the cog"""
    await bot.add_cog(HomelabCommands(bot))
    logger.info("Homelab commands cog loaded")