"""
Three-agent pipeline: Monitor -> Diagnose (RAG) -> Recommend.

- Monitor      : summarises the asset's current condition and flags concerns.
- Diagnosis    : infers probable cause + severity, and retrieves supporting guidance.
- Recommendation: composes a grounded, cited action (LLM-polished if available,
                  deterministic template otherwise).
"""
from rag.retriever import retrieve
from agents.llm import generate

THERMAL_MAX_C = 41.0


def monitor(asset: dict):
    obs = [
        f"State of Health at {asset['soh'] * 100:.1f}% ({asset['risk']}).",
        f"Predicted remaining useful life: {asset['rul_cycles']} cycles.",
        f"{asset['cycles_observed']} discharge cycles observed.",
    ]
    if asset.get("max_temp", 0) > THERMAL_MAX_C:
        obs.append(f"Elevated discharge temperature ({asset['max_temp']:.1f} C).")
    return obs


def diagnose(asset: dict):
    risk = asset["risk"]
    signals = []
    if risk == "Critical":
        signals.append("advanced capacity fade")
    elif risk == "Watch":
        signals.append("measurable capacity fade")
    else:
        signals.append("nominal degradation")
    if asset["rul_cycles"] <= 10:
        signals.append("approaching end of life")
    thermal = asset.get("max_temp", 0) > THERMAL_MAX_C
    if thermal:
        signals.append("elevated thermal stress")

    query = " ".join(signals) + " battery state of health maintenance action"
    citations = retrieve(query, k=3)

    cause = {
        "Critical": "Advanced capacity fade consistent with cycle aging; the battery is approaching end of life.",
        "Watch": "Measurable capacity fade from ongoing cycle aging; degradation is progressing.",
        "Healthy": "Normal, expected degradation for the observed cycle count.",
    }[risk]
    if thermal:
        cause += " Elevated discharge temperatures may be accelerating degradation."

    return {"probable_cause": cause, "severity": risk, "signals": signals}, citations


def recommend(asset: dict, diagnosis: dict, citations: list):
    risk = asset["risk"]
    rul = asset["rul_cycles"]

    if risk == "Critical":
        action = "Schedule battery replacement"
        timing = "immediately" if rul <= 5 else f"within {rul} cycles, before end of life"
    elif risk == "Watch":
        action = "Plan battery replacement and increase monitoring"
        timing = f"within ~{rul} cycles; begin procurement now"
    else:
        action = "Continue normal operation"
        timing = f"next health check in ~{max(rul // 3, 10)} cycles"

    cite_str = "; ".join(c["source"] for c in citations[:2]) if citations else "maintenance policy"
    template = (
        f"{action} for {asset['name']} ({asset.get('asset_type', 'asset')}). "
        f"State of Health is {asset['soh'] * 100:.1f}% ({risk}) with an estimated {rul} cycles of useful life remaining. "
        f"{diagnosis['probable_cause']} Recommended action: {action.lower()} {timing}. "
        f"Basis: {cite_str}."
    )

    prompt = (
        f"Asset: {asset['name']} ({asset.get('asset_type', 'asset')}). "
        f"SoH {asset['soh'] * 100:.1f}% ({risk}). RUL {rul} cycles. "
        f"Probable cause: {diagnosis['probable_cause']}\n"
        f"Retrieved guidance:\n"
        + "\n".join(f"- {c['source']}: {c['snippet']}" for c in citations)
        + "\n\nWrite a concise (3-4 sentence) maintenance recommendation for the fleet operator. "
        "State the action and timing clearly, cite the guidance by name, and do not invent facts."
    )
    llm_text = generate(prompt)

    return {"action": action, "timing": timing, "text": llm_text or template}, bool(llm_text)


def run(asset: dict):
    observations = monitor(asset)
    diagnosis, citations = diagnose(asset)
    recommendation, llm_used = recommend(asset, diagnosis, citations)
    return {
        "asset_id": asset["asset_id"],
        "name": asset["name"],
        "risk": asset["risk"],
        "observations": observations,
        "diagnosis": diagnosis,
        "recommendation": recommendation,
        "citations": citations,
        "llm_used": llm_used,
    }
