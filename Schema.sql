-- Enable foreign key support (for SQLite)
PRAGMA foreign_keys = ON;

-- 1. Users Table (Authentication & Session Management)
CREATE TABLE users (
    user_id SERIAL PRIMARY KEY,
    username VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 2. Skier Profiles Table (Member Details & Ability)
CREATE TABLE skier_profiles (
    profile_id SERIAL PRIMARY KEY,
    user_id INT NOT NULL UNIQUE,
    full_name VARCHAR(150) NOT NULL,
    age INT CHECK (age >= 1 AND age <= 120),
    skiing_ability VARCHAR(50) NOT NULL DEFAULT 'Beginner', -- e.g., Beginner, Intermediate, Advanced, Expert
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_user_profile FOREIGN KEY (user_id) 
        REFERENCES users(user_id) 
        ON DELETE CASCADE
);

-- 3. Mountains / Resorts Table (Directory Cache & Metadata)
CREATE TABLE mountains (
    mountain_id SERIAL PRIMARY KEY,
    name VARCHAR(200) NOT NULL,
    location VARCHAR(255), -- City, State, Country combined or normalized
    num_trails INT,
    difficulty_levels TEXT, -- Stored as text summary or JSON string
    lift_ticket_prices TEXT,
    available_lessons TEXT,
    trail_map_url TEXT,
    last_synced_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 4. User Favorite Mountains (Many-to-Many Bookmark Relationship)
CREATE TABLE user_favorite_mountains (
    user_id INT NOT NULL,
    mountain_id INT NOT NULL,
    favorited_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (user_id, mountain_id),
    CONSTRAINT fk_fav_user FOREIGN KEY (user_id) 
        REFERENCES users(user_id) 
        ON DELETE CASCADE,
    CONSTRAINT fk_fav_mountain FOREIGN KEY (mountain_id) 
        REFERENCES mountains(mountain_id) 
        ON DELETE CASCADE
);

-- Indexes for performance on frequent lookups & search queries
CREATE INDEX idx_users_username ON users(username);
CREATE INDEX idx_mountains_name ON mountains(name);
CREATE INDEX idx_mountains_location ON mountains(location);