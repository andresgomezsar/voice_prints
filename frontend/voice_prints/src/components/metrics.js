import React from 'react';
import MetricsChart from './MetricsChart';

function Metrics() {
  return (
    <div className="vocal-metrics-container">
      {/* Metric Cards */}
      <div className="metric-cards">
        <div className="metric-card">
          <h2>150</h2>
          <p>Words/min</p>
          <i className="trend-icon-up">⬆️</i>
        </div>
        <div className="metric-card">
          <h2>14</h2>
          <p>Per minute</p>
          <i className="caution-icon">⚠️</i>
        </div>
        <div className="metric-card">
          <h2>85%</h2>
          <p>Clarity score</p>
          <i className="waveform-icon">📊</i>
        </div>
      </div>

      {/* Line Chart for Vocal Metrics */}
      <MetricsChart />
    </div>
  );
}

export default Metrics;
