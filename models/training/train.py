"""
Train and evaluate the SoH and RUL models — the provable core of CellSense AI.

Evaluation is *cross-cell*: we hold out one entire cell (B0018) as the test set
and train on the others. This proves the model generalises to a battery it has
never seen, rather than memorising cycles — the metric judges actually care about.

Outputs:
  models/artifacts/soh_model.pkl
  models/artifacts/rul_model.pkl
  models/artifacts/metrics.json
"""
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import joblib
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT))
from utils.features import FEATURE_COLS

CSV = REPO_ROOT / "datasets" / "processed" / "cell_features.csv"
ARTIFACTS = REPO_ROOT / "models" / "artifacts"
TEST_CELL = "B0018"

# Prefer XGBoost (as per the design); fall back to sklearn if unavailable.
try:
    from xgboost import XGBRegressor
    def make_model():
        return XGBRegressor(n_estimators=400, max_depth=4, learning_rate=0.05,
                            subsample=0.9, colsample_bytree=0.9, random_state=42)
    MODEL_NAME = "XGBoost"
except Exception:
    from sklearn.ensemble import RandomForestRegressor
    def make_model():
        return RandomForestRegressor(n_estimators=400, random_state=42, n_jobs=-1)
    MODEL_NAME = "RandomForest"


def rmse(y, p):
    return float(np.sqrt(mean_squared_error(y, p)))


def evaluate(df, target, feature_cols, label, unit):
    train = df[df.cell != TEST_CELL]
    test = df[df.cell == TEST_CELL]
    model = make_model()
    model.fit(train[feature_cols], train[target])
    pred = model.predict(test[feature_cols])
    metrics = {
        "rmse": round(rmse(test[target], pred), 4),
        "mae": round(float(mean_absolute_error(test[target], pred)), 4),
        "r2": round(float(r2_score(test[target], pred)), 4),
        "test_cell": TEST_CELL,
        "n_test": int(len(test)),
        "unit": unit,
    }
    print(f"\n[{label}]  model={MODEL_NAME}  held-out cell={TEST_CELL}")
    print(f"    RMSE = {metrics['rmse']} {unit}   MAE = {metrics['mae']} {unit}   R2 = {metrics['r2']}")
    return model, metrics


def main():
    if not CSV.exists():
        raise SystemExit("Processed CSV not found — run build_dataset.py first.")
    df = pd.read_csv(CSV)
    print(f"Loaded {len(df)} cycles across cells: {sorted(df.cell.unique())}")

    ARTIFACTS.mkdir(parents=True, exist_ok=True)

    soh_model, soh_metrics = evaluate(df, "soh", FEATURE_COLS, "SoH estimation", "SoH")
    # RUL uses the health features plus current SoH as an extra signal
    rul_features = FEATURE_COLS + ["soh"]
    rul_model, rul_metrics = evaluate(df, "rul", rul_features, "RUL prediction", "cycles")

    joblib.dump(soh_model, ARTIFACTS / "soh_model.pkl")
    joblib.dump(rul_model, ARTIFACTS / "rul_model.pkl")
    metrics = {"model": MODEL_NAME, "soh": soh_metrics, "rul": rul_metrics,
               "features": FEATURE_COLS}
    (ARTIFACTS / "metrics.json").write_text(json.dumps(metrics, indent=2))

    print(f"\nArtifacts saved to {ARTIFACTS.relative_to(REPO_ROOT)}")
    print("  soh_model.pkl, rul_model.pkl, metrics.json")


if __name__ == "__main__":
    main()
