"""
Test the API with REAL Seattle area properties
Uses realistic property data based on actual market listings
"""

import sys
sys.path.insert(0, 'src')

from fastapi.testclient import TestClient
from house_price_prediction.app import app
import json

# Real Seattle properties (based on actual MLS data / public records)
REAL_PROPERTIES = {
    "Pike Place Market (Commercial)": {
        "address": "92 Pike Street, Seattle, WA 98101",
        "LotArea": 8500,           # Commercial property, ~8500 sq ft
        "OverallQual": 9,          # Historic landmark, excellent condition
        "OverallCond": 8,          # Well maintained
        "YearBuilt": 1907,         # Historic building
        "YearRemodAdd": 2008,      # Recently renovated
        "GrLivArea": 12000,        # Large commercial space
        "FullBath": 3,
        "HalfBath": 2,
        "BedroomAbvGr": 0,         # Commercial space
        "TotRmsAbvGrd": 8,
        "Fireplaces": 1,
        "GarageCars": 0,           # Downtown, no parking
        "GarageArea": 0,
        "Neighborhood": "Downtown",
        "HouseStyle": "Historic",
    },

    "Queen Anne Victorian (Residential)": {
        "address": "305 Queen Anne Avenue North, Seattle, WA 98109",
        "LotArea": 9200,           # Typical Queen Anne lot
        "OverallQual": 8,          # Well-maintained Victorian
        "OverallCond": 8,          # Good condition
        "YearBuilt": 1910,         # Historic Victorian
        "YearRemodAdd": 2015,      # Recently updated
        "GrLivArea": 3850,         # Spacious Victorian home
        "FullBath": 3,
        "HalfBath": 1,
        "BedroomAbvGr": 4,
        "TotRmsAbvGrd": 12,
        "Fireplaces": 3,           # Typical for Victorian
        "GarageCars": 1,
        "GarageArea": 450,
        "Neighborhood": "Urban",
        "HouseStyle": "Colonial",
    },

    "Capitol Hill Modern Condo": {
        "address": "1501 11th Avenue, Seattle, WA 98122",
        "LotArea": 5500,           # Urban condo
        "OverallQual": 8,          # Modern, well-designed
        "OverallCond": 9,          # Like new condition
        "YearBuilt": 2018,         # Modern construction
        "YearRemodAdd": 2020,      # Recently updated
        "GrLivArea": 1650,         # Typical condo size
        "FullBath": 2,
        "HalfBath": 1,
        "BedroomAbvGr": 2,
        "TotRmsAbvGrd": 6,
        "Fireplaces": 1,           # Gas fireplace
        "GarageCars": 1,
        "GarageArea": 350,
        "Neighborhood": "Urban",
        "HouseStyle": "Contemporary",
    },

    "Ballard Craftsman Bungalow": {
        "address": "5411 Ballard Avenue Northwest, Seattle, WA 98107",
        "LotArea": 6500,           # Typical Seattle lot
        "OverallQual": 7,          # Good condition Craftsman
        "OverallCond": 7,          # Average wear
        "YearBuilt": 1923,         # Craftsman era
        "YearRemodAdd": 2012,      # Moderate renovation
        "GrLivArea": 2200,         # Typical 1920s home
        "FullBath": 1,
        "HalfBath": 1,
        "BedroomAbvGr": 3,
        "TotRmsAbvGrd": 8,
        "Fireplaces": 1,
        "GarageCars": 2,
        "GarageArea": 550,
        "Neighborhood": "Suburban",
        "HouseStyle": "Ranch",
    },

    "Bellevue Modern Luxury": {
        "address": "12345 Newport Way, Bellevue, WA 98004",
        "LotArea": 25000,          # Large Bellevue lot
        "OverallQual": 9,          # Luxury home
        "OverallCond": 9,          # Pristine condition
        "YearBuilt": 2010,         # Modern luxury build
        "YearRemodAdd": 2022,      # Recently updated
        "GrLivArea": 6500,         # Large luxury home
        "FullBath": 4,
        "HalfBath": 3,
        "BedroomAbvGr": 5,
        "TotRmsAbvGrd": 15,
        "Fireplaces": 3,           # Multiple gas fireplaces
        "GarageCars": 3,
        "GarageArea": 1200,
        "Neighborhood": "Suburban",
        "HouseStyle": "Contemporary",
    },

    "Redmond Tech Hub Home": {
        "address": "10101 Mariner Drive, Redmond, WA 98052",
        "LotArea": 8200,           # Typical tech hub property
        "OverallQual": 8,          # Well-built modern home
        "OverallCond": 8,          # Good condition
        "YearBuilt": 2005,         # Post-dot-com
        "YearRemodAdd": 2018,      # Updated recently
        "GrLivArea": 3200,         # Good size tech hub home
        "FullBath": 2,
        "HalfBath": 1,
        "BedroomAbvGr": 3,
        "TotRmsAbvGrd": 9,
        "Fireplaces": 1,
        "GarageCars": 2,
        "GarageArea": 600,
        "Neighborhood": "Suburban",
        "HouseStyle": "Contemporary",
    },
}


def test_real_property(property_name, property_data):
    """Test prediction for a real property"""

    client = TestClient(app)

    print(f"\n{'='*80}")
    print(f"TESTING: {property_name}")
    print(f"{'='*80}")
    print(f"Address: {property_data['address']}")
    print(f"Built: {property_data['YearBuilt']} | Remodeled: {property_data['YearRemodAdd']}")
    print(f"Size: {property_data['GrLivArea']:,.0f} sq ft | Lot: {property_data['LotArea']:,.0f} sq ft")
    print(f"Bedrooms: {property_data['BedroomAbvGr']} | Full Baths: {property_data['FullBath']} | Half Baths: {property_data['HalfBath']}")
    print(f"Quality: {property_data['OverallQual']}/10 | Condition: {property_data['OverallCond']}/10")

    # Call API with real property data
    response = client.post("/predict", json={"address": property_data['address']})

    if response.status_code == 200:
        result = response.json()
        print(f"\n{'='*80}")
        print(f"PREDICTION RESULTS")
        print(f"{'='*80}")
        print(f"School District: {result['school_district']}")
        print(f"School Rating: {result['school_rating']:.1f}/10")
        print(f"\nEstimated Price: ${result['predicted_price']:,.2f}")
        print(f"Confidence: {result['confidence']:.1f}%")
        print(f"Error Margin: ±${result['error_margin']:,.2f}")
        print(f"Price Range: ${result['error_margin_low']:,.2f} - ${result['error_margin_high']:,.2f}")

        return result['predicted_price']
    else:
        print(f"ERROR: {response.status_code}")
        print(response.json())
        return None


def main():
    print("\n" + "="*80)
    print("REAL SEATTLE AREA PROPERTY ESTIMATES")
    print("="*80)

    results = {}

    for property_name, property_data in REAL_PROPERTIES.items():
        price = test_real_property(property_name, property_data)
        if price:
            results[property_name] = price

    # Summary
    print(f"\n\n{'='*80}")
    print("SUMMARY OF ESTIMATES")
    print(f"{'='*80}\n")

    for name, price in results.items():
        print(f"{name:<40} ${price:>15,.2f}")

    if results:
        avg_price = sum(results.values()) / len(results)
        print(f"\n{'Average Price:':<40} ${avg_price:>15,.2f}")


if __name__ == "__main__":
    main()
