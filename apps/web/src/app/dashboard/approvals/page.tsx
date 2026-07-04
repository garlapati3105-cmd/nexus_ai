"use client";

import { Card, CardContent, CardHeader, CardTitle, CardDescription, CardFooter } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Check, X, Info, LineChart, Cpu, BrainCircuit, Clock } from "lucide-react";
import * as motion from "framer-motion/client";

export default function ApprovalsPage() {
  return (
    <div className="space-y-6 max-w-5xl mx-auto pb-12">
      <div>
        <h2 className="text-2xl font-bold tracking-tight">Human Approval Center</h2>
        <p className="text-sm text-muted-foreground mt-1">Review and authorize critical logistical decisions gated by the AI.</p>
      </div>

      <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.4, ease: "easeOut" }}>
        <Card className="border-border/40 shadow-2xl bg-card overflow-hidden relative">
          <div className="absolute top-0 left-0 w-1 h-full bg-primary" />
          <CardHeader className="flex flex-row items-start justify-between pb-4 bg-secondary/10 border-b border-border/40">
            <div>
              <div className="flex items-center space-x-3 mb-2">
                <Badge className="bg-primary/10 text-primary border-primary/20 shadow-none font-semibold">AI Recommendation</Badge>
                <span className="text-xs text-muted-foreground font-mono flex items-center">
                  <Clock className="w-3 h-3 mr-1"/> 2 mins ago
                </span>
              </div>
              <CardTitle className="text-xl tracking-tight">Transfer Amoxicillin 500mg</CardTitle>
              <CardDescription className="text-sm mt-1">Staging logic: Route 80 Units from Branch 7 to Branch 4.</CardDescription>
            </div>
            <div className="text-right">
              <span className="text-[10px] uppercase font-bold tracking-widest text-muted-foreground block mb-1">Compute Confidence</span>
              <span className="text-3xl font-black text-emerald-500 tracking-tighter drop-shadow-sm">98.2%</span>
            </div>
          </CardHeader>
          <CardContent className="pt-6">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              
              {/* Explainable AI Panel */}
              <div className="bg-background rounded-xl p-5 border border-border/40 shadow-sm relative overflow-hidden group">
                <div className="absolute top-0 right-0 p-4 opacity-5 pointer-events-none group-hover:opacity-10 transition-opacity">
                  <BrainCircuit className="w-24 h-24" />
                </div>
                <h4 className="flex items-center text-sm font-semibold mb-4 tracking-tight">
                  <BrainCircuit className="w-4 h-4 mr-2 text-primary" /> Reasoning Trace
                </h4>
                <ul className="space-y-3 text-sm text-muted-foreground">
                  <li className="flex items-start">
                    <Check className="w-4 h-4 mr-2.5 text-emerald-500 shrink-0 mt-0.5" /> 
                    <span>Demand for Amoxicillin at Branch 4 increased <strong className="text-foreground font-semibold">22% structurally</strong> over 48h.</span>
                  </li>
                  <li className="flex items-start">
                    <Check className="w-4 h-4 mr-2.5 text-emerald-500 shrink-0 mt-0.5" /> 
                    <span>Branch 7 holds 120 surplus units expiring in <strong className="text-foreground font-semibold">40 days</strong>.</span>
                  </li>
                  <li className="flex items-start">
                    <Check className="w-4 h-4 mr-2.5 text-emerald-500 shrink-0 mt-0.5" /> 
                    <span>Inter-branch courier cost (₹120) mitigates primary supplier indent (₹4,500).</span>
                  </li>
                </ul>
              </div>

              {/* Business Impact Panel */}
              <div className="bg-secondary/20 rounded-xl p-5 border border-border/40 shadow-inner flex flex-col justify-center">
                <h4 className="flex items-center text-sm font-semibold mb-5 tracking-tight">
                  <LineChart className="w-4 h-4 mr-2 text-emerald-500" /> Projected Impact
                </h4>
                <div className="grid grid-cols-2 gap-x-4 gap-y-6">
                  <div>
                    <span className="text-[10px] uppercase font-bold tracking-wider text-muted-foreground">Expected Savings</span>
                    <p className="text-xl font-bold text-emerald-500 tracking-tight mt-0.5">₹18,200</p>
                  </div>
                  <div>
                    <span className="text-[10px] uppercase font-bold tracking-wider text-muted-foreground">Time Preserved</span>
                    <p className="text-xl font-bold text-foreground tracking-tight mt-0.5">45 mins</p>
                  </div>
                  <div>
                    <span className="text-[10px] uppercase font-bold tracking-wider text-muted-foreground">Risk Audit</span>
                    <p className="text-sm font-semibold text-emerald-500 mt-1">Very Low</p>
                  </div>
                  <div>
                    <span className="text-[10px] uppercase font-bold tracking-wider text-muted-foreground">Clinical Outcome</span>
                    <p className="text-sm font-semibold text-foreground mt-1">Zero Stockouts</p>
                  </div>
                </div>
              </div>
            </div>
          </CardContent>
          <CardFooter className="bg-background border-t border-border/40 py-4 px-6 flex justify-between items-center">
            <Button variant="ghost" className="text-muted-foreground hover:bg-secondary/50 hover:text-foreground text-sm font-medium">
              <Info className="w-4 h-4 mr-2" /> Request Alternative Route
            </Button>
            <div className="space-x-3">
              <Button variant="outline" className="border-border/50 text-foreground hover:bg-destructive/10 hover:text-destructive hover:border-destructive/30 transition-colors">
                <X className="w-4 h-4 mr-2" /> Reject
              </Button>
              <Button className="bg-foreground text-background hover:bg-foreground/90 shadow-md font-semibold">
                <Cpu className="w-4 h-4 mr-2" /> Execute Transfer
              </Button>
            </div>
          </CardFooter>
        </Card>
      </motion.div>
    </div>
  );
}
