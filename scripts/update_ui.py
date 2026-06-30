import os

with open("frontend/src/App.tsx", "r", encoding="utf-8") as f:
    content = f.read()

# Replace states and imports
content = content.replace("export default function App() {", """export default function App() {
  const [activeTab, setActiveTab] = useState('Query Engine');
  const [systemStats, setSystemStats] = useState<any>({
    repositories: 3, problems: 127, decisions: 842, nodes: 1421, edges: 5832, avg_confidence: 0.89,
    recent_decisions: [
      {repo: "tiangolo/fastapi", decision: "Chose Pydantic v2", type: "adopted"},
      {repo: "langchain-ai/langchain", decision: "Rejected Memory Cache", type: "rejected"},
      {repo: "topoteretes/cognee", decision: "Adopted LanceDB", type: "adopted"}
    ]
  });

  useEffect(() => {
    fetch("http://localhost:8004/system")
      .then(res => res.json())
      .then(data => setSystemStats(data))
      .catch(console.error);
  }, []);""")

content = content.replace("setProblems(p => p < 127 ? p + 3 : 127);", "setProblems(p => p < systemStats.problems ? p + Math.max(1, Math.floor(systemStats.problems/20)) : systemStats.problems);")
content = content.replace("setDecisions(d => d < 842 ? d + 23 : 842);", "setDecisions(d => d < systemStats.decisions ? d + Math.max(1, Math.floor(systemStats.decisions/20)) : systemStats.decisions);")
content = content.replace("}, 50);", "}, 50);")
content = content.replace("}, []);", "}, [systemStats.problems, systemStats.decisions]);")

# Update Sidebar buttons
sidebar_search = """{[
            { icon: Search, label: 'Query Engine', active: true },
            { icon: Layers, label: 'Problem Domains' },
            { icon: GitMerge, label: 'Decision Trees' },
            { icon: ShieldAlert, label: 'Regret Analysis' },
            { icon: Activity, label: 'System Analytics' },
          ].map((item, i) => (
            <button key={i} className={`flex items-center gap-3 px-3 py-2 rounded-md text-sm transition-all duration-200 ${item.active ? 'bg-blue-500/10 text-blue-400 border border-blue-500/20' : 'text-muted hover:text-[#FAFAFA] hover:bg-[rgba(255,255,255,0.04)]'}`}>
              <item.icon className="w-4 h-4" />
              {item.label}
            </button>
          ))}"""

sidebar_replace = """{[
            { icon: Search, label: 'Query Engine' },
            { icon: Layers, label: 'Problem Domains' },
            { icon: GitMerge, label: 'Decision Trees' },
            { icon: ShieldAlert, label: 'Regret Analysis' },
            { icon: Activity, label: 'System Analytics' },
          ].map((item, i) => (
            <button key={i} onClick={() => setActiveTab(item.label)} className={`flex items-center w-full gap-3 px-3 py-2 rounded-md text-sm transition-all duration-200 ${activeTab === item.label ? 'bg-blue-500/10 text-blue-400 border border-[rgba(59,130,246,0.2)]' : 'text-muted hover:text-[#FAFAFA] hover:bg-[rgba(255,255,255,0.04)]'}`}>
              <item.icon className="w-4 h-4" />
              {item.label}
            </button>
          ))}"""

content = content.replace(sidebar_search, sidebar_replace)

# Render main content conditionally
main_start = """{/* Search Header */}"""
main_content_replacement = """{activeTab === 'Query Engine' ? (
            <div className="flex flex-col flex-1 w-full relative h-full">
              {/* Search Header */}"""

content = content.replace(main_start, main_content_replacement)

# Close Query Engine block and add other tabs
main_end_search = """</AnimatePresence>

        </main>"""

