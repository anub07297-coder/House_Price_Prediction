from house_price_prediction.config import load_settings
from house_price_prediction.model import train_and_save_model


if __name__ == "__main__":
    settings = load_settings()
    metrics = train_and_save_model(settings)

    print("Training complete")
    print(f"Saved model: {settings.model_path}")
    print("Metrics:")
    for name, value in metrics.items():
        print(f"  {name}: {value:.4f}")
