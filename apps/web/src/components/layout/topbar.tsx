import React, { useState } from "react";
import { useSession } from "@/context/SessionContext";
import { Bell, Search, Hexagon, Command, Sparkles, X, Send, Bot } from "lucide-react";
import { Button } from "@/components/ui/button";
import { motion, AnimatePresence } from "framer-motion";

export function Topbar() {
  const { profile, currentRole, activeBranch } = useSession();
  const [isCopilotOpen, setIsCopilotOpen] = useState(false);
  const [prompt, setPrompt] = useState("");
  const [messages, setMessages] = useState<Array<{ sender: "user" | "bot"; text: string }>>([
    { sender: "bot", text: "Hello! I am your Nexus AI copilot. How can I help optimize your network operations today?" }
  ]);

  // Construct dynamic name and scope representations
  const displayName = profile?.email
    ? profile.email
        .split("@")[0]
        .split(".")
        .map((part) => part.charAt(0).toUpperCase() + part.slice(1))
        .join(" ")
    : "System Agent";

  const displayRole = `${currentRole || "Guest"}${
    activeBranch ? ` - ${activeBranch.name}` : " (Global)"
  }`;

  const handleSendMessage = () => {
    if (!prompt.trim()) return;
    const userMsg = prompt;
    setMessages((prev) => [...prev, { sender: "user", text: userMsg }]);
    setPrompt("");

    // Simulate smart AI domain reasoning based on keyword matches
    setTimeout(() => {
      let botText = "I resolve medicine telemetry, stock check metrics, and price margins. Ask me about 'stock', 'saved', or 'orchestrator'!";
      const q = userMsg.toLowerCase();
      if (q.includes("stock") || q.includes("transfer")) {
        botText = "Stockout detectors scan nearest branches (e.g. Banjara Hills -> Jubilee Hills) and generate inter-branch transfer proposals to avoid logistics waste.";
      } else if (q.includes("save") || q.includes("saving") || q.includes("money")) {
        botText = "Currently, simulated margins optimize daily sales, providing up to ₹7,420.50 ($7.4k) baseline savings via FEFO batch selection.";
      } else if (q.includes("orchestrator") || q.includes("langgraph")) {
        botText = "The LangGraph Orchestrator routes customer checkout events statefully through Sales AI, Inventory check node, Finance auditor, and manager approvals.";
      } else if (q.includes("grok") || q.includes("llm")) {
        botText = "xAI Grok executes reasoning validations with average confidence rates above 98.4%.";
      }
      setMessages((prev) => [...prev, { sender: "bot", text: botText }]);
    }, 1000);
  };

  return (
    <>
      <div className="h-14 border-b border-border/40 bg-background/80 backdrop-blur-md flex justify-between items-center px-6 sticky top-0 z-50">
        <div className="flex items-center w-full max-w-md">
          {/* Vercel-style Command Palette Trigger */}
          <button className="flex items-center justify-between w-full h-9 px-3 bg-secondary/30 hover:bg-secondary/50 border border-border/50 rounded-md transition-colors text-sm text-muted-foreground group">
            <div className="flex items-center space-x-2">
              <Search className="h-4 w-4 opacity-50 group-hover:opacity-100 transition-opacity" />
              <span className="font-medium">Search or jump to...</span>
            </div>
            <div className="flex items-center space-x-1">
              <kbd className="bg-background border border-border/40 px-1.5 py-0.5 rounded text-[10px] font-mono shadow-sm">⌘</kbd>
              <kbd className="bg-background border border-border/40 px-1.5 py-0.5 rounded text-[10px] font-mono shadow-sm">K</kbd>
            </div>
          </button>
        </div>
        
        <div className="flex items-center space-x-4">
          <Button variant="ghost" size="icon" className="relative text-muted-foreground hover:bg-secondary/50 h-8 w-8 rounded-full">
            <Bell className="h-4 w-4" />
            <span className="absolute top-1.5 right-1.5 h-1.5 w-1.5 bg-destructive rounded-full shadow-[0_0_5px_rgba(239,68,68,0.5)]" />
          </Button>
          <div className="h-4 w-px bg-border/50 mx-1" />
          <div className="flex items-center space-x-3 cursor-pointer group">
            <div className="text-right hidden md:block">
              <p className="text-sm font-semibold leading-none group-hover:text-primary transition-colors tracking-tight">{displayName}</p>
              <p className="text-[10px] uppercase tracking-wider text-muted-foreground mt-1">{displayRole}</p>
            </div>
            <div className="h-8 w-8 bg-gradient-to-tr from-primary/30 to-primary/5 rounded-full flex items-center justify-center border border-primary/20 shadow-sm transition-transform group-hover:scale-105">
              <Hexagon className="h-4 w-4 text-primary fill-primary/10" />
            </div>
          </div>
        </div>
      </div>

      {/* Floating Copilot Dialog Panel */}
      <AnimatePresence>
        {isCopilotOpen && (
          <motion.div
            initial={{ opacity: 0, y: 50, scale: 0.95 }}
            animate={{ opacity: 1, y: 0, scale: 1 }}
            exit={{ opacity: 0, y: 30, scale: 0.95 }}
            transition={{ type: "spring", damping: 25, stiffness: 200 }}
            className="fixed bottom-24 right-6 w-96 max-w-[90vw] h-[480px] bg-slate-950/95 backdrop-blur-lg border border-slate-800 rounded-2xl shadow-2xl flex flex-col z-50 overflow-hidden"
          >
            {/* Header banner */}
            <div className="p-4 border-b border-slate-800 bg-slate-900/50 flex justify-between items-center bg-gradient-to-r from-slate-900/50 to-indigo-950/20">
              <div className="flex items-center space-x-2">
                <div className="p-1.5 bg-indigo-500/10 rounded-lg border border-indigo-500/30 text-indigo-400">
                  <Bot className="w-5 h-5 animate-pulse" />
                </div>
                <div>
                  <h3 className="font-bold text-sm text-slate-200 flex items-center">
                    Nexus Copilot 
                    <span className="ml-2 text-[9px] font-bold uppercase tracking-wider rounded border border-emerald-500/50 text-emerald-400 bg-emerald-500/5 px-1 py-0.5 leading-none">
                      Active
                    </span>
                  </h3>
                  <p className="text-[10px] text-slate-400">AI Operating Kernel Companion</p>
                </div>
              </div>
              <button 
                onClick={() => setIsCopilotOpen(false)}
                className="p-1 hover:bg-slate-800 rounded-lg text-slate-400 transition"
              >
                <X className="w-4 h-4" />
              </button>
            </div>

            {/* Chat Messages */}
            <div className="flex-1 p-4 overflow-y-auto space-y-3 font-sans">
              {messages.map((msg, i) => (
                <div 
                  key={i} 
                  className={`flex ${msg.sender === "user" ? "justify-end" : "justify-start"}`}
                >
                  <div className={`max-w-[80%] rounded-xl p-3 text-xs leading-relaxed ${
                    msg.sender === "user" 
                      ? "bg-indigo-600 text-white rounded-tr-none" 
                      : "bg-slate-900 border border-slate-800/80 text-slate-300 rounded-tl-none"
                  }`}>
                    {msg.text}
                  </div>
                </div>
              ))}
            </div>

            {/* Bottom Actions input */}
            <div className="p-3 border-t border-slate-800/80 bg-slate-900/10 flex gap-2">
              <input
                type="text"
                placeholder="Ask about stock, savings, langgraph..."
                value={prompt}
                onChange={(e) => setPrompt(e.target.value)}
                onKeyDown={(e) => e.key === "Enter" && handleSendMessage()}
                className="flex-1 bg-slate-900 border border-slate-850 rounded-lg px-3 py-1.5 text-xs text-slate-300 placeholder-slate-500 focus:outline-none focus:border-indigo-500/60"
              />
              <button 
                onClick={handleSendMessage}
                className="p-2 bg-indigo-600 hover:bg-indigo-500 text-white rounded-lg transition active:scale-95"
              >
                <Send className="w-3.5 h-3.5" />
              </button>
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Floating Nexus AI Command Button */}
      <div className="fixed bottom-6 right-6 z-50">
        <button 
          onClick={() => setIsCopilotOpen(!isCopilotOpen)}
          className="group flex items-center space-x-2 bg-foreground text-background px-4 py-3 rounded-full shadow-2xl hover:scale-105 active:scale-95 transition-all outline-none border border-border/20"
        >
          <div className="relative">
            <Sparkles className="w-4 h-4 text-background" />
            <div className="absolute inset-0 bg-primary rounded-full blur-md opacity-40 group-hover:opacity-80 transition-opacity animate-pulse" />
          </div>
          <span className="font-semibold tracking-tight text-sm">Nexus AI</span>
          <Command className="w-3 h-3 ml-1 opacity-50 hidden md:block" />
        </button>
      </div>
    </>
  );
}
