"""
Kafka Producer: Performs complete ETL pipeline and streams all records.
Reads 5 CSV files, standardizes columns, imputes missing values,
and streams ALL records (train + test) to Kafka.
"""
import os
import json
import time
import pandas as pd
import numpy as np
from kafka import KafkaProducer
from kafka.errors import KafkaError
import miceforest as mf
from config import KAFKA_CONFIG, FEATURE_COLUMNS, TARGET_COLUMN, COLUMN_MAPPING, DATA_PATH

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
            acks='all',
            retries=3
        )
        print(f"✓ Kafka Producer connected to {KAFKA_CONFIG['bootstrap_servers']}")
        return producer
    except KafkaError as e:
        print(f"Error creating Kafka Producer: {e}")
        raise

def load_and_combine_data(data_path):
    """
    Load all CSV files from the data directory and combine them.
    Standardizes column names across different year formats.
    
    Args:
        data_path: Path to the directory containing CSV files
    
    Returns:
        Combined DataFrame with all data and standardized column names
    """
    print("\n" + "="*60)
    print("STEP 1: LOADING AND COMBINING CSV FILES")
    print("="*60)
    
    # Get all CSV files in the directory
    csv_files = [f for f in os.listdir(data_path) if f.endswith('.csv')]
    
    if not csv_files:
        raise ValueError(f"No CSV files found in {data_path}")
    
    # Load and combine all CSV files
    dataframes = []
    for file in csv_files:
        file_path = os.path.join(data_path, file)
        df = pd.read_csv(file_path)
        
        print(f"\n  Loading {file}...")
        print(f"    Original columns: {len(df.columns)} columns")
        
        # Rename columns using the mapping
        df = df.rename(columns=COLUMN_MAPPING)
        
        # Extract year from filename
        year = file.replace('.csv', '')
        df['Year'] = year
        
        # Add Region column if it doesn't exist (for 2018-2019)
        if 'Region' not in df.columns:
            df['Region'] = 'Unknown'
            print(f"    Added 'Region' column (missing in this year)")
        
        dataframes.append(df)
        print(f"    Rows: {len(df)}")
    
    # Combine all dataframes
    combined_df = pd.concat(dataframes, ignore_index=True)
    print(f"\n{'='*60}")
    print(f"✓ Total combined data: {len(combined_df)} rows")
    print(f"{'='*60}")
    
    return combined_df

def preprocess_data(df):
    """
    Preprocess the data: handle missing values using MICE with PMM imputation.
    
    Args:
        df: Input DataFrame
    
    Returns:
        Preprocessed DataFrame with imputed values
    """
    print("\n" + "="*60)
    print("STEP 2: PREPROCESSING DATA (MICE IMPUTATION)")
    print("="*60)
    
    # Check for missing values before imputation
    print(f"\nMissing values BEFORE imputation:")
    missing_before = df[FEATURE_COLUMNS + [TARGET_COLUMN]].isnull().sum()
    print(missing_before)
    total_missing = missing_before.sum()
    print(f"\nTotal missing values: {total_missing}")
    
    if total_missing == 0:
        print("✓ No missing values detected. Skipping imputation.")
        return df
    
    # Prepare data for imputation
    columns_to_impute = FEATURE_COLUMNS + [TARGET_COLUMN]
    df_impute = df[columns_to_impute].copy()
    
    print(f"\nPerforming MICE imputation with PMM method...")
    print(f"This may take a few moments...")
    
    try:
        # Create MICE kernel for imputation
        kernel = mf.ImputationKernel(
            df_impute,
            save_all_iterations_data=True,
            random_state=42
        )
        
        # Run the MICE algorithm
        kernel.mice(iterations=5, verbose=True, variable_schema='pmm')
        
        # Get the completed dataset
        df_imputed = kernel.complete_data(0)
        
        print("\n✓ Imputation completed successfully!")
        
        # Replace the imputed columns in the original dataframe
        for col in columns_to_impute:
            df[col] = df_imputed[col].values
        
        print(f"\n✓ Final dataset size: {len(df)} rows")
        
    except Exception as e:
        print(f"\n⚠️ Error during MICE imputation: {e}")
        print("Falling back to simple mean imputation...")
        
        # Fallback: Simple mean imputation
        for col in columns_to_impute:
            if df[col].isnull().any():
                mean_val = df[col].mean()
                df[col] = df[col].fillna(mean_val)
                print(f"  Imputed {col} with mean: {mean_val:.4f}")
    
    return df

def add_train_test_split_column(df):
    """
    Load the complete data with split info and merge with current df.
    If file doesn't exist, mark all as 'unknown'.
    
    Args:
        df: Preprocessed DataFrame
    
    Returns:
        DataFrame with data_split column
    """
    print("\n" + "="*60)
    print("STEP 3: ADDING TRAIN/TEST SPLIT INFORMATION")
    print("="*60)
    
    split_file = 'data/processed/complete_data_with_split.csv'
    
    if os.path.exists(split_file):
        print(f"✓ Found split information file: {split_file}")
        df_split = pd.read_csv(split_file)
        
        # Convert Year to string in both DataFrames to ensure compatibility
        df['Year'] = df['Year'].astype(str)
        df_split['Year'] = df_split['Year'].astype(str)
        
        # Also ensure Country is string (just in case)
        df['Country'] = df['Country'].astype(str)
        df_split['Country'] = df_split['Country'].astype(str)
        
        # Merge based on Country and Year to get data_split column
        df = df.merge(
            df_split[['Country', 'Year', 'data_split']], 
            on=['Country', 'Year'], 
            how='left'
        )
        
        # Fill NaN with 'unknown' (in case some records don't match)
        df['data_split'] = df['data_split'].fillna('unknown')
        
        train_count = (df['data_split'] == 'train').sum()
        test_count = (df['data_split'] == 'test').sum()
        unknown_count = (df['data_split'] == 'unknown').sum()
        
        print(f"\n✓ Split information added:")
        print(f"   - Train records: {train_count}")
        print(f"   - Test records: {test_count}")
        print(f"   - Unknown records: {unknown_count}")
        
    else:
        print(f"⚠️ Split information file not found: {split_file}")
        print("   Marking all records as 'unknown'")
        print("   Run train_model.py first to generate split information!")
        df['data_split'] = 'unknown'
    
    return df

def send_records(producer, df, topic):
    """
    Send ALL records to Kafka topic one by one.
    
    Args:
        producer: KafkaProducer instance
        df: DataFrame with ALL data (train + test)
        topic: Kafka topic name
    """
    print("\n" + "="*60)
    print(f"STEP 4: STREAMING RECORDS TO KAFKA TOPIC '{topic}'")
    print("="*60)
    
    total_records = len(df)
    train_count = 0
    test_count = 0
    unknown_count = 0
    
    for idx, row in df.iterrows():
        # Count by split type
        if row['data_split'] == 'train':
            train_count += 1
        elif row['data_split'] == 'test':
            test_count += 1
        else:
            unknown_count += 1
        
        # Prepare the message
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
            'actual_happiness_score': float(row[TARGET_COLUMN]),
            'data_split': row['data_split']  # NEW: Include train/test info
        }
        
        try:
            # Send message
            future = producer.send(topic, value=message)
            record_metadata = future.get(timeout=10)
            
            # Print progress every 50 records
            if (idx + 1) % 50 == 0 or (idx + 1) == total_records:
                print(f"[{idx+1}/{total_records}] Sent: {message['country']} ({message['year']}) "
                      f"[{message['data_split'].upper()}] - Partition: {record_metadata.partition}")
            
            
        except KafkaError as e:
            print(f"Error sending message {idx+1}: {e}")
    
    # Ensure all messages are sent
    producer.flush()
    
    print(f"\n{'='*60}")
    print(f"✓ ALL RECORDS SENT SUCCESSFULLY!")
    print(f"{'='*60}")
    print(f"Total records: {total_records}")
    print(f"  - Train records: {train_count}")
    print(f"  - Test records: {test_count}")
    print(f"  - Unknown records: {unknown_count}")
    print(f"{'='*60}")

def main():
    """
    Main function to run the complete ETL pipeline and stream data.
    """
    print("="*60)
    print("KAFKA PRODUCER - COMPLETE ETL + DATA STREAMING")
    print("="*60)
    
    try:
        # Step 1: Load and combine CSVs
        df = load_and_combine_data(DATA_PATH)
        
        # Step 2: Preprocess data (MICE imputation)
        df_clean = preprocess_data(df)
        
        # Step 3: Add train/test split information
        df_clean = add_train_test_split_column(df_clean)
        
        # Step 4: Create Kafka producer
        producer = create_producer()
        
        # Step 5: Send ALL records to Kafka
        send_records(
            producer=producer,
            df=df_clean,
            topic=KAFKA_CONFIG['topic']
        )
        
    except KeyboardInterrupt:
        print("\n\n⚠️ Producer interrupted by user")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        if 'producer' in locals():
            producer.close()
            print("\n✓ Producer closed.")
        print("="*60)

if __name__ == "__main__":
    main()