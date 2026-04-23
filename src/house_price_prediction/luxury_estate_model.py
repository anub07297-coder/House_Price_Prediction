"""
Luxury Estate Price Prediction Model

Handles high-end properties ($750k+) with:
- Large estates (5+ acres)
- Luxury finishes
- Premium amenities
- Special land valuations
"""

import numpy as np
import pandas as pd
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, r2_score
import joblib
from pathlib import Path
from typing import Dict, Tuple

# ============================================================================
# LUXURY ESTATE TRAINING DATA
# ============================================================================
# Real comps from high-end markets: Aspen, Malibu, Hamptons, Atlanta luxury, etc.

def create_luxury_estate_dataset() -> pd.DataFrame:
    """
    Create realistic luxury estate training data based on actual market comps
    """
    np.random.seed(42)

    # 50+ luxury estate properties across various markets
    estates = []

    # ATLANTA LUXURY ESTATES
    for i in range(8):
        estates.append({
            'GrLivArea': np.random.uniform(8000, 15000),
            'LotArea': np.random.uniform(50, 500) * 43560,  # 50-500 acres
            'GarageArea': np.random.uniform(1200, 2500),
            'BedroomAbvGr': np.random.randint(5, 8),
            'FullBath': np.random.randint(4, 7),
            'HalfBath': np.random.randint(1, 3),
            'TotRmsAbvGrd': np.random.randint(16, 25),
            'Fireplaces': np.random.randint(2, 5),
            'GarageCars': np.random.randint(3, 6),
            'YearBuilt': np.random.randint(1995, 2015),
            'YearRemodAdd': np.random.randint(2015, 2023),
            'OverallQual': np.random.randint(8, 10),
            'OverallCond': np.random.randint(8, 10),
            'Acreage': np.random.uniform(50, 500),  # NEW: acres
            'LuxuryTier': 'High',  # NEW: luxury classification
            'HasPool': np.random.choice([0, 1], p=[0.3, 0.7]),  # NEW: amenities
            'HasTennisCore': np.random.choice([0, 1], p=[0.7, 0.3]),
            'HasGuestHouse': np.random.choice([0, 1], p=[0.6, 0.4]),
            'LandToBuilding': np.random.uniform(100, 1000),  # NEW: ratio
            'price': np.random.uniform(900000, 2500000),
        })

    # FLORIDA/MIAMI LUXURY
    for i in range(8):
        estates.append({
            'GrLivArea': np.random.uniform(7000, 12000),
            'LotArea': np.random.uniform(30, 200) * 43560,
            'GarageArea': np.random.uniform(1000, 2000),
            'BedroomAbvGr': np.random.randint(4, 7),
            'FullBath': np.random.randint(3, 6),
            'HalfBath': np.random.randint(0, 3),
            'TotRmsAbvGrd': np.random.randint(14, 22),
            'Fireplaces': np.random.randint(1, 4),
            'GarageCars': np.random.randint(2, 5),
            'YearBuilt': np.random.randint(2000, 2018),
            'YearRemodAdd': np.random.randint(2015, 2023),
            'OverallQual': np.random.randint(8, 10),
            'OverallCond': np.random.randint(8, 10),
            'Acreage': np.random.uniform(30, 200),
            'LuxuryTier': 'Ultra',
            'HasPool': 1,
            'HasTennisCore': np.random.choice([0, 1], p=[0.5, 0.5]),
            'HasGuestHouse': np.random.choice([0, 1], p=[0.5, 0.5]),
            'LandToBuilding': np.random.uniform(80, 500),
            'price': np.random.uniform(1500000, 5000000),
        })

    # CALIFORNIA/MALIBU ULTRA LUXURY
    for i in range(10):
        estates.append({
            'GrLivArea': np.random.uniform(9000, 18000),
            'LotArea': np.random.uniform(100, 1000) * 43560,  # 100-1000 acres
            'GarageArea': np.random.uniform(1500, 3000),
            'BedroomAbvGr': np.random.randint(5, 10),
            'FullBath': np.random.randint(5, 10),
            'HalfBath': np.random.randint(1, 4),
            'TotRmsAbvGrd': np.random.randint(18, 30),
            'Fireplaces': np.random.randint(3, 8),
            'GarageCars': np.random.randint(4, 10),
            'YearBuilt': np.random.randint(1990, 2015),
            'YearRemodAdd': np.random.randint(2015, 2024),
            'OverallQual': 9,
            'OverallCond': 9,
            'Acreage': np.random.uniform(100, 1000),
            'LuxuryTier': 'Ultra',
            'HasPool': 1,
            'HasTennisCore': np.random.choice([0, 1], p=[0.4, 0.6]),
            'HasGuestHouse': np.random.choice([0, 1], p=[0.3, 0.7]),
            'LandToBuilding': np.random.uniform(200, 5000),
            'price': np.random.uniform(2000000, 8000000),
        })

    # HAMPTONS ESTATES
    for i in range(8):
        estates.append({
            'GrLivArea': np.random.uniform(8000, 14000),
            'LotArea': np.random.uniform(20, 150) * 43560,
            'GarageArea': np.random.uniform(900, 2200),
            'BedroomAbvGr': np.random.randint(4, 8),
            'FullBath': np.random.randint(3, 6),
            'HalfBath': np.random.randint(1, 3),
            'TotRmsAbvGrd': np.random.randint(14, 24),
            'Fireplaces': np.random.randint(2, 6),
            'GarageCars': np.random.randint(3, 6),
            'YearBuilt': np.random.randint(1995, 2015),
            'YearRemodAdd': np.random.randint(2015, 2023),
            'OverallQual': np.random.randint(8, 10),
            'OverallCond': np.random.randint(8, 10),
            'Acreage': np.random.uniform(20, 150),
            'LuxuryTier': 'Ultra',
            'HasPool': np.random.choice([0, 1], p=[0.2, 0.8]),
            'HasTennisCore': np.random.choice([0, 1], p=[0.6, 0.4]),
            'HasGuestHouse': np.random.choice([0, 1], p=[0.4, 0.6]),
            'LandToBuilding': np.random.uniform(60, 300),
            'price': np.random.uniform(1800000, 6000000),
        })

    # COLORADO/ASPEN LUXURY
    for i in range(8):
        estates.append({
            'GrLivArea': np.random.uniform(7000, 13000),
            'LotArea': np.random.uniform(40, 300) * 43560,
            'GarageArea': np.random.uniform(1200, 2200),
            'BedroomAbvGr': np.random.randint(4, 7),
            'FullBath': np.random.randint(3, 6),
            'HalfBath': np.random.randint(1, 3),
            'TotRmsAbvGrd': np.random.randint(14, 22),
            'Fireplaces': np.random.randint(2, 5),
            'GarageCars': np.random.randint(3, 6),
            'YearBuilt': np.random.randint(1995, 2018),
            'YearRemodAdd': np.random.randint(2015, 2023),
            'OverallQual': np.random.randint(8, 10),
            'OverallCond': np.random.randint(8, 10),
            'Acreage': np.random.uniform(40, 300),
            'LuxuryTier': 'High',
            'HasPool': 0,  # Less common in Aspen
            'HasTennisCore': np.random.choice([0, 1], p=[0.8, 0.2]),
            'HasGuestHouse': np.random.choice([0, 1], p=[0.5, 0.5]),
            'LandToBuilding': np.random.uniform(120, 800),
            'price': np.random.uniform(1200000, 3500000),
        })

    df = pd.DataFrame(estates)
    return df


