import { useEffect, useState } from "react";
import { getFleet, getAsset } from "./api.js";
import SummaryCards from "./components/SummaryCards.jsx";
import FleetTable from "./components/FleetTable.jsx";
import AssetDetail from "./components/AssetDetail.jsx";

export default function App() {
  const [fleet, setFleet] = useState(null);
  const [selected, setSelected] = useState(null);
  const [asset, setAsset] = useState(null);
  const [error, setError] = useState(null);

  useEffect(() => {
    getFleet()
      .then((f) => {
        setFleet(f);
        if (f.assets.length) setSelected(f.assets[0].asset_id);
      })
      .catch(() => setError("Cannot reach the backend on :8000. Start it with run_backend."));
  }, []);

  useEffect(() => {
    if (selected) getAsset(selected).then(setAsset).catch(() => {});
  }, [selected]);

  return (
    <div className="app">
      <header className="topbar">
        <div className="brand">
          CellSense<span className="brand-ai">AI</span>
        </div>
        <div className="tagline">Industrial EV Fleet Asset Intelligence</div>
      </header>

      {error && <div className="error">{error}</div>}

      {fleet && (
        <>
          <SummaryCards summary={fleet.summary} />
          <div className="main-grid">
            <FleetTable assets={fleet.assets} selected={selected} onSelect={setSelected} />
            <AssetDetail asset={asset} />
          </div>
          <footer className="footer">
            Predictions run on real NASA battery-cell data · SoH shown is measured, RUL is model-predicted
          </footer>
        </>
      )}

      {!fleet && !error && <div className="loading">Loading fleet…</div>}
    </div>
  );
}
