import React, { useState, useEffect, useRef } from 'react';
import { Send, Terminal as TerminalIcon, WifiOff } from 'lucide-react';

const Terminal = ({ websocket, isConnected }) => {
  const [history, setHistory] = useState([
    { type: 'system', content: 'INITIALIZING WEB TERMINATOR INTERFACE...' },
    { type: 'system', content: 'ATTEMPTING CONNECTION TO TERMINATOR BRIDGE...' }
  ]);
  const [input, setInput] = useState('');
  const bottomRef = useRef(null);

  // Handle incoming messages
  useEffect(() => {
    if (!websocket) return;

    const handleMessage = (event) => {
      const message = JSON.parse(event.data);
      // Ignore metrics updates (handled by useMetrics)
      if (message.type === 'metrics_update') return;
      setHistory(prev => [...prev, message]);
    };

    websocket.addEventListener('message', handleMessage);
    return () => websocket.removeEventListener('message', handleMessage);
  }, [websocket]);

  // Update connection status messages
  useEffect(() => {
    if (isConnected) {
      setHistory(prev => [...prev,
        { type: 'success', content: 'CONNECTION ESTABLISHED. TERMINATOR BRIDGE ONLINE.' },
        { type: 'ai', content: 'Hello sir. I am T.E.R.M.I.N.A.T.O.R. How may I assist you today?' }
      ]);
    } else if (history.length > 2) {
      setHistory(prev => [...prev, { type: 'error', content: 'CONNECTION LOST. TERMINATOR BRIDGE OFFLINE.' }]);
    }
  }, [isConnected]);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [history]);

  const handleCommand = (e) => {
    e.preventDefault();
    if (!input.trim() || !isConnected) return;

    const cmd = input.trim();
    setHistory(prev => [...prev, { type: 'user', content: cmd }]);
    setInput('');

    // Send command via WebSocket
    websocket.send(JSON.stringify({ command: cmd }));
  };

  return (
    <div className="flex-1 bg-slate-900/50 backdrop-blur-md border border-terminator-blue/30 rounded-lg flex flex-col glow-border overflow-hidden">
      {/* Terminal Header */}
      <div className="h-10 bg-terminator-blue/10 border-b border-terminator-blue/20 flex items-center px-4 justify-between">
        <div className="flex items-center gap-2 text-terminator-blue/70 font-mono text-sm">
           <TerminalIcon size={14} />
           <span>THE TERMINATOR TERMINAL</span>
        </div>
        <div className="flex items-center gap-3">
            {!isConnected && <WifiOff size={18} className="text-red-500 animate-pulse" />}
            <div className="flex gap-1.5">
              <div className="w-3 h-3 rounded-full bg-red-500/50"></div>
              <div className="w-3 h-3 rounded-full bg-yellow-500/50"></div>
              <div className="w-3 h-3 rounded-full bg-green-500/50"></div>
            </div>
        </div>
      </div>

      {/* Output Area */}
      <div className="flex-1 overflow-y-auto p-6 font-mono text-sm space-y-3">
        {history.map((entry, idx) => (
          <div key={idx} className={`leading-relaxed animate-in fade-in slide-in-from-left-4 duration-300`}>
            {entry.type === 'user' && (
              <div className="flex gap-2 text-white/90">
                <span className="text-terminator-blue font-bold">{'>'}</span>
                <span>{entry.content}</span>
              </div>
            )}
            {entry.type === 'ai' && (
               <div className="text-terminator-blue pl-4 border-l-2 border-terminator-blue/50">
                 {entry.content}
               </div>
            )}
            {entry.type === 'system' && (
               <div className="text-terminator-blue/60 italic">
                 {`[SYSTEM]: ${entry.content}`}
               </div>
            )}
             {entry.type === 'success' && (
               <div className="text-emerald-400 pl-4">
                 {`✓ ${entry.content}`}
               </div>
            )}
             {entry.type === 'warning' && (
               <div className="text-yellow-400 pl-4">
                 {`⚠ ${entry.content}`}
               </div>
            )}
             {entry.type === 'error' && (
               <div className="text-terminator-alert pl-4">
                 {`✗ ${entry.content}`}
               </div>
            )}
          </div>
        ))}
        <div ref={bottomRef} />
      </div>

      {/* Input Area */}
      <div className="p-4 bg-black/20 border-t border-terminator-blue/20">
        <form onSubmit={handleCommand} className="relative flex items-center gap-3">
          <span className="text-terminator-glow font-bold animate-pulse">{'>'}</span>
          <input 
            type="text" 
            value={input}
            onChange={(e) => setInput(e.target.value)}
            className="flex-1 bg-transparent border-none outline-none text-white font-mono placeholder-terminator-blue/30"
            placeholder={isConnected ? "Enter command protocol..." : "Connecting to bridge..."}
            autoFocus
            disabled={!isConnected}
          />
          <button type="submit" className="text-terminator-blue hover:text-white transition-colors" disabled={!isConnected}>
            <Send size={18} />
          </button>
        </form>
      </div>
    </div>
  );
};

export default Terminal;