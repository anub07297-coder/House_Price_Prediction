"""
Convert house_price_model.joblib to house_price_model.pkl
"""
import joblib
import pickle
from pathlib import Path

# Define paths
joblib_path = Path("models/house_price_model.joblib")
pkl_path = Path("models/house_price_model.pkl")

# Check if joblib file exists
if not joblib_path.exists():
    raise FileNotFoundError(f"Model file not found at {joblib_path}")

print(f"Loading model from {joblib_path}...")
model = joblib.load(joblib_path)

print(f"Saving model to {pkl_path}...")
with open(pkl_path, 'wb') as f:
    pickle.dump(model, f)

print(f"✓ Conversion complete!")
print(f"  Source: {joblib_path}")
print(f"  Target: {pkl_path}")

# Verify the conversion
print(f"\nVerifying...")
with open(pkl_path, 'rb') as f:
    loaded_model = pickle.load(f)
print(f"✓ Model successfully loaded from .pkl file")
print(f"  Model type: {type(loaded_model)}")
