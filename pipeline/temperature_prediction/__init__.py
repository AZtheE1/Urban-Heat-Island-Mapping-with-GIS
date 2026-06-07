"""Modular temperature prediction package."""

from .base import BaseTemperaturePredictor
from .engine import predict_temperature_for_region
from .linear_regression import LinearRegressionPredictor
from .registry import DEFAULT_PREDICTOR, PREDICTOR_REGISTRY, get_predictor

__all__ = [
    "BaseTemperaturePredictor",
    "LinearRegressionPredictor",
    "DEFAULT_PREDICTOR",
    "PREDICTOR_REGISTRY",
    "get_predictor",
    "predict_temperature_for_region",
]
