#!/usr/bin/env python3
"""
Migration Script for Fenrir Bot
Converts from monolithic to modular structure
"""

import os
import shutil
import sys
from pathlib import Path

def create_directory_structure():
    """Create the new directory structure"""
    directories = [
        "cogs",
        "utils", 
        "logs",
        "misc"
    ]
    
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
        print(f"✅ Created directory: {directory}/")
    
    # Create __init__.py files
    init_files = ["cogs/__init__.py", "utils/__init__.py"]
    for init_file in init_files:
        Path(init_file).touch()
        print(f"✅ Created: {init_file}")

def backup_old_files():
    """Backup the old bot.py"""
    if os.path.exists("bot.py"):
        shutil.copy2("bot.py", "bot_old.py")
        print("📁 Backed up old bot.py to bot_old.py")
    
    if os.path.exists("cleanup_commands.py"):
        shutil.move("cleanup_commands.py", "misc/cleanup_commands.py")
        print("📁 Moved cleanup_commands.py to misc/")

def check_requirements():
    """Check if additional packages are needed"""
    print("\n📦 Checking requirements...")
    
    # Check if current requirements are sufficient
    with open("requirements.txt", "r") as f:
        current_requirements = f.read()
    
    if "aiohttp" in current_requirements and "discord.py" in current_requirements:
        print("✅ Current requirements.txt looks good!")
    else:
        print("⚠️  You may need to update requirements.txt")

def update_env_file():
    """Check and suggest .env updates"""
    print("\n🔧 Checking .env configuration...")
    
    if os.path.exists(".env"):
        with open(".env", "r") as f:
            env_content = f.read()
        
        suggestions = []
        
        if "ENABLE_HOMELAB" not in env_content:
            suggestions.append("ENABLE_HOMELAB=false")
        
        if "LOG_LEVEL" not in env_content:
            suggestions.append("LOG_LEVEL=INFO")
        
        if "BOT_PREFIX" not in env_content:
            suggestions.append("BOT_PREFIX=!")
        
        if suggestions:
            print("💡 Consider adding these to your .env file:")
            for suggestion in suggestions:
                print(f"   {suggestion}")
        else:
            print("✅ .env file looks good!")
    else:
        print("⚠️  No .env file found. Create one with your configuration.")

def migration_instructions():
    """Print migration instructions"""
    print("\n" + "="*50)
    print("🐺 FENRIR BOT MIGRATION COMPLETE")
    print("="*50)
    
    instructions = """
NEXT STEPS:

1. 📁 File Structure Created:
   ├── cogs/          # Command modules
   ├── utils/         # Utility functions  
   ├── logs/          # Log files
   └── misc/          # Deployment files

2. 📝 Replace your bot.py with the new modular version
   - Your old bot.py is backed up as bot_old.py

3. 🔧 Copy the new files from the artifacts:
   - config.py
   - utils/api_client.py
   - utils/embeds.py
   - cogs/core.py
   - cogs/admin.py
   - cogs/homelab.py

4. 🗑️ Remove the sync code from on_ready after first run:
   - The new bot handles this better with command management

5. 🚀 Start your new modular bot:
   python bot.py

6. 🔄 Test with /sync_commands if needed

BENEFITS OF NEW STRUCTURE:
- ✅ Organized code by functionality
- ✅ Easy to add new command modules
- ✅ Better error handling and logging
- ✅ Cleaner configuration management
- ✅ Easier debugging and maintenance

Need help? Check the migration guide!
"""
    
    print(instructions)

def main():
    """Run the migration"""
    print("🐺 Starting Fenrir Bot Migration...")
    print("Converting from monolithic to modular structure")
    print("-" * 50)
    
    # Check if we're in the right directory
    if not os.path.exists("bot.py"):
        print("❌ No bot.py found. Are you in the right directory?")
        sys.exit(1)
    
    try:
        create_directory_structure()
        backup_old_files()
        check_requirements()
        update_env_file()
        migration_instructions()
        
        print("\n🎉 Migration structure created successfully!")
        print("📋 Follow the instructions above to complete the migration.")
        
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()