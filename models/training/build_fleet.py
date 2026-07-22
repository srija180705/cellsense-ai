"""
Build the fleet view table for the dashboard.

We use only the four clean, room-temperature benchmark cells (B0005/06/07/18),
which have valid full-discharge capacity references. To present a realistic
operating fleet (rather than four cells all at end-of-life), each cell is
snapshotted at several life stages — every snapshot is a genuine slice of real
measured data, just observed up to a different cycle.

Output: datasets/processed/fleet_features.csv  (git-ignored)
"""
import sys
from pathlib import Path

import pandas as pd

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT))
from utils.mat_parser import load_cell, discharge_cycles, cycle_capacity
from utils.features import cycle_features

DATA_DIR = REPO_ROOT / "datasets" / "NASA_Battery" / "mat"
OUT_CSV = REPO_ROOT / "datasets" / "processed" / "fleet_features.csv"

CORE_CELLS = ["B0005", "B0006", "B0007", "B0018"]
EOL_CAPACITY = 1.4
SNAPSHOTS = [0.30, 0.55, 0.75, 1.0]          # life-stage fractions per cell
ASSET_TYPES = ["Haul Truck", "Forklift", "Loader", "Yard Shuttle"]


def build_all():
    rows = []
    asset_num = 100
    for ci, cell in enumerate(CORE_CELLS):
        dis = discharge_cycles(load_cell(DATA_DIR / f"{cell}.mat"))
        caps = [cycle_capacity(c) for c in dis]
        initial = caps[0]
        n = len(dis)
        eol_idx = next((k for k, c in enumerate(caps) if c <= EOL_CAPACITY), n - 1)

        for si, frac in enumerate(SNAPSHOTS):
            snap = max(3, int(frac * (n - 1)))
            asset_num += 1
            asset_id = f"EV-{asset_num}"
            atype = ASSET_TYPES[(ci + si) % len(ASSET_TYPES)]

            for k in range(snap + 1):
                feats = cycle_features(dis[k])
                if feats is None:
                    continue
                feats.update({
                    "asset_id": asset_id, "name": asset_id, "asset_type": atype,
                    "cell": cell, "cycle": k, "capacity": caps[k],
                    "soh": caps[k] / initial, "rul": max(eol_idx - k, 0),
                })
                rows.append(feats)

    df = pd.DataFrame(rows)
    OUT_CSV.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(OUT_CSV, index=False)
    print(f"Fleet: {df.asset_id.nunique()} assets from {len(CORE_CELLS)} real cells, "
          f"{len(df)} cycle rows | SoH range {df.soh.min():.2f}-{df.soh.max():.2f}")
    return df


if __name__ == "__main__":
    build_all()
