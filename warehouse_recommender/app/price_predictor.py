import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error, r2_score
import joblib
import os
from scipy import stats

class WarehousePricePredictor:
    def __init__(self):
        self.model = None
        self.scaler = StandardScaler()
        self.feature_columns = ['area_sqft', 'latitude', 'longitude']
        
    def preprocess_data(self, df):
        """Preprocess the data for training"""
        # Create a copy to avoid modifying original
        df = df.copy()
        
        # Convert area to numeric (remove 'sqft' and commas)
        df['area_sqft'] = df['area'].str.replace('sqft', '').str.replace(',', '').astype(float)
        
        # Convert rent to numeric (already done in extraction.py)
        df['rent'] = pd.to_numeric(df['rent'], errors='coerce')
        
        # Print data info before cleaning
        print(f"Total samples before cleaning: {len(df)}")
        
        # Drop rows with missing values
        df = df.dropna(subset=['rent', 'area_sqft', 'latitude', 'longitude'])
        
        # Print data info after cleaning
        print(f"Total samples after cleaning: {len(df)}")
        
        # Print sample statistics
        print("\nData Statistics:")
        print(df[['rent', 'area_sqft', 'latitude', 'longitude']].describe())
        
        return df
    
    def train(self, data_path):
        """Train the model on the data"""
        # Load and preprocess data
        df = pd.read_csv(data_path)
        df = self.preprocess_data(df)
        
        # Prepare features and target
        X = df[self.feature_columns]
        y = df['rent']
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42
        )
        
        # Scale features
        X_train_scaled = self.scaler.fit_transform(X_train)
        X_test_scaled = self.scaler.transform(X_test)
        
        # Train model
        self.model = RandomForestRegressor(
            n_estimators=100,
            max_depth=10,
            random_state=42
        )
        self.model.fit(X_train_scaled, y_train)
        
        # Evaluate model
        y_pred = self.model.predict(X_test_scaled)
        mse = mean_squared_error(y_test, y_pred)
        r2 = r2_score(y_test, y_pred)
        
        print(f"\nModel Performance:")
        print(f"Mean Squared Error: {mse:.2f}")
        print(f"R2 Score: {r2:.2f}")
        
        # Print feature importance
        feature_importance = pd.DataFrame({
            'feature': self.feature_columns,
            'importance': self.model.feature_importances_
        }).sort_values('importance', ascending=False)
        
        print("\nFeature Importance:")
        print(feature_importance)
        
        return self.model
    
    def predict(self, area_sqft, latitude, longitude):
        """Predict price for given features"""
        if self.model is None:
            raise ValueError("Model not trained yet. Call train() first.")
            
        # Create feature array with proper column names
        features = pd.DataFrame({
            'area_sqft': [area_sqft],
            'latitude': [latitude],
            'longitude': [longitude]
        })
        
        # Scale features
        features_scaled = self.scaler.transform(features)
        
        # Make prediction
        prediction = self.model.predict(features_scaled)[0]
        
        return prediction
    
    def get_optimal_price_suggestions(self, area_sqft, latitude, longitude):
        """Get optimal price suggestions with confidence intervals"""
        if self.model is None:
            raise ValueError("Model not trained yet. Call train() first.")
            
        # Create feature array
        features = pd.DataFrame({
            'area_sqft': [area_sqft],
            'latitude': [latitude],
            'longitude': [longitude]
        })
        
        # Scale features
        features_scaled = self.scaler.transform(features)
        
        # Get predictions from all trees
        predictions = []
        for estimator in self.model.estimators_:
            pred = estimator.predict(features_scaled)[0]
            predictions.append(pred)
        
        # Calculate statistics
        mean_price = np.mean(predictions)
        std_price = np.std(predictions)
        
        # Calculate confidence intervals
        confidence = 0.95
        ci = stats.t.interval(confidence, len(predictions)-1, loc=mean_price, scale=std_price)
        
        # Calculate price ranges
        low_price = max(0, ci[0])  # Ensure price is not negative
        high_price = ci[1]
        
        # Calculate price per sqft
        price_per_sqft = mean_price / area_sqft
        
        return {
            'optimal_price': mean_price,
            'price_range': {
                'low': low_price,
                'high': high_price
            },
            'price_per_sqft': price_per_sqft,
            'confidence': confidence * 100
        }
    
    def save_model(self, model_path):
        """Save the trained model"""
        if self.model is None:
            raise ValueError("No model to save. Train the model first.")
            
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(model_path), exist_ok=True)
        
        # Save model and scaler
        joblib.dump({
            'model': self.model,
            'scaler': self.scaler,
            'feature_columns': self.feature_columns
        }, model_path)
        
        print(f"\nModel saved to {model_path}")
    
    def load_model(self, model_path):
        """Load a trained model"""
        saved_data = joblib.load(model_path)
        self.model = saved_data['model']
        self.scaler = saved_data['scaler']
        self.feature_columns = saved_data['feature_columns']
        print("Model loaded successfully")

def main():
    # Initialize predictor
    predictor = WarehousePricePredictor()
    
    # Train model
    data_path = "D:/django/edit 2/vaultspace/users/tests/99acres_warehouse_rentals_updated.csv"
    model_path = "warehouse_recommender/app/models/price_predictor.joblib"
    
    print("Training model...")
    predictor.train(data_path)
    
    # Save model
    predictor.save_model(model_path)
    
    # Example predictions with optimal price suggestions
    print("\nExample predictions with optimal price suggestions:")
    test_cases = [
        (10000, 10.0521676, 76.3199033),  # Kalamassery
        (5000, 10.1100952, 76.3495159),   # Aluva
        (20000, 11.18868155, 75.85291367)  # Ramanattukara
    ]
    
    for area, lat, lon in test_cases:
        suggestions = predictor.get_optimal_price_suggestions(area, lat, lon)
        print(f"\nWarehouse at ({lat}, {lon}) with {area:,} sqft:")
        print(f"Optimal Price: ₹{suggestions['optimal_price']:,.2f}")
        print(f"Price Range: ₹{suggestions['price_range']['low']:,.2f} - ₹{suggestions['price_range']['high']:,.2f}")
        print(f"Price per sqft: ₹{suggestions['price_per_sqft']:,.2f}")
        print(f"Confidence: {suggestions['confidence']:.1f}%")

if __name__ == "__main__":
    main() 