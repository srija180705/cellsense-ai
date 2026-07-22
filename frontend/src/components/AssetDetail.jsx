import { useRef, useState, useEffect } from "react";
import {
  LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ReferenceLine,
} from "recharts";
import RiskBadge from "./RiskBadge.jsx";
import { getRecommendation } from "../api.js";

// Measure the container width ourselves — more reliable than ResponsiveContainer,
// which can commit a 0-width chart on first render.
function useContainerWidth(defaultWidth = 680) {
  const ref = useRef(null);
  const [width, setWidth] = useState(defaultWidth);
  useEffect(() => {
    const el = ref.current;
    if (!el) return;
    const update = () => setWidth(el.clientWidth || defaultWidth);
    update();
    const ro = new ResizeObserver(update);
    ro.observe(el);
    window.addEventListener("resize", update);
    return () => {
      ro.disconnect();
      window.removeEventListener("resize", update);
    };
  }, [defaultWidth]);
  return [ref, width];
}

function Metric({ label, value, accent }) {
  return (
    <div className="metric">
      <div className={`metric-value ${accent || ""}`}>{value}</div>
      <div className="metric-label">{label}</div>
    </div>
  );
}

export default function AssetDetail({ asset }) {
  const [chartRef, chartWidth] = useContainerWidth();
  const [reco, setReco] = useState(null);
  const [loadingReco, setLoadingReco] = useState(false);

  useEffect(() => {
    setReco(null);
  }, [asset?.asset_id]);

  async function generate() {
    setLoadingReco(true);
    try {
      setReco(await getRecommendation(asset.asset_id));
    } catch {
      /* ignore */
    } finally {
      setLoadingReco(false);
    }
  }

  if (!asset) return <div className="panel detail-panel empty">Select an asset to inspect</div>;

  const data = asset.history.map((h) => ({
    cycle: h.cycle,
    soh: +(h.soh * 100).toFixed(1),
  }));
  const minSoh = Math.min(...data.map((d) => d.soh));
  const yFloor = Math.max(0, Math.floor(minSoh / 10) * 10 - 5);

  return (
    <div className="panel detail-panel">
      <div className="detail-head">
        <div>
          <div className="detail-title">{asset.name}</div>
          <div className="detail-sub">
            {asset.asset_type} · {asset.cycles_observed} cycles observed · cell {asset.source_cell}
          </div>
        </div>
        <RiskBadge risk={asset.risk} />
      </div>

      <div className="metrics">
        <Metric label="State of Health" value={`${(asset.soh * 100).toFixed(1)}%`} />
        <Metric label="Predicted SoH" value={`${(asset.soh_pred * 100).toFixed(1)}%`} accent="teal" />
        <Metric label="Remaining Useful Life" value={`${asset.rul_cycles} cyc`} accent="amber" />
      </div>

      <div className="chart-title">State of Health over battery life</div>
      <div className="chart-wrap" ref={chartRef}>
        <LineChart width={chartWidth} height={280} data={data} margin={{ top: 10, right: 24, left: -6, bottom: 6 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#e5eaf0" />
          <XAxis dataKey="cycle" tick={{ fontSize: 12 }} stroke="#8a97a6" />
          <YAxis domain={[yFloor, 100]} tick={{ fontSize: 12 }} stroke="#8a97a6" tickFormatter={(v) => `${v}%`} />
          <Tooltip formatter={(v) => [`${v}%`, "SoH"]} labelFormatter={(c) => `Cycle ${c}`} />
          <ReferenceLine y={85} stroke="#E0A020" strokeDasharray="4 4" />
          <ReferenceLine y={78} stroke="#C0392B" strokeDasharray="4 4" />
          <Line type="monotone" dataKey="soh" stroke="#2E8B8B" strokeWidth={2.5} dot={false} isAnimationActive={false} />
        </LineChart>
      </div>

      <div className="reco-placeholder">
        <div className="reco-head">
          <div className="reco-title">AI Maintenance Recommendation</div>
          {!reco && (
            <button className="reco-btn" onClick={generate} disabled={loadingReco}>
              {loadingReco ? "Analysing…" : "Generate"}
            </button>
          )}
        </div>

        {!reco && !loadingReco && (
          <div className="reco-body">
            Runs the agent pipeline — Monitor → Diagnose → Recommend — grounded in the
            maintenance knowledge base.
          </div>
        )}

        {reco && (
          <>
            <div className="reco-text">{reco.recommendation.text}</div>
            <div className="reco-cites">
              {reco.citations.map((c, i) => (
                <span key={i} className="cite-chip" title={c.snippet}>
                  {c.source}
                </span>
              ))}
            </div>
            <div className="reco-tag">
              {reco.llm_used ? "LLM-composed" : "rule-composed"} · grounded in{" "}
              {reco.citations.length} sources
            </div>
          </>
        )}
      </div>
    </div>
  );
}
