# 🌍 Happiness Score Prediction with Kafka + Machine Learning

ETL Workshop 3 - Data Engineering and Artificial Intelligence  
Universidad Autónoma de Occidente

## 📋 Project Overview

This project implements an end-to-end ML pipeline that combines **Data Streaming (Apache Kafka)** with **Machine Learning** to predict happiness scores across different countries and years. The system trains a regression model on World Happiness Report data, streams transformed data through Kafka, and stores predictions in a MySQL database for analysis.

## 🏗️ System Architecture

```
CSV Files → EDA → Model Training → .pkl Model
                                      ↓
Test Data → Kafka Producer → Kafka Topic → Kafka Consumer → Predictions
                                                  ↓
                                            Load Model (.pkl)
                                                  ↓
                                            MySQL Database
```

## 🎯 Key Features

- **ETL Pipeline**: Extract, Transform, Load data from multiple CSV sources
- **Machine Learning**: Train regression model (70/30 split) to predict happiness scores
- **Real-time Streaming**: Stream data using Apache Kafka
- **Prediction System**: Load trained model and predict on streaming data
- **Database Storage**: Store features, actual scores, and predictions in MySQL
- **Performance Metrics**: R², MAE, RMSE evaluation

## 📁 Project Structure

```
happiness-kafka-project/
├── data/
│   ├── raw/                    # Place your 5 CSV files here
│   └── processed/              # Processed data (auto-generated)
├── models/
│   └── happiness_model.pkl     # Trained model (auto-generated)
├── src/
│   ├── config.py              # Configuration file
│   ├── train_model.py         # Model training script
│   ├── kafka_producer.py      # Kafka producer
│   └── kafka_consumer.py      # Kafka consumer
├── database/
│   └── create_database.sql    # SQL script to create database
├── notebooks/                  # Jupyter notebooks (optional)
├── visualizations/            # Charts and visualizations
├── .env                       # Environment variables (create this)
├── .env.example              # Environment variables template
├── .gitignore
├── requirements.txt
└── README.md
```

## 🚀 Setup Instructions

### 1. Prerequisites

- Python 3.7+
- MySQL (with Workbench)
- Apache Kafka (installed and running)
- WSL (if using Windows)

### 2. Clone/Download the Project

```bash
git clone <your-repo-url>
cd happiness-kafka-project
```

### 3. Install Python Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables

Create a `.env` file in the project root:

```bash
cp .env.example .env
```

Edit `.env` with your MySQL credentials:

```env
DB_HOST=localhost
DB_PORT=3306
DB_USER=root
DB_PASSWORD=your_password_here
DB_NAME=happiness_predictions

KAFKA_BOOTSTRAP_SERVERS=localhost:9092
KAFKA_TOPIC=happiness-data

MODEL_PATH=models/happiness_model.pkl
```

### 5. Setup MySQL Database

Run the SQL script in MySQL Workbench:

```bash
mysql -u root -p < database/create_database.sql
```

Or open `database/create_database.sql` in MySQL Workbench and execute it.

### 6. Add Your Data

Place your 5 CSV files in the `data/raw/` directory:
- 2015.csv
- 2016.csv
- 2017.csv
- 2018.csv
- 2019.csv (or whatever years you have)

## 📊 Running the Project

### Step 1: Start Kafka Services

Open **3 separate CMD/Terminal windows**:

**Terminal 1 - Start Zookeeper:**
```bash
cd C:\kafka  # or your Kafka installation path
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

### Step 2: Train the Model

```bash
cd src
python train_model.py
```

This will:
- Load and combine all CSV files
- Preprocess the data
- Train the model (70/30 split)
- Save the model as `models/happiness_model.pkl`
- Save test data to `data/processed/test_data.csv`
- Print evaluation metrics (R², MAE, RMSE)

### Step 3: Start Kafka Consumer

Open a new terminal:

```bash
cd src
python kafka_consumer.py
```

The consumer will:
- Load the trained model
- Connect to MySQL database
- Wait for incoming messages from Kafka

### Step 4: Start Kafka Producer

Open another terminal:

```bash
cd src
python kafka_producer.py
```

The producer will:
- Load test data
- Stream records to Kafka one by one
- Display progress

### Step 5: Monitor Results

Watch the consumer terminal for real-time predictions:

```
[Message 1] Denmark (2016)
  Actual Score:    7.5260
  Predicted Score: 7.5143
  Error:           0.0117
  ✓ Saved to database
