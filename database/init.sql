-- AI Video Database Schema
-- This file initializes the database tables for the AI Video Generator project

-- Users table
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    email VARCHAR(255) UNIQUE NOT NULL,
    username VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    first_name VARCHAR(100),
    last_name VARCHAR(100),
    is_active BOOLEAN DEFAULT 1 NOT NULL,
    is_verified BOOLEAN DEFAULT 0 NOT NULL,
    last_login TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL
);

-- Create indexes for users
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
CREATE INDEX IF NOT EXISTS idx_users_username ON users(username);

-- Projects table
CREATE TABLE IF NOT EXISTS projects (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    topic VARCHAR(500),
    status VARCHAR(50) DEFAULT 'draft' NOT NULL,
    total_duration REAL,
    total_scenes INTEGER DEFAULT 0,
    settings JSON,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- Create indexes for projects
CREATE INDEX IF NOT EXISTS idx_projects_user_id ON projects(user_id);
CREATE INDEX IF NOT EXISTS idx_projects_status ON projects(status);

-- Scenes table
CREATE TABLE IF NOT EXISTS scenes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    project_id INTEGER NOT NULL,
    scene_number INTEGER NOT NULL,
    narration TEXT NOT NULL,
    visual_prompt TEXT NOT NULL,
    duration REAL NOT NULL,
    camera_movement VARCHAR(100) DEFAULT 'static',
    mood VARCHAR(100) DEFAULT 'professional',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE
);

-- Create indexes for scenes
CREATE INDEX IF NOT EXISTS idx_scenes_project_id ON scenes(project_id);
CREATE INDEX IF NOT EXISTS idx_scenes_scene_number ON scenes(scene_number);

-- Generated assets table
CREATE TABLE IF NOT EXISTS generated_assets (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    project_id INTEGER NOT NULL,
    scene_id INTEGER,
    asset_type VARCHAR(50) NOT NULL,
    file_path VARCHAR(500) NOT NULL,
    file_url VARCHAR(500),
    file_size INTEGER,
    asset_metadata JSON,
    status VARCHAR(50) DEFAULT 'processing' NOT NULL,
    error_message TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE,
    FOREIGN KEY (scene_id) REFERENCES scenes(id) ON DELETE CASCADE
);

-- Create indexes for generated_assets
CREATE INDEX IF NOT EXISTS idx_generated_assets_project_id ON generated_assets(project_id);
CREATE INDEX IF NOT EXISTS idx_generated_assets_scene_id ON generated_assets(scene_id);
CREATE INDEX IF NOT EXISTS idx_generated_assets_asset_type ON generated_assets(asset_type);
CREATE INDEX IF NOT EXISTS idx_generated_assets_status ON generated_assets(status);

-- Trigger to update updated_at timestamp for users
CREATE TRIGGER IF NOT EXISTS update_users_timestamp 
AFTER UPDATE ON users
BEGIN
    UPDATE users SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
END;

-- Trigger to update updated_at timestamp for projects
CREATE TRIGGER IF NOT EXISTS update_projects_timestamp 
AFTER UPDATE ON projects
BEGIN
    UPDATE projects SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
END;

-- Trigger to update updated_at timestamp for scenes
CREATE TRIGGER IF NOT EXISTS update_scenes_timestamp 
AFTER UPDATE ON scenes
BEGIN
    UPDATE scenes SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
END;

-- Trigger to update updated_at timestamp for generated_assets
CREATE TRIGGER IF NOT EXISTS update_generated_assets_timestamp 
AFTER UPDATE ON generated_assets
BEGIN
    UPDATE generated_assets SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
END;
