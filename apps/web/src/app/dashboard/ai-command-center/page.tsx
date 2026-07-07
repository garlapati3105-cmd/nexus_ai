"use client";

import React, { useState, useEffect } from "react";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { 
  BrainCircuit, Cpu, Zap, Activity, Clock, GitBranch, ArrowRight, 
  TrendingUp, CheckCircle, AlertTriangle, Play, RefreshCw, Layers, 
  Sparkles, BookOpen, DollarSign, Command, ShieldCheck 
} from "lucide-react";
import { motion, AnimatePresence } from "framer-motion";

// Configuration of the LangGraph simulation steps
const SCENARIO_YES_STEPS = [
  {
    node: "sales",
    agent: "Sales AI",
    action: "Validating order",
    status: "Active",
    reasoning: "Prescription validated. Dosage matches generic catalog guidance.",
    evidence: ["Generic paracetamol dosage verified", "Prescription scan matches customer record"],
    sources: ["Standard Prescription Directives v4", "Medicine Formulary Guide 2026"],
    confidence: 0.98,
    savings: 0.0,
    outcome: "Order validated for stock checks.",
    risk: "LOW",
    tools: ["prescription_validator", "formulary_resolver"]
  },
  {
    node: "inventory",
    agent: "Inventory AI",
    action: "Checking stock levels",
    status: "Active",
    reasoning: "Local stock level is sufficient (5 units remaining; threshold is 2).",
    evidence: ["Batch paracetamol units: 12", "Requested count: 5"],
    sources: ["Local Branch Stock Ledger"],
    confidence: 0.95,
    savings: 0.0,
    outcome: "Local checkout authorized.",
    risk: "LOW",
    tools: ["stock_level_checker"]
  },
  {
    node: "finance",
    agent: "Finance AI",
    action: "Optimizing prices",
    status: "Active",
    reasoning: "Profit margin check complete. Gross margin optimized at 24.5%.",
    evidence: ["Local unit margin: $5.50", "Transaction total: $27.50"],
    sources: ["Financial Revenue Optimization Policy"],
    confidence: 0.99,
    savings: 5.50,
    outcome: "Billing pricing approved.",
    risk: "LOW",
    tools: ["margin_auditor"]
  },
  {
    node: "invoice",
    agent: "System Engine",
    action: "Billing checkout",
    status: "Completed",
    reasoning: "Successfully completed checkout invoice computation.",
    evidence: ["Invoice total: $27.50", "Client authorization: SIGNED"],
    sources: ["Corporate Billing Policy"],
    confidence: 1.0,
    savings: 5.50,
    outcome: "Invoice INV-A92B1 generated. Billing completed.",
    risk: "LOW",
    tools: ["invoice_generator", "notification_dispatcher"]
  }
];

