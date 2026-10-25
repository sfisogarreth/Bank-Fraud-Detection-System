import os
import sys
import json
import joblib
import warnings
import kagglehub
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, confusion_matrix, roc_auc_score

warnings.filterwarnings('ignore')

# Paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODEL_DIR = os.path.join(BASE_DIR, 'models')
MODEL_PATH = os.path.join(MODEL_DIR, 'fraud_model.pkl')
META_PATH = os.path.join(MODEL_DIR, 'model_metadata.json')

os.makedirs(MODEL_DIR, exist_ok=True)


def download_and_load_data():
    print("📥 Downloading dataset from Kaggle...")
    path = kagglehub.dataset_download("jainilcoder/online-payment-fraud-detection")
    
    csv_file = [f for f in os.listdir(path) if f.endswith('.csv')][0]
    full_path = os.path.join(path, csv_file)
    
    print(f"✅ Dataset downloaded to: {full_path}")
    return pd.read_csv(full_path)


def train_and_save():
    # 1. Load Data
    df = download_and_load_data()
    print(f"✅ Dataset loaded: {df.shape[0]:,} rows, {df.shape[1]} columns")
    print(f"   Fraud rate: {df['isFraud'].mean()*100:.2f}%")

    # 2. Preprocessing
    print("⚙️ Preprocessing data...")
    drop_cols = [c for c in ['nameOrig', 'nameDest', 'isFlaggedFraud'] if c in df.columns]
    df = df.drop(columns=drop_cols)
    
    # One-Hot Encoding with drop_first=True (creates reference category)
    df_encoded = pd.get_dummies(df, columns=['type'], drop_first=True)
    
    # Capture EXACT feature names and reference category
    feature_cols = [c for c in df_encoded.columns if c != 'isFraud']
    type_cols = [c for c in feature_cols if c.startswith('type_')]
    reference_category = None
    
    # Find which type was dropped (the one NOT in type_cols)
    all_types = ['CASH_IN', 'CASH_OUT', 'DEBIT', 'PAYMENT', 'TRANSFER']
    present_types = [c.replace('type_', '') for c in type_cols]
    dropped = [t for t in all_types if t not in present_types]
    if dropped:
        reference_category = dropped[0]
    
    print(f"   Features: {len(feature_cols)}")
    print(f"   Type columns: {type_cols}")
    print(f"   Reference (dropped) category: {reference_category}")

    X = df_encoded[feature_cols]
    y = df_encoded['isFraud']

    # 3. Split
    print("✂️ Splitting data...")
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    # 4. Train
    print("🧠 Training Random Forest Classifier...")
    model = RandomForestClassifier(
        n_estimators=100,      # Balanced trees for high performance
        max_depth=15,          # Deep enough to capture complex fraud patterns
        min_samples_split=5,
        class_weight='balanced',
        n_jobs=-1,
        random_state=42
    )
    model.fit(X_train, y_train)

    # 5. Evaluate
    y_pred = model.predict(X_test)
    y_proba = model.predict_proba(X_test)[:, 1]
    
    print("\n📊 --- MODEL EVALUATION ---")
    print(confusion_matrix(y_test, y_pred))
    print("\nClassification Report:")
    print(classification_report(y_test, y_pred, target_names=['Safe', 'Fraud']))
    print(f"ROC-AUC Score: {roc_auc_score(y_test, y_proba):.4f}")

    # Feature importance
    importances = pd.Series(model.feature_importances_, index=feature_cols).sort_values(ascending=False)
    print("\n🔥 Top 5 Important Features:")
    print(importances.head(5))

    # 6. Save model + metadata
    joblib.dump(model, MODEL_PATH)
    
    metadata = {
        'feature_names': feature_cols,
        'type_columns': type_cols,
        'reference_category': reference_category,
        'all_types': all_types,
        'model_version': '1.0.0',
        'training_samples': len(X_train),
        'fraud_rate': float(y.mean()),
        'roc_auc': float(roc_auc_score(y_test, y_proba))
    }
    
    with open(META_PATH, 'w') as f:
        json.dump(metadata, f, indent=2)
    
    print(f"\n💾 Model saved to: {MODEL_PATH}")
    print(f"📋 Metadata saved to: {META_PATH}")
    print("🎉 Training complete!")

if __name__ == "__main__":
    train_and_save()