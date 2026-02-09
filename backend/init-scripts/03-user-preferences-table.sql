-- Drop and recreate user preferences table with all columns
DROP TABLE IF EXISTS user_preferences CASCADE;

CREATE TABLE user_preferences (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    
    -- Style Preferences
    preferred_colors TEXT[] DEFAULT '{}'::text[],
    preferred_fabrics TEXT[] DEFAULT '{}'::text[],
    preferred_styles TEXT[] DEFAULT '{}'::text[],
    preferred_occasions TEXT[] DEFAULT '{}'::text[],
    
    -- Body & Fit
    body_type VARCHAR(50) DEFAULT NULL,
    fit_preference VARCHAR(50) DEFAULT NULL,
    size_preference VARCHAR(10) DEFAULT NULL,
    
    -- Budget
    budget_min DECIMAL(10, 2) DEFAULT NULL,
    budget_max DECIMAL(10, 2) DEFAULT NULL,
    budget_currency VARCHAR(3) DEFAULT 'USD',
    
    -- Communication
    language_preference VARCHAR(10) DEFAULT 'en',
    notification_preferences JSONB DEFAULT '{}'::jsonb,
    
    -- Shopping
    preferred_brands TEXT[] DEFAULT '{}'::text[],
    avoid_colors TEXT[] DEFAULT '{}'::text[],
    avoid_fabrics TEXT[] DEFAULT '{}'::text[],
    
    -- AI Learning
    interaction_count INTEGER DEFAULT 0,
    last_interaction TIMESTAMP DEFAULT NULL,
    preference_confidence FLOAT DEFAULT 0.0,
    
    -- Metadata
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create index
CREATE INDEX IF NOT EXISTS idx_user_preferences_user_id ON user_preferences(user_id);

-- Create trigger function for auto-updating timestamp
CREATE OR REPLACE FUNCTION update_user_preferences_timestamp()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Create trigger
DROP TRIGGER IF EXISTS trigger_user_preferences_updated ON user_preferences;
CREATE TRIGGER trigger_user_preferences_updated
    BEFORE UPDATE ON user_preferences
    FOR EACH ROW
    EXECUTE FUNCTION update_user_preferences_timestamp();

-- Insert default preferences for existing users
INSERT INTO user_preferences (user_id)
SELECT id FROM users
WHERE NOT EXISTS (
    SELECT 1 FROM user_preferences WHERE user_preferences.user_id = users.id
);

-- Verify
SELECT * FROM user_preferences LIMIT 5;
