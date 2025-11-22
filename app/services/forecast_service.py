import numpy as np
import joblib
import os
from datetime import datetime


class ForecastService:
    def __init__(self):
        self.model_dir = os.path.join(os.path.dirname(__file__), "..", "ml_models")
        self.model = None
        self.x_scaler = None
        self.y_scaler = None
        self._load_models()

    def _load_models(self):
        """Load SVR model and scalers"""
        try:
            model_path = os.path.join(self.model_dir, "svr_model.pkl")
            x_scaler_path = os.path.join(self.model_dir, "x_scaler.pkl")
            y_scaler_path = os.path.join(self.model_dir, "y_scaler.pkl")

            if os.path.exists(model_path):
                self.model = joblib.load(model_path)
            if os.path.exists(x_scaler_path):
                self.x_scaler = joblib.load(x_scaler_path)
            if os.path.exists(y_scaler_path):
                self.y_scaler = joblib.load(y_scaler_path)
        except Exception as e:
            print(f"Warning: Could not load ML models: {e}")

    def _preprocess_input(self, warehouse_id, sku_id, historical_demand):
        """Prepare features for the model"""
        sales_avg = np.mean(historical_demand) if historical_demand else 0
        today = datetime.now()
        features = np.array(
            [[warehouse_id, sku_id, sales_avg, today.year, today.month]]
        )
        return features

    def predict_demand(self, warehouse_id, sku_id, historical_demand):
        """Predict demand for tomorrow"""
        if self.model is None:
            # Fallback to simple average if model not available
            return np.mean(historical_demand) if historical_demand else 10

        try:
            features = self._preprocess_input(warehouse_id, sku_id, historical_demand)

            if self.x_scaler:
                features = self.x_scaler.transform(features)

            prediction = self.model.predict(features)[0]

            if self.y_scaler:
                prediction = self.y_scaler.inverse_transform([[prediction]])[0][0]

            return max(0, prediction)  # Ensure non-negative

        except Exception as e:
            print(f"Prediction error: {e}")
            return np.mean(historical_demand) if historical_demand else 10

    def predict_7_day_demand(self, warehouse_id, sku_id, historical_demand):
        """Predict total demand for next 7 days"""
        daily_forecast = self.predict_demand(warehouse_id, sku_id, historical_demand)

        # Apply slight variation for 7-day forecast
        # In production, you'd run the model for each day
        weekly_multiplier = 7.0
        trend_factor = 1.05  # Slight upward trend assumption

        return daily_forecast * weekly_multiplier * trend_factor
