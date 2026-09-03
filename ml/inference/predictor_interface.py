"""ML Inference Predictor Interface for Developer 1"""
from abc import ABC, abstractmethod
from typing import Dict, Any

class MLPredictorInterface(ABC):
    @abstractmethod
    def load_model(self, model_path: str):
        pass

    @abstractmethod
    def predict(self, features: Dict[str, Any]) -> Dict[str, Any]:
        pass
