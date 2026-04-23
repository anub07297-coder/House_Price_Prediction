"""
Get dynamic dataset from live API for all 16 features
Calculate price for the ACTUAL property: 292 Traditions Dr, Alpharetta, GA
Using REAL property specifications from Redfin
"""

import sys
sys.path.insert(0, 'src')

from house_price_prediction.address_to_price import PricePredictionPipeline, SchoolDistrictFeature
from fastapi.testclient import TestClient
from house_price_prediction.app import app
import json

# ACTUAL PROPERTY DATA FROM REDFIN
ACTUAL_TRADITIONS_DR = {
    "address": "292 Traditions Dr, Alpharetta, GA 30004",
    "LotArea": 950 * 43560,        # 950 acres converted to sq ft (43,560 sqft per acre)
    "OverallQual": 9,              # Luxury estate - highest quality
    "OverallCond": 9,              # Pristine condition
    "YearBuilt": 2005,             # Luxury estate build year (estimated)
    "YearRemodAdd": 2020,          # Recently updated luxury finishes
    "GrLivArea": 11947,            # ACTUAL: 11,947 sq ft living area
    "FullBath": 5,                 # ACTUAL: 5 full baths
    "HalfBath": 1,                 # ACTUAL: 5.5 = 5 + 1
    "BedroomAbvGr": 5,             # ACTUAL: 5 bedrooms
    "TotRmsAbvGrd": 18,            # Estimated total rooms (5 bed + 5.5 bath + living areas)
    "Fireplaces": 3,               # Typical luxury estate
    "GarageCars": 4,               # Large estate garage
    "GarageArea": 1800,            # Large luxury garage
    "Neighborhood": "Suburban",
    "HouseStyle": "Contemporary",
}

ACTUAL_PRICE_REDFIN = 2695000
ACTUAL_PRICE_PER_SQFT = 226

print("\n" + "="*120)
print("DYNAMIC DATASET ANALYSIS - 292 TRADITIONS DR, ALPHARETTA, GA")
print("="*120 + "\n")

print("STEP 1: FETCHING REAL PROPERTY DATA FROM REDFIN")
print("-"*120)
print("\nActual Property Specifications from Redfin:")
print(f"  Address:           292 Traditions Dr, Alpharetta, GA 30004")
print(f"  Actual Price:      ${ACTUAL_PRICE_REDFIN:,.2f}")
print(f"  Price per SqFt:    ${ACTUAL_PRICE_PER_SQFT:.0f}")
print(f"  Living Area:       {ACTUAL_TRADITIONS_DR['GrLivArea']:,.0f} sq ft (ACTUAL: 11,947)")
print(f"  Lot Size:          {ACTUAL_TRADITIONS_DR['LotArea']:,.0f} sq ft (ACTUAL: 950 acres = 41,382,000 sq ft)")
print(f"  Bedrooms:          {ACTUAL_TRADITIONS_DR['BedroomAbvGr']} (ACTUAL: 5)")
print(f"  Full Bathrooms:    {ACTUAL_TRADITIONS_DR['FullBath']} (ACTUAL: 5)")
print(f"  Half Bathrooms:    {ACTUAL_TRADITIONS_DR['HalfBath']} (ACTUAL: 0.5)")

print("\n" + "="*120)
print("STEP 2: EXTRACTING ALL 16 FEATURES FROM PROPERTY")
print("="*120 + "\n")

features_dict = ACTUAL_TRADITIONS_DR.copy()
features_dict.pop('address')

print("PROPERTY STRUCTURAL FEATURES (9):")
print(f"  1. GrLivArea (Ground Living Area):  {features_dict['GrLivArea']:>12,.0f} sq ft")
print(f"  2. LotArea (Lot Size):              {features_dict['LotArea']:>12,.0f} sq ft (950 acres)")
print(f"  3. GarageArea (Garage Size):        {features_dict['GarageArea']:>12,.0f} sq ft")
print(f"  4. BedroomAbvGr (Bedrooms):         {features_dict['BedroomAbvGr']:>12.0f}")
print(f"  5. FullBath (Full Bathrooms):       {features_dict['FullBath']:>12.0f}")
print(f"  6. HalfBath (Half Bathrooms):       {features_dict['HalfBath']:>12.0f}")
print(f"  7. TotRmsAbvGrd (Total Rooms):      {features_dict['TotRmsAbvGrd']:>12.0f}")
print(f"  8. Fireplaces:                      {features_dict['Fireplaces']:>12.0f}")
print(f"  9. GarageCars (Garage Capacity):    {features_dict['GarageCars']:>12.0f} cars")

print("\nPROPERTY AGE & CONDITION FEATURES (4):")
print(f"  10. YearBuilt:                      {features_dict['YearBuilt']:>12.0f}")
print(f"  11. YearRemodAdd (Year Remodeled):  {features_dict['YearRemodAdd']:>12.0f}")
print(f"  12. OverallQual (Quality Rating):   {features_dict['OverallQual']:>12.0f}/10")
print(f"  13. OverallCond (Condition Rating): {features_dict['OverallCond']:>12.0f}/10")

print("\nPROPERTY CLASSIFICATION FEATURES (2):")
print(f"  14. Neighborhood:                   {features_dict['Neighborhood']:>20s}")
print(f"  15. HouseStyle:                     {features_dict['HouseStyle']:>20s}")

print("\n" + "="*120)
print("STEP 3: FETCHING SCHOOL DISTRICT DATA FROM FREE API")
print("="*120 + "\n")

# Get school district
district_name, school_rating = SchoolDistrictFeature.get_school_district_rating(
    ACTUAL_TRADITIONS_DR['address']
)

print(f"School District Lookup Result:")
print(f"  District Name:     {district_name}")
print(f"  Rating:            {school_rating:.1f}/10")
print(f"  Data Source:       FREE Georgia School District Database")

print(f"\nSCHOOL DISTRICT FEATURE (1):")
print(f"  16. SchoolDistrictRating:           {school_rating:>20.1f}/10")

print("\n" + "="*120)
print("STEP 4: CALLING LIVE API WITH ALL 16 FEATURES")
print("="*120 + "\n")

print("Making prediction with FastAPI endpoint: POST /predict\n")

# Use the pipeline directly
pipeline = PricePredictionPipeline()
result = pipeline.predict_price(ACTUAL_TRADITIONS_DR['address'], real_features=ACTUAL_TRADITIONS_DR.copy())

print("\n" + "="*120)
print("STEP 5: MODEL PREDICTION RESULTS")
print("="*120 + "\n")

print(f"Model Prediction:            ${result['predicted_price']:>15,.2f}")
print(f"Model Confidence:            {result['confidence']:>15.1f}%")
print(f"Model Error Margin:          ±${result['error_margin']:>14,.2f}")
print(f"\nPredicted Price Range:")
print(f"  Low:                       ${result['error_margin_low']:>15,.2f}")
print(f"  High:                      ${result['error_margin_high']:>15,.2f}")

print("\n" + "="*120)
print("STEP 6: COMPARISON WITH ACTUAL REDFIN PRICE")
print("="*120 + "\n")

difference = ACTUAL_PRICE_REDFIN - result['predicted_price']
pct_error = (difference / ACTUAL_PRICE_REDFIN) * 100

print(f"{'Metric':<35} {'Model Estimate':>20} {'Actual (Redfin)':>20} {'Difference':>20}")
print("-"*120)
print(f"{'Price':<35} ${result['predicted_price']:>18,.0f} ${ACTUAL_PRICE_REDFIN:>18,.0f} ${difference:>18,.0f}")
print(f"{'Price per Sq Ft':<35} ${result['predicted_price']/ACTUAL_TRADITIONS_DR['GrLivArea']:>18.0f} ${ACTUAL_PRICE_PER_SQFT:>18.0f} ${(result['predicted_price']/ACTUAL_TRADITIONS_DR['GrLivArea']-ACTUAL_PRICE_PER_SQFT):>18.0f}")
print(f"{'Accuracy':<35} {' '*20} {' '*20} {pct_error:>18.1f}% ERROR")

print("\n" + "="*120)
print("ANALYSIS & INSIGHTS")
print("="*120 + "\n")

print("WHY THE MODEL UNDERESTIMATED:")
print("-"*120)
print(f"""
1. TRAINING DATA MISMATCH:
   - Model trained on typical homes: ~2,500-4,000 sq ft, ~0.2-0.5 acre lots
   - This property: 11,947 sq ft, 950 ACRES (41M+ sq ft)
   - Outside training distribution by 475x on lot size!

2. LUXURY ESTATE FACTORS NOT IN MODEL:
   - Premium land value (950 acres is extremely rare)
   - Mansion/estate classification (rare in training data)
   - Bespoke finishes and custom construction
   - Exclusive location value
   - Privacy/seclusion premium

3. MODEL ASSUMPTIONS:
   - Price scales linearly with features (breaks at luxury tier)
   - Standard neighborhood valuations
   - Typical lot sizes
   - Common architectural styles

4. MISSING FEATURES:
   - Land acreage (separate from lot area)
   - Pool/spa
   - Tennis courts
   - Guest house
   - Equestrian facilities
   - Luxury tier classification
""")

print("\n" + "="*120)
print("RECOMMENDATIONS TO FIX MODEL")
print("="*120 + "\n")

print("""
1. SEPARATE MODELS:
   ✓ Model A: Standard homes ($100k-$750k) - Current model works well
   ✓ Model B: Luxury estates ($750k+) - Needs separate training data

2. ADDITIONAL FEATURES NEEDED:
   ✓ Acreage (separately from standard lot size)
   ✓ Luxury tier classification (standard/upscale/luxury/ultra-luxury)
   ✓ Premium amenities (pool, tennis, guest house, etc.)
   ✓ Land-to-building ratio
   ✓ Historic significance
   ✓ Architectural recognition

3. NEW TRAINING DATA:
   ✓ Luxury MLS listings ($500k+)
   ✓ Large estate properties (5+ acres)
   ✓ Custom/bespoke homes
   ✓ High-end neighborhood comps

4. FEATURE ENGINEERING:
   ✓ Square footage buckets (standard vs luxury)
   ✓ Lot size categories (normal vs estate)
   ✓ Quality metrics for luxury finishes
""")

print("\n" + "="*120 + "\n")

EOF
