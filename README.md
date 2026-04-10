# House Price Prediction

End-to-end machine learning scaffold for training and serving a house price regression model.

## Project Structure

```text
.
├── data/
│   ├── raw/                # Place your source CSV here (default: housing.csv)
│   └── processed/          # Generated prediction inputs/outputs
├── models/                 # Trained model artifacts (.joblib)
├── notebooks/              # Exploration notebooks
├── scripts/
│   ├── train.py            # Train + evaluate + save model
│   └── predict.py          # Batch inference from CSV
├── src/house_price_prediction/
│   ├── config.py           # Env-based settings
│   ├── data.py             # Data loading and split helpers
│   ├── features.py         # Preprocessing pipeline
│   ├── model.py            # Training, metrics, serialization
│   └── predict.py          # Inference helper
├── tests/
├── .env.example
├── pyproject.toml
└── requirements-dev.txt
```

## Environment Setup

1. Create and activate a virtual environment:

```bash
python -m venv .venv
source .venv/bin/activate
```

2. Install dependencies:

```bash
pip install -r requirements-dev.txt
pip install -e .
```

3. Copy environment defaults:

```bash
cp .env.example .env
```

## Data Expectations

- Default training file path: `data/raw/housing.csv`
- Default target column: `SalePrice`
- Configure via `.env` if your data uses different names

Example `.env` values:

```env
RAW_DATA_PATH=data/raw/housing.csv
TARGET_COLUMN=SalePrice
MODEL_PATH=models/house_price_model.joblib
TEST_SIZE=0.2
RANDOM_STATE=42
```

## Train

```bash
python scripts/train.py
```

Output:
- model saved at `models/house_price_model.joblib`
- printed evaluation metrics: MAE, RMSE, R2

## Predict

1. Create input file for inference at `data/processed/predict_input.csv`.
2. Run:

```bash
python scripts/predict.py
```

Output:
- `data/processed/predictions.csv`

## Tests

```bash
pytest
```

## Optional Make Commands

```bash
make setup
make train
make predict
make test
```
