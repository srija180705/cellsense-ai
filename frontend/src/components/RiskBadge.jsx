function slug(risk) {
  return risk.toLowerCase().replace(/[^a-z0-9]+/g, "-").replace(/(^-|-$)/g, "");
}

export default function RiskBadge({ risk }) {
  return <span className={`badge badge-${slug(risk)}`}>{risk}</span>;
}
