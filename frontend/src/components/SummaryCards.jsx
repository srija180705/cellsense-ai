export default function SummaryCards({ summary }) {
  const cards = [
    { label: "Total Assets", value: summary.total, cls: "total" },
    { label: "Critical", value: summary.critical, cls: "critical" },
    { label: "Watch", value: summary.watch, cls: "watch" },
    { label: "Healthy", value: summary.healthy, cls: "healthy" },
  ];
  return (
    <div className="cards">
      {cards.map((c) => (
        <div key={c.label} className={`card card-${c.cls}`}>
          <div className="card-value">{c.value}</div>
          <div className="card-label">{c.label}</div>
        </div>
      ))}
    </div>
  );
}
