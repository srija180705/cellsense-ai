// API client. Empty base -> uses the Vite dev proxy (/api -> :8000).
const BASE = import.meta.env.VITE_API_URL || "";

export async function getFleet() {
  const r = await fetch(`${BASE}/api/fleet`);
  if (!r.ok) throw new Error("Failed to load fleet");
  return r.json();
}

export async function getAsset(id) {
  const r = await fetch(`${BASE}/api/assets/${id}`);
  if (!r.ok) throw new Error("Failed to load asset");
  return r.json();
}

export async function getRecommendation(id) {
  const r = await fetch(`${BASE}/api/assets/${id}/recommend`, { method: "POST" });
  if (!r.ok) throw new Error("Failed to generate recommendation");
  return r.json();
}
