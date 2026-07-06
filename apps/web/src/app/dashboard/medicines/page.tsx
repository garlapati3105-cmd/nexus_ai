"use client";

import { useState, useMemo } from "react";
import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Search, BrainCircuit, TrendingUp, AlertTriangle, Pill, ExternalLink } from "lucide-react";
import { Input } from "@/components/ui/input";
import * as motion from "framer-motion/client";

const ALL_CATALOG = [
  { sku: "MED-001", name: "Amoxicillin 500mg", expiry: "High Risk (22d)", demand: "Spiking", reorder: "AI Route: Br 7 Transfer", status: "critical", reasoning: "Prescription spike detected. 22% demand surge over 48h. Transfer from Branch 7 is the optimal action to prevent stockout." },
  { sku: "MED-002", name: "Paracetamol 650mg", expiry: "Safe (1.2y)", demand: "Stable", reorder: "Supplier: Nov 12", status: "safe", reasoning: "Stock levels are optimal. No action needed. Reorder scheduled with Meditrina Suppliers." },
  { sku: "MED-003", name: "Azithromycin 250mg", expiry: "Med Risk (80d)", demand: "Dropping", reorder: "Halt Procurement", status: "warning", reasoning: "Demand velocity is declining. Halting procurement avoids ₹4,200 dead stock write-off." },
  { sku: "MED-004", name: "Cetirizine 10mg", expiry: "Safe (300d)", demand: "Fast Moving", reorder: "Supplier: Nov 1", status: "safe", reasoning: "Seasonal allergy velocity increasing. Reorder triggered ahead of schedule to capitalize on demand window." },
  { sku: "MED-005", name: "Metformin 500mg", expiry: "Safe (180d)", demand: "Stable", reorder: "Supplier: Dec 5", status: "safe", reasoning: "Chronic disease category. Demand is stable month-over-month. No intervention required." },
  { sku: "MED-006", name: "Atorvastatin 10mg", expiry: "Low Risk (4m)", demand: "Dropping", reorder: "Reduce Order Volume", status: "warning", reasoning: "Statin demand dropped 15% following generic competitor entry. Recommend reducing standing order volume by 30%." },
];

export default function MedicinesPage() {
  const [search, setSearch] = useState("");
  const [expandedSku, setExpandedSku] = useState<string | null>(null);

  const catalog = useMemo(() => {
    if (!search.trim()) return ALL_CATALOG;
    const q = search.toLowerCase();
    return ALL_CATALOG.filter(
      (item) =>
        item.name.toLowerCase().includes(q) ||
        item.sku.toLowerCase().includes(q) ||
        item.demand.toLowerCase().includes(q)
    );
  }, [search]);

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-end">
        <div>
          <h2 className="text-3xl font-bold tracking-tight">Medicine Intelligence</h2>
          <p className="text-muted-foreground mt-1">AI-driven SKU catalog forecasting demand curves, expiry vectors, and automated reorder strategies.</p>
        </div>
      </div>

      <div className="flex space-x-4 mb-6 relative z-10">
        <div className="relative flex-1 max-w-xl">
          <BrainCircuit className="absolute left-3 top-3 h-4 w-4 text-primary" />
          <Input
            placeholder="Search medicines, SKUs, demand status..."
            className="pl-10 py-5 bg-card/60 backdrop-blur border-primary/20 shadow-lg"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
          />
        </div>
      </div>

      <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }}>
        <Card className="bg-card/50 border-border/50">
          <CardContent className="p-0">
            <table className="w-full text-sm text-left">
              <thead className="text-xs text-muted-foreground bg-secondary/50 border-b border-border">
                <tr>
                  <th className="px-6 py-4 font-medium">SKU / Medicine</th>
                  <th className="px-6 py-4 font-medium">AI Expiry Risk</th>
                  <th className="px-6 py-4 font-medium">Demand Vector</th>
                  <th className="px-6 py-4 font-medium">Auto-Reorder Strategy</th>
                  <th className="px-6 py-4 font-medium">Explainability</th>
                </tr>
              </thead>
              <tbody>
                {catalog.length === 0 ? (
                  <tr>
                    <td colSpan={5} className="px-6 py-12 text-center text-muted-foreground text-sm">
                      No medicines match your search.
                    </td>
                  </tr>
                ) : (
                  catalog.map((item, i) => (
                    <>
                      <tr key={i} className="border-b border-border/50 hover:bg-secondary/20 transition-colors cursor-pointer" onClick={() => setExpandedSku(expandedSku === item.sku ? null : item.sku)}>
                        <td className="px-6 py-4">
                          <p className="font-bold flex items-center"><Pill className="w-3 h-3 mr-2 opacity-50"/> {item.name}</p>
                          <p className="text-[10px] text-muted-foreground uppercase tracking-widest mt-0.5">{item.sku}</p>
                        </td>
                        <td className="px-6 py-4">
                          <Badge variant="outline" className={`
                            ${item.status === "critical" ? "border-destructive text-destructive bg-destructive/10" : 
                              item.status === "warning" ? "border-amber-500 text-amber-500 bg-amber-500/10" : "border-emerald-500 text-emerald-500 bg-emerald-500/10"}
                          `}>
                            {item.status === "critical" && <AlertTriangle className="w-3 h-3 mr-1" />}
                            {item.expiry}
                          </Badge>
                        </td>
                        <td className="px-6 py-4 font-medium flex items-center">
                          {(item.demand.includes("Spiking") || item.demand.includes("Fast")) ? <TrendingUp className="w-4 h-4 mr-1 text-primary"/> : ""}
                          {item.demand}
                        </td>
                        <td className="px-6 py-4 font-semibold text-muted-foreground">{item.reorder}</td>
                        <td className="px-6 py-4">
                          <span className="text-xs text-primary cursor-pointer hover:underline flex items-center gap-1">
                            View AI Trace <ExternalLink className="w-3 h-3"/>
                          </span>
                        </td>
                      </tr>
                      {expandedSku === item.sku && (
                        <tr key={`${i}-expanded`} className="bg-secondary/10 border-b border-border/50">
                          <td colSpan={5} className="px-6 py-4">
                            <div className="flex items-start gap-3">
                              <BrainCircuit className="w-4 h-4 text-primary shrink-0 mt-0.5" />
                              <div>
                                <p className="text-xs font-bold uppercase tracking-widest text-primary mb-1">AI Reasoning Trace</p>
                                <p className="text-sm text-muted-foreground">{item.reasoning}</p>
                              </div>
                            </div>
                          </td>
                        </tr>
                      )}
                    </>
                  ))
                )}
              </tbody>
            </table>
          </CardContent>
        </Card>
      </motion.div>
    </div>
  );
}
