import pandas as pd
import joblib
import os
from sklearn.ensemble import RandomForestClassifier
from datetime import datetime

# Model file path
MODEL_PATH = os.path.join(os.path.dirname(__file__), 'turbine_model.pkl')

def train_and_save_model():
    """Train the model with your CSV data and save it"""
    
    # Your CSV data path - save the CSV file in backend folder
    csv_path = os.path.join(os.path.dirname(__file__), 'turbine_data.csv')
    
    if not os.path.exists(csv_path):
        print(f"CSV file not found at {csv_path}")
        return None
    
    # Load and train
    df = pd.read_csv(csv_path)
    X = df[['month', 'day', 'hour', 'current']]
    y = df['abnormal']
    
    model = RandomForestClassifier(n_estimators=100, random_state=42)
    model.fit(X, y)
    
    # Save model
    joblib.dump(model, MODEL_PATH)
    print(f"Model saved to {MODEL_PATH}")
    return model

def load_model():
    """Load the trained model"""
    if os.path.exists(MODEL_PATH):
        return joblib.load(MODEL_PATH)
    else:
        return train_and_save_model()

def predict_turbine_behavior(month, day, hour, current):
    """Predict if turbine behavior is abnormal"""
    model = load_model()
    if model is None:
        return None, "Model not available"
    
    prediction = model.predict([[month, day, hour, current]])[0]
    probability = model.predict_proba([[month, day, hour, current]])[0]
    
    is_abnormal = bool(prediction == 1)
    confidence = float(max(probability))
    
    return is_abnormal, confidence


def calculate_flood_risk(distance_cm, current_amps):
    """Simplified flood risk based on hand distance (demo mode)
    
    Distance thresholds:
    - < 5 cm: CRITICAL (hand touching sensor)
    - 5-10 cm: HIGH (hand very close)
    - 10-20 cm: MEDIUM (hand close)
    - 20-50 cm: LOW (hand at distance)
    - > 50 cm: NORMAL (hand far)
    """
    
    if distance_cm < 5:  # Hand almost touching sensor
        flood_risk = 98
        risk_level = "CRITICAL"
        message = "🔴 CRITICAL! Water level DANGEROUSLY HIGH! Immediate evacuation required!"
        status = "🔴 DANGER"
    elif distance_cm < 10:  # Hand very close
        flood_risk = 85
        risk_level = "HIGH"
        message = "🟠 HIGH flood risk! Water level very high! Take precautions now!"
        status = "🔴 DANGER"
    elif distance_cm < 20:  # Hand close
        flood_risk = 60
        risk_level = "MEDIUM"
        message = "🟡 MEDIUM flood risk! Water level rising. Stay alert!"
        status = "🟡 CAUTION"
    elif distance_cm < 50:  # Hand at distance
        flood_risk = 30
        risk_level = "LOW"
        message = "🔵 LOW flood risk. Normal monitoring advised."
        status = "🟢 SAFE"
    else:  # Hand far away
        flood_risk = 5
        risk_level = "NORMAL"
        message = "🟢 NORMAL conditions. No flood risk detected."
        status = "🟢 SAFE"
    
    # Calculate water level percentage (inverse of distance)
    water_level_percent = max(0, min(100, (200 - distance_cm) / 200 * 100))
    
    return {
        'risk_percentage': flood_risk,
        'risk_level': risk_level,
        'water_level_percent': round(water_level_percent, 1),
        'distance_cm': distance_cm,
        'message': message,
        'status': status
    }