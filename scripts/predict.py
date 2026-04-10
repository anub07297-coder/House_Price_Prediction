from pathlib import Path

from house_price_prediction.config import load_settings
from house_price_prediction.predict import predict_from_csv


if __name__ == "__main__":
    settings = load_settings()
    input_path = Path("data/processed/predict_input.csv")
    predictions = predict_from_csv(settings.model_path, input_path)

    output_path = Path("data/processed/predictions.csv")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    predictions.to_csv(output_path, index=False)

    print(f"Predictions saved to: {output_path}")
