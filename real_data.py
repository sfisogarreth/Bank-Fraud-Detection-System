import os
import pandas as pd
import time
import random

try:
    import kagglehub
except ImportError:
    print("❌ Missing kagglehub. Please run: pip install kagglehub pandas")
    exit()

from database.connection import get_db_connection

def import_csv_to_db():
    print("📥 Connecting to Kaggle...")
    print("Downloading the PaySim synthetic financial fraud dataset...")
    
    # Download dataset from Kaggle directly
    dataset_path = kagglehub.dataset_download("ealaxi/paysim1")
    print(f"✅ Download complete! Files saved in: {dataset_path}")

    # Find the CSV file inside the downloaded folder
    csv_path = None
    for file in os.listdir(dataset_path):
        if file.endswith(".csv"):
            csv_path = os.path.join(dataset_path, file)
            break
            
    if not csv_path:
        print("❌ Error: Could not find a CSV file in the Kaggle download.")
        return

    print(f"📊 Loading data from {csv_path}...")
    
    # Load the Kaggle dataset
    df = pd.read_csv(csv_path)
    
    # Take a sample of 500 rows to make the dashboard look busy without lagging your PC
    df = df.sample(n=500, random_state=42) 

    conn = get_db_connection()
    cursor = conn.cursor()

    print("Injecting real transactions into database...")
    success_count = 0
    locations = ["Johannesburg, ZA", "Durban, ZA", "Cape Town, ZA", "Pretoria, ZA", "Lagos, NG (Proxy)"]

    for index, row in df.iterrows():
        transaction_id = f"TXN{int(time.time() * 1000)}{index}"
        
        # Maps the Kaggle PaySim dataset columns to your database
        account = str(row.get('nameOrig', f"ACC-{index}"))
        amount = float(row.get('amount', random.uniform(100, 15000)))
        tx_type = str(row.get('type', random.choice(["TRANSFER", "CASH_OUT", "PAYMENT"])))
        is_fraud = int(row.get('isFraud', 0))
        
        # Generate realistic risk scores based on the Kaggle data
        if is_fraud == 1:
            risk_score = random.randint(85, 99)
            status = 'Confirmed_Fraud'
        else:
            risk_score = random.randint(5, 60)
            status = 'Safe' if risk_score < 40 else 'Flagged'
            
        location = random.choice(locations)
        
        try:
            cursor.execute("""
                INSERT INTO transactions 
                (transaction_id, account_number, amount, location, risk_score, status, is_fraud, type)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (transaction_id, account, amount, location, risk_score, status, is_fraud, tx_type))
            success_count += 1
        except Exception as e:
            # Skip rows if there are database constraints
            pass 

    conn.commit()
    cursor.close()
    conn.close()
    print(f"✅ Successfully loaded {success_count} real transactions into the system!")
    print("Refresh your web dashboard to see the live charts reflect the new data!")

if __name__ == "__main__":
    import_csv_to_db()