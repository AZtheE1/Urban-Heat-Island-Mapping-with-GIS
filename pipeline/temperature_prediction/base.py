"""Abstract base class for temperature prediction models."""

from abc import ABC, abstractmethod

import numpy as np
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score


class BaseTemperaturePredictor(ABC):
    """Interface for pluggable temperature forecasting models."""

    name = "base"

    @abstractmethod
    def fit(self, years, temperatures):
        """Train the model on annual temperature observations."""

    @abstractmethod
    def predict(self, years):
        """Return temperature predictions for the given years."""

    def evaluate(self, years, temperatures):
        """Compute RMSE, MAE, and R² on the provided year/temperature pairs."""
        years_arr = np.asarray(years, dtype=float)
        temps_arr = np.asarray(temperatures, dtype=float)
        predictions = np.asarray(self.predict(years_arr), dtype=float)

        return {
            "rmse": round(float(np.sqrt(mean_squared_error(temps_arr, predictions))), 4),
            "mae": round(float(mean_absolute_error(temps_arr, predictions)), 4),
            "r2": round(float(r2_score(temps_arr, predictions)), 4),
        }
