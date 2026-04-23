"""
Test the API with REAL Georgia single-family homes
Uses realistic property data for Georgia properties
"""

import sys
sys.path.insert(0, 'src')

from house_price_prediction.address_to_price import SchoolDistrictFeature, PricePredictionPipeline

# Add Georgia school districts to the database
SchoolDistrictFeature.SCHOOL_DISTRICT_DB.update({
    # Atlanta area (Fulton County)
    'atlanta': 7.1,
    'buckhead': 8.2,
    'midtown': 6.9,
    'sandy springs': 8.5,
    'dunwoody': 8.3,
    'johns creek': 8.7,
    'alpharetta': 8.4,

    # Cobb County
    'marietta': 7.8,
    'kennesaw': 7.6,
    'acworth': 7.5,

    # Gwinnett County
    'lawrenceville': 7.9,
    'buford': 7.7,
    'snellville': 7.8,

    # DeKalb County
    'decatur': 8.1,
    'stone mountain': 7.4,
    'lithonia': 7.3,

    # Other areas
    'peachtree city': 8.6,
    'savannah': 7.2,
    'augusta': 6.8,
})

# Real Georgia single-family homes
GEORGIA_PROPERTIES = {
    "Buckhead Atlanta (Luxury)": {
        "address": "3250 Peachtree Road NE, Atlanta, GA 30305",
        "LotArea": 12000,
        "OverallQual": 9,
        "OverallCond": 9,
        "YearBuilt": 2012,
        "YearRemodAdd": 2022,
        "GrLivArea": 5200,
        "FullBath": 4,
        "HalfBath": 2,
        "BedroomAbvGr": 5,
        "TotRmsAbvGrd": 14,
        "Fireplaces": 2,
        "GarageCars": 3,
        "GarageArea": 1100,
        "Neighborhood": "Urban",
        "HouseStyle": "Contemporary",
    },

    "Sandy Springs Colonial": {
        "address": "405 Blackland Road NW, Sandy Springs, GA 30342",
        "LotArea": 18500,
        "OverallQual": 8,
        "OverallCond": 8,
        "YearBuilt": 1998,
        "YearRemodAdd": 2018,
        "GrLivArea": 4100,
        "FullBath": 3,
        "HalfBath": 2,
        "BedroomAbvGr": 4,
        "TotRmsAbvGrd": 12,
        "Fireplaces": 2,
        "GarageCars": 3,
        "GarageArea": 950,
        "Neighborhood": "Suburban",
        "HouseStyle": "Colonial",
    },

    "Johns Creek Modern Farmhouse": {
        "address": "10200 Hillwood Parkway, Johns Creek, GA 30097",
        "LotArea": 22000,
        "OverallQual": 9,
        "OverallCond": 9,
        "YearBuilt": 2015,
        "YearRemodAdd": 2023,
        "GrLivArea": 4800,
        "FullBath": 3,
        "HalfBath": 2,
        "BedroomAbvGr": 4,
        "TotRmsAbvGrd": 13,
        "Fireplaces": 2,
        "GarageCars": 3,
        "GarageArea": 1050,
        "Neighborhood": "Suburban",
        "HouseStyle": "Contemporary",
    },

    "Marietta Craftsman": {
        "address": "2847 South Cobb Drive, Marietta, GA 30060",
        "LotArea": 8500,
        "OverallQual": 7,
        "OverallCond": 7,
        "YearBuilt": 1995,
        "YearRemodAdd": 2015,
        "GrLivArea": 2400,
        "FullBath": 2,
        "HalfBath": 1,
        "BedroomAbvGr": 3,
        "TotRmsAbvGrd": 10,
        "Fireplaces": 1,
        "GarageCars": 2,
        "GarageArea": 550,
        "Neighborhood": "Suburban",
        "HouseStyle": "Ranch",
    },

    "Decatur Historic Craftsman": {
        "address": "632 East Lake Drive, Decatur, GA 30030",
        "LotArea": 7200,
        "OverallQual": 8,
        "OverallCond": 8,
        "YearBuilt": 1935,
        "YearRemodAdd": 2019,
        "GrLivArea": 2650,
        "FullBath": 2,
        "HalfBath": 1,
        "BedroomAbvGr": 3,
        "TotRmsAbvGrd": 10,
        "Fireplaces": 2,
        "GarageCars": 1,
        "GarageArea": 350,
        "Neighborhood": "Urban",
        "HouseStyle": "Colonial",
    },

    "Alpharetta Family Home": {
        "address": "5195 Abbotts Cove Drive, Alpharetta, GA 30022",
        "LotArea": 10500,
        "OverallQual": 7,
        "OverallCond": 8,
        "YearBuilt": 2005,
        "YearRemodAdd": 2020,
        "GrLivArea": 3200,
        "FullBath": 2,
        "HalfBath": 1,
        "BedroomAbvGr": 4,
        "TotRmsAbvGrd": 11,
        "Fireplaces": 1,
        "GarageCars": 2,
        "GarageArea": 600,
        "Neighborhood": "Suburban",
        "HouseStyle": "Contemporary",
    },

    "Peachtree City Golf Course": {
        "address": "215 Smoketree Lane, Peachtree City, GA 30269",
        "LotArea": 16000,
        "OverallQual": 8,
        "OverallCond": 8,
        "YearBuilt": 2008,
        "YearRemodAdd": 2021,
        "GrLivArea": 3800,
        "FullBath": 3,
        "HalfBath": 1,
        "BedroomAbvGr": 4,
        "TotRmsAbvGrd": 12,
        "Fireplaces": 2,
        "GarageCars": 2,
        "GarageArea": 700,
        "Neighborhood": "Suburban",
        "HouseStyle": "Contemporary",
    },
}


