-- Database initialization script for AI Chatbot
-- PostgreSQL schema for products, users, and chat data

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Users table
CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(255) NOT NULL,
    email VARCHAR(255) UNIQUE,
    avatar_url VARCHAR(500),
    preferences JSONB DEFAULT '{}',
    design_preferences JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Products table
CREATE TABLE IF NOT EXISTS products (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    category VARCHAR(100) NOT NULL,
    sub_category VARCHAR(100),
    description TEXT,
    fabric_type VARCHAR(100),
    color VARCHAR(50),
    price DECIMAL(10, 2),
    occasion VARCHAR(100),
    body_type_suitable VARCHAR(100)[],
    availability BOOLEAN DEFAULT TRUE,
    image_url VARCHAR(500),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Fabrics table
CREATE TABLE IF NOT EXISTS fabrics (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    properties JSONB DEFAULT '{}',
    care_instructions TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Chat sessions table
CREATE TABLE IF NOT EXISTS chat_sessions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id) ON DELETE SET NULL,
    title VARCHAR(255),
    language VARCHAR(10) DEFAULT 'en',
    context JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Messages table
CREATE TABLE IF NOT EXISTS messages (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    session_id UUID REFERENCES chat_sessions(id) ON DELETE CASCADE,
    role VARCHAR(20) NOT NULL CHECK (role IN ('user', 'assistant', 'system')),
    content TEXT NOT NULL,
    language VARCHAR(10),
    audio_url VARCHAR(500),
    rich_content JSONB,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Feedback table
CREATE TABLE IF NOT EXISTS feedback (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    session_id UUID REFERENCES chat_sessions(id) ON DELETE CASCADE,
    message_id UUID REFERENCES messages(id) ON DELETE SET NULL,
    rating INTEGER CHECK (rating BETWEEN 1 AND 5),
    comment TEXT,
    is_helpful BOOLEAN,
    corrections TEXT[],
    processed BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Recommendations table
CREATE TABLE IF NOT EXISTS recommendations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id) ON DELETE SET NULL,
    session_id UUID REFERENCES chat_sessions(id) ON DELETE SET NULL,
    product_id INTEGER REFERENCES products(id) ON DELETE SET NULL,
    reason TEXT,
    confidence_score FLOAT,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- User preferences table
CREATE TABLE IF NOT EXISTS user_preferences (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    preferred_colors VARCHAR(50)[],
    preferred_fabrics VARCHAR(100)[],
    body_type VARCHAR(50),
    budget_range NUMRANGE,
    style_preferences TEXT[],
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Analytics events table
CREATE TABLE IF NOT EXISTS analytics_events (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    session_id UUID REFERENCES chat_sessions(id) ON DELETE SET NULL,
    user_id UUID REFERENCES users(id) ON DELETE SET NULL,
    event_type VARCHAR(100) NOT NULL,
    event_data JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_messages_session ON messages(session_id);
CREATE INDEX IF NOT EXISTS idx_messages_created ON messages(created_at);
CREATE INDEX IF NOT EXISTS idx_products_category ON products(category);
CREATE INDEX IF NOT EXISTS idx_products_fabric ON products(fabric_type);
CREATE INDEX IF NOT EXISTS idx_feedback_session ON feedback(session_id);
CREATE INDEX IF NOT EXISTS idx_feedback_rating ON feedback(rating);
CREATE INDEX IF NOT EXISTS idx_analytics_events_type ON analytics_events(event_type);

-- Insert sample data
INSERT INTO products (name, category, description, fabric_type, color, price, occasion, body_type_suitable) VALUES
('Elegant Silk Dress', 'Dress', 'Beautiful silk dress perfect for formal occasions', 'Silk', 'Navy Blue', 199.99, 'Formal', ARRAY['slim', 'curvy', 'petite']),
('Casual Cotton Shirt', 'Top', 'Comfortable cotton shirt for everyday wear', 'Cotton', 'White', 49.99, 'Casual', ARRAY['slim', 'athletic', 'petite']),
('Designer Denim Jeans', 'Bottom', 'Stylish denim jeans with perfect fit', 'Denim', 'Blue', 89.99, 'Casual', ARRAY['slim', 'athletic', 'plus']);

INSERT INTO fabrics (name, properties, care_instructions) VALUES
('Silk', '{"breathable": true, "delicate": true}', 'Dry clean only, do not bleach'),
('Cotton', '{"breathable": true, "durable": true}', 'Machine wash cold, tumble dry low'),
('Denim', '{"durable": true, "stretch": false}', 'Machine wash cold, do not bleach');
