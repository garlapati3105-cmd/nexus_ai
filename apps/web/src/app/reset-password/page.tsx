"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "@/components/ui/card";
import { BrainCircuit, ArrowLeft, Loader2, CheckCircle2 } from "lucide-react";
import { supabase } from "@/lib/supabase";

export default function ResetPasswordPage() {
  const router = useRouter();
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);
  const [isSuccess, setIsSuccess] = useState(false);

  const handlePasswordUpdate = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    setErrorMsg(null);

    if (password !== confirmPassword) {
      setErrorMsg("Passwords do not match.");
      setIsLoading(false);
      return;
    }

    try {
      const { error } = await supabase.auth.updateUser({
        password: password,
      });

      if (error) throw error;
      setIsSuccess(true);
    } catch (err: any) {
      console.error("Password update error:", err);
      setErrorMsg(err.message || "Failed to update password.");
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-background relative overflow-hidden">
      <div className="absolute top-0 w-full h-screen bg-[radial-gradient(ellipse_at_top,_var(--tw-gradient-stops))] from-primary/10 via-background to-background -z-10" />
      
      <Link 
        href="/login" 
        className="absolute top-6 left-6 flex items-center space-x-2 text-xs font-semibold text-muted-foreground hover:text-foreground transition-colors group"
      >
        <ArrowLeft className="w-3.5 h-3.5 group-hover:-translate-x-0.5 transition-transform" />
        <span>Return to Login</span>
      </Link>

      <Card className="w-full max-w-md bg-card/60 backdrop-blur-xl border-border/50 shadow-2xl">
        {isSuccess ? (
          <div className="p-8 flex flex-col items-center text-center space-y-4">
            <div className="w-12 h-12 bg-primary/10 border border-primary/20 text-primary rounded-xl flex items-center justify-center shadow-lg shadow-primary/5">
              <CheckCircle2 className="h-6 w-6" />
            </div>
            <CardTitle className="text-xl font-bold tracking-tight">Decryption Keys Reset</CardTitle>
            <CardDescription className="text-sm">
              Your password has been updated. You may now retrieve access utilizing the updated credentials.
            </CardDescription>
            <Button className="w-full mt-4" onClick={() => (window.location.href = "/login")}>
              Re-Authenticate
            </Button>
          </div>
        ) : (
          <form onSubmit={handlePasswordUpdate}>
            <CardHeader className="space-y-1 flex flex-col items-center">
              <div className="w-12 h-12 bg-primary rounded-xl flex items-center justify-center mb-4 border border-primary/20 shadow-lg shadow-primary/20">
                <BrainCircuit className="h-6 w-6 text-primary-foreground" />
              </div>
              <CardTitle className="text-2xl font-bold tracking-tight">Reset Password</CardTitle>
              <CardDescription>
                Provide your new secure terminal decryption keys.
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              {errorMsg && (
                <div className="bg-destructive/15 border border-destructive/20 text-destructive text-xs px-3.5 py-2.5 rounded-lg flex items-start space-x-2.5">
                  <span>{errorMsg}</span>
                </div>
              )}
              <div className="space-y-2">
                <Label htmlFor="password">New Password</Label>
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
              <div className="space-y-2">
                <Label htmlFor="confirm-password">Confirm Password</Label>
                <Input 
                  id="confirm-password" 
                  type="password" 
                  className="bg-background/50" 
                  value={confirmPassword}
                  onChange={(e) => setConfirmPassword(e.target.value)}
                  required
                  disabled={isLoading}
                />
              </div>
            </CardContent>
            <CardFooter>
              <Button type="submit" className="w-full font-semibold" disabled={isLoading}>
                {isLoading ? (
                  <>
                    <Loader2 className="w-4 h-4 mr-2.5 animate-spin" />
                    Resetting...
                  </>
                ) : (
                  "Update Verification Password"
                )}
              </Button>
            </CardFooter>
          </form>
        )}
      </Card>
    </div>
  );
}
