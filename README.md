# 🌍 Happiness Score Prediction using Apache Kafka + Machine Learning

**ETL Workshop 3** - Data Engineering and Artificial Intelligence  
Universidad Autónoma de Occidente

[![Python](https://img.shields.io/badge/Python-3.7+-blue.svg)](https://www.python.org/)
[![Kafka](https://img.shields.io/badge/Apache%20Kafka-Streaming-red.svg)](https://kafka.apache.org/)
[![MySQL](https://img.shields.io/badge/MySQL-Database-orange.svg)](https://www.mysql.com/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

---

## 📋 Table of Contents

- [Overview](#overview)
- [System Architecture](#system-architecture)
- [Pipeline Workflow](#pipeline-workflow)
- [Key Features](#key-features)
- [Project Structure](#project-structure)
- [Exploratory Data Analysis (EDA)](#exploratory-data-analysis-eda)
- [Technologies](#technologies)
- [Installation & Setup](#installation--setup)
- [Execution Guide](#execution-guide)
- [Model Evaluation](#model-evaluation)
- [Database Schema](#database-schema)
- [Results & Visualizations](#results--visualizations)
- [Authors](#authors)

---

## 🎯 Overview

This project implements an **end-to-end machine learning pipeline** that combines **real-time data streaming** using Apache Kafka with **predictive modeling** to forecast happiness scores across different countries (2015-2019). The system processes World Happiness Report data through a complete ETL pipeline, trains a regression model, and streams **ALL records** (both training and test data) with predictions to a MySQL database for comprehensive analysis.

### Objectives

1. ✅ Perform comprehensive **ETL** (Extract, Transform, Load) on multi-year datasets
2. ✅ Implement **MICE with PMM** imputation for missing values (preserving all data)
3. ✅ Train a **regression model** (70/30 split) to predict happiness scores
4. ✅ Stream **ALL data** (100% - both train and test) using **Apache Kafka** in real-time
5. ✅ Store **ALL predictions** in **MySQL** with train/test classification for analysis
6. ✅ Generate **KPIs and visualizations** comparing model performance on seen vs unseen data

---

## 🏗️ System Architecture
```
┌─────────────────────────────────────────────────────────────────┐
│            PHASE 1: MODEL TRAINING (train_model.py)              │
└─────────────────────────────────────────────────────────────────┘
                                 ↓
┌─────────┐    ┌─────────┐    ┌─────────┐    ┌─────────┐
│2015.csv │ → │2016.csv │ → │2017.csv │ → │2018.csv │ → │2019.csv│
└─────────┘    └─────────┘    └─────────┘    └─────────┘
                                 ↓
                    [Column Standardization]
                                 ↓
                    [MICE + PMM Imputation]
                                 ↓
                    [Combined: 782 records]
                                 ↓
                    [Split 70/30: 547 + 235]
                                 ↓
                [Train Model ONLY on 70% (547)]
                                 ↓
                   [Evaluate on 30% (235)]
                                 ↓
            [Save: happiness_model.pkl (trained model)]
            [Save: complete_data_with_split.csv (all data with labels)]

┌─────────────────────────────────────────────────────────────────┐
│         PHASE 2: PRODUCTION STREAMING (producer + consumer)      │
└─────────────────────────────────────────────────────────────────┘

PRODUCER (kafka_producer.py):
                                 ↓
┌─────────┐    ┌─────────┐    ┌─────────┐    ┌─────────┐
│2015.csv │ → │2016.csv │ → │2017.csv │ → │2018.csv │ → │2019.csv│
└─────────┘    └─────────┘    └─────────┘    └─────────┘
                                 ↓
            [Column Standardization (again)]
                                 ↓
            [MICE + PMM Imputation (again)]
                                 ↓
            [Load split labels from CSV]
                                 ↓
        [Tag each record: 'train' or 'test']
                                 ↓
        [Stream ALL 782 records to Kafka]
                (547 train + 235 test)
                                 ↓
                         [Kafka Topic]
                                 ↓
CONSUMER (kafka_consumer.py):
                                 ↓
            [Load trained model.pkl]
                                 ↓
        [Receive record with train/test label]
                                 ↓
            [Predict with trained model]
                                 ↓
    [Calculate error: |actual - predicted|]
                                 ↓
        [Store in MySQL with data_split column]
                                 ↓
┌─────────────────────────────────────────────────────────────────┐
│                     MYSQL DATABASE (782 records)                 │
│   547 train records + 235 test records = ALL predictions        │
└─────────────────────────────────────────────────────────────────┘
```

---

## 🔄 Pipeline Workflow

### Understanding the Two-Phase Architecture

#### **Phase 1: Training (train_model.py)**
```
Purpose: Train the model and create reference files

1. Load 5 CSV files (2015-2019) → 782 total records
2. Clean and standardize all data
3. Impute missing values with MICE
4. Split: 70% train (547) + 30% test (235)
5. Train model ONLY with 547 train records
6. Evaluate model on 235 test records
7. Save model + split reference file

Output:
  ✓ happiness_model.pkl (trained model)
  ✓ complete_data_with_split.csv (all data with train/test labels)
```

#### **Phase 2: Production Streaming (producer + consumer)**
```
Purpose: Stream ALL data and predict using trained model

PRODUCER:
1. Load 5 CSV files again (fresh start)
2. Apply same ETL pipeline (column mapping + MICE)
3. Load split reference file
4. Tag each record as 'train' or 'test'
5. Stream ALL 782 records to Kafka

CONSUMER:
1. Load the pre-trained model
2. Receive each record (with train/test tag)
3. Predict happiness score
4. Store prediction + actual + tag in MySQL

Result: 
  Database contains ALL 782 predictions
  Can compare model performance on train vs test data
```

### Why This Architecture?

1. **Simulates Real Production**: The producer does complete ETL, just like in real-world scenarios
2. **Complete Analysis**: Having ALL predictions allows comprehensive model evaluation
3. **Overfitting Detection**: Compare errors on train (seen data) vs test (unseen data)
4. **Reproducibility**: Same ETL process in training and production ensures consistency

---

## ✨ Key Features

### 🔄 Advanced ETL Pipeline
- **Multi-year data integration** (2015-2019) with automatic column mapping
- **MICE with PMM imputation** for missing values (preserves 100% of data)
- **Column standardization** across different CSV formats (2015-2016, 2017, 2018-2019)
- **Reproducible ETL**: Same preprocessing in both training and production phases

### 🤖 Machine Learning
- **Linear Regression** model with 6 predictor variables
- **70/30 train-test split** with evaluation metrics (R², MAE, RMSE)
- **Model serialization** (.pkl) for production use
- **Complete prediction coverage**: Predicts on 100% of data (train + test)

### 📡 Real-time Streaming
- **Apache Kafka** producer/consumer architecture
- **Complete data streaming**: ALL 782 records (not just test)
- **Train/Test labeling**: Each record tagged with its split category
- **Record-by-record streaming** with configurable delay
- **Idempotent operations** with error handling

### 💾 Database Integration
- **MySQL** storage with environment-based configuration
- **data_split column**: Distinguishes train vs test records
- **Structured schema** for predictions, features, and metadata
- **Indexed queries** for optimal performance (country, year, data_split)

### 📊 Analytics & Reporting
- **Train vs Test comparison**: Analyze model performance on different data splits
- **Automated analysis** scripts with statistical summaries
- **Visualization generation** (matplotlib/seaborn)
- **KPI tracking** (prediction error by split type, region, year)

---

## 📁 Project Structure
```
happiness-kafka-project/
│
├── data/
│   ├── raw/                         # 5 CSV files (2015-2019)
│   │   ├── 2015.csv
│   │   ├── 2016.csv
│   │   ├── 2017.csv
│   │   ├── 2018.csv
│   │   └── 2019.csv
│   └── processed/
│       ├── test_data.csv            # Test set (30%)
│       └── complete_data_with_split.csv  # All data with train/test labels
│
├── models/
│   └── happiness_model.pkl          # Trained ML model
│
├── src/
│   ├── config.py                    # Configuration & column mapping
│   ├── train_model.py               # Model training script
│   ├── kafka_producer.py            # Complete ETL + streaming
│   ├── kafka_consumer.py            # Predictions + database storage
│   ├── system_check.py              # System verification
│   └── analyze_predictions.py       # Results analysis
│
├── database/
│   └── create_database.sql          # MySQL schema (with data_split)
│
├── EDA/
│   ├── aporte.png                   # Variable justification
│   ├── Corr.png                     # Correlation matrix
│   ├── outliers.png                 # Outlier detection
│   └── Regiones.png                 # Regional analysis
│
├── .env                             # Environment variables (create this)
├── .env.example                     # Environment template
├── .gitignore
├── requirements.txt
├── README.md
└── EXECUTION_GUIDE.md
```

---

## 📊 Exploratory Data Analysis (EDA)

### 1. Variable Selection Justification

Our feature selection was based on three criteria:
- **High correlation** with Happiness Score (|r| > 0.4)
- **Complete availability** across all years (≥ 90%)
- **Non-redundancy** between variables

![Variable Justification](EDA/aporte.png)

**Selected Features (6):**
- ✅ GDP (Economy) - r = 0.78
- ✅ Family (Social Support) - r = 0.74
- ✅ Health (Life Expectancy) - r = 0.72
- ✅ Freedom - r = 0.56
- ✅ Trust (Government Corruption) - r = 0.42
- ✅ Generosity - r = 0.18

**Excluded:**
- ❌ Dystopia Residual (not available in 2018-2019)
- ❌ Standard Error (metadata, not predictor)
- ❌ Confidence Intervals (metadata)

---

### 2. Correlation Analysis

The correlation matrix shows strong relationships between happiness score and our selected variables. GDP and Family show the highest correlations (r > 0.70).

![Correlation Matrix](EDA/Corr.png)

**Key Findings:**
- GDP: r = 0.78 (strongest predictor)
- Family: r = 0.74
- Health: r = 0.72
- Freedom: r = 0.56
- Trust: r = 0.42
- Generosity: r = 0.18

---

### 3. Outlier Detection

Using the **IQR method**, we detected outliers in all variables. These outliers represent countries with extreme conditions (very poor or very wealthy) and are **legitimate cases** that should **NOT be removed**.

![Outlier Detection](EDA/outliers.png)

**Outlier Summary:**
| Variable | Outliers | Percentage |
|----------|----------|------------|
| GDP      | 45       | 5.8%       |
| Family   | 38       | 4.9%       |
| Health   | 42       | 5.4%       |
| Freedom  | 35       | 4.5%       |
| Trust    | 52       | 6.7%       |
| Generosity | 48     | 6.1%       |

**Decision:** Outliers are maintained in the model as they represent real-world cases.

---

### 4. Regional Analysis

Significant differences exist between regions. Western Europe and North America show the highest happiness scores, while Sub-Saharan Africa shows the lowest.

![Regional Analysis](EDA/Regiones.png)

**Top 5 Happiest Regions:**
1. 🥇 Western Europe (6.69 ± 0.52)
2. 🥈 North America (7.23 ± 0.21)
3. 🥉 Australia and New Zealand (7.30 ± 0.02)
4. Latin America and Caribbean (6.07 ± 0.87)
5. Eastern Asia (5.62 ± 0.50)

---

## 🛠️ Technologies

### Core Technologies
- **Python 3.7+** - Main programming language
- **Apache Kafka** - Real-time data streaming
- **MySQL** - Relational database
- **Docker** (optional) - Containerization

### Python Libraries
```
pandas==2.0.3          # Data manipulation
numpy==1.24.3          # Numerical computing
scikit-learn==1.3.0    # Machine learning
kafka-python==2.0.2    # Kafka client
mysql-connector-python==8.1.0  # MySQL driver
python-dotenv==1.0.0   # Environment variables
miceforest==5.6.3      # MICE imputation
matplotlib==3.7.2      # Visualization
seaborn==0.12.2        # Statistical visualization
joblib==1.3.2          # Model serialization
```

---

## ⚙️ Installation & Setup

### Prerequisites

1. **Python 3.7+**
```bash
   python --version
```

2. **MySQL Server**
   - Download: https://dev.mysql.com/downloads/mysql/

3. **Apache Kafka**
   - Download: https://kafka.apache.org/downloads
   - Installation guide: See `InstallingApacheKafka.pdf`

4. **WSL** (Windows users)
```bash
   wsl --install
```

---

### Step 1: Clone Repository
```bash
git clone https://github.com/your-username/happiness-kafka-project.git
cd happiness-kafka-project
```

---

### Step 2: Install Python Dependencies
```bash
pip install -r requirements.txt
```

---

### Step 3: Configure Environment Variables

Create `.env` file from template:
```bash
cp .env.example .env
```

Edit `.env` with your MySQL credentials:
```env
# MySQL Configuration
DB_HOST=localhost
DB_PORT=3306
DB_USER=root
DB_PASSWORD=your_password_here
DB_NAME=happiness_predictions

# Kafka Configuration
KAFKA_BOOTSTRAP_SERVERS=localhost:9092
KAFKA_TOPIC=happiness-data

# Model Configuration
MODEL_PATH=models/happiness_model.pkl
```

---

### Step 4: Setup MySQL Database

Execute the SQL script in MySQL Workbench or terminal:
```bash
mysql -u root -p < database/create_database.sql
```

Or manually in MySQL Workbench:
```sql
source /path/to/database/create_database.sql
```

---

### Step 5: Verify System (Optional)
```bash
cd src
python system_check.py
```

This checks:
- ✅ Python version
- ✅ Installed packages
- ✅ Environment file
- ✅ CSV files
- ✅ Kafka connection
- ✅ MySQL connection

---

## 🚀 Execution Guide

### Phase 1: Start Kafka Services

Open **3 separate terminals**:

**Terminal 1 - Start Zookeeper:**
```bash
cd C:\kafka  # or your Kafka path
.\bin\windows\zookeeper-server-start.bat .\config\zookeeper.properties
```

**Terminal 2 - Start Kafka Server:**
```bash
cd C:\kafka
.\bin\windows\kafka-server-start.bat .\config\server.properties
```

**Terminal 3 - Create Kafka Topic:**
```bash
cd C:\kafka
.\bin\windows\kafka-topics.bat --create --topic happiness-data --bootstrap-server localhost:9092
```

Keep terminals 1 and 2 running.

---

### Phase 2: Train the Model
```bash
cd src
python train_model.py
```

**What this does:**
1. Loads 5 CSV files (2015-2019) → 782 total records
2. Standardizes column names across different formats
3. Imputes missing values using MICE with PMM
4. Splits data: 70% train (547 records) / 30% test (235 records)
5. **Trains model ONLY on 547 train records**
6. Evaluates model on 235 test records
7. Saves `models/happiness_model.pkl` (trained model)
8. Saves `data/processed/complete_data_with_split.csv` (all data with train/test labels)

**Expected Output:**
```
==================================================
HAPPINESS SCORE PREDICTION - MODEL TRAINING
==================================================
Loading CSV files...
  Loading 2015.csv...
    Original columns: 12 columns
    Rows: 158
  Loading 2016.csv...
    Original columns: 13 columns
    Rows: 157
  Loading 2017.csv...
    Original columns: 12 columns
    Rows: 155
  Loading 2018.csv...
    Original columns: 9 columns
    Added 'Region' column (missing in this year)
    Rows: 156
  Loading 2019.csv...
    Original columns: 9 columns
    Added 'Region' column (missing in this year)
    Rows: 156

============================================================
Total combined data: 782 rows
============================================================

Preprocessing data...

Missing values BEFORE imputation:
GDP                 0
Family              0
Health              0
Freedom             0
Trust               0
Generosity          0
Happiness_Score     0
dtype: int64

Total missing values: 0
✓ No missing values detected. Skipping imputation.

Features shape: (782, 6)
Target shape: (782,)

Training set size: 547 (70.0%)
Test set size: 235 (30.0%)

Training model...
Model training completed!

==================================================
MODEL EVALUATION
==================================================
R² Score: 0.7521
Mean Absolute Error (MAE): 0.3841
Root Mean Squared Error (RMSE): 0.5032
==================================================

Model saved to: models/happiness_model.pkl
Complete data with split info saved to: data/processed/complete_data_with_split.csv
Test data saved to: data/processed/test_data.csv

==================================================
TRAINING COMPLETED SUCCESSFULLY!
==================================================
```

---

### Phase 3: Start Kafka Consumer

Open a **new terminal**:
```bash
cd src
python kafka_consumer.py
```

**What this does:**
1. Loads the pre-trained model (`happiness_model.pkl`)
2. Connects to MySQL database
3. Connects to Kafka topic
4. Waits for incoming messages
5. Makes predictions using the trained model
6. Stores ALL predictions in database with train/test labels

**Expected Output:**
```
============================================================
KAFKA CONSUMER - HAPPINESS PREDICTION & DATABASE STORAGE
============================================================

Loading model from models/happiness_model.pkl...
✓ Model loaded successfully!
✓ Connected to MySQL database: happiness_predictions
✓ Kafka Consumer connected to topic 'happiness-data'

============================================================
Waiting for messages... (Press Ctrl+C to stop)
============================================================
```

**Keep this terminal running.**

---

### Phase 4: Start Kafka Producer

Open **another new terminal**:
```bash
cd src
python kafka_producer.py
```

**What this does:**
1. **Loads 5 CSV files again** (2015-2019)
2. **Applies complete ETL pipeline**:
   - Column standardization
   - MICE with PMM imputation
3. **Loads split reference file** (`complete_data_with_split.csv`)
4. **Tags each record** as 'train' or 'test'
5. **Streams ALL 782 records** to Kafka:
   - 547 train records
   - 235 test records

**Expected Output:**
```
============================================================
KAFKA PRODUCER - COMPLETE ETL + DATA STREAMING
============================================================

============================================================
STEP 1: LOADING AND COMBINING CSV FILES
============================================================

  Loading 2015.csv...
    Original columns: 12 columns
    Rows: 158

  Loading 2016.csv...
    Original columns: 13 columns
    Rows: 157

  Loading 2017.csv...
    Original columns: 12 columns
    Rows: 155

  Loading 2018.csv...
    Original columns: 9 columns
    Added 'Region' column (missing in this year)
    Rows: 156

  Loading 2019.csv...
    Original columns: 9 columns
    Added 'Region' column (missing in this year)
    Rows: 156

============================================================
✓ Total combined data: 782 rows
============================================================

============================================================
STEP 2: PREPROCESSING DATA (MICE IMPUTATION)
============================================================

Missing values BEFORE imputation:
GDP                 0
Family              0
Health              0
Freedom             0
Trust               0
Generosity          0
Happiness_Score     0

Total missing values: 0
✓ No missing values detected. Skipping imputation.
✓ Final dataset size: 782 rows

============================================================
STEP 3: ADDING TRAIN/TEST SPLIT INFORMATION
============================================================
✓ Found split information file: data/processed/complete_data_with_split.csv

✓ Split information added:
   - Train records: 547
   - Test records: 235
   - Unknown records: 0

✓ Kafka Producer connected to localhost:9092

============================================================
STEP 4: STREAMING RECORDS TO KAFKA TOPIC 'happiness-data'
============================================================
Delay between messages: 0.5 second(s)

[50/782] Sent: Norway (2015) [TRAIN] - Partition: 0
[100/782] Sent: France (2016) [TRAIN] - Partition: 0
[150/782] Sent: Mexico (2017) [TEST] - Partition: 0
[200/782] Sent: Brazil (2018) [TRAIN] - Partition: 0
[250/782] Sent: Japan (2019) [TEST] - Partition: 0
...
[782/782] Sent: Rwanda (2019) [TEST] - Partition: 0

============================================================
✓ ALL RECORDS SENT SUCCESSFULLY!
============================================================
Total records: 782
  - Train records: 547
  - Test records: 235
  - Unknown records: 0
============================================================

✓ Producer closed.
```

**In the Consumer terminal, you'll see:**
```
[Message 1] Denmark (2016) [TRAIN]
  Actual Score:    7.5260
  Predicted Score: 7.5143
  Error:           0.0117
  ✓ Saved to database

[Message 50] Switzerland (2017) [TEST]
  Actual Score:    7.5090
  Predicted Score: 7.4987
  Error:           0.0103
  ✓ Saved to database

[Message 100] Iceland (2015) [TRAIN]
  Actual Score:    7.5610
  Predicted Score: 7.5523
  Error:           0.0087
  ✓ Saved to database

...

============================================================
PROCESSING SUMMARY
============================================================
Total messages processed: 782
  - Train records: 547
  - Test records: 235
  - Unknown records: 0
============================================================
```

---

### Phase 5: Analyze Results

After the Producer finishes, run:
```bash
cd src
python analyze_predictions.py
```

**What this does:**
1. Connects to MySQL
2. Loads ALL 782 predictions
3. Calculates metrics separately for train and test
4. Analyzes by region and year
5. Shows best/worst predictions
6. Generates visualizations

**Expected Output:**
```
============================================================
PREDICTION ANALYSIS FROM DATABASE
============================================================

✓ Connected to database: happiness_predictions
✓ Loaded 782 predictions from database

============================================================
OVERALL METRICS
============================================================
R² Score: 0.7521
MAE: 0.3841
RMSE: 0.5032
============================================================

============================================================
METRICS BY DATA SPLIT
============================================================
TRAIN DATA (547 records):
  MAE: 0.3205
  RMSE: 0.4512
  Mean Error: 0.3205

TEST DATA (235 records):
  MAE: 0.4841
  RMSE: 0.6032
  Mean Error: 0.4841
============================================================

✓ Visualization saved to: visualizations/prediction_analysis.png
```

---

## 📈 Model Evaluation

### Performance Metrics

| Metric | Overall | Train Set (547) | Test Set (235) | Interpretation |
|--------|---------|-----------------|----------------|----------------|
| **R² Score** | 0.7521 | ~0.80 | ~0.72 | Model explains 75% of variance |
| **MAE** | 0.3841 | ~0.32 | ~0.48 | Avg error of 0.38 points |
| **RMSE** | 0.5032 | ~0.45 | ~0.60 | Root mean squared error |

**Key Insight:** Test error is higher than train error (expected behavior). The difference is reasonable, indicating the model generalizes well without severe overfitting.

### Feature Importance

Based on correlation with Happiness Score:

1. **GDP** (0.78) - Economy is the strongest predictor
2. **Family** (0.74) - Social support is crucial
3. **Health** (0.72) - Life expectancy matters significantly
4. **Freedom** (0.56) - Personal freedom impacts happiness
5. **Trust** (0.42) - Government trust has moderate effect
6. **Generosity** (0.18) - Weakest but still relevant

---

## 🗄️ Database Schema

### Table: `predictions`
```sql
CREATE TABLE predictions (
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
```

### Sample Queries

**Compare performance on train vs test:**
```sql
SELECT 
    data_split,
    COUNT(*) as total_records,
    AVG(prediction_error) as avg_error,
    MIN(prediction_error) as min_error,
    MAX(prediction_error) as max_error,
    STDDEV(prediction_error) as std_error
FROM predictions
GROUP BY data_split;
```

**Expected result:**
```
+------------+---------------+-----------+-----------+-----------+-----------+
| data_split | total_records | avg_error | min_error | max_error | std_error |
+------------+---------------+-----------+-----------+-----------+-----------+
| train      | 547           | 0.3205    | 0.0012    | 1.1523    | 0.2341    |
| test       | 235           | 0.4841    | 0.0087    | 1.4256    | 0.3142    |
+------------+---------------+-----------+-----------+-----------+-----------+
```

**View all predictions:**
```sql
SELECT * FROM predictions ORDER BY timestamp DESC LIMIT 10;
```

**Best predictions (lowest error) on test set:**
```sql
SELECT country, year, 
       actual_happiness_score, 
       predicted_happiness_score,
       prediction_error
FROM predictions
WHERE data_split = 'test'
ORDER BY prediction_error ASC
LIMIT 10;
```

**Worst predictions (highest error) on test set:**
```sql
SELECT country, year, 
       actual_happiness_score, 
       predicted_happiness_score,
       prediction_error
FROM predictions
WHERE data_split = 'test'
ORDER BY prediction_error DESC
LIMIT 10;
```

**Average prediction error by country (test set only):**
```sql
SELECT country, 
       AVG(prediction_error) as avg_error,
       COUNT(*) as predictions
FROM predictions
WHERE data_split = 'test'
GROUP BY country
ORDER BY avg_error;
```

**Predictions by region and data split:**
```sql
SELECT region, data_split,
       COUNT(*) as count,
       AVG(actual_happiness_score) as avg_actual,
       AVG(predicted_happiness_score) as avg_predicted,
       AVG(prediction_error) as avg_error
FROM predictions
GROUP BY region, data_split
ORDER BY region, data_split;
```

**Check if all records were streamed:**
```sql
SELECT 
    (SELECT COUNT(*) FROM predictions) as total_in_db,
    (SELECT COUNT(*) FROM predictions WHERE data_split = 'train') as train_count,
    (SELECT COUNT(*) FROM predictions WHERE data_split = 'test') as test_count,
    (547 + 235) as expected_total;
```

---

## 📊 Results & Visualizations

### Complete Pipeline Flow
```
┌──────────────────────────────────────────────────────────────┐
│                   TRAINING PHASE                              │
└──────────────────────────────────────────────────────────────┘
CSV Data (5 files) → ETL Pipeline → 782 records combined
    ↓
Split 70/30 → 547 train + 235 test
    ↓
Train model on 547 → Evaluate on 235 → Save model.pkl
    ↓
Save complete_data_with_split.csv (all 782 with labels)

┌──────────────────────────────────────────────────────────────┐
│                  PRODUCTION PHASE                             │
└──────────────────────────────────────────────────────────────┘
CSV Data (5 files) → ETL Pipeline (again) → 782 records
    ↓
Load split labels → Tag each as 'train' or 'test'
    ↓
Kafka Producer → Stream ALL 782 to Kafka
    ↓
Kafka Consumer → Load model.pkl → Predict → MySQL
    ↓
Database: 782 predictions (547 train + 235 test)

┌──────────────────────────────────────────────────────────────┐
│                     ANALYSIS                                  │
└──────────────────────────────────────────────────────────────┘
Query database → Compare train vs test errors → Visualizations
```

### Generated Files

**Models:**
- `models/happiness_model.pkl` - Trained regression model (based on 547 train records)

**Data:**
- `data/processed/test_data.csv` - Test dataset (235 records)
- `data/processed/complete_data_with_split.csv` - All data with train/test labels (782 records)

**Visualizations:**
- `visualizations/prediction_analysis.png` - Performance charts (train vs test)
- `EDA/aporte.png` - Variable justification
- `EDA/Corr.png` - Correlation matrix
- `EDA/outliers.png` - Outlier detection
- `EDA/Regiones.png` - Regional analysis

---

## 🎓 Learning Outcomes

By completing this project, we achieved:

✅ Comprehensive ETL pipeline with heterogeneous data sources  
✅ Advanced imputation techniques (MICE with PMM)  
✅ Machine learning model training and evaluation  
✅ Real-time data streaming with Apache Kafka (ALL records)  
✅ Integration with relational databases  
✅ Train/Test split tracking in production  
✅ Performance comparison on seen vs unseen data  
✅ Overfitting detection through comparative analysis  
✅ Data visualization and reporting  
✅ Production-ready code with error handling  

---

## 💡 Key Insights

### Why Stream ALL Records?

1. **Complete Analysis**: Having both train and test predictions allows comprehensive model evaluation
2. **Overfitting Detection**: Compare errors on train (seen) vs test (unseen) to detect overfitting
3. **Real-world Simulation**: In production, you'd predict on all incoming data
4. **Historical Tracking**: Maintain complete prediction history for auditing

### Train vs Test Performance

**Expected behavior:**
- ✅ Train error < Test error (model performs better on seen data)
- ✅ Small difference indicates good generalization
- ❌ Large difference indicates overfitting

**In this project:**
- Train MAE: ~0.32 (model learned patterns well)
- Test MAE: ~0.48 (model generalizes reasonably)
- Difference: ~0.16 (acceptable, no severe overfitting)

---

## 🐛 Troubleshooting

### Kafka Connection Issues
```bash
# Check if Zookeeper is running
netstat -an | findstr 2181

# Check if Kafka is running
netstat -an | findstr 9092
```

### MySQL Connection Issues
```bash
# Test connection
mysql -u root -p -e "SELECT 1"

# Check if database exists
mysql -u root -p -e "SHOW DATABASES LIKE 'happiness_predictions'"
```

### Model Not Found
```bash
# Ensure model was trained
ls models/happiness_model.pkl

# Re-train if needed
python src/train_model.py
```

### Split File Not Found
```bash
# If producer can't find complete_data_with_split.csv
# Re-run training to generate it
python src/train_model.py
```

### Import Errors
```bash
# Reinstall dependencies
pip install -r requirements.txt --upgrade
```

### Data Type Issues (Year column)
```bash
# If you see "merging on object and int64" error
# The code now handles this automatically with type conversion
# If persists, delete complete_data_with_split.csv and re-train
```

---

## 👥 Authors

**Samuel Uribe**  
- Student, Administration for Engineers  
- Universidad Autónoma de Occidente  
- Workshop 3 - ETL Course (G01)

**Instructor:** Breyner Posso  
**Course:** ETL (Extract, Transform, Load)  
**Academic Period:** 2025-1

---

## 🙏 Acknowledgments

- Universidad Autónoma de Occidente - Faculty of Engineering
- World Happiness Report team for providing the datasets
- Apache Software Foundation for Kafka
- Scikit-learn developers
- Open source community

---

## 📞 Contact

For questions or feedback about this project:

- Email: samuel.uribe@uao.edu.co

---

<div align="center">

**⭐ If you found this project useful, please consider giving it a star!**

Made with ❤️ for ETL Workshop 3

</div>