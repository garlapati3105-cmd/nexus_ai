"use client";

import { useRouter } from "next/navigation";
import { Button } from "@/components/ui/button";
import { ShieldAlert, ArrowLeft } from "lucide-react";

export default function UnauthorizedPage() {
  const router = useRouter();

  return (
    <div className="min-h-screen flex items-center justify-center bg-background relative overflow-hidden">
      <div className="absolute top-0 w-full h-screen bg-[radial-gradient(ellipse_at_top,_var(--tw-gradient-stops))] from-destructive/10 via-background to-background -z-10" />
      
      <div className="text-center space-y-6 max-w-md p-6">
        <div className="inline-flex w-16 h-16 bg-destructive/10 border border-destructive/20 text-destructive rounded-full items-center justify-center mb-2 shadow-lg shadow-destructive/5">
          <ShieldAlert className="w-8 h-8 animate-pulse" />
        </div>
        
        <div className="space-y-2">
          <h1 className="text-3xl font-extrabold tracking-tight bg-clip-text text-transparent bg-gradient-to-r from-foreground to-foreground/70">
            Access Restricted
          </h1>
          <p className="text-muted-foreground text-sm leading-relaxed">
            Your current decrypted access token does not possess authorization to view this terminal node. Access is strictly logged and audited.
          </p>
        </div>

        <div className="pt-4 flex flex-col sm:flex-row justify-center items-center gap-3">
          <Button 
            variant="outline" 
            className="w-full sm:w-auto flex items-center justify-center space-x-2"
            onClick={() => router.push("/dashboard")}
          >
            <ArrowLeft className="w-4 h-4 shrink-0" />
            <span>Back to Dashboard</span>
          </Button>
          <Button 
            className="w-full sm:w-auto flex items-center justify-center"
            onClick={() => router.push("/login")}
          >
            Re-Authenticate Account
          </Button>
        </div>
      </div>
    </div>
  );
}
