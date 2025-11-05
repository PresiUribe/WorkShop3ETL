"""
Script to train the Happiness Score prediction model.
Loads multiple CSV files, combines them, trains a regression model, and saves it.
Uses MICE with PMM for imputation of missing values.
"""
import os
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
import joblib
import miceforest as mf
from config import FEATURE_COLUMNS, TARGET_COLUMN, MODEL_PATH, DATA_PATH

def load_and_combine_data(data_path):
    """
    Load all CSV files from the data directory and combine them.
    Standardizes column names across different year formats.
    
    Args:
        data_path: Path to the directory containing CSV files
    
    Returns:
        Combined DataFrame with all data and standardized column names
    """
    from config import COLUMN_MAPPING
    
    print("Loading CSV files...")
    
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
        
        # Extract year from filename (assuming format like 2015.csv, 2016.csv, etc.)
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
    print(f"Total combined data: {len(combined_df)} rows")
    print(f"Standardized columns: {combined_df.columns.tolist()}")
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
    print("\nPreprocessing data...")
    
    # Check for missing values before imputation
    print(f"\nMissing values BEFORE imputation:")
    missing_before = df[FEATURE_COLUMNS + [TARGET_COLUMN]].isnull().sum()
    print(missing_before)
    total_missing = missing_before.sum()
    print(f"\nTotal missing values: {total_missing}")
    
    if total_missing == 0:
        print("No missing values detected. Skipping imputation.")
        return df
    
    # Prepare data for imputation (only numeric columns)
    columns_to_impute = FEATURE_COLUMNS + [TARGET_COLUMN]
    
    # Create a copy of the dataframe for imputation
    df_impute = df[columns_to_impute].copy()
    
    print(f"\nPerforming MICE imputation with PMM method...")
    print(f"This may take a few moments...")
    
    try:
        # Create MICE kernel for imputation
        # Using PMM (Predictive Mean Matching) which is ideal for continuous variables
        kernel = mf.ImputationKernel(
            df_impute,
            save_all_iterations_data=True,
            random_state=42
        )
        
        # Run the MICE algorithm
        # iterations: number of iterations to run
        # variable_schema: use 'pmm' for all variables
        kernel.mice(iterations=5, verbose=True, variable_schema='pmm')
        
        # Get the completed dataset (using the first imputed dataset)
        df_imputed = kernel.complete_data(0)
        
        print("\n✓ Imputation completed successfully!")
        
        # Check for missing values after imputation
        print(f"\nMissing values AFTER imputation:")
        missing_after = df_imputed.isnull().sum()
        print(missing_after)
        
        # Replace the imputed columns in the original dataframe
        for col in columns_to_impute:
            df[col] = df_imputed[col].values
        
        # Verify no missing values remain
        remaining_missing = df[columns_to_impute].isnull().sum().sum()
        if remaining_missing > 0:
            print(f"\n⚠️ Warning: {remaining_missing} missing values still remain after imputation")
            print("Dropping remaining rows with missing values...")
            df = df.dropna(subset=columns_to_impute)
        
        print(f"\nFinal dataset size: {len(df)} rows")
        
    except Exception as e:
        print(f"\n⚠️ Error during MICE imputation: {e}")
        print("Falling back to simple mean imputation...")
        
        # Fallback: Simple mean imputation (fix pandas warning)
        for col in columns_to_impute:
            if df[col].isnull().any():
                mean_val = df[col].mean()
                df[col] = df[col].fillna(mean_val)
                print(f"  Imputed {col} with mean: {mean_val:.4f}")
    
    return df

def train_model(X_train, y_train):
    """
    Train the regression model.
    
    Args:
        X_train: Training features
        y_train: Training target
    
    Returns:
        Trained model
    """
    print("\nTraining model...")
    
    # Initialize model (you can try RandomForestRegressor for better performance)
    model = LinearRegression()
    # model = RandomForestRegressor(n_estimators=100, random_state=42)
    
    # Train the model
    model.fit(X_train, y_train)
    
    print("Model training completed!")
    
    return model

def evaluate_model(model, X_test, y_test):
    """
    Evaluate the model and print metrics.
    
    Args:
        model: Trained model
        X_test: Test features
        y_test: Test target
    """
    print("\n" + "="*50)
    print("MODEL EVALUATION")
    print("="*50)
    
    # Make predictions
    y_pred = model.predict(X_test)
    
    # Calculate metrics
    r2 = r2_score(y_test, y_pred)
    mae = mean_absolute_error(y_test, y_pred)
    rmse = np.sqrt(mean_squared_error(y_test, y_pred))
    
    print(f"\nR² Score: {r2:.4f}")
    print(f"Mean Absolute Error (MAE): {mae:.4f}")
    print(f"Root Mean Squared Error (RMSE): {rmse:.4f}")
    print("="*50)
    
    return {
        'r2': r2,
        'mae': mae,
        'rmse': rmse
    }

def save_model(model, model_path):
    """
    Save the trained model to a file.
    
    Args:
        model: Trained model
        model_path: Path to save the model
    """
    # Create models directory if it doesn't exist
    os.makedirs(os.path.dirname(model_path), exist_ok=True)
    
    # Save the model
    joblib.dump(model, model_path)
    print(f"\nModel saved to: {model_path}")

def main():
    """
    Main function to orchestrate the training pipeline.
    """
    print("="*50)
    print("HAPPINESS SCORE PREDICTION - MODEL TRAINING")
    print("="*50)
    
    # Load and combine data
    df = load_and_combine_data(DATA_PATH)
    
    # Preprocess data
    df_clean = preprocess_data(df)
    
    # Prepare features and target
    X = df_clean[FEATURE_COLUMNS]
    y = df_clean[TARGET_COLUMN]
    
    print(f"\nFeatures shape: {X.shape}")
    print(f"Target shape: {y.shape}")
    
    # Split data into train and test sets (70-30 split)
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.3, random_state=42
    )
    
    print(f"\nTraining set size: {len(X_train)} ({len(X_train)/len(X)*100:.1f}%)")
    print(f"Test set size: {len(X_test)} ({len(X_test)/len(X)*100:.1f}%)")
    
    # Train the model
    model = train_model(X_train, y_train)
    
    # Evaluate the model
    metrics = evaluate_model(model, X_test, y_test)
    
    # Save the model
    save_model(model, MODEL_PATH)
    
    # Save test data for later use in Kafka streaming
    test_data = df_clean.iloc[X_test.index].copy()
    test_data_path = 'data/processed/test_data.csv'
    os.makedirs(os.path.dirname(test_data_path), exist_ok=True)
    test_data.to_csv(test_data_path, index=False)
    print(f"Test data saved to: {test_data_path}")
    
    print("\n" + "="*50)
    print("TRAINING COMPLETED SUCCESSFULLY!")
    print("="*50)

if __name__ == "__main__":
    main()