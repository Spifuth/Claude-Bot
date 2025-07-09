"""
Attachment Logging Module - cogs/logging/attachment_logs.py
Handles file/image upload and deletion logging with enhanced URL preservation
"""

import discord
from discord.ext import commands
import logging
from datetime import datetime

from .base import LoggingModule
from utils.bot_logger import log_message, log_event, log_error

logger = logging.getLogger(__name__)


class AttachmentLogs(LoggingModule):
    """Handles attachment-related logging events"""

    def __init__(self, bot):
        super().__init__(bot)

        # Define event types this module handles
        self.event_types = {
            'image_send': 'Image/File Uploads',
            'image_delete': 'Image/File Deletions'
        }

        # Import enhanced attachment logging if available
        try:
            from utils.enhanced_attachment_logging import (
                enhanced_on_message_send_logging,
                enhanced_on_message_delete_logging,
                debug_message_attachments
            )
            self.enhanced_logging = True
            self.enhanced_send_logging = enhanced_on_message_send_logging
            self.enhanced_delete_logging = enhanced_on_message_delete_logging
            self.debug_attachments = debug_message_attachments
            logger.info("Enhanced attachment logging available")
        except ImportError:
            self.enhanced_logging = False
            logger.warning("Enhanced attachment logging not available")

    async def setup(self):
        """Setup method called when module is loaded"""
        logger.info("Attachment logging module initialized")

    async def on_message(self, message):
        """Log messages with attachments/images - ENHANCED with URL preservation"""
        # Skip bot messages
        if message.author.bot:
            return

        # Skip if no guild (DMs, etc.)
        if not message.guild:
            return

        # Skip if no attachments
        if not message.attachments:
            return

        # Enhanced attachment logging if available
        if self.enhanced_logging:
            try:
                self.debug_attachments(message, "upload")
                preserved_data = self.enhanced_send_logging(message)
            except Exception as e:
                logger.warning(f"Enhanced attachment logging failed: {e}")

        logger.info(f"📤 Message with {len(message.attachments)} attachments uploaded")
        logger.info(f"   Message ID: {message.id}")
        logger.info(f"   Author: {message.author} ({message.author.id})")

        # Log all attachment URLs for monitoring
        for i, attachment in enumerate(message.attachments):
            logger.info(f"   📎 Attachment {i + 1}: {attachment.filename}")
            logger.info(f"      🔗 Live URL: {attachment.url}")
            logger.info(f"      📏 Size: {attachment.size} bytes")
            logger.info(f"      🆔 ID: {attachment.id}")

        guild_id = str(message.guild.id)

        # Check if logging is enabled for this event
        if not await self.base.check_logging_enabled(guild_id, 'image_send'):
            return

        logger.info(f"📤 Processing file upload in {message.guild.name}")

        # Separate images from other files
        images = [att for att in message.attachments if self.base.is_image_file(att.filename)]
        other_files = [att for att in message.attachments if not self.base.is_image_file(att.filename)]

        # Determine title based on content
        if images and other_files:
            title = f"📎 Files & Images Uploaded ({len(message.attachments)} total)"
        elif images:
            title = f"🖼️ Image{'s' if len(images) > 1 else ''} Uploaded ({len(images)} image{'s' if len(images) > 1 else ''})"
        else:
            title = f"📎 File{'s' if len(other_files) > 1 else ''} Uploaded ({len(other_files)} file{'s' if len(other_files) > 1 else ''})"

        # Create main embed
        embed = discord.Embed(title=title, color=discord.Color.blue())

        # Add user information
        self.base.add_user_info(embed, message.author, "Author")

        # Add channel and message info
        embed.add_field(name="Channel", value=message.channel.mention, inline=True)
        embed.add_field(name="Message ID", value=str(message.id), inline=True)

        # Add message content if any
        if message.content:
            content = self.base.format_content(message.content, 500)
            embed.add_field(name="Message Content", value=f"```{content}```", inline=False)

        # Set first image as main embed image
        if images:
            embed.set_image(url=images[0].url)

        # Process ALL attachments for listing with enhanced metadata
        attachments_info = []
        image_links = []
        live_urls = []
        total_size = 0

        for i, attachment in enumerate(message.attachments):
            emoji = self.base.get_file_type_emoji(attachment.filename)
            file_size = f"{attachment.size / 1024:.1f} KB" if attachment.size < 1024 * 1024 else f"{attachment.size / (1024 * 1024):.1f} MB"
            total_size += attachment.size

            # Enhanced attachment info with technical details
            content_type = getattr(attachment, 'content_type', 'Unknown')
            dimensions = ""
            if hasattr(attachment, 'width') and attachment.width:
                dimensions = f" • {attachment.width}x{attachment.height}"

            # Add to main list with enhanced info
            attachments_info.append(f"{emoji} **{attachment.filename}** ({file_size} • {content_type}{dimensions})")

            # Store live URL data
            live_urls.append({
                'filename': attachment.filename,
                'url': attachment.url,
                'id': attachment.id,
                'size': attachment.size,
                'captured_at': datetime.utcnow().isoformat()
            })

            # If it's an image, add to clickable links
            if self.base.is_image_file(attachment.filename):
                image_links.append(f"[{attachment.filename}]({attachment.url})")

            # Limit display to avoid embed limits
            if i >= 9:
                attachments_info.append(f"... and {len(message.attachments) - 10} more files")
                break

        # Add enhanced attachments list
        embed.add_field(
            name=f"📎 All Files ({len(message.attachments)}) - Total: {total_size / (1024 * 1024):.2f} MB",
            value="\n".join(attachments_info),
            inline=False
        )

        # Add clickable image links if there are multiple images
        if len(images) > 1:
            embed.add_field(
                name=f"🖼️ View All Images ({len(images)})",
                value=" • ".join(image_links),
                inline=False
            )

        # Add live URL preservation info for admin reference
        if len(live_urls) <= 3:  # Only show for small numbers
            url_info = []
            for url_data in live_urls:
                url_info.append(f"• [{url_data['filename']}]({url_data['url']}) (ID: {url_data['id']})")

            embed.add_field(
                name="🔗 Live URLs (Accessible)",
                value="\n".join(url_info),
                inline=False
            )

        # Add technical metadata
        embed.add_field(
            name="📊 Upload Metadata",
            value=f"**Images:** {len(images)} files\n"
                  f"**Other Files:** {len(other_files)} files\n"
                  f"**Total Size:** {total_size / (1024 * 1024):.2f} MB\n"
                  f"**Uploaded:** <t:{int(message.created_at.timestamp())}:F>\n"
                  f"**URLs Captured:** {len(live_urls)}/{len(message.attachments)}",
            inline=True
        )

        # Add jump link
        self.base.create_jump_link_field(embed, message)

        # Add avatar if enabled
        add_avatar = self.base.add_guild_avatar(embed, message.author, guild_id)
        await add_avatar()

        # Log live URLs for monitoring/debugging
        logger.info(f"📊 CAPTURED LIVE URLS for message {message.id}:")
        for url_data in live_urls:
            logger.info(f"   📎 {url_data['filename']}: {url_data['url']}")

        # Send main embed
        await self.base.send_log(message.guild, 'image_send', embed)

        # If there are multiple images (more than 3), send additional embeds
        if len(images) > 3:
            await self.send_multiple_image_logs(message, message.attachments, guild_id)

    async def on_message_delete(self, message):
        """Log message deletions with attachments - ENHANCED with URL preservation"""
        # Skip bot messages
        if message.author.bot:
            return

        # Skip if no guild (DMs, etc.)
        if not message.guild:
            return

        # Only handle messages WITH attachments
        if not message.attachments:
            return

        # Enhanced attachment logging if available
        if self.enhanced_logging:
            try:
                self.debug_attachments(message, "delete")
                preserved_data = self.enhanced_delete_logging(message)
            except Exception as e:
                logger.warning(f"Enhanced attachment logging failed: {e}")

        guild_id = str(message.guild.id)

        # Check if logging is enabled for this event
        if not await self.base.check_logging_enabled(guild_id, 'image_delete'):
            return

        logger.info(f"🗑️ Processing deletion of message with {len(message.attachments)} attachments")

        # Preserve ALL attachment URLs and metadata BEFORE they become inaccessible
        preserved_attachments = []
        for attachment in message.attachments:
            preserved_data = {
                'filename': attachment.filename,
                'size': attachment.size,
                'url': attachment.url,
                'proxy_url': attachment.proxy_url,
                'id': attachment.id,
                'content_type': getattr(attachment, 'content_type', None),
                'width': getattr(attachment, 'width', None),
                'height': getattr(attachment, 'height', None),
                'is_spoiler': attachment.is_spoiler(),
                'preserved_at': datetime.utcnow().isoformat()
            }
            preserved_attachments.append(preserved_data)

            # Log each URL for debugging
            logger.info(f"📎 PRESERVING: {attachment.filename}")
            logger.info(f"   🔗 URL: {attachment.url}")
            logger.info(f"   📏 Size: {attachment.size} bytes")

        # Separate images from other files
        images = [att for att in message.attachments if self.base.is_image_file(att.filename)]
        other_files = [att for att in message.attachments if not self.base.is_image_file(att.filename)]

        # Determine title
        if images and other_files:
            title = f"🗑️ Files & Images Deleted ({len(message.attachments)} total)"
        elif images:
            title = f"🗑️ Image{'s' if len(images) > 1 else ''} Deleted ({len(images)} image{'s' if len(images) > 1 else ''})"
        else:
            title = f"🗑️ File{'s' if len(other_files) > 1 else ''} Deleted ({len(other_files)} file{'s' if len(other_files) > 1 else ''})"

        # Create embed
        embed = discord.Embed(title=title, color=discord.Color.red())

        # Add user information
        self.base.add_user_info(embed, message.author, "Author")

        # Add channel and message info
        embed.add_field(name="Channel", value=message.channel.mention, inline=True)
        embed.add_field(name="Message ID", value=str(message.id), inline=True)

        # Add message content if any
        if message.content:
            content = self.base.format_content(message.content, 1000)
            embed.add_field(name="Content", value=f"```{content}```", inline=False)

        # Process attachments
        attachments_info = []
        preserved_urls = []

        for i, attachment in enumerate(message.attachments):
            emoji = self.base.get_file_type_emoji(attachment.filename)
            file_size = f"{attachment.size / 1024:.1f} KB" if attachment.size < 1024 * 1024 else f"{attachment.size / (1024 * 1024):.1f} MB"

            # Create attachment info with preserved data
            if hasattr(attachment, 'content_type') and attachment.content_type:
                type_info = f" • {attachment.content_type}"
            else:
                type_info = ""

            attachments_info.append(f"{emoji} **{attachment.filename}** ({file_size}){type_info}")

            # Store the URL that was preserved
            preserved_urls.append({
                'filename': attachment.filename,
                'url': attachment.url,
                'size': attachment.size,
                'id': attachment.id
            })

            # Log the URL for debugging/monitoring
            logger.info(f"📎 Deleted attachment URL: {attachment.url}")

            # Limit to avoid embed limits
            if i >= 9:
                attachments_info.append(f"... and {len(message.attachments) - 10} more files")
                break

        embed.add_field(
            name=f"Deleted Attachments ({len(message.attachments)})",
            value="\n".join(attachments_info),
            inline=False
        )

        # Add preserved URLs for admin reference (though they won't work)
        if len(preserved_urls) <= 3:
            url_list = []
            for url_data in preserved_urls:
                url_list.append(f"• [{url_data['filename']}]({url_data['url']}) (ID: {url_data['id']})")

            embed.add_field(
                name="🔗 Preserved URLs (Now Inaccessible)",
                value="\n".join(url_list),
                inline=False
            )

        # Enhanced note about deleted files with technical details
        embed.add_field(
            name="⚠️ Technical Information",
            value="**Discord CDN Behavior:**\n"
                  f"• {len(preserved_urls)} file URL(s) were captured before deletion\n"
                  "• URLs become HTTP 404 immediately upon message deletion\n"
                  "• Files are removed from Discord's CDN permanently\n"
                  "• Only metadata (filename, size, type) is preserved\n"
                  f"• Total deleted content: {sum(url['size'] for url in preserved_urls) / (1024 * 1024):.2f} MB",
            inline=False
        )

        # Add deletion timestamp with precise timing
        embed.add_field(
            name="🕒 Deletion Details",
            value=f"**When:** <t:{int(datetime.utcnow().timestamp())}:F>\n"
                  f"**Detected:** {datetime.utcnow().strftime('%H:%M:%S.%f')[:-3]} UTC\n"
                  f"**URLs Preserved:** {len(preserved_urls)}/{len(message.attachments)}",
            inline=True
        )

        # Add avatar if enabled
        add_avatar = self.base.add_guild_avatar(embed, message.author, guild_id)
        await add_avatar()

        # Store preserved data in logs for potential recovery/analysis
        logger.info(f"🔍 PRESERVED ATTACHMENT DATA for message {message.id}:")
        for url_data in preserved_urls:
            logger.info(f"   📎 {url_data['filename']}: {url_data['url']}")

        # Send log
        await self.base.send_log(message.guild, 'image_delete', embed)

        # Log to interaction logger
        log_message(message, "deleted_with_attachments",
                    f"Content: {message.content[:100]}... | Attachments: {len(message.attachments)}")

    async def send_multiple_image_logs(self, message, attachments, guild_id):
        """Send additional embeds for multiple images (when there are many images)"""
        try:
            from utils.database import get_guild_config
            config = await get_guild_config(guild_id)
            if not config or not config.get('log_channel_id'):
                return

            log_channel = message.guild.get_channel(int(config['log_channel_id']))
            if not log_channel:
                return

            images = [att for att in attachments if self.base.is_image_file(att.filename)]

            # Send additional embeds for images 2, 3, 4+ (first is in main embed)
            for i, attachment in enumerate(images[1:], 2):
                embed = discord.Embed(
                    title=f"🖼️ Image {i}/{len(images)} (continued)",
                    color=discord.Color.blue()
                )

                embed.set_image(url=attachment.url)

                file_size = f"{attachment.size / 1024:.1f} KB" if attachment.size < 1024 * 1024 else f"{attachment.size / (1024 * 1024):.1f} MB"
                embed.add_field(
                    name="File Info",
                    value=f"**{attachment.filename}** ({file_size})",
                    inline=False
                )

                embed.add_field(
                    name="Direct Link",
                    value=f"[Open Image]({attachment.url})",
                    inline=True
                )

                # Apply guild styling
                if config.get('embed_color'):
                    try:
                        embed.color = discord.Color(int(config['embed_color'].replace('#', ''), 16))
                    except:
                        pass

                if config.get('show_timestamps', True):
                    embed.timestamp = datetime.utcnow()

                await log_channel.send(embed=embed)

        except Exception as e:
            logger.error(f"Failed to send additional image logs: {e}")

    async def get_attachment_statistics(self, guild_id: str, days: int = 7):
        """Get attachment upload/deletion statistics for a guild"""
        # This method can be expanded when we add analytics in future weeks
        stats = {
            'uploads_tracked': 0,
            'deletions_tracked': 0,
            'total_files_size_mb': 0,
            'images_count': 0,
            'documents_count': 0,
            'other_files_count': 0,
            'period_days': days
        }

        # TODO: Query database for actual statistics
        # This will be implemented when we add the analytics features

        return stats