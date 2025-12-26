import React, { useState, useEffect, useRef } from 'react';
import Terminal from './components/Terminal';
import StatusPanel from './components/StatusPanel';
import Header from './components/Header';
import ArcReactor from './components/ArcReactor';
import { useMetrics } from './hooks/useMetrics';
import { motion } from 'framer-motion';

function App() {
  const [init, setInit] = useState(false);
  const ws = useRef(null);
  const [isConnected, setIsConnected] = useState(false);

  // Initialize WebSocket once at App level
  useEffect(() => {
    ws.current = new WebSocket("ws://localhost:8000/ws");

    ws.current.onopen = () => {
      setIsConnected(true);
    };

    ws.current.onclose = () => {
      setIsConnected(false);
    };

    return () => {
      ws.current?.close();
    };
  }, []);

  const metrics = useMetrics(ws.current);

  useEffect(() => {
    // Simulate startup sequence
    setTimeout(() => setInit(true), 1000);
  }, []);

  return (
    <div className="relative h-screen w-screen bg-black overflow-hidden flex flex-col p-4 gap-4">
      {/* Dynamic Background Grid */}
      <div className="absolute inset-0 z-0 opacity-20 pointer-events-none" 
           style={{ backgroundImage: 'radial-gradient(#00a8ff 1px, transparent 1px)', backgroundSize: '40px 40px' }}>
      </div>

      <Header />

      <main className="flex-1 flex gap-4 z-10 relative h-full">
        {/* Left: Status & Reactor */}
        <motion.div 
          initial={{ x: -100, opacity: 0 }}
          animate={{ x: 0, opacity: 1 }}
          transition={{ duration: 0.8 }}
          className="w-1/4 flex flex-col gap-4"
        >
          <div className="flex-1 bg-slate-900/50 backdrop-blur-md border border-terminator-blue/30 rounded-lg p-4 glow-border flex items-center justify-center relative overflow-hidden">
             <div className="absolute inset-0 bg-grid-pattern opacity-10"></div>
             <ArcReactor />
          </div>
          <StatusPanel metrics={metrics} />
        </motion.div>

        {/* Right: Terminal */}
        <motion.div
          initial={{ x: 100, opacity: 0 }}
          animate={{ x: 0, opacity: 1 }}
          transition={{ duration: 0.8, delay: 0.2 }}
          className="w-3/4 flex flex-col"
        >
          <Terminal websocket={ws.current} isConnected={isConnected} />
        </motion.div>
      </main>
      
      {/* Startup Overlay */}
      {!init && (
        <div className="absolute inset-0 z-50 bg-black flex items-center justify-center">
          <div className="text-terminator-blue text-2xl font-display animate-pulse">
            INITIALIZING T.E.R.M.I.N.A.T.O.R...
          </div>
        </div>
      )}
    </div>
  );
}

export default App;
