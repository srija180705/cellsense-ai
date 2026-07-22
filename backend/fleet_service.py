"""
Fleet service — loads the trained models + fleet table and produces the
fleet overview and per-asset detail the API serves.

Each asset is a real NASA cell; its 'current' state is the latest observed
discharge cycle. SoH shown is measured (real); SoH/RUL predictions come from
the trained models to showcase the ML.
"""
import sys
from pathlib import Path

import pandas as pd
import joblib

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))
from utils.features import FEATURE_COLS
from backend.rules import risk_band, RISK_ORDER

ART = REPO_ROOT / "models" / "artifacts"
FLEET_CSV = REPO_ROOT / "datasets" / "processed" / "fleet_features.csv"

_soh_model = joblib.load(ART / "soh_model.pkl")
_rul_model = joblib.load(ART / "rul_model.pkl")
_df = pd.read_csv(FLEET_CSV)

# Fleet-wide reference statistics (computed once) for the explanation agent.
_last_rows = _df.sort_values("cycle").groupby("asset_id").tail(1)
FLEET_STATS = {
    "cycles_median": float((_last_rows["cycle"] + 1).median()),
    "max_temp_median": round(float(_last_rows["max_temp"].median()), 1),
}

# What the SoH model weighs most — real model explainability (top 3 features).
try:
    _imp = _soh_model.feature_importances_
    MODEL_DRIVERS = sorted(
        ({"feature": f, "importance": round(float(v), 3)} for f, v in zip(FEATURE_COLS, _imp)),
        key=lambda x: -x["importance"],
    )[:3]
except Exception:
    MODEL_DRIVERS = []


def _predict(last_row: pd.DataFrame):
    soh_pred = float(_soh_model.predict(last_row[FEATURE_COLS])[0])
    rul_in = last_row[FEATURE_COLS].copy()
    rul_in["soh"] = last_row["soh"].values
    rul_pred = float(_rul_model.predict(rul_in[FEATURE_COLS + ["soh"]])[0])
    return soh_pred, max(rul_pred, 0.0)


def _summary(asset_id: str, g: pd.DataFrame):
    last = g.iloc[[-1]]
    soh_meas = float(last["soh"].iloc[0])
    soh_pred, rul_pred = _predict(last)
    return {
        "asset_id": asset_id,
        "name": str(last["name"].iloc[0]),
        "asset_type": str(last["asset_type"].iloc[0]),
        "source_cell": str(last["cell"].iloc[0]),
        "cycles_observed": int(last["cycle"].iloc[0]) + 1,
        "soh": round(soh_meas, 3),
        "soh_pred": round(soh_pred, 3),
        "rul_cycles": int(round(rul_pred)),
        "risk": risk_band(soh_meas),
        "max_temp": round(float(last["max_temp"].iloc[0]), 1),
    }


def get_fleet():
    assets = [_summary(aid, g.sort_values("cycle")) for aid, g in _df.groupby("asset_id")]
    assets.sort(key=lambda a: (RISK_ORDER[a["risk"]], a["rul_cycles"]))
    return assets


def get_asset(asset_id: str):
    g = _df[_df.asset_id == asset_id].sort_values("cycle")
    if g.empty:
        return None
    detail = _summary(asset_id, g)
    detail["history"] = [
        {"cycle": int(r.cycle), "soh": round(float(r.soh), 3), "capacity": round(float(r.capacity), 3)}
        for r in g.itertuples()
    ]
    return detail
