-- AppointmentHub Database Initialization Script
-- This script sets up the initial database configuration

-- Create the main database (if not exists)
-- Note: This is handled by the POSTGRES_DB environment variable

-- Create additional databases for different environments
CREATE DATABASE appointment_hub_test;

-- Create extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";

-- Create indexes for better performance
-- These will be created by SQLAlchemy migrations, but we can pre-create some

-- Grant permissions
GRANT ALL PRIVILEGES ON DATABASE appointment_hub TO appointment_user;
GRANT ALL PRIVILEGES ON DATABASE appointment_hub_test TO appointment_user;

-- Set timezone
SET timezone = 'UTC';

