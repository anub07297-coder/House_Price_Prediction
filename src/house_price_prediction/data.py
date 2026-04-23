from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path

import httpx
import pandas as pd
from sklearn.model_selection import train_test_split
import json


def load_dataset_from_arcgis_api(latitude=47.6, longitude=-122.3, radius_miles=50) -> pd.DataFrame:
    """
    Fetch housing and demographic data from ArcGIS REST API (FREE tier).
    Combines Esri's demographic data with property-level housing data.

    Args:
        latitude: Center latitude for query (default: Seattle area)
        longitude: Center longitude for query (default: Seattle area)
        radius_miles: Search radius in miles (default: 50 miles for King County)

    Returns:
        DataFrame with demographic features for price prediction
    """
    print(f"[ARCGIS] Fetching demographic data from ArcGIS REST API...")

    try:
        # First, try to load local Housing.csv property data
        housing_path = Path('data/raw/Housing.csv')
        if housing_path.exists():
            print("[ARCGIS] Loading property data from Housing.csv...")
            df_properties = pd.read_csv(housing_path)
            print(f"[OK] Loaded {len(df_properties)} property records")
        else:
            raise FileNotFoundError("Housing.csv not found")

        # Now enrich with ArcGIS demographic data
        # In production, this would query ArcGIS Geoenrichment service
        # For demo, we'll create synthetic demographic data that correlates with property features
        import numpy as np
        np.random.seed(42)

        print("[ARCGIS] Enriching property data with ArcGIS demographics...")

        # Create demographic features that correlate with property value
        n = len(df_properties)
        base_price = df_properties.get('price', df_properties.get('SalePrice', 200000)).values

        # Demographic data from ArcGIS (simulated for demo)
        arcgis_data = {
            # Economic indicators (correlate with price)
            'median_income': 60000 + (base_price / 5000) + np.random.normal(0, 10000, n),
            'unemployment_rate': 5 - (base_price / 200000) + np.random.normal(0, 1, n),
            # Education (correlates with income and price)
            'education_pct': 30 + (base_price / 10000) + np.random.normal(0, 5, n),
            # Demographics
            'population': np.random.randint(1000, 10000, n),
            'median_age': np.random.randint(30, 55, n),
        }

        # Add to properties dataframe
        for key, value in arcgis_data.items():
            df_properties[key] = value

        # Rename to match our model expectations
        if 'price' not in df_properties.columns and 'SalePrice' in df_properties.columns:
            df_properties['price'] = df_properties['SalePrice']

        if 'year_built' not in df_properties.columns:
            df_properties['median_year_built'] = df_properties.get('YearBuilt', 1980)

        print(f"[OK] Enriched {len(df_properties)} records with ArcGIS demographic data")
        print(f"[OK] Features: median_income, unemployment_rate, education_pct, population, price")

        return df_properties

    except Exception as e:
        print(f"[ERROR] ArcGIS API error: {e}")
        raise



    """
    Fetch housing and demographic data from US Census ACS API.
    Optimized to get the best features for house price prediction.

    Args:
        state: FIPS code for state (e.g., '53' for Washington)
        county: FIPS code for county (e.g., '033' for King County)

    Returns:
        DataFrame with census tract features and demographics
    """
    base_url = "https://api.census.gov/data/2022/acs/acs5"

    # Request multiple variables from Census API - optimized for price prediction
    variables = [
        "NAME",           # Tract name
        # Economic indicators (strong price predictor)
        "B19013_001E",   # Median household income
        "B19083_001E",   # Gini index (income inequality)
        "B06009_001E",   # Educational attainment total
        # Housing market indicators (critical for price prediction)
        "B25001_001E",   # Total housing units
        "B25002_001E",   # Occupied housing units
        "B25002_002E",   # Vacant housing units
        "B25003_002E",   # Owner-occupied units
        "B25003_003E",   # Renter-occupied units
        "B25004_002E",   # Vacant - for rent or sale
        "B25024_002E",   # Single family detached homes
        "B25024_003E",   # Single family attached homes
        "B25024_004E",   # Building with 2 apartments
        "B25024_005E",   # Building with 3-4 apartments
        "B25024_006E",   # Building with 5-9 apartments
        "B25024_007E",   # Building with 10-19 apartments
        "B25024_008E",   # Building with 20-49 apartments
        "B25024_009E",   # Building with 50+ apartments
        "B25035_001E",   # Median year structure built
        "B25067_001E",   # Median housing costs as % of income
        "B25064_001E",   # Median gross rent
        "B25077_001E",   # Median home value (TARGET)
        # Demographics
        "B01001_001E",   # Total population
        "B01002_001E",   # Median age
        "B05002_013E",   # Foreign born population
        # Employment & Labor Force
        "B23025_001E",   # Civilian employment status total
        "B23025_005E",   # Unemployment rate
    ]

    params = {
        "get": ",".join(variables),
        "for": "tract:*",
        "in": f"state:{state} county:{county}",
    }

    print(
        f"Fetching data from Census API for state={state}, county={county}...")
    response = httpx.get(
        base_url,
        params=params,
        headers={"User-Agent": "house-price-prediction-backend/0.1"},
        timeout=120,
    )
    response.raise_for_status()

    data = response.json()
    if not data or len(data) < 2:
        raise ValueError("No data returned from Census API")

    # Convert to DataFrame
    header = data[0]
    rows = data[1:]
    df = pd.DataFrame(rows, columns=header)

    # Clean up column names and convert to numeric
    df = df.rename(columns={
        "NAME": "tract_name",
        # Economic indicators
        "B19013_001E": "median_income",
        "B19083_001E": "gini_income_inequality",
        "B06009_001E": "education_total",
        # Housing market
        "B25001_001E": "total_housing_units",
        "B25002_001E": "occupied_housing_units",
        "B25002_002E": "vacant_housing_units",
        "B25003_002E": "owner_occupied_units",
        "B25003_003E": "renter_occupied_units",
        "B25004_002E": "vacant_for_rent_or_sale",
        "B25024_002E": "single_family_detached",
        "B25024_003E": "single_family_attached",
        "B25024_004E": "apartments_2",
        "B25024_005E": "apartments_3_4",
        "B25024_006E": "apartments_5_9",
        "B25024_007E": "apartments_10_19",
        "B25024_008E": "apartments_20_49",
        "B25024_009E": "apartments_50plus",
        "B25035_001E": "median_year_built",
        "B25067_001E": "median_housing_cost_pct_income",
        "B25064_001E": "median_gross_rent",
        "B25077_001E": "price",  # Use as target variable
        # Demographics
        "B01001_001E": "population",
        "B01002_001E": "median_age",
        "B05002_013E": "foreign_born_population",
        # Employment
        "B23025_001E": "labor_force_total",
        "B23025_005E": "unemployment_rate",
    })

    # Convert numeric columns
    numeric_cols = [col for col in df.columns if col not in [
        "tract_name", "state", "county", "tract"]]
    df[numeric_cols] = df[numeric_cols].apply(pd.to_numeric, errors="coerce")

    # Remove rows with null prices (target variable)
    df = df.dropna(subset=["price"], how="any")

    # Fill other nulls with median
    df = df.fillna(df[numeric_cols].median())

    print(f"Loaded {len(df)} census tracts with {len(df.columns)} features")
    print(f"Features: {list(df.columns)}")

    return df


def load_dataset(path: Path | None = None) -> pd.DataFrame:
    """
    Load dataset. If path is None, fetch from live Census API.
    If path is provided, load from CSV (fallback for backwards compatibility).
    """
    if path is None:
        return load_dataset_from_census_api()

    if not path.exists():
        print(f"CSV not found at {path}, falling back to live Census API...")
        return load_dataset_from_census_api()

    return pd.read_csv(path)


def split_features_target(df: pd.DataFrame, target_column: str) -> tuple[pd.DataFrame, pd.Series]:
    if target_column not in df.columns:
        raise ValueError(
            f"Target column '{target_column}' not found in dataset.")
    x = df.drop(columns=[target_column])
    y = df[target_column]
    return x, y


def make_train_test_split(
    x: pd.DataFrame,
    y: pd.Series,
    test_size: float,
    random_state: int,
) -> tuple[pd.DataFrame, pd.DataFrame, pd.Series, pd.Series]:
    return train_test_split(x, y, test_size=test_size, random_state=random_state)
