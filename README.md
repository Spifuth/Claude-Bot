# Fenrir - Discord Bot

A modular Discord bot named Fenrir for managing and monitoring your homelab through Traefik reverse proxy at `nebulahost.tech`.

## 🐺 Features

- 🏓 **Core Commands**: Ping, status, and module management
- 🏠 **Homelab Module**: Monitor services and system information (optional)
- 🐳 **Docker Management**: List and restart containers
- 🔄 **Service Control**: Restart services and Docker Compose stacks
- 🔒 **Secure**: API key authentication for homelab endpoints
- 📦 **Modular**: Easy to extend with new functionality

## ⚙️ Prerequisites

- Python 3.8+
- Discord Bot Token
- Traefik reverse proxy with `proxy` network
- Domain: `nebulahost.tech` (API at `fenrir.nebulahost.tech`)

## 🚀 Quick Start

### 1. Discord Bot Setup

1. Go to [Discord Developer Portal](https://discord.com/developers/applications)
2. Create a new application named "Fenrir"
3. Go to "Bot" section and create a bot
4. Copy the bot token
5. Under "OAuth2" > "URL Generator", select:
   - Scopes: `bot`, `applications.commands`
   - Bot Permissions: `Send Messages`, `Use Slash Commands`
6. Use the generated URL to invite Fenrir to your server

### 2. Environment Setup

1. Navigate to your bot directory:
```bash
cd /home/nl/Projects/DiscordBot/Claude-Bot
```

2. Create virtual environment:
```bash
python -m venv venv
source venv/bin/activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create `.env` file:
```bash
cp .env.example .env
```

5. Edit `.env` with your values:
```env
DISCORD_BOT_TOKEN=your_discord_bot_token_here
ENABLE_HOMELAB=false  # Set to true when you want homelab features
HOMELAB_BASE_URL=https://fenrir.nebulahost.tech
HOMELAB_API_KEY=your_secret_api_key
```

### 3. Run Fenrir

**Option 1: Direct Python**
```bash
python bot.py
```

**Option 2: Docker (Recommended)**
```bash
docker-compose up -d
```

## 🏠 Homelab Integration (Optional)

The homelab module is **disabled by default**. To enable it:

1. Set `ENABLE_HOMELAB=true` in your `.env` file
2. Deploy the API server (see below)
3. Restart Fenrir

### Deploy Homelab API Server

```bash
# Copy API files to a separate directory
cp homelab_api.py Dockerfile.api requirements-api.txt docker-compose.api.yml /path/to/api/

# Deploy with docker-compose
cd /path/to/api/
docker-compose -f docker-compose.api.yml up -d
```

## 🤖 Available Commands

### Core Commands (Always Available)
- `/ping` - Check if Fenrir is awake
- `/status` - Show Fenrir's status and enabled modules

### Homelab Commands (When Module Enabled)
- `/homelab_status` - Check homelab services status
- `/docker_containers` - List Docker containers
- `/restart_service <name>` - Restart containers/services
- `/system_info` - Get system resource information

## 🌐 Traefik Configuration

Fenrir's API server will automatically configure with Traefik using these labels:

```yaml
labels:
  - "traefik.http.routers.fenrir-api.rule=Host(`fenrir.nebulahost.tech`)"
  - "traefik.http.routers.fenrir-api.tls=true"
  - "traefik.http.routers.fenrir-api.tls.certresolver=letsencrypt"
```

Make sure your Traefik setup includes:
- External `proxy` network
- SSL certificate resolver for `nebulahost.tech`

## 🔧 Directory Structure

```
/home/nl/Projects/DiscordBot/Claude-Bot/
├── bot.py                 # Main Fenrir bot
├── requirements.txt       # Bot dependencies
├── docker-compose.yml     # Bot deployment
├── Dockerfile            # Bot container
├── homelab_api.py        # Homelab API server
├── requirements-api.txt  # API dependencies
├── Dockerfile.api        # API container
└── .env                  # Configuration
```

## 🛡️ Security

- Homelab module disabled by default
- API key authentication for all homelab requests
- HTTPS through Traefik reverse proxy
- Non-root container execution
- Secure environment variable handling

## 🔮 Future Expansion

Fenrir is designed to be modular. Add new modules by:

1. Adding module configuration to `.env`
2. Adding module check in `FenrirBot.__init__()`
3. Creating commands with module validation
4. Updating the `/status` command

Example module structure:
```python
# In bot.py
self.modules_enabled = {
    'homelab': os.getenv('ENABLE_HOMELAB', 'false').lower() == 'true',
    'music': os.getenv('ENABLE_MUSIC', 'false').lower() == 'true',
    'gaming': os.getenv('ENABLE_GAMING', 'false').lower() == 'true',
}

@bot.tree.command(name="my_command", description="My new feature")
async def my_command(interaction: discord.Interaction):
    if not bot.modules_enabled['my_module']:
        await interaction.response.send_message("🔴 Module not enabled.", ephemeral=True)
        return
    # Command logic here
```

## Quick Start

### 1. Discord Bot Setup

1. Go to [Discord Developer Portal](https://discord.com/developers/applications)
2. Create a new application
3. Go to "Bot" section and create a bot
4. Copy the bot token
5. Under "OAuth2" > "URL Generator", select:
   - Scopes: `bot`, `applications.commands`
   - Bot Permissions: `Send Messages`, `Use Slash Commands`
6. Use the generated URL to invite the bot to your server

### 2. Environment Setup

1. Clone this repository:
```bash
git clone <your-repo-url>
cd claude-bot
```

2. Create virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create `.env` file (copy from `.env.example`):
```bash
cp .env.example .env
```

5. Edit `.env` with your values:
```env
DISCORD_BOT_TOKEN=your_discord_bot_token_here
HOMELAB_BASE_URL=https://api.your-domain.com
HOMELAB_API_KEY=your_secret_api_key
```

### 3. Run the Bot

```bash
python bot.py
```

## Homelab API Server Setup

The bot expects a REST API on your homelab server. You can use the provided `homelab_api.py` as a starting point.

### Install API Server Dependencies

```bash
pip install flask docker psutil requests
```

### Run API Server

```bash
export API_KEY=your_secret_api_key
python homelab_api.py
```

### Docker Deployment

1. Build and run with Docker Compose:
```bash
docker-compose up -d
```

2. Or build manually:
```bash
docker build -t claude-bot .
docker run -d --name claude-bot --env-file .env claude-bot
```

## Traefik Configuration

Add these labels to your API server's docker-compose.yml:

```yaml
labels:
  - "traefik.enable=true"
  - "traefik.http.routers.homelab-api.rule=Host(`api.your-domain.com`)"
  - "traefik.http.routers.homelab-api.tls=true"
  - "traefik.http.routers.homelab-api.tls.certresolver=letsencrypt"
  - "traefik.http.services.homelab-api.loadbalancer.server.port=5000"
```

## Available Slash Commands

- `/ping` - Check if bot is alive
- `/homelab_status` - Check homelab services status
- `/docker_containers` - List Docker containers
- `/restart_service <service_name>` - Restart a service or container
- `/system_info` - Get system resource information

## API Endpoints

The homelab API server provides these endpoints:

- `GET /api/status` - Overall system status
- `GET /api/system` - System resource information
- `GET /api/docker/containers` - List Docker containers
- `POST /api/services/<name>/restart` - Restart service/container
- `POST /api/docker/compose/<stack>/restart` - Restart Docker Compose stack
- `GET /api/traefik/services` - Get Traefik services (if configured)

## Security

- Use strong API keys
- Run API server behind Traefik with HTTPS
- Consider IP whitelisting for API access
- Keep bot token secure and never commit to version control

## Customization

### Adding New Commands

Add new slash commands in `bot.py`:

```python
@bot.tree.command(name="my_command", description="My custom command")
async def my_command(interaction: discord.Interaction):
    await interaction.response.send_message("Hello!")
```

### Adding New API Endpoints

Add new endpoints in `homelab_api.py`:

```python
@app.route('/api/my-endpoint')
@require_auth
def my_endpoint():
    return jsonify({'message': 'Hello from API!'})
```

## Troubleshooting

### Bot Not Responding
- Check bot token is correct
- Ensure bot has proper permissions in Discord server
- Check bot logs for errors

### API Connection Issues
- Verify `HOMELAB_BASE_URL` is correct
- Check API server is running and accessible
- Verify API key matches between bot and server
- Check Traefik routing if using reverse proxy

### Container Management Issues
- Ensure API server has Docker socket access
- Check user permissions for Docker commands
- Verify service names match actual container/service names

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## License

This project is released into the public domain under the Unlicense. See LICENSE file for details.