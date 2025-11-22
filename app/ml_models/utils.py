import joblib
import numpy as np
import os
from datetime import datetime


def load_svr_model():
    """Load the pre-trained SVR model"""
    model_path = os.path.join(os.path.dirname(__file__), "svr_model.pkl")
    if os.path.exists(model_path):
        return joblib.load(model_path)
    return None


def load_scalers():
    """Load feature and target scalers"""
    base_path = os.path.dirname(__file__)
    x_scaler_path = os.path.join(base_path, "x_scaler.pkl")
    y_scaler_path = os.path.join(base_path, "y_scaler.pkl")

    x_scaler = joblib.load(x_scaler_path) if os.path.exists(x_scaler_path) else None
    y_scaler = joblib.load(y_scaler_path) if os.path.exists(y_scaler_path) else None

    return x_scaler, y_scaler


def preprocess_input(warehouse_id, sku_id, historical_demand):
    """
    Preprocess input data for the SVR model.
    Features: warehouse_id, sku_id, avg_sales, year, month
    """
    sales_avg = np.mean(historical_demand) if historical_demand else 0
    today = datetime.now()
    features = np.array([[warehouse_id, sku_id, sales_avg, today.year, today.month]])
    return features


def predict_demand(warehouse_id, sku_id, historical_demand):
    """Make a demand prediction"""
    model = load_svr_model()
    if model is None:
        return np.mean(historical_demand) if historical_demand else 10

    x_scaler, y_scaler = load_scalers()
    features = preprocess_input(warehouse_id, sku_id, historical_demand)

    if x_scaler:
        features = x_scaler.transform(features)

    prediction = model.predict(features)[0]

    if y_scaler:
        prediction = y_scaler.inverse_transform([[prediction]])[0][0]

    return max(0, prediction)
