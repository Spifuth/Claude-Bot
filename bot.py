import discord
from discord.ext import commands
from discord import app_commands
import aiohttp
import asyncio
import os
from dotenv import load_dotenv
import json
import logging
from typing import Optional

# Load environment variables
load_dotenv()

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class FenrirBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        super().__init__(command_prefix='!', intents=intents)
        
        # Homelab configuration
        self.homelab_base_url = os.getenv('HOMELAB_BASE_URL', 'https://fenrir.nebulahost.tech')
        self.api_key = os.getenv('HOMELAB_API_KEY', '')
        
        # Modular system for future expansion
        self.modules_enabled = {
            'homelab': os.getenv('ENABLE_HOMELAB', 'false').lower() == 'true',
            # Add more modules here as you expand
        }
        
    async def setup_hook(self):
        """Called when the bot is starting up"""
        await self.tree.sync()
        logger.info(f"Synced slash commands for {self.user}")

    async def on_ready(self):
        """Called when the bot is ready"""
        logger.info(f'🐺 Fenrir has awakened and connected to Discord!')
        logger.info(f'Bot is in {len(self.guilds)} guilds')
        logger.info(f'Homelab module: {"✅ Enabled" if self.modules_enabled["homelab"] else "❌ Disabled"}')

    async def make_homelab_request(self, endpoint: str, method: str = 'GET', data: dict = None) -> dict:
        """Make HTTP requests to homelab services through Traefik"""
        url = f"{self.homelab_base_url}/{endpoint.lstrip('/')}"
        headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json'
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                if method.upper() == 'GET':
                    async with session.get(url, headers=headers) as response:
                        return await response.json()
                elif method.upper() == 'POST':
                    async with session.post(url, headers=headers, json=data) as response:
                        return await response.json()
                elif method.upper() == 'PUT':
                    async with session.put(url, headers=headers, json=data) as response:
                        return await response.json()
                elif method.upper() == 'DELETE':
                    async with session.delete(url, headers=headers) as response:
                        return await response.json()
        except Exception as e:
            logger.error(f"Error making homelab request: {e}")
            return {"error": str(e)}

# Initialize bot
bot = FenrirBot()

@bot.tree.command(name="ping", description="Check if Fenrir is alive")
async def ping(interaction: discord.Interaction):
    """Simple ping command"""
    await interaction.response.send_message("🐺 Fenrir is awake!")

@bot.tree.command(name="status", description="Check Fenrir's status and available modules")
async def status(interaction: discord.Interaction):
    """Check bot status and enabled modules"""
    embed = discord.Embed(
        title="🐺 Fenrir Status",
        color=discord.Color.blue()
    )
    
    embed.add_field(name="Bot Status", value="🟢 Online", inline=True)
    embed.add_field(name="Latency", value=f"{round(bot.latency * 1000)}ms", inline=True)
    embed.add_field(name="Guilds", value=len(bot.guilds), inline=True)
    
    # Show enabled modules
    modules_status = []
    for module, enabled in bot.modules_enabled.items():
        status_emoji = "🟢" if enabled else "🔴"
        modules_status.append(f"{status_emoji} {module.title()}")
    
    embed.add_field(name="Modules", value="\n".join(modules_status), inline=False)
    
    await interaction.response.send_message(embed=embed)

# Homelab commands (only if module is enabled)
@bot.tree.command(name="homelab_status", description="Check the status of homelab services")
async def homelab_status(interaction: discord.Interaction):
    """Check homelab services status"""
    if not bot.modules_enabled['homelab']:
        await interaction.response.send_message("🔴 Homelab module is not enabled.", ephemeral=True)
        return
    await interaction.response.defer()
    
    try:
        # Example endpoint - adjust based on your actual services
        status_data = await bot.make_homelab_request('api/status')
        
        if 'error' in status_data:
            embed = discord.Embed(
                title="❌ Homelab Status Error",
                description=f"Failed to fetch status: {status_data['error']}",
                color=discord.Color.red()
            )
        else:
            embed = discord.Embed(
                title="🏠 Homelab Status",
                color=discord.Color.green()
            )
            
            # Add fields based on your actual response structure
            for service, status in status_data.items():
                embed.add_field(
                    name=service.replace('_', ' ').title(),
                    value="🟢 Online" if status == "up" else "🔴 Offline",
                    inline=True
                )
        
        await interaction.followup.send(embed=embed)
        
    except Exception as e:
        embed = discord.Embed(
            title="❌ Error",
            description=f"An error occurred: {str(e)}",
            color=discord.Color.red()
        )
        await interaction.followup.send(embed=embed)

