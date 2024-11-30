import React from "react";
import MetricsDashboard from "./components/MetricsDashboard";
import CanvasBackground from "./components/canvasbackground";
import "./App.css";

function App() {
  return (
    <div className="App">
      <CanvasBackground />
      <MetricsDashboard />
    </div>
    
  );
}

export default App;
