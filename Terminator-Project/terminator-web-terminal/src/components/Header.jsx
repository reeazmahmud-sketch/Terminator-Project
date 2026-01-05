import React, { useState, useEffect } from 'react';
import { Wifi, Battery, ShieldCheck, WifiOff } from 'lucide-react';

const Header = () => {
  const [time, setTime] = useState(new Date());

  useEffect(() => {
    const timer = setInterval(() => setTime(new Date()), 1000);
    return () => clearInterval(timer);
  }, []);

  // This component doesn't directly know WebSocket connection status
  // For a full implementation, you'd pass this state via context or props from App.jsx
  // For now, we'll keep it as a placeholder or assume connection for display.
  const isConnected = true; // Placeholder

  return (
    <div className="w-full h-16 bg-slate-900/50 backdrop-blur-md border border-terminator-blue/30 rounded-lg flex items-center justify-between px-6 glow-border shrink-0 z-20">
      <div className="flex items-center gap-4">
         <div className="text-terminator-blue font-display font-bold text-2xl tracking-widest glow-text">
            THE TERMINATOR TERMINAL
         </div>
         <div className="text-xs text-terminator-blue/60 font-mono mt-1">
            SYSTEM VERSION 2.5.1
         </div>
      </div>

      <div className="flex items-center gap-8">
        <div className="flex items-center gap-2 text-terminator-blue/80">
           <ShieldCheck size={18} />
           <span className="text-xs font-mono">SECURE</span>
        </div>
        <div className="flex items-center gap-2 text-terminator-blue/80">
           {isConnected ? <Wifi size={18} /> : <WifiOff size={18} className="text-red-500 animate-pulse" />}
           <span className="text-xs font-mono">{isConnected ? "CONNECTED" : "DISCONNECTED"}</span>
        </div>
        <div className="flex items-center gap-2 text-terminator-blue/80">
           <Battery size={18} />
           <span className="text-xs font-mono">100%</span>
        </div>
        <div className="w-px h-8 bg-terminator-blue/30 mx-2"></div>
        <div className="text-terminator-blue font-mono font-bold text-xl">
           {time.toLocaleTimeString()}
        </div>
      </div>
    </div>
  );
};

export default Header;