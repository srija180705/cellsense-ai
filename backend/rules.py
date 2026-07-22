"""
Deterministic rule engine — risk banding.

Safety-critical banding is intentionally NOT done by the LLM. Thresholds are
explicit and auditable. (State of Health = capacity / initial capacity.)
"""

HEALTHY_MIN = 0.85
WATCH_MIN = 0.78  # below this = Critical


def risk_band(soh: float) -> str:
    if soh >= HEALTHY_MIN:
        return "Healthy"
    if soh >= WATCH_MIN:
        return "Watch"
    return "Critical"


# Sort order for fleet prioritisation (most urgent first)
RISK_ORDER = {"Critical": 0, "Watch": 1, "Healthy": 2}
