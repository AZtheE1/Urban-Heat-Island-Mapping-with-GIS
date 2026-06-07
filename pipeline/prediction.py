import json
import os
import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor
from sklearn.tree import DecisionTreeRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

def run_machine_learning_predictions(df, meta, models_dir, calc_results=None):
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
    avg_temp = calc_results.get("avg_temp") if calc_results else round(float(df["Temperature"].mean()), 2)
    
    if calc_results:
        peak_hotspot = calc_results.get("peak_hotspot")
        peak_coolspot = calc_results.get("peak_coolspot")
    else:
        hottest_idx = df["Temperature"].idxmax()
        coolest_idx = df["Temperature"].idxmin()
        peak_hotspot = {
            "name": str(df.loc[hottest_idx, "LocationName"]),
            "temp": float(df.loc[hottest_idx, "Temperature"]),
            "lat": float(df.loc[hottest_idx, "Latitude"]),
            "lng": float(df.loc[hottest_idx, "Longitude"])
        }
        peak_coolspot = {
            "name": str(df.loc[coolest_idx, "LocationName"]),
            "temp": float(df.loc[coolest_idx, "Temperature"]),
            "lat": float(df.loc[coolest_idx, "Latitude"]),
            "lng": float(df.loc[coolest_idx, "Longitude"])
        }

    metrics = {
        "region_id": region,
        "region_name": meta["name"],
        "alpha_intercept": round(intercept, 4),
        "beta_slope": round(-slope, 4),  # Positive Beta in: Intercept - Beta * NDVI
        "r2_score": round(r2_lr, 4),
        "rmse": round(rmse_lr, 4),
        "mae": round(mae_lr, 4),
        "avg_temp": avg_temp,
        "peak_hotspot": peak_hotspot,
        "peak_coolspot": peak_coolspot,
        "linear_regression": {
            "alpha_intercept": round(intercept, 4),
            "beta_slope": round(-slope, 4),
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

def run_hybrid_ml_predictions(df, models_dir):
    """
    Advanced Hybrid Machine Learning Pipeline & Projections.
    Uses Linear Regression for macro trend and tree estimators for microclimatic residuals.
    """
    import numpy as np
    import pandas as pd
    from sklearn.linear_model import LinearRegression, Ridge
    from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor, ExtraTreesRegressor
    from sklearn.metrics import mean_squared_error, r2_score
    from sklearn.preprocessing import LabelEncoder
    
    df = df.copy()
    
    # Process dates if not present
    if 'Observation_Time' in df.columns:
        dt_col = pd.to_datetime(df['Observation_Time'])
        if 'Year' not in df.columns:
            df['Year'] = dt_col.dt.year
        if 'Month' not in df.columns:
            df['Month'] = dt_col.dt.month
        if 'Day' not in df.columns:
            df['Day'] = dt_col.dt.day
        if 'Hour' not in df.columns:
            df['Hour'] = dt_col.dt.hour
    else:
        # Fallback if preprocessing added observation columns
        if 'Year' not in df.columns and 'Observation_Year' in df.columns:
            df['Year'] = df['Observation_Year']
        if 'Month' not in df.columns and 'Observation_Month' in df.columns:
            df['Month'] = df['Observation_Month']
        if 'Hour' not in df.columns and 'Observation_Hour' in df.columns:
            df['Hour'] = df['Observation_Hour']
        if 'Day' not in df.columns:
            df['Day'] = 1  # Fallback
        
    # Encoded Features
    le_surface = LabelEncoder()
    df['SurfaceType_Enc'] = le_surface.fit_transform(df['SurfaceType'].astype(str))
    le_traffic = LabelEncoder()
    df['TrafficDensity_Enc'] = le_traffic.fit_transform(df['TrafficDensity'].astype(str))
    
    target = 'heat_index_C'
    features = ['Latitude', 'Longitude', 'SurfaceType_Enc', 'TrafficDensity_Enc', 'Year', 'Month', 'Day', 'Hour', 'wind_speed_kmh', 'humidity_pct', 'rainfall_mm']
    rf_features = ['Latitude', 'Longitude', 'SurfaceType_Enc', 'TrafficDensity_Enc', 'Month', 'Day', 'Hour', 'wind_speed_kmh', 'humidity_pct', 'rainfall_mm']
    
    X_train, y_train = df[df['Year'] <= 2024][features], df[df['Year'] <= 2024][target]
    X_test, y_test = df[df['Year'] > 2024][features], df[df['Year'] > 2024][target]
    
    # 1. Macro Regional Climate Trend
    lr_macro = LinearRegression()
    lr_macro.fit(df[['Year']], df[target])
    df['Linear_Trend'] = lr_macro.predict(df[['Year']])
    df['Residual'] = df[target] - df['Linear_Trend']
    
    base_models = {
        'Linear Regression': LinearRegression(),
        'Ridge Regression': Ridge(alpha=1.0)
    }
    hybrid_trees = {
        'Hybrid Random Forest': RandomForestRegressor(n_estimators=100, random_state=42, n_jobs=-1),
        'Hybrid Gradient Boosting': GradientBoostingRegressor(n_estimators=100, random_state=42),
        'Hybrid Extra Trees': ExtraTreesRegressor(n_estimators=100, random_state=42, n_jobs=-1)
    }
    
    results_list = []
    
    # Base Model Scoring
    for name, model in base_models.items():
        model.fit(X_train, y_train)
        if len(X_test) > 0:
            preds = model.predict(X_test)
            results_list.append({'Model': name, 'RMSE': np.sqrt(mean_squared_error(y_test, preds)), 'R2': r2_score(y_test, preds)})
        else:
            results_list.append({'Model': name, 'RMSE': 0, 'R2': 0})
            
    # Hybrid Tree Model Scoring
    X_train_res = df[df['Year'] <= 2024][rf_features]
    y_train_res = df[df['Year'] <= 2024]['Residual']
    X_test_res = df[df['Year'] > 2024][rf_features]
    
    for name, model in hybrid_trees.items():
        model.fit(X_train_res, y_train_res)
        if len(X_test) > 0:
            base_trend_test = lr_macro.predict(X_test[['Year']])
            predicted_residual = model.predict(X_test_res)
            final_hybrid_preds = base_trend_test + predicted_residual
            results_list.append({'Model': name, 'RMSE': np.sqrt(mean_squared_error(y_test, final_hybrid_preds)), 'R2': r2_score(y_test, final_hybrid_preds)})
        else:
            results_list.append({'Model': name, 'RMSE': 0, 'R2': 0})
            
    metrics_df = pd.DataFrame(results_list)
    
    # 2. Generate Long-Term Future Simulations (2027 - 2030)
    for name, model in base_models.items():
        model.fit(df[features], df[target])
    for name, model in hybrid_trees.items():
        model.fit(df[rf_features], df['Residual'])
        
    baseline_weather = df[df['Year'] == df['Year'].max()].copy()
    future_years = [2027, 2028, 2029, 2030]
    future_blocks = []
    for yr in future_years:
        f_slice = baseline_weather.copy()
        f_slice['Year'] = yr
        future_blocks.append(f_slice)
    
    future_df = pd.concat(future_blocks, ignore_index=True) if len(future_blocks) > 0 else pd.DataFrame()
    
    timeline_records = []
    hist_means = df.groupby('Year')[target].mean().reset_index()
    for _, r in hist_means.iterrows():
        timeline_records.append({'Year': int(r['Year']), 'Model': 'Observed Baseline', 'Heat_Index': float(r[target])})
        
    for name, model in base_models.items():
        if len(future_df) > 0:
            future_df['pred'] = model.predict(future_df[features])
            for yr in future_years:
                timeline_records.append({'Year': yr, 'Model': name, 'Heat_Index': float(future_df[future_df['Year'] == yr]['pred'].mean())})
                
    for name, model in hybrid_trees.items():
        if len(future_df) > 0:
            trend_component = lr_macro.predict(future_df[['Year']])
            residual_component = model.predict(future_df[rf_features])
            future_df['pred'] = trend_component + residual_component
            for yr in future_years:
                timeline_records.append({'Year': yr, 'Model': name, 'Heat_Index': float(future_df[future_df['Year'] == yr]['pred'].mean())})
                
    timeline_df = pd.DataFrame(timeline_records)
    
    # Save metrics JSON
    metrics_json = metrics_df.to_dict(orient='records')
    metrics_path = os.path.join(models_dir, "hybrid_reg_metrics.json")
    with open(metrics_path, "w", encoding="utf-8") as f:
        import json
        json.dump(metrics_json, f, indent=2)

    timeline_json = timeline_df.to_dict(orient='records')
    timeline_path = os.path.join(models_dir, "hybrid_projection_timeline.json")
    with open(timeline_path, "w", encoding="utf-8") as f:
        json.dump(timeline_json, f, indent=2)
        
    return metrics_df, timeline_df, metrics_path
