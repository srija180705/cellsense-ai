const BAND_META = [
  { key: "Critical", cls: "critical" },
  { key: "Near End-of-Life", cls: "near-end-of-life" },
  { key: "Watch", cls: "watch" },
  { key: "Early Wear", cls: "early-wear" },
  { key: "Healthy", cls: "healthy" },
];

export default function SummaryCards({ summary }) {
  const bands = summary.bands || {};
  return (
    <div className="cards">
      <div className="card card-total">
        <div className="card-value">{summary.total}</div>
        <div className="card-label">Total Assets</div>
      </div>
      {BAND_META.map((b) => (
        <div key={b.key} className={`card card-${b.cls}`}>
          <div className="card-value">{bands[b.key] ?? 0}</div>
          <div className="card-label">{b.key}</div>
        </div>
      ))}
    </div>
  );
}
