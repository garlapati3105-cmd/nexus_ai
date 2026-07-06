"use client";

import { useState } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { AlertTriangle, CheckCircle2, Brain, BarChart3, TrendingUp, Sparkles, CornerDownRight, Cpu, Send } from "lucide-react";
import * as motion from "framer-motion/client";

interface Message {
  sender: "user" | "bot";
  text: string;
}

const BOT_RESPONSES: Record<string, string> = {
  stock: "Current local stock of Amoxicillin is 0 units. Branch 7 has 120 surplus — inter-branch dispatch is staged and awaiting approval.",
  transfer: "Transfer route proposed: Branch 7 → Branch 4. Estimated dispatch time: 2 hours. Courier cost: ₹120.",
  margin: "Local revenue margin is 92%. Amoxicillin deficit is currently blocking ₹18,200 in pending orders.",
  demand: "21-day demand velocity shows prescription demand at Branch 4 surged 22% for Amoxicillin 500mg.",
  revenue: "Today's revenue stands at ₹1.2L. Peak volume session active. AI estimates ₹1.8L by close.",
  dispatch: "Dispatch authorization has been forwarded to the Human Approval Center. It's awaiting CEO sign-off.",
};

function getBotResponse(text: string): string {
  const q = text.toLowerCase();
  for (const [key, response] of Object.entries(BOT_RESPONSES)) {
    if (q.includes(key)) return response;
  }
  return "I track stock levels, demand vectors, transfer routes, margins, and revenue. Try asking about 'stock', 'margin', or 'demand'.";
}

