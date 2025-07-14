-- Flexible Event Channels Schema
-- File: data/schemas/005_event_channel_mapping.sql
-- Description: Advanced event-to-channel mapping for granular logging control

-- Log Event Channels Table
-- Enables mapping any event type to any specific channel
-- Supports both individual event mapping and grouped event mapping
CREATE TABLE IF NOT EXISTS log_event_channels (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    guild_id TEXT NOT NULL,
    event_type TEXT NOT NULL,
    channel_id TEXT NOT NULL,
    channel_name TEXT,

    -- Metadata for better management
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    -- Foreign key constraint
    FOREIGN KEY (guild_id) REFERENCES guild_configs (guild_id) ON DELETE CASCADE,

    -- Ensure each event maps to exactly one channel per guild
    UNIQUE(guild_id, event_type)
);

-- Index for fast event-to-channel resolution
CREATE INDEX IF NOT EXISTS idx_log_event_channels_lookup
ON log_event_channels(guild_id, event_type);

-- Index for channel-based queries (finding all events for a channel)
CREATE INDEX IF NOT EXISTS idx_log_event_channels_by_channel
ON log_event_channels(guild_id, channel_id);

-- Index for management queries
CREATE INDEX IF NOT EXISTS idx_log_event_channels_guild
ON log_event_channels(guild_id);

-- Create a view for easy channel mapping summary
CREATE VIEW IF NOT EXISTS v_channel_mapping_summary AS
SELECT
    guild_id,
    channel_id,
    channel_name,
    COUNT(event_type) as event_count,
    GROUP_CONCAT(event_type) as events,
    MIN(created_at) as first_mapped,
    MAX(updated_at) as last_updated
FROM log_event_channels
GROUP BY guild_id, channel_id, channel_name;