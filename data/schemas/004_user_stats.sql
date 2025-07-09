-- User Statistics Tables Schema
-- File: data/schemas/004_user_stats.sql
-- Description: Tables for user behavior analytics

-- User Daily Activity Table
-- Daily activity statistics per user
CREATE TABLE IF NOT EXISTS user_daily_activity (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id TEXT NOT NULL,
    guild_id TEXT NOT NULL,
    date DATE NOT NULL,

    -- Message Activity
    messages_sent INTEGER DEFAULT 0,
    messages_deleted INTEGER DEFAULT 0,
    messages_edited INTEGER DEFAULT 0,

    -- Voice Activity (duplicated from voice stats for convenience)
    voice_time_seconds INTEGER DEFAULT 0,
    voice_sessions INTEGER DEFAULT 0,
    voice_channels_used INTEGER DEFAULT 0,

    -- File Activity
    files_uploaded INTEGER DEFAULT 0,
    files_deleted INTEGER DEFAULT 0,

    -- Engagement Metrics
    first_activity_time TIME,
    last_activity_time TIME,
    active_hours INTEGER DEFAULT 0,

    -- Tracking
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    UNIQUE(user_id, guild_id, date)
);

-- User Behavior Patterns Table
-- Weekly/monthly behavior analysis
CREATE TABLE IF NOT EXISTS user_behavior_patterns (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id TEXT NOT NULL,
    guild_id TEXT NOT NULL,

    -- Period (week/month)
    period_type TEXT NOT NULL, -- 'week', 'month'
    period_start DATE NOT NULL,
    period_end DATE NOT NULL,

    -- Calculated Patterns
    avg_daily_messages REAL DEFAULT 0,
    avg_daily_voice_minutes REAL DEFAULT 0,
    most_active_hour INTEGER,
    most_active_day_of_week INTEGER,
    consistency_score REAL DEFAULT 0,

    -- Activity Classification
    activity_level TEXT, -- 'very_active', 'active', 'moderate', 'low', 'inactive'
    primary_activity TEXT, -- 'messaging', 'voice', 'mixed'

    -- Tracking
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    UNIQUE(user_id, guild_id, period_type, period_start)
);