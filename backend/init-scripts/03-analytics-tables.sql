-- Analytics tables for Learning Loop
-- Run this in PostgreSQL to create analytics tables

-- Drop existing tables if exists (for fresh setup)
DROP TABLE IF EXISTS chat_messages CASCADE;
DROP TABLE IF EXISTS chat_sessions CASCADE;
DROP TABLE IF EXISTS learning_feedback CASCADE;

-- Create chat_sessions table
CREATE TABLE chat_sessions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    ended_at TIMESTAMP,
    session_type VARCHAR(50) DEFAULT 'general',
    metadata JSONB DEFAULT '{}'
);

-- Create index on user_id and started_at
CREATE INDEX idx_chat_sessions_user_id ON chat_sessions(user_id);
CREATE INDEX idx_chat_sessions_started_at ON chat_sessions(started_at);

-- Create chat_messages table
CREATE TABLE chat_messages (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id UUID NOT NULL REFERENCES chat_sessions(id) ON DELETE CASCADE,
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    user_message TEXT NOT NULL,
    ai_response TEXT NOT NULL,
    agent_used VARCHAR(50) NOT NULL DEFAULT 'general',
    response_time_ms INTEGER DEFAULT 0,
    tokens_used INTEGER DEFAULT 0,
    was_helpful BOOLEAN,
    user_feedback TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    metadata JSONB DEFAULT '{}'
);

-- Create indexes on chat_messages
CREATE INDEX idx_chat_messages_session_id ON chat_messages(session_id);
CREATE INDEX idx_chat_messages_user_id ON chat_messages(user_id);
CREATE INDEX idx_chat_messages_created_at ON chat_messages(created_at);
CREATE INDEX idx_chat_messages_agent_used ON chat_messages(agent_used);

-- Create learning_feedback table
CREATE TABLE learning_feedback (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    session_id UUID REFERENCES chat_sessions(id) ON DELETE SET NULL,
    category VARCHAR(100) NOT NULL,
    rating INTEGER CHECK (rating >= 1 AND rating <= 5),
    comment TEXT,
    suggested_improvement TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes on learning_feedback
CREATE INDEX idx_learning_feedback_user_id ON learning_feedback(user_id);
CREATE INDEX idx_learning_feedback_category ON learning_feedback(category);

-- Add comments
COMMENT ON TABLE chat_sessions IS 'Chat session tracking for analytics';
COMMENT ON TABLE chat_messages IS 'Chat messages for learning loop and analytics';
COMMENT ON TABLE learning_feedback IS 'User feedback for system improvement';
