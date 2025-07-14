"""
Enhanced Attachment Logging - Complete File URL and Metadata Preservation
Captures all attachment details including URLs before they become inaccessible
"""

import discord
from discord.ext import commands
import logging
import json
from datetime import datetime
from typing import Dict, List, Any, Optional
from utils.bot_logger import log_event, log_error, debug_dump

logger = logging.getLogger(__name__)


class AttachmentLogger:
    """Specialized logger for Discord attachments with URL preservation"""

    def __init__(self):
        self.setup_attachment_logger()

        # File type categorization
        self.file_types = {
            'images': {'.png', '.jpg', '.jpeg', '.gif', '.webp', '.bmp', '.svg', '.tiff', '.ico'},
            'documents': {'.pdf', '.doc', '.docx', '.txt', '.rtf', '.odt', '.xls', '.xlsx', '.ppt', '.pptx'},
            'videos': {'.mp4', '.avi', '.mov', '.wmv', '.flv', '.webm', '.mkv', '.m4v'},
            'audio': {'.mp3', '.wav', '.flac', '.aac', '.ogg', '.wma', '.m4a'},
            'archives': {'.zip', '.rar', '.7z', '.tar', '.gz', '.bz2'},
            'code': {'.py', '.js', '.html', '.css', '.java', '.cpp', '.c', '.php', '.rb', '.go'}
        }

    def setup_attachment_logger(self):
        """Setup specialized logger for attachments"""
        self.attachment_logger = logging.getLogger('Fenrir.attachments')
        self.attachment_logger.setLevel(logging.INFO)

        # File handler for attachment logs
        attachment_file = logging.FileHandler('logs/attachments.log', encoding='utf-8')
        attachment_file.setLevel(logging.INFO)
        formatter = logging.Formatter(
            '%(asctime)s | %(levelname)s | %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        attachment_file.setFormatter(formatter)
        self.attachment_logger.addHandler(attachment_file)

    def categorize_file(self, filename: str) -> str:
        """Categorize file by extension"""
        filename_lower = filename.lower()
        for category, extensions in self.file_types.items():
            if any(filename_lower.endswith(ext) for ext in extensions):
                return category
        return 'other'

    def extract_attachment_data(self, attachment: discord.Attachment) -> Dict[str, Any]:
        """Extract comprehensive attachment data"""
        return {
            'id': attachment.id,
            'filename': attachment.filename,
            'url': attachment.url,
            'proxy_url': attachment.proxy_url,
            'size_bytes': attachment.size,
            'size_mb': round(attachment.size / (1024 * 1024), 2),
            'content_type': getattr(attachment, 'content_type', None),
            'category': self.categorize_file(attachment.filename),
            'width': getattr(attachment, 'width', None),
            'height': getattr(attachment, 'height', None),
            'is_spoiler': attachment.is_spoiler(),
            'extracted_at': datetime.utcnow().isoformat()
        }

    def log_message_with_attachments(self, message: discord.Message, action: str):
        """Log message with comprehensive attachment details"""
        if not message.attachments:
            return

        # Extract message metadata
        message_data = {
            'message_id': str(message.id),
            'author': f"{message.author} ({message.author.id})",
            'channel': f"#{message.channel.name}" if hasattr(message.channel, 'name') else str(message.channel),
            'guild': f"{message.guild.name} ({message.guild.id})" if message.guild else "DM",
            'action': action,
            'timestamp': datetime.utcnow().isoformat(),
            'content_length': len(message.content) if message.content else 0,
            'attachment_count': len(message.attachments),
            'attachments': []
        }

        # Extract detailed attachment data
        total_size = 0
        categories = {}

        for attachment in message.attachments:
            attachment_data = self.extract_attachment_data(attachment)
            message_data['attachments'].append(attachment_data)

            total_size += attachment.size
            category = attachment_data['category']
            categories[category] = categories.get(category, 0) + 1

            # Log individual attachment
            self.attachment_logger.info(f"📎 ATTACHMENT {action.upper()}: {attachment.filename}")
            self.attachment_logger.info(f"   🆔 ID: {attachment.id}")
            self.attachment_logger.info(f"   🔗 URL: {attachment.url}")
            self.attachment_logger.info(f"   📏 Size: {attachment_data['size_mb']} MB")
            self.attachment_logger.info(f"   📂 Category: {category}")
            if attachment_data['content_type']:
                self.attachment_logger.info(f"   🏷️  Type: {attachment_data['content_type']}")
            if attachment_data['width'] and attachment_data['height']:
                self.attachment_logger.info(f"   📐 Dimensions: {attachment_data['width']}x{attachment_data['height']}")

        # Log summary
        message_data['total_size_mb'] = round(total_size / (1024 * 1024), 2)
        message_data['categories'] = categories

        self.attachment_logger.info(f"📋 MESSAGE {action.upper()} SUMMARY:")
        self.attachment_logger.info(f"   💬 Message: {message_data['message_id']}")
        self.attachment_logger.info(f"   👤 Author: {message_data['author']}")
        self.attachment_logger.info(f"   📍 Location: {message_data['guild']} > {message_data['channel']}")
        self.attachment_logger.info(
            f"   📎 Attachments: {len(message.attachments)} files ({message_data['total_size_mb']} MB)")
        self.attachment_logger.info(f"   📂 Categories: {json.dumps(categories)}")

        # Log full data as JSON for parsing
        self.attachment_logger.info(f"📊 FULL_DATA: {json.dumps(message_data, indent=2)}")

        # Also log to main interaction logger
        log_event(f"attachments_{action}", message_data)

        return message_data


# Global attachment logger
attachment_logger = AttachmentLogger()


def log_attachments(message: discord.Message, action: str) -> Optional[Dict[str, Any]]:
    """Quick function to log message attachments"""
    return attachment_logger.log_message_with_attachments(message, action)


# Enhanced logging functions for the existing logging cog
def enhanced_on_message_delete_logging(message: discord.Message):
    """Enhanced message delete logging with preserved attachment URLs"""
    if not message.attachments:
        return None

    logger.info(f"🔍 DEBUGGING MESSAGE DELETE WITH ATTACHMENTS:")
    logger.info(f"   Message ID: {message.id}")
    logger.info(f"   Author: {message.author} ({message.author.id})")
    logger.info(f"   Attachments: {len(message.attachments)}")

    # Extract and preserve all attachment data BEFORE deletion
    preserved_attachments = []

    for i, attachment in enumerate(message.attachments):
        attachment_data = {
            'index': i,
            'id': attachment.id,
            'filename': attachment.filename,
            'size': attachment.size,
            'url': attachment.url,  # This is what you found!
            'proxy_url': attachment.proxy_url,
            'content_type': getattr(attachment, 'content_type', None),
            'width': getattr(attachment, 'width', None),
            'height': getattr(attachment, 'height', None),
            'is_spoiler': attachment.is_spoiler(),
            'preserved_at': datetime.utcnow().isoformat()
        }

        preserved_attachments.append(attachment_data)

        # Log each attachment URL for debugging
        logger.info(f"   📎 Attachment {i + 1}: {attachment.filename}")
        logger.info(f"      🔗 URL: {attachment.url}")
        logger.info(f"      📏 Size: {attachment.size} bytes")
        logger.info(f"      🏷️  Type: {attachment_data['content_type']}")

        # Debug dump the entire attachment object
        debug_dump({
            'filename': attachment.filename,
            'url': attachment.url,
            'proxy_url': attachment.proxy_url,
            'size': attachment.size,
            'content_type': getattr(attachment, 'content_type', None),
            'id': attachment.id
        }, f"Attachment {i + 1} Full Data")

    # Log the comprehensive attachment data
    log_event("message_delete_with_attachments", {
        'message_id': str(message.id),
        'author_id': str(message.author.id),
        'guild_id': str(message.guild.id) if message.guild else None,
        'channel_id': str(message.channel.id),
        'attachment_count': len(message.attachments),
        'preserved_attachments': preserved_attachments,
        'total_size_bytes': sum(att.size for att in message.attachments),
        'deletion_timestamp': datetime.utcnow().isoformat()
    })

    # Also use the specialized attachment logger
    return log_attachments(message, "deleted")


def enhanced_on_message_send_logging(message: discord.Message):
    """Enhanced message send logging with attachment URLs"""
    if not message.attachments:
        return None

    logger.info(f"📤 MESSAGE SENT WITH ATTACHMENTS:")
    logger.info(f"   Message ID: {message.id}")
    logger.info(f"   Author: {message.author} ({message.author.id})")
    logger.info(f"   Attachments: {len(message.attachments)}")

    for i, attachment in enumerate(message.attachments):
        logger.info(f"   📎 Attachment {i + 1}: {attachment.filename}")
        logger.info(f"      🔗 URL: {attachment.url}")
        logger.info(f"      📏 Size: {attachment.size} bytes")

    return log_attachments(message, "sent")


# Function to analyze attachment URLs
def analyze_attachment_url(url: str) -> Dict[str, Any]:
    """Analyze Discord attachment URL structure"""
    import re
    from urllib.parse import urlparse, parse_qs

    parsed = urlparse(url)
    analysis = {
        'domain': parsed.netloc,
        'path': parsed.path,
        'is_discord_cdn': 'discord' in parsed.netloc.lower(),
        'is_media_proxy': 'media.discordapp' in parsed.netloc.lower(),
        'full_url': url
    }

    # Extract Discord-specific URL components
    if analysis['is_discord_cdn']:
        # Discord CDN URLs typically have this structure:
        # https://cdn.discordapp.com/attachments/channel_id/message_id/filename
        path_parts = parsed.path.strip('/').split('/')
        if len(path_parts) >= 4 and path_parts[0] == 'attachments':
            analysis.update({
                'url_type': 'discord_cdn',
                'channel_id': path_parts[1],
                'message_id': path_parts[2],
                'filename': path_parts[3]
            })

    return analysis


# Function to test attachment URL accessibility
async def test_attachment_accessibility(url: str) -> Dict[str, Any]:
    """Test if an attachment URL is still accessible"""
    import aiohttp
    import asyncio

    try:
        async with aiohttp.ClientSession() as session:
            start_time = datetime.utcnow()
            async with session.head(url, timeout=5) as response:
                end_time = datetime.utcnow()

                return {
                    'url': url,
                    'accessible': response.status == 200,
                    'status_code': response.status,
                    'response_time_ms': (end_time - start_time).total_seconds() * 1000,
                    'content_type': response.headers.get('content-type'),
                    'content_length': response.headers.get('content-length'),
                    'tested_at': start_time.isoformat()
                }
    except Exception as e:
        return {
            'url': url,
            'accessible': False,
            'error': str(e),
            'tested_at': datetime.utcnow().isoformat()
        }


# Utility function for debugging attachment data
def debug_message_attachments(message: discord.Message, action: str = "debug"):
    """Debug function to examine all attachment data"""
    if not message.attachments:
        logger.info(f"📋 No attachments in message {message.id}")
        return

    logger.info(f"🔍 DEBUGGING MESSAGE ATTACHMENTS ({action.upper()}):")
    logger.info(f"   Message ID: {message.id}")
    logger.info(f"   Attachment Count: {len(message.attachments)}")

    for i, attachment in enumerate(message.attachments):
        logger.info(f"\n   📎 ATTACHMENT {i + 1}:")
        logger.info(f"      Filename: {attachment.filename}")
        logger.info(f"      ID: {attachment.id}")
        logger.info(f"      Size: {attachment.size} bytes ({attachment.size / 1024:.1f} KB)")
        logger.info(f"      URL: {attachment.url}")
        logger.info(f"      Proxy URL: {attachment.proxy_url}")
        logger.info(f"      Content Type: {getattr(attachment, 'content_type', 'Unknown')}")
        logger.info(f"      Is Spoiler: {attachment.is_spoiler()}")

        # Additional properties for images
        if hasattr(attachment, 'width') and attachment.width:
            logger.info(f"      Dimensions: {attachment.width}x{attachment.height}")

        # Analyze the URL structure
        url_analysis = analyze_attachment_url(attachment.url)
        logger.info(f"      URL Analysis: {json.dumps(url_analysis, indent=8)}")

        # Full debug dump of attachment object
        debug_dump(attachment_logger.extract_attachment_data(attachment), f"Attachment {i + 1} Complete Data")