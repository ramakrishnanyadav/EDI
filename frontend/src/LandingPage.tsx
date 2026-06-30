import React, { useState, useEffect } from 'react';
import { motion, useAnimation, useMotionValue, useTransform } from 'framer-motion';
import { ArrowRight, GitMerge, Cpu, Search, Activity, Layers, Terminal } from 'lucide-react';

export default function LandingPage({ onLogin }: { onLogin: () => void }) {
  const [mousePosition, setMousePosition] = useState({ x: 0, y: 0 });
  const x = useMotionValue(0);
  const y = useMotionValue(0);
  
  // High-fidelity 3D tilt for the hero visualization
  const rotateX = useTransform(y, [-500, 500], [15, -15]);
  const rotateY = useTransform(x, [-500, 500], [-15, 15]);

  useEffect(() => {
    const handleMouseMove = (e: MouseEvent) => {
      setMousePosition({ x: e.clientX, y: e.clientY });
      x.set(e.clientX - window.innerWidth / 2);
      y.set(e.clientY - window.innerHeight / 2);
    };
    window.addEventListener("mousemove", handleMouseMove);
    return () => window.removeEventListener("mousemove", handleMouseMove);
  }, [x, y]);

  return (
    <div className="relative min-h-screen bg-[#000000] text-white overflow-hidden flex flex-col font-sans selection:bg-blue-500/30">
      
      {/* 1. Hyper-Modern Background: Moving Grid & Mouse Spotlight */}
      <div className="fixed inset-0 z-0 pointer-events-none">
        {/* Dynamic mouse spotlight */}
        <div 
          className="absolute inset-0 opacity-40 transition-opacity duration-300"
          style={{
            background: `radial-gradient(600px circle at ${mousePosition.x}px ${mousePosition.y}px, rgba(59, 130, 246, 0.15), transparent 40%)`
          }}
        />
        {/* Animated Perspective Grid */}
        <div className="absolute inset-0 bg-[linear-gradient(rgba(255,255,255,0.03)_1px,transparent_1px),linear-gradient(90deg,rgba(255,255,255,0.03)_1px,transparent_1px)] bg-[size:64px_64px] [mask-image:radial-gradient(ellipse_80%_50%_at_50%_0%,#000_70%,transparent_100%)]" style={{ transform: 'perspective(1000px) rotateX(60deg) translateY(-100px) scale(3)', transformOrigin: 'top center' }} />
        {/* Top ambient glow */}
        <div className="absolute top-[-20%] left-[20%] w-[60%] h-[40%] bg-blue-600/20 blur-[120px] rounded-full" />
      </div>

      {/* 2. Top Navigation */}
      <nav className="relative z-20 flex items-center justify-between px-8 py-6 max-w-7xl mx-auto w-full">
        <div className="flex items-center gap-3">
          <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-blue-500 to-indigo-600 flex items-center justify-center shadow-[0_0_20px_rgba(59,130,246,0.5)]">
            <Cpu className="w-4 h-4 text-white" />
          </div>
          <span className="font-bold text-xl tracking-tight">EDI<span className="text-blue-500">.</span></span>
        </div>
        <div className="flex gap-4">
          <button onClick={onLogin} className="px-5 py-2 text-sm font-medium text-gray-300 hover:text-white transition-colors">Sign In</button>
          <button onClick={onLogin} className="px-5 py-2 text-sm font-medium bg-white text-black rounded-full hover:scale-105 transition-transform shadow-[0_0_20px_rgba(255,255,255,0.2)]">Get Access</button>
        </div>
      </nav>

      {/* 3. Hero Section */}
      <main className="relative z-10 flex-1 flex flex-col lg:flex-row items-center justify-center px-8 max-w-7xl mx-auto w-full gap-16 pt-10 pb-20">
        
        {/* Left Column: Typography & CTAs */}
        <div className="flex-1 flex flex-col items-start text-left">
          <motion.div 
            initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.6 }}
            className="inline-flex items-center gap-2 px-3 py-1 rounded-full border border-white/10 bg-white/5 backdrop-blur-md mb-6"
          >
            <span className="flex h-2 w-2 rounded-full bg-blue-500 animate-pulse"></span>
            <span className="text-xs font-mono text-gray-300 uppercase tracking-widest">v2.0 Autonomous Agent</span>
          </motion.div>

          <motion.h1 
            initial={{ opacity: 0, y: 30 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.8, delay: 0.1 }}
            className="text-6xl sm:text-7xl lg:text-8xl font-extrabold tracking-tighter leading-[1.1] mb-8"
          >
            Engineer <br />
            with <span className="text-transparent bg-clip-text bg-gradient-to-r from-blue-400 via-indigo-400 to-purple-400 animate-gradient-x">Foresight.</span>
          </motion.h1>

          <motion.p 
            initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.8, delay: 0.2 }}
            className="text-lg sm:text-xl text-gray-400 max-w-xl leading-relaxed mb-10 font-light"
          >
            The world's first causal traversal engine. We ingest your GitHub, map historical decisions into a vector graph, and prevent catastrophic architectural regrets before a single line is merged.
          </motion.p>

          <motion.div 
            initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.8, delay: 0.3 }}
            className="flex flex-col sm:flex-row gap-4 w-full sm:w-auto"
          >
            <button onClick={onLogin} className="group relative px-8 py-4 bg-white text-black font-semibold rounded-2xl overflow-hidden transition-all hover:scale-[1.02] active:scale-[0.98] shadow-[0_0_40px_rgba(255,255,255,0.2)]">
              <span className="relative z-10 flex items-center justify-center gap-2">
                Deploy Agent <ArrowRight className="w-4 h-4 group-hover:translate-x-1 transition-transform" />
              </span>
            </button>
            <button onClick={onLogin} className="px-8 py-4 bg-white/5 hover:bg-white/10 text-white font-semibold rounded-2xl border border-white/10 transition-colors flex items-center justify-center gap-2 backdrop-blur-sm">
              <Terminal className="w-4 h-4 text-gray-400" /> Read Documentation
            </button>
          </motion.div>
        </div>

        {/* Right Column: Mind-Blowing 3D Interactive Visualization */}
        <div className="flex-1 w-full relative h-[600px] flex items-center justify-center perspective-[2000px]">
          <motion.div
            style={{ rotateX, rotateY, transformStyle: "preserve-3d" }}
            className="relative w-full h-full max-w-lg mx-auto flex items-center justify-center cursor-crosshair"
          >
            {/* Core Floating Glass Dashboard */}
            <motion.div 
              initial={{ opacity: 0, scale: 0.8, rotateX: 20, rotateY: -15, rotateZ: 5 }}
              animate={{ opacity: 1, scale: 1, y: [-10, 10, -10] }}
              transition={{ 
                opacity: { duration: 1 },
                scale: { duration: 1 },
                y: { duration: 6, repeat: Infinity, ease: "easeInOut" }
              }}
              className="absolute w-full aspect-[4/3] rounded-2xl border border-white/10 bg-[#0A0A0C]/80 backdrop-blur-2xl shadow-[0_30px_60px_rgba(0,0,0,0.5),0_0_40px_rgba(59,130,246,0.2)] p-6 overflow-hidden"
              style={{ transformStyle: "preserve-3d" }}
            >
              {/* Dashboard Header */}
              <div className="flex items-center justify-between border-b border-white/10 pb-4 mb-4" style={{ transform: "translateZ(20px)" }}>
                <div className="flex items-center gap-2">
                  <div className="w-3 h-3 rounded-full bg-red-500/80" />
                  <div className="w-3 h-3 rounded-full bg-yellow-500/80" />
                  <div className="w-3 h-3 rounded-full bg-green-500/80" />
                </div>
                <div className="px-2 py-1 rounded bg-blue-500/10 text-blue-400 text-[10px] font-mono border border-blue-500/20">SYSTEM OPERATIONAL</div>
              </div>

              {/* Dashboard Content - Simulated Graph */}
              <div className="relative w-full h-full" style={{ transform: "translateZ(40px)" }}>
                {/* SVG Connections */}
                <svg className="absolute inset-0 w-full h-full" style={{ transform: "translateZ(-10px)" }}>
                  <path d="M 50 50 C 150 50, 100 150, 200 150" fill="transparent" stroke="rgba(59,130,246,0.4)" strokeWidth="2" className="animate-pulse" strokeDasharray="4 4" />
                  <path d="M 200 150 C 300 150, 250 250, 350 250" fill="transparent" stroke="rgba(168,85,247,0.4)" strokeWidth="2" className="animate-pulse" strokeDasharray="4 4" />
                </svg>

                {/* Nodes */}
                <motion.div animate={{ scale: [1, 1.05, 1] }} transition={{ duration: 3, repeat: Infinity }} className="absolute top-[20px] left-[10px] p-3 rounded-xl bg-white/5 border border-white/10 backdrop-blur-md flex items-center gap-3">
                  <Search className="w-4 h-4 text-gray-400" />
                  <div>
                    <div className="text-xs font-semibold text-white">Microservices Risk</div>
                    <div className="text-[10px] text-gray-400 font-mono">Query Executed</div>
                  </div>
                </motion.div>

                <motion.div animate={{ scale: [1, 1.05, 1] }} transition={{ duration: 3, repeat: Infinity, delay: 1 }} className="absolute top-[110px] left-[140px] p-3 rounded-xl bg-blue-500/10 border border-blue-500/30 backdrop-blur-md flex items-center gap-3 shadow-[0_0_20px_rgba(59,130,246,0.2)]" style={{ transform: "translateZ(30px)" }}>
                  <GitMerge className="w-4 h-4 text-blue-400" />
                  <div>
                    <div className="text-xs font-semibold text-blue-100">Historical Regret</div>
                    <div className="text-[10px] text-blue-400/70 font-mono">12 Teams Reverted</div>
                  </div>
                </motion.div>

                <motion.div animate={{ scale: [1, 1.05, 1] }} transition={{ duration: 3, repeat: Infinity, delay: 2 }} className="absolute top-[210px] left-[260px] p-3 rounded-xl bg-purple-500/10 border border-purple-500/30 backdrop-blur-md flex items-center gap-3 shadow-[0_0_20px_rgba(168,85,247,0.2)]" style={{ transform: "translateZ(50px)" }}>
                  <Activity className="w-4 h-4 text-purple-400" />
                  <div>
                    <div className="text-xs font-semibold text-purple-100">Recommendation</div>
                    <div className="text-[10px] text-purple-400/70 font-mono">Monolith First</div>
                  </div>
                </motion.div>
              </div>
            </motion.div>
            
            {/* Accent Glowing Orbs in 3D Space */}
            <motion.div 
              animate={{ rotate: 360 }} transition={{ duration: 20, repeat: Infinity, ease: "linear" }}
              className="absolute w-full h-full pointer-events-none" style={{ transformStyle: "preserve-3d" }}
            >
              <div className="absolute top-0 right-10 w-32 h-32 bg-blue-500/20 rounded-full blur-2xl" style={{ transform: "translateZ(100px)" }} />
              <div className="absolute bottom-10 left-10 w-40 h-40 bg-purple-500/20 rounded-full blur-2xl" style={{ transform: "translateZ(150px)" }} />
            </motion.div>
          </motion.div>
        </div>
      </main>
      
      {/* 4. Bottom Logos/Social Proof Strip */}
      <div className="relative z-10 w-full border-t border-white/5 bg-white/[0.01] py-8 mt-auto">
        <div className="max-w-7xl mx-auto px-8 flex flex-col sm:flex-row items-center justify-between gap-4 text-gray-500 text-sm font-mono uppercase tracking-widest">
          <span>Trusted by Engineering Teams</span>
          <div className="flex gap-8">
            <span className="hover:text-white transition-colors cursor-pointer">Vercel</span>
            <span className="hover:text-white transition-colors cursor-pointer">Linear</span>
            <span className="hover:text-white transition-colors cursor-pointer">Stripe</span>
            <span className="hover:text-white transition-colors cursor-pointer">OpenAI</span>
          </div>
        </div>
      </div>

    </div>
  );
}
