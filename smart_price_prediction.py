"""
Dual-Model Price Prediction Pipeline
Automatically chooses between Standard and Luxury Estate models
"""

import sys
sys.path.insert(0, 'src')

from house_price_prediction.address_to_price import PricePredictionPipeline, SchoolDistrictFeature
from house_price_prediction.luxury_estate_model import LuxuryEstateModel, build_luxury_features
from pathlib import Path
import joblib


class SmartPricePredictionPipeline:
    """
    Dual-model pipeline that intelligently selects between:
    - Standard model for typical homes ($100k-$750k)
    - Luxury estate model for high-end properties ($750k+)
    """

    def __init__(self):
        """Initialize both models"""
        self.standard_pipeline = PricePredictionPipeline()

        # Load luxury estate model
        luxury_model_path = Path('models/luxury_estate_model.joblib')
        if luxury_model_path.exists():
            self.luxury_model = LuxuryEstateModel.load(str(luxury_model_path))
            print("[OK] Luxury estate model loaded")
        else:
            print("[WARNING] Luxury estate model not found, will use standard model only")
            self.luxury_model = None

    def is_luxury_estate(self, property_data: dict) -> bool:
        """
        Classify if property is a luxury estate

        Criteria:
        - Price estimate > $750k
        - OR Living area > 7,000 sq ft
        - OR Lot size > 5 acres
        - OR Quality = 9/10
        """

        lot_area_sqft = property_data.get('LotArea', 0)
        acreage = lot_area_sqft / 43560

        living_area = property_data.get('GrLivArea', 0)
        quality = property_data.get('OverallQual', 7)

        return (
            acreage > 5 or
            living_area > 7000 or
            quality == 9 or
            (living_area > 5000 and quality >= 8)
        )

    def predict_price(self, address: str, real_features: dict = None) -> dict:
        """
        Predict house price using the appropriate model

        Returns:
        - Standard home prediction OR
        - Luxury estate prediction
        """

        print("\n" + "="*100)
        print(f"SMART PRICE PREDICTION: {address}")
        print("="*100)

        # Use provided features or get from assessor
        if real_features:
            property_data = real_features.copy()
        else:
            from house_price_prediction.address_to_price import AssessorAPIConnector
            property_data = AssessorAPIConnector.search_property_by_address(address)

        # Get school district
        district_name, school_rating = SchoolDistrictFeature.get_school_district_rating(address)

        # DETECT PROPERTY TYPE
        is_luxury = self.is_luxury_estate(property_data)

        print(f"\n[DETECTION] Property Classification:")
        print(f"  Living Area: {property_data.get('GrLivArea', 0):,.0f} sq ft")
        print(f"  Lot Size: {property_data.get('LotArea', 0):,.0f} sq ft ({property_data.get('LotArea', 0) / 43560:.1f} acres)")
        print(f"  Quality: {property_data.get('OverallQual', 7)}/10")
        print(f"  Type: {'LUXURY ESTATE' if is_luxury else 'STANDARD HOME'}")

        if is_luxury and self.luxury_model:
            # USE LUXURY MODEL
            print(f"\n[MODEL] Using LUXURY ESTATE model")

            # Build enhanced features
            enhanced_features = build_luxury_features(property_data)
            enhanced_features['SchoolDistrictRating'] = school_rating

            print(f"\n[FEATURES] Enhanced luxury features:")
            print(f"  Acreage: {enhanced_features.get('Acreage', 0):.1f}")
            print(f"  Luxury Tier: {enhanced_features.get('LuxuryTier', 'Unknown')}")
            print(f"  Land-to-Building Ratio: {enhanced_features.get('LandToBuilding', 0):.1f}")
            print(f"  Has Pool: {enhanced_features.get('HasPool', 0)}")
            print(f"  Has Tennis Court: {enhanced_features.get('HasTennisCore', 0)}")
            print(f"  Has Guest House: {enhanced_features.get('HasGuestHouse', 0)}")

            # Predict with luxury model
            luxury_price = self.luxury_model.predict(enhanced_features)

            # Add school district adjustment
            school_adjustment = (school_rating - 7.5) * 0.02 * luxury_price
            final_price = luxury_price + school_adjustment

            return {
                'address': address,
                'predicted_price': final_price,
                'model_used': 'Luxury Estate Model',
                'model_accuracy': '64.57% (R²)',
                'model_mae': '$1,161,336',
                'confidence': 64.57,
                'error_margin': 1161336,
                'error_margin_low': final_price - 1161336,
                'error_margin_high': final_price + 1161336,
                'all_features': enhanced_features,
                'school_district': district_name,
                'school_rating': school_rating,
                'property_type': 'Luxury Estate',
                'timestamp': __import__('datetime').datetime.now().isoformat()
            }
        else:
            # USE STANDARD MODEL
            print(f"\n[MODEL] Using STANDARD HOME model")

            property_data['SchoolDistrictRating'] = school_rating
            property_data['SchoolDistrict'] = district_name

            result = self.standard_pipeline.predict_price(address, real_features=property_data)
            result['model_used'] = 'Standard Home Model (LightGBM)'
            result['model_accuracy'] = '92.38% (R²)'
            result['model_mae'] = '$16,808'
            result['property_type'] = 'Standard Home'

            return result


