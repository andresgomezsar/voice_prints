import React from "react";
import LineChart from "./LineChart";
import "./MetricsDashboard.css";

function MetricsDashboard() {
  return (
    <div className="dashboard-container">
      <h1 className="dashboard-title">Primary Vocal Metrics</h1>
      
      {/* Metrics Cards */}
      <div className="metrics-cards">
        <div className="metric-card">
          <h2 className="metric-value">
            150 <span className="metric-unit">Words/min</span>
          </h2>
          <p className="metric-label">
            Speech Rate <span className="metric-icon trend-icon">⬆️</span>
          </p>
        </div>
        <div className="metric-card">
          <h2 className="metric-value">
            14 <span className="metric-unit">Per minute</span>
          </h2>
          <p className="metric-label">
            Pauses <span className="metric-icon caution-icon">⚠️</span>
          </p>
        </div>
        <div className="metric-card">
          <h2 className="metric-value">
            85% <span className="metric-unit">Clarity score</span>
          </h2>
          <p className="metric-label">
            Voice Quality <span className="metric-icon waveform-icon">📊</span>
          </p>
        </div>
      </div>

      {/* Line Chart */}
      <LineChart />
    </div>
  );
}

export default MetricsDashboard;
