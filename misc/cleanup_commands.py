import discord
from discord.ext import commands
import os
from dotenv import load_dotenv

load_dotenv()

class CleanupBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        super().__init__(command_prefix='!', intents=intents)

    async def setup_hook(self):
        print("🧹 Starting command cleanup...")
        
        # Clear all global commands
        self.tree.clear_commands(guild=None)
        global_sync = await self.tree.sync()
        print(f"✅ Cleared global commands. Synced: {len(global_sync)}")
        
        # Clear commands from all guilds the bot is in
        for guild in self.guilds:
            self.tree.clear_commands(guild=guild)
            guild_sync = await self.tree.sync(guild=guild)
            print(f"✅ Cleared commands from {guild.name}. Synced: {len(guild_sync)}")
        
        print("🎉 Cleanup complete! You can now restart your main bot.")
        await self.close()

if __name__ == "__main__":
    token = os.getenv('DISCORD_BOT_TOKEN')
    if not token:
        print("❌ DISCORD_BOT_TOKEN not found!")
        exit(1)
    
    cleanup_bot = CleanupBot()
    cleanup_bot.run(token)