def main():
    print("\n" + "="*100)
    print("REAL GEORGIA SINGLE-FAMILY HOME PRICE ESTIMATES")
    print("="*100 + "\n")

    pipeline = PricePredictionPipeline()
    results = []

    for prop_name, features in GEORGIA_PROPERTIES.items():
        print(f"\n{'-'*100}")
        print(f"{prop_name}")
        print(f"{'-'*100}")

        addr = features.pop('address')
        print(f"Address: {addr}")
        print(f"  Details: {features['BedroomAbvGr']} bed, {features['FullBath']} full bath, {features['GrLivArea']:,.0f} sq ft")
        print(f"  Built: {features['YearBuilt']} | Quality: {features['OverallQual']}/10 | Condition: {features['OverallCond']}/10")
        print(f"  Lot Size: {features['LotArea']:,.0f} sq ft")

        result = pipeline.predict_price(addr, real_features=features)

        print(f"\n  School District: {result['school_district']} ({result['school_rating']:.1f}/10)")
        print(f"  ESTIMATED PRICE: ${result['predicted_price']:,.2f}")
        print(f"  Confidence: {result['confidence']:.1f}%")
        print(f"  Price Range: ${result['error_margin_low']:,.2f} - ${result['error_margin_high']:,.2f}")

        results.append({
            'name': prop_name,
            'address': addr,
            'price': result['predicted_price'],
            'district': result['school_district'],
            'rating': result['school_rating'],
            'beds': features['BedroomAbvGr'],
            'sqft': features['GrLivArea']
        })

    # Summary
    print(f"\n\n{'='*100}")
    print("SUMMARY - GEORGIA SINGLE-FAMILY HOMES")
    print(f"{'='*100}\n")

    print(f"{'Property':<35} {'City/District':<18} {'Rating':<8} {'Est. Price':<18} {'Price/SqFt':<15}")
    print(f"{'-'*94}")

    for r in results:
        price_sqft = r['price'] / r['sqft'] if r['sqft'] > 0 else 0
        print(f"{r['name']:<35} {r['district']:<18} {r['rating']:<8.1f} ${r['price']:>15,.0f}  ${price_sqft:>12,.0f}")

    print(f"\n{'-'*94}")
    avg = sum(r['price'] for r in results) / len(results)
    avg_sqft = sum(r['sqft'] for r in results) / len(results) if results else 0
    avg_price_sqft = avg / avg_sqft if avg_sqft > 0 else 0

    print(f"{'AVERAGE':<35} {' '*18} {' '*8} ${avg:>15,.0f}  ${avg_price_sqft:>12,.0f}")

    print(f"\n{'='*100}\n")

    # Price insights
    print("KEY INSIGHTS:")
    print(f"  Highest: {max(results, key=lambda x: x['price'])['name']} - ${max(r['price'] for r in results):,.0f}")
    print(f"  Lowest: {min(results, key=lambda x: x['price'])['name']} - ${min(r['price'] for r in results):,.0f}")
    print(f"  Average: ${avg:,.0f}")
    print(f"  Average Price/SqFt: ${avg_price_sqft:.0f}")
    print()


if __name__ == "__main__":
    main()
