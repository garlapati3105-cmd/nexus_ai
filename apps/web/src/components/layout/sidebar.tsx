"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { useSession } from "@/context/SessionContext";
import {
  LayoutDashboard,
  Building2,
  Package,
  Pill,
  LineChart,
  BrainCircuit,
  BookOpen,
  Settings,
  ShoppingCart,
  CheckSquare,
  LogOut
} from "lucide-react";

export function Sidebar() {
  const { currentRole, signOut } = useSession();
  const pathname = usePathname();


  const allRoutes = [
    { label: "CEO Dashboard", icon: LayoutDashboard, href: "/dashboard", roles: ["CEO", "ADMIN"] },
    { label: "POS Billing", icon: ShoppingCart, href: "/dashboard/cashier", roles: ["CASHIER", "ADMIN"] },
    { label: "Dispensation Queue", icon: Pill, href: "/dashboard/pharmacist", roles: ["PHARMACIST", "ADMIN"] },
    { label: "Approvals", icon: CheckSquare, href: "/dashboard/approvals", actionRequired: true, roles: ["CEO", "ADMIN", "REGIONAL_MANAGER"] },
    { label: "AI Command Center", icon: BrainCircuit, href: "/dashboard/ai-command-center", roles: ["CEO", "ADMIN", "REGIONAL_MANAGER"] },
    { label: "Branch Operations", icon: Building2, href: "/dashboard/branch", roles: ["CEO", "ADMIN", "REGIONAL_MANAGER"] },
    { label: "Orders", icon: ShoppingCart, href: "/dashboard/orders", roles: ["CEO", "ADMIN", "BRANCH_MANAGER", "PHARMACIST"] },
    { label: "Global Inventory", icon: Package, href: "/dashboard/inventory", roles: ["CEO", "ADMIN", "REGIONAL_MANAGER", "BRANCH_MANAGER", "INVENTORY"] },
    { label: "Medicine Intelligence", icon: Pill, href: "/dashboard/medicines", roles: ["CEO", "ADMIN", "BRANCH_MANAGER", "PHARMACIST", "INVENTORY"] },
    { label: "Finance & Margin", icon: LineChart, href: "/dashboard/finance", roles: ["CEO", "ADMIN", "FINANCE"] },
    { label: "Predictive Analytics", icon: LineChart, href: "/dashboard/analytics", roles: ["CEO", "ADMIN", "REGIONAL_MANAGER"] },
    { label: "Knowledge Center", icon: BookOpen, href: "/dashboard/knowledge", roles: ["CEO", "ADMIN", "REGIONAL_MANAGER", "BRANCH_MANAGER", "PHARMACIST", "INVENTORY"] },
    { label: "Customers", icon: Building2, href: "/dashboard/customers", roles: ["BRANCH_MANAGER"] },
    { label: "Employees", icon: Building2, href: "/dashboard/employees", roles: ["BRANCH_MANAGER"] },
  ];

  // Filter routes based on active role
  const visibleRoutes = allRoutes.filter((route) => {
    if (!currentRole) return false;
    const roleNormalized = currentRole.toUpperCase();
    if (roleNormalized === "ADMIN") return true;
    return route.roles.includes(roleNormalized);
  });

  return (
    <div className="flex flex-col h-full bg-background border-r border-border/40 w-[260px] p-4 z-20 transition-all">
      <div className="flex items-center space-x-3 px-3 py-4 mb-4">
        <div className="relative flex items-center justify-center">
          <div className="h-7 w-7 bg-primary rounded-md flex items-center justify-center relative z-10 shadow-md border border-primary/20">
            <BrainCircuit className="text-primary-foreground h-4 w-4" />
          </div>
          <div className="absolute inset-0 bg-primary rounded-md animate-ping opacity-20 z-0" style={{ animationDuration: '3s' }} />
        </div>
        <span className="font-bold text-lg tracking-tight bg-clip-text text-transparent bg-gradient-to-r from-foreground to-foreground/70">
          Nexus AI
        </span>
      </div>

      <div className="flex-1 space-y-0.5 mt-2">
        {visibleRoutes.map((route) => {
          const isActive =
            route.href === "/dashboard"
              ? pathname === "/dashboard"
              : pathname.startsWith(route.href);
          return (
            <Link
              key={route.href}
              href={route.href}
              className={`flex items-center justify-between px-3 py-2 rounded-md text-sm transition-all group active:scale-[0.98] ${
                isActive
                  ? "bg-primary/10 text-primary font-semibold"
                  : "text-muted-foreground hover:bg-secondary/60 hover:text-foreground"
              }`}
            >
              <div className="flex items-center space-x-3">
                <route.icon className={`h-4 w-4 transition-colors ${isActive ? "text-primary" : "text-muted-foreground/70 group-hover:text-primary"}`} />
                <span className="font-medium tracking-tight drop-shadow-sm">{route.label}</span>
              </div>
              {route.actionRequired && (
                <span className="flex h-5 w-5 items-center justify-center rounded-full bg-primary text-[10px] font-bold text-primary-foreground shadow-[0_0_10px_rgba(59,130,246,0.3)] animate-pulse">
                  2
                </span>
              )}
            </Link>
          );
        })}
      </div>

      <div className="pt-4 border-t border-border/40 space-y-1">
        <Link
          href="/dashboard/settings"
          className="flex items-center space-x-3 px-3 py-2 rounded-md text-sm text-muted-foreground hover:bg-secondary/60 hover:text-foreground transition-colors group active:scale-[0.98]"
        >
          <Settings className="h-4 w-4 text-muted-foreground/70 group-hover:text-foreground transition-colors" />
          <span className="font-medium tracking-tight">Settings</span>
        </Link>
        <button
          onClick={async () => {
            await signOut();
            window.location.href = "/login";
          }}
          className="w-full flex items-center space-x-3 px-3 py-2 rounded-md text-sm text-muted-foreground hover:bg-destructive/10 hover:text-destructive transition-colors group active:scale-[0.98]"
        >
          <LogOut className="h-4 w-4 text-muted-foreground/70 group-hover:text-destructive transition-colors" />
          <span className="font-medium tracking-tight">Logout</span>
        </button>
      </div>
    </div>
  );
}
