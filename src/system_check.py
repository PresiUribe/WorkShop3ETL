"""
System check script to verify all requirements are met.
Run this before starting the project.
"""
import sys
import os

def check_python_version():
    """Check Python version."""
    print("Checking Python version...")
    version = sys.version_info
    if version.major >= 3 and version.minor >= 7:
        print(f"  ✓ Python {version.major}.{version.minor}.{version.micro}")
        return True
    else:
        print(f"  ✗ Python version too old: {version.major}.{version.minor}")
        print("    Please install Python 3.7 or higher")
        return False

def check_packages():
    """Check if required packages are installed."""
    print("\nChecking required packages...")
    required_packages = [
        'pandas', 'numpy', 'sklearn', 'kafka', 
        'mysql.connector', 'dotenv', 'joblib'
    ]
    
    all_installed = True
    for package in required_packages:
        try:
            __import__(package)
            print(f"  ✓ {package}")
        except ImportError:
            print(f"  ✗ {package} not installed")
            all_installed = False
    
    if not all_installed:
        print("\n  Run: pip install -r requirements.txt")
    
    return all_installed

def check_env_file():
    """Check if .env file exists."""
    print("\nChecking .env file...")
    if os.path.exists('.env'):
        print("  ✓ .env file found")
        return True
    else:
        print("  ✗ .env file not found")
        print("    Create .env file from .env.example")
        return False

def check_data_files():
    """Check if CSV data files exist."""
    print("\nChecking data files...")
    data_path = 'data/raw'
    
    if not os.path.exists(data_path):
        print(f"  ✗ Directory {data_path} not found")
        return False
    
    csv_files = [f for f in os.listdir(data_path) if f.endswith('.csv')]
    
    if len(csv_files) >= 1:
        print(f"  ✓ Found {len(csv_files)} CSV file(s)")
        for file in csv_files:
            print(f"    - {file}")
        return True
    else:
        print(f"  ✗ No CSV files found in {data_path}")
        print("    Place your CSV files in data/raw/ directory")
        return False

def check_kafka():
    """Check if Kafka is accessible."""
    print("\nChecking Kafka connection...")
    try:
        from kafka import KafkaProducer
        producer = KafkaProducer(
            bootstrap_servers='localhost:9092',
            request_timeout_ms=5000
        )
        producer.close()
        print("  ✓ Kafka is running on localhost:9092")
        return True
    except Exception as e:
        print(f"  ✗ Cannot connect to Kafka: {e}")
        print("    Make sure Kafka and Zookeeper are running")
        return False

def check_mysql():
    """Check if MySQL is accessible."""
    print("\nChecking MySQL connection...")
    try:
        import mysql.connector
        from dotenv import load_dotenv
        
        load_dotenv()
        
        connection = mysql.connector.connect(
            host=os.getenv('DB_HOST', 'localhost'),
            user=os.getenv('DB_USER', 'root'),
            password=os.getenv('DB_PASSWORD', ''),
            connection_timeout=5
        )
        connection.close()
        print("  ✓ MySQL is accessible")
        return True
    except Exception as e:
        print(f"  ✗ Cannot connect to MySQL: {e}")
        print("    Check your MySQL credentials in .env file")
        return False

def main():
    """Run all system checks."""
    print("="*60)
    print("SYSTEM CHECK - HAPPINESS PREDICTION PROJECT")
    print("="*60 + "\n")
    
    checks = [
        ("Python Version", check_python_version),
        ("Python Packages", check_packages),
        ("Environment File", check_env_file),
        ("Data Files", check_data_files),
        ("Kafka", check_kafka),
        ("MySQL", check_mysql)
    ]
    
    results = []
    for name, check_func in checks:
        try:
            result = check_func()
            results.append((name, result))
        except Exception as e:
            print(f"  ✗ Error during {name} check: {e}")
            results.append((name, False))
    
    # Summary
    print("\n" + "="*60)
    print("SUMMARY")
    print("="*60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status:8} | {name}")
    
    print("-"*60)
    print(f"Total: {passed}/{total} checks passed")
    
    if passed == total:
        print("\n🎉 All checks passed! You're ready to start.")
    else:
        print("\n⚠️  Some checks failed. Please fix the issues above.")
    
    print("="*60)

if __name__ == "__main__":
    main()