@bot.tree.command(name="docker_containers", description="List Docker containers")
async def docker_containers(interaction: discord.Interaction):
    """List running Docker containers"""
    if not bot.modules_enabled['homelab']:
        await interaction.response.send_message("🔴 Homelab module is not enabled.", ephemeral=True)
        return
    await interaction.response.defer()
    
    try:
        containers_data = await bot.make_homelab_request('api/docker/containers')
        
        if 'error' in containers_data:
            embed = discord.Embed(
                title="❌ Docker Containers Error",
                description=f"Failed to fetch containers: {containers_data['error']}",
                color=discord.Color.red()
            )
        else:
            embed = discord.Embed(
                title="🐳 Docker Containers",
                color=discord.Color.blue()
            )
            
            # Adjust based on your actual API response
            if isinstance(containers_data, list):
                for container in containers_data[:10]:  # Limit to 10 for embed limits
                    status_emoji = "🟢" if container.get('status', '').startswith('Up') else "🔴"
                    embed.add_field(
                        name=f"{status_emoji} {container.get('name', 'Unknown')}",
                        value=f"Image: {container.get('image', 'N/A')}\nStatus: {container.get('status', 'N/A')}",
                        inline=True
                    )
            else:
                embed.description = "No containers found or unexpected response format"
        
        await interaction.followup.send(embed=embed)
        
    except Exception as e:
        embed = discord.Embed(
            title="❌ Error",
            description=f"An error occurred: {str(e)}",
            color=discord.Color.red()
        )
        await interaction.followup.send(embed=embed)

@bot.tree.command(name="restart_service", description="Restart a homelab service")
@app_commands.describe(service_name="Name of the service to restart")
async def restart_service(interaction: discord.Interaction, service_name: str):
    """Restart a specific service"""
    if not bot.modules_enabled['homelab']:
        await interaction.response.send_message("🔴 Homelab module is not enabled.", ephemeral=True)
        return
    await interaction.response.defer()
    
    try:
        restart_data = await bot.make_homelab_request(
            f'api/services/{service_name}/restart',
            method='POST'
        )
        
        if 'error' in restart_data:
            embed = discord.Embed(
                title="❌ Restart Failed",
                description=f"Failed to restart {service_name}: {restart_data['error']}",
                color=discord.Color.red()
            )
        else:
            embed = discord.Embed(
                title="✅ Service Restarted",
                description=f"Successfully restarted {service_name}",
                color=discord.Color.green()
            )
        
        await interaction.followup.send(embed=embed)
        
    except Exception as e:
        embed = discord.Embed(
            title="❌ Error",
            description=f"An error occurred: {str(e)}",
            color=discord.Color.red()
        )
        await interaction.followup.send(embed=embed)

@bot.tree.command(name="system_info", description="Get homelab system information")
async def system_info(interaction: discord.Interaction):
    """Get system information from homelab"""
    if not bot.modules_enabled['homelab']:
        await interaction.response.send_message("🔴 Homelab module is not enabled.", ephemeral=True)
        return
    await interaction.response.defer()
    
    try:
        system_data = await bot.make_homelab_request('api/system')
        
        if 'error' in system_data:
            embed = discord.Embed(
                title="❌ System Info Error",
                description=f"Failed to fetch system info: {system_data['error']}",
                color=discord.Color.red()
            )
        else:
            embed = discord.Embed(
                title="💻 System Information",
                color=discord.Color.purple()
            )
            
            # Adjust fields based on your actual API response
            if 'cpu_usage' in system_data:
                embed.add_field(name="CPU Usage", value=f"{system_data['cpu_usage']}%", inline=True)
            if 'memory_usage' in system_data:
                embed.add_field(name="Memory Usage", value=f"{system_data['memory_usage']}%", inline=True)
            if 'disk_usage' in system_data:
                embed.add_field(name="Disk Usage", value=f"{system_data['disk_usage']}%", inline=True)
            if 'uptime' in system_data:
                embed.add_field(name="Uptime", value=system_data['uptime'], inline=True)
        
        await interaction.followup.send(embed=embed)
        
    except Exception as e:
        embed = discord.Embed(
            title="❌ Error",
            description=f"An error occurred: {str(e)}",
            color=discord.Color.red()
        )
        await interaction.followup.send(embed=embed)

# Error handling
@bot.tree.error
async def on_app_command_error(interaction: discord.Interaction, error: app_commands.AppCommandError):
    """Handle slash command errors"""
    if isinstance(error, app_commands.CommandOnCooldown):
        await interaction.response.send_message(
            f"Command is on cooldown. Try again in {error.retry_after:.2f} seconds.",
            ephemeral=True
        )
    else:
        logger.error(f"Unexpected error: {error}")
        if not interaction.response.is_done():
            await interaction.response.send_message(
                "An unexpected error occurred. Please try again later.",
                ephemeral=True
            )

if __name__ == "__main__":
    # Get bot token from environment variable
    token = os.getenv('DISCORD_BOT_TOKEN')
    if not token:
        logger.error("DISCORD_BOT_TOKEN environment variable is required!")
        exit(1)
    
    bot.run(token)