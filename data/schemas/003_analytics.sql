-- Analytics Tables Schema
-- File: data/schemas/003_analytics.sql
-- Description: Tables for analytics and reporting features

-- Guild Statistics Table
-- Daily aggregated statistics per guild
CREATE TABLE IF NOT EXISTS guild_daily_stats (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    guild_id TEXT NOT NULL,
    date DATE NOT NULL,

    -- Message Statistics
    total_messages INTEGER DEFAULT 0,
    total_deleted INTEGER DEFAULT 0,
    total_edited INTEGER DEFAULT 0,

    -- Member Statistics
    total_joins INTEGER DEFAULT 0,
    total_leaves INTEGER DEFAULT 0,
    member_count_end INTEGER DEFAULT 0,

    -- Voice Statistics
    total_voice_time_seconds INTEGER DEFAULT 0,
    total_voice_sessions INTEGER DEFAULT 0,
    active_voice_users INTEGER DEFAULT 0,

    -- File Statistics
    total_files_uploaded INTEGER DEFAULT 0,
    total_files_deleted INTEGER DEFAULT 0,
    total_file_size_mb REAL DEFAULT 0,

    -- Tracking
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    UNIQUE(guild_id, date)
);

-- Channel Statistics Table
-- Daily aggregated statistics per channel
CREATE TABLE IF NOT EXISTS channel_daily_stats (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    guild_id TEXT NOT NULL,
    channel_id TEXT NOT NULL,
    channel_name TEXT NOT NULL,
    channel_type TEXT NOT NULL,
    date DATE NOT NULL,

    -- Activity Statistics
    total_messages INTEGER DEFAULT 0,
    unique_users INTEGER DEFAULT 0,
    peak_active_users INTEGER DEFAULT 0,

    -- Tracking
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    UNIQUE(guild_id, channel_id, date)
);