const SCENARIO_NO_STEPS = [
  {
    node: "sales",
    agent: "Sales AI",
    action: "Validating order",
    status: "Active",
    reasoning: "Amoxicillin prescription validated. Generic alternative authorized by patient.",
    evidence: ["Antibiotic dosage verification positive", "Generic substitution flag active"],
    sources: ["Ministry of Health Guidelines", "Standard Prescription Directives v4"],
    confidence: 0.99,
    savings: 0.0,
    outcome: "Order validated. Proceeding to inventory check.",
    risk: "LOW",
    tools: ["prescription_validator"]
  },
  {
    node: "inventory",
    agent: "Inventory AI",
    action: "Checking stock levels API",
    status: "Active",
    reasoning: "Local stockout detected on Amoxicillin. Initiating inter-branch transfer routing.",
    evidence: ["Local stock count: 0", "Current stock status: STOCKOUT"],
    sources: ["Local Branch Stock Ledger"],
    confidence: 0.92,
    savings: 0.0,
    outcome: "Initiating multi-branch routing protocols.",
    risk: "LOW",
    tools: ["stock_level_checker", "cross_branch_lookup"]
  },
  {
    node: "regional",
    agent: "Regional AI",
    action: "Finding optimal transfer branch",
    status: "Active",
    reasoning: "Branch 2 holds excess stock of 50 units. Proposing inter-branch transfer.",
    evidence: ["Branch 2 current stock: 50", "Distance to Branch 1: 5.2 km"],
    sources: ["Regional Distribution Guidelines", "Logistics Shipping Ledger"],
    confidence: 0.96,
    savings: 0.0,
    outcome: "Transfer route proposed: Branch 2 -> Branch 1.",
    risk: "MEDIUM",
    tools: ["route_optimizer", "travel_estimator"]
  },
  {
    node: "finance",
    agent: "Finance AI",
    action: "Analyzing transfer costs",
    status: "Active",
    reasoning: "Inter-branch transfer shipping cost ($15.00) is cheaper than external purchase ($80.00).",
    evidence: ["Transfer cost: $15.00", "External procurement price: $80.00", "Total savings: $65.00"],
    sources: ["Finance Procurement and Cost Policy"],
    confidence: 0.99,
    savings: 65.00,
    outcome: "Transfer optimization approved. Forwarding to approval gating.",
    risk: "LOW",
    tools: ["margin_auditor", "procurement_cost_comparator"]
  },
  {
    node: "approval",
    agent: "System Engine",
    action: "Verifying approval requirements",
    status: "Active",
    reasoning: "Gating approval resolved. Cost-ratio is within limits under regional guidelines.",
    evidence: ["Approval token: AUTH_REGIONAL", "Risk quotient: 0.12"],
    sources: ["Regional AI Governance Guide"],
    confidence: 0.97,
    savings: 65.00,
    outcome: "Approval granted. Proceeding to invoice.",
    risk: "LOW",
    tools: ["approval_service"]
  },
  {
    node: "invoice",
    agent: "System Engine",
    action: "Billing checkouts",
    status: "Completed",
    reasoning: "Successfully completed checkout invoice computation. Dispatching notifications.",
    evidence: ["Invoice total: $55.00", "Transfer invoice: INV-B83F3"],
    sources: ["Corporate Billing Policy"],
    confidence: 1.0,
    savings: 65.00,
    outcome: "Invoice INV-B83F3 generated. Billing completed.",
    risk: "LOW",
    tools: ["invoice_generator", "notification_dispatcher"]
  }
];

