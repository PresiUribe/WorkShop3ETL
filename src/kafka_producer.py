"""
Kafka Producer: Reads transformed data and streams it record by record.
"""
import json
import time
import pandas as pd
from kafka import KafkaProducer
from kafka.errors import KafkaError
from config import KAFKA_CONFIG, FEATURE_COLUMNS, TARGET_COLUMN

def create_producer():
    """
    Create and return a Kafka producer instance.
    
    Returns:
        KafkaProducer instance
    """
    try:
        producer = KafkaProducer(
            bootstrap_servers=KAFKA_CONFIG['bootstrap_servers'],
            value_serializer=lambda v: json.dumps(v).encode('utf-8'),
            acks='all',  # Wait for all replicas to acknowledge
            retries=3
        )
        print(f"Kafka Producer connected to {KAFKA_CONFIG['bootstrap_servers']}")
        return producer
    except KafkaError as e:
        print(f"Error creating Kafka Producer: {e}")
        raise

def load_data(file_path):
    """
    Load the test data to be streamed.
    
    Args:
        file_path: Path to the CSV file
    
    Returns:
        DataFrame with the data
    """
    print(f"\nLoading data from {file_path}...")
    df = pd.read_csv(file_path)
    print(f"Loaded {len(df)} records")
    return df

def send_records(producer, df, topic):
    """
    Send records to Kafka topic one by one.
    
    Args:
        producer: KafkaProducer instance
        df: DataFrame with data to send
        topic: Kafka topic name
        delay: Delay between messages in seconds
    """
    print(f"\nStarting to send records to topic '{topic}'...")
    
    
    total_records = len(df)
    
    for idx, row in df.iterrows():
        # Prepare the message with standardized column names
        message = {
            'country': row.get('Country', 'Unknown'),
            'region': row.get('Region', 'Unknown'),
            'year': row.get('Year', 'Unknown'),
            'features': {
                'gdp': float(row[FEATURE_COLUMNS[0]]),
                'family': float(row[FEATURE_COLUMNS[1]]),
                'health': float(row[FEATURE_COLUMNS[2]]),
                'freedom': float(row[FEATURE_COLUMNS[3]]),
                'trust': float(row[FEATURE_COLUMNS[4]]),
                'generosity': float(row[FEATURE_COLUMNS[5]])
            },
            'actual_happiness_score': float(row[TARGET_COLUMN])
        }
        
        try:
            # Send message
            future = producer.send(topic, value=message)
            
            # Wait for the message to be sent
            record_metadata = future.get(timeout=10)
            
            print(f"[{idx+1}/{total_records}] Sent: {message['country']} ({message['year']}) "
                  f"- Partition: {record_metadata.partition}, Offset: {record_metadata.offset}")
            
           
        except KafkaError as e:
            print(f"Error sending message: {e}")
    
    # Ensure all messages are sent
    producer.flush()
    print(f"\n✓ All {total_records} records sent successfully!")

def main():
    """
    Main function to run the Kafka Producer.
    """
    print("="*60)
    print("KAFKA PRODUCER - HAPPINESS DATA STREAMING")
    print("="*60)
    
    # Load test data
    data_file = 'data/processed/test_data.csv'
    df = load_data(data_file)
    
    # Create Kafka producer
    producer = create_producer()
    
    try:
        # Send records to Kafka
        send_records(
            producer=producer,
            df=df,
            topic=KAFKA_CONFIG['topic']
           
        )
    except KeyboardInterrupt:
        print("\n\nProducer interrupted by user")
    except Exception as e:
        print(f"\nError: {e}")
    finally:
        # Close the producer
        producer.close()
        print("\nProducer closed.")
        print("="*60)

if __name__ == "__main__":
    main()