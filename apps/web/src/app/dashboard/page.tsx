"use client";

import { useState, useEffect } from "react";
import { useSession } from "@/context/SessionContext";
import { useRouter } from "next/navigation";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { 
  BrainCircuit, LineChart, PackageMinus, 
  TrendingUp, AlertTriangle, Zap, Clock, ShieldCheck,
  Activity, Network, ShoppingCart, Users, CheckSquare, Layers
} from "lucide-react";
import * as motion from "framer-motion/client";

export default function DashboardRouter() {
  const { currentRole, activeBranch } = useSession();
  const router = useRouter();

  // Route landing based on roles
  const roleName = currentRole ? currentRole.toUpperCase() : "GUEST";

  useEffect(() => {
    if (!currentRole) return;
    const roleUpper = currentRole.toUpperCase();
    if (roleUpper === "PHARMACIST") {
      router.replace("/dashboard/pharmacist");
    } else if (roleUpper === "CASHIER") {
      router.replace("/dashboard/cashier");
    } else if (roleUpper === "INVENTORY") {
      router.replace("/dashboard/inventory");
    } else if (roleUpper === "FINANCE") {
      router.replace("/dashboard/finance");
    }
  }, [currentRole, router]);

  if (["PHARMACIST", "CASHIER", "INVENTORY", "FINANCE"].includes(roleName)) {
    return (
      <div className="flex h-[60vh] w-full items-center justify-center">
        <div className="flex flex-col items-center space-y-4">
          <div className="w-10 h-10 border-4 border-primary border-t-transparent rounded-full animate-spin" />
          <p className="text-sm font-medium text-muted-foreground animate-pulse">Redirecting to workspace...</p>
        </div>
      </div>
    );
  }

  if (roleName === "BRANCH_MANAGER") {
    return <BranchManagerDashboardView activeBranch={activeBranch} />;
  }

  if (roleName === "REGIONAL_MANAGER") {
    return <RegionalManagerDashboardView />;
  }

  if (roleName === "CEO" || roleName === "ADMIN") {
    return <CEODashboardView />;
  }

  // Fallback for custom/unhandled roles
  return (
    <div className="flex h-[60vh] w-full items-center justify-center">
      <p className="text-sm text-muted-foreground font-medium">Welcome to Nexus AI. Access your workflow via the sidebar panel.</p>
    </div>
  );
}

