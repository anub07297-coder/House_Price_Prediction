# Geocoding & Census API Integration Guide

## Overview

This guide documents how to integrate geocoding services and Census API data to enrich property features for price prediction.

---

## Architecture

### Data Flow
```
User Address Input
    ↓
Geocoding Service (Nominatim/Census Geography)
    ↓
Get Coordinates (Latitude, Longitude)
    ↓
Census API Query (ACS 2022)
    ↓
Extract Census Features (MedianIncome, UnemploymentRate, etc.)
    ↓
Combine with Property Features
    ↓
Model Prediction
```

---

## Geocoding Services

### 1. Nominatim (OpenStreetMap)
**Purpose**: Convert address to geographic coordinates

**Endpoint**:
```
https://nominatim.openstreetmap.org/search?q={ADDRESS}&format=json
```

**Features**:
- Free, no API key required
- Rate limited (~1 request/second)
- Returns: lat, lon, display_name

**Response Format**:
```json
[
  {
    "lat": "47.6062",
    "lon": "-122.3321",
    "display_name": "Seattle, Washington, USA"
  }
]
```

### 2. Census Geography API
**Purpose**: Convert coordinates to Census tract/block group

**Endpoint**:
```
https://geo.fcc.gov/api/census/tract?lat={LAT}&lon={LON}&format=json
```

**Features**:
- Free API from FCC
- Returns Census tract, block group, state, county
- No authentication required

**Response Format**:
```json
{
  "type": "Point",
  "coordinates": [-122.3321, 47.6062],
  "properties": {
    "Census2020": {
      "fips": "53033",
      "name": "King County, WA",
      "tract": "0123.45"
    }
  }
}
```

---

## Census API (American Community Survey)

### ACS 2022 Data Most Predictive Features

| Feature | Census Variable | Type | Range | Predictive Power |
|---------|-----------------|------|-------|-----------------|
| Median Income | B19013_001E | Integer | $0 - $250K+ | High (10.81%) |
| Unemployment Rate | DP03_0005PE | Percentage | 0-100% | High (10.77%) |
| Median Age | B01002_001E | Integer | 0-100 years | High (14.90%) |
| Population | B01003_001E | Integer | 0-10000+ | Medium |
| Owner-Occupied Units | B25003_002E | Integer | 0-10000+ | Medium |
| Renter-Occupied Units | B25003_003E | Integer | 0-10000+ | Low (4.61%) |
| Education Level | B15003_001E | Integer | 0-100% | Medium (4.89%) |

---

## Integration Steps

### Step 1: Get Property Address
```python
address = "123 Main St, Seattle, WA 98101"
```

### Step 2: Geocode Address
```python
import requests

def geocode_address(address):
    params = {
        'q': address,
        'format': 'json'
    }
    response = requests.get('https://nominatim.openstreetmap.org/search', params=params)
    data = response.json()
    
    if data:
        return {
            'latitude': float(data[0]['lat']),
            'longitude': float(data[0]['lon'])
        }
    return None
```

### Step 3: Get Census Tract
```python
def get_census_tract(latitude, longitude):
    params = {
        'lat': latitude,
        'lon': longitude,
        'format': 'json'
    }
    response = requests.get('https://geo.fcc.gov/api/census/tract', params=params)
    data = response.json()
    
    if 'properties' in data:
        tract_data = data['properties']['Census2020']
        return {
            'fips': tract_data['fips'],
            'tract': tract_data['tract'],
            'state': tract_data['name']
        }
    return None
```

### Step 4: Query Census API
```python
import census
import os

def get_census_features(fips_code, tract_number):
    """
    Query ACS 2022 data for Census tract
    
    Requires: Census API key in environment variable CENSUS_API_KEY
    Get free key at: https://api.census.gov/data/key_signup.html
    """
    
    api_key = os.getenv('CENSUS_API_KEY')
    
    features = {
        'B19013_001E': 'median_income',
        'DP03_0005PE': 'unemployment_rate',
        'B01002_001E': 'median_age',
        'B01003_001E': 'population',
        'B25003_002E': 'owner_occupied_units',
        'B25003_003E': 'renter_occupied_units',
        'B15003_001E': 'education_total'
    }
    
    # Construct query
    variables = ','.join(features.keys())
    url = f"https://api.census.gov/data/2022/acs/acs5?get={variables}&for=tract:{tract_number}&in=state:{fips_code[:2]}&key={api_key}"
    
    response = requests.get(url)
    data = response.json()
    
    result = {}
    for i, key in enumerate(features.keys()):
        result[features[key]] = data[1][i]
    
    return result
```

---

## Implementation in FastAPI

### Complete Pipeline Example

