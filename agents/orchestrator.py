"""
Three-agent pipeline: Monitor -> Diagnose (knowledge-graph + RAG) -> Recommend.

- Monitor       : summarises the asset's current condition and flags concerns.
- Diagnosis     : detects symptoms, traverses the failure-mode knowledge graph to
                  explain probable causes, and quantifies WHY it is degrading
                  (fade rate, thermal state, cycle count, model drivers).
- Recommendation: produces a prioritised, grounded, cited action plan
                  (LLM-polished if available, deterministic otherwise).
"""
from rag.retriever import retrieve
from agents.llm import generate
from agents.knowledge_graph import SYMPTOMS, ACTIONS, causes_for

THERMAL_MAX_C = 41.0


# ---------- helpers ----------
def _fade_rate(history):
    """Early-life vs recent SoH decline (fade per cycle). Positive = capacity dropping."""
    n = len(history)
    if n < 6:
        return {"recent": 0.0, "early": 0.0, "accelerating": False}
    soh = [h["soh"] for h in history]
    w = max(5, n // 4)
    early = (soh[0] - soh[w]) / w
    recent = (soh[-1 - w] - soh[-1]) / w
    return {"recent": recent, "early": early,
            "accelerating": recent > early * 1.3 and recent > 0}


def _detect_symptoms(asset, history, fleet_stats, fade):
    syms, evidence = [], {}
    soh = asset["soh"] * 100
    rul = asset["rul_cycles"]

    if soh < 78:
        syms.append("advanced_fade")
        evidence["advanced_fade"] = f"SoH {soh:.1f}% is below the 78% action threshold."
    elif soh < 85:
        syms.append("moderate_fade")
        evidence["moderate_fade"] = f"SoH {soh:.1f}% shows measurable fade."

    if rul <= 10:
        syms.append("approaching_eol")
        evidence["approaching_eol"] = f"Only ~{rul} cycles of predicted useful life remain."

    mt = asset.get("max_temp", 0)
    if mt > THERMAL_MAX_C:
        syms.append("thermal_stress")
        evidence["thermal_stress"] = f"Peak discharge temperature {mt:.1f} C exceeds the ~41 C guidance."

    cyc = asset["cycles_observed"]
    if cyc > fleet_stats.get("cycles_median", 0):
        syms.append("high_cycles")
        evidence["high_cycles"] = f"{cyc} cycles observed, above the fleet median ({fleet_stats.get('cycles_median', 0):.0f})."

    if fade["accelerating"]:
        syms.append("rapid_recent_fade")
        evidence["rapid_recent_fade"] = (
            f"Recent fade ({fade['recent'] * 100:.2f}%/cycle) exceeds early-life fade "
            f"({fade['early'] * 100:.2f}%/cycle)."
        )
    return syms, evidence


def monitor(asset):
    obs = [
        f"State of Health at {asset['soh'] * 100:.1f}% ({asset['risk']}).",
        f"Predicted remaining useful life: {asset['rul_cycles']} cycles.",
        f"{asset['cycles_observed']} discharge cycles observed.",
    ]
    if asset.get("max_temp", 0) > THERMAL_MAX_C:
        obs.append(f"Elevated discharge temperature ({asset['max_temp']:.1f} C).")
    return obs


def _select_actions(asset, syms):
    risk = asset["risk"]
    rul = asset["rul_cycles"]
    chosen = []  # list of (action_id, reason)

    if "advanced_fade" in syms or "approaching_eol" in syms:
        chosen.append(("replace_now", f"SoH and RUL indicate end of life (~{rul} cycles left)."))
        chosen.append(("procure", "Start procurement now so lead time does not cause downtime."))
    elif "moderate_fade" in syms:
        chosen.append(("plan_replace", "Degradation is progressing; plan replacement and budget now."))

    if "thermal_stress" in syms:
        chosen.append(("thermal_inspect", "Peak discharge temperature is elevated; check cooling and load."))
        if risk in ("Critical", "Near End-of-Life"):
            chosen.append(("reduce_load", "Avoid high-load duty until inspected or replaced."))

    if not chosen:
        chosen.append(("monitor", "Health is within normal limits; continue standard monitoring."))

    actions = []
    for aid, reason in chosen:
        meta = ACTIONS[aid]
        cite = retrieve(meta["cite"], k=1)
        actions.append({
            "action": meta["label"],
            "priority": meta["priority"],
            "reason": reason,
            "citation": cite[0]["source"] if cite else None,
            "snippet": cite[0]["snippet"] if cite else None,
        })
    return actions


def _explanation(asset, syms, evidence, fade, causes, model_drivers):
    drivers = [{"factor": SYMPTOMS[s]["label"], "evidence": evidence[s]} for s in syms]
    cause_list = [{"cause": c["label"], "why": c["desc"]} for c in causes.values()]

    soh = asset["soh"] * 100
    narrative = (
        f"{asset['name']} is at {soh:.1f}% State of Health ({asset['risk']}) after "
        f"{asset['cycles_observed']} discharge cycles. "
    )
    if cause_list:
        narrative += "Primary degradation drivers: " + ", ".join(c["cause"].lower() for c in cause_list) + ". "
    narrative += ("Recent degradation is accelerating relative to early life."
                  if fade["accelerating"]
                  else "Degradation is following an expected trajectory.")

    return {
        "narrative": narrative,
        "cycles_observed": asset["cycles_observed"],
        "fade_rate_recent_pct_per_cycle": round(fade["recent"] * 100, 3),
        "fade_rate_early_pct_per_cycle": round(fade["early"] * 100, 3),
        "accelerating": fade["accelerating"],
        "drivers": drivers,
        "causes": cause_list,
        "model_drivers": model_drivers,
    }


def _compose_text(asset, actions, causes, citations, llm_enabled=True):
    soh = asset["soh"] * 100
    rul = asset["rul_cycles"]
    lead = actions[0]
    template = (
        f"{asset['name']} ({asset.get('asset_type', 'asset')}) is {asset['risk']} at {soh:.1f}% SoH "
        f"with ~{rul} cycles of useful life remaining. "
        f"Priority action: {lead['action'].lower()} — {lead['reason']} "
    )
    if causes:
        template += "Likely cause: " + ", ".join(c["label"].lower() for c in causes.values()) + ". "
    if citations:
        template += "Basis: " + "; ".join(sorted({c["source"] for c in citations})[:2]) + "."

    if not llm_enabled:
        return template, False

    prompt = (
        f"Asset {asset['name']} ({asset.get('asset_type', 'asset')}): SoH {soh:.1f}% ({asset['risk']}), "
        f"RUL {rul} cycles.\n"
        f"Probable causes: {', '.join(c['label'] for c in causes.values()) or 'nominal aging'}.\n"
        "Recommended actions:\n"
        + "\n".join(f"- [{a['priority']}] {a['action']}: {a['reason']} (source: {a['citation']})" for a in actions)
        + "\n\nWrite a concise (3-4 sentence) maintenance recommendation for the fleet operator. "
        "State the priority action and timing, mention the cause, cite sources by name, invent nothing."
    )
    llm = generate(prompt)
    return (llm or template), bool(llm)


# ---------- entrypoint ----------
def run(asset, fleet_stats=None, model_drivers=None):
    fleet_stats = fleet_stats or {}
    model_drivers = model_drivers or []
    history = asset.get("history", [])

    fade = _fade_rate(history)
    syms, evidence = _detect_symptoms(asset, history, fleet_stats, fade)
    causes = causes_for(syms)
    actions = _select_actions(asset, syms)

    # Unique citations across actions
    seen, citations = set(), []
    for a in actions:
        if a["citation"] and a["citation"] not in seen:
            seen.add(a["citation"])
            citations.append({"source": a["citation"], "snippet": a["snippet"]})

    explanation = _explanation(asset, syms, evidence, fade, causes, model_drivers)
    text, llm_used = _compose_text(asset, actions, causes, citations)

    return {
        "asset_id": asset["asset_id"],
        "name": asset["name"],
        "risk": asset["risk"],
        "observations": monitor(asset),
        "explanation": explanation,
        "recommendation": {"actions": actions, "text": text},
        "citations": citations,
        "llm_used": llm_used,
    }
