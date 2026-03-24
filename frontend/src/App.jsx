/**
 * FRONTEND ENTRY POINT (App.jsx)
 * ------------------------------
 * This is the main layout component of our application.
 * It is responsible for splitting the screen into two main areas:
 * 1. The visual Node Graph (Left side)
 * 2. The AI Chat Interface (Right side)
 * 
 * Flow: 
 * - When the app loads, it fetches node/link data from the Backend API (/api/graph).
 * - It passes that data into the <GraphView /> component.
 * - It manages the state for the floating "Detail Card" when a user clicks a node.
 */
import React, { useState, useEffect } from 'react';
import GraphView from './components/GraphView';
import ChatInterface from './components/ChatInterface';
import './index.css';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

function App() {
  const [graphData, setGraphData] = useState({ nodes: [], links: [] });
  const [selectedNode, setSelectedNode] = useState(null);

  useEffect(() => {
    fetch(`${API_BASE_URL}/api/graph`)
      .then(res => res.json())
      .then(data => setGraphData(data))
      .catch(err => console.error("Failed to load graph:", err));
  }, []);

  return (
    <div className="flex h-screen w-screen bg-white text-slate-800 font-sans overflow-hidden select-none">
      
      {/* LEFT PANE - GRAPH */}
      <div className="flex-1 w-full h-full relative">
        {/* Header Overlay */}
        <div className="absolute top-6 left-6 z-10 pointer-events-none">
          <div className="flex items-center gap-3">
            <div className="w-8 h-8 rounded-lg bg-blue-600 flex items-center justify-center shadow-lg shadow-blue-500/30">
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="white" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round"><path d="M18 3a3 3 0 0 0-3 3v12a3 3 0 0 0 3 3 3 3 0 0 0 3-3 3 3 0 0 0-3-3H6a3 3 0 0 0-3 3 3 3 0 0 0 3 3 3 3 0 0 0 3-3V6a3 3 0 0 0-3-3 3 3 0 0 0-3 3 3 3 0 0 0 3 3h12a3 3 0 0 0 3-3 3 3 0 0 0-3-3z"></path></svg>
            </div>
            <div>
              <h1 className="text-xl font-bold tracking-tight text-slate-900">Nexus</h1>
              <div className="flex items-center gap-1.5 mt-0.5">
                <span className="text-xs font-medium text-slate-500 uppercase tracking-widest">Order to Cash</span>
                <span className="w-1 h-1 rounded-full bg-slate-300"></span>
                <span className="text-xs text-slate-400">Context Graph</span>
              </div>
            </div>
          </div>
        </div>

        <GraphView data={graphData} onNodeClick={setSelectedNode} />

        {/* Node Detail Popup */}
        {selectedNode && (
          <div className="absolute top-24 left-6 z-20 w-80 bg-white/80 backdrop-blur-xl border border-slate-200/50 shadow-2xl rounded-2xl p-5 transform transition-all animate-in fade-in slide-in-from-left-4">
            <div className="flex justify-between items-start mb-4">
              <div>
                <span className="text-[10px] font-bold uppercase tracking-wider text-blue-600 mb-1 block">Selected Entity</span>
                <h3 className="font-bold text-lg text-slate-900 leading-tight">{selectedNode.name}</h3>
              </div>
              <button 
                onClick={() => setSelectedNode(null)}
                className="p-1 hover:bg-slate-100 rounded-full text-slate-400 hover:text-slate-600 transition-colors"
              >
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><line x1="18" y1="6" x2="6" y2="18"></line><line x1="6" y1="6" x2="18" y2="18"></line></svg>
              </button>
            </div>
            
            <div className="space-y-3">
              <div className="flex flex-col">
                <span className="text-xs text-slate-500 font-medium">Type</span>
                <span className="text-sm font-semibold text-slate-700">{selectedNode.label}</span>
              </div>
              <div className="flex flex-col">
                <span className="text-xs text-slate-500 font-medium">Identifier</span>
                <span className="text-sm font-mono text-slate-700 bg-slate-100 w-fit px-1.5 py-0.5 rounded mt-0.5">{selectedNode.id}</span>
              </div>
              <div className="pt-2 border-t border-slate-100 flex items-center justify-between">
                <span className="text-xs text-slate-400 italic">
                  Connections: {graphData.links.filter(l => l.source === selectedNode.id || l.target === selectedNode.id || l.source?.id === selectedNode.id || l.target?.id === selectedNode.id).length}
                </span>
                <button 
                  onClick={() => {
                    const input = document.querySelector('input[placeholder="Analyze anything..."]');
                    if (input) {
                      const nativeInputValueSetter = Object.getOwnPropertyDescriptor(window.HTMLInputElement.prototype, "value").set;
                      nativeInputValueSetter.call(input, `Analyze all context and numbers for ${selectedNode.label} ID: ${selectedNode.id}`);
                      input.dispatchEvent(new Event('input', { bubbles: true }));
                      
                      // Auto-trigger the send button logic
                      const sendBtn = Array.from(document.querySelectorAll('button')).find(b => b.textContent === 'Send');
                      if (sendBtn) setTimeout(() => sendBtn.click(), 100);
                    }
                  }}
                  className="text-xs text-blue-600 font-semibold hover:text-blue-700 transition-colors bg-blue-50/50 px-2 py-1 rounded-md ml-2"
                >
                  Explore Flow →
                </button>
              </div>
            </div>
          </div>
        )}
      </div>
      
      {/* RIGHT PANE - CHAT */}
      <div className="w-[420px] h-full flex flex-col bg-white border-l border-slate-200 shadow-2xl z-20">
        <ChatInterface />
      </div>
    </div>
  )
}

export default App;