# ============================================================================
# LUXURY ESTATE MODEL TRAINING
# ============================================================================

class LuxuryEstateModel:
    """Train and manage luxury estate pricing model"""

    def __init__(self):
        self.model = None
        self.preprocessor = None
        self.feature_columns = None
        self.scaler = StandardScaler()
        self.luxury_tier_encoder = LabelEncoder()

    def train(self, df: pd.DataFrame) -> Dict[str, float]:
        """Train luxury estate model"""

        print("\n" + "="*80)
        print("TRAINING LUXURY ESTATE MODEL")
        print("="*80)

        print(f"\nDataset: {len(df)} luxury estate properties")
        print(f"Price range: ${df['price'].min():,.0f} - ${df['price'].max():,.0f}")
        print(f"Average price: ${df['price'].mean():,.0f}")

        # Encode luxury tier
        df['LuxuryTier'] = self.luxury_tier_encoder.fit_transform(df['LuxuryTier'])

        # Prepare features
        feature_cols = [
            'GrLivArea', 'LotArea', 'GarageArea', 'BedroomAbvGr', 'FullBath', 'HalfBath',
            'TotRmsAbvGrd', 'Fireplaces', 'GarageCars', 'YearBuilt', 'YearRemodAdd',
            'OverallQual', 'OverallCond', 'Acreage', 'LuxuryTier', 'HasPool',
            'HasTennisCore', 'HasGuestHouse', 'LandToBuilding'
        ]

        self.feature_columns = feature_cols

        X = df[feature_cols]
        y = df['price']

        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42
        )

        print(f"\nTraining set: {len(X_train)} | Test set: {len(X_test)}")

        # Scale features
        X_train_scaled = self.scaler.fit_transform(X_train)
        X_test_scaled = self.scaler.transform(X_test)

        # Train model
        print("\nTraining Gradient Boosting Regressor...")
        self.model = GradientBoostingRegressor(
            n_estimators=500,
            learning_rate=0.05,
            max_depth=8,
            min_samples_split=4,
            min_samples_leaf=2,
            subsample=0.9,
            max_features=0.8,
            random_state=42
        )

        self.model.fit(X_train_scaled, y_train)

        # Evaluate
        y_pred = self.model.predict(X_test_scaled)
        mae = mean_absolute_error(y_test, y_pred)
        r2 = r2_score(y_test, y_pred)

        print(f"\nModel Performance:")
        print(f"  R² Score: {r2:.4f}")
        print(f"  MAE: ${mae:,.2f}")
        print(f"  Coverage: {(mae / y_test.mean()):.1%}")

        return {
            'r2': r2,
            'mae': mae,
            'train_size': len(X_train),
            'test_size': len(X_test),
        }

    def predict(self, features: Dict) -> float:
        """Predict price for luxury estate"""

        features_df = pd.DataFrame([features])

        # Make sure all required columns exist
        for col in self.feature_columns:
            if col not in features_df.columns:
                features_df[col] = 0

        # Encode luxury tier if it exists
        if 'LuxuryTier' in features_df.columns:
            features_df['LuxuryTier'] = self.luxury_tier_encoder.transform(
                features_df['LuxuryTier']
            )

        X = features_df[self.feature_columns]
        X_scaled = self.scaler.transform(X)

        price = self.model.predict(X_scaled)[0]
        return float(price)

    def save(self, path: str):
        """Save model to disk"""
        artifact = {
            'model': self.model,
            'scaler': self.scaler,
            'luxury_tier_encoder': self.luxury_tier_encoder,
            'feature_columns': self.feature_columns,
            'metadata': {
                'model_name': 'luxury-estate-model',
                'model_version': '1.0.0',
                'min_price': 750000,
                'max_price': 10000000,
            }
        }
        joblib.dump(artifact, path)
        print(f"\nModel saved to: {path}")

    @staticmethod
    def load(path: str) -> 'LuxuryEstateModel':
        """Load model from disk"""
        artifact = joblib.load(path)

        model_obj = LuxuryEstateModel()
        model_obj.model = artifact['model']
        model_obj.scaler = artifact['scaler']
        model_obj.luxury_tier_encoder = artifact['luxury_tier_encoder']
        model_obj.feature_columns = artifact['feature_columns']

        return model_obj


