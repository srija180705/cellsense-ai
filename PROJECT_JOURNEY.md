# CellSense AI — Project Journey & Collaborator Guide

*A complete, precise walkthrough of what this project is, why we chose it, what we
built, and how — written so a new collaborator can get fully up to speed.*

> **Accuracy note:** This document describes what actually exists in the repository
> as of now. Where our written solution document proposes something we have **not
> yet implemented** (e.g. a SQL database, a vector database), it is called out
> explicitly in the section *"Design vs. what is actually built."* Nothing here is
> aspirational unless labelled as such.

---

## 1. The hackathon context

- **Event:** ET AI Hackathon 2026 (branded "AI Hackathon 2.0"), organised by The Economic Times.
- **Prize pool:** ₹10 lakh. **Industry partner:** **Octave** (a 2026 software spin-off from Hexagon AB).
- **Format:** an online MCQ round shortlists teams; shortlisted teams enter a **Phase-2 build sprint**, pick **one** problem statement, and build a working prototype + architecture + demo video.
- **Judging criteria (fixed weights):** Innovation 25% · Business Impact 25% · Technical Excellence 20% · Scalability 15% · User Experience 15%.

**Why the partner matters:** Octave's business is industrial intelligence. Its divisions include **Asset Lifecycle Intelligence / Asset Performance Management (APM)**, **Safety-Infrastructure-Geospatial**, and **ETQ (quality management)**. Judges from Octave reward problems close to their domain — this directly influenced our choice (see §5).

---

## 2. The problem statement we chose — PS3

**"AI for Industrial EV Supply Chain & Asset Intelligence: Accelerating Net Zero."**
Theme: *Sustainability / EV Manufacturing / Asset Performance Management / Supply Chain.*

The statement is deliberately broad and has **two prongs**:

1. **Industrial EV fleet asset intelligence** — help asset-intensive operators manage EV fleets (battery lifecycle, degradation, maintenance) with the rigour they apply to conventional equipment.
2. **EV manufacturing supply chain** — help EV makers manage battery-material sourcing, quality traceability, and multi-tier supplier risk.

**We committed to prong 1 only (fleet APM).** Reason: doing both fragments the narrative and the timeline; a single sharp story scores higher than two half-finished ones (this is a scoping decision, explained in §6).

---

## 3. The real-world problem (why it genuinely matters)

The figures below are quoted in the official problem statement:

- India registered **over 2 million EVs in FY2025**, yet EVs are still **<7% of total vehicle sales**.
- In **industrial/commercial segments** (freight, mining, intra-plant logistics, construction) penetration is **below 2.5%**.
- The barrier is **no longer mainly financial** — incentives (FAME-II, >₹10,000 cr) and total-cost-of-ownership parity with diesel are close.
- **The real bottleneck is operational:** fleet operators lack the *asset-intelligence tooling* to manage EV batteries — the single most valuable and failure-prone component — the way they manage other industrial assets.
- India targets **30% commercial-EV penetration by 2030**; closing this asset-intelligence gap is on the critical path.

**Concrete real-life example.** Picture a mining or logistics operator running a fleet of electric haul trucks and forklifts. Each vehicle's battery pack costs a large fraction of the vehicle (roughly 30–40%). Today the operator has **no reliable view of how much life each battery has left**. So two bad things happen: (a) a battery fails mid-shift with no warning → **unplanned downtime**; or (b) the operator replaces batteries too early "to be safe" → **wasted capital**. There is no tool that says *"this specific asset will cross end-of-life in N cycles — act now, and here's exactly what to do."* That gap is what our project targets.

**Stakeholders who benefit:** fleet operations managers, maintenance engineers, sustainability/net-zero officers, finance/capital planners, and battery OEMs.

---

## 4. Why we chose PS3 over the other statements

The hackathon offered 8 statements. We evaluated all of them and narrowed using four practical filters. This is the honest decision trail:

