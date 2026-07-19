# CellSense AI — Industrial EV Fleet Asset Intelligence

**ET AI Hackathon 2026 · Problem Statement 3 — AI for Industrial EV Supply Chain & Asset Intelligence**

CellSense AI is an **Asset Performance Management (APM)** platform for industrial and commercial EV fleets. It predicts each battery's **State of Health (SoH)** and **Remaining Useful Life (RUL)** from real cell-cycling data, ranks the fleet by risk, and turns every prediction into a **grounded, cited maintenance decision** using a multi-agent reasoning layer over OEM manuals and safety standards.

> The battery is the asset. CellSense AI makes its invisible degradation visible — and actionable.

---

## Key result (Phase P1 — ML core)

Cross-cell evaluation (train on 3 cells, test on a **completely unseen** cell, B0018):

| Model | Metric | Result |
|---|---|---|
| **SoH estimation** | RMSE | **0.0275 SoH** (~2.75% error) |
| | R² | **0.89** |
| **RUL prediction** | RMSE | **16.5 cycles** |
| | R² | **0.74** |

These are **generalisation** numbers — the model never saw the test cell during training. Metrics are written to `models/artifacts/metrics.json`.

---

## Architecture

![CellSense AI System Architecture](CellSense_AI_Architecture_Diagram.png)

A provable ML core (SoH/RUL) + a deterministic rule engine (risk banding) + an agentic RAG layer that grounds every recommendation in real documents.

---

## Project structure

```
ET/
├── utils/                    # shared parsing & feature engineering
│   ├── mat_parser.py         #   NASA .mat loader
│   └── features.py           #   health-indicator feature extraction
├── models/
│   ├── training/
│   │   ├── build_dataset.py  #   raw .mat -> processed feature table
│   │   └── train.py          #   train + cross-cell evaluate SoH & RUL
│   └── artifacts/            #   trained models + metrics.json (git-ignored)
├── datasets/                 # raw + processed data (git-ignored, see below)
├── backend/                  # FastAPI service            (Phase P2 — planned)
├── frontend/                 # React dashboard            (Phase P4 — planned)
├── agents/                   # Monitor/Diagnose/Recommend (Phase P3 — planned)
├── rag/                      # document corpus + retrieval(Phase P3 — planned)
├── requirements.txt
└── docs/                     # solution document, diagram, deck
```

---

## Data (not committed — download separately)

The NASA battery data is large (200 MB+) and is **git-ignored**. Download it yourself:

1. Get the NASA PCoE Li-ion Battery Aging dataset:
   `https://phm-datasets.s3.amazonaws.com/NASA/5.+Battery+Data+Set.zip`
   (mirror: [NASA PCoE repository](https://www.nasa.gov/intelligent-systems-division/discovery-and-systems-health/pcoe/pcoe-data-set-repository/) · [Kaggle](https://www.kaggle.com/datasets/patrickfleith/nasa-battery-dataset))
2. Extract the nested zips and place the `.mat` cell files in:
   `datasets/NASA_Battery/mat/` (e.g. `B0005.mat`, `B0006.mat`, `B0007.mat`, `B0018.mat`).

---

## Setup & run

```bash
# 1. Create a virtual environment
python -m venv .venv
.venv\Scripts\activate        # Windows
# source .venv/bin/activate   # macOS / Linux

# 2. Install dependencies
pip install -r requirements.txt

# 3. Build the processed dataset from the raw cells
python models/training/build_dataset.py

# 4. Train and evaluate the SoH + RUL models
python models/training/train.py
```

Step 4 prints the accuracy metrics and saves models to `models/artifacts/`.

---

## Roadmap

| Phase | Scope | Status |
|---|---|---|
| **P1** | Data parsing + SoH/RUL ML core (provable RMSE) | ✅ Done |
| P2 | FastAPI backend + database serving predictions | ⏳ Next |
| P3 | RAG corpus + 3-agent grounded recommendation | ⏳ Planned |
| P4 | React fleet dashboard (risk ranking, drill-down) | ⏳ Planned |
| P5 | End-to-end integration | ⏳ Planned |
| P6 | Demo polish, deck, video | ⏳ Planned |

---

## A note on data integrity

All predictions run on **real battery-cell degradation data** (NASA PCoE). The fleet
layer (asset IDs, routes, duty cycles) is **illustrative and clearly labelled** — the
machine-learning results are honest and reproducible.

## Team

| Member | Role |
|---|---|
| _[Name 1]_ | ML Lead |
| _[Name 2]_ | Backend + Agents |
| _[Name 3]_ | Frontend |
| _[Name 4]_ | AI/NLP + Integration + Demo |
