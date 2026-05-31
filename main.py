import os
import sys

# Paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CSV_PATH = os.path.join(BASE_DIR, "data", "environmental", "mirpur12_ground_data.csv")

# Create output folders
OUTPUT_DIR = os.path.join(BASE_DIR, "output")
GRAPHS_DIR = os.path.join(OUTPUT_DIR, "graphs")
MAPS_DIR = os.path.join(OUTPUT_DIR, "maps")
MODELS_DIR = os.path.join(OUTPUT_DIR, "models")

for d in [GRAPHS_DIR, MAPS_DIR, MODELS_DIR]:
    os.makedirs(d, exist_ok=True)

# Add project base directory to python system path
sys.path.append(BASE_DIR)

from pipeline import (
    load_regional_data,
    perform_mathematical_calculations,
    generate_visualizations,
    run_machine_learning_predictions
)

def run_full_pipeline():
    print("=" * 65)
    print("🌡️  URBAN HEAT ISLAND DATA PIPELINE - PIPELINE INITIATED  🌡️")
    print("=" * 65)
    
    regions = ["mirpur12", "dhaka_all", "sylhet", "rajshahi", "chittagong"]
    
    for r in regions:
        print(f"\n[PHASE 1] Preprocessing: Ingesting dataset for region: '{r}'...")
        try:
            # 1. Ingest Ground CSV / Satellite simulated values
            df, meta = load_regional_data(r, CSV_PATH)
            print(f" -> Ingested {len(df)} coordinate points for {meta['name']}.")
            
            # 2. Perform LST & NDVI Math Calculations
            print(f"[PHASE 2] Calculation: Computing physical indices (LST & Calculated NDVI)...")
            df, calc_results = perform_mathematical_calculations(df)
            print(f" -> Computed baseline average temperature: {calc_results['avg_temp']}°C.")
            print(f" -> Peak Hotspot: {calc_results['peak_hotspot']['name']} ({calc_results['peak_hotspot']['temp']}°C).")
            print(f" -> Peak Coolspot: {calc_results['peak_coolspot']['name']} ({calc_results['peak_coolspot']['temp']}°C).")
            
            # 3. Train Machine Learning Models (Linear, DT, Random Forest)
            print(f"[PHASE 3] Machine Learning: Training AI regressors (Linear & Random Forest)...")
            metrics, metrics_file = run_machine_learning_predictions(df, meta, MODELS_DIR)
            print(f" -> Trained Linear Regression Formula: {metrics['linear_regression']['formula']}")
            print(f" -> R² Fit Scores: Linear: {metrics['linear_regression']['r2_score']} | Decision Tree: {metrics['decision_tree']['r2_score']} | Random Forest: {metrics['random_forest']['r2_score']}")
            print(f" -> RMSE Values: Linear: {metrics['linear_regression']['rmse']} | Decision Tree: {metrics['decision_tree']['rmse']} | Random Forest: {metrics['random_forest']['rmse']}")
            print(f" -> Saved fit metrics to: {os.path.basename(metrics_file)}")
            
            # 4. Generate visual outputs (Matplotlib PNG + Folium Leaflet.js HTML Map)
            print(f"[PHASE 4] Visualization: Generating visual scatter plots & Leaflet.js interactive maps...")
            graph_file, map_file = generate_visualizations(df, meta, GRAPHS_DIR, MAPS_DIR)
            print(f" -> Exported scatter plot visualization to: {os.path.basename(graph_file)}")
            print(f" -> Generated dynamic HTML Leaflet hotspot overlay: {os.path.basename(map_file)}")
            print("-" * 65)
            
        except Exception as e:
            print(f" -> ERROR: Pipeline execution failed for region '{r}': {e}")
            import traceback
            traceback.print_exc()
            print("-" * 65)
            
    print("\n" + "=" * 65)
    print("🚀 PIPELINE COMPLETED SUCCESSFULLY! ALL OUTPUTS EXPORTED! 🚀")
    print("=" * 65)

if __name__ == "__main__":
    run_full_pipeline()