// ----------------------------------------------------
// 1. CEO DASHBOARD VIEW
// ----------------------------------------------------
function CEODashboardView() {
  const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "https://nexusai-production-bd29.up.railway.app";
  
  const [metrics, setMetrics] = useState({
    totalSales: 4.2,
    aiDecisions: 842,
  });

  useEffect(() => {
    const fetchDbMetrics = async () => {
      try {
        const response = await fetch(`${API_BASE_URL}/api/dashboard/summary`);
        if (response.ok) {
          const data = await response.json();
          const additionalSalesLakhs = (data.total_sales || 0) / 100000;
          setMetrics({
            totalSales: Math.round((4.2 + additionalSalesLakhs) * 100) / 100,
            aiDecisions: 842 + (data.ai_decisions_executed || 0),
          });
        }
      } catch (err) {
        console.warn("Live API endpoints offline, using baseline stats.", err);
      }
    };

    fetchDbMetrics();
    const interval = setInterval(fetchDbMetrics, 5000);
    return () => clearInterval(interval);
  }, [API_BASE_URL]);

  const kpis = [
    { title: "AI Hours Saved", value: "1,420", unit: "hrs", change: "+12% vs last month", positive: true, icon: Clock },
    { title: "Net Savings", value: `${metrics.totalSales}`, unit: "L", change: "+8.4% vs last month", positive: true, icon: TrendingUp },
    { title: "Autocorrections", value: `${metrics.aiDecisions}`, unit: "nodes", change: "+24% volume", positive: true, icon: Network },
    { title: "Expiry Avoidance", value: "1.1", unit: "L", change: "-65% waste", positive: true, icon: ShieldCheck },
  ];

  return (
    <div className="space-y-6 pb-24 max-w-7xl mx-auto">
      {/* CEO AI Briefing Card - Stripe-Style */}
      <motion.div initial={{ opacity: 0, scale: 0.98 }} animate={{ opacity: 1, scale: 1 }} transition={{ duration: 0.4, ease: "easeOut" }}>
        <Card className="bg-gradient-to-br from-primary/10 via-background to-background border-border/40 shadow-sm relative overflow-hidden">
          <div className="absolute -left-10 -top-10 w-40 h-40 bg-primary/20 rounded-full blur-3xl opacity-50" />
          <CardContent className="p-6 md:p-8 relative z-10 flex flex-col md:flex-row items-start justify-between gap-6">
            <div className="space-y-3 max-w-2xl">
              <div className="flex items-center space-x-2.5">
                <div className="relative flex h-3 w-3">
                  <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-primary opacity-75"></span>
                  <span className="relative inline-flex rounded-full h-3 w-3 bg-primary"></span>
                </div>
                <h2 className="text-xl font-bold tracking-tight">CEO Briefing Center</h2>
              </div>
              <p className="text-sm md:text-base text-muted-foreground leading-relaxed">
                Global chain operations are optimal. Network revenue is probabilistically mapped at <strong className="text-foreground">₹45L</strong> today. Branch 4 requires critical Amoxicillin transfer (98% confidence). Global inventory health runs at 94%.
              </p>
            </div>
            <div className="text-right shrink-0 bg-background/50 backdrop-blur-md p-4 rounded-xl border border-border/50 shadow-sm">
              <p className="text-[10px] uppercase font-bold tracking-widest text-muted-foreground mb-1">Global Health</p>
              <p className="text-4xl font-black tracking-tighter text-foreground">98.4%</p>
            </div>
          </CardContent>
        </Card>
      </motion.div>

      {/* Extreme Density KPIs */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        {kpis.map((kpi, i) => (
          <motion.div key={kpi.title} initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: i * 0.05 + 0.1 }}>
            <Card className="bg-background border-border/40 shadow-sm hover:shadow-md transition-shadow group">
              <CardContent className="p-5">
                <div className="flex justify-between items-center mb-3">
                  <h3 className="text-[11px] uppercase font-bold tracking-wider text-muted-foreground group-hover:text-foreground transition-colors">{kpi.title}</h3>
                  <kpi.icon className="h-4 w-4 text-muted-foreground/50 group-hover:text-primary transition-colors" />
                </div>
                <div className="flex items-baseline space-x-1">
                  <span className="text-3xl font-bold tracking-tighter">{kpi.value}</span>
                  <span className="text-sm font-semibold text-muted-foreground">{kpi.unit}</span>
                </div>
                <div className="mt-2 text-[11px] font-medium text-emerald-500">{kpi.change}</div>
              </CardContent>
            </Card>
          </motion.div>
        ))}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Animated Network Visualization */}
        <Card className="lg:col-span-2 bg-background border-border/40 shadow-sm relative overflow-hidden">
          <CardHeader className="relative z-10 border-b border-border/30 pb-4 bg-secondary/5">
            <div className="flex justify-between items-center">
              <div>
                <CardTitle className="text-lg tracking-tight flex items-center">
                  <Network className="w-4 h-4 mr-2 text-primary" /> Architecture Nodes
                </CardTitle>
                <CardDescription className="text-xs">Live graph traversal visualization</CardDescription>
              </div>
              <Badge variant="outline" className="bg-emerald-500/10 text-emerald-500 border-emerald-500/20 font-semibold shadow-sm">
                10 Branches Live
              </Badge>
            </div>
          </CardHeader>
          <CardContent className="relative z-10 h-[350px] flex items-center justify-center p-0 overflow-hidden bg-dot-pattern">
            <div className="relative w-full h-full max-w-lg mx-auto">
              <motion.div 
                animate={{ scale: [1, 1.2, 1], opacity: [0.1, 0.3, 0.1] }} 
                transition={{ duration: 4, repeat: Infinity, ease: "easeInOut" }}
                className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-48 h-48 bg-primary rounded-full blur-3xl pointer-events-none"
              />
              <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-10 h-10 bg-background border border-primary/40 rounded-xl flex items-center justify-center shadow-[0_0_20px_rgba(59,130,246,0.3)] z-20">
                <BrainCircuit className="w-5 h-5 text-primary" />
              </div>
              
              <div className="absolute top-[15%] left-[20%] w-3 h-3 bg-emerald-500 rounded-full shadow-[0_0_10px_rgba(16,185,129,0.5)] z-20" />
              <div className="absolute top-[25%] right-[25%] w-4 h-4 bg-destructive rounded-full shadow-[0_0_10px_rgba(239,68,68,0.5)] z-20 animate-pulse" />
              <div className="absolute bottom-[20%] left-[30%] w-3 h-3 bg-emerald-500 rounded-full z-20" />
              <div className="absolute bottom-[25%] right-[20%] w-3 h-3 bg-emerald-500 rounded-full z-20" />

              <svg className="absolute inset-0 w-full h-full z-10 pointer-events-none" aria-hidden="true">
                <line x1="50%" y1="50%" x2="20%" y2="15%" stroke="var(--border)" strokeWidth="1" />
                <line x1="50%" y1="50%" x2="30%" y2="80%" stroke="var(--border)" strokeWidth="1" />
                <line x1="50%" y1="50%" x2="80%" y2="75%" stroke="var(--border)" strokeWidth="1" />
                <motion.line 
                  initial={{ strokeDashoffset: 10 }}
                  animate={{ strokeDashoffset: 0 }}
                  transition={{ duration: 0.5, repeat: Infinity, ease: "linear" }}
                  x1="50%" y1="50%" x2="75%" y2="25%" 
                  stroke="var(--destructive)" strokeWidth="2" strokeDasharray="4 4" 
                />
              </svg>

              <div className="absolute top-[18%] right-[12%] bg-background/90 backdrop-blur-md border border-destructive/30 p-2.5 rounded-lg shadow-xl z-30">
                <span className="font-bold text-[10px] uppercase tracking-wider text-destructive flex items-center">
                  <AlertTriangle className="w-3 h-3 mr-1"/> Requesting Transfer
                </span>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* AI Activity Traces */}
        <Card className="bg-background border-border/40 shadow-sm flex flex-col">
          <CardHeader className="border-b border-border/30 pb-4 bg-secondary/5">
            <CardTitle className="text-lg tracking-tight flex items-center">
              <Activity className="w-4 h-4 mr-2 text-foreground/50" /> Global Protocol Trace
            </CardTitle>
          </CardHeader>
          <CardContent className="flex-1 overflow-y-auto p-0">
            <div className="divide-y divide-border/20">
              {[
                { ai: "Inventory AI", msg: "Amoxicillin baseline deflected by -18%", time: "2s", color: "text-amber-500", dot: "bg-amber-500" },
                { ai: "Logistics Router", msg: "Branch 7 mapping completed successfully", time: "15s", color: "text-primary", dot: "bg-primary" },
                { ai: "Finance AI", msg: "Re-calculated margin overhead", time: "1m", color: "text-emerald-500", dot: "bg-emerald-500" },
                { ai: "Sales AI", msg: "Processed 12 active carts", time: "3m", color: "text-foreground", dot: "bg-foreground/50" },
              ].map((feed, i) => (
                <div key={i} className="p-4 hover:bg-secondary/30 transition-colors flex items-start space-x-3 group cursor-default">
                  <div className={`mt-1.5 w-1.5 h-1.5 rounded-full shrink-0 ${feed.dot} shadow-[0_0_5px_currentColor]`} />
                  <div className="flex-1">
                    <div className="flex justify-between items-baseline">
                      <p className={`text-[11px] font-bold uppercase tracking-widest ${feed.color}`}>{feed.ai}</p>
                      <p className="text-[10px] text-muted-foreground font-mono">{feed.time}</p>
                    </div>
                    <p className="text-sm font-medium mt-1 text-foreground/90 group-hover:text-foreground transition-colors">{feed.msg}</p>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}

// ----------------------------------------------------
// 2. REGIONAL MANAGER DASHBOARD VIEW
// ----------------------------------------------------
function RegionalManagerDashboardView() {
  const kpis = [
    { title: "Regional Revenue", value: "₹15.8", unit: "L", change: "+10% vs last month", positive: true, icon: TrendingUp },
    { title: "Regional Orders", value: "482", unit: "txns", change: "Daily average", positive: true, icon: ShoppingCart },
    { title: "Pending Transfers", value: "14", unit: "items", change: "Within Hyderabad North", positive: true, icon: Network },
    { title: "Shortage Risks", value: "3", unit: "SKUs", change: "Requires inter-branch movement", positive: false, icon: PackageMinus },
  ];

  const branches = [
    { name: "Jubilee Hills Branch", sales: "₹4.5L", status: "Optimal", stockLevel: "94%" },
    { name: "Banjara Hills Branch", sales: "₹3.8L", status: "Optimal", stockLevel: "91%" },
    { name: "Gachibowli Branch", sales: "₹4.2L", status: "Low Stock", stockLevel: "79%" },
    { name: "Begumpet Branch", sales: "₹3.3L", status: "Optimal", stockLevel: "88%" },
  ];

  return (
    <div className="space-y-6 pb-24 max-w-7xl mx-auto">
      <motion.div initial={{ opacity: 0, scale: 0.98 }} animate={{ opacity: 1, scale: 1 }} transition={{ duration: 0.4 }}>
        <Card className="bg-gradient-to-br from-indigo-500/10 via-background to-background border-border/40 shadow-sm relative overflow-hidden">
          <CardContent className="p-6 md:p-8 relative z-10 flex flex-col md:flex-row justify-between items-start gap-6">
            <div className="space-y-3">
              <h2 className="text-xl font-bold tracking-tight">Hyderabad North Region</h2>
              <p className="text-sm text-muted-foreground">
                Monitoring 4 active branches. Standard operations running. Low stock flag triggered at Gachibowli Branch.
              </p>
            </div>
            <div className="bg-background/80 border border-border/40 p-4 rounded-xl shadow-xs">
              <p className="text-[10px] uppercase font-bold text-muted-foreground mb-1">Region Health</p>
              <p className="text-3xl font-extrabold text-foreground">92.0%</p>
            </div>
          </CardContent>
        </Card>
      </motion.div>

      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        {kpis.map((kpi) => (
          <Card key={kpi.title} className="bg-background border-border/40">
            <CardContent className="p-5">
              <div className="flex justify-between items-center mb-3">
                <h3 className="text-[11px] uppercase font-bold text-muted-foreground">{kpi.title}</h3>
                <kpi.icon className="h-4 w-4 text-muted-foreground/50" />
              </div>
              <div className="flex items-baseline space-x-1">
                <span className="text-3xl font-bold">{kpi.value}</span>
                <span className="text-sm text-muted-foreground">{kpi.unit}</span>
              </div>
              <div className="mt-2 text-[11px] font-medium text-emerald-500">{kpi.change}</div>
            </CardContent>
          </Card>
        ))}
      </div>

      <div className="grid grid-cols-2 gap-6">
        <Card className="bg-background border-border/40 col-span-2 md:col-span-1">
          <CardHeader>
            <CardTitle className="text-lg">Branch Performance</CardTitle>
            <CardDescription className="text-xs">Assigned regional branch metrics</CardDescription>
          </CardHeader>
          <CardContent className="p-0">
            <div className="divide-y divide-border/20">
              {branches.map((b, i) => (
                <div key={i} className="p-4 flex justify-between items-center">
                  <div>
                    <p className="font-semibold text-sm">{b.name}</p>
                    <p className="text-xs text-muted-foreground">Stock Level: {b.stockLevel}</p>
                  </div>
                  <div className="text-right">
                    <p className="font-bold text-sm">{b.sales}</p>
                    <span className={`text-[10px] px-1.5 py-0.5 rounded leading-none ${b.status === "Optimal" ? "bg-emerald-500/10 text-emerald-400" : "bg-amber-500/10 text-amber-400"}`}>{b.status}</span>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>

        {/* Regional transfers approvals */}
        <Card className="bg-background border-border/40 col-span-2 md:col-span-1 flex flex-col">
          <CardHeader>
            <CardTitle className="text-lg">Regional Approvals Queue</CardTitle>
            <CardDescription className="text-xs">Pending stock movements inside region</CardDescription>
          </CardHeader>
          <CardContent className="flex-1 p-4 flex flex-col justify-center items-center text-center text-muted-foreground">
            <CheckSquare className="w-10 h-10 mb-2 opacity-50" />
            <p className="text-sm font-semibold">2 Pending Regional Transfers</p>
            <p className="text-xs mt-1">Review transfer triggers inside Hyderabad North region.</p>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}

// ----------------------------------------------------
// 3. BRANCH MANAGER DASHBOARD VIEW
// ----------------------------------------------------
function BranchManagerDashboardView({ activeBranch }: { activeBranch: any }) {
  const kpis = [
    { title: "Today's Revenue", value: "₹1.82", unit: "L", change: "+14.2% vs yesterday", icon: TrendingUp },
    { title: "Active Orders", value: "48", unit: "bills", change: "12 completed, 36 processing", icon: ShoppingCart },
    { title: "Low Stock Items", value: "7", unit: "items", change: "Requires transfer request", icon: PackageMinus },
    { title: "Prescription Expiries", value: "34", unit: "boxes", change: "Within 30 days window", icon: AlertTriangle },
  ];

  return (
    <div className="space-y-6 pb-24 max-w-7xl mx-auto">
      <motion.div initial={{ opacity: 0, scale: 0.98 }} animate={{ opacity: 1, scale: 1 }} transition={{ duration: 0.4 }}>
        <Card className="bg-gradient-to-br from-emerald-500/10 via-background to-background border-border/40 shadow-sm relative overflow-hidden">
          <CardContent className="p-6 md:p-8 relative z-10 flex justify-between items-start gap-6">
            <div className="space-y-3">
              <h2 className="text-xl font-bold tracking-tight">{activeBranch?.name || "Jubilee Hills Branch"} Status</h2>
              <p className="text-sm text-muted-foreground">
                Branch Terminal active. Node triggers monitored under local credentials. Expiring batches flagged for inter-branch transfer.
              </p>
            </div>
            <div className="bg-background/80 border border-border/40 p-4 rounded-xl shadow-xs">
              <p className="text-[10px] uppercase font-bold text-muted-foreground mb-1">Local Health</p>
              <p className="text-3xl font-extrabold text-foreground">96.8%</p>
            </div>
          </CardContent>
        </Card>
      </motion.div>

      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        {kpis.map((kpi) => (
          <Card key={kpi.title} className="bg-background border-border/40">
            <CardContent className="p-5">
              <div className="flex justify-between items-center mb-3">
                <h3 className="text-[11px] uppercase font-bold text-muted-foreground">{kpi.title}</h3>
                <kpi.icon className="h-4 w-4 text-muted-foreground/50" />
              </div>
              <div className="flex items-baseline space-x-1">
                <span className="text-3xl font-bold">{kpi.value}</span>
                <span className="text-sm text-muted-foreground">{kpi.unit}</span>
              </div>
              <div className="mt-2 text-[11px] font-medium text-emerald-500">{kpi.change}</div>
            </CardContent>
          </Card>
        ))}
      </div>

      <div className="grid grid-cols-3 gap-6">
        {/* Local Orders list */}
        <Card className="col-span-3 lg:col-span-2 bg-background border-border/40">
          <CardHeader>
            <CardTitle className="text-lg">Recent Branch Orders</CardTitle>
            <CardDescription className="text-xs">Live customer checkouts recorded today</CardDescription>
          </CardHeader>
          <CardContent className="p-0">
            <div className="divide-y divide-border/20">
              {[
                { id: "TXN-79401", cust: "Amit Sharma", count: "3 Meds", total: "₹1,450", time: "10 mins ago", status: "Completed" },
                { id: "TXN-79402", cust: "Priya Patel", count: "1 Meds", total: "₹450", time: "22 mins ago", status: "Processing" },
                { id: "TXN-79403", cust: "Rahul Verma", count: "5 Meds", total: "₹4,120", time: "1 hr ago", status: "Processing" },
              ].map((txn) => (
                <div key={txn.id} className="p-4 flex justify-between items-center hover:bg-secondary/10 transition-colors">
                  <div>
                    <p className="font-semibold text-sm">{txn.cust}</p>
                    <p className="text-xs text-muted-foreground">{txn.id} • {txn.count}</p>
                  </div>
                  <div className="text-right">
                    <p className="font-bold text-sm">{txn.total}</p>
                    <span className={`text-[9px] uppercase font-bold tracking-wider px-1.5 py-0.5 rounded ${txn.status === "Completed" ? "bg-emerald-500/10 text-emerald-400" : "bg-amber-500/10 text-amber-400"}`}>{txn.status}</span>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>

        {/* Local Stockout Alerts */}
        <Card className="col-span-3 lg:col-span-1 bg-background border-border/40 flex flex-col">
          <CardHeader>
            <CardTitle className="text-lg">Local Stock Shortages</CardTitle>
            <CardDescription className="text-xs">Items requiring urgent stock transfers</CardDescription>
          </CardHeader>
          <CardContent className="flex-1 p-4 flex flex-col justify-center items-center text-center text-muted-foreground">
            <Layers className="w-10 h-10 mb-2 opacity-50 text-indigo-400" />
            <p className="text-sm font-semibold">Paracetamol running low</p>
            <p className="text-xs mt-1">Suggested transfer logic of 200 units from Jubilee Hills to Banjara Hills.</p>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
