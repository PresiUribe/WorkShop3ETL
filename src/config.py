"""
Configuration file for the Happiness Prediction Kafka project.
Loads environment variables from .env file.
"""
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# MySQL Database Configuration
DB_CONFIG = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'port': int(os.getenv('DB_PORT', 3306)),
    'user': os.getenv('DB_USER', 'root'),
    'password': os.getenv('DB_PASSWORD', ''),
    'database': os.getenv('DB_NAME', 'happiness_predictions')
}

# Kafka Configuration
KAFKA_CONFIG = {
    'bootstrap_servers': os.getenv('KAFKA_BOOTSTRAP_SERVERS', 'localhost:9092'),
    'topic': os.getenv('KAFKA_TOPIC', 'happiness-data')
}

# Model Configuration
MODEL_PATH = os.getenv('MODEL_PATH', 'models/happiness_model.pkl')

# Data Configuration
DATA_PATH = 'data/raw'
PROCESSED_DATA_PATH = 'data/processed'

# Column mapping to standardize different year formats
COLUMN_MAPPING = {
    # 2015 format
    'Country': 'Country',
    'Region': 'Region',
    'Happiness Rank': 'Happiness_Rank',
    'Happiness Score': 'Happiness_Score',
    'Economy (GDP per Capita)': 'GDP',
    'Family': 'Family',
    'Health (Life Expectancy)': 'Health',
    'Freedom': 'Freedom',
    'Trust (Government Corruption)': 'Trust',
    'Generosity': 'Generosity',
    'Dystopia Residual': 'Dystopia_Residual',
    
    # 2017 format (with dots)
    'Happiness.Rank': 'Happiness_Rank',
    'Happiness.Score': 'Happiness_Score',
    'Economy..GDP.per.Capita.': 'GDP',
    'Health..Life.Expectancy.': 'Health',
    'Trust..Government.Corruption.': 'Trust',
    'Dystopia.Residual': 'Dystopia_Residual',
    
    # 2018-2019 format
    'Overall rank': 'Happiness_Rank',
    'Country or region': 'Country',
    'Score': 'Happiness_Score',
    'GDP per capita': 'GDP',
    'Social support': 'Family',
    'Healthy life expectancy': 'Health',
    'Freedom to make life choices': 'Freedom',
    'Perceptions of corruption': 'Trust',
}

# Features to use for prediction (common across all years)
# Note: Dystopia Residual is excluded as it's not present in 2018-2019
FEATURE_COLUMNS = [
    'GDP',
    'Family',
    'Health',
    'Freedom',
    'Trust',
    'Generosity'
]

TARGET_COLUMN = 'Happiness_Score'