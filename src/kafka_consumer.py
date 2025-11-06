"""
Kafka Consumer: Receives streaming data, makes predictions, and stores results in MySQL.
"""
import pandas as pd
import json
import joblib
import numpy as np
import mysql.connector
from kafka import KafkaConsumer
from kafka.errors import KafkaError
from config import KAFKA_CONFIG, MODEL_PATH, DB_CONFIG

def load_model(model_path):
    """
    Load the trained model from file.
    
    Args:
        model_path: Path to the .pkl model file
    
    Returns:
        Loaded model
    """
    print(f"Loading model from {model_path}...")
    try:
        model = joblib.load(model_path)
        print("✓ Model loaded successfully!")
        return model
    except Exception as e:
        print(f"Error loading model: {e}")
        raise

def create_db_connection():
    """
    Create and return a MySQL database connection.
    
    Returns:
        MySQL connection object
    """
    try:
        connection = mysql.connector.connect(**DB_CONFIG)
        print(f"✓ Connected to MySQL database: {DB_CONFIG['database']}")
        return connection
    except mysql.connector.Error as e:
        print(f"Error connecting to MySQL: {e}")
        raise


def create_consumer():
    """
    Create and return a Kafka consumer instance.
    
    Returns:
        KafkaConsumer instance
    """
    try:
        consumer = KafkaConsumer(
            KAFKA_CONFIG['topic'],
            bootstrap_servers=KAFKA_CONFIG['bootstrap_servers'],
            auto_offset_reset='earliest',
            enable_auto_commit=True,
            group_id='happiness-prediction-group',
            value_deserializer=lambda m: json.loads(m.decode('utf-8'))
        )
        print(f"✓ Kafka Consumer connected to topic '{KAFKA_CONFIG['topic']}'")
        return consumer
    except KafkaError as e:
        print(f"Error creating Kafka Consumer: {e}")
        raise

def insert_prediction(cursor, connection, data, prediction):
    """
    Insert prediction results into the database.
    
    Args:
        cursor: MySQL cursor object
        connection: MySQL connection object
        data: Original data message
        prediction: Predicted happiness score
    """
    try:
        query = """
        INSERT INTO predictions (
            country, region, year,
            gdp, family, health,
            freedom, trust, generosity,
            actual_happiness_score, predicted_happiness_score, prediction_error,
            data_split
        ) VALUES (
            %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
        )
        """
        
        features = data['features']
        actual_score = data['actual_happiness_score']
        prediction_error = abs(actual_score - prediction)
        data_split = data.get('data_split', 'unknown')  # NEW
        
        values = (
            data['country'],
            data['region'],
            data['year'],
            features['gdp'],
            features['family'],
            features['health'],
            features['freedom'],
            features['trust'],
            features['generosity'],
            actual_score,
            float(prediction),
            float(prediction_error),
            data_split  # NEW
        )
        
        cursor.execute(query, values)
        connection.commit()
        
    except mysql.connector.Error as e:
        print(f"Error inserting into database: {e}")
        connection.rollback()

def process_messages(consumer, model, db_connection):
    """
    Process incoming messages from Kafka.
    
    Args:
        consumer: KafkaConsumer instance
        model: Trained ML model
        db_connection: MySQL database connection
    """
    cursor = db_connection.cursor()
    message_count = 0
    train_count = 0
    test_count = 0
    unknown_count = 0
    
    print("\n" + "="*60)
    print("Waiting for messages... (Press Ctrl+C to stop)")
    print("="*60 + "\n")
    
    try:
        for message in consumer:
            message_count += 1
            data = message.value
            
            # Count by split type
            data_split = data.get('data_split', 'unknown')
            if data_split == 'train':
                train_count += 1
            elif data_split == 'test':
                test_count += 1
            else:
                unknown_count += 1
            
            # Extract features for prediction (6 features)
            features = data['features']
            feature_array = np.array([[
                features['gdp'],
                features['family'],
                features['health'],
                features['freedom'],
                features['trust'],
                features['generosity']
            ]])
            
            # Make prediction
            prediction = model.predict(feature_array)[0]
            
            # Calculate error
            actual = data['actual_happiness_score']
            error = abs(actual - prediction)
            
            # Store in database
            insert_prediction(cursor, db_connection, data, prediction)
            
            # Print results (every 50 messages or if it's a test record)
            if message_count % 50 == 0 or data_split == 'test':
                print(f"[Message {message_count}] {data['country']} ({data['year']}) [{data_split.upper()}]")
                print(f"  Actual Score:    {actual:.4f}")
                print(f"  Predicted Score: {prediction:.4f}")
                print(f"  Error:           {error:.4f}")
                print(f"  ✓ Saved to database\n")
            
    except KeyboardInterrupt:
        print("\n\n⚠️ Consumer interrupted by user")
    finally:
        cursor.close()
        print(f"\n{'='*60}")
        print(f"PROCESSING SUMMARY")
        print(f"{'='*60}")
        print(f"Total messages processed: {message_count}")
        print(f"  - Train records: {train_count}")
        print(f"  - Test records: {test_count}")
        print(f"  - Unknown records: {unknown_count}")
        print(f"{'='*60}")

def main():
    """
    Main function to run the Kafka Consumer.
    """
    print("="*60)
    print("KAFKA CONSUMER - HAPPINESS PREDICTION & DATABASE STORAGE")
    print("="*60 + "\n")
    
    # Load the trained model
    model = load_model(MODEL_PATH)
    
    # Connect to database
    db_connection = create_db_connection()
    
    # Create Kafka consumer
    consumer = create_consumer()
    
    try:
        # Process messages
        process_messages(consumer, model, db_connection)
    except Exception as e:
        print(f"\nError: {e}")
    finally:
        # Close connections
        consumer.close()
        db_connection.close()
        print("\nConsumer closed.")
        print("="*60)

if __name__ == "__main__":
    main()