1. **Data availability (decisive filter).** A hackathon lives or dies on whether real data is obtainable for free. PS3's core (battery health) has **benchmark-grade, free, public datasets** (NASA, Oxford, MIT). By contrast, other strong statements failed here — e.g. the industrial-safety statement has **no public dataset** fusing sensors + permits + logs (it would have to be fabricated), and the energy-supply-chain statement needed live ship-tracking (AIS) data that is only free if you run your own receiver. **We have zero budget**, so "free and real" was non-negotiable.
2. **Partner alignment.** PS3's core discipline — **Asset Performance Management** — *is* Octave's flagship business. A judge from Octave sees their own product.
3. **Judging math.** PS3 scores well on the two heaviest criteria: Business Impact (net-zero, capital, downtime) and Technical Excellence (a *provable* accuracy number from real data).
4. **Feasibility for our skills and time.** The battery model is time-series/tabular ML (learnable quickly), and the differentiator (a natural-language recommendation layer) plays to strength in ML/NLP.

**The honest trade-off we accepted:** battery State-of-Health prediction is a *well-studied* topic, so a plain prediction model would look ordinary (weak on the 25% Innovation score). We deliberately fixed that weakness with the decision-intelligence layer described next.

---

## 5. Our solution — CellSense AI (what it is)

**CellSense AI is an Asset Performance Management platform for industrial EV fleets.** It does three things, in order:

1. **Predicts** each battery asset's **State of Health (SoH)** and **Remaining Useful Life (RUL)** from real cell data (machine learning).
2. **Ranks the fleet by risk** using a deterministic rule engine (Healthy / Watch / Critical).
3. **Recommends a grounded, cited maintenance action** for any asset via a small multi-agent pipeline that retrieves supporting text from a maintenance knowledge base.

The demo arc is: *see which asset fails next → open it → see its real degradation curve and predicted life → click Generate → get a cited "replace within N cycles, because…" recommendation.*

---

## 6. The novelty — what makes it stand out (stated honestly)

We are **not** claiming to have invented battery SoH prediction — that is a mature research area. Our differentiation, and the reason it stands out in this hackathon, is **integration and framing**:

- **Decision-intelligence *over* prediction.** Most battery projects stop at a number ("SoH = 74%"). We close the loop to a **decision**: probable cause → severity → a specific action with timing → grounded in a **cited** source. This is the actual "Asset Performance Management" value proposition, not just a forecast.
- **Grounding + citations for trust.** The recommendation is not a free-form LLM guess. Safety-critical banding is done by a **deterministic rule engine** (no hallucination), and the wording is **grounded in retrieved documents with citations** — so a maintenance engineer can audit *why*.
- **Fleet-level prioritisation.** The system ranks *which asset to act on first* across a fleet — the operator's real question — rather than analysing a single cell in isolation.
- **Honest, real-data core.** The predictions run on **real NASA battery measurements**, so the accuracy number is defensible rather than a mock.

In short: the *prediction* earns credibility; the *grounded, cited decision layer* is what a plain battery model does not provide, and is our claim to Innovation.

---

## 7. The dataset — exactly what we use

- **Source:** **NASA Prognostics Center of Excellence (PCoE) Li-ion Battery Aging Dataset** — a public, free dataset of 18650 lithium-ion cells cycled to end-of-life.
- **How obtained:** downloaded as a single 200 MB zip from the public PHM datasets S3 bucket (`phm-datasets.s3.amazonaws.com/NASA/5.+Battery+Data+Set.zip`), then the nested archives were extracted into `datasets/NASA_Battery/mat/`.
- **Contents:** **34 real cells** (`B0005.mat` … `B0056.mat`).
- **Core cells we build on:** the four room-temperature benchmark cells **B0005, B0006, B0007, B0018** — the standard set used across the SoH/RUL research literature.
- **What each cell contains:** a list of cycles (charge / discharge / impedance). Every **discharge** cycle carries measured arrays — `Voltage_measured`, `Current_measured`, `Temperature_measured`, `Current_load`, `Voltage_load`, `Time` — plus a scalar `Capacity` (Ah), which is the ground-truth that degrades over life.
- **Example (verified):** B0005 has 168 discharge cycles; its capacity fades from **1.856 Ah → 1.325 Ah (~29% fade)**.

