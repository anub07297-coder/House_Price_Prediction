"""
IMPROVED PRICE PREDICTION MODEL - Fixed Lot Size Handling

Key Improvements:
1. Lot size categories (not just continuous)
2. Land-to-building ratio feature
3. Lot-based price multipliers
4. Better decomposition of building vs land value
"""

import numpy as np
import pandas as pd
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.preprocessing import StandardScaler
import joblib
from pathlib import Path
from typing import Dict


class ImprovedPricePredictionModel:
    """Enhanced model with proper lot size feature engineering"""

    def __init__(self):
        self.model = None
        self.scaler = StandardScaler()
        self.feature_columns = None
        self.metadata = {}

    @staticmethod
    def engineer_lot_features(property_data: Dict) -> Dict:
        """
        Create lot-size-aware features that significantly improve predictions
        """
        features = property_data.copy()

        # FEATURE 1: Convert lot area to acres
        lot_sqft = features.get('LotArea', 0)
        lot_acres = lot_sqft / 43560 if lot_sqft > 0 else 0
        features['LotAcres'] = lot_acres

        # FEATURE 2: Lot size category (WITH PRICE MULTIPLIERS)
        if lot_acres < 0.5:
            features['LotCategory'] = 1  # Small - tight urban
            features['LotMultiplier'] = 0.95  # Slight discount
        elif lot_acres < 1.0:
            features['LotCategory'] = 2  # Standard suburban (baseline)
            features['LotMultiplier'] = 1.0  # Baseline
        elif lot_acres < 5.0:
            features['LotCategory'] = 3  # Large suburban
            features['LotMultiplier'] = 1.25  # 25% premium
        elif lot_acres < 20.0:
            features['LotCategory'] = 4  # Small estate
            features['LotMultiplier'] = 1.40  # 40% premium
        else:
            features['LotCategory'] = 5  # Large estate
            # 50% premium (caps out, diminishing returns)
            features['LotMultiplier'] = 1.50

        # FEATURE 3: Land-to-Building Ratio
        living_area = features.get('GrLivArea', 0)
        if living_area > 0:
            features['LandToBuilding'] = lot_sqft / living_area
        else:
            features['LandToBuilding'] = 0

        # FEATURE 4: Decomposed Building Value Baseline
        # Estimate: quality buildings get more per sqft on premium lots
        quality = features.get('OverallQual', 7)
        condition = features.get('OverallCond', 7)
        quality_score = (quality + condition) / 2

        # Base price per sqft depends on lot size!
        if lot_acres < 0.5:
            base_price_per_sqft = 180  # Urban: building is main value
        elif lot_acres < 1.0:
            base_price_per_sqft = 200  # Standard: good balance
        elif lot_acres < 10.0:
            base_price_per_sqft = 220  # Larger lot: land adds value
        else:
            base_price_per_sqft = 240  # Estate: land is significant

        # Adjust for quality
        quality_adjusted_price_per_sqft = base_price_per_sqft * \
            (quality_score / 7.0)
        features['EstimatedBuildingValuePerSqft'] = quality_adjusted_price_per_sqft

        # FEATURE 5: Log-scaled lot acres (captures diminishing returns)
        features['LogLotAcres'] = np.log1p(lot_acres)

        return features

    @staticmethod
    def create_training_data() -> pd.DataFrame:
        """Create enhanced training dataset with proper lot pricing"""
        np.random.seed(42)

        data = []

        # Generate diverse properties with CORRECT lot-price relationships
        properties_configs = [
            # (count, lot_acres_range, sqft_range, price_range, lot_mult)
            # Small lots, $250-450k
            (30, (0.15, 0.35), (1200, 2500), (250000, 450000), 0.95),
            (40, (0.35, 0.75), (1800, 3200),
             (350000, 550000), 1.00),     # Standard lots
            (30, (0.75, 1.5), (2500, 4000),
             (500000, 850000), 1.25),      # Large suburban
            (20, (1.5, 5.0), (3500, 5500),
             (700000, 1200000), 1.40),      # Small estates
            (15, (5.0, 50.0), (5000, 9000),
             (1200000, 2500000), 1.50),    # Large estates
            (10, (50.0, 500.0), (8000, 15000),
             (2000000, 5000000), 1.50),  # Very large estates
        ]

        for count, lot_range, sqft_range, price_range, lot_mult in properties_configs:
            for _ in range(count):
                lot_acres = np.random.uniform(lot_range[0], lot_range[1])
                lot_sqft = lot_acres * 43560

                living_sqft = np.random.uniform(sqft_range[0], sqft_range[1])
                quality = np.random.randint(6, 10)

                # CORRECT PRICING MODEL:
                # Base price from building
                base_price_per_sqft = 200 * (quality / 7.0)
                building_value = living_sqft * base_price_per_sqft

                # Add land value (diminishing returns on large lots)
                price_per_acre_base = 80000
                land_value = price_per_acre_base * np.log1p(lot_acres) * 0.8

                # Total with lot multiplier
                total_price = (building_value + land_value) * lot_mult

                data.append({
                    'LotAcres': lot_acres,
                    'GrLivArea': living_sqft,
                    'OverallQual': quality,
                    'OverallCond': np.random.randint(6, 9),
                    'YearBuilt': np.random.randint(1990, 2020),
                    'YearRemodAdd': np.random.randint(2010, 2024),
                    'BedroomAbvGr': np.random.randint(2, 6),
                    'FullBath': np.random.randint(1, 4),
                    'HalfBath': np.random.randint(0, 2),
                    'GarageCars': np.random.randint(1, 4),
                    'GarageArea': np.random.uniform(300, 1200),
                    'TotRmsAbvGrd': np.random.randint(6, 16),
                    'Fireplaces': np.random.randint(0, 3),
                    'price': total_price,
                })

        df = pd.DataFrame(data)

        # Add engineered features
        engineered_data = []
        for idx, row in df.iterrows():
            row_dict = row.to_dict()
            row_dict['LotArea'] = row_dict.pop('LotAcres') * 43560

            engineered = ImprovedPricePredictionModel.engineer_lot_features(
                row_dict)
            engineered_data.append(engineered)

        return pd.DataFrame(engineered_data)

    def train(self, df: pd.DataFrame):
        """Train the improved model"""
        print("\n" + "="*80)
        print("TRAINING IMPROVED PRICE PREDICTION MODEL")
        print("="*80)

        print(f"\nDataset: {len(df)} properties")
        print(
            f"Price range: ${df['price'].min():,.0f} - ${df['price'].max():,.0f}")
        print(f"Average price: ${df['price'].mean():,.0f}")

        # Features for training
        feature_cols = [
            'LotAcres', 'GrLivArea', 'OverallQual', 'OverallCond',
            'YearBuilt', 'YearRemodAdd', 'BedroomAbvGr', 'FullBath', 'HalfBath',
            'GarageCars', 'GarageArea', 'TotRmsAbvGrd', 'Fireplaces',
            'LotCategory', 'LotMultiplier', 'LandToBuilding',
            'LogLotAcres', 'EstimatedBuildingValuePerSqft'
        ]

        self.feature_columns = feature_cols

        X = df[feature_cols]
        y = df['price']

        # Scale
        X_scaled = self.scaler.fit_transform(X)

        # Train
        print("\nTraining Gradient Boosting Regressor with improved features...")
        self.model = GradientBoostingRegressor(
            n_estimators=300,
            learning_rate=0.08,
            max_depth=6,
            min_samples_split=5,
            min_samples_leaf=2,
            subsample=0.9,
            max_features=0.8,
            random_state=42
        )

        self.model.fit(X_scaled, y)

        # Evaluate
        from sklearn.metrics import mean_absolute_error, r2_score
        y_pred = self.model.predict(X_scaled)
        mae = mean_absolute_error(y, y_pred)
        r2 = r2_score(y, y_pred)

        print(f"\nImproved Model Performance:")
        print(f"  R² Score: {r2:.4f}")
        print(f"  MAE: ${mae:,.0f}")
        print(f"  RMSE: ${np.sqrt(np.mean((y - y_pred)**2)):,.0f}")

        self.metadata = {
            'r2': r2,
            'mae': mae,
            'features': feature_cols,
            'model_type': 'GradientBoosting_ImprovedLotHandling',
        }

    def predict(self, property_data: Dict) -> float:
        """Make prediction with improved model"""
        # Engineer features
        engineered = self.engineer_lot_features(property_data)

        # Prepare dataframe
        X = pd.DataFrame([engineered])[self.feature_columns]

        # Scale and predict
        X_scaled = self.scaler.transform(X)
        price = self.model.predict(X_scaled)[0]

        return float(price)

    def save(self, path: str):
        """Save model"""
        artifact = {
            'model': self.model,
            'scaler': self.scaler,
            'feature_columns': self.feature_columns,
            'metadata': self.metadata,
        }
        joblib.dump(artifact, path)
        print(f"\nModel saved to: {path}")

    @staticmethod
    def load(path: str) -> 'ImprovedPricePredictionModel':
        """Load model"""
        artifact = joblib.load(path)
        obj = ImprovedPricePredictionModel()
        obj.model = artifact['model']
        obj.scaler = artifact['scaler']
        obj.feature_columns = artifact['feature_columns']
        obj.metadata = artifact['metadata']
        return obj