export default function BranchDashboard() {
  const [inputText, setInputText] = useState("");
  const [messages, setMessages] = useState<Message[]>([
    {
      sender: "bot",
      text: "Hello Manager. Analyzing branch metrics via localized ChromaDB index. You are currently losing revenue opportunities on Amoxicillin 500mg. I have routed a sub-query to the Regional AI. Branch 7 has surplus and can dispatch 80 units within 2 hours.",
    },
  ]);
  const [resolveState, setResolveState] = useState<"idle" | "loading" | "done">("idle");
  const [dispatchDone, setDispatchDone] = useState(false);

  const sendMessage = () => {
    if (!inputText.trim()) return;
    const userMsg = inputText.trim();
    setInputText("");
    setMessages((prev) => [...prev, { sender: "user", text: userMsg }]);
    setTimeout(() => {
      setMessages((prev) => [...prev, { sender: "bot", text: getBotResponse(userMsg) }]);
    }, 700);
  };

  const handleAutoResolve = async () => {
    setResolveState("loading");
    await new Promise((r) => setTimeout(r, 1500));
    setResolveState("done");
    setMessages((prev) => [
      ...prev,
      { sender: "bot", text: "Auto-Resolve initiated. Transfer of 80 units routed from Branch 7 to Branch 4. Approval request sent to CEO dashboard." },
    ]);
  };

  const handleAuthorize = async () => {
    setDispatchDone(true);
    setMessages((prev) => [
      ...prev,
      { sender: "bot", text: "Dispatch authorized. 80 units of Amoxicillin 500mg scheduled for delivery. ETA: 2 hours." },
    ]);
  };

  return (
    <div className="space-y-6 max-w-7xl mx-auto pb-12">
      <div className="flex flex-col md:flex-row md:justify-between md:items-end gap-4">
        <div>
          <h2 className="text-2xl font-bold tracking-tight">Branch Node 4</h2>
          <p className="text-sm text-muted-foreground mt-1">Banjara Hills Sector • Local Execution Mode</p>
        </div>
        <div className="flex space-x-2">
          <Badge variant="outline" className="border-emerald-500/30 text-emerald-500 bg-emerald-500/10 px-3 py-1 font-semibold rounded-md">
            <CheckCircle2 className="w-3.5 h-3.5 mr-1.5" /> Edge Network Online
          </Badge>
          <Badge variant="outline" className="border-primary/30 text-primary bg-primary/10 px-3 py-1 font-semibold rounded-md">
            <Brain className="w-3.5 h-3.5 mr-1.5" /> AI Active
          </Badge>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Card className="bg-background border-border/40 col-span-1 shadow-sm">
          <CardContent className="p-5 flex flex-col h-full justify-center">
            <p className="text-[10px] uppercase font-bold tracking-widest text-muted-foreground mb-1">Efficiency Ratio</p>
            <h4 className="font-black text-4xl tracking-tighter text-emerald-500">92%</h4>
          </CardContent>
        </Card>
        
        <Card className="bg-background border-border/40 col-span-1 shadow-sm">
          <CardContent className="p-5 flex flex-col h-full justify-center">
            <p className="text-[10px] uppercase font-bold tracking-widest text-muted-foreground mb-1">Local Revenue</p>
            <div className="flex items-baseline space-x-2">
              <h4 className="font-black text-4xl tracking-tighter">₹1.2<span className="text-xl">L</span></h4>
            </div>
            <p className="text-xs text-emerald-500 mt-2 flex items-center font-medium"><TrendingUp className="w-3 h-3 mr-1"/> Peak volume</p>
          </CardContent>
        </Card>
        
        <Card className="bg-destructive/5 border-destructive/20 col-span-2 shadow-sm group">
          <CardContent className="p-5 flex flex-col justify-between h-full">
            <div className="flex items-start justify-between">
              <div>
                <p className="text-[10px] uppercase font-bold tracking-widest text-destructive mb-1 flex items-center">
                  <AlertTriangle className="w-3 h-3 mr-1" /> Action Required (Protocol ID: 8X2)
                </p>
                <h4 className="font-bold text-xl tracking-tight text-foreground">Deficit: Amoxicillin Component</h4>
              </div>
            </div>
            <div className="flex flex-col sm:flex-row justify-between items-start sm:items-end mt-4 gap-4">
              <p className="text-sm text-foreground/80 max-w-sm">Local storage empty. RAG forecasting predicts 14 orders blocked today. Regional routing is staged.</p>
              <Button
                size="sm"
                disabled={resolveState === "loading" || resolveState === "done"}
                onClick={handleAutoResolve}
                className="bg-foreground text-background hover:bg-foreground/90 font-semibold shadow-md whitespace-nowrap"
              >
                <Sparkles className="w-4 h-4 mr-2"/>
                {resolveState === "loading" ? "Routing..." : resolveState === "done" ? "Routed ✓" : "Auto-Resolve in Terminal"}
              </Button>
            </div>
          </CardContent>
        </Card>
      </div>

      <Card className="bg-background border-border/40 overflow-hidden relative shadow-md rounded-xl">
        <CardHeader className="border-b border-border/30 bg-secondary/5 py-4 px-5">
          <div className="flex justify-between items-center">
            <CardTitle className="flex items-center space-x-2 text-lg tracking-tight font-semibold">
              <Sparkles className="w-5 h-5 text-primary" />
              <span>Interactive Copilot</span>
            </CardTitle>
            <span className="text-[10px] font-mono text-muted-foreground uppercase tracking-wider bg-background px-2 py-1 rounded border border-border/50">Terminal Live</span>
          </div>
        </CardHeader>
        <CardContent className="p-0 h-[500px] flex flex-col relative bg-dot-pattern">
          
          <div className="flex-1 overflow-y-auto p-5 space-y-4 scroll-smooth">
            {messages.map((msg, i) => (
              <div key={i} className={`flex ${msg.sender === "user" ? "justify-end" : "justify-start"} w-full`}>
                {msg.sender === "bot" ? (
                  <div className="bg-card border border-border/50 shadow-sm rounded-2xl rounded-tl-sm p-5 text-sm w-full max-w-[85%]">
                    <div className="flex items-center space-x-2 mb-3">
                      <div className="w-6 h-6 rounded-full bg-primary/20 flex items-center justify-center">
                        <Brain className="w-3 h-3 text-primary" />
                      </div>
                      <p className="font-semibold text-foreground tracking-tight">Branch Copilot</p>
                    </div>
                    <p className="text-muted-foreground leading-relaxed">{msg.text}</p>
                    {i === 0 && (
                      <>
                        <div className="p-4 bg-background rounded-lg border border-border/40 mt-4">
                          <span className="text-[10px] font-bold text-primary uppercase tracking-widest block mb-3 flex items-center">
                            <Cpu className="w-3 h-3 mr-1.5"/> Execution Reasoning
                          </span>
                          <div className="space-y-2 text-[13px]">
                            <div className="flex items-start">
                              <CornerDownRight className="w-4 h-4 mr-2 text-muted-foreground shrink-0 mt-0.5" /> 
                              <span><strong className="text-emerald-500 font-medium">Data Trigger:</strong> Sourced from 21-day hyper-local clinical script velocity.</span>
                            </div>
                            <div className="flex items-start">
                              <CornerDownRight className="w-4 h-4 mr-2 text-muted-foreground shrink-0 mt-0.5" /> 
                              <span><strong className="text-emerald-500 font-medium">Business Impact:</strong> Prevents ₹18,200 loss in immediately pending scripts.</span>
                            </div>
                          </div>
                        </div>
                        <div className="flex flex-wrap gap-2 mt-5">
                          <Button
                            size="sm"
                            variant="outline"
                            onClick={() => setMessages((prev) => [...prev, { sender: "bot", text: BOT_RESPONSES.transfer }])}
                            className="bg-background border-border/60 hover:bg-secondary text-xs"
                          >
                            Preview Routing Log
                          </Button>
                          <Button
                            size="sm"
                            disabled={dispatchDone}
                            onClick={handleAuthorize}
                            className="bg-foreground text-background shadow-md hover:bg-foreground/90 font-semibold text-xs"
                          >
                            {dispatchDone ? "Authorized ✓" : "Authorize Dispatch"}
                          </Button>
                        </div>
                      </>
                    )}
                  </div>
                ) : (
                  <div className="bg-primary text-primary-foreground rounded-2xl rounded-tr-sm px-4 py-3 text-sm max-w-[75%]">
                    {msg.text}
                  </div>
                )}
              </div>
            ))}

            <div className="flex flex-col items-end w-full space-y-3 pt-4">
              <span className="text-[10px] text-muted-foreground uppercase tracking-widest font-bold px-1">Contextual Actions</span>
              <div className="flex flex-wrap justify-end gap-2 max-w-[80%]">
                <Badge
                  variant="outline"
                  onClick={() => { setInputText("demand"); sendMessage(); }}
                  className="cursor-pointer hover:bg-secondary/80 py-1.5 px-3 bg-card shadow-sm border-border/40 transition-all font-medium text-muted-foreground hover:text-foreground"
                >
                  <BarChart3 className="w-3.5 h-3.5 mr-1.5 opacity-70"/> Render Demand Matrix
                </Badge>
                <Badge
                  variant="outline"
                  onClick={() => { setMessages((prev) => [...prev, { sender: "user", text: "Trace local margin loss" }, { sender: "bot", text: BOT_RESPONSES.margin }]); }}
                  className="cursor-pointer hover:bg-secondary/80 py-1.5 px-3 bg-card shadow-sm border-border/40 transition-all font-medium text-muted-foreground hover:text-foreground"
                >
                  Trace Local Margin Loss
                </Badge>
              </div>
            </div>
          </div>
          
          <div className="p-4 bg-background border-t border-border/30">
            <div className="relative flex items-center gap-2">
              <input
                type="text"
                value={inputText}
                onChange={(e) => setInputText(e.target.value)}
                onKeyDown={(e) => e.key === "Enter" && sendMessage()}
                className="w-full bg-secondary/30 border border-border/50 rounded-xl py-3.5 pl-4 pr-16 text-sm focus:outline-none focus:ring-1 focus:ring-primary focus:bg-background transition-colors placeholder:text-muted-foreground/60"
                placeholder="Ask the Copilot about stock, transfers, margins..."
              />
              <Button
                size="sm"
                onClick={sendMessage}
                className="absolute right-2 top-1/2 -translate-y-1/2 h-8 rounded-lg bg-foreground text-background shadow-sm px-3"
              >
                <Send className="w-3.5 h-3.5" />
              </Button>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
