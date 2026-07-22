"""
NASA PCoE battery .mat parser.

Each cell file (e.g. B0005.mat) contains a list of cycles. Every cycle has a
`type` (charge / discharge / impedance) and a `data` block of measured signals.
For State-of-Health we use the *discharge* cycles, which each carry a measured
`Capacity` (Ah) — the ground truth that degrades over the cell's life.
"""
from pathlib import Path
import numpy as np
import scipy.io as sio


def load_cell(mat_path):
    """Load a cell .mat file and return its list of cycle records."""
    mat_path = Path(mat_path)
    name = mat_path.stem  # 'B0005'
    m = sio.loadmat(str(mat_path), simplify_cells=True)
    return m[name]["cycle"]


def discharge_cycles(cycles):
    """Return only discharge cycles that carry a measured capacity."""
    out = []
    for c in cycles:
        if c.get("type") == "discharge":
            d = c.get("data", {})
            if isinstance(d, dict) and "Capacity" in d and np.ravel(d["Capacity"]).size > 0:
                out.append(c)
    return out


def cycle_capacity(cycle):
    """Extract the scalar discharge capacity (Ah) from a cycle."""
    return float(np.ravel(cycle["data"]["Capacity"])[0])
