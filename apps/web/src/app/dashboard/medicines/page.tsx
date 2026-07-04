"use client";

import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Search, BrainCircuit, TrendingUp, AlertTriangle, Pill } from "lucide-react";
import { Input } from "@/components/ui/input";
import * as motion from "framer-motion/client";

export default function MedicinesPage() {
  const catalog = [
    { sku: "MED-001", name: "Amoxicillin 500mg", expiry: "High Risk (22d)", demand: "Spiking", reorder: "AI Route: Br 7 Transfer", status: "critical" },
    { sku: "MED-002", name: "Paracetamol 650mg", expiry: "Safe (1.2y)", demand: "Stable", reorder: "Supplier: Nov 12", status: "safe" },
    { sku: "MED-003", name: "Azithromycin 250mg", expiry: "Med Risk (80d)", demand: "Dropping", reorder: "Halt Procurement", status: "warning" },
    { sku: "MED-004", name: "Cetirizine 10mg", expiry: "Safe (300d)", demand: "Fast Moving", reorder: "Supplier: Nov 1", status: "safe" },
  ];

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
          <Input placeholder="Query database via semantic intent (e.g. 'Show me fading antibiotics')..." className="pl-10 py-5 bg-card/60 backdrop-blur border-primary/20 shadow-lg" />
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
                {catalog.map((item, i) => (
                  <tr key={i} className="border-b border-border/50 hover:bg-secondary/20 transition-colors">
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
                      {item.demand.includes('Spiking') || item.demand.includes('Fast') ? <TrendingUp className="w-4 h-4 mr-1 text-primary"/> : ''}
                      {item.demand}
                    </td>
                    <td className="px-6 py-4 font-semibold text-muted-foreground">{item.reorder}</td>
                    <td className="px-6 py-4">
                      <span className="text-xs text-primary cursor-pointer hover:underline">View AI Trace</span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </CardContent>
        </Card>
      </motion.div>
    </div>
  );
}
