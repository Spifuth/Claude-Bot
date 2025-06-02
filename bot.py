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
        
        # Force sync commands to all guilds (remove this after first run)
        for guild in self.guilds:
            try:
                synced = await self.tree.sync(guild=guild)
                logger.info(f"Synced {len(synced)} commands to {guild.name}")
            except Exception as e:
                logger.error(f"Failed to sync to {guild.name}: {e}")
    
        logger.info("🎉 All commands synced! You can now use /sync_commands for future updates.")

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
    
    
    async def sync_commands_to_guild(self, guild_id: int = None):
        """Sync commands to a specific guild or globally"""
        try:
            if guild_id:
                guild = discord.Object(id=guild_id)
                synced = await self.tree.sync(guild=guild)
                return f"Synced {len(synced)} commands to guild {guild_id}"
            else:
                synced = await self.tree.sync()
                return f"Synced {len(synced)} commands globally"
        except Exception as e:
            return f"Failed to sync: {str(e)}"
    
    async def clear_commands_from_guild(self, guild_id: int = None):
        """Clear all commands from a guild or globally"""
        try:
            if guild_id:
                guild = discord.Object(id=guild_id)
                self.tree.clear_commands(guild=guild)
                await self.tree.sync(guild=guild)
                return f"Cleared commands from guild {guild_id}"
            else:
                self.tree.clear_commands(guild=None)
                await self.tree.sync()
                return "Cleared global commands"
        except Exception as e:
            return f"Failed to clear commands: {str(e)}"
        

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

@bot.tree.command(name="sync_commands", description="Sync slash commands (Admin only)")
@app_commands.describe(
    scope="Where to sync commands: 'global', 'guild', or 'clear_global', 'clear_guild'"
)
async def sync_commands(interaction: discord.Interaction, scope: str = "guild"):
    """Sync slash commands - useful for updating command list"""
    
    # Check if user has administrator permissions
    if not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message("❌ You need administrator permissions to use this command.", ephemeral=True)
        return
    
    await interaction.response.defer(ephemeral=True)
    
    try:
        if scope.lower() == "global":
            result = await bot.sync_commands_to_guild(None)
            embed = discord.Embed(
                title="🌍 Global Command Sync",
                description=result,
                color=discord.Color.green()
            )
            embed.add_field(
                name="Note", 
                value="Global commands may take up to 1 hour to update across all servers.", 
                inline=False
            )
            
        elif scope.lower() == "guild":
            guild_id = interaction.guild_id
            result = await bot.sync_commands_to_guild(guild_id)
            embed = discord.Embed(
                title="🏠 Guild Command Sync",
                description=result,
                color=discord.Color.blue()
            )
            embed.add_field(
                name="Note", 
                value="Guild commands update immediately in this server.", 
                inline=False
            )
            
        elif scope.lower() == "clear_global":
            result = await bot.clear_commands_from_guild(None)
            embed = discord.Embed(
                title="🗑️ Global Commands Cleared",
                description=result,
                color=discord.Color.orange()
            )
            embed.add_field(
                name="Warning", 
                value="All global commands have been removed. Use 'global' scope to re-add them.", 
                inline=False
            )
            
        elif scope.lower() == "clear_guild":
            guild_id = interaction.guild_id
            result = await bot.clear_commands_from_guild(guild_id)
            embed = discord.Embed(
                title="🗑️ Guild Commands Cleared",
                description=result,
                color=discord.Color.orange()
            )
            embed.add_field(
                name="Warning", 
                value="All guild commands have been removed. Use 'guild' scope to re-add them.", 
                inline=False
            )
            
        else:
            embed = discord.Embed(
                title="❌ Invalid Scope",
                description="Valid options: `global`, `guild`, `clear_global`, `clear_guild`",
                color=discord.Color.red()
            )
        
        await interaction.followup.send(embed=embed)
        
    except Exception as e:
        embed = discord.Embed(
            title="❌ Command Sync Error",
            description=f"An error occurred: {str(e)}",
            color=discord.Color.red()
        )
        await interaction.followup.send(embed=embed)

@bot.tree.command(name="list_commands", description="List all registered slash commands")
async def list_commands(interaction: discord.Interaction):
    """List all currently registered slash commands"""
    
    embed = discord.Embed(
        title="📝 Registered Slash Commands",
        color=discord.Color.purple()
    )
    
    # Get guild commands
    guild_commands = bot.tree.get_commands(guild=interaction.guild)
    if guild_commands:
        guild_cmd_list = [f"• `/{cmd.name}` - {cmd.description}" for cmd in guild_commands]
        embed.add_field(
            name=f"🏠 Guild Commands ({len(guild_commands)})",
            value="\n".join(guild_cmd_list) if guild_cmd_list else "None",
            inline=False
        )
    
    # Get global commands
    global_commands = bot.tree.get_commands(guild=None)
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

@bot.tree.command(name="bot_info", description="Get detailed information about Fenrir")
async def bot_info(interaction: discord.Interaction):
    """Get detailed bot information"""
    embed = discord.Embed(
        title="🐺 Fenrir Bot Information",
        color=discord.Color.gold()
    )
    
    # Basic info
    embed.add_field(name="Bot Name", value=bot.user.name, inline=True)
    embed.add_field(name="Bot ID", value=bot.user.id, inline=True)
    embed.add_field(name="Latency", value=f"{round(bot.latency * 1000)}ms", inline=True)
    
    # Server info
    embed.add_field(name="Guilds", value=len(bot.guilds), inline=True)
    embed.add_field(name="Users", value=len(bot.users), inline=True)
    embed.add_field(name="Commands", value=len(bot.tree.get_commands()), inline=True)
    
    # Module status
    modules_status = []
    for module, enabled in bot.modules_enabled.items():
        status_emoji = "🟢" if enabled else "🔴"
        modules_status.append(f"{status_emoji} {module.title()}")
    
    embed.add_field(name="Modules", value="\n".join(modules_status), inline=False)
    
    # Add bot avatar
    if bot.user.avatar:
        embed.set_thumbnail(url=bot.user.avatar.url)
    
    embed.set_footer(text=f"Discord.py version: {discord.__version__}")
    
    await interaction.response.send_message(embed=embed)

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
