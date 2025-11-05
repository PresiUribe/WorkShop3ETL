-- Script to create the database and table for storing predictions
-- Run this in MySQL Workbench before running the Kafka consumer

-- Create database
CREATE DATABASE IF NOT EXISTS happiness_predictions;

-- Use the database
USE happiness_predictions;

-- Create predictions table
CREATE TABLE IF NOT EXISTS predictions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    country VARCHAR(255),
    region VARCHAR(255),
    year VARCHAR(10),
    economy_gdp FLOAT,
    family FLOAT,
    health_life_expectancy FLOAT,
    freedom FLOAT,
    trust_government FLOAT,
    generosity FLOAT,
    dystopia_residual FLOAT,
    actual_happiness_score FLOAT,
    predicted_happiness_score FLOAT,
    prediction_error FLOAT,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_country (country),
    INDEX idx_year (year),
    INDEX idx_timestamp (timestamp)
);

-- Display table structure
DESCRIBE predictions;

-- Display message
SELECT 'Database and table created successfully!' AS Status;
