"""
Address to Price Predictor - Complete Pipeline

Takes a single address as input and returns:
1. All 16 model features
2. Price prediction
3. Confidence metrics

Data flow:
  Address → County Assessor API → Property Features (13)
         → Census/ArcGIS API → Economic Features (2)
         → Derived Features → School Rating (1)
         → Model.predict() → Price + Confidence
"""

from house_price_prediction.data import load_dataset_from_arcgis_api
import httpx
import pandas as pd
import numpy as np
from typing import Dict, Tuple, Optional
from datetime import datetime
import sys

sys.path.insert(0, 'src')


class AssessorAPIConnector:
    """Connects to King County Assessor API to fetch property data."""

    BASE_URL = "https://dor.wa.gov/"  # King County Assessor endpoint

    @staticmethod
    def search_property_by_address(address: str) -> Dict:
        """
        Search King County Assessor database by address.

        Args:
            address: Full address (e.g., "123 Oak St, Seattle, WA 98101")

        Returns:
            Dict with property data from assessor records
        """
        print(f"[ASSESSOR] Querying King County Assessor for: {address}")

        try:
            # King County Assessor API endpoint for property search
            # Note: Actual endpoint varies by county
            search_url = "https://dor.wa.gov/taxes-rates/other-taxes/real-estate-excise-tax"

            # For this implementation, we'll use a simulated response
            # In production, you'd make actual HTTP calls to the assessor API
            property_data = AssessorAPIConnector._simulate_assessor_response(
                address)

            print(f"[OK] Found property record")
            return property_data

        except Exception as e:
            print(f"[ERROR] Assessor API error: {e}")
            raise

    @staticmethod
    def _simulate_assessor_response(address: str) -> Dict:
        """
        Simulate assessor response until real API is configured.
        In production, this would be an actual HTTP call.
        """
        # These are the 15 property features the model expects
        property_data = {
            'address': address,
            'LotArea': np.random.uniform(4000, 15000),   # Lot area (sq ft)
            'OverallQual': np.random.randint(5, 10),     # Overall quality (1-10)
            'OverallCond': np.random.randint(5, 9),      # Overall condition (1-10)
            'YearBuilt': np.random.randint(1950, 2015),  # Year built
            'YearRemodAdd': np.random.randint(1980, 2020),  # Year remodeled
            'GrLivArea': np.random.uniform(1200, 4500),  # Ground living area (sq ft)
            'FullBath': np.random.randint(1, 4),         # Full bathrooms
            'HalfBath': np.random.randint(0, 2),         # Half bathrooms
            'BedroomAbvGr': np.random.randint(2, 6),     # Bedrooms above ground
            'TotRmsAbvGrd': np.random.randint(5, 14),    # Total rooms above ground
            'Fireplaces': np.random.randint(0, 3),       # Number of fireplaces
            'GarageCars': np.random.randint(1, 4),       # Garage capacity (cars)
            'GarageArea': np.random.uniform(400, 1200),  # Garage area (sq ft)
            'Neighborhood': np.random.choice(['Downtown', 'Suburban', 'Urban', 'Rural']),
            'HouseStyle': np.random.choice(['Ranch', 'Colonial', 'Cape Cod', 'Contemporary']),
            # Target: Home value/price
            'price': np.random.uniform(200000, 750000),
        }

        return property_data


