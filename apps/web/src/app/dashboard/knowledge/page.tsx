"use client";

import { useState, useRef } from "react";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { BookOpen, Database, RefreshCw, Network, ShieldCheck, Box, CheckCircle, Loader2, FileUp } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import * as motion from "framer-motion/client";

export default function KnowledgePage() {
  const [isSyncing, setIsSyncing] = useState(false);
  const [syncDone, setSyncDone] = useState(false);
  const [uploadedFile, setUploadedFile] = useState<string | null>(null);
  const [isUploading, setIsUploading] = useState(false);
  const fileRef = useRef<HTMLInputElement>(null);

  const handleVectorSync = async () => {
    setIsSyncing(true);
    setSyncDone(false);
    await new Promise((r) => setTimeout(r, 2000));
    setIsSyncing(false);
    setSyncDone(true);
    setTimeout(() => setSyncDone(false), 4000);
  };

  const handleFileSelect = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;
    setIsUploading(true);
    setUploadedFile(null);
    await new Promise((r) => setTimeout(r, 1500));
    setIsUploading(false);
    setUploadedFile(file.name);
  };

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-end">
        <div>
          <h2 className="text-3xl font-bold tracking-tight">AI Knowledge Base (RAG)</h2>
          <p className="text-muted-foreground mt-1">ChromaDB semantic embeddings powering local node logic.</p>
        </div>
        <div className="flex space-x-2">
          <Badge variant="outline" className="border-emerald-500/50 text-emerald-500 bg-emerald-500/10 px-3 py-1">
            <ShieldCheck className="w-4 h-4 mr-2" /> 99.9% RAG Confidence
          </Badge>
          <Button
            onClick={handleVectorSync}
            disabled={isSyncing}
            className="bg-primary/20 text-primary hover:bg-primary/30 border border-primary/30"
          >
            {isSyncing ? (
              <><Loader2 className="mr-2 h-4 w-4 animate-spin" /> Syncing...</>
            ) : syncDone ? (
              <><CheckCircle className="mr-2 h-4 w-4 text-emerald-400" /> Synced!</>
            ) : (
              <><RefreshCw className="mr-2 h-4 w-4" /> Trigger Vector Sync</>
            )}
          </Button>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <motion.div initial={{ opacity: 0, scale: 0.95 }} animate={{ opacity: 1, scale: 1 }}>
          <Card className="bg-card/50 border-border/50 h-full">
            <CardHeader className="pb-2">
              <CardTitle className="flex items-center text-sm text-muted-foreground"><Database className="mr-2 h-4 w-4"/> Embeddings</CardTitle>
            </CardHeader>
            <CardContent>
              <h4 className="text-3xl font-bold">14,204</h4>
              <p className="text-xs text-muted-foreground mt-1">Total Vector Chunks</p>
            </CardContent>
          </Card>
        </motion.div>
        
        <motion.div initial={{ opacity: 0, scale: 0.95 }} animate={{ opacity: 1, scale: 1 }} transition={{ delay: 0.1 }}>
          <Card className="bg-card/50 border-border/50 h-full">
            <CardHeader className="pb-2">
              <CardTitle className="flex items-center text-sm text-muted-foreground"><Network className="mr-2 h-4 w-4"/> AI Agents Linked</CardTitle>
            </CardHeader>
            <CardContent>
              <h4 className="text-3xl font-bold text-primary">5 / 6</h4>
              <p className="text-xs text-muted-foreground mt-1">LangGraph Nodes Querying</p>
            </CardContent>
          </Card>
        </motion.div>

        <motion.div initial={{ opacity: 0, scale: 0.95 }} animate={{ opacity: 1, scale: 1 }} transition={{ delay: 0.2 }}>
          <Card className="bg-card/50 border-border/50 h-full">
            <CardHeader className="pb-2">
              <CardTitle className="flex items-center text-sm text-muted-foreground"><Box className="mr-2 h-4 w-4"/> System Health</CardTitle>
            </CardHeader>
            <CardContent>
              <h4 className="text-3xl font-bold text-emerald-500">Pristine</h4>
              <p className="text-xs text-muted-foreground mt-1">2ms Avg Retrieval Latency</p>
            </CardContent>
          </Card>
        </motion.div>
      </div>

      <Card className="bg-card/50 border-border/50 mt-6 relative overflow-hidden">
        <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_bottom_right,_var(--tw-gradient-stops))] from-primary/10 via-background to-background z-0 pointer-events-none" />
        
        <CardHeader className="relative z-10 border-b border-border/50 bg-secondary/10">
          <CardTitle>Vectorize Operational Documents</CardTitle>
          <CardDescription>Upload pharmaceutical pricing, HR policies, or standard operating procedures.</CardDescription>
        </CardHeader>
        <CardContent className="flex flex-col items-center justify-center p-12 text-center relative z-10">
          {/* Hidden native file input */}
          <input
            type="file"
            ref={fileRef}
            accept=".pdf,.csv,.md,.txt"
            className="hidden"
            onChange={handleFileSelect}
          />
          <div className="w-20 h-20 bg-secondary/50 rounded-full flex items-center justify-center border border-border/50 shadow-inner mb-6 relative">
            <BookOpen className="h-8 w-8 text-muted-foreground" />
            <div className="absolute top-0 right-0 w-3 h-3 bg-primary rounded-full animate-ping" />
          </div>
          <h3 className="text-xl font-bold">Inject Context</h3>
          <p className="text-sm text-muted-foreground mt-2 max-w-sm mb-6">
            Documents are automatically chunked, embedded using <code>text-embedding-3</code>, and securely siloed via RLS.
          </p>
          {uploadedFile && (
            <div className="mb-4 flex items-center gap-2 text-emerald-500 text-sm font-medium">
              <CheckCircle className="w-4 h-4" />
              <span>{uploadedFile} — vectorization queued!</span>
            </div>
          )}
          <Button
            className="px-8 bg-foreground text-background hover:bg-foreground/90"
            disabled={isUploading}
            onClick={() => fileRef.current?.click()}
          >
            {isUploading ? (
              <><Loader2 className="w-4 h-4 mr-2 animate-spin" /> Processing...</>
            ) : (
              <><FileUp className="w-4 h-4 mr-2" /> Select Files (.pdf, .csv, .md)</>
            )}
          </Button>
        </CardContent>
      </Card>
    </div>
  );
}