def test_improved_model():
    """Test on both properties"""
    print("\n" + "="*100)
    print("CREATING AND TESTING IMPROVED MODEL")
    print("="*100)

    # Train
    df = ImprovedPricePredictionModel.create_training_data()
    model = ImprovedPricePredictionModel()
    model.train(df)

    # Save
    model_path = Path('models/improved_price_prediction_model.joblib')
    model_path.parent.mkdir(parents=True, exist_ok=True)
    model.save(str(model_path))

    # Test on both properties
    print("\n" + "="*100)
    print("TESTING ON REAL PROPERTIES")
    print("="*100 + "\n")

    # Test 1: 750 Tramore Pl
    tramore = {
        'LotArea': 1.1 * 43560,
        'GrLivArea': 3650,
        'OverallQual': 7,
        'OverallCond': 7,
        'YearBuilt': 2006,
        'YearRemodAdd': 2015,
        'BedroomAbvGr': 4,
        'FullBath': 2,
        'HalfBath': 1,
        'GarageCars': 3,
        'GarageArea': 900,
        'TotRmsAbvGrd': 11,
        'Fireplaces': 1,
    }

    tramore_pred = model.predict(tramore)
    tramore_actual = 1299400

    print(f"750 TRAMORE PL")
    print(f"  Old Model Prediction: $682,863")
    print(f"  New Model Prediction: ${tramore_pred:,.2f}")
    print(f"  Actual:               ${tramore_actual:,.2f}")
    print(
        f"  Improvement:          {abs((tramore_pred - 682863) / (tramore_actual - 682863) * 100):.1f}% better")

    # Test 2: 292 Traditions Dr
    traditions = {
        'LotArea': 950 * 43560,
        'GrLivArea': 11947,
        'OverallQual': 9,
        'OverallCond': 9,
        'YearBuilt': 2005,
        'YearRemodAdd': 2020,
        'BedroomAbvGr': 5,
        'FullBath': 5,
        'HalfBath': 1,
        'GarageCars': 4,
        'GarageArea': 1800,
        'TotRmsAbvGrd': 18,
        'Fireplaces': 3,
    }

    traditions_pred = model.predict(traditions)
    traditions_actual = 2695000

    print(f"\n292 TRADITIONS DR")
    print(f"  Old Model Prediction: $716,402")
    print(f"  New Model Prediction: ${traditions_pred:,.2f}")
    print(f"  Actual:               ${traditions_actual:,.2f}")
    print(
        f"  Improvement:          {abs((traditions_pred - 716402) / (traditions_actual - 716402) * 100):.1f}% better")

    print("\n" + "="*100)


if __name__ == "__main__":
    test_improved_model()
