-- Script to create the database and table for storing predictions
-- Run this in MySQL Workbench before running the Kafka consumer

-- Create database
CREATE DATABASE IF NOT EXISTS happiness_predictions;

-- Use the database
USE happiness_predictions;

-- Drop table if exists (to recreate with new structure)
DROP TABLE IF EXISTS predictions;

-- Create predictions table with standardized column names
CREATE TABLE IF NOT EXISTS predictions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    country VARCHAR(255),
    region VARCHAR(255),
    year VARCHAR(10),
    gdp FLOAT,
    family FLOAT,
    health FLOAT,
    freedom FLOAT,
    trust FLOAT,
    generosity FLOAT,
    actual_happiness_score FLOAT,
    predicted_happiness_score FLOAT,
    prediction_error FLOAT,
    data_split VARCHAR(10),              -- NEW: 'train' or 'test'
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_country (country),
    INDEX idx_year (year),
    INDEX idx_data_split (data_split),   -- NEW: Index for filtering
    INDEX idx_timestamp (timestamp)
);

-- Display table structure
DESCRIBE predictions;

-- Display message
SELECT 'Database and table created successfully!' AS Status;