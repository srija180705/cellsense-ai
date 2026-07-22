"""
Deterministic rule engine — risk banding.

Safety-critical banding is intentionally NOT done by the LLM. Thresholds are
explicit and auditable. (State of Health = capacity / initial capacity.)

Five stages give the operator a graded view of battery life rather than a blunt
three-way split.
"""

# SoH (%) lower bounds for each band, most-healthy first.
BAND_THRESHOLDS = [
    ("Healthy", 90),
    ("Early Wear", 85),
    ("Watch", 80),
    ("Near End-of-Life", 75),
    ("Critical", 0),
]

# Most-urgent-first ordering for fleet prioritisation and summaries.
BANDS = ["Critical", "Near End-of-Life", "Watch", "Early Wear", "Healthy"]
RISK_ORDER = {b: i for i, b in enumerate(BANDS)}


def risk_band(soh: float) -> str:
    pct = soh * 100
    for name, low in BAND_THRESHOLDS:
        if pct >= low:
            return name
    return "Critical"
