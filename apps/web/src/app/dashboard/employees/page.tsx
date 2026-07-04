"use client";

import { useSession } from "@/context/SessionContext";
import { UserCheck, Shield, Clock, Plus } from "lucide-react";
import { Button } from "@/components/ui/button";

export default function EmployeesPage() {
  const { currentRole, activeBranch } = useSession();

  const mockEmployees = [
    { id: 1, name: "Karan Johar", role: "Pharmacist", shift: "Morning (08:00 - 16:00)", status: "On Duty" },
    { id: 2, name: "Anil Kapoor", role: "Cashier / clerk", shift: "General (10:00 - 18:00)", status: "On Duty" },
    { id: 3, name: "Juhi Chawla", role: "Inventory Lead", shift: "Evening (14:00 - 22:00)", status: "Scheduled" },
    { id: 4, name: "Farhan Akhtar", role: "Delivery Assistant", shift: "Holiday", status: "Off Duty" },
  ];

  return (
    <div className="p-6 space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-bold tracking-tight">Branch Roster & Staff</h1>
          <p className="text-sm text-muted-foreground mt-1">
            Manage attendance and shifts active for {activeBranch?.name || "Hyderabad Main Branch"}
          </p>
        </div>
        <Button className="flex items-center space-x-2">
          <Plus className="w-4 h-4" />
          <span>Add Employee</span>
        </Button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="bg-card border border-border/40 p-4 rounded-xl flex items-center space-x-4">
          <div className="p-3 bg-emerald-500/10 text-emerald-400 rounded-lg">
            <UserCheck className="w-6 h-6" />
          </div>
          <div>
            <p className="text-2xl font-bold">2 / 4</p>
            <p className="text-xs text-muted-foreground">On Duty Currently</p>
          </div>
        </div>
        <div className="bg-card border border-border/40 p-4 rounded-xl flex items-center space-x-4">
          <div className="p-3 bg-indigo-500/10 text-indigo-400 rounded-lg">
            <Shield className="w-6 h-6" />
          </div>
          <div>
            <p className="text-2xl font-bold">1</p>
            <p className="text-xs text-muted-foreground">Manager In-Charge</p>
          </div>
        </div>
        <div className="bg-card border border-border/40 p-4 rounded-xl flex items-center space-x-4">
          <div className="p-3 bg-amber-500/10 text-amber-400 rounded-lg">
            <Clock className="w-6 h-6" />
          </div>
          <div>
            <p className="text-2xl font-bold">98.5%</p>
            <p className="text-xs text-muted-foreground">Weekly Shift Attendance Rate</p>
          </div>
        </div>
      </div>

      <div className="bg-card border border-border/40 rounded-xl overflow-hidden shadow-sm">
        <table className="w-full border-collapse text-left text-sm">
          <thead>
            <tr className="border-b border-border/40 bg-secondary/10">
              <th className="p-4 font-semibold text-muted-foreground">Staff Member</th>
              <th className="p-4 font-semibold text-muted-foreground">Operational Role</th>
              <th className="p-4 font-semibold text-muted-foreground">Assigned Shift</th>
              <th className="p-4 font-semibold text-muted-foreground">Current Status</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-border/40">
            {mockEmployees.map((emp) => (
              <tr key={emp.id} className="hover:bg-secondary/15 transition-colors">
                <td className="p-4 font-medium text-foreground">{emp.name}</td>
                <td className="p-4 text-muted-foreground">{emp.role}</td>
                <td className="p-4 text-muted-foreground">{emp.shift}</td>
                <td className="p-4">
                  <span className={`text-[10px] uppercase font-bold tracking-wider px-2 py-0.5 rounded border ${
                    emp.status === "On Duty" 
                      ? "border-emerald-500/50 text-emerald-400 bg-emerald-500/5"
                      : emp.status === "Scheduled"
                      ? "border-indigo-500/50 text-indigo-400 bg-indigo-500/5"
                      : "border-slate-500/50 text-slate-400 bg-slate-500/5"
                  }`}>
                    {emp.status}
                  </span>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
