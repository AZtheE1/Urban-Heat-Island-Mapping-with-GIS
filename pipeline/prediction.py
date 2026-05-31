import json
import os
import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor
from sklearn.tree import DecisionTreeRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

def run_machine_learning_predictions(df, meta, models_dir):
    """
    Trains multiple AI / Machine Learning regression models (Linear, Decision Tree, and Random Forest)
    on vegetation density index (NDVI) to predict future surface temperatures.
    Equation: Predicted Temperature = Alpha - (Beta * NDVI)
    """
    region = meta["region"]
    
    # 1. Prepare features and targets
    X = df[["NDVI"]].values
    y = df["Temperature"].values
    
    # 2. Model 1: Simple Linear Regression
    lr = LinearRegression()
    lr.fit(X, y)
    y_pred_lr = lr.predict(X)
    
    slope = float(lr.coef_[0])
    intercept = float(lr.intercept_)
    
    mae_lr = mean_absolute_error(y, y_pred_lr)
    rmse_lr = np.sqrt(mean_squared_error(y, y_pred_lr))
    r2_lr = r2_score(y, y_pred_lr)
    
    # 3. Model 2: Decision Tree Regressor
    dt = DecisionTreeRegressor(max_depth=3, random_state=42)
    dt.fit(X, y)
    y_pred_dt = dt.predict(X)
    mae_dt = mean_absolute_error(y, y_pred_dt)
    rmse_dt = np.sqrt(mean_squared_error(y, y_pred_dt))
    r2_dt = r2_score(y, y_pred_dt)
    
    # 4. Model 3: Random Forest Regressor (Advanced ML option)
    rf = RandomForestRegressor(n_estimators=50, max_depth=3, random_state=42)
    rf.fit(X, y)
    y_pred_rf = rf.predict(X)
    mae_rf = mean_absolute_error(y, y_pred_rf)
    rmse_rf = np.sqrt(mean_squared_error(y, y_pred_rf))
    r2_rf = r2_score(y, y_pred_rf)
    
    # 5. Compile prediction metrics
    metrics = {
        "region_id": region,
        "region_name": meta["name"],
        "linear_regression": {
            "alpha_intercept": round(intercept, 4),
            "beta_slope": round(-slope, 4),  # Represented as Positive Beta in: Intercept - Beta * NDVI
            "r2_score": round(r2_lr, 4),
            "rmse": round(rmse_lr, 4),
            "mae": round(mae_lr, 4),
            "formula": f"Temperature = {round(intercept, 2)} - ({round(-slope, 2)} * NDVI)"
        },
        "decision_tree": {
            "r2_score": round(r2_dt, 4),
            "rmse": round(rmse_dt, 4),
            "mae": round(mae_dt, 4)
        },
        "random_forest": {
            "r2_score": round(r2_rf, 4),
            "rmse": round(rmse_rf, 4),
            "mae": round(mae_rf, 4)
        }
    }
    
    # Write metrics to serialized JSON file
    metrics_path = os.path.join(models_dir, f"{region}_reg_metrics.json")
    with open(metrics_path, "w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2)
        
    return metrics, metrics_path
