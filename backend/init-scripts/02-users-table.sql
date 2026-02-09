-- Users table for JWT authentication
-- Run this in PostgreSQL to create the users table

-- Drop existing users table if exists (for fresh setup)
DROP TABLE IF EXISTS users CASCADE;

-- Create users table
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    name VARCHAR(255) NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create index on email for faster lookups
CREATE INDEX idx_users_email ON users(email);

-- Add comments
COMMENT ON TABLE users IS 'Users table for JWT authentication';
COMMENT ON COLUMN users.hashed_password IS 'Bcrypt hashed password';
COMMENT ON COLUMN users.is_active IS 'Account active status';