**What is real vs. illustrative (important for honesty):**
- **Real:** every battery measurement, every SoH/RUL prediction, and the accuracy metrics.
- **Illustrative (clearly labelled):** the "fleet wrapper" — we present the cells as named vehicles (Haul Truck, Forklift, etc.). Each vehicle *is* a real cell observed to a chosen point in its life; the vehicle names/types are cosmetic framing and never feed a prediction. The maintenance knowledge base (see §11) is also illustrative reference text, meant to be replaced by real OEM manuals.

---

## 8. How we built it, step by step

Build order was **P1 → P2 → P4 → P3** (model first, then serve it, then visualise it, then add the intelligence layer).

### Phase P1 — the machine-learning core (the provable heart)

1. **Parsing** (`utils/mat_parser.py`): loads each `.mat` with `scipy.io.loadmat(simplify_cells=True)`, and returns the discharge cycles that carry a valid capacity.
2. **Feature engineering** (`utils/features.py`): from each discharge cycle's raw signals we compute **8 health-indicator features** — `mean_voltage`, `min_voltage`, `mean_temp`, `max_temp`, `temp_rise`, `discharge_time`, `time_v_window` (time in the mid-voltage window), and `volt_drop_rate`. These are *curve-shape* indicators that change as a cell ages.
3. **Dataset build** (`models/training/build_dataset.py`): iterates the 4 core cells, and for each discharge cycle records the features plus two targets:
   - **SoH** = capacity ÷ that cell's initial capacity.
   - **RUL** = discharge cycles remaining until the cell reaches end-of-life (capacity ≤ **1.4 Ah**).
   Output: `datasets/processed/cell_features.csv` (636 rows).
4. **Training + evaluation** (`models/training/train.py`): trains **XGBoost** regressors. Evaluation is **cross-cell** — train on B0005/B0006/B0007, **test on the completely unseen cell B0018** — which proves generalisation rather than memorisation. **Results (verified):**
   - **SoH:** RMSE **0.0275** (~2.75% error), MAE 0.023, **R² 0.89**.
   - **RUL:** RMSE **16.5 cycles**, MAE 13.4, **R² 0.74**.
   Artifacts saved to `models/artifacts/` (`soh_model.pkl`, `rul_model.pkl`, `metrics.json`).

### Phase P2 — the backend API

1. **Rule engine** (`backend/rules.py`): deterministic risk banding — **Healthy ≥ 85%**, **Watch 78–85%**, **Critical < 78%** SoH. Safety-critical banding is intentionally *not* left to any model.
2. **Fleet builder** (`models/training/build_fleet.py`): builds the demo fleet from the **4 clean core cells**, each **snapshotted at several life stages** (30%, 55%, 75%, 100% of life). This yields **16 assets** with a realistic spread of health (SoH range 0.57–1.00), all from real data. Each asset is tagged with a type (Haul Truck / Forklift / Loader / Yard Shuttle). Output: `datasets/processed/fleet_features.csv`.
   *Why snapshots:* using every cell's *last* cycle made everything look end-of-life; snapshots give a realistic operating fleet. (We also found some higher-numbered NASA cells produce invalid SoH because their first cycle isn't a full-capacity reference — so the fleet is restricted to the 4 verified-clean cells.)
