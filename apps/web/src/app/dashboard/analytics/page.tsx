"use client";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { LineChart, Activity, DollarSign, BrainCircuit, Box, Eye } from "lucide-react";
import * as motion from "framer-motion/client";

export default function AnalyticsPage() {
  return (
    <div className="space-y-6">
      <div className="flex justify-between items-end">
        <div>
          <h2 className="text-3xl font-bold tracking-tight">Predictive Analytics</h2>
          <p className="text-muted-foreground mt-1">AI-steered forecasting covering 30 to 90-day probabilistic trajectories.</p>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        {[
          { title: "Revenue Forecast (30D)", val: "₹14.2M", conf: "94% Conf", trend: "+12%" },
          { title: "Demand Deficit Risk", val: "Critical", conf: "89% Conf", trend: "Amoxicillin Spike" },
          { title: "Expiry Value at Risk", val: "₹1.4L", conf: "99% Conf", trend: "-8% vs last month" },
          { title: "Projected Margin", val: "44.2%", conf: "91% Conf", trend: "+1.2%" },
        ].map(item => (
          <Card key={item.title} className="bg-card/50 border-border/50">
            <CardContent className="p-4">
              <h5 className="text-xs text-muted-foreground uppercase">{item.title}</h5>
              <div className="mt-2 flex justify-between items-end">
                <span className="text-xl font-bold">{item.val}</span>
                <Badge variant="outline" className="text-[10px] bg-secondary/50">{item.conf}</Badge>
              </div>
              <p className="text-xs text-emerald-500 mt-2 font-medium">{item.trend}</p>
            </CardContent>
          </Card>
        ))}
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <motion.div initial={{ opacity: 0, scale: 0.95 }} animate={{ opacity: 1, scale: 1 }}>
          <Card className="bg-card/50 border-border/50 h-[350px] relative overflow-hidden group hover:border-primary/50 transition">
            <div className="absolute top-4 right-4"><Badge className="bg-primary/20 text-primary hover:bg-primary/20"><BrainCircuit className="w-3 h-3 mr-1"/> ML Forecast Node</Badge></div>
            <div className="h-full flex flex-col justify-center items-center text-center p-6">
              <LineChart className="h-12 w-12 text-primary mb-4 opacity-50" />
              <h3 className="text-lg font-semibold cursor-pointer">Revenue Protections</h3>
              <p className="text-sm text-muted-foreground mt-2 max-w-sm">
                Graphs will dynamically mount upon Supabase Edge hydration sequence via API deployment.
              </p>
            </div>
          </Card>
        </motion.div>
        
        <motion.div initial={{ opacity: 0, scale: 0.95 }} animate={{ opacity: 1, scale: 1 }} transition={{ delay: 0.1 }}>
          <Card className="bg-card/50 border-border/50 h-[350px] relative overflow-hidden group hover:border-emerald-500/50 transition">
            <div className="absolute top-4 right-4"><Badge variant="outline" className="bg-emerald-500/10 text-emerald-500"><Box className="w-3 h-3 mr-1"/> FEFO Prediction Node</Badge></div>
            <div className="h-full flex flex-col justify-center items-center text-center p-6">
              <Activity className="h-12 w-12 text-emerald-500 mb-4 opacity-50" />
              <h3 className="text-lg font-semibold cursor-pointer">Impending Expirations (90D)</h3>
              <p className="text-sm text-muted-foreground mt-2 max-w-sm">
                Graphs will dynamically mount upon Supabase Edge hydration sequence via API deployment.
              </p>
            </div>
          </Card>
        </motion.div>
      </div>
    </div>
  );
}