export default function AICommandCenter() {
  const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "https://nexusai-production-bd29.up.railway.app";

  const [scenario, setScenario] = useState<"YES" | "NO">("YES");
  const [stepIndex, setStepIndex] = useState<number>(-1);
  const [isPlaying, setIsPlaying] = useState<boolean>(false);
  const [metrics, setMetrics] = useState({
    moneySaved: 7420.50,
    transfersOptimized: 1845,
    ordersProcessed: 14204,
    stockoutsPrevented: 322,
    expiryLossPrevented: 412,
    aiDecisionsToday: 24502,
    automationRate: 94.6,
  });

  // Pull live metrics from FastAPI API endpoint to display real database outcomes
  useEffect(() => {
    const fetchDbMetrics = async () => {
      try {
        const response = await fetch(`${API_BASE_URL}/api/dashboard/summary`);
        if (response.ok) {
          const data = await response.json();
          // Merge database aggregates with baseline dashboard counters
          setMetrics(prev => ({
            ...prev,
            moneySaved: 7420.50 + (data.total_sales || 0),
            ordersProcessed: 14204 + (data.total_transactions || 0),
            aiDecisionsToday: 24502 + (data.ai_decisions_executed || 0),
            transfersOptimized: 1845 + (data.total_stockouts || 0),
          }));
        }
      } catch (err) {
        console.warn("Live API endpoints offline, using baseline stats.", err);
      }
    };

    fetchDbMetrics();
    const interval = setInterval(fetchDbMetrics, 5000);
    return () => clearInterval(interval);
  }, [API_BASE_URL]);


  const [agents, setAgents] = useState([
    { name: "Regional AI", role: "Macro-Orchestrator", status: "Idle", confidence: 99.1, latency: "140ms", health: 100, task: "Monitoring regional vectors", lastDecision: "Stock allocation approved", tools: ["route_optimizer", "travel_estimator"] },
    { name: "Branch AI", role: "Local Triage", status: "Idle", confidence: 95.5, latency: "85ms", health: 98, task: "Awaiting local queues", lastDecision: "Optimized worker schedule", tools: ["schedule_balancer"] },
    { name: "Inventory AI", role: "Supply Chain", status: "Idle", confidence: 92.0, latency: "450ms", health: 97, task: "FEFO SKU analysis active", lastDecision: "Flagged expiring batches", tools: ["stock_level_checker"] },
    { name: "Sales AI", role: "POS NLP Parser", status: "Idle", confidence: 98.2, latency: "45ms", health: 100, task: "Awaiting prescriptions", lastDecision: "Validated antibiotic script", tools: ["prescription_validator"] },
    { name: "Finance AI", role: "Margin Guardian", status: "Idle", confidence: 99.9, latency: "110ms", health: 100, task: "Auditing gross margins", lastDecision: "Audited procurement costs", tools: ["margin_auditor"] },
  ]);

  const activeSteps = scenario === "YES" ? SCENARIO_YES_STEPS : SCENARIO_NO_STEPS;
  const currentStep = stepIndex >= 0 && stepIndex < activeSteps.length ? activeSteps[stepIndex] : null;

  const updateTelemetryForStep = (step: typeof SCENARIO_YES_STEPS[0]) => {
    // 1. Update Agent Status Grid
    setAgents(prev => prev.map(agent => {
      if (agent.name === step.agent) {
        return {
          ...agent,
          status: "Running",
          task: step.action,
          lastDecision: step.outcome,
          confidence: Math.round(step.confidence * 1000) / 10,
        };
      }
      return { ...agent, status: agent.name === "System Engine" ? "Idle" : "Idle" };
    }));

    // 2. Increment counters as step runs
    setMetrics(prev => ({
      ...prev,
      ordersProcessed: prev.ordersProcessed + 1,
      aiDecisionsToday: prev.aiDecisionsToday + 1,
      moneySaved: prev.moneySaved + step.savings,
      transfersOptimized: step.agent === "Regional AI" ? prev.transfersOptimized + 1 : prev.transfersOptimized,
      stockoutsPrevented: step.node === "inventory" && scenario === "NO" ? prev.stockoutsPrevented + 1 : prev.stockoutsPrevented,
    }));
  };

  // Run simulation loops
  useEffect(() => {
    let timer: NodeJS.Timeout;
    if (isPlaying) {
      if (stepIndex < activeSteps.length - 1) {
        timer = setTimeout(() => {
          const nextIndex = stepIndex + 1;
          setStepIndex(nextIndex);
          updateTelemetryForStep(activeSteps[nextIndex]);
        }, 3000);
      } else {
        setTimeout(() => setIsPlaying(false), 0);
      }
    }
    return () => clearTimeout(timer);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [isPlaying, stepIndex, scenario]);


  const triggerSimulation = (selectedScenario: "YES" | "NO") => {
    setScenario(selectedScenario);
    setStepIndex(0);
    setIsPlaying(true);
    updateTelemetryForStep(selectedScenario === "YES" ? SCENARIO_YES_STEPS[0] : SCENARIO_NO_STEPS[0]);

    // Hit the real backend API orders checkout in the background to execute full multi-agent workflow runs
    fetch(`${API_BASE_URL}/api/orders/`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        customer_id: "99999999-9999-9999-9999-999999999999",
        branch_id: "11111111-1111-1111-1111-111111111111",
        medicine_id: "22222222-2222-2222-2222-222222222222",
        quantity: selectedScenario === "YES" ? 5 : 50,
      }),
    })
      .then(res => res.json())
      .then(data => {
        console.log("Live workflow completed in database:", data);
      })
      .catch(err => console.warn("Live API transaction failed:", err));
  };

  const resetSimulation = () => {
    setStepIndex(-1);
    setIsPlaying(false);
    // Reset all agents to Idle
    setAgents(prev => prev.map(a => ({ ...a, status: "Idle" })));
  };



  // Node position helper inside SVGs
  const nodeCoords = {
    sales: { x: 70, y: 100 },
    inventory: { x: 200, y: 100 },
    finance: { x: 330, y: 50 },
    regional: { x: 330, y: 150 },
    approval: { x: 460, y: 150 },
    invoice: { x: 590, y: 100 },
  };

  return (
    <div className="space-y-6 text-slate-100 p-6 bg-slate-950 min-h-screen">
      {/* Top Header Section */}
      <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4 bg-slate-900/50 p-6 rounded-xl border border-slate-800">
        <div>
          <div className="flex items-center space-x-2">
            <div className="p-2 bg-indigo-500/10 rounded-lg text-indigo-400 border border-indigo-500/20">
              <Command className="w-6 h-6 animate-pulse" />
            </div>
            <div>
              <h2 className="text-3xl font-extrabold tracking-tight bg-gradient-to-r from-white via-indigo-200 to-indigo-400 bg-clip-text text-transparent">AI Command Center</h2>
              <p className="text-slate-400 text-sm mt-1">Real-time telemetry and stateful LangGraph orchestration pipeline.</p>
            </div>
          </div>
        </div>
        
        <div className="flex items-center gap-3">
          <Badge variant="outline" className="border-indigo-500/50 text-indigo-400 bg-indigo-500/10 px-3 py-1 font-mono text-xs">
            Orchestrator: LangGraph v0.2
          </Badge>
          <Badge variant="outline" className="border-emerald-500/50 text-emerald-400 bg-emerald-500/10 px-3 py-1 font-mono text-xs flex items-center">
            <Zap className="w-3 h-3 mr-1 animate-pulse" /> Grok API Active
          </Badge>
        </div>
      </div>

      {/* Simulator Controls & Business Metrics */}
      <div className="grid grid-cols-1 xl:grid-cols-4 gap-6">
        {/* Play Controller */}
        <Card className="bg-slate-900 border-slate-800 xl:col-span-1 shadow-2xl relative overflow-hidden group">
          <div className="absolute top-0 left-0 w-full h-1 bg-gradient-to-r from-indigo-500 via-purple-500 to-pink-500" />
          <CardHeader>
            <CardTitle className="text-lg flex items-center gap-2"><Play className="w-5 h-5 text-indigo-400" /> Simulation Control</CardTitle>
            <CardDescription className="text-slate-400">Trigger standard multi-agent purchase scenarios.</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="flex flex-col gap-3">
              <Button 
                onClick={() => triggerSimulation("YES")} 
                disabled={isPlaying}
                className="w-full h-auto py-2.5 px-3 justify-start bg-gradient-to-r from-emerald-600 to-emerald-500 hover:from-emerald-500 hover:to-emerald-400 text-white border-0 font-medium text-xs whitespace-normal text-left"
              >
                <Sparkles className="w-4 h-4 mr-2 shrink-0" />
                <span>Scenario A: Local Stock (YES)</span>
              </Button>
              <Button 
                onClick={() => triggerSimulation("NO")} 
                disabled={isPlaying}
                className="w-full h-auto py-2.5 px-3 justify-start bg-gradient-to-r from-indigo-600 to-indigo-500 hover:from-indigo-500 hover:to-indigo-400 text-white border-0 font-medium text-xs whitespace-normal text-left"
              >
                <Layers className="w-4 h-4 mr-2 shrink-0" />
                <span>Scenario B: Stockout Transfer (NO)</span>
              </Button>
            </div>
            
            <div className="flex gap-2">
              <Button 
                variant="outline" 
                onClick={resetSimulation}
                className="w-full h-auto py-2 border-slate-800 bg-slate-950 text-slate-300 hover:bg-slate-900 text-xs"
              >
                <RefreshCw className="w-3.5 h-3.5 mr-2" /> Reset
              </Button>
            </div>

            {isPlaying && (
              <div className="p-3 bg-indigo-950/40 rounded-lg border border-indigo-800/40 flex items-center space-x-3">
                <div className="w-3 h-3 bg-indigo-500 rounded-full animate-ping" />
                <span className="text-xs text-indigo-300 font-mono">Running Node: {currentStep?.agent}</span>
              </div>
            )}
          </CardContent>
        </Card>

        {/* Global Impact Dashboard */}
        <div className="xl:col-span-3 grid grid-cols-2 sm:grid-cols-4 gap-4">
          <Card className="bg-slate-900 border-slate-800 shadow-xl p-4 flex flex-col justify-between hover:border-slate-700 transition">
            <div className="flex justify-between items-start text-indigo-400">
              <DollarSign className="w-5 h-5" />
              <Badge className="bg-emerald-500/10 text-emerald-400 border-emerald-500/20 text-[10px]">Optimal</Badge>
            </div>
            <div className="mt-4">
              <span className="text-xs text-slate-400 block font-medium">Estimated Realized Savings</span>
              <motion.h4 key={metrics.moneySaved} initial={{ scale: 0.9 }} animate={{ scale: 1 }} className="text-2xl font-extrabold mt-1 font-mono text-emerald-400">
                ${metrics.moneySaved.toLocaleString("en-US", { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
              </motion.h4>
            </div>
          </Card>

          <Card className="bg-slate-900 border-slate-800 shadow-xl p-4 flex flex-col justify-between hover:border-slate-700 transition">
            <div className="flex justify-between items-start text-indigo-400">
              <GitBranch className="w-5 h-5" />
              <Badge className="bg-indigo-500/10 text-indigo-400 border-indigo-500/20 text-[10px]">Live</Badge>
            </div>
            <div className="mt-4">
              <span className="text-xs text-slate-400 block font-medium">Transfers Optimized</span>
              <motion.h4 key={metrics.transfersOptimized} initial={{ scale: 0.9 }} animate={{ scale: 1 }} className="text-2xl font-extrabold mt-1 font-mono text-white">
                {metrics.transfersOptimized.toLocaleString()}
              </motion.h4>
            </div>
          </Card>

          <Card className="bg-slate-900 border-slate-800 shadow-xl p-4 flex flex-col justify-between hover:border-slate-700 transition">
            <div className="flex justify-between items-start text-indigo-400">
              <Activity className="w-5 h-5" />
              <Badge className="bg-emerald-500/10 text-emerald-400 border-emerald-500/20 text-[10px]">99.8% Success</Badge>
            </div>
            <div className="mt-4">
              <span className="text-xs text-slate-400 block font-medium">Orders Processed</span>
              <motion.h4 key={metrics.ordersProcessed} initial={{ scale: 0.9 }} animate={{ scale: 1 }} className="text-2xl font-extrabold mt-1 font-mono text-white">
                {metrics.ordersProcessed.toLocaleString()}
              </motion.h4>
            </div>
          </Card>

          <Card className="bg-slate-900 border-slate-800 shadow-xl p-4 flex flex-col justify-between hover:border-slate-700 transition">
            <div className="flex justify-between items-start text-indigo-400">
              <ShieldCheck className="w-5 h-5" />
              <Badge className="bg-indigo-500/10 text-indigo-400 border-indigo-500/20 text-[10px]">{metrics.automationRate}% Auto</Badge>
            </div>
            <div className="mt-4">
              <span className="text-xs text-slate-400 block font-medium">AI Decisions Executed</span>
              <motion.h4 key={metrics.aiDecisionsToday} initial={{ scale: 0.9 }} animate={{ scale: 1 }} className="text-2xl font-extrabold mt-1 font-mono text-indigo-400">
                {metrics.aiDecisionsToday.toLocaleString()}
              </motion.h4>
            </div>
          </Card>
        </div>
      </div>

      {/* Interactive LangGraph Visualizer & Timeline */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* SVG Flow Display */}
        <Card className="lg:col-span-2 bg-slate-900 border-slate-800 shadow-xl overflow-hidden relative">
          <div className="absolute top-0 right-0 p-3">
            <Badge variant="outline" className="border-indigo-500/30 text-indigo-400 bg-indigo-950/20 font-mono text-[10px]">
              Type: LLM StateGraph
            </Badge>
          </div>
          <CardHeader className="pb-0">
            <CardTitle className="text-lg flex items-center gap-2"><Layers className="w-5 h-5 text-indigo-500" /> Stateful LangGraph Visualization</CardTitle>
            <CardDescription className="text-slate-400">Active path mapping logic. Nodes emit orange halos when executing step-by-step.</CardDescription>
          </CardHeader>
          <CardContent className="flex justify-center items-center py-10 relative">
            <div className="w-full max-w-[650px] aspect-[650/200] relative">
              <svg width="100%" height="100%" viewBox="0 0 650 200" className="overflow-visible">
                {/* 1. Connector Paths */}
                {/* START -> Sales */}
                <line x1="20" y1="100" x2="70" y2="100" stroke="#334155" strokeWidth="2" />
                {/* Sales -> Inventory */}
                <path d="M 70 100 L 200 100" stroke={stepIndex >= 1 ? "#3b82f6" : "#334155"} strokeWidth="2" strokeDasharray={stepIndex === 0 ? "5,5" : "none"} className={stepIndex === 0 ? "animate-[dash_2s_linear_infinite]" : ""} />
                
                {/* Inventory -> Conditionals */}
                {/* Inventory -> Finance (YES path) */}
                <path d="M 200 100 L 330 50" stroke={stepIndex >= 2 && scenario === "YES" ? "#10b981" : "#334155"} strokeWidth="2" strokeDasharray={stepIndex === 1 && scenario === "YES" ? "5,5" : ""} className={stepIndex === 1 && scenario === "YES" ? "animate-[dash_1s_linear_infinite]" : ""} />
                
                {/* Inventory -> Regional (NO path) */}
                <path d="M 200 100 L 330 150" stroke={stepIndex >= 2 && scenario === "NO" ? "#6366f1" : "#334155"} strokeWidth="2" strokeDasharray={stepIndex === 1 && scenario === "NO" ? "5,5" : ""} className={stepIndex === 1 && scenario === "NO" ? "animate-[dash_1s_linear_infinite]" : ""} />

                {/* Finance -> Invoice (YES path) */}
                <path d="M 330 50 L 590 100" stroke={stepIndex >= 3 && scenario === "YES" ? "#10b981" : "#334155"} strokeWidth="2" strokeDasharray={stepIndex === 2 && scenario === "YES" ? "5,5" : ""} className={stepIndex === 2 && scenario === "YES" ? "animate-[dash_1s_linear_infinite]" : ""} />

                {/* Regional -> Finance (NO path) */}
                <path d="M 330 150 L 330 50" stroke={stepIndex >= 3 && scenario === "NO" ? "#6366f1" : "#334155"} strokeWidth="2" strokeDasharray={stepIndex === 2 && scenario === "NO" ? "5,5" : ""} className={stepIndex === 2 && scenario === "NO" ? "animate-[dash_1s_linear_infinite]" : ""} />

                {/* Finance -> Approval (NO path) */}
                <path d="M 330 50 L 460 150" stroke={stepIndex >= 4 && scenario === "NO" ? "#6366f1" : "#334155"} strokeWidth="2" strokeDasharray={stepIndex === 3 && scenario === "NO" ? "5,5" : ""} className={stepIndex === 3 && scenario === "NO" ? "animate-[dash_1s_linear_infinite]" : ""} />

                {/* Approval -> Invoice (NO path) */}
                <path d="M 460 150 L 590 100" stroke={stepIndex >= 5 && scenario === "NO" ? "#6366f1" : "#334155"} strokeWidth="2" strokeDasharray={stepIndex === 4 && scenario === "NO" ? "5,5" : ""} className={stepIndex === 4 && scenario === "NO" ? "animate-[dash_1s_linear_infinite]" : ""} />

                {/* Invoice -> END */}
                <line x1="590" y1="100" x2="640" y2="100" stroke={stepIndex >= (scenario === "YES" ? 3 : 5) ? "#a855f7" : "#334155"} strokeWidth="2" />

                {/* 2. Drawing Nodes */}
                {Object.entries(nodeCoords).map(([name, coords]) => {
                  // Determine highlights
                  const isNodeActive = currentStep?.node === name;
                  const isNodeVisited = activeSteps.findIndex(s => s.node === name) <= stepIndex && stepIndex !== -1;
                  
                  let strokeColor = "#334155";
                  let fillColor = "#0f172a";
                  
                  if (isNodeActive) {
                    strokeColor = "#f97316"; // Orange halo for active node
                    fillColor = "#fff7ed";
                  } else if (isNodeVisited) {
                    strokeColor = name === "finance" && scenario === "YES" || name === "invoice" ? "#10b981" : "#6366f1";
                  }

                  return (
                    <g key={name} transform={`translate(${coords.x}, ${coords.y})`}>
                      {isNodeActive && (
                        <circle r="22" fill="none" stroke="#f97316" strokeWidth="2" className="animate-ping" />
                      )}
                      <circle r="16" fill={isNodeActive ? "#ea580c" : fillColor} stroke={strokeColor} strokeWidth="3" className="transition-all duration-300" />
                      <text textAnchor="middle" dy="4" fill={isNodeActive ? "#ffffff" : "#94a3b8"} fontSize="9" fontWeight="bold" className="uppercase font-mono">
                        {name.substring(0, 3)}
                      </text>
                      <text x="0" y="28" textAnchor="middle" fill={isNodeActive ? "#f97316" : "#64748b"} fontSize="9" fontWeight="bold" className="capitalize">
                        {name}
                      </text>
                    </g>
                  );
                })}
              </svg>
            </div>
          </CardContent>
        </Card>

        {/* Workflow Timeline Logs */}
        <Card className="bg-slate-900 border-slate-800 shadow-xl overflow-hidden flex flex-col">
          <CardHeader>
            <CardTitle className="text-lg flex items-center gap-2"><Clock className="w-5 h-5 text-indigo-400" /> Execution Tracer</CardTitle>
            <CardDescription className="text-slate-400">Step-by-step audit logs of the running Graph.</CardDescription>
          </CardHeader>
          <CardContent className="flex-1 overflow-y-auto space-y-4 max-h-[300px]">
            {stepIndex === -1 ? (
              <div className="h-full flex flex-col justify-center items-center py-10 text-slate-500 text-sm">
                <Activity className="w-8 h-8 mb-2 opacity-50" />
                <span>Simulation inactive. Click play to trace workflows.</span>
              </div>
            ) : (
              <div className="space-y-4">
                {activeSteps.slice(0, stepIndex + 1).map((step, idx) => (
                  <motion.div key={idx} initial={{ opacity: 0, x: -10 }} animate={{ opacity: 1, x: 0 }} className="flex gap-3 text-xs leading-relaxed border-l-2 border-indigo-800 pl-4 py-1 relative">
                    <div className="absolute -left-[5px] top-2 w-2 h-2 rounded-full bg-indigo-500" />
                    <div>
                      <div className="flex items-center gap-2">
                        <span className="font-bold text-slate-100">{step.agent}</span>
                        <Badge className="bg-indigo-950 text-indigo-300 border-indigo-800/30 scale-90">{step.action}</Badge>
                      </div>
                      <p className="text-slate-400 mt-1">{step.outcome}</p>
                    </div>
                  </motion.div>
                ))}
              </div>
            )}
          </CardContent>
        </Card>
      </div>

      {/* Agents Telemetry List */}
      <Card className="bg-slate-900 border-slate-800 shadow-xl">
        <CardHeader>
          <CardTitle className="text-lg flex items-center gap-2"><Cpu className="w-5 h-5 text-indigo-400" /> Active AI Agent Fleet</CardTitle>
          <CardDescription className="text-slate-400">Live capability telemetry tracking agent latencies and execution logs.</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-5 gap-4">
            {agents.map((agent) => (
              <Card key={agent.name} className="bg-slate-950/60 border-slate-850 hover:border-slate-800 transition duration-300 relative group overflow-hidden">
                {agent.status === "Running" && (
                  <div className="absolute top-0 right-0 w-2 h-2 rounded-full bg-orange-500 animate-ping m-3" />
                )}
                <CardHeader className="p-4 pb-2">
                  <div className="flex justify-between items-start">
                    <div>
                      <CardTitle className="text-sm font-bold text-slate-200">{agent.name}</CardTitle>
                      <CardDescription className="text-[10px] text-slate-500">{agent.role}</CardDescription>
                    </div>
                    <Badge className={
                      agent.status === "Running" 
                        ? "bg-orange-500/10 text-orange-400 border-orange-500/20 text-[9px]" 
                        : "bg-slate-950 text-slate-450 border-slate-850 text-[9px]"
                    }>
                      {agent.status}
                    </Badge>
                  </div>
                </CardHeader>
                <CardContent className="p-4 pt-0 space-y-3 text-[11px]">
                  <div className="bg-slate-900/60 rounded p-2 border border-slate-800/50">
                    <span className="text-slate-500 block text-[9px] uppercase tracking-wider font-bold mb-0.5">Active Job</span>
                    <span className="text-slate-350 block font-medium truncate">{agent.task}</span>
                  </div>
                  
                  <div className="grid grid-cols-2 gap-2 text-[10px] text-slate-400 font-mono">
                    <div>
                      <span className="text-[9px] block text-slate-500">Latency</span>
                      <span className="font-bold">{agent.latency}</span>
                    </div>
                    <div>
                      <span className="text-[9px] block text-slate-500">Confidence</span>
                      <span className="font-bold text-emerald-400">{agent.confidence}%</span>
                    </div>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* Real-time Explainability & RAG Panels */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Real-time Explainability */}
        <Card className="bg-slate-900 border-slate-800 shadow-xl">
          <CardHeader>
            <CardTitle className="text-lg flex items-center gap-2"><ShieldCheck className="w-5 h-5 text-indigo-400" /> Explainability & Audit Engine</CardTitle>
            <CardDescription className="text-slate-400">Verifiably explain decisions made by agents using financial models and alternatives.</CardDescription>
          </CardHeader>
          <CardContent className="min-h-[250px] flex flex-col justify-between">
            {currentStep ? (
              <div className="space-y-4 text-sm">
                <div className="grid grid-cols-2 gap-4">
                  <div className="p-3 bg-slate-955 rounded-lg border border-slate-800">
                    <span className="text-[10px] font-bold text-slate-500 uppercase tracking-widest block mb-1">Expected Outcome</span>
                    <p className="text-slate-300 font-medium">{currentStep.outcome}</p>
                  </div>
                  <div className="p-3 bg-slate-955 rounded-lg border border-slate-800">
                    <span className="text-[10px] font-bold text-slate-500 uppercase tracking-widest block mb-1">Business Impact</span>
                    <p className="text-slate-300 font-medium">Estimated savings: ${currentStep.savings.toFixed(2)}</p>
                  </div>
                </div>

                <div className="p-3 bg-slate-955 rounded-lg border border-slate-800">
                  <span className="text-[10px] font-bold text-slate-500 uppercase tracking-widest block mb-1">Agent Reasoning</span>
                  <p className="text-slate-200">{currentStep.reasoning}</p>
                </div>

                {scenario === "NO" && stepIndex >= 2 && (
                  <div className="p-3 bg-slate-955 rounded-lg border border-slate-800">
                    <span className="text-[10px] font-bold text-slate-500 uppercase tracking-widest block mb-1">Alternative Actions Evaluated</span>
                    <ul className="list-disc pl-4 text-slate-400 text-xs mt-1 space-y-1">
                      <li>Procure from external wholesale pharmaceutical supplier.</li>
                      <li>Substitute with equivalent generic molecular formulation.</li>
                    </ul>
                  </div>
                )}
              </div>
            ) : (
              <div className="flex-1 flex flex-col justify-center items-center py-10 text-slate-500">
                <ShieldCheck className="w-8 h-8 mb-2 opacity-50" />
                <span>Select a scenario and click execute to verify audit records.</span>
              </div>
            )}
          </CardContent>
        </Card>

        {/* Real-time Knowledge Panel (RAG) */}
        <Card className="bg-slate-900 border-slate-800 shadow-xl">
          <CardHeader>
            <CardTitle className="text-lg flex items-center gap-2"><BookOpen className="w-5 h-5 text-indigo-400" /> RAG Knowledge Retrieval</CardTitle>
            <CardDescription className="text-slate-400">Context injected into agent prompts from documents library.</CardDescription>
          </CardHeader>
          <CardContent className="min-h-[250px] flex flex-col justify-between">
            {currentStep ? (
              <div className="space-y-4">
                <div className="space-y-3">
                  <span className="text-[10px] font-bold text-slate-500 uppercase tracking-widest block">Retrieved Evidence Documents</span>
                  <div className="space-y-2">
                    {currentStep.sources.map((src, i) => (
                      <div key={i} className="flex justify-between items-center p-2.5 bg-slate-955 rounded-lg border border-slate-800/80 text-xs">
                        <div className="flex items-center gap-2">
                          <BookOpen className="w-4 h-4 text-indigo-400" />
                          <span className="text-slate-200 font-medium">{src}</span>
                        </div>
                        <Badge className="bg-emerald-500/10 text-emerald-400 border-emerald-500/20 text-[9px] font-mono">
                          Score: 0.94
                        </Badge>
                      </div>
                    ))}
                  </div>
                </div>

                <div className="space-y-2">
                  <span className="text-[10px] font-bold text-slate-500 uppercase tracking-widest block">Extracted Vector Chunks</span>
                  <div className="p-3 bg-slate-955 rounded-lg border border-slate-800 text-xs text-slate-400 leading-relaxed font-mono">
                    {currentStep.evidence.map((ev, i) => (
                      <div key={i} className="flex items-start gap-1 pb-1">
                        <span className="text-indigo-400 mr-1">▸</span>
                        <span>{ev}</span>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            ) : (
              <div className="flex-1 flex flex-col justify-center items-center py-10 text-slate-500">
                <BookOpen className="w-8 h-8 mb-2 opacity-50" />
                <span>Select a scenario to inspect RAG document matches.</span>
              </div>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