```

## 📈 Evaluation Metrics

The model is evaluated using:
- **R² Score**: Coefficient of determination
- **MAE (Mean Absolute Error)**: Average absolute difference
- **RMSE (Root Mean Squared Error)**: Square root of average squared differences

## 🗄️ Database Schema

**Table: `predictions`**

| Column | Type | Description |
|--------|------|-------------|
| id | INT | Primary key (auto-increment) |
| country | VARCHAR(255) | Country name |
| region | VARCHAR(255) | Geographic region |
| year | VARCHAR(10) | Year of data |
| economy_gdp | FLOAT | GDP per capita |
| family | FLOAT | Family support score |
| health_life_expectancy | FLOAT | Life expectancy score |
| freedom | FLOAT | Freedom score |
| trust_government | FLOAT | Government trust score |
| generosity | FLOAT | Generosity score |
| dystopia_residual | FLOAT | Dystopia residual score |
| actual_happiness_score | FLOAT | Actual happiness score |
| predicted_happiness_score | FLOAT | ML predicted score |
| prediction_error | FLOAT | Absolute error |
| timestamp | TIMESTAMP | Record creation time |

## 📊 Query Examples

```sql
-- View all predictions
SELECT * FROM predictions ORDER BY timestamp DESC LIMIT 10;

-- Average prediction error by country
SELECT country, AVG(prediction_error) as avg_error
FROM predictions
GROUP BY country
ORDER BY avg_error;

-- Compare actual vs predicted scores
SELECT country, year, 
       actual_happiness_score, 
       predicted_happiness_score,
       prediction_error
FROM predictions
WHERE year = '2016'
ORDER BY actual_happiness_score DESC;
```

## 🛠️ Technologies Used

- **Python 3.x**: Main programming language
- **Pandas & NumPy**: Data manipulation
- **Scikit-learn**: Machine learning (LinearRegression)
- **Apache Kafka**: Data streaming
- **kafka-python**: Python Kafka client
- **MySQL**: Database storage
- **mysql-connector-python**: MySQL Python driver
- **python-dotenv**: Environment variables management
- **Joblib**: Model serialization

## 🎓 Learning Objectives Achieved

✅ Conduct EDA on multiple datasets  
✅ Perform ETL processes  
✅ Engineer features for regression modeling  
✅ Train and evaluate ML model (70/30 split)  
✅ Implement Kafka-based streaming system  
✅ Use serialized model for predictions  
✅ Store results in database  
✅ Compute performance metrics  

## 🐛 Troubleshooting

### Kafka Connection Issues
- Ensure Zookeeper and Kafka are running
- Check ports 2181 (Zookeeper) and 9092 (Kafka)
- Verify `KAFKA_BOOTSTRAP_SERVERS` in `.env`

### Database Connection Issues
- Verify MySQL is running
- Check credentials in `.env` file
- Ensure database `happiness_predictions` exists

### Model Not Found
- Run `train_model.py` first
- Check `MODEL_PATH` in `.env`

### Import Errors
- Ensure all dependencies are installed: `pip install -r requirements.txt`
- Activate virtual environment if using one

## 📝 Next Steps

1. **Visualizations**: Create dashboards in PowerBI/Tableau/Looker
2. **Advanced Models**: Try RandomForestRegressor or XGBoost
3. **Feature Engineering**: Add more derived features
4. **Hyperparameter Tuning**: Optimize model parameters
5. **Real-time Monitoring**: Add logging and monitoring

## 👥 Authors

- Your Name
- Universidad Autónoma de Occidente
- Data Engineering and AI Program

## 📄 License

This project is part of the ETL course (Workshop 3).

---

**Happy Coding! 🚀**
