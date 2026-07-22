import RiskBadge from "./RiskBadge.jsx";

export default function FleetTable({ assets, selected, onSelect }) {
  return (
    <div className="panel fleet-panel">
      <div className="panel-title">Fleet — ranked by risk</div>
      <div className="fleet-list">
        <div className="fleet-row fleet-head">
          <span>Asset</span>
          <span>SoH</span>
          <span>RUL</span>
          <span>Status</span>
        </div>
        {assets.map((a) => (
          <div
            key={a.asset_id}
            className={`fleet-row ${selected === a.asset_id ? "active" : ""}`}
            onClick={() => onSelect(a.asset_id)}
          >
            <span className="mono">{a.name}</span>
            <span>{(a.soh * 100).toFixed(1)}%</span>
            <span>{a.rul_cycles} cyc</span>
            <span>
              <RiskBadge risk={a.risk} />
            </span>
          </div>
        ))}
      </div>
    </div>
  );
}