new_tabs = """</AnimatePresence>
            </div>
          ) : activeTab === 'System Analytics' ? (
            <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="max-w-4xl w-full mx-auto">
              <h1 className="text-3xl font-semibold mb-2 text-[#FAFAFA] tracking-tight">System Analytics</h1>
              <p className="text-muted text-sm mb-12">Live telemetry from the Engineering Decision Intelligence memory graph.</p>
              
              <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
                <div className="bg-card border border-[rgba(255,255,255,0.08)] rounded-lg p-6">
                  <h3 className="text-xs font-mono text-muted uppercase tracking-wider mb-6">Graph Size</h3>
                  <div className="space-y-4">
                    <div className="flex justify-between items-center"><span className="text-muted">Nodes</span><span className="text-2xl font-mono text-[#FAFAFA]">{systemStats.nodes.toLocaleString()}</span></div>
                    <div className="flex justify-between items-center"><span className="text-muted">Edges</span><span className="text-2xl font-mono text-[#FAFAFA]">{systemStats.edges.toLocaleString()}</span></div>
                    <div className="flex justify-between items-center pt-4 border-t border-[rgba(255,255,255,0.08)]"><span className="text-[#FAFAFA]">Density</span><span className="font-mono text-blue-400">{(systemStats.edges / systemStats.nodes).toFixed(2)} edges/node</span></div>
                  </div>
                </div>
                <div className="bg-card border border-[rgba(255,255,255,0.08)] rounded-lg p-6">
                  <h3 className="text-xs font-mono text-muted uppercase tracking-wider mb-6">Extraction Metrics</h3>
                  <div className="space-y-4">
                    <div className="flex justify-between items-center"><span className="text-muted">Avg Confidence</span><span className="text-2xl font-mono text-success">{Math.round(systemStats.avg_confidence * 100)}%</span></div>
                    <div className="flex justify-between items-center"><span className="text-muted">Problems Extracted</span><span className="text-2xl font-mono text-[#FAFAFA]">{systemStats.problems}</span></div>
                    <div className="flex justify-between items-center"><span className="text-muted">Decisions Mapped</span><span className="text-2xl font-mono text-[#FAFAFA]">{systemStats.decisions}</span></div>
                  </div>
                </div>
              </div>
            </motion.div>
          ) : activeTab === 'Regret Analysis' ? (
            <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="max-w-4xl w-full mx-auto">
              <h1 className="text-3xl font-semibold mb-2 text-[#FAFAFA] tracking-tight">Regret Analysis</h1>
              <p className="text-muted text-sm mb-12">Identifying decisions that were historically reverted or caused downstream pain.</p>
              
              <div className="bg-card border border-[rgba(255,255,255,0.08)] rounded-lg p-6">
                <h3 className="text-xs font-mono text-muted uppercase tracking-wider mb-6 text-[#EF4444]">Most Reversed Decisions</h3>
                <div className="space-y-6">
                  <div className="flex items-start gap-4 pb-6 border-b border-[rgba(255,255,255,0.05)] cursor-pointer group" onClick={() => { setQuery("Small team choosing MongoDB"); setActiveTab('Query Engine'); }}>
                    <div className="w-8 h-8 rounded-full bg-[#EF4444]/20 flex items-center justify-center text-[#EF4444] font-mono text-sm">1</div>
                    <div>
                      <span className="text-lg text-[#FAFAFA] block mb-1 group-hover:text-blue-400 transition-colors">MongoDB for relational data models</span>
                      <span className="text-sm text-muted block mb-3">Reversed by 6 teams due to complex join requirements.</span>
                      <div className="flex gap-2">
                        <span className="text-[10px] uppercase font-mono bg-[rgba(255,255,255,0.05)] px-2 py-1 rounded text-muted">Problem: database-selection</span>
                        <span className="text-[10px] uppercase font-mono bg-[rgba(255,255,255,0.05)] px-2 py-1 rounded text-muted">Outcome: Reverted</span>
                      </div>
                    </div>
                  </div>
                  <div className="flex items-start gap-4 pb-6 border-b border-[rgba(255,255,255,0.05)] cursor-pointer group" onClick={() => { setQuery("Should startups adopt microservices?"); setActiveTab('Query Engine'); }}>
                    <div className="w-8 h-8 rounded-full bg-[#EF4444]/20 flex items-center justify-center text-[#EF4444] font-mono text-sm">2</div>
                    <div>
                      <span className="text-lg text-[#FAFAFA] block mb-1 group-hover:text-blue-400 transition-colors">Microservices too early</span>
                      <span className="text-sm text-muted block mb-3">High operational overhead caused 4 teams to revert to monoliths.</span>
                      <div className="flex gap-2">
                        <span className="text-[10px] uppercase font-mono bg-[rgba(255,255,255,0.05)] px-2 py-1 rounded text-muted">Problem: microservices</span>
                        <span className="text-[10px] uppercase font-mono bg-[rgba(255,255,255,0.05)] px-2 py-1 rounded text-muted">Outcome: Reverted</span>
                      </div>
                    </div>
                  </div>
                  <div className="flex items-start gap-4 cursor-pointer group" onClick={() => { setQuery("Premature Kubernetes adoption"); setActiveTab('Query Engine'); }}>
                    <div className="w-8 h-8 rounded-full bg-[#EF4444]/20 flex items-center justify-center text-[#EF4444] font-mono text-sm">3</div>
                    <div>
                      <span className="text-lg text-[#FAFAFA] block mb-1 group-hover:text-blue-400 transition-colors">Premature Kubernetes adoption</span>
                      <span className="text-sm text-muted block mb-3">Caused deployment bottlenecks in 3 small repositories.</span>
                      <div className="flex gap-2">
                        <span className="text-[10px] uppercase font-mono bg-[rgba(255,255,255,0.05)] px-2 py-1 rounded text-muted">Problem: orchestration</span>
                        <span className="text-[10px] uppercase font-mono bg-[rgba(255,255,255,0.05)] px-2 py-1 rounded text-muted">Outcome: Mixed</span>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </motion.div>
          ) : activeTab === 'Problem Domains' ? (
            <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="max-w-4xl w-full mx-auto">
              <h1 className="text-3xl font-semibold mb-2 text-[#FAFAFA] tracking-tight">Problem Domains</h1>
              <p className="text-muted text-sm mb-12">Categorized problems and their historical recurrence across repositories.</p>
              
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div className="bg-card border border-[rgba(255,255,255,0.08)] rounded-lg p-5 group hover:border-blue-500/50 transition-colors cursor-pointer" onClick={() => { setQuery("How do projects handle schema evolution?"); setActiveTab('Query Engine'); }}>
                  <div className="flex justify-between items-center mb-3"><span className="text-lg text-[#FAFAFA] group-hover:text-blue-400 transition-colors">schema-evolution</span><span className="font-mono text-success">↑12</span></div>
                  <p className="text-sm text-muted mb-4">Managing database migrations and backward compatibility during rapid growth.</p>
                  <div className="flex gap-2">
                    <span className="text-xs bg-[#22C55E]/10 text-success px-2 py-1 rounded">Regret Rate: Low</span>
                  </div>
                </div>
                <div className="bg-card border border-[rgba(255,255,255,0.08)] rounded-lg p-5 group hover:border-blue-500/50 transition-colors cursor-pointer" onClick={() => { setQuery("database selection"); setActiveTab('Query Engine'); }}>
                  <div className="flex justify-between items-center mb-3"><span className="text-lg text-[#FAFAFA] group-hover:text-blue-400 transition-colors">database-selection</span><span className="font-mono text-success">↑9</span></div>
                  <p className="text-sm text-muted mb-4">Choosing the primary datastore for scale vs early stage development speed.</p>
                  <div className="flex gap-2">
                    <span className="text-xs bg-[#F59E0B]/10 text-[#F59E0B] px-2 py-1 rounded">Regret Rate: High</span>
                  </div>
                </div>
                <div className="bg-card border border-[rgba(255,255,255,0.08)] rounded-lg p-5 group hover:border-blue-500/50 transition-colors cursor-pointer" onClick={() => { setQuery("auth strategy"); setActiveTab('Query Engine'); }}>
                  <div className="flex justify-between items-center mb-3"><span className="text-lg text-[#FAFAFA] group-hover:text-blue-400 transition-colors">auth-strategy</span><span className="font-mono text-success">↑7</span></div>
                  <p className="text-sm text-muted mb-4">Implementing JWTs, session tokens, or migrating to OAuth providers.</p>
                  <div className="flex gap-2">
                    <span className="text-xs bg-[#22C55E]/10 text-success px-2 py-1 rounded">Regret Rate: Low</span>
                  </div>
                </div>
                <div className="bg-card border border-[rgba(255,255,255,0.08)] rounded-lg p-5 group hover:border-blue-500/50 transition-colors cursor-pointer" onClick={() => { setQuery("Should startups adopt microservices?"); setActiveTab('Query Engine'); }}>
                  <div className="flex justify-between items-center mb-3"><span className="text-lg text-[#FAFAFA] group-hover:text-blue-400 transition-colors">microservices</span><span className="font-mono text-success">↑6</span></div>
                  <p className="text-sm text-muted mb-4">Decomposing monolithic architectures into distinct deployable services.</p>
                  <div className="flex gap-2">
                    <span className="text-xs bg-[#EF4444]/10 text-[#EF4444] px-2 py-1 rounded">Regret Rate: Critical</span>
                  </div>
                </div>
              </div>
            </motion.div>
          ) : activeTab === 'Decision Trees' ? (
            <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="flex flex-col h-full">
              <h1 className="text-3xl font-semibold mb-2 text-[#FAFAFA] tracking-tight px-8">Decision Trees</h1>
              <p className="text-muted text-sm mb-6 px-8">Exploratory view of causal topology.</p>
              <div className="flex-1 border-t border-[rgba(255,255,255,0.08)] relative mt-4">
                <ReactFlow nodes={initialNodes} edges={initialEdges} fitView proOptions={{ hideAttribution: true }}>
                  <Background color="rgba(255,255,255,0.1)" gap={16} />
                  <Controls className="bg-card border border-[rgba(255,255,255,0.08)] fill-[#FAFAFA]" />
                </ReactFlow>
              </div>
            </motion.div>
          ) : null}

        </main>"""

content = content.replace(main_end_search, new_tabs)

# Update hardcoded stats with systemStats
content = content.replace('1,421', '{systemStats.nodes.toLocaleString()}')
content = content.replace('5,832', '{systemStats.edges.toLocaleString()}')
content = content.replace('89%', '{Math.round(systemStats.avg_confidence * 100)}%')
content = content.replace('REPOSITORIES: 3', 'REPOSITORIES: {systemStats.repositories}')

with open("frontend/src/App.tsx", "w", encoding="utf-8") as f:
    f.write(content)
