"""
Lightweight battery failure-mode knowledge graph.

Nodes: symptoms (observable conditions), causes (why degradation happens),
actions (what to do). Edges: symptom --explained_by--> cause --mitigated_by--> action.

The Diagnosis agent detects active symptoms from an asset's state, then traverses
this graph to explain the probable causes. This is what powers the "why is it
degrading" reasoning and keeps the logic auditable.
"""
import networkx as nx

SYMPTOMS = {
    "advanced_fade":      {"label": "Advanced capacity fade", "causes": ["cycle_aging", "end_of_life"]},
    "moderate_fade":      {"label": "Measurable capacity fade", "causes": ["cycle_aging"]},
    "approaching_eol":    {"label": "Approaching end of life", "causes": ["end_of_life"]},
    "thermal_stress":     {"label": "Elevated discharge temperature", "causes": ["thermal_stress"]},
    "high_cycles":        {"label": "High accumulated cycle count", "causes": ["cycle_aging"]},
    "rapid_recent_fade":  {"label": "Accelerating recent fade", "causes": ["thermal_stress", "cycle_aging"]},
}

CAUSES = {
    "cycle_aging": {
        "label": "Cycle aging",
        "desc": "Repeated charge/discharge cycles gradually consume active material and reduce usable capacity — the dominant, expected cause in an actively used fleet.",
    },
    "thermal_stress": {
        "label": "Thermal stress",
        "desc": "Elevated operating or discharge temperatures accelerate side reactions and internal-resistance growth, causing faster-than-expected fade.",
    },
    "end_of_life": {
        "label": "End of life",
        "desc": "Capacity has fallen close to the end-of-life threshold, where usable range, reliability and safety margins drop below requirements.",
    },
}

ACTIONS = {
    "replace_now":     {"label": "Schedule battery replacement", "priority": "Immediate", "cite": "replacement remaining useful life end of life"},
    "plan_replace":    {"label": "Plan replacement and increase monitoring", "priority": "Soon", "cite": "replacement planning monitoring interval watch band"},
    "procure":         {"label": "Begin battery procurement", "priority": "Soon", "cite": "procurement lead time avoid unplanned downtime"},
    "thermal_inspect": {"label": "Inspect thermal management / cooling path", "priority": "Soon", "cite": "elevated temperature thermal management cooling"},
    "reduce_load":     {"label": "Reduce load / avoid high-load duty", "priority": "Soon", "cite": "critical asset high-load duty precautions"},
    "monitor":         {"label": "Continue monitoring at standard interval", "priority": "Monitor", "cite": "healthy band routine inspection interval"},
}


def build_graph():
    g = nx.DiGraph()
    for sid, s in SYMPTOMS.items():
        g.add_node(("symptom", sid), kind="symptom", label=s["label"])
    for cid, c in CAUSES.items():
        g.add_node(("cause", cid), kind="cause", label=c["label"], desc=c["desc"])
    for sid, s in SYMPTOMS.items():
        for cid in s["causes"]:
            g.add_edge(("symptom", sid), ("cause", cid), rel="explained_by")
    return g


GRAPH = build_graph()


def causes_for(active_symptoms):
    """Traverse the graph: active symptoms -> ordered unique causes (with metadata)."""
    out = {}
    for sid in active_symptoms:
        node = ("symptom", sid)
        if node not in GRAPH:
            continue
        for _, cause_node in GRAPH.out_edges(node):
            cid = cause_node[1]
            out.setdefault(cid, CAUSES[cid])
    return out