3. **Fleet service** (`backend/fleet_service.py`): loads the two trained models + the fleet CSV, and produces the fleet overview and per-asset detail. SoH shown is **measured**; SoH/RUL predictions come from the models.
4. **API** (`backend/main.py`, FastAPI): `GET /api/health`, `GET /api/fleet` (ranked, with a risk summary), `GET /api/assets/{id}` (detail + full SoH history), and `POST /api/assets/{id}/recommend` (added in P3).

### Phase P4 — the dashboard

- **Stack:** Vite + React + Recharts (`frontend/`).
- **Views:** summary cards (total / critical / watch / healthy), a **risk-ranked asset table**, and an **asset detail** panel with measured SoH, predicted SoH, RUL, and a **State-of-Health degradation curve** (with Watch/Critical threshold lines).
- The Vite dev server proxies `/api` to the backend, so there is no CORS setup during development.
- **Two real bugs found and fixed here:** (a) impossible SoH values from bad cells → fixed by restricting to clean core cells; (b) a blank chart from Recharts' `ResponsiveContainer` committing 0 width → fixed by measuring the container width explicitly.

### Phase P3 — the agent recommendation layer (the differentiator)

1. **Knowledge base** (`rag/corpus/`): 4 illustrative maintenance/safety documents (SoH thresholds, capacity-fade causes, replacement policy, thermal & safety), split into **16 citable sections**.
2. **Retriever** (`rag/retriever.py`): **TF-IDF** retrieval (scikit-learn) over those sections — runs offline with zero downloads; returns the top matching sections with a citation string.
3. **Agents** (`agents/orchestrator.py`): a three-step pipeline —
   - **Monitor** — summarises the asset's condition, flags concerns (e.g. elevated discharge temperature > 41 °C).
   - **Diagnose** — infers probable cause + severity from the asset state, and **retrieves supporting guidance**.
   - **Recommend** — composes a grounded action (what + when) with citations.
4. **Optional LLM** (`agents/llm.py`): if a free key/model is available (Groq free tier via `GROQ_API_KEY`, or a local Ollama server) it polishes the wording; **otherwise a deterministic template is used**. The system is fully functional with **no LLM and no paid API**. The response field `llm_used` reports which path ran.
5. **Frontend:** a **Generate** button on each asset calls the recommend endpoint and shows the recommendation text plus **citation chips**.

---

## 9. Architecture — how the pieces talk

```
React dashboard (Vite, :5173)
        │  REST/JSON (/api proxied to :8000)
        ▼
FastAPI backend (:8000)
   ├── fleet_service ──► XGBoost models (SoH/RUL, .pkl)  + fleet CSV
   ├── rules (risk banding)
   └── agent orchestrator ──► TF-IDF retriever ──► rag/corpus (docs)
                          └─► optional LLM (Groq/Ollama) or template
```

- **Prediction** is machine learning (XGBoost).
- **Risk banding** is a deterministic rule engine.
- **Recommendation wording** is retrieval-grounded, optionally LLM-polished.
- Data is read from **CSV files** and **`.pkl` model artifacts** on disk.

---

## 10. Technologies & techniques used (and why)

| Area | Technology / technique | Why we used it |
|---|---|---|
| Language | Python 3.10+ | Same language for data, ML, and backend |
| Data parsing | SciPy (`loadmat`) | NASA data ships as MATLAB `.mat` |
| Data handling | NumPy, pandas | Feature tables, CSV I/O |
| ML model | **XGBoost** (scikit-learn fallback) | Reliable, fast, accurate on tabular data; provable RMSE |
| Model persistence | joblib | Save/load `.pkl` artifacts |
| Backend | **FastAPI** + Uvicorn | Fast to build REST APIs in Python |
| Retrieval (RAG) | **TF-IDF** (scikit-learn) | Offline, zero-download semantic-ish retrieval |
| Agents | Custom 3-agent orchestrator | Monitor → Diagnose → Recommend |
| LLM (optional) | Groq free tier / local Ollama | Free prose polishing; not required |
| Frontend | **React 18 + Vite 5** | Fast, standard SPA tooling |
| Charts | **Recharts** | SoH degradation line chart |
| Packaging | Python venv, **Docker** (Dockerfile + compose) | One-command local run and containerised run |
| Version control | Git | Source management |