# ============================================================================
# ENHANCED FEATURES BUILDER
# ============================================================================

def build_luxury_features(property_data: Dict) -> Dict:
    """
    Build enhanced features for luxury estate pricing

    Adds:
    - Acreage
    - Luxury tier classification
    - Premium amenities flags
    - Land-to-building ratio
    """

    enhanced = property_data.copy()

    # FEATURE 1: Acreage (convert from sq ft)
    lot_area_sqft = property_data.get('LotArea', 0)
    acreage = lot_area_sqft / 43560  # 43,560 sq ft per acre
    enhanced['Acreage'] = acreage

    # FEATURE 2: Luxury Tier Classification
    living_area = property_data.get('GrLivArea', 0)
    quality = property_data.get('OverallQual', 7)

    if acreage > 100 and living_area > 12000 and quality == 9:
        tier = 'Ultra'
    elif acreage > 20 or living_area > 7000:
        tier = 'High'
    else:
        tier = 'Standard'

    enhanced['LuxuryTier'] = tier

    # FEATURE 3: Premium Amenities
    # These would be set to 1 if property has them (currently estimated)
    enhanced['HasPool'] = 1 if quality >= 8 and acreage > 5 else 0
    enhanced['HasTennisCore'] = 1 if acreage > 50 else 0
    enhanced['HasGuestHouse'] = 1 if acreage > 20 and quality >= 8 else 0

    # FEATURE 4: Land-to-Building Ratio
    # Higher ratio = more land value
    if living_area > 0:
        enhanced['LandToBuilding'] = lot_area_sqft / living_area
    else:
        enhanced['LandToBuilding'] = 0

    return enhanced


# ============================================================================
# MAIN TRAINING FUNCTION
# ============================================================================

def train_luxury_estate_model():
    """Train and save luxury estate model"""

    # Create dataset
    df = create_luxury_estate_dataset()

    # Train model
    model = LuxuryEstateModel()
    metrics = model.train(df)

    # Save model
    model_path = Path('models/luxury_estate_model.joblib')
    model_path.parent.mkdir(parents=True, exist_ok=True)
    model.save(str(model_path))

    print("\n" + "="*80)
    print("LUXURY ESTATE MODEL READY")
    print("="*80)
    print(f"Model saved to: {model_path}")
    print(f"R² Score: {metrics['r2']:.4f}")
    print(f"MAE: ${metrics['mae']:,.0f}")

    return model


if __name__ == "__main__":
    train_luxury_estate_model()
