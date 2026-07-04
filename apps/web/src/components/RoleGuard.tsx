"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";
import { useSession } from "@/context/SessionContext";

interface RoleGuardProps {
  allowedRoles: string[];
  children: React.ReactNode;
}

export function RoleGuard({ allowedRoles, children }: RoleGuardProps) {
  const router = useRouter();
  const { hasRole, isLoading, user } = useSession();

  useEffect(() => {
    if (!isLoading) {
      if (!user) {
        router.push("/login");
      } else if (!hasRole(allowedRoles)) {
        router.push("/unauthorized");
      }
    }
  }, [isLoading, user, hasRole, allowedRoles, router]);

  if (isLoading) {
    return null;
  }

  if (!user || !hasRole(allowedRoles)) {
    return null;
  }

  return <>{children}</>;
}
