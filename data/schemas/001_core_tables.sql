-- Core Logging Tables Schema
-- File: data/schemas/001_core_tables.sql
-- Description: Essential tables for guild configuration and logging events

-- Guild Configuration Table
-- Stores per-guild logging settings and preferences
CREATE TABLE IF NOT EXISTS guild_configs (
    guild_id TEXT PRIMARY KEY,
    guild_name TEXT,

    -- Logging Settings
    logging_enabled BOOLEAN DEFAULT 0,
    log_channel_id TEXT,
    log_format TEXT DEFAULT 'embed',

    -- Display Settings
    show_avatars BOOLEAN DEFAULT 1,
    show_timestamps BOOLEAN DEFAULT 1,
    embed_color TEXT DEFAULT '#3498db',

    -- Timestamps
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Log Events Configuration Table
-- Stores which events are enabled for each guild
CREATE TABLE IF NOT EXISTS log_events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    guild_id TEXT NOT NULL,
    event_type TEXT NOT NULL,
    enabled BOOLEAN DEFAULT 0,

    -- Constraints
    FOREIGN KEY (guild_id) REFERENCES guild_configs (guild_id),
    UNIQUE(guild_id, event_type)
);

-- Message Archive Table (Optional - for future message search)
-- Stores message metadata for search and analytics
CREATE TABLE IF NOT EXISTS message_archive (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    message_id TEXT NOT NULL,
    guild_id TEXT NOT NULL,
    channel_id TEXT NOT NULL,
    author_id TEXT NOT NULL,
    content TEXT,
    attachment_count INTEGER DEFAULT 0,
    embed_count INTEGER DEFAULT 0,
    created_at TIMESTAMP NOT NULL,
    deleted_at TIMESTAMP,

    -- Indexes will be in separate file
    UNIQUE(message_id)
);