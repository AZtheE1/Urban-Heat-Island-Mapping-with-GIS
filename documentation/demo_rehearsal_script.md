# Thesis Defense Demo Rehearsal Script

**Duration:** ~10 minutes  
**Prerequisites:** Run `python main.py` once, then `python dashboard/run_dashboard.py`  
**URL:** http://127.0.0.1:5000

---

## 1. Pipeline & Data Foundation (1 min)

Explain that the system runs a unified Python pipeline:

```bash
python main.py
```

- **Mirpur 12:** 20 GPS field survey points with photographic verification (`field_data/mirpur12_ground_data.csv`)
- **Divisional regions:** Framework scalability demonstration via parameterized presets (15 points each)
- **Historical analysis:** ~11k observations → hybrid ML metrics in `ml_models/hybrid_reg_metrics.json`

---

## 2. Environmental Command Center — `/` (3 min)

1. Select **Mirpur 12** — show ground-truth badge: “Ground-truth baseline”
2. Point to **6 KPI cards** (temperature, NDVI, HRI, resilience, high risk, alerts)
3. **Model intelligence panel:**
   - Regression formula: `Temperature = α − (β × NDVI)`
   - R², RMSE, MAE, Decision Tree R², Random Forest R²
4. **Regional temperature forecast:** current + 1/3/5 year predictions from `/api/predict-temperature`
5. **Data & methodology panel:** field survey vs framework demo classification
6. **Map:** Toggle Heat Risk layer — click a marker — show ground verification photo popup
7. Switch to **Dhaka** — note badge changes to “Scalability demonstration”
8. **Surface type chart** updates per region; **hotspot table** refreshes

---

## 3. Climate Analytics — `/analytics` (3 min)

1. Comparative city bar chart across 5 jurisdictions
2. Historical thermal trends + heatwave days
3. **Hybrid ML forecast (2027–2030)** chart — observed baseline vs best hybrid model
4. **Model validation table** — linear R², RMSE, tree model scores per region
5. Click a city bar → drill-down with **regional temperature forecast**

---

## 4. Supporting Modules (2 min)

- **Simulation** (`/simulation`): green infrastructure cooling scenarios
- **Decision Support** (`/decisions`): policy recommendations
- **Report Studio** (`/reports`): PDF/JSON environmental reports
- **Alert Center** (`/alerts`): heatwave severity monitoring + historical events

---

## 5. Viva Talking Points

| Question | Answer |
|----------|--------|
| What is real vs simulated? | Mirpur 12 = field ground-truth. Four divisions = framework demo data. |
| Where is satellite data? | NDVI/LST derived via prescribed formulas and surface reflectance presets fused with ground observations. |
| How is the model validated? | R², RMSE, MAE on Mirpur 12; hybrid model comparison on historical unified dataset. |
| 2030 forecast? | Hybrid residual-fitting pipeline; shown on Climate Analytics chart. |
| Regression relationship? | Inverse correlation: higher NDVI → lower temperature (β slope in formula). |

---

## API Health Check (before demo)

```bash
curl -s http://127.0.0.1:5000/api/heat-data?region=mirpur12 | head -c 80
curl -s http://127.0.0.1:5000/api/predict-temperature?region=mirpur12
curl -s http://127.0.0.1:5000/api/hybrid-forecast | head -c 80
curl -s http://127.0.0.1:5000/api/model-validation
curl -s http://127.0.0.1:5000/api/data-provenance?region=mirpur12
```

All should return HTTP 200 JSON.