# ============================================================================
# TEST WITH ACTUAL PROPERTY
# ============================================================================

def test_smart_pipeline():
    """Test the smart dual-model pipeline"""

    # The problematic luxury estate property
    TRADITIONS_DR_ACTUAL = {
        "address": "292 Traditions Dr, Alpharetta, GA 30004",
        "LotArea": 950 * 43560,        # 950 acres
        "OverallQual": 9,
        "OverallCond": 9,
        "YearBuilt": 2005,
        "YearRemodAdd": 2020,
        "GrLivArea": 11947,
        "FullBath": 5,
        "HalfBath": 1,
        "BedroomAbvGr": 5,
        "TotRmsAbvGrd": 18,
        "Fireplaces": 3,
        "GarageCars": 4,
        "GarageArea": 1800,
        "Neighborhood": "Suburban",
        "HouseStyle": "Contemporary",
    }

    ACTUAL_REDFIN_PRICE = 2695000

    print("\n" + "="*100)
    print("TESTING SMART DUAL-MODEL PIPELINE")
    print("="*100 + "\n")

    pipeline = SmartPricePredictionPipeline()
    result = pipeline.predict_price(
        TRADITIONS_DR_ACTUAL['address'],
        real_features=TRADITIONS_DR_ACTUAL
    )

    print("\n" + "="*100)
    print("RESULTS COMPARISON")
    print("="*100 + "\n")

    print(f"Property: {result['address']}")
    print(f"Property Type: {result['property_type']}")
    print(f"Model Used: {result['model_used']}")
    print(f"Model Accuracy: {result['model_accuracy']}")

    print(f"\n{'Metric':<35} {'Model Prediction':>20} {'Actual (Redfin)':>20}")
    print("-"*75)
    print(f"{'Price':<35} ${result['predicted_price']:>18,.0f} ${ACTUAL_REDFIN_PRICE:>18,.0f}")

    error = ACTUAL_REDFIN_PRICE - result['predicted_price']
    pct_error = (error / ACTUAL_REDFIN_PRICE) * 100

    print(f"{'Difference':<35} ${error:>18,.0f} ({pct_error:>6.1f}%)")

    print(f"\nLuxury Property Features:")
    print(f"  Lot Size: 950 acres (41.38M sq ft)")
    print(f"  Living Area: 11,947 sq ft")
    print(f"  Bedrooms: 5 | Bathrooms: 5.5")
    print(f"  Quality: 9/10 | Condition: 9/10")
    print(f"  School District: {result['school_district']} ({result['school_rating']:.1f}/10)")

    print(f"\n{'='*100}\n")

    # Show improvement
    print("\n" + "="*100)
    print("IMPROVEMENT OVER PREVIOUS MODEL")
    print("="*100 + "\n")

    print(f"Previous model estimate:  $716,402")
    print(f"Luxury model estimate:    ${result['predicted_price']:,.0f}")
    print(f"Actual Redfin price:      ${ACTUAL_REDFIN_PRICE:,.0f}")

    old_error_pct = ((2695000 - 716402) / 2695000) * 100
    new_error_pct = abs((ACTUAL_REDFIN_PRICE - result['predicted_price']) / ACTUAL_REDFIN_PRICE * 100)

    print(f"\nPrevious model error: {old_error_pct:.1f}%")
    print(f"Luxury model error:   {new_error_pct:.1f}%")
    print(f"Improvement:          {old_error_pct - new_error_pct:.1f} percentage points")

    print(f"\n{'='*100}\n")


if __name__ == "__main__":
    test_smart_pipeline()
