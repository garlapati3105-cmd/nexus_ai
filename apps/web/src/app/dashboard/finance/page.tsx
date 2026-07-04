"use client";

import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { DollarSign, Landmark, ArrowUpRight, ArrowDownRight } from "lucide-react";

export default function FinancePage() {
  const metrics = [
    { title: "Network Revenue", value: "₹42,50,000", change: "+14.2%", trend: "up" },
    { title: "COGS", value: "₹21,00,000", change: "+4.1%", trend: "down" },
    { title: "Operating Margin", value: "48.2%", change: "+2.1%", trend: "up" },
    { title: "Dead Stock Write-offs", value: "₹45,000", change: "-85%", trend: "down" },
  ];

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-3xl font-bold tracking-tight">Finance & Margin</h2>
        <p className="text-muted-foreground mt-1">AI-audited financial ledgers across the Nexus network.</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {metrics.map((m, i) => (
          <Card key={i} className="bg-card/50 border-border/50">
            <CardHeader className="flex flex-row items-center justify-between pb-2">
              <CardTitle className="text-sm font-medium text-muted-foreground">
                {m.title}
              </CardTitle>
              <DollarSign className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{m.value}</div>
              <p className={`text-xs mt-1 flex items-center ${
                (m.trend === 'up' && !m.title.includes('Write-off')) || (m.trend === 'down' && m.title.includes('Write-off')) 
                ? "text-emerald-500" : "text-destructive"
              }`}>
                {m.trend === 'up' ? <ArrowUpRight className="w-3 h-3 mr-1" /> : <ArrowDownRight className="w-3 h-3 mr-1" />}
                {m.change}
              </p>
            </CardContent>
          </Card>
        ))}
      </div>

      <Card className="bg-card/50 border-border/50 h-[400px] flex items-center justify-center">
        <div className="text-center">
          <Landmark className="h-12 w-12 text-muted-foreground mx-auto mb-4 opacity-50" />
          <h3 className="text-lg font-semibold">Margin Trajectory Chart</h3>
          <p className="text-sm text-muted-foreground mt-2 max-w-sm mx-auto">
            Interactive visualizer component requiring Supabase TS structural data.
          </p>
        </div>
      </Card>
    </div>
  );
}
