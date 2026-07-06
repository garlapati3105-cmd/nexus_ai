"use client";

import { useState, useMemo } from "react";
import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Input } from "@/components/ui/input";
import { Search, Filter, AlertTriangle, Fingerprint, MapPin } from "lucide-react";
import * as motion from "framer-motion/client";

const ALL_INVENTORY = [
  { sku: "NEX-AMX-500", name: "Amoxicillin 500mg", type: "Antibiotic", stock: 0, branch: "Banjara Hills", status: "Critical Out" },
  { sku: "NEX-PAR-650", name: "Paracetamol 650mg", type: "Analgesic", stock: 1450, branch: "Banjara Hills", status: "Optimal" },
  { sku: "NEX-AZT-250", name: "Azithromycin 250mg", type: "Antibiotic", stock: 12, branch: "Jubilee Hills", status: "Low Stock" },
  { sku: "NEX-CET-10", name: "Cetirizine 10mg", type: "Antihistamine", stock: 450, branch: "Madhapur", status: "Optimal" },
  { sku: "NEX-MET-500", name: "Metformin 500mg", type: "Antidiabetic", stock: 320, branch: "Madhapur", status: "Optimal" },
  { sku: "NEX-ATR-10", name: "Atorvastatin 10mg", type: "Statin", stock: 5, branch: "Jubilee Hills", status: "Low Stock" },
  { sku: "NEX-OFX-200", name: "Ofloxacin 200mg", type: "Antibiotic", stock: 0, branch: "Gachibowli", status: "Critical Out" },
  { sku: "NEX-PAN-40", name: "Pantoprazole 40mg", type: "PPI", stock: 780, branch: "Gachibowli", status: "Optimal" },
];

export default function InventoryPage() {
  const [search, setSearch] = useState("");
  const [branchFilter, setBranchFilter] = useState("");

  const inventory = useMemo(() => {
    return ALL_INVENTORY.filter((item) => {
      const matchSearch =
        !search ||
        item.name.toLowerCase().includes(search.toLowerCase()) ||
        item.sku.toLowerCase().includes(search.toLowerCase());
      const matchBranch =
        !branchFilter || item.branch.toLowerCase().includes(branchFilter.toLowerCase());
      return matchSearch && matchBranch;
    });
  }, [search, branchFilter]);

  return (
    <div className="space-y-6 max-w-7xl mx-auto pb-12">
      <div className="flex justify-between items-end">
        <div>
          <h2 className="text-2xl font-bold tracking-tight">Global Inventory Grid</h2>
          <p className="text-sm text-muted-foreground mt-1">Live distributed stock metrics across all nodes.</p>
        </div>
        <div className="flex items-center space-x-2 text-sm text-muted-foreground font-medium bg-secondary/50 px-3 py-1.5 rounded-full border border-border/40">
          <div className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse"/>
          <span>Live Sync Active</span>
        </div>
      </div>

      <div className="flex items-center justify-between mb-4">
        <div className="flex space-x-3 w-full max-w-lg">
          <div className="relative flex-1">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
            <Input
              placeholder="Search SKUs or generic names..."
              className="pl-9 bg-background border-border/50 h-9 text-sm rounded-md shadow-sm"
              value={search}
              onChange={(e) => setSearch(e.target.value)}
            />
          </div>
          <div className="relative">
            <Filter className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
            <Input
              placeholder="Branch Filter"
              className="pl-9 w-40 bg-background border-border/50 h-9 text-sm rounded-md shadow-sm"
              value={branchFilter}
              onChange={(e) => setBranchFilter(e.target.value)}
            />
          </div>
        </div>
      </div>

      <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.3 }}>
        <Card className="bg-background border-border/40 shadow-sm overflow-hidden rounded-xl">
          <CardContent className="p-0">
            <table className="w-full text-sm text-left">
              <thead className="text-xs text-muted-foreground bg-secondary/20 border-b border-border/40">
                <tr>
                  <th className="px-6 py-4 font-semibold tracking-tight uppercase">SKU Identity</th>
                  <th className="px-6 py-4 font-semibold tracking-tight uppercase">Medicine</th>
                  <th className="px-6 py-4 font-semibold tracking-tight uppercase">Node Link</th>
                  <th className="px-6 py-4 font-semibold tracking-tight uppercase text-right">Volume</th>
                  <th className="px-6 py-4 font-semibold tracking-tight uppercase text-right">Status</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-border/20">
                {inventory.length === 0 ? (
                  <tr>
                    <td colSpan={5} className="px-6 py-12 text-center text-muted-foreground text-sm">
                      No inventory items match your search.
                    </td>
                  </tr>
                ) : (
                  inventory.map((item, i) => (
                    <tr key={i} className="group hover:bg-secondary/30 transition-colors">
                      <td className="px-6 py-4">
                        <div className="flex items-center space-x-2 text-muted-foreground">
                          <Fingerprint className="w-4 h-4 opacity-70"/>
                          <span className="font-mono text-xs">{item.sku}</span>
                        </div>
                      </td>
                      <td className="px-6 py-4">
                        <div className="font-semibold tracking-tight group-hover:text-primary transition-colors flex items-center">
                          {item.name}
                        </div>
                        <div className="text-[11px] text-muted-foreground mt-0.5">{item.type}</div>
                      </td>
                      <td className="px-6 py-4">
                        <div className="flex items-center text-muted-foreground">
                          <MapPin className="w-3.5 h-3.5 mr-1.5 opacity-70" />
                          <span className="font-medium text-xs">{item.branch}</span>
                        </div>
                      </td>
                      <td className="px-6 py-4 text-right">
                        <span className="font-mono font-bold tracking-tight">{item.stock}</span>
                      </td>
                      <td className="px-6 py-4 text-right">
                        <Badge variant="outline" className={`ml-auto font-semibold uppercase tracking-tight text-[10px] flex w-fit items-center px-2 py-0.5
                          ${item.status === "Critical Out" ? "border-transparent bg-destructive/15 text-destructive" : 
                            item.status === "Low Stock" ? "border-transparent bg-amber-500/15 text-amber-500" : "border-transparent bg-emerald-500/10 text-emerald-500"}
                        `}>
                          {item.status.includes("Critical") && <AlertTriangle className="w-3 h-3 mr-1" />}
                          {item.status}
                        </Badge>
                      </td>
                    </tr>
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
