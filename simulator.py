import requests
import random
import time

API_URL = "http://127.0.0.1:5000/api/v1/transactions"

locations = [
    "Johannesburg, ZA", 
    "Durban, ZA", 
    "Cape Town, ZA", 
    "Pretoria, ZA", 
    "Lagos, NG (Proxy)"
]

print("🚀 Starting MAZI Live Traffic Simulator...")
print("Leave this running in the background to watch your dashboard update live!\n")

while True:
    payload = {
        "account_number": f"ACC-{random.randint(1000, 9999)}",
        "amount": round(random.uniform(50.0, 25000.0), 2),
        "location": random.choice(locations),
        "type": random.choice(["PAYMENT", "TRANSFER", "CASH_OUT"]),
        "oldbalanceOrg": round(random.uniform(1000.0, 50000.0), 2),
        "newbalanceOrig": 0 
    }

    try:
        response = requests.post(API_URL, json=payload)
        
        if response.status_code == 201:
            data = response.json()
            score = data.get("risk_score", 0)
            
            if score > 75:
                print(f"🚨 FRAUD FLAGGED: {data['transaction_id']} | Risk: {score}")
            elif score > 40:
                print(f"⚠️ Suspicious:   {data['transaction_id']} | Risk: {score}")
            else:
                print(f"✅ Safe Txn:      {data['transaction_id']} | Risk: {score}")
        else:
            print(f"⚠️ API Error: {response.status_code} - Reason: {response.text}")
            
    except Exception:
        print("Waiting for Flask server to start...")

    time.sleep(random.uniform(3.0, 7.0))