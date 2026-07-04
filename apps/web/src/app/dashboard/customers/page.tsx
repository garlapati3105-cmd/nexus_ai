"use client";

import { useSession } from "@/context/SessionContext";
import { Users, Search, Plus, Filter } from "lucide-react";
import { Button } from "@/components/ui/button";

export default function CustomersPage() {
  const { currentRole, activeBranch } = useSession();

  const mockCustomers = [
    { id: 1, name: "Amit Sharma", phone: "+91 98765 43210", visits: 18, lastActive: "Today", rank: "Premium" },
    { id: 2, name: "Priya Patel", phone: "+91 87654 32109", visits: 12, lastActive: "Yesterday", rank: "Standard" },
    { id: 3, name: "Rahul Verma", phone: "+91 76543 21098", visits: 24, lastActive: "2 days ago", rank: "VIP" },
    { id: 4, name: "Sneha Reddy", phone: "+91 99887 76655", visits: 5, lastActive: "3 days ago", rank: "New Account" },
  ];

  return (
    <div className="p-6 space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-bold tracking-tight">Customer Profiles</h1>
          <p className="text-sm text-muted-foreground mt-1">
            Active patients and clients registered at {activeBranch?.name || "Hyderabad Main Branch"}
          </p>
        </div>
        <Button className="flex items-center space-x-2">
          <Plus className="w-4 h-4" />
          <span>Register Patient</span>
        </Button>
      </div>

      <div className="flex gap-4">
        <div className="relative flex-1">
          <Search className="absolute left-3 top-2.5 h-4 w-4 text-muted-foreground" />
          <input 
            type="text" 
            placeholder="Search database by phone or patient name..." 
            className="w-full bg-secondary/20 border border-border/80 rounded-lg pl-9 pr-4 py-2 text-sm focus:outline-none focus:border-primary"
          />
        </div>
        <Button variant="outline" className="flex items-center space-x-2">
          <Filter className="w-4 h-4" />
          <span>Filters</span>
        </Button>
      </div>

      <div className="bg-card border border-border/40 rounded-xl overflow-hidden shadow-sm">
        <table className="w-full border-collapse text-left text-sm">
          <thead>
            <tr className="border-b border-border/40 bg-secondary/10">
              <th className="p-4 font-semibold text-muted-foreground">Patient Name</th>
              <th className="p-4 font-semibold text-muted-foreground">Contact Phone</th>
              <th className="p-4 font-semibold text-muted-foreground">Visits (30 Days)</th>
              <th className="p-4 font-semibold text-muted-foreground">Last Telemetry Check</th>
              <th className="p-4 font-semibold text-muted-foreground">Tier Status</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-border/40">
            {mockCustomers.map((cust) => (
              <tr key={cust.id} className="hover:bg-secondary/15 transition-colors">
                <td className="p-4 font-medium text-foreground">{cust.name}</td>
                <td className="p-4 text-muted-foreground">{cust.phone}</td>
                <td className="p-4 text-foreground font-semibold">{cust.visits} times</td>
                <td className="p-4 text-muted-foreground">{cust.lastActive}</td>
                <td className="p-4">
                  <span className={`text-[10px] uppercase font-bold tracking-wider px-2 py-0.5 rounded border ${
                    cust.rank === "VIP" 
                      ? "border-purple-500/50 text-purple-400 bg-purple-500/5"
                      : cust.rank === "Premium"
                      ? "border-indigo-500/50 text-indigo-400 bg-indigo-500/5"
                      : cust.rank === "Standard"
                      ? "border-slate-500/50 text-slate-400 bg-slate-500/5"
                      : "border-emerald-500/50 text-emerald-400 bg-emerald-500/5"
                  }`}>
                    {cust.rank}
                  </span>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
