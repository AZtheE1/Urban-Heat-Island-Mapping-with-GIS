import pandas as pd
import numpy as np

def run_regression_analysis(csv_path):
    """
    Reads the synthesized ground CSV data, builds a clean Linear Regression 
    model linking vegetation cover (NDVI) with Temperature, and yields metrics.
    Equation: Predicted Temperature = Alpha - (Beta * NDVI)
    """
    try:
        # Load csv data
        df = pd.read_csv(csv_path)
        
        # Extract features and targets
        X = df['NDVI'].values
        y = df['Temperature'].values
        
        # Calculate Linear Regression via Simple Least Squares: y = alpha + beta * X
        # Since NDVI has an inverse relation, we expect a negative slope (beta).
        n = len(X)
        X_mean = np.mean(X)
        y_mean = np.mean(y)
        
        numerator = np.sum((X - X_mean) * (y - y_mean))
        denominator = np.sum((X - X_mean) ** 2)
        
        slope = numerator / denominator
        intercept = y_mean - (slope * X_mean)
        
        # Predictions
        y_pred = intercept + slope * X
        
        # Performance Metrics
        mae = np.mean(np.abs(y - y_pred))
        mse = np.mean((y - y_pred) ** 2)
        rmse = np.sqrt(mse)
        
        # R-squared (Coefficient of Determination)
        ss_tot = np.sum((y - y_mean) ** 2)
        ss_res = np.sum((y - y_pred) ** 2)
        r2 = 1 - (ss_res / ss_tot)
        
        # Summary Analytics
        hottest_idx = np.argmax(y)
        coolest_idx = np.argmin(y)
        
        results = {
            "alpha_intercept": round(float(intercept), 4),
            "beta_slope": round(float(-slope), 4), # Represented as Positive Beta in: Alpha - Beta * NDVI
            "rmse": round(float(rmse), 4),
            "mae": round(float(mae), 4),
            "r2_score": round(float(r2), 4),
            "avg_temp": round(float(y_mean), 2),
            "peak_hotspot": {
                "name": str(df.iloc[hottest_idx]['LocationName']),
                "temp": float(df.iloc[hottest_idx]['Temperature']),
                "lat": float(df.iloc[hottest_idx]['Latitude']),
                "lng": float(df.iloc[hottest_idx]['Longitude'])
            },
            "peak_coolspot": {
                "name": str(df.iloc[coolest_idx]['LocationName']),
                "temp": float(df.iloc[coolest_idx]['Temperature']),
                "lat": float(df.iloc[coolest_idx]['Latitude']),
                "lng": float(df.iloc[coolest_idx]['Longitude'])
            }
        }
        return results, df.to_dict(orient="records")
        
    except Exception as e:
        return {"error": str(e)}, []
