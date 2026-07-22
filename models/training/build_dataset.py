"""
Build the processed training table from raw NASA .mat cells.

For every discharge cycle of every core cell we compute:
  - health-indicator features (from utils.features)
  - SoH  = capacity / initial capacity of that cell
  - RUL  = discharge cycles remaining until the cell reaches end-of-life

Output: datasets/processed/cell_features.csv  (regenerable; git-ignored)
"""
import sys
from pathlib import Path

import numpy as np
import pandas as pd

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT))

from utils.mat_parser import load_cell, discharge_cycles, cycle_capacity
from utils.features import cycle_features

DATA_DIR = REPO_ROOT / "datasets" / "NASA_Battery" / "mat"
OUT_CSV = REPO_ROOT / "datasets" / "processed" / "cell_features.csv"

# Core room-temperature cells (the standard SoH/RUL benchmark set)
CORE_CELLS = ["B0005", "B0006", "B0007", "B0018"]
EOL_CAPACITY = 1.4  # Ah — end-of-life threshold (~70% of 2 Ah rated)


def build(cells=CORE_CELLS):
    rows = []
    for cell in cells:
        path = DATA_DIR / f"{cell}.mat"
        if not path.exists():
            print(f"  ! missing {path.name}, skipping")
            continue

        dis = discharge_cycles(load_cell(path))
        caps = [cycle_capacity(c) for c in dis]
        initial = caps[0]

        # First cycle index at or below end-of-life
        eol_idx = next((k for k, cap in enumerate(caps) if cap <= EOL_CAPACITY), len(caps) - 1)

        for k, cyc in enumerate(dis):
            feats = cycle_features(cyc)
            if feats is None:
                continue
            feats.update({
                "cell": cell,
                "cycle": k,
                "capacity": caps[k],
                "soh": caps[k] / initial,
                "rul": max(eol_idx - k, 0),
            })
            rows.append(feats)

        print(f"  {cell}: {len(dis)} discharge cycles | "
              f"cap {initial:.3f}->{caps[-1]:.3f} Ah | EOL@cycle {eol_idx}")

    df = pd.DataFrame(rows)
    OUT_CSV.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(OUT_CSV, index=False)
    print(f"\nSaved {len(df)} rows -> {OUT_CSV.relative_to(REPO_ROOT)}")
    return df


if __name__ == "__main__":
    print("Building processed dataset from NASA cells...")
    build()
