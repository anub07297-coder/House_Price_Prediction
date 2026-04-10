"""House price prediction package."""

from .config import Settings
from .model import train_and_save_model

__all__ = ["Settings", "train_and_save_model"]
