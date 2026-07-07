"use client";

import { useState } from "react";
import { Sidebar } from "@/components/layout/sidebar";
import { Topbar } from "@/components/layout/topbar";
import { AuthGuard } from "@/components/auth-guard";

export default function DashboardLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const [isSidebarOpen, setIsSidebarOpen] = useState(false);

  return (
    <AuthGuard>
      <div className="flex h-screen bg-background overflow-hidden relative">
        {/* Desktop Sidebar */}
        <div className="hidden lg:block shrink-0 border-r border-border/40">
          <Sidebar />
        </div>

        <div className="flex-1 flex flex-col h-screen overflow-hidden w-full">
          <Topbar onMenuToggle={() => setIsSidebarOpen(true)} />
          <main className="flex-1 overflow-y-auto p-4 md:p-6 scroll-smooth">
            {children}
          </main>
        </div>

        {/* Mobile Sidebar overlay */}
        {isSidebarOpen && (
          <div className="fixed inset-0 z-50 flex lg:hidden">
            {/* Backdrop */}
            <div 
              className="fixed inset-0 bg-background/80 backdrop-blur-sm"
              onClick={() => setIsSidebarOpen(false)}
            />
            {/* Drawer */}
            <div className="relative flex w-[260px] max-w-xs flex-col bg-background border-r border-border/40 h-full p-4 z-50 animate-in slide-in-from-left duration-200">
              {/* Close button inside Drawer */}
              <button 
                onClick={() => setIsSidebarOpen(false)}
                className="absolute top-4 right-4 p-1.5 rounded-md text-muted-foreground hover:bg-secondary/60 hover:text-foreground transition-colors"
              >
                <span className="sr-only">Close sidebar</span>
                <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
              
              {/* Sidebar Content */}
              <div className="h-full mt-8" onClick={() => setIsSidebarOpen(false)}>
                <Sidebar />
              </div>
            </div>
          </div>
        )}
      </div>
    </AuthGuard>
  );
}
