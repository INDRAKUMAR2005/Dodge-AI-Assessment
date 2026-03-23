/**
 * GRAPH VISUALIZATION COMPONENT (GraphView.jsx)
 * ---------------------------------------------
 * This component uses the `react-force-graph-2d` library to render the nodes and links.
 * 
 * How to explain it:
 * - We mapped Entity Types to specific colors (SalesOrders=Blue, Customers=Rose).
 * - We overridden the default drawing logic to create sleek, small outlined circles (like the reference).
 * - The graph calculates physics dynamically (velocity, repel forces) to naturally spread out the nodes.
 */
import React, { useRef, useEffect, useState, useCallback } from 'react';
import ForceGraph2D from 'react-force-graph-2d';

export default function GraphView({ data, onNodeClick }) {
  const fgRef = useRef();
  const [dimensions, setDimensions] = useState({ width: 0, height: 0 });
  const containerRef = useRef();

  useEffect(() => {
    if (containerRef.current) {
      setDimensions({
        width: containerRef.current.clientWidth,
        height: containerRef.current.clientHeight
      });
    }
    const updateSize = () => {
      if (containerRef.current) {
        setDimensions({
          width: containerRef.current.clientWidth,
          height: containerRef.current.clientHeight
        });
      }
    };
    window.addEventListener('resize', updateSize);
    return () => window.removeEventListener('resize', updateSize);
  }, []);

  const getNodeColor = useCallback((node) => {
    switch(node.label) {
      case 'SalesOrder': return '#3b82f6'; // Blue
      case 'Customer': return '#f43f5e';   // Rose
      case 'Delivery': return '#10b981';   // Emerald
      case 'Invoice': return '#8b5cf6';    // Violet
      default: return '#94a3b8';           // Slate
    }
  }, []);

  return (
    <div ref={containerRef} className="w-full h-full bg-[#fafbfd] overflow-hidden" style={{ backgroundImage: 'radial-gradient(#e2e8f0 1px, transparent 1px)', backgroundSize: '32px 32px' }}>
      <ForceGraph2D
        ref={fgRef}
        width={dimensions.width}
        height={dimensions.height}
        graphData={data}
        nodeLabel={null} // Custom rendering
        nodeColor={getNodeColor}
        nodeRelSize={4}
        linkDirectionalArrowLength={2.5}
        linkDirectionalArrowRelPos={1}
        linkColor={() => '#93c5fd'} // Light blue links mapping to reference
        linkWidth={1}
        d3VelocityDecay={0.3} // More fluid, expansive layout
        d3AlphaDecay={0.01}
        onNodeClick={(node) => {
          onNodeClick(node);
          fgRef.current.centerAt(node.x, node.y, 800);
          fgRef.current.zoom(3, 1000);
        }}
        nodeCanvasObject={(node, ctx, globalScale) => {
          // Draw a small polished circle outline like reference
          ctx.beginPath();
          ctx.arc(node.x, node.y, 3, 0, 2 * Math.PI, false);
          ctx.fillStyle = '#ffffff';
          ctx.fill();
          
          ctx.lineWidth = 1.5;
          ctx.strokeStyle = getNodeColor(node);
          ctx.stroke();

          // Only show labels when zoomed in closely or hovered
          if (globalScale > 3) {
            const label = node.label.substring(0, 3).toUpperCase();
            const fontSize = 10 / globalScale;
            ctx.font = `bold ${fontSize}px Inter, sans-serif`;
            ctx.textAlign = 'center';
            ctx.textBaseline = 'middle';
            ctx.fillStyle = '#475569';
            ctx.fillText(label, node.x, node.y + 6);
          }
        }}
      />
    </div>
  );
}