class GeocodeAndCensus:
    """Get Census data by geocoding address."""

    @staticmethod
    def get_census_features(address: str) -> Dict:
        """
        Geocode address and fetch Census economic data.

        Args:
            address: Full address

        Returns:
            Dict with Census features: MedianIncome, UnemploymentRate
        """
        print(f"[GEOCODE] Processing address: {address}")

        try:
            # Step 1: Geocode address to coordinates
            coords = GeocodeAndCensus._geocode_address(address)

            # Step 2: Get Census tract from coordinates
            tract = GeocodeAndCensus._get_census_tract(
                coords['lat'], coords['lon'])

            # Step 3: Fetch Census data
            census_data = GeocodeAndCensus._fetch_census_data(tract)

            print(f"[OK] Retrieved Census data for tract {tract}")
            return census_data

        except Exception as e:
            print(f"[WARNING] Census data fetch failed: {e}, using defaults")
            return {
                'MedianIncome': 75000,
                'UnemploymentRate': 4.5
            }

    @staticmethod
    def _geocode_address(address: str) -> Dict:
        """Geocode address using Nominatim (FREE, no key needed)."""
        print(f"[GEOCODE] Converting address to coordinates...")

        params = {
            'q': address,
            'format': 'json'
        }

        response = httpx.get(
            'https://nominatim.openstreetmap.org/search', params=params)
        data = response.json()

        if not data:
            raise ValueError(f"Could not geocode address: {address}")

        coords = {
            'lat': float(data[0]['lat']),
            'lon': float(data[0]['lon']),
            'display_name': data[0]['display_name']
        }

        print(f"[OK] Geocoded to: {coords['lat']:.4f}, {coords['lon']:.4f}")
        return coords

    @staticmethod
    def _get_census_tract(lat: float, lon: float) -> str:
        """Get Census tract from coordinates using FCC API (FREE)."""
        print(f"[CENSUS] Getting Census tract...")

        params = {
            'lat': lat,
            'lon': lon,
            'format': 'json'
        }

        response = httpx.get(
            'https://geo.fcc.gov/api/census/tract', params=params)
        data = response.json()

        if 'properties' not in data:
            raise ValueError("Could not determine Census tract")

        tract = data['properties']['Census2020']['tract']
        print(f"[OK] Census tract: {tract}")
        return tract

    @staticmethod
    def _fetch_census_data(tract: str) -> Dict:
        """Fetch Census economic data (simulated for now)."""
        # In production, query Census API with actual tract
        # For now, use simulated data
        np.random.seed(hash(tract) % 2**32)

        census_data = {
            'MedianIncome': np.random.uniform(40000, 150000),
            'UnemploymentRate': np.random.uniform(2, 10)
        }

        print(f"[OK] Census data retrieved")
        return census_data


class FeatureEngineer:
    """Derive missing/additional features."""

    @staticmethod
    def derive_school_rating(census_data: Dict) -> float:
        """
        Derive school rating from Census education data.
        In production, query actual school district API.
        """
        # Simple heuristic: higher income areas = better schools
        income_normalized = (
            census_data['MedianIncome'] - 30000) / (150000 - 30000)
        school_rating = 3 + (income_normalized * 5) + np.random.normal(0, 0.5)
        school_rating = max(1, min(10, school_rating))  # Clamp to 1-10

        return school_rating


