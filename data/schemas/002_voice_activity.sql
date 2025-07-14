-- Voice Activity Tables Schema
-- File: data/schemas/002_voice_activity.sql
-- Description: Tables for tracking voice channel activity and sessions

-- Voice Sessions Table
-- Tracks individual voice sessions with duration and metadata
CREATE TABLE IF NOT EXISTS voice_sessions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id TEXT NOT NULL,
    guild_id TEXT NOT NULL,
    channel_id TEXT NOT NULL,
    channel_name TEXT NOT NULL,

    -- Session Timing
    start_time TIMESTAMP NOT NULL,
    end_time TIMESTAMP,
    duration_seconds INTEGER,

    -- Session Metadata
    channel_moves INTEGER DEFAULT 0,
    end_reason TEXT,

    -- Tracking
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Voice Events Table
-- Tracks all voice-related events for detailed logging
CREATE TABLE IF NOT EXISTS voice_events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id TEXT NOT NULL,
    guild_id TEXT NOT NULL,
    channel_id TEXT,
    channel_name TEXT,

    -- Event Data
    event_type TEXT NOT NULL, -- 'join', 'leave', 'move', 'mute', 'deafen', 'stream', 'video'
    event_details TEXT, -- JSON data for additional event-specific information

    -- Timing
    timestamp TIMESTAMP NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Channel Activity Table
-- Aggregated daily statistics per voice channel
CREATE TABLE IF NOT EXISTS channel_activity (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    guild_id TEXT NOT NULL,
    channel_id TEXT NOT NULL,
    channel_name TEXT NOT NULL,
    channel_type TEXT NOT NULL, -- 'voice', 'stage'

    -- Daily Statistics
    date DATE NOT NULL,
    total_joins INTEGER DEFAULT 0,
    total_leaves INTEGER DEFAULT 0,
    total_time_seconds INTEGER DEFAULT 0,
    unique_users INTEGER DEFAULT 0,
    peak_users INTEGER DEFAULT 0,

    -- Tracking
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    -- Ensure one record per channel per day
    UNIQUE(guild_id, channel_id, date)
);

-- User Voice Statistics Table
-- Daily aggregated voice stats per user
CREATE TABLE IF NOT EXISTS user_voice_stats (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id TEXT NOT NULL,
    guild_id TEXT NOT NULL,

    -- Daily Statistics
    date DATE NOT NULL,
    total_time_seconds INTEGER DEFAULT 0,
    session_count INTEGER DEFAULT 0,
    channels_used INTEGER DEFAULT 0,
    moves_count INTEGER DEFAULT 0,

    -- Activity Breakdown
    time_in_general INTEGER DEFAULT 0,
    time_in_music INTEGER DEFAULT 0,
    time_in_gaming INTEGER DEFAULT 0,
    time_in_other INTEGER DEFAULT 0,

    -- Tracking
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    -- Ensure one record per user per guild per day
    UNIQUE(user_id, guild_id, date)
);