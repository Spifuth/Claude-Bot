"""
Enhanced Database Manager with Flexible Event Channel Support
Manages SQLite database with organized schema files and per-event channel mapping
"""

import aiosqlite
import logging
import os
import asyncio
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime

logger = logging.getLogger(__name__)

class SchemaManager:
    """Manages database schema files and migrations"""

    def __init__(self, data_path: str):
        self.data_path = Path(data_path)
        self.schemas_path = self.data_path / "schemas"
        self.migrations_path = self.data_path / "migrations"
        self.migrations_file = self.migrations_path / "applied_migrations.txt"

        # Ensure directories exist
        self.schemas_path.mkdir(parents=True, exist_ok=True)
        self.migrations_path.mkdir(parents=True, exist_ok=True)

    async def get_applied_migrations(self) -> List[str]:
        """Get list of already applied migrations"""
        if not self.migrations_file.exists():
            return []

        try:
            with open(self.migrations_file, 'r') as f:
                return [line.split(' - ')[0].strip() for line in f.readlines() if line.strip()]
        except Exception as e:
            logger.error(f"Error reading migrations file: {e}")
            return []

    async def mark_migration_applied(self, schema_name: str):
        """Mark a migration as applied"""
        try:
            timestamp = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
            with open(self.migrations_file, 'a') as f:
                f.write(f"{schema_name} - {timestamp}\n")
            logger.info(f"Marked migration as applied: {schema_name}")
        except Exception as e:
            logger.error(f"Error marking migration applied: {e}")

    async def get_schema_files(self) -> List[Path]:
        """Get all schema files in order"""
        schema_files = []

        # Get numbered schema files first (001_, 002_, etc.)
        numbered_files = sorted([f for f in self.schemas_path.glob("*.sql") if f.name[0].isdigit()])
        schema_files.extend(numbered_files)

        # Add indexes.sql last if it exists
        indexes_file = self.schemas_path / "indexes.sql"
        if indexes_file.exists() and indexes_file not in schema_files:
            schema_files.append(indexes_file)

        return schema_files

    async def read_schema_file(self, schema_path: Path) -> str:
        """Read and return schema file content"""
        try:
            with open(schema_path, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            logger.error(f"Error reading schema file {schema_path}: {e}")
            return ""

    def create_sample_schemas(self):
        """Create sample schema files if they don't exist"""
        # This method helps users get started with the schema structure
        sample_files = {
            "001_core_tables.sql": """-- Core logging tables
CREATE TABLE IF NOT EXISTS guild_configs (
    guild_id TEXT PRIMARY KEY,
    guild_name TEXT,
    logging_enabled BOOLEAN DEFAULT 0,
    log_channel_id TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);""",
            "indexes.sql": """-- Basic indexes
CREATE INDEX IF NOT EXISTS idx_guild_configs_enabled 
ON guild_configs(logging_enabled) WHERE logging_enabled = 1;"""
        }

        for filename, content in sample_files.items():
            file_path = self.schemas_path / filename
            if not file_path.exists():
                try:
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(content)
                    logger.info(f"Created sample schema file: {filename}")
                except Exception as e:
                    logger.error(f"Error creating sample schema {filename}: {e}")

class DatabaseManager:
    """Enhanced database manager with flexible event channel support"""

    def __init__(self, db_path: str):
        self.db_path = db_path
        self.data_path = Path(db_path).parent
        self.schema_manager = SchemaManager(self.data_path)
        self._pool_lock = asyncio.Lock()
        self._connection_pool = {}

        # Ensure directory exists
        Path(db_path).parent.mkdir(parents=True, exist_ok=True)

    async def initialize(self):
        """Initialize database with schema files"""
        logger.info("Initializing database with schema files...")

        # Create sample schemas if none exist (for first-time setup)
        schema_files = await self.schema_manager.get_schema_files()
        if not schema_files:
            logger.info("No schema files found, creating samples...")
            self.schema_manager.create_sample_schemas()
            schema_files = await self.schema_manager.get_schema_files()

        # Get already applied migrations
        applied_migrations = await self.schema_manager.get_applied_migrations()
        logger.info(f"Found {len(applied_migrations)} previously applied migrations")

        # Apply new schema files
        async with aiosqlite.connect(self.db_path) as db:
            applied_count = 0

            for schema_file in schema_files:
                schema_name = schema_file.name

                # Skip if already applied
                if schema_name in applied_migrations:
                    logger.debug(f"Schema already applied: {schema_name}")
                    continue

                logger.info(f"Applying schema: {schema_name}")

                # Read and execute schema
                schema_content = await self.schema_manager.read_schema_file(schema_file)
                if schema_content:
                    try:
                        # Split on semicolons and execute each statement
                        statements = [stmt.strip() for stmt in schema_content.split(';') if stmt.strip()]

                        for statement in statements:
                            if statement:
                                await db.execute(statement)

                        await db.commit()

                        # Mark as applied
                        await self.schema_manager.mark_migration_applied(schema_name)
                        applied_count += 1

                        logger.info(f"✅ Successfully applied schema: {schema_name}")

                    except Exception as e:
                        logger.error(f"❌ Error applying schema {schema_name}: {e}")
                        await db.rollback()
                        raise

            if applied_count > 0:
                logger.info(f"✅ Applied {applied_count} new schema files")
            else:
                logger.info("✅ Database schema up to date")

        logger.info("Database initialization completed successfully")

    async def get_connection(self):
        """Get a database connection with basic pooling"""
        # CHANGE: Add simple connection pooling to reduce overhead
        async with self._pool_lock:
            thread_id = id(asyncio.current_task())

            if thread_id not in self._connection_pool:
                self._connection_pool[thread_id] = await aiosqlite.connect(self.db_path)

            return self._connection_pool[thread_id]

    async def close_connections(self):
        """Close all pooled connections"""
        # CHANGE: Add cleanup method
        async with self._pool_lock:
            for conn in self._connection_pool.values():
                await conn.close()
            self._connection_pool.clear()

    async def add_new_schema(self, schema_name: str, schema_content: str):
        """Add a new schema file and apply it"""
        schema_path = self.schema_manager.schemas_path / schema_name

        try:
            # Write schema file
            with open(schema_path, 'w', encoding='utf-8') as f:
                f.write(schema_content)

            logger.info(f"Created new schema file: {schema_name}")

            # Apply the schema
            async with aiosqlite.connect(self.db_path) as db:
                statements = [stmt.strip() for stmt in schema_content.split(';') if stmt.strip()]

                for statement in statements:
                    if statement:
                        await db.execute(statement)

                await db.commit()

                # Mark as applied
                await self.schema_manager.mark_migration_applied(schema_name)

                logger.info(f"✅ Successfully applied new schema: {schema_name}")

        except Exception as e:
            logger.error(f"❌ Error adding new schema {schema_name}: {e}")
            raise

    async def get_schema_status(self) -> Dict[str, Any]:
        """Get status of all schema files"""
        schema_files = await self.schema_manager.get_schema_files()
        applied_migrations = await self.schema_manager.get_applied_migrations()

        status = {
            'total_schemas': len(schema_files),
            'applied_schemas': len(applied_migrations),
            'pending_schemas': [],
            'applied_schemas_list': applied_migrations,
            'schema_files': []
        }

        for schema_file in schema_files:
            schema_name = schema_file.name
            is_applied = schema_name in applied_migrations

            if not is_applied:
                status['pending_schemas'].append(schema_name)

            status['schema_files'].append({
                'name': schema_name,
                'path': str(schema_file),
                'applied': is_applied,
                'size_kb': round(schema_file.stat().st_size / 1024, 2) if schema_file.exists() else 0
            })

        return status

    # ==================== EXISTING DATABASE METHODS ====================
    # Keep all your existing database methods unchanged

    async def get_guild_config(self, guild_id: str) -> Optional[Dict[str, Any]]:
        """Get configuration for a guild"""
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute(
                "SELECT * FROM guild_configs WHERE guild_id = ?",
                (guild_id,)
            ) as cursor:
                row = await cursor.fetchone()
                return dict(row) if row else None

    async def create_or_update_guild_config(self, guild_id: str, config: Dict[str, Any]):
        """Create or update guild configuration"""
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute('''
                INSERT OR REPLACE INTO guild_configs 
                (guild_id, guild_name, logging_enabled, log_channel_id, log_format, 
                 show_avatars, show_timestamps, embed_color, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
            ''', (
                guild_id,
                config.get('guild_name'),
                config.get('logging_enabled', False),
                config.get('log_channel_id'),
                config.get('log_format', 'embed'),
                config.get('show_avatars', True),
                config.get('show_timestamps', True),
                config.get('embed_color', '#3498db')
            ))
            await db.commit()
            logger.info(f"Updated config for guild {guild_id}")

    async def get_log_events(self, guild_id: str) -> List[Dict[str, Any]]:
        """Get enabled log events for a guild"""
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute(
                "SELECT * FROM log_events WHERE guild_id = ? AND enabled = 1",
                (guild_id,)
            ) as cursor:
                rows = await cursor.fetchall()
                return [dict(row) for row in rows]

    async def set_log_event(self, guild_id: str, event_type: str, enabled: bool):
        """Enable or disable a log event for a guild"""
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute('''
                INSERT OR REPLACE INTO log_events (guild_id, event_type, enabled)
                VALUES (?, ?, ?)
            ''', (guild_id, event_type, enabled))
            await db.commit()
            logger.info(f"Set {event_type} = {enabled} for guild {guild_id}")

    async def get_all_enabled_events(self, guild_id: str) -> List[str]:
        """Get list of enabled event types for a guild"""
        async with aiosqlite.connect(self.db_path) as db:
            async with db.execute(
                "SELECT event_type FROM log_events WHERE guild_id = ? AND enabled = 1",
                (guild_id,)
            ) as cursor:
                rows = await cursor.fetchall()
                return [row[0] for row in rows]

    # ==================== NEW: FLEXIBLE EVENT CHANNEL METHODS ====================

    async def set_event_channel(self, guild_id: str, event_type: str, channel_id: str, channel_name: str = None):
        """Map a specific event type to a specific channel"""
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute('''
                INSERT OR REPLACE INTO log_event_channels 
                (guild_id, event_type, channel_id, channel_name)
                VALUES (?, ?, ?, ?)
            ''', (guild_id, event_type, channel_id, channel_name))
            await db.commit()
            logger.info(f"Mapped {event_type} to channel {channel_id} for guild {guild_id}")

    async def set_events_channel(self, guild_id: str, event_types: List[str], channel_id: str, channel_name: str = None):
        """Map multiple event types to a single channel (grouping)"""
        async with aiosqlite.connect(self.db_path) as db:
            for event_type in event_types:
                await db.execute('''
                    INSERT OR REPLACE INTO log_event_channels 
                    (guild_id, event_type, channel_id, channel_name)
                    VALUES (?, ?, ?, ?)
                ''', (guild_id, event_type, channel_id, channel_name))
            await db.commit()
            logger.info(f"Mapped {len(event_types)} events to channel {channel_id} for guild {guild_id}")

    async def get_event_channel(self, guild_id: str, event_type: str) -> Optional[str]:
        """Get the specific channel ID for an event type"""
        async with aiosqlite.connect(self.db_path) as db:
            async with db.execute(
                "SELECT channel_id FROM log_event_channels WHERE guild_id = ? AND event_type = ?",
                (guild_id, event_type)
            ) as cursor:
                row = await cursor.fetchone()
                return row[0] if row else None

    async def get_all_event_channels(self, guild_id: str) -> Dict[str, str]:
        """Get all event-to-channel mappings for a guild"""
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute(
                "SELECT event_type, channel_id FROM log_event_channels WHERE guild_id = ?",
                (guild_id,)
            ) as cursor:
                rows = await cursor.fetchall()
                return {row['event_type']: row['channel_id'] for row in rows}

    async def get_channel_events(self, guild_id: str, channel_id: str) -> List[str]:
        """Get all event types mapped to a specific channel"""
        async with aiosqlite.connect(self.db_path) as db:
            async with db.execute(
                "SELECT event_type FROM log_event_channels WHERE guild_id = ? AND channel_id = ?",
                (guild_id, channel_id)
            ) as cursor:
                rows = await cursor.fetchall()
                return [row[0] for row in rows]

    async def get_channel_mapping_summary(self, guild_id: str) -> Dict[str, Any]:
        """Get a comprehensive summary of channel mappings"""
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute('''
                SELECT channel_id, channel_name, GROUP_CONCAT(event_type) as events
                FROM log_event_channels 
                WHERE guild_id = ?
                GROUP BY channel_id, channel_name
            ''', (guild_id,)) as cursor:
                rows = await cursor.fetchall()

                summary = {
                    'total_channels': len(rows),
                    'total_events_mapped': 0,
                    'channels': []
                }

                for row in rows:
                    events = row['events'].split(',') if row['events'] else []
                    summary['total_events_mapped'] += len(events)
                    summary['channels'].append({
                        'channel_id': row['channel_id'],
                        'channel_name': row['channel_name'],
                        'events': events,
                        'event_count': len(events)
                    })

                return summary

    async def remove_event_channel(self, guild_id: str, event_type: str):
        """Remove channel mapping for an event type"""
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                "DELETE FROM log_event_channels WHERE guild_id = ? AND event_type = ?",
                (guild_id, event_type)
            )
            await db.commit()
            logger.info(f"Removed channel mapping for {event_type} in guild {guild_id}")

    async def remove_channel_mappings(self, guild_id: str, channel_id: str):
        """Remove all event mappings for a specific channel"""
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute(
                "DELETE FROM log_event_channels WHERE guild_id = ? AND channel_id = ?",
                (guild_id, channel_id)
            )
            await db.commit()
            removed_count = cursor.rowcount
            logger.info(f"Removed {removed_count} event mappings from channel {channel_id} in guild {guild_id}")
            return removed_count

    async def clear_all_event_channels(self, guild_id: str):
        """Clear all event channel mappings for a guild"""
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute(
                "DELETE FROM log_event_channels WHERE guild_id = ?",
                (guild_id,)
            )
            await db.commit()
            removed_count = cursor.rowcount
            logger.info(f"Cleared {removed_count} event channel mappings for guild {guild_id}")
            return removed_count

    async def migrate_to_event_channels(self, guild_id: str, fallback_channel_id: str):
        """Migrate existing single-channel setup to per-event channels"""
        # Get all enabled events
        enabled_events = await self.get_all_enabled_events(guild_id)

        if not enabled_events:
            logger.info(f"No enabled events to migrate for guild {guild_id}")
            return 0

        # Map all enabled events to the fallback channel
        async with aiosqlite.connect(self.db_path) as db:
            for event_type in enabled_events:
                await db.execute('''
                    INSERT OR REPLACE INTO log_event_channels 
                    (guild_id, event_type, channel_id, channel_name)
                    VALUES (?, ?, ?, ?)
                ''', (guild_id, event_type, fallback_channel_id, "migrated-logs"))
            await db.commit()

        logger.info(f"Migrated {len(enabled_events)} events to event channels for guild {guild_id}")
        return len(enabled_events)

# Global database manager instance
db_manager: Optional[DatabaseManager] = None

async def init_database(db_path: str):
    """Initialize the global database manager with schema files"""
    global db_manager
    db_manager = DatabaseManager(db_path)
    await db_manager.initialize()
    logger.info(f"Database initialized with schema files at {db_path}")

async def get_guild_config(guild_id: str) -> Optional[Dict[str, Any]]:
    """Get guild configuration"""
    if db_manager:
        return await db_manager.get_guild_config(str(guild_id))
    return None

async def is_logging_enabled(guild_id: str) -> bool:
    """Check if logging is enabled for a guild"""
    config = await get_guild_config(str(guild_id))
    return config and config.get('logging_enabled', False)

async def is_event_enabled(guild_id: str, event_type: str) -> bool:
    """Check if specific event logging is enabled"""
    if db_manager:
        events = await db_manager.get_log_events(str(guild_id))
        return any(event['event_type'] == event_type for event in events)
    return False

async def update_guild_config(guild_id: str, config: Dict[str, Any]):
    """Update guild configuration"""
    if db_manager:
        await db_manager.create_or_update_guild_config(str(guild_id), config)

async def set_event_enabled(guild_id: str, event_type: str, enabled: bool):
    """Enable or disable an event type"""
    if db_manager:
        await db_manager.set_log_event(str(guild_id), event_type, enabled)

# New schema management functions
async def get_schema_status() -> Dict[str, Any]:
    """Get database schema status"""
    if db_manager:
        return await db_manager.get_schema_status()
    return {}

async def add_schema_file(schema_name: str, schema_content: str):
    """Add a new schema file and apply it"""
    if db_manager:
        await db_manager.add_new_schema(schema_name, schema_content)

# ==================== NEW: FLEXIBLE EVENT CHANNEL FUNCTIONS ====================

async def set_event_channel(guild_id: str, event_type: str, channel_id: str, channel_name: str = None):
    """Map an event type to a specific channel"""
    if db_manager:
        await db_manager.set_event_channel(str(guild_id), event_type, str(channel_id), channel_name)

async def set_events_channel(guild_id: str, event_types: List[str], channel_id: str, channel_name: str = None):
    """Map multiple event types to a single channel"""
    if db_manager:
        await db_manager.set_events_channel(str(guild_id), event_types, str(channel_id), channel_name)

async def get_event_channel(guild_id: str, event_type: str) -> Optional[str]:
    """Get the channel ID for a specific event type"""
    if db_manager:
        return await db_manager.get_event_channel(str(guild_id), event_type)
    return None

async def get_all_event_channels(guild_id: str) -> Dict[str, str]:
    """Get all event-to-channel mappings"""
    if db_manager:
        return await db_manager.get_all_event_channels(str(guild_id))
    return {}

async def get_channel_events(guild_id: str, channel_id: str) -> List[str]:
    """Get all events mapped to a channel"""
    if db_manager:
        return await db_manager.get_channel_events(str(guild_id), str(channel_id))
    return []

async def get_channel_mapping_summary(guild_id: str) -> Dict[str, Any]:
    """Get comprehensive channel mapping summary"""
    if db_manager:
        return await db_manager.get_channel_mapping_summary(str(guild_id))
    return {}

async def remove_event_channel(guild_id: str, event_type: str):
    """Remove channel mapping for an event"""
    if db_manager:
        await db_manager.remove_event_channel(str(guild_id), event_type)

async def clear_all_event_channels(guild_id: str):
    """Clear all event channel mappings"""
    if db_manager:
        return await db_manager.clear_all_event_channels(str(guild_id))
    return 0