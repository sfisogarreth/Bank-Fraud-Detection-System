import pandas as pd
import os
import joblib
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression

# Define paths
current_dir = os.path.dirname(__file__)
data_path = os.path.join(current_dir, "AIML_Dataset.csv")
model_path = os.path.join(current_dir, "fraud_model.pkl")

def train_and_save():
    if not os.path.exists(data_path):
        print(f"Error: Dataset not found at {data_path}")
        return

    # Load data
    df = pd.read_csv(data_path)
    print("Dataset loaded successfully!")

    # ASSUMPTION: 'is_fraud' is your target column. Update to match your actual CSV.
    X = df.drop(columns=['is_fraud']) 
    y = df['is_fraud']

    # Split, train, and evaluate
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    model = LogisticRegression(max_iter=1000)
    model.fit(X_train, y_train)
    
    accuracy = model.score(X_test, y_test)
    print(f"Model trained! Accuracy: {accuracy * 100:.2f}%")

    # Save the compiled model for Flask to use
    joblib.dump(model, model_path)
    print(f"Model saved to {model_path}")

if __name__ == "__main__":
    train_and_save()