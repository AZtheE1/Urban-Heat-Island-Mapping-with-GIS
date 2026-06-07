"""High-level temperature prediction engine."""

import pandas as pd

from .data_loader import load_annual_temperature_series, load_regional_baseline_temperature
from .registry import DEFAULT_PREDICTOR, get_predictor

PREDICTION_HORIZONS = (1, 3, 5)


def predict_temperature_for_region(
    base_dir,
    region="mirpur12",
    model_name=None,
    horizons=PREDICTION_HORIZONS,
):
    """
    Train a regression model on historical annual temperatures and forecast
    regional surface temperatures for 1, 3, and 5 years ahead.
    """
    annual_series, data_source = load_annual_temperature_series(base_dir)
    years = annual_series.index.to_numpy(dtype=float)
    temperatures = annual_series.to_numpy(dtype=float)

    if len(years) < 2:
        raise ValueError("At least two annual temperature records are required.")

    predictor = get_predictor(model_name or DEFAULT_PREDICTOR)
    predictor.fit(years, temperatures)
    evaluation = predictor.evaluate(years, temperatures)

    current_year = int(years.max())
    regional_baseline, region_name = load_regional_baseline_temperature(base_dir, region)
    trend_at_current_year = float(predictor.predict([current_year])[0])

    if regional_baseline is not None:
        current_temperature = round(regional_baseline, 4)
        calibration_offset = regional_baseline - trend_at_current_year
    else:
        current_temperature = round(trend_at_current_year, 4)
        calibration_offset = 0.0

    future_years = [current_year + horizon for horizon in horizons]
    raw_predictions = predictor.predict(future_years)
    calibrated_predictions = [float(value) + calibration_offset for value in raw_predictions]

    horizon_keys = {
        1: "predicted1Year",
        3: "predicted3Years",
        5: "predicted5Years",
    }
    predictions = {
        horizon_keys[horizon]: round(calibrated_predictions[idx], 4)
        for idx, horizon in enumerate(horizons)
        if horizon in horizon_keys
    }

    return {
        "region": region,
        "name": region_name,
        "model": predictor.name,
        "dataSource": data_source,
        "baseYear": current_year,
        "trainingYears": [int(year) for year in years],
        "currentTemperature": current_temperature,
        **predictions,
        "evaluation": evaluation,
    }