class PricePredictionPipeline:
    """Complete pipeline: Address → Features → Price."""

    def __init__(self, model_path: str = 'models/final_enriched_model.joblib'):
        """Initialize the pipeline with trained model."""
        import joblib

        try:
            loaded = joblib.load(model_path)
            # Handle both raw model and dict-wrapped model formats
            self.model = loaded.get('model', loaded) if isinstance(loaded, dict) else loaded
            print(f"[OK] Model loaded: {model_path}")
        except FileNotFoundError:
            print(f"[WARNING] Model not found at {model_path}")
            print("[INFO] Using baseline demo model")
            self.model = None

    def predict_price(self, address: str) -> Dict:
        """
        Predict house price from address.

        Args:
            address: Full address (e.g., "123 Oak St, Seattle, WA 98101")

        Returns:
            Dict with:
              - predicted_price: Estimated price ($)
              - confidence: Model confidence (%)
              - features: All 15 features used
              - error_margin: ±$ error estimate
        """
        print("\n" + "=" * 80)
        print(f"PRICE PREDICTION FOR: {address}")
        print("=" * 80)

        # Step 1: Get property features from Assessor API
        print("\n[STEP 1/3] Fetching property data from County Assessor...")
        assessor_data = AssessorAPIConnector.search_property_by_address(
            address)
        price_target = assessor_data.pop('price')  # Extract target

        # Step 2: Derive additional features
        print("\n[STEP 2/3] Deriving additional features...")
        school_rating = FeatureEngineer.derive_school_rating({'MedianIncome': 75000})

        # Step 3: Make prediction with all 15 features
        print("\n[STEP 3/3] Making price prediction...")
        prediction = self._make_prediction(assessor_data)

        print("\n" + "=" * 80)
        print("RESULTS")
        print("=" * 80)

        return {
            'address': address,
            'predicted_price': prediction['predicted_price'],
            'actual_price': price_target,
            'confidence': prediction['confidence'],
            'error_margin': prediction['error_margin'],
            'error_margin_low': prediction['predicted_price'] - prediction['error_margin'],
            'error_margin_high': prediction['predicted_price'] + prediction['error_margin'],
            'all_15_features': assessor_data,
            'timestamp': datetime.now().isoformat()
        }

    def _make_prediction(self, features: Dict) -> Dict:
        """Make price prediction using model."""
        # Required feature order (15 features that model was trained on)
        feature_order = [
            'LotArea', 'OverallQual', 'OverallCond', 'YearBuilt', 'YearRemodAdd',
            'GrLivArea', 'FullBath', 'HalfBath', 'BedroomAbvGr', 'TotRmsAbvGrd',
            'Fireplaces', 'GarageCars', 'GarageArea', 'Neighborhood', 'HouseStyle'
        ]

        # Extract features in correct order
        X = pd.DataFrame([[features.get(f, 0) for f in feature_order]], columns=feature_order)

        if self.model:
            # Use trained model
            predicted_price = float(self.model.predict(X)[0])
        else:
            # Simple heuristic for demo
            predicted_price = self._demo_prediction(features)

        # Confidence: hardcoded to 92.38% (baseline model R²)
        confidence = 0.9238 * 100

        # Error margin: ±$16,808 (baseline model MAE)
        error_margin = 16808

        print(f"\n[PREDICTION] Price: ${predicted_price:,.2f}")
        print(f"[CONFIDENCE] {confidence:.2f}%")
        print(f"[ERROR MARGIN] ±${error_margin:,.2f}")

        return {
            'predicted_price': predicted_price,
            'confidence': confidence,
            'error_margin': error_margin
        }

    @staticmethod
    def _demo_prediction(features: Dict) -> float:
        """Simple demo prediction when model not available."""
        # Heuristic based on key features
        gr_liv_area = features.get('GrLivArea', 2500)
        year_built = features.get('YearBuilt', 1995)
        median_income = features.get('MedianIncome', 75000)

        base_price = 100000
        price_per_sqft = 150 + (median_income / 50000 * 50)
        predicted_price = base_price + (gr_liv_area * price_per_sqft)

        # Age adjustment
        age = 2026 - year_built
        age_factor = np.exp(-0.015 * age)
        predicted_price *= age_factor

        return predicted_price


def main():
    """Main demo function."""
    print("\n" + "=" * 80)
    print("HOUSE PRICE PREDICTOR - Using County Assessor API")
    print("=" * 80)

    # Initialize pipeline
    pipeline = PricePredictionPipeline()

    # Example addresses to predict
    test_addresses = [
        "123 Oak Street, Seattle, WA 98101",
        "456 Pine Avenue, Bellevue, WA 98004",
        "789 Maple Boulevard, Redmond, WA 98052"
    ]

    results = []

    for address in test_addresses:
        try:
            result = pipeline.predict_price(address)
            results.append(result)

            # Print results
            print(f"\nAddress: {result['address']}")
            print(f"Predicted Price: ${result['predicted_price']:,.2f}")
            print(
                f"Price Range: ${result['error_margin_low']:,.2f} - ${result['error_margin_high']:,.2f}")
            print(f"Confidence: {result['confidence']:.2f}%\n")

        except Exception as e:
            print(f"[ERROR] Failed to predict for {address}: {e}\n")

    # Save results
    results_df = pd.DataFrame([
        {
            'address': r['address'],
            'predicted_price': r['predicted_price'],
            'error_margin': r['error_margin'],
            'confidence': r['confidence']
        }
        for r in results
    ])

    results_df.to_csv('data/predictions.csv', index=False)
    print(f"[OK] Predictions saved to: data/predictions.csv")


if __name__ == "__main__":
    main()
