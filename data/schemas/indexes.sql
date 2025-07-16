-- Database Indexes Schema
-- File: data/schemas/indexes.sql
-- Description: Performance indexes for all tables

-- ==================== CORE TABLE INDEXES ====================

-- Guild Configs Indexes
CREATE INDEX IF NOT EXISTS idx_guild_configs_enabled
ON guild_configs(logging_enabled)
WHERE logging_enabled = 1;

-- Log Events Indexes
CREATE INDEX IF NOT EXISTS idx_log_events_guild_type
ON log_events(guild_id, event_type);

CREATE INDEX IF NOT EXISTS idx_log_events_enabled
ON log_events(guild_id, enabled)
WHERE enabled = 1;

-- Message Archive Indexes (if using message search)
CREATE INDEX IF NOT EXISTS idx_message_archive_guild_time
ON message_archive(guild_id, created_at DESC);

CREATE INDEX IF NOT EXISTS idx_message_archive_author_time
ON message_archive(author_id, created_at DESC);

CREATE INDEX IF NOT EXISTS idx_message_archive_channel_time
ON message_archive(channel_id, created_at DESC);

-- ==================== VOICE ACTIVITY INDEXES ====================

-- Voice Sessions Indexes
CREATE INDEX IF NOT EXISTS idx_voice_sessions_user_guild
ON voice_sessions(user_id, guild_id);

CREATE INDEX IF NOT EXISTS idx_voice_sessions_guild_time
ON voice_sessions(guild_id, start_time DESC);

CREATE INDEX IF NOT EXISTS idx_voice_sessions_channel_time
ON voice_sessions(channel_id, start_time DESC);

CREATE INDEX IF NOT EXISTS idx_voice_sessions_duration
ON voice_sessions(duration_seconds DESC)
WHERE duration_seconds IS NOT NULL;

CREATE INDEX IF NOT EXISTS idx_voice_sessions_active
ON voice_sessions(guild_id, end_time)
WHERE end_time IS NULL;

-- Voice Events Indexes
CREATE INDEX IF NOT EXISTS idx_voice_events_guild_time
ON voice_events(guild_id, timestamp DESC);

CREATE INDEX IF NOT EXISTS idx_voice_events_user_type
ON voice_events(user_id, event_type);

CREATE INDEX IF NOT EXISTS idx_voice_events_channel_time
ON voice_events(channel_id, timestamp DESC);

CREATE INDEX IF NOT EXISTS idx_voice_events_type_time
ON voice_events(event_type, timestamp DESC);

-- Channel Activity Indexes
CREATE INDEX IF NOT EXISTS idx_channel_activity_guild_date
ON channel_activity(guild_id, date DESC);

CREATE INDEX IF NOT EXISTS idx_channel_activity_channel_date
ON channel_activity(channel_id, date DESC);

-- User Voice Stats Indexes
CREATE INDEX IF NOT EXISTS idx_user_voice_stats_user_date
ON user_voice_stats(user_id, guild_id, date DESC);

CREATE INDEX IF NOT EXISTS idx_user_voice_stats_guild_date
ON user_voice_stats(guild_id, date DESC);

-- ==================== ANALYTICS INDEXES (if using analytics tables) ====================

-- Guild Daily Stats Indexes
CREATE INDEX IF NOT EXISTS idx_guild_daily_stats_date
ON guild_daily_stats(guild_id, date DESC);

-- Channel Daily Stats Indexes
CREATE INDEX IF NOT EXISTS idx_channel_daily_stats_date
ON channel_daily_stats(guild_id, channel_id, date DESC);

-- User Daily Activity Indexes
CREATE INDEX IF NOT EXISTS idx_user_daily_activity_date
ON user_daily_activity(user_id, guild_id, date DESC);

-- User Behavior Patterns Indexes
CREATE INDEX IF NOT EXISTS idx_user_behavior_patterns_period
ON user_behavior_patterns(user_id, guild_id, period_type, period_start DESC);