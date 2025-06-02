"""
Discord Embed Utilities
Common embed templates and utilities
"""

import discord
from typing import List, Dict, Any, Optional

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
    
    @staticmethod
    def status_embed(data: Dict[str, Any], title: str = "Status") -> discord.Embed:
        """Create a status embed from API data"""
        if 'error' in data:
            return EmbedBuilder.error("Status Error", data['error'])
        
        embed = discord.Embed(
            title=f"🔍 {title}",
            color=discord.Color.green()
        )
        
        for key, value in data.items():
            if key.startswith('_'):  # Skip internal keys
                continue
                
            # Format the field name
            field_name = key.replace('_', ' ').title()
            
            # Format the value
            if isinstance(value, bool):
                field_value = "🟢 Yes" if value else "🔴 No"
            elif isinstance(value, str) and value in ['up', 'online']:
                field_value = "🟢 Online"
            elif isinstance(value, str) and value in ['down', 'offline']:
                field_value = "🔴 Offline"
            else:
                field_value = str(value)
            
            embed.add_field(name=field_name, value=field_value, inline=True)
        
        return embed
    
    @staticmethod
    def container_list_embed(containers: List[Dict], title: str = "Docker Containers") -> discord.Embed:
        """Create an embed for Docker container list"""
        embed = discord.Embed(
            title=f"🐳 {title}",
            color=discord.Color.blue()
        )
        
        if not containers:
            embed.description = "No containers found"
            return embed
        
        # Limit to avoid embed limits
        for container in containers[:10]:
            name = container.get('name', 'Unknown')
            status = container.get('status', 'Unknown')
            image = container.get('image', 'N/A')
            
            # Status emoji
            if status.startswith('Up'):
                status_emoji = "🟢"
            elif status.startswith('Exited'):
                status_emoji = "🔴"
            else:
                status_emoji = "🟡"
            
            embed.add_field(
                name=f"{status_emoji} {name}",
                value=f"**Image:** {image}\n**Status:** {status}",
                inline=True
            )
        
        if len(containers) > 10:
            embed.set_footer(text=f"Showing 10 of {len(containers)} containers")
        
        return embed
    
    @staticmethod
    def system_info_embed(system_data: Dict[str, Any]) -> discord.Embed:
        """Create a system information embed"""
        if 'error' in system_data:
            return EmbedBuilder.error("System Info Error", system_data['error'])
        
        embed = discord.Embed(
            title="💻 System Information",
            color=discord.Color.purple()
        )
        
        # CPU
        if 'cpu_usage' in system_data:
            cpu_value = f"{system_data['cpu_usage']}%"
            embed.add_field(name="CPU Usage", value=cpu_value, inline=True)
        
        # Memory
        if 'memory_usage' in system_data:
            memory_value = f"{system_data['memory_usage']}%"
            if 'memory_used_gb' in system_data and 'memory_total_gb' in system_data:
                memory_value += f"\n({system_data['memory_used_gb']:.1f}GB / {system_data['memory_total_gb']:.1f}GB)"
            embed.add_field(name="Memory Usage", value=memory_value, inline=True)
        
        # Disk
        if 'disk_usage' in system_data:
            disk_value = f"{system_data['disk_usage']}%"
            if 'disk_used_gb' in system_data and 'disk_total_gb' in system_data:
                disk_value += f"\n({system_data['disk_used_gb']:.1f}GB / {system_data['disk_total_gb']:.1f}GB)"
            embed.add_field(name="Disk Usage", value=disk_value, inline=True)
        
        # Uptime
        if 'uptime' in system_data:
            embed.add_field(name="Uptime", value=system_data['uptime'], inline=True)
        
        return embed