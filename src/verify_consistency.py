"""
Verify that the train/test split in MySQL matches the original split from training.
This is CRITICAL for accurate model evaluation.
"""
import pandas as pd
import mysql.connector
from config import DB_CONFIG

def verify_split_consistency():
    """
    Compare the train/test split in MySQL vs the original split file.
    """
    print("="*70)
    print("TRAIN/TEST SPLIT CONSISTENCY VERIFICATION")
    print("="*70)
    
    # ============================================
    # 1. Load original split from training
    # ============================================
    print("\n1. Loading original split from train_model.py...")
    try:
        df_original = pd.read_csv('data/processed/complete_data_with_split.csv')
        print(f"✓ Loaded {len(df_original)} records from complete_data_with_split.csv")
        
        # Convert to string for comparison
        df_original['Year'] = df_original['Year'].astype(str)
        df_original['Country'] = df_original['Country'].astype(str)
        
        # Count train/test in original
        train_original = (df_original['data_split'] == 'train').sum()
        test_original = (df_original['data_split'] == 'test').sum()
        
        print(f"\n  Original split:")
        print(f"    Train: {train_original} records")
        print(f"    Test:  {test_original} records")
        
    except FileNotFoundError:
        print("❌ ERROR: complete_data_with_split.csv not found!")
        print("   Run train_model.py first to generate this file.")
        return False
    
    # ============================================
    # 2. Load split from MySQL
    # ============================================
    print("\n2. Loading split from MySQL database...")
    try:
        connection = mysql.connector.connect(**DB_CONFIG)
        df_mysql = pd.read_sql("SELECT country, year, data_split FROM predictions", connection)
        connection.close()
        
        print(f"✓ Loaded {len(df_mysql)} records from MySQL")
        
        # Convert to string for comparison
        df_mysql['year'] = df_mysql['year'].astype(str)
        df_mysql['country'] = df_mysql['country'].astype(str)
        
        # Rename columns to match
        df_mysql = df_mysql.rename(columns={'country': 'Country', 'year': 'Year'})
        
        # Count train/test in MySQL
        train_mysql = (df_mysql['data_split'] == 'train').sum()
        test_mysql = (df_mysql['data_split'] == 'test').sum()
        
        print(f"\n  MySQL split:")
        print(f"    Train: {train_mysql} records")
        print(f"    Test:  {test_mysql} records")
        
    except mysql.connector.Error as e:
        print(f"❌ ERROR connecting to MySQL: {e}")
        return False
    
    # ============================================
    # 3. Compare counts
    # ============================================
    print("\n" + "="*70)
    print("3. COMPARING COUNTS")
    print("="*70)
    
    count_match = True
    
    if len(df_original) != len(df_mysql):
        print(f"❌ MISMATCH: Total records differ!")
        print(f"   Original: {len(df_original)}")
        print(f"   MySQL:    {len(df_mysql)}")
        count_match = False
    else:
        print(f"✓ Total records match: {len(df_original)}")
    
    if train_original != train_mysql:
        print(f"❌ MISMATCH: Train records differ!")
        print(f"   Original: {train_original}")
        print(f"   MySQL:    {train_mysql}")
        count_match = False
    else:
        print(f"✓ Train records match: {train_original}")
    
    if test_original != test_mysql:
        print(f"❌ MISMATCH: Test records differ!")
        print(f"   Original: {test_original}")
        print(f"   MySQL:    {test_mysql}")
        count_match = False
    else:
        print(f"✓ Test records match: {test_original}")
    
    # ============================================
    # 4. Compare record-by-record
    # ============================================
    print("\n" + "="*70)
    print("4. COMPARING RECORD-BY-RECORD")
    print("="*70)
    
    # Merge to compare
    merged = df_original.merge(
        df_mysql,
        on=['Country', 'Year'],
        how='outer',
        suffixes=('_original', '_mysql'),
        indicator=True
    )
    
    # Check for records only in original
    only_original = merged[merged['_merge'] == 'left_only']
    if len(only_original) > 0:
        print(f"\n⚠️  WARNING: {len(only_original)} records ONLY in original file:")
        print(only_original[['Country', 'Year', 'data_split_original']].head(10))
    else:
        print("✓ No records found only in original file")
    
    # Check for records only in MySQL
    only_mysql = merged[merged['_merge'] == 'right_only']
    if len(only_mysql) > 0:
        print(f"\n⚠️  WARNING: {len(only_mysql)} records ONLY in MySQL:")
        print(only_mysql[['Country', 'Year', 'data_split_mysql']].head(10))
    else:
        print("✓ No records found only in MySQL")
    
    # Check for records in both with different splits
    both = merged[merged['_merge'] == 'both']
    mismatches = both[both['data_split_original'] != both['data_split_mysql']]
    
    if len(mismatches) > 0:
        print(f"\n❌ CRITICAL ERROR: {len(mismatches)} records have DIFFERENT splits!")
        print("\nExamples of mismatches:")
        print(mismatches[['Country', 'Year', 'data_split_original', 'data_split_mysql']].head(10))
        
        print("\nThis means the model was trained on different data than what's in MySQL!")
        print("Your Power BI metrics will be INCORRECT.")
        
    else:
        print(f"\n✓ All {len(both)} matched records have IDENTICAL splits!")
    
    # ============================================
    # 5. FINAL VERDICT
    # ============================================
    print("\n" + "="*70)
    print("FINAL VERDICT")
    print("="*70)
    
    if count_match and len(only_original) == 0 and len(only_mysql) == 0 and len(mismatches) == 0:
        print("\n✅ SUCCESS! The splits are 100% CONSISTENT!")
        print("\n   Your Power BI analysis will be ACCURATE.")
        print("   The train/test split in MySQL exactly matches the training split.")
        return True
    else:
        print("\n❌ FAILURE! The splits are NOT CONSISTENT!")
        print("\n   ⚠️  Your Power BI analysis may be INCORRECT.")
        print("\n   Recommended actions:")
        print("   1. Delete all records from MySQL: TRUNCATE TABLE predictions;")
        print("   2. Re-run train_model.py to regenerate split file")
        print("   3. Re-run kafka_consumer.py and kafka_producer.py")
        return False

if __name__ == "__main__":
    verify_split_consistency()