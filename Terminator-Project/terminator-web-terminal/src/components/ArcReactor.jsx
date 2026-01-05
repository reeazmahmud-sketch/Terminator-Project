import React from 'react';
import { motion } from 'framer-motion';

const ArcReactor = () => {
  return (
    <div className="relative w-48 h-48 flex items-center justify-center">
      {/* Outer Ring */}
      <motion.div 
        animate={{ rotate: 360 }}
        transition={{ duration: 10, repeat: Infinity, ease: "linear" }}
        className="absolute w-full h-full rounded-full border-4 border-dashed border-terminator-blue/30"
      />
      
      {/* Inner Ring */}
      <motion.div 
        animate={{ rotate: -360 }}
        transition={{ duration: 15, repeat: Infinity, ease: "linear" }}
        className="absolute w-36 h-36 rounded-full border-2 border-terminator-glow/40"
      />

      {/* Core Glow */}
      <motion.div 
        animate={{ scale: [1, 1.1, 1], opacity: [0.8, 1, 0.8] }}
        transition={{ duration: 2, repeat: Infinity }}
        className="w-24 h-24 rounded-full bg-terminator-blue/20 flex items-center justify-center shadow-[0_0_30px_rgba(0,168,255,0.6)]"
      >
        <div className="w-16 h-16 rounded-full bg-white/10 shadow-[0_0_20px_rgba(255,255,255,0.8)] backdrop-blur-sm border border-white/50"></div>
      </motion.div>
      
      {/* Particles */}
      <div className="absolute inset-0">
         {[...Array(3)].map((_, i) => (
           <motion.div
             key={i}
             className="absolute w-full h-full rounded-full border border-transparent border-t-terminator-glow/60"
             animate={{ rotate: 360 }}
             transition={{ duration: 3 + i, repeat: Infinity, ease: "linear", delay: i }}
           />
         ))}
      </div>
      
      <div className="absolute -bottom-12 text-terminator-blue/50 font-mono text-xs tracking-[0.5em]">
        STARK IND.
      </div>
    </div>
  );
};

export default ArcReactor;
