"""Linear regression trend model for annual temperature forecasting."""

import numpy as np
from sklearn.linear_model import LinearRegression

from .base import BaseTemperaturePredictor


class LinearRegressionPredictor(BaseTemperaturePredictor):
    """Fits a linear trend: temperature = intercept + slope * year."""

    name = "linear_regression"

    def __init__(self):
        self._model = LinearRegression()
        self._fitted = False

    def fit(self, years, temperatures):
        years_arr = np.asarray(years, dtype=float).reshape(-1, 1)
        temps_arr = np.asarray(temperatures, dtype=float)
        self._model.fit(years_arr, temps_arr)
        self._fitted = True
        return self

    def predict(self, years):
        if not self._fitted:
            raise RuntimeError("Model must be fitted before calling predict().")
        years_arr = np.asarray(years, dtype=float).reshape(-1, 1)
        return self._model.predict(years_arr)
