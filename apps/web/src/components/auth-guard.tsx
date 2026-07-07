"use client";

import { useEffect, useState } from "react";
import { useSession } from "@/context/SessionContext";
import { BrainCircuit } from "lucide-react";

const LoadingSpinner = ({ label }: { label: string }) => (
  <div className="flex h-screen w-full items-center justify-center bg-background">
    <div className="flex flex-col items-center space-y-4">
      <div className="w-12 h-12 bg-primary rounded-xl flex items-center justify-center border border-primary/20 shadow-lg shadow-primary/20 animate-pulse">
        <BrainCircuit className="h-6 w-6 text-primary-foreground" />
      </div>
      <p className="text-sm font-semibold text-muted-foreground animate-pulse tracking-widest uppercase">{label}</p>
    </div>
  </div>
);

export function AuthGuard({ children }: { children: React.ReactNode }) {
  const { user, isLoading } = useSession();
  // Give auth extra 2s beyond SessionContext to avoid race conditions
  const [waitingForAuth, setWaitingForAuth] = useState(true);
  const [timeoutReached, setTimeoutReached] = useState(false);

  useEffect(() => {
    const timer = setTimeout(() => {
      setWaitingForAuth(false);
    }, 2000);
    return () => clearTimeout(timer);
  }, []);

  useEffect(() => {
    const timeoutTimer = setTimeout(() => {
      setTimeoutReached(true);
    }, 5000); // 5 seconds fail-safe timeout
    return () => clearTimeout(timeoutTimer);
  }, []);

  const hasLegacyAuth =
    typeof window !== "undefined" &&
    (!!localStorage.getItem("nexus_auth") || document.cookie.includes("nexus_auth="));
  const hasUserAuth = !!user;

  // Step 1: Show spinner while SessionContext is loading (unless timeout reached)
  if ((isLoading || waitingForAuth) && !timeoutReached) {
    return <LoadingSpinner label="Verifying Session..." />;
  }

  // Step 2: After load or timeout — check for valid auth
  if (!user && !hasLegacyAuth) {
    // Redirect to login (full reload to clear all state)
    if (typeof window !== "undefined") {
      setTimeout(() => { window.location.href = "/login"; }, 0);
    }
    return <LoadingSpinner label="Redirecting to Login..." />;
  }

  return <>{children}</>;
}