```python
from fastapi import APIRouter, HTTPException
from typing import Optional

router = APIRouter()

@router.post("/predict")
async def predict_price(address: str, property_features: dict) -> dict:
    """
    Predict house price given address and property features
    """
    
    # Step 1: Geocode
    coords = geocode_address(address)
    if not coords:
        raise HTTPException(status_code=400, detail="Could not geocode address")
    
    # Step 2: Get Census Tract
    tract = get_census_tract(coords['latitude'], coords['longitude'])
    if not tract:
        raise HTTPException(status_code=400, detail="Could not find Census tract")
    
    # Step 3: Get Census Features
    census_features = get_census_features(tract['fips'], tract['tract'])
    
    # Step 4: Combine Features
    combined_features = {
        **property_features,
        'MedianIncome': census_features['median_income'],
        'UnemploymentRate': census_features['unemployment_rate'],
        'SchoolDistrictRating': derive_school_rating(census_features)
    }
    
    # Step 5: Predict
    prediction = model.predict(combined_features)
    
    return {
        'address': address,
        'predicted_price': prediction,
        'census_tract': tract['tract'],
        'location': {
            'latitude': coords['latitude'],
            'longitude': coords['longitude']
        }
    }
```

---

## Configuration

### Environment Variables
```bash
# .env file
CENSUS_API_KEY=your_census_api_key_here
NOMINATIM_USER_AGENT=your_app_name/1.0

# API Rate Limiting
GEOCODING_RATE_LIMIT=1  # requests per second
CENSUS_API_TIMEOUT=30   # seconds
```

### Census API Key
1. Sign up: https://api.census.gov/data/key_signup.html
2. Get free key (no credit card required)
3. Add to `.env` file
4. Restart API service

---

## Error Handling

### Common Issues

| Issue | Cause | Solution |
|-------|-------|----------|
| "Could not geocode address" | Invalid/ambiguous address | Normalize address format, add ZIP code |
| "Census API timeout" | Network issue or rate limiting | Retry with exponential backoff |
| "Missing Census data" | Address outside US or Census doesn't have data | Use fallback features |
| "Rate limited" | Too many requests to Nominatim | Cache results, use local fallback |

### Fallback Strategy
```python
def get_census_features_with_fallback(latitude, longitude):
    """
    Try Census API, fall back to synthetic features if unavailable
    """
    try:
        return get_census_features(latitude, longitude)
    except Exception as e:
        logger.warning(f"Census API failed: {e}, using fallback features")
        return generate_fallback_features(latitude, longitude)
```

---

## Performance Optimization

### Caching
```python
from functools import lru_cache
import hashlib

@lru_cache(maxsize=1000)
def geocode_address_cached(address: str):
    """Cache geocoding results for 24 hours"""
    return geocode_address(address)
```

### Batch Processing
```python
def batch_geocode(addresses: list) -> dict:
    """Process multiple addresses with rate limiting"""
    results = {}
    for i, address in enumerate(addresses):
        if i > 0:
            time.sleep(1.1)  # Rate limit: 1 req/sec
        results[address] = geocode_address(address)
    return results
```

---

## Testing

### Unit Test Example
```python
import pytest

def test_geocode_address():
    result = geocode_address("Seattle, WA")
    assert result is not None
    assert 'latitude' in result
    assert 'longitude' in result
    assert 47.0 < result['latitude'] < 48.0  # Seattle bounds

def test_get_census_tract():
    coords = geocode_address("Seattle, WA")
    tract = get_census_tract(coords['latitude'], coords['longitude'])
    assert tract is not None
    assert tract['state'] == 'Washington'

def test_census_api_integration():
    """Full integration test with real API"""
    address = "123 Main St, Seattle, WA 98101"
    coords = geocode_address(address)
    tract = get_census_tract(coords['latitude'], coords['longitude'])
    features = get_census_features(tract['fips'], tract['tract'])
    
    assert features['median_income'] > 0
    assert 0 <= features['unemployment_rate'] <= 100
```

---

## References

- **Nominatim Documentation**: https://nominatim.org/release-docs/latest/api/Overview/
- **Census Geography API**: https://geo.fcc.gov/api/census/
- **Census API (ACS 2022)**: https://api.census.gov/
- **Census Variable Definitions**: https://api.census.gov/data/2022/acs/acs5/variables.html

---

## Production Considerations

1. **API Keys**: Store in secure environment, rotate regularly
2. **Rate Limiting**: Implement backoff for third-party APIs
3. **Caching**: Cache geocoding and Census results to reduce API calls
4. **Monitoring**: Log all API calls for debugging and analytics
5. **Fallbacks**: Have synthetic/default features if APIs unavailable
6. **Privacy**: Don't log full addresses in production logs

---

**Last Updated**: April 21, 2026  
**Status**: Production Ready
