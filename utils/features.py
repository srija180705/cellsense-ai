"""
Feature engineering for battery State-of-Health estimation.

We derive a compact set of curve-based health indicators from each discharge
cycle's raw signals (voltage, current, temperature, time). These indicators
degrade as the cell ages and let a model estimate SoH from the shape of a cycle
rather than reading capacity directly.
"""
import numpy as np


def cycle_features(cycle):
    """Return a dict of health-indicator features for one discharge cycle,
    or None if the cycle is too short / malformed."""
    d = cycle["data"]
    v = np.asarray(d.get("Voltage_measured", []), dtype=float)
    temp = np.asarray(d.get("Temperature_measured", []), dtype=float)
    t = np.asarray(d.get("Time", []), dtype=float)

    if v.size < 5 or t.size < 5 or temp.size < 5:
        return None

    duration = float(t.max() - t.min())
    # Time spent in the mid-voltage discharge window (a strong ageing indicator)
    mask = (v <= 3.6) & (v >= 3.2)
    t_window = float(t[mask].max() - t[mask].min()) if mask.sum() > 1 else 0.0

    return {
        "mean_voltage": float(np.mean(v)),
        "min_voltage": float(np.min(v)),
        "mean_temp": float(np.mean(temp)),
        "max_temp": float(np.max(temp)),
        "temp_rise": float(np.max(temp) - temp[0]),
        "discharge_time": duration,
        "time_v_window": t_window,
        "volt_drop_rate": float((v.max() - v.min()) / duration) if duration > 0 else 0.0,
    }


# Feature columns used by the models (keeps training / inference in sync)
FEATURE_COLS = [
    "mean_voltage", "min_voltage", "mean_temp", "max_temp",
    "temp_rise", "discharge_time", "time_v_window", "volt_drop_rate",
]

# The RUL model additionally uses current SoH as a signal. (Trajectory features
# such as cap-loss / fade-rate / cycle index were tested but did not improve
# cross-cell generalisation — the absolute scales differ per cell — so the
# proven curve+SoH feature set is kept.)
RUL_FEATURE_COLS = FEATURE_COLS + ["soh"]
