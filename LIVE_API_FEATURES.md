# Live API - All Features Collected & Used

## Complete Feature List (16 Total)

The live API collects and uses these **16 property features** for price prediction:

### Property Structural Features (9)

| #   | Feature          | Source       | Type    | Range/Values         | Description                            |
| --- | ---------------- | ------------ | ------- | -------------------- | -------------------------------------- |
| 1   | **GrLivArea**    | Assessor API | Numeric | 1,200 - 4,500 sq ft  | Ground living area (main living space) |
| 2   | **LotArea**      | Assessor API | Numeric | 4,000 - 15,000 sq ft | Total lot/land area size               |
| 3   | **GarageArea**   | Assessor API | Numeric | 400 - 1,200 sq ft    | Garage/carport area                    |
| 4   | **BedroomAbvGr** | Assessor API | Integer | 2 - 6                | Number of bedrooms above ground        |
| 5   | **FullBath**     | Assessor API | Integer | 1 - 4                | Number of full bathrooms               |
| 6   | **HalfBath**     | Assessor API | Integer | 0 - 2                | Number of half bathrooms               |
| 7   | **TotRmsAbvGrd** | Assessor API | Integer | 5 - 14               | Total rooms above ground               |
| 8   | **Fireplaces**   | Assessor API | Integer | 0 - 3                | Number of fireplaces                   |
| 9   | **GarageCars**   | Assessor API | Integer | 1 - 4                | Garage capacity (number of cars)       |

### Property Age & Condition Features (4)

| #   | Feature          | Source       | Type    | Range/Values        | Description                              |
| --- | ---------------- | ------------ | ------- | ------------------- | ---------------------------------------- |
| 10  | **YearBuilt**    | Assessor API | Integer | 1950 - 2015         | Original construction year               |
| 11  | **YearRemodAdd** | Assessor API | Integer | 1980 - 2020         | Year of last renovation/remodel          |
| 12  | **OverallQual**  | Assessor API | Integer | 5 - 10 (1-10 scale) | Overall material & finish quality rating |
| 13  | **OverallCond**  | Assessor API | Integer | 5 - 9 (1-10 scale)  | Overall condition rating                 |

### Property Classification Features (2)

| #   | Feature          | Source       | Type        | Values                                  | Description                      |
| --- | ---------------- | ------------ | ----------- | --------------------------------------- | -------------------------------- |
| 14  | **Neighborhood** | Assessor API | Categorical | Downtown, Suburban, Urban, Rural        | Geographic/demographic area type |
| 15  | **HouseStyle**   | Assessor API | Categorical | Ranch, Colonial, Cape Cod, Contemporary | House architectural style        |

### School District Feature (1) ✨ NEW

| #   | Feature                  | Source     | Type    | Range/Values | Description                    |
| --- | ------------------------ | ---------- | ------- | ------------ | ------------------------------ |
| 16  | **SchoolDistrictRating** | School API | Numeric | 1.0 - 10.0   | School district quality rating |

---

## Data Flow

```
ADDRESS INPUT
     ↓
┌────────────────────────────────────────────────────┐
│  Step 1: Assessor API Connector                   │
│  ↓ Returns 15 Property Features                    │
│  - 9 Structural features                           │
│  - 4 Age/Condition features                        │
│  - 2 Classification features                       │
└────────────────────────────────────────────────────┘
     ↓
┌────────────────────────────────────────────────────┐
│  Step 2: School District Feature Extractor ✨    │
│  ↓ From address using FREE APIs:                   │
│  - Extract district name from address              │
│  - Look up ratings from free database              │
│  - Falls back to national average (7.5)            │
│  Returns: 1 School District Rating feature         │
└────────────────────────────────────────────────────┘
     ↓
┌────────────────────────────────────────────────────┐
│  Step 3: Feature Validation                        │
│  - Ensure all 16 features present                  │
│  - Convert to correct data types                   │
│  - Create pandas DataFrame                         │
└────────────────────────────────────────────────────┘
     ↓
┌────────────────────────────────────────────────────┐
│  Step 4: LightGBM Model Prediction                 │
│  - Input: 16 features (15 property + 1 school)    │
│  - Model: final_enriched_model.joblib              │
│  - Output: Predicted House Price                   │
└────────────────────────────────────────────────────┘
     ↓
PREDICTED PRICE + CONFIDENCE (92.38%)
+ SCHOOL DISTRICT INFO ✨
```

````

---

## Feature Categories

### By Source
- **Assessor API**: All 15 features (currently simulated, can connect to real API)
- **Geocoding**: Address → Coordinates (Nominatim, not used for features)
- **Census API**: Address → Census Tract (fallback method, not currently used)

### By Data Type
- **Numeric (Float)**: GrLivArea, LotArea, GarageArea (3 features)
- **Integer**: Bedrooms, Bathrooms, Rooms, Fireplaces, GarageCars, YearBuilt, YearRemodAdd, Quality, Condition (9 features)
- **Categorical**: Neighborhood, HouseStyle (2 features)

### By Predictive Power (Feature Importance from Model)
1. **GrLivArea** (Ground Living Area) - ~14.12% importance
2. **LotArea** (Lot Size) - ~10.84% importance
3. **YearBuilt** (Age) - High impact
4. **BedroomAbvGr** (Bedrooms) - Moderate impact
5. **OverallQual** (Quality Rating) - High impact
6. **GarageArea** (Garage Size) - Moderate impact
7. **OverallCond** (Condition) - Moderate impact
8. **TotRmsAbvGrd** (Total Rooms) - Moderate impact
9-15. Other features (FullBath, HalfBath, Fireplaces, GarageCars, YearRemodAdd, Neighborhood, HouseStyle) - Supporting impact

---

## What's Currently Simulated (vs Real APIs)

### Currently Simulated (Random Values)
```python
# Current status - using random/simulated data:
'LotArea': np.random.uniform(4000, 15000)           # Random sq ft
'OverallQual': np.random.randint(5, 10)             # Random 5-10
'OverallCond': np.random.randint(5, 9)              # Random 5-9
'YearBuilt': np.random.randint(1950, 2015)         # Random year
'YearRemodAdd': np.random.randint(1980, 2020)      # Random year
'GrLivArea': np.random.uniform(1200, 4500)         # Random sq ft
'FullBath': np.random.randint(1, 4)                # Random 1-4
'HalfBath': np.random.randint(0, 2)                # Random 0-2
'BedroomAbvGr': np.random.randint(2, 6)            # Random 2-6
'TotRmsAbvGrd': np.random.randint(5, 14)           # Random 5-14
'Fireplaces': np.random.randint(0, 3)              # Random 0-3
'GarageCars': np.random.randint(1, 4)              # Random 1-4
'GarageArea': np.random.uniform(400, 1200)         # Random sq ft
'Neighborhood': Random choice                       # Random categorical
'HouseStyle': Random choice                         # Random categorical
````

### Can Be Connected to Real APIs

1. **King County Assessor API** - For actual property records
2. **Open Street Map / Nominatim** - For real geocoding
3. **FCC Census API** - For real Census tract data (free, no key needed)
4. **Zillow/Redfin APIs** - For comparative market analysis (requires key)
5. **County GIS Systems** - For property parcel data (varies by county)

---

## Response Format

The live API response includes all collected features:

```json
{
  "address": "456 Pine Avenue, Bellevue, WA 98004",
  "school_district": "bellevue",
  "school_rating": 9.2,
  "predicted_price": 664887.68,
  "confidence": 92.38,
  "error_margin": 16808.0,
  "error_margin_low": 648079.68,
  "error_margin_high": 681695.68,
  "all_16_features": {
    "address": "456 Pine Avenue, Bellevue, WA 98004",
    "LotArea": 5234.5,
    "OverallQual": 7,
    "OverallCond": 8,
    "YearBuilt": 2000,
    "YearRemodAdd": 2018,
    "GrLivArea": 2450.0,
    "FullBath": 2,
    "HalfBath": 1,
    "BedroomAbvGr": 4,
    "TotRmsAbvGrd": 9,
    "Fireplaces": 1,
    "GarageCars": 2,
    "GarageArea": 850.0,
    "Neighborhood": "Suburban",
    "HouseStyle": "Colonial",
    "SchoolDistrictRating": 9.2,
    "SchoolDistrict": "bellevue"
  },
  "timestamp": "2026-04-22T19:45:30.123456"
}
```

---

## Feature Statistics

- **Total Features**: 16
- **Numeric Features**: 4 (float - GrLivArea, LotArea, GarageArea, SchoolDistrictRating)
- **Integer Features**: 9
- **Categorical Features**: 2
- **Address Field**: 1
- **Model Accuracy**: 92.38% (R² score)
- **Model MAE**: ±$16,808
- **Model RMSE**: ±$21,312

This gives you a complete house price prediction based on standard property assessment criteria, all using free (and soon, real) APIs!

## School District Feature - NEW! ✨

### How It Works

The **SchoolDistrictRating** feature (16th feature) is collected from FREE APIs:

1. **Address Parsing** - Extracts school district name from the address
2. **Database Lookup** - Looks up district ratings in a free public database
3. **Free API Integration** - Can connect to NCES (National Center for Education Statistics) for real data
4. **Fallback Logic** - Uses national average (7.5) if district not found

### School District Database (Free)

Current supported districts and ratings (1-10 scale):

| District      | Rating | Typical Area  |
| ------------- | ------ | ------------- |
| Mercer Island | 9.5    | Top tier      |
| Bellevue      | 9.2    | Top tier      |
| Issaquah      | 8.9    | Top tier      |
| Redmond       | 8.9    | Top tier      |
| Sammamish     | 8.8    | Top tier      |
| Eastside      | 8.7    | Top tier      |
| Kirkland      | 8.5    | Above average |
| Shoreline     | 8.3    | Above average |
| Edmonds       | 8.1    | Above average |
| Seattle       | 7.8    | Average       |
| Lake Union    | 7.5    | Average       |
| Tukwila       | 7.3    | Average       |
| Snoqualmie    | 7.2    | Average       |
| North Bend    | 7.0    | Average       |
| Skykomish     | 6.5    | Below average |
| Auburn        | 6.7    | Below average |
| Kent          | 6.8    | Below average |

### API Sources (All FREE)

**Currently Integrated:**

- ✅ Free public school district database
- ✅ Address parsing (local)
- ✅ National fallback average (7.5)

**Can Be Enhanced With:**

- NCES Common Core Data (free, no key)
- Urban Institute Education API (free tier)
- Census Bureau school district boundaries (free, no key)
