# 🌐 FastAPI Web Backend Implementation Plan

## 🎯 **Project Goal**
Create a web interface for managing your Fenrir Discord bot configuration, replacing Discord slash commands with a user-friendly web dashboard.

## 📋 **What We'll Build**

### Core Features
- 🔐 **Discord OAuth Authentication** - Users login with Discord
- 👥 **Guild Management** - Show servers where user has admin permissions  
- ⚙️ **Logging Configuration** - Web interface for all 8 logging event types
- 📊 **Real-time Status** - Show current bot status in each guild
- 🔄 **Live Updates** - Changes apply immediately to your Discord bot

### API Endpoints
```
# Authentication
POST /auth/discord/login     # Redirect to Discord OAuth
GET  /auth/discord/callback  # Handle OAuth callback
GET  /auth/me               # Get current user info
POST /auth/logout           # Logout user

# Guild Management
GET  /api/guilds            # User's manageable guilds
GET  /api/guilds/{id}       # Guild details
GET  /api/guilds/{id}/channels # Text channels in guild

# Configuration
GET  /api/config/{guild_id}        # Get guild config
PUT  /api/config/{guild_id}        # Update guild config
GET  /api/config/{guild_id}/events # Get event settings
PUT  /api/config/{guild_id}/events # Update event settings

# Bot Status  
GET  /api/bot/status              # Bot health and stats
GET  /api/bot/guilds/{id}/status  # Bot status in specific guild
```

## 🛠️ **Technology Stack**

### Backend
- **FastAPI** - Modern, fast Python web framework
- **fastapi-discord** - Discord OAuth integration library
- **SQLite** - Your existing database (no changes needed!)
- **Pydantic** - Data validation and API documentation
- **uvicorn** - ASGI server

### Authentication
- **Discord OAuth 2.0** - Secure login with Discord
- **JWT tokens** - Session management
- **Permission checking** - Verify guild admin permissions

## 📅 **3-Week Implementation Timeline**

### **Week 1: Foundation & Auth**

#### Day 1-2: Project Setup
```bash
# Create web backend directory
mkdir web-backend
cd web-backend

# Install dependencies
pip install fastapi uvicorn fastapi-discord python-jose[cryptography] aiosqlite
```

#### Day 3-4: Discord OAuth Setup
- Configure Discord application OAuth settings
- Implement login/logout endpoints
- Set up JWT token handling
- Test authentication flow

#### Day 5-7: Database Integration
- Connect to your existing SQLite database
- Create API models (Pydantic schemas)
- Test database operations
- Implement basic CRUD operations

### **Week 2: Core API Development**

#### Day 8-10: Guild Management
- Implement guild listing with permission checks
- Add guild details and channel endpoints
- Verify bot presence in guilds
- Test with real Discord data

#### Day 11-13: Configuration API
- Build configuration read/write endpoints
- Implement event management
- Add validation and error handling
- Test with your existing bot database

#### Day 14: Integration Testing
- Test all endpoints with Postman/Insomnia
- Verify database updates reflect in Discord bot
- Performance testing and optimization

### **Week 3: Polish & Production**

#### Day 15-17: Security & Validation
- Add request validation
- Implement rate limiting
- Security headers and CORS setup
- Error handling and logging

#### Day 18-19: Documentation & Testing
- Generate OpenAPI documentation
- Write unit tests for critical endpoints
- Integration tests with bot database
- API documentation

#### Day 20-21: Deployment Preparation
- Docker containerization
- Environment configuration
- Production database setup
- Monitoring and health checks

## 🔧 **Key Components**

### 1. **Discord OAuth Client**
```python
from fastapi_discord import DiscordOAuthClient

discord_oauth = DiscordOAuthClient(
    client_id="YOUR_BOT_CLIENT_ID",
    client_secret="YOUR_BOT_CLIENT_SECRET", 
    redirect_uri="http://localhost:8000/auth/discord/callback",
    scopes=("identify", "guilds")
)
```

### 2. **Database Models** (reusing your existing database)
```python
class GuildConfig(BaseModel):
    guild_id: str
    guild_name: str
    logging_enabled: bool
    log_channel_id: Optional[str]
    show_avatars: bool = True
    show_timestamps: bool = True
    embed_color: str = "#3498db"

class LogEvent(BaseModel):
    guild_id: str
    event_type: str
    enabled: bool
```

### 3. **Permission Checking**
```python
async def check_guild_permissions(user_id: str, guild_id: str) -> bool:
    # Check if user has admin permissions in guild
    # Verify bot is present in guild
    # Return True if user can manage bot settings
```

## 🔗 **Integration with Your Existing Bot**

### No Bot Changes Required! ✅
Your Discord bot will automatically pick up configuration changes because it already reads from the SQLite database.

### Real-time Updates
- Web interface updates database
- Bot reads from database on next event
- Changes take effect immediately

### Shared Database
```
web-backend/     ← New FastAPI server
├── main.py
├── models/
├── routes/
└── requirements.txt

your-bot/        ← Your existing bot (no changes!)  
├── bot.py
├── cogs/
├── utils/
└── data/
    └── fenrir.db ← Shared database
```

## 🎯 **Benefits of This Approach**

### For Users
- ✅ **Better UX** - Web interface instead of Discord commands
- ✅ **Visual Configuration** - See all settings at once
- ✅ **Guild Overview** - Manage multiple servers easily
- ✅ **Real-time Status** - See bot health and activity

### For You
- ✅ **Professional Interface** - Looks more polished
- ✅ **Easier Support** - Users can self-configure
- ✅ **Scalable** - Foundation for future features
- ✅ **API-First** - Can add mobile app later

## 🚀 **Getting Started**

### Prerequisites
1. Your existing Fenrir bot (✅ you have this)
2. Discord application with OAuth2 setup
3. Python 3.8+ environment
4. Your current SQLite database

### First Steps
1. **Create Discord OAuth App**
   - Go to Discord Developer Portal
   - Add redirect URI: `http://localhost:8000/auth/discord/callback`
   - Note down Client ID and Secret

2. **Set up FastAPI project structure**
3. **Implement basic authentication**
4. **Test with your existing database**

## 🔧 **Configuration Changes Needed**

### Environment Variables (add to .env)
```env
# Existing bot config (no changes)
DISCORD_BOT_TOKEN=your_bot_token

# New web backend config  
WEB_CLIENT_ID=your_oauth_client_id
WEB_CLIENT_SECRET=your_oauth_client_secret
WEB_SECRET_KEY=your_jwt_secret_key
WEB_REDIRECT_URI=http://localhost:8000/auth/discord/callback
```

### No Database Changes Required! ✅
Your existing SQLite database with `guild_configs` and `log_events` tables works perfectly.

## 📊 **Success Metrics**

By the end of Week 3, you'll have:
- ✅ Working Discord OAuth login
- ✅ Web interface showing user's manageable guilds
- ✅ Configuration pages for all 8 logging events
- ✅ Real-time bot status display
- ✅ Complete API documentation
- ✅ Production-ready deployment

## 🎯 **After Web Backend**

Once complete, you'll be ready for:
- **Week 4**: React frontend dashboard
- **Week 5**: Advanced features (analytics, logs viewer)
- **Week 6**: Mobile-responsive design
- **Week 7**: Production deployment & monitoring

Ready to start building the web backend? 🚀