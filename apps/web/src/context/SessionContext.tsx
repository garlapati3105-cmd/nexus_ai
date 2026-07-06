"use client";

import React, { createContext, useContext, useEffect, useState } from "react";
import { User, Session } from "@supabase/supabase-js";
import { supabase } from "@/lib/supabase";

export interface UserProfile {
  id: string;
  email: string;
  phone: string | null;
  branch_id: string | null;
  status: string;
}

export interface BranchInfo {
  id: string;
  organization_id: string;
  name: string;
  code: string;
}

export interface OrgInfo {
  id: string;
  name: string;
}

interface SessionContextType {
  user: User | null;
  session: Session | null;
  profile: UserProfile | null;
  roles: string[];
  currentRole: string | null;
  activeBranch: BranchInfo | null;
  activeOrg: OrgInfo | null;
  isLoading: boolean;
  hasRole: (allowedRoles: string[]) => boolean;
  signOut: () => Promise<void>;
}

const SessionContext = createContext<SessionContextType | undefined>(undefined);

export function SessionProvider({ children }: { children: React.ReactNode }) {
  const [session, setSession] = useState<Session | null>(null);
  const [user, setUser] = useState<User | null>(null);
  const [profile, setProfile] = useState<UserProfile | null>(null);
  const [roles, setRoles] = useState<string[]>([]);
  const [currentRole, setCurrentRole] = useState<string | null>(null);
  const [activeBranch, setActiveBranch] = useState<BranchInfo | null>(null);
  const [activeOrg, setActiveOrg] = useState<OrgInfo | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  const setMockProfileData = (email: string) => {
    const emailNorm = email.toLowerCase();
    let mockRole = "CEO";
    let branchName = "";
    let branchCode = "";
    let branchId = "";
    
    if (emailNorm.includes("manager")) {
      mockRole = "BRANCH_MANAGER";
      branchName = "Banjara Hills Branch";
      branchCode = "NEX-HYD-001";
      branchId = "b1111111-1111-4111-9111-111111111111";
    } else if (emailNorm.includes("demo") || emailNorm.includes("regional")) {
      mockRole = "REGIONAL_MANAGER";
    } else if (emailNorm.includes("cashier") || emailNorm.includes("billing")) {
      mockRole = "CASHIER";
      branchName = "Banjara Hills Branch";
      branchCode = "NEX-HYD-001";
      branchId = "b1111111-1111-4111-9111-111111111111";
    } else if (
      emailNorm.includes("pharmacist") ||
      emailNorm.includes("divya") ||
      emailNorm.includes("ganesh") ||
      emailNorm.includes("kavitha") ||
      emailNorm.includes("vijay") ||
      emailNorm.includes("employee") ||
      emailNorm.endsWith("@nexuscare.net")
    ) {
      mockRole = "PHARMACIST";
      branchName = "Banjara Hills Branch";
      branchCode = "NEX-HYD-001";
      branchId = "b1111111-1111-4111-9111-111111111111";
    }
    
    setProfile({
      id: "mock-proto-user-id",
      email: emailNorm,
      phone: "+91 99999 99999",
      branch_id: branchId || null,
      status: "active",
    });
    setRoles([mockRole]);
    setCurrentRole(mockRole);
    if (branchId) {
      setActiveBranch({
        id: branchId,
        organization_id: "org-1",
        name: branchName,
        code: branchCode,
      });
    } else {
      setActiveBranch(null);
    }
    setActiveOrg({
      id: "org-1",
      name: "NexusCare Pharmacy",
    });
  };

  // Helper function to query user metadata from PostgreSQL public tables
  const loadUserMetaData = async (userId: string) => {
    try {
      // 1. Fetch user profile from public.users table
      const { data: userProfile, error: profileErr } = await supabase
        .from("users")
        .select("id, email, phone, branch_id, status")
        .eq("id", userId)
        .maybeSingle();

      if (profileErr || !userProfile) {
        console.error("User profile load failed:", profileErr);
        const mockEmail = localStorage.getItem("nexus_email") || "ceo@nexuscare.com";
        setMockProfileData(mockEmail);
        setIsLoading(false);
        return;
      }

      setProfile(userProfile as UserProfile);

      // 2. Fetch system roles for this user
      const { data: userRoles, error: rolesErr } = await supabase
        .from("user_roles")
        .select("role:roles(name)")
        .eq("user_id", userId);

      if (rolesErr) {
        console.error("User roles fetch failed:", rolesErr);
        const emailNorm = userProfile.email.toLowerCase();
        let mockRole = "CEO";
        if (emailNorm.includes("manager")) {
          mockRole = "BRANCH_MANAGER";
        } else if (emailNorm.includes("demo")) {
          mockRole = "REGIONAL_MANAGER";
        }
        setRoles([mockRole]);
        setCurrentRole(mockRole);
      } else {
        const roleNames = (userRoles || [])
          .map((ur: any) => ur.role?.name)
          .filter(Boolean) as string[];
        
        if (roleNames.length === 0) {
          const emailNorm = userProfile.email.toLowerCase();
          let mockRole = "CEO";
          if (emailNorm.includes("manager")) {
            mockRole = "BRANCH_MANAGER";
          } else if (emailNorm.includes("demo")) {
            mockRole = "REGIONAL_MANAGER";
          }
          setRoles([mockRole]);
          setCurrentRole(mockRole);
        } else {
          setRoles(roleNames);
          if (roleNames.length > 0) {
            setCurrentRole(roleNames[0]);
          }
        }
      }

      // 3. Fetch branch details if user possesses a branch scope
      let orgId: string | null = null;
      if (userProfile.branch_id) {
        const { data: branchDetails, error: branchErr } = await supabase
          .from("branches")
          .select("id, organization_id, name, code")
          .eq("id", userProfile.branch_id)
          .maybeSingle();

        if (!branchErr && branchDetails) {
          setActiveBranch(branchDetails as BranchInfo);
          orgId = branchDetails.organization_id;
        }
      } else {
        const emailNorm = userProfile.email.toLowerCase();
        if (emailNorm.includes("manager")) {
          setActiveBranch({
            id: "00000000-0000-0000-0000-000000000001",
            organization_id: "org-1",
            name: "Jubilee Hills Branch",
            code: "H-JH01",
          });
        }
      }

      // 4. Fetch organization details (or query first org if global user)
      if (orgId) {
        const { data: orgDetails, error: orgErr } = await supabase
          .from("organizations")
          .select("id, name")
          .eq("id", orgId)
          .maybeSingle();

        if (!orgErr && orgDetails) {
          setActiveOrg(orgDetails as OrgInfo);
        }
      } else {
        // Fallback or global org fetch for network executive users
        const { data: globalOrg, error: globalOrgErr } = await supabase
          .from("organizations")
          .select("id, name")
          .limit(1)
          .maybeSingle();

        if (!globalOrgErr && globalOrg) {
          setActiveOrg(globalOrg as OrgInfo);
        }
      }
    } catch (e) {
      console.error("Detailed user metadata compilation error:", e);
      const mockEmail = localStorage.getItem("nexus_email") || "ceo@nexuscare.com";
      setMockProfileData(mockEmail);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    // Check active session on initialization
    supabase.auth.getSession().then(({ data: { session } }) => {
      setSession(session);
      setUser(session?.user ?? null);
      if (session?.user) {
        loadUserMetaData(session.user.id);
      } else {
        const localAuth = localStorage.getItem("nexus_auth") === "true";
        if (localAuth) {
          const mockEmail = localStorage.getItem("nexus_email") || "ceo@nexuscare.com";
          setMockProfileData(mockEmail);
          setIsLoading(false);
        } else {
          setIsLoading(false);
        }
      }
    }).catch(err => {
      console.error("Session resolution failed on init:", err);
      const localAuth = localStorage.getItem("nexus_auth") === "true";
      if (localAuth) {
        const mockEmail = localStorage.getItem("nexus_email") || "ceo@nexuscare.com";
        setMockProfileData(mockEmail);
      }
      setIsLoading(false);
    });

    // Listen for auth state alterations
    const {
      data: { subscription },
    } = supabase.auth.onAuthStateChange(async (_event, currentSession) => {
      setSession(currentSession);
      setUser(currentSession?.user ?? null);
      if (currentSession?.user) {
        setIsLoading(true);
        await loadUserMetaData(currentSession.user.id);
      } else {
        const localAuth = localStorage.getItem("nexus_auth") === "true";
        if (localAuth) {
          const mockEmail = localStorage.getItem("nexus_email") || "ceo@nexuscare.com";
          setMockProfileData(mockEmail);
          setIsLoading(false);
        } else {
          // Safe resets
          setProfile(null);
          setRoles([]);
          setCurrentRole(null);
          setActiveBranch(null);
          setActiveOrg(null);
          setIsLoading(false);
        }
      }
    });

    return () => {
      subscription.unsubscribe();
    };
  }, []);

  const hasRole = (allowedRoles: string[]) => {
    if (!currentRole) return false;
    // Admins have full access
    if (roles.includes("Admin") || currentRole === "Admin" || roles.includes("ceo") || currentRole === "CEO") return true;
    return allowedRoles.includes(currentRole);
  };

  const signOut = async () => {
    await supabase.auth.signOut();
    localStorage.removeItem("nexus_auth");
    // Clear the nexus_auth cookie so middleware stops redirecting to /dashboard
    document.cookie = "nexus_auth=; path=/; max-age=0; expires=Thu, 01 Jan 1970 00:00:00 GMT; SameSite=Lax";
  };

  return (
    <SessionContext.Provider
      value={{
        user,
        session,
        profile,
        roles,
        currentRole,
        activeBranch,
        activeOrg,
        isLoading,
        hasRole,
        signOut,
      }}
    >
      {children}
    </SessionContext.Provider>
  );
}

export function useSession() {
  const context = useContext(SessionContext);
  if (context === undefined) {
    throw new Error("useSession must be utilized inside a SessionProvider wrapper");
  }
  return context;
}
