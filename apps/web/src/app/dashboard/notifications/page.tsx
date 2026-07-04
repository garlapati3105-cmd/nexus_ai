"use client";

import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { BrainCircuit, AlertTriangle, ShieldAlert, Sparkles, Filter } from "lucide-react";
import * as motion from "framer-motion/client";

export default function NotificationsPage() {
  const notifications = [
    { title: "Critical Stockout: Amoxicillin", message: "Branch 4 is entirely out of stock. Patients are being turned away.", time: "2 mins ago", type: "critical" },
    { title: "AI Transfer Recommendation", message: "Regional AI has negotiated an 80 unit transfer from Branch 7. Awaiting approval.", time: "1 min ago", type: "ai" },
    { title: "Margin Bleed Alert", message: "Finance AI detected Branch 2 discounting cough syrup 18% below floor price.", time: "2 hours ago", type: "warning" },
    { title: "Nightly Audit Complete", message: "Inventory AI successfully mapped 120,400 FEFO pathways.", time: "8 hours ago", type: "system" },
  ];

  return (
    <div className="space-y-6 max-w-4xl mx-auto">
      <div>
        <h2 className="text-3xl font-bold tracking-tight">Notification Intelligence</h2>
        <p className="text-muted-foreground mt-1">AI-classified system alerts and decision requests.</p>
      </div>

      <div className="flex space-x-2">
        <Badge className="bg-primary/20 text-primary border-primary/30 cursor-pointer hover:bg-primary/30"><Filter className="w-3 h-3 mr-1"/> All Events</Badge>
        <Badge variant="outline" className="border-destructive/30 text-destructive cursor-pointer hover:bg-destructive/10">Critical Alerts</Badge>
        <Badge variant="outline" className="border-amber-500/30 text-amber-500 cursor-pointer hover:bg-amber-500/10">Warnings</Badge>
        <Badge variant="outline" className="border-emerald-500/30 text-emerald-500 cursor-pointer hover:bg-emerald-500/10">AI Traces</Badge>
      </div>

      <div className="space-y-4">
        {notifications.map((notif, i) => (
          <motion.div key={i} initial={{ opacity: 0, x: -10 }} animate={{ opacity: 1, x: 0 }} transition={{ delay: i * 0.1 }}>
            <Card className="bg-card/40 backdrop-blur border-border/50 hover:border-border transition-colors cursor-pointer group">
              <CardContent className="p-4 flex items-start space-x-4 relative overflow-hidden">
                <div className={`absolute left-0 top-0 w-1 h-full ${notif.type === 'critical' ? 'bg-destructive' : notif.type === 'ai' ? 'bg-primary' : notif.type === 'warning' ? 'bg-amber-500' : 'bg-muted'}`} />
                
                <div className={`h-10 w-10 rounded flex items-center justify-center shrink-0 border ${
                  notif.type === 'critical' ? 'bg-destructive/10 text-destructive border-destructive/20' : 
                  notif.type === 'ai' ? 'bg-primary/10 text-primary border-primary/20' : 
                  notif.type === 'warning' ? 'bg-amber-500/10 text-amber-500 border-amber-500/20' : 
                  'bg-secondary text-muted-foreground border-border'
                }`}>
                  {notif.type === 'critical' ? <ShieldAlert className="w-5 h-5" /> : 
                   notif.type === 'ai' ? <BrainCircuit className="w-5 h-5" /> : 
                   notif.type === 'warning' ? <AlertTriangle className="w-5 h-5" /> : <Sparkles className="w-5 h-5" />}
                </div>
                <div className="flex-1">
                  <div className="flex justify-between items-start">
                    <h4 className="font-semibold text-sm group-hover:text-primary transition-colors">{notif.title}</h4>
                    <span className="text-xs text-muted-foreground font-mono">{notif.time}</span>
                  </div>
                  <p className="text-sm text-foreground/80 mt-1">{notif.message}</p>
                </div>
              </CardContent>
            </Card>
          </motion.div>
        ))}
      </div>
    </div>
  );
}