**Techniques worth calling out:** cross-cell evaluation (train on some cells, test on an unseen one) to prove generalisation; curve-based feature engineering; deterministic rule banding to keep safety decisions out of the model; retrieval-augmented, citation-grounded recommendations to keep the language trustworthy.

---

## 11. Design vs. what is actually built (read this to avoid confusion)

Our formal **solution document** (`CellSense_AI_Solution_Document.pdf`) proposes an ideal architecture. A few items in it are **planned, not yet implemented** — the running code uses simpler, equivalent choices:

| Item in the solution document | What the code actually uses now |
|---|---|
| Relational database (SQLite / Postgres) | **CSV files** on disk (`cell_features.csv`, `fleet_features.csv`) |
| Vector database (ChromaDB) + MiniLM embeddings | **TF-IDF** retrieval (scikit-learn) |
| Knowledge graph | **Not used** (was intentionally out of scope) |
| LLM always in the loop | **LLM optional**; deterministic template by default |

None of these change the demo behaviour; they are pragmatic substitutions for hackathon speed and zero cost. Swapping in a real DB or a vector store later would not require redesigning the system.

---

## 12. Current status

**Working today, end-to-end:** real data → trained SoH/RUL models (verified metrics) → fleet API → dashboard → grounded, cited recommendation.

- **Phases done:** P1 (ML core) ✅, P2 (backend) ✅, P4 (dashboard) ✅, P3 (agents/RAG) ✅.
- **Not yet done:** P6 (demo polish — pitch deck, demo video, run-through). Optional: enable a free LLM key for nicer prose; improve the RUL model (R² 0.74); add Oxford dataset for extra cross-dataset validation.

---

## 13. Project structure

```
ET/
├── utils/            mat_parser.py, features.py
├── models/
│   ├── training/     build_dataset.py, train.py, build_fleet.py
│   └── artifacts/    trained models + metrics.json (git-ignored)
├── backend/          main.py, fleet_service.py, rules.py (FastAPI)
├── agents/           orchestrator.py, llm.py (3-agent pipeline)
├── rag/              retriever.py + corpus/ (knowledge base)
├── frontend/         React + Vite + Recharts dashboard
├── datasets/         NASA .mat data + processed CSVs (git-ignored)
├── deployment/       Dockerfile, docker-compose.yml, entrypoint.sh
├── setup / run scripts (.ps1 / .sh)
├── requirements.txt
└── docs: solution document (pdf/docx), architecture diagram, this file
```

---

## 14. How to run it (for a new collaborator)

**Prerequisites:** Python 3.10+, Node.js, and the NASA data downloaded into `datasets/NASA_Battery/mat/` (see §7).

```powershell
# Windows
.\setup.ps1          # once: creates .venv, installs Python deps
.\run_backend.ps1    # terminal 1: trains models on first run, serves API on :8000
.\run_frontend.ps1   # terminal 2: dashboard on http://localhost:5173
```

(macOS/Linux: `bash setup.sh`, `bash run_backend.sh`, `bash run_frontend.sh`. Or `cd deployment && docker compose up --build`.)

Then open **http://localhost:5173**, click an asset, and click **Generate** to see the full pipeline in action.

---

## 15. Integrity summary (how to talk about this honestly)

- All predictions run on **real NASA battery data**; the metrics are genuine cross-cell generalisation results.
- The **fleet wrapper** (vehicle names/types) and the **maintenance knowledge base** are **illustrative and clearly labelled** — designed to be replaced with a real fleet and real OEM manuals.
- The novelty claim is **integration and grounded decision-making for fleet APM**, not a new battery-prediction algorithm. State it that way — it is both accurate and stronger.
