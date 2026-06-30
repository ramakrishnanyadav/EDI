import React, { useState, useEffect } from 'react';
import { motion, useMotionValue, useTransform } from 'framer-motion';
import { GitMerge, Cpu, Search, Activity, Layers, ExternalLink } from 'lucide-react';

export default function LandingPage({ onLogin }: { onLogin: () => void }) {
  const [mousePosition, setMousePosition] = useState({ x: 0, y: 0 });
  const x = useMotionValue(0);
  const y = useMotionValue(0);
  
  const rotateX = useTransform(y, [-500, 500], [25, -25]);
  const rotateY = useTransform(x, [-500, 500], [-25, 25]);

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
    <div className="relative min-h-screen bg-[#020202] text-white overflow-hidden flex flex-col font-sans selection:bg-purple-500/30">
      
      {/* 1. Ultra-Rizz Background System */}
      <div className="fixed inset-0 z-0 pointer-events-none">
        {/* Animated Color-Shifting Orbs */}
        <motion.div 
          animate={{ scale: [1, 1.2, 1], rotate: [0, 90, 0], backgroundColor: ['rgba(59,130,246,0.15)', 'rgba(168,85,247,0.15)', 'rgba(59,130,246,0.15)'] }}
          transition={{ duration: 10, repeat: Infinity, ease: "easeInOut" }}
          className="absolute top-[-10%] left-[20%] w-[50vw] h-[50vw] blur-[150px] rounded-full" 
        />
        <motion.div 
          animate={{ scale: [1, 1.5, 1], rotate: [0, -90, 0], backgroundColor: ['rgba(168,85,247,0.1)', 'rgba(236,72,153,0.1)', 'rgba(168,85,247,0.1)'] }}
          transition={{ duration: 15, repeat: Infinity, ease: "easeInOut" }}
          className="absolute bottom-[-20%] right-[-10%] w-[60vw] h-[60vw] blur-[150px] rounded-full" 
        />
        
        {/* Intense Mouse Spotlight */}
        <div 
          className="absolute inset-0 opacity-60 mix-blend-screen transition-opacity duration-300"
          style={{ background: `radial-gradient(800px circle at ${mousePosition.x}px ${mousePosition.y}px, rgba(168,85,247,0.15), transparent 50%)` }}
        />
        
        {/* Moving Dot Grid */}
        <div className="absolute inset-0 bg-[linear-gradient(rgba(255,255,255,0.05)_2px,transparent_2px),linear-gradient(90deg,rgba(255,255,255,0.05)_2px,transparent_2px)] bg-[size:32px_32px] [mask-image:radial-gradient(ellipse_60%_60%_at_50%_40%,#000_40%,transparent_100%)]" style={{ transform: 'perspective(500px) rotateX(45deg) scale(2) translateY(-100px)' }} />
      </div>

      {/* Floating Tech Orbs (Rizz Elements) */}
      <div className="absolute inset-0 pointer-events-none z-10 overflow-hidden">
        {[
          { Icon: Cpu, color: "text-blue-400", bg: "bg-blue-500/10", border: "border-blue-500/30", delay: 0, top: "20%", left: "10%" },
          { Icon: Layers, color: "text-purple-400", bg: "bg-purple-500/10", border: "border-purple-500/30", delay: 1.5, top: "60%", left: "5%" },
          { Icon: GitMerge, color: "text-pink-400", bg: "bg-pink-500/10", border: "border-pink-500/30", delay: 3, top: "15%", left: "85%" },
          { Icon: Activity, color: "text-cyan-400", bg: "bg-cyan-500/10", border: "border-cyan-500/30", delay: 0.5, top: "70%", left: "80%" }
        ].map((orb, i) => (
          <motion.div
            key={i}
            initial={{ opacity: 0, scale: 0 }}
            animate={{ 
              opacity: [0.5, 1, 0.5], 
              scale: [1, 1.1, 1],
              y: [0, -30, 0],
              rotate: [0, 10, -10, 0]
            }}
            transition={{ duration: 6, delay: orb.delay, repeat: Infinity, ease: "easeInOut" }}
            className={`absolute ${orb.top} ${orb.left} p-4 rounded-2xl backdrop-blur-xl border shadow-[0_0_30px_rgba(255,255,255,0.05)] ${orb.bg} ${orb.border}`}
          >
            <orb.Icon className={`w-8 h-8 ${orb.color}`} />
          </motion.div>
        ))}
      </div>

      <nav className="relative z-20 flex items-center justify-between px-8 py-6 max-w-7xl mx-auto w-full">
        <motion.div initial={{ opacity: 0, x: -20 }} animate={{ opacity: 1, x: 0 }} className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-purple-500 via-indigo-500 to-blue-500 flex items-center justify-center shadow-[0_0_30px_rgba(168,85,247,0.4)]">
            <Cpu className="w-5 h-5 text-white" />
          </div>
          <span className="font-bold text-2xl tracking-tighter">EDI<span className="text-purple-500">.</span></span>
        </motion.div>
        <motion.div initial={{ opacity: 0, x: 20 }} animate={{ opacity: 1, x: 0 }} className="flex gap-4">
          <button onClick={onLogin} className="px-5 py-2 text-sm font-medium text-gray-300 hover:text-white transition-colors">Sign In</button>
          <button onClick={onLogin} className="relative group px-6 py-2 rounded-full bg-white text-black font-semibold overflow-hidden">
            <span className="relative z-10 group-hover:text-purple-600 transition-colors duration-300">Get Access</span>
            <div className="absolute inset-0 bg-gradient-to-r from-purple-200 to-blue-200 opacity-0 group-hover:opacity-100 transition-opacity duration-300" />
          </button>
        </motion.div>
      </nav>

      <main className="relative z-20 flex-1 flex flex-col items-center justify-center px-8 w-full pb-20 mt-10">
        
        {/* Massive Rizz Typography */}
        <div className="flex flex-col items-center text-center max-w-5xl mx-auto">
          <motion.div 
            initial={{ opacity: 0, scale: 0.8, y: 20 }} animate={{ opacity: 1, scale: 1, y: 0 }} transition={{ type: "spring", bounce: 0.5 }}
            className="inline-flex items-center gap-2 px-4 py-2 rounded-full border border-purple-500/30 bg-purple-500/10 text-purple-300 text-xs font-mono uppercase tracking-widest mb-10 shadow-[0_0_30px_rgba(168,85,247,0.3)]"
          >
            <span className="relative flex h-2 w-2">
              <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-purple-400 opacity-75"></span>
              <span className="relative inline-flex rounded-full h-2 w-2 bg-purple-500"></span>
            </span>
            Neural Architecture Intelligence
          </motion.div>

          <motion.h1 
            initial={{ opacity: 0, y: 40 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.8, delay: 0.1, ease: "easeOut" }}
            className="text-6xl sm:text-7xl lg:text-[7rem] font-extrabold tracking-tighter leading-[0.95] mb-8"
          >
            Don't Guess. <br />
            <span className="relative inline-block mt-4">
              <span className="absolute -inset-2 bg-gradient-to-r from-purple-600 via-pink-600 to-blue-600 opacity-30 blur-2xl rounded-full"></span>
              <span className="relative text-transparent bg-clip-text bg-gradient-to-r from-purple-400 via-pink-400 to-blue-400 animate-gradient-x">
                Know The Future.
              </span>
            </span>
          </motion.h1>

          <motion.p 
            initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ duration: 1, delay: 0.4 }}
            className="text-xl sm:text-2xl text-gray-400 max-w-2xl leading-relaxed mb-14 font-light"
          >
            The autonomous causal engine that maps your historical <span className="text-white font-medium">engineering memory</span> and prevents architectural disasters before they happen.
          </motion.p>

          {/* Glowing Border Rizz Button */}
          <motion.div 
            initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.8, delay: 0.5 }}
            className="flex flex-col sm:flex-row gap-6 items-center justify-center w-full"
          >
            <div className="relative group cursor-pointer" onClick={onLogin}>
              <div className="absolute -inset-1 bg-gradient-to-r from-purple-600 via-pink-600 to-blue-600 rounded-2xl blur opacity-70 group-hover:opacity-100 transition duration-1000 group-hover:duration-200 animate-tilt"></div>
              <button className="relative flex items-center gap-3 px-10 py-5 bg-black text-white font-bold text-lg rounded-xl leading-none transition-all duration-200">
                Deploy Agent Now <ExternalLink className="w-5 h-5 group-hover:translate-x-2 transition-transform" />
              </button>
            </div>
            
            <button onClick={onLogin} className="flex items-center gap-2 px-8 py-5 rounded-xl bg-white/5 hover:bg-white/10 text-white font-medium border border-white/10 backdrop-blur-md transition-colors">
              <Search className="w-5 h-5 text-gray-400" /> Watch Demo
            </button>
          </motion.div>
        </div>

        {/* Floating 3D Dashboard Rizz (Centered below text) */}
        <motion.div 
          initial={{ opacity: 0, y: 100 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 1, delay: 0.6 }}
          style={{ perspective: 1200 }}
          className="w-full max-w-5xl mt-24 relative flex justify-center items-center"
          onMouseMove={handleMouseMove}
        >
          <motion.div
            style={{ rotateX, rotateY, transformStyle: "preserve-3d" }}
            className="w-full aspect-[21/9] rounded-3xl border border-white/10 bg-black/50 backdrop-blur-3xl shadow-[0_0_100px_rgba(168,85,247,0.3)] p-1 overflow-hidden"
          >
            {/* Inner Dashboard Glow */}
            <div className="absolute inset-0 bg-gradient-to-tr from-purple-500/10 via-transparent to-blue-500/10" />
            
            {/* Dashboard Content Mock */}
            <div className="relative w-full h-full bg-[#0A0A0C] rounded-[22px] overflow-hidden border border-white/5 flex flex-col">
              {/* Header */}
              <div className="h-12 border-b border-white/5 flex items-center px-4 justify-between bg-white/[0.02]">
                <div className="flex gap-2">
                  <div className="w-3 h-3 rounded-full bg-red-500/50" />
                  <div className="w-3 h-3 rounded-full bg-yellow-500/50" />
                  <div className="w-3 h-3 rounded-full bg-green-500/50" />
                </div>
                <div className="text-[10px] font-mono text-purple-400 uppercase tracking-widest px-3 py-1 bg-purple-500/10 rounded-full border border-purple-500/20">Agent Terminal Active</div>
              </div>
              
              {/* Fake Terminal Output */}
              <div className="p-6 font-mono text-sm text-left flex-1 relative">
                <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_center,rgba(168,85,247,0.1),transparent_70%)]" />
                <motion.div 
                  initial={{ opacity: 0, x: -20 }} animate={{ opacity: 1, x: 0 }} transition={{ duration: 0.5, delay: 1 }}
                  className="text-gray-500 mb-2"
                >
                  &gt; edi-agent connect --repo="langchain-ai/langchain"
                </motion.div>
                <motion.div 
                  initial={{ opacity: 0, x: -20 }} animate={{ opacity: 1, x: 0 }} transition={{ duration: 0.5, delay: 1.5 }}
                  className="text-blue-400 mb-2 flex items-center gap-2"
                >
                  <Activity className="w-4 h-4 animate-spin" /> Ingesting 5,421 issues...
                </motion.div>
                <motion.div 
                  initial={{ opacity: 0, x: -20 }} animate={{ opacity: 1, x: 0 }} transition={{ duration: 0.5, delay: 2.5 }}
                  className="text-purple-400 mb-2"
                >
                  [SUCCESS] Vector graph constructed. 342 architectural decisions mapped.
                </motion.div>
                <motion.div 
                  initial={{ opacity: 0, x: -20 }} animate={{ opacity: 1, x: 0 }} transition={{ duration: 0.5, delay: 3 }}
                  className="text-white mt-4 border-l-2 border-purple-500 pl-4 py-2 bg-purple-500/10 rounded-r"
                >
                  <span className="text-purple-300 font-bold">CRITICAL INSIGHT:</span> 84% of teams using early microservices reverted due to operational overhead. Recommendation: Monolith-First.
                </motion.div>
              </div>
            </div>
          </motion.div>
        </motion.div>
      </main>

    </div>
  );
}
