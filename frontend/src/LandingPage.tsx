import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { ArrowRight, BrainCircuit, Github, Cpu, Network } from 'lucide-react';

export default function LandingPage({ onLogin }: { onLogin: () => void }) {
  const [isHovering, setIsHovering] = useState(false);

  return (
    <div className="relative min-h-screen bg-[#030303] text-[#FAFAFA] overflow-hidden flex flex-col items-center justify-center selection:bg-blue-500/30">
      
      {/* Background Animated Gradients */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        <motion.div 
          animate={{ 
            scale: [1, 1.2, 1],
            opacity: [0.3, 0.5, 0.3],
          }}
          transition={{ duration: 8, repeat: Infinity, ease: "easeInOut" }}
          className="absolute -top-[20%] -left-[10%] w-[70vw] h-[70vw] rounded-full bg-blue-900/20 blur-[120px]"
        />
        <motion.div 
          animate={{ 
            scale: [1, 1.5, 1],
            opacity: [0.2, 0.4, 0.2],
          }}
          transition={{ duration: 12, repeat: Infinity, ease: "easeInOut", delay: 2 }}
          className="absolute -bottom-[20%] -right-[10%] w-[60vw] h-[60vw] rounded-full bg-indigo-900/20 blur-[120px]"
        />
      </div>

      {/* Floating 3D-like Nodes */}
      <div className="absolute inset-0 pointer-events-none">
        {[...Array(6)].map((_, i) => (
          <motion.div
            key={i}
            initial={{ y: Math.random() * 100 - 50, x: Math.random() * 100 - 50, opacity: 0 }}
            animate={{ 
              y: [Math.random() * 200 - 100, Math.random() * -200 + 100],
              x: [Math.random() * 200 - 100, Math.random() * -200 + 100],
              opacity: [0.1, 0.4, 0.1],
              rotate: [0, 180, 360]
            }}
            transition={{ duration: 15 + Math.random() * 10, repeat: Infinity, repeatType: "reverse", ease: "linear" }}
            className="absolute"
            style={{
              top: `${20 + Math.random() * 60}%`,
              left: `${10 + Math.random() * 80}%`,
            }}
          >
            <div className="w-16 h-16 rounded-2xl border border-white/10 bg-white/5 backdrop-blur-3xl flex items-center justify-center rotate-45 shadow-[0_0_30px_rgba(59,130,246,0.15)]">
              <Network className="w-6 h-6 text-blue-400/50 -rotate-45" />
            </div>
          </motion.div>
        ))}
      </div>

      {/* Grid Pattern overlay */}
      <div className="absolute inset-0 bg-[linear-gradient(rgba(255,255,255,0.02)_1px,transparent_1px),linear-gradient(90deg,rgba(255,255,255,0.02)_1px,transparent_1px)] bg-[size:4rem_4rem] [mask-image:radial-gradient(ellipse_60%_60%_at_50%_50%,#000_20%,transparent_100%)] pointer-events-none" />

      {/* Main Glassmorphic Hero Container */}
      <motion.div 
        initial={{ opacity: 0, y: 40 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 1, ease: "easeOut" }}
        className="relative z-10 max-w-5xl w-full px-6 flex flex-col items-center text-center"
      >
        <motion.div 
          initial={{ scale: 0.9, opacity: 0 }}
          animate={{ scale: 1, opacity: 1 }}
          transition={{ duration: 0.8, delay: 0.2 }}
          className="inline-flex items-center gap-2 px-3 py-1.5 rounded-full border border-blue-500/30 bg-blue-500/10 text-blue-400 text-xs font-mono uppercase tracking-widest mb-8 shadow-[0_0_20px_rgba(59,130,246,0.2)]"
        >
          <Cpu className="w-3.5 h-3.5 animate-pulse" />
          Autonomous Engineering Intelligence
        </motion.div>

        <h1 className="text-5xl md:text-7xl font-bold tracking-tighter mb-6 bg-clip-text text-transparent bg-gradient-to-b from-white to-white/50 leading-tight">
          Stop repeating <br className="hidden md:block" />
          <span className="text-transparent bg-clip-text bg-gradient-to-r from-blue-400 via-indigo-400 to-purple-400">historical mistakes.</span>
        </h1>
        
        <p className="text-lg md:text-xl text-muted max-w-2xl mb-12 font-light leading-relaxed">
          The causal traversal engine that reads your GitHub, maps past engineering decisions, and warns your team before they adopt the wrong architecture.
        </p>

        {/* Action Buttons Glass Box */}
        <motion.div 
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8, delay: 0.4 }}
          className="p-8 rounded-3xl border border-white/10 bg-white/[0.02] backdrop-blur-xl shadow-2xl flex flex-col sm:flex-row gap-4 items-center justify-center w-full max-w-md relative overflow-hidden group"
          onMouseEnter={() => setIsHovering(true)}
          onMouseLeave={() => setIsHovering(false)}
        >
          <div className="absolute inset-0 bg-gradient-to-r from-blue-500/10 to-purple-500/10 opacity-0 group-hover:opacity-100 transition-opacity duration-500" />
          
          <button 
            onClick={onLogin}
            className="w-full relative overflow-hidden px-8 py-4 bg-white text-black font-semibold rounded-xl transition-all duration-300 hover:scale-[1.02] active:scale-[0.98] flex items-center justify-center gap-2 shadow-[0_0_40px_rgba(255,255,255,0.3)] hover:shadow-[0_0_60px_rgba(255,255,255,0.5)]"
          >
            <Github className="w-5 h-5" />
            Continue with GitHub
          </button>

          <button 
            onClick={onLogin}
            className="w-full px-8 py-4 bg-transparent text-white border border-white/20 font-semibold rounded-xl hover:bg-white/5 transition-all duration-300 flex items-center justify-center gap-2 group"
          >
            Access Platform
            <ArrowRight className={`w-4 h-4 transition-transform duration-300 ${isHovering ? 'translate-x-1' : ''}`} />
          </button>
        </motion.div>

        {/* Feature Highlights */}
        <motion.div 
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ duration: 1, delay: 0.8 }}
          className="grid grid-cols-1 md:grid-cols-3 gap-6 mt-24 text-left w-full"
        >
          {[
            { title: "Autonomous Ingestion", desc: "Connects to GitHub and parses thousands of closed issues automatically." },
            { title: "Causal Graph Mapping", desc: "Transforms raw text into a semantic decision tree using Cognee vector DB." },
            { title: "Regret Prevention", desc: "Identifies systemic failures before your team commits to an architecture." }
          ].map((feature, idx) => (
            <div key={idx} className="p-6 rounded-2xl border border-white/5 bg-white/[0.01] hover:bg-white/[0.03] transition-colors">
              <BrainCircuit className="w-6 h-6 text-blue-400 mb-4" />
              <h3 className="font-semibold text-white mb-2">{feature.title}</h3>
              <p className="text-sm text-muted">{feature.desc}</p>
            </div>
          ))}
        </motion.div>
      </motion.div>
    </div>
  );
}
