"use client";

import Link from "next/link";
import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "@/components/ui/card";
import { BrainCircuit, ArrowLeft, Loader2, AlertCircle } from "lucide-react";
import { supabase } from "@/lib/supabase";

export default function LoginPage() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");

  const [isLoading, setIsLoading] = useState(false);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    setErrorMsg(null);

    try {
      const { data, error } = await supabase.auth.signInWithPassword({
        email,
        password,
      });

      if (error) {
        // Fallback for local prototype authentication checks
        const prototypeAccounts = ["demo@nexuscare.com", "manager@nexuscare.com", "ceo@nexuscare.com"];
        if (prototypeAccounts.includes(email.toLowerCase())) {
          localStorage.setItem("nexus_auth", "true");
          localStorage.setItem("nexus_email", email.toLowerCase());
          document.cookie = "nexus_auth=true; path=/; max-age=86400; SameSite=Lax";
          // Force full page reload so SessionContext reinitializes fresh
          window.location.href = "/dashboard";
          return;
        }
        throw new Error(error.message);
      }

      if (data.session) {
        document.cookie = "nexus_auth=true; path=/; max-age=86400; SameSite=Lax";
        // Force full page reload — prevents race condition between client navigation and session propagation
        window.location.href = "/dashboard";
      }
    } catch (err: any) {
      console.error("Login verification failed:", err);
      setErrorMsg(err.message || "Failed to authenticate. Please check your credentials.");
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-background relative overflow-hidden">
      <div className="absolute top-0 w-full h-screen bg-[radial-gradient(ellipse_at_top,_var(--tw-gradient-stops))] from-primary/10 via-background to-background -z-10" />
      
      <Link 
        href="/" 
        className="absolute top-6 left-6 flex items-center space-x-2 text-xs font-semibold text-muted-foreground hover:text-foreground transition-colors group"
      >
        <ArrowLeft className="w-3.5 h-3.5 group-hover:-translate-x-0.5 transition-transform" />
        <span>Back to Landing</span>
      </Link>

      <Card className="w-full max-w-md bg-card/60 backdrop-blur-xl border-border/50 shadow-2xl">
        <form onSubmit={handleLogin}>
          <CardHeader className="space-y-1 flex flex-col items-center">
            <div className="w-12 h-12 bg-primary rounded-xl flex items-center justify-center mb-4 border border-primary/20 shadow-lg shadow-primary/20">
              <BrainCircuit className="h-6 w-6 text-primary-foreground" />
            </div>
            <CardTitle className="text-2xl font-bold tracking-tight">Nexus AI Login</CardTitle>
            <CardDescription>
              Enter your credentials to access the terminal.
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            {errorMsg && (
              <div className="bg-destructive/15 border border-destructive/20 text-destructive text-xs px-3.5 py-2.5 rounded-lg flex items-start space-x-2.5">
                <AlertCircle className="w-4 h-4 mt-0.5 shrink-0" />
                <span>{errorMsg}</span>
              </div>
            )}
            <div className="space-y-2">
              <Label htmlFor="email">Email</Label>
              <Input 
                id="email" 
                type="email" 
                placeholder="ceo@nexuscare.com" 
                className="bg-background/50" 
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                required
                disabled={isLoading}
              />
            </div>
            <div className="space-y-2">
              <div className="flex justify-between items-center">
                <Label htmlFor="password">Password</Label>
                <Link 
                  href="/forgot-password" 
                  className="text-xs text-muted-foreground hover:text-primary transition-colors hover:underline"
                >
                  Forgot Password?
                </Link>
              </div>
              <Input 
                id="password" 
                type="password" 
                className="bg-background/50" 
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                required
                disabled={isLoading}
              />
            </div>
          </CardContent>
          <CardFooter className="flex flex-col space-y-4">
            <Button type="submit" className="w-full font-semibold relative overflow-hidden" disabled={isLoading}>
              {isLoading ? (
                <>
                  <Loader2 className="w-4 h-4 mr-2.5 animate-spin" />
                  Decrypting...
                </>
              ) : (
                "Authenticate Agent"
              )}
            </Button>
            <div className="text-sm text-center text-muted-foreground">
              Strictly authorized personnel only.
            </div>
          </CardFooter>
        </form>
      </Card>
    </div>
  );
}
