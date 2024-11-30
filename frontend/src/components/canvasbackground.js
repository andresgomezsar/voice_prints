import React, { useEffect, useRef } from "react";

function CanvasBackground() {
  const canvasRef = useRef(null);

  useEffect(() => {
    const canvas = canvasRef.current;
    const ctx = canvas.getContext("2d");
    const width = window.innerWidth;
    const height = window.innerHeight;

    canvas.width = width;
    canvas.height = height;

    function drawTriangle(x, y, size, depth) {
      if (depth === 0) return;

      ctx.beginPath();
      ctx.moveTo(x, y);
      ctx.lineTo(x + size / 2, y + size);
      ctx.lineTo(x - size / 2, y + size);
      ctx.closePath();

      const colors = ["#1c1c3c", "#3c99dc", "#ff007f", "#00ffcc"];
      ctx.fillStyle = colors[Math.floor(Math.random() * colors.length)];
      ctx.fill();

      drawTriangle(x, y, size / 2, depth - 1);
      drawTriangle(x - size / 4, y + size / 2, size / 2, depth - 1);
      drawTriangle(x + size / 4, y + size / 2, size / 2, depth - 1);
    }

    ctx.clearRect(0, 0, width, height);
    drawTriangle(width / 2, 100, 300, 5); 

    return () => {
      ctx.clearRect(0, 0, width, height); 
    };
  }, []);

  return <canvas ref={canvasRef} style={{ position: "absolute", top: 0, left: 0, zIndex: -1 }} />;
}

export default CanvasBackground;
