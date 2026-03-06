-- Create database
CREATE DATABASE IF NOT EXISTS team_builder;
USE team_builder;

-- Create teams table
CREATE TABLE IF NOT EXISTS teams (
    id INT AUTO_INCREMENT PRIMARY KEY,
    team_name VARCHAR(100) NOT NULL,
    secret_key VARCHAR(255) NOT NULL,
    members TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- Create index for faster searches
CREATE INDEX idx_team_name ON teams(team_name);