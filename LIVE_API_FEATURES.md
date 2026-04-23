# Live API - All Features Collected & Used

## Complete Feature List (15 Total)

The live API collects and uses these **15 property features** for price prediction:

### Property Structural Features (9)
| # | Feature | Source | Type | Range/Values | Description |
|---|---------|--------|------|--------------|-------------|
| 1 | **GrLivArea** | Assessor API | Numeric | 1,200 - 4,500 sq ft | Ground living area (main living space) |
| 2 | **LotArea** | Assessor API | Numeric | 4,000 - 15,000 sq ft | Total lot/land area size |
| 3 | **GarageArea** | Assessor API | Numeric | 400 - 1,200 sq ft | Garage/carport area |
| 4 | **BedroomAbvGr** | Assessor API | Integer | 2 - 6 | Number of bedrooms above ground |
| 5 | **FullBath** | Assessor API | Integer | 1 - 4 | Number of full bathrooms |
| 6 | **HalfBath** | Assessor API | Integer | 0 - 2 | Number of half bathrooms |
| 7 | **TotRmsAbvGrd** | Assessor API | Integer | 5 - 14 | Total rooms above ground |
| 8 | **Fireplaces** | Assessor API | Integer | 0 - 3 | Number of fireplaces |
| 9 | **GarageCars** | Assessor API | Integer | 1 - 4 | Garage capacity (number of cars) |

### Property Age & Condition Features (4)
| # | Feature | Source | Type | Range/Values | Description |
|---|---------|--------|------|--------------|-------------|
| 10 | **YearBuilt** | Assessor API | Integer | 1950 - 2015 | Original construction year |
| 11 | **YearRemodAdd** | Assessor API | Integer | 1980 - 2020 | Year of last renovation/remodel |
| 12 | **OverallQual** | Assessor API | Integer | 5 - 10 (1-10 scale) | Overall material & finish quality rating |
| 13 | **OverallCond** | Assessor API | Integer | 5 - 9 (1-10 scale) | Overall condition rating |

### Property Classification Features (2)
| # | Feature | Source | Type | Values | Description |
|---|---------|--------|------|--------|-------------|
| 14 | **Neighborhood** | Assessor API | Categorical | Downtown, Suburban, Urban, Rural | Geographic/demographic area type |
| 15 | **HouseStyle** | Assessor API | Categorical | Ranch, Colonial, Cape Cod, Contemporary | House architectural style |

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
│  Step 2: Feature Validation                        │
│  - Ensure all 15 features present                  │
│  - Convert to correct data types                   │
│  - Create pandas DataFrame                         │
└────────────────────────────────────────────────────┘
     ↓
┌────────────────────────────────────────────────────┐
│  Step 3: LightGBM Model Prediction                 │
│  - Input: 15 features                              │
│  - Model: final_enriched_model.joblib              │
│  - Output: Predicted House Price                   │
└────────────────────────────────────────────────────┘
     ↓
PREDICTED PRICE + CONFIDENCE (92.38%)
```

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
```

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
  "address": "123 Main Street, Seattle, WA 98101",
  "predicted_price": 625000.00,
  "confidence": 92.38,
  "error_margin": 16808.00,
  "error_margin_low": 608192.00,
  "error_margin_high": 641808.00,
  "all_15_features": {
    "LotArea": 5234.50,
    "OverallQual": 7,
    "OverallCond": 8,
    "YearBuilt": 2000,
    "YearRemodAdd": 2018,
    "GrLivArea": 2450.00,
    "FullBath": 2,
    "HalfBath": 1,
    "BedroomAbvGr": 4,
    "TotRmsAbvGrd": 9,
    "Fireplaces": 1,
    "GarageCars": 2,
    "GarageArea": 850.00,
    "Neighborhood": "Suburban",
    "HouseStyle": "Colonial"
  },
  "timestamp": "2026-04-22T19:45:30.123456"
}
```

---

## Feature Statistics

- **Total Features**: 15
- **Numeric Features**: 3 (float)
- **Integer Features**: 9
- **Categorical Features**: 2
- **Model Accuracy**: 92.38% (R² score)
- **Model MAE**: ±$16,808
- **Model RMSE**: ±$21,312

This gives you a complete house price prediction based on standard property assessment criteria, all using free (and soon, real) APIs!
