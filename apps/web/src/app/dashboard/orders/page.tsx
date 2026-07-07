"use client";

import { useEffect, useRef, useState } from "react";
import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Download, RefreshCw } from "lucide-react";

const INITIAL_ORDERS = [
  { id: "ORD-9921", time: "10:42 AM", branch: "Banjara Hills", items: 3, total: "₹450.00", status: "Completed" },
  { id: "ORD-9922", time: "10:45 AM", branch: "Jubilee Hills", items: 1, total: "₹120.00", status: "Completed" },
  { id: "ORD-9923", time: "10:48 AM", branch: "Banjara Hills", items: 2, total: "₹890.00", status: "Pending (Out of Stock)" },
  { id: "ORD-9924", time: "10:51 AM", branch: "Madhapur", items: 5, total: "₹2,100.00", status: "Completed" },
  { id: "ORD-9925", time: "11:02 AM", branch: "Gachibowli", items: 4, total: "₹1,340.00", status: "Completed" },
  { id: "ORD-9926", time: "11:15 AM", branch: "Jubilee Hills", items: 2, total: "₹560.00", status: "Processing" },
];

import { useSession } from "@/context/SessionContext";

const BRANCHES = ["Banjara Hills", "Jubilee Hills", "Madhapur", "Gachibowli", "Secunderabad"];
const STATUSES = ["Completed", "Completed", "Completed", "Processing"] as const;

function randomOrder(lastId: number) {
  const branch = BRANCHES[Math.floor(Math.random() * BRANCHES.length)];
  const items = Math.floor(Math.random() * 5) + 1;
  const total = (Math.random() * 3000 + 200).toFixed(2);
  const status = STATUSES[Math.floor(Math.random() * STATUSES.length)];
  const now = new Date();
  const time = now.toLocaleTimeString("en-IN", { hour: "2-digit", minute: "2-digit" });
  return { id: `ORD-${lastId + 1}`, time, branch, items, total: `₹${total}`, status };
}

export default function OrdersPage() {
  const { currentRole, activeBranch } = useSession();
  const [orders, setOrders] = useState(INITIAL_ORDERS);
  const [isRefreshing, setIsRefreshing] = useState(false);
  const lastIdRef = useRef(9926);

  // Filter orders based on user permission level and active branch assignment
  const userBranchName = activeBranch
    ? activeBranch.name
        .toLowerCase()
        .replace(/nexuscare\s+/g, "")
        .replace(/\s+branch/g, "")
        .trim()
    : "banjara hills";

  const filteredOrders = orders.filter((o) => {
    if (currentRole === "CEO" || currentRole === "REGIONAL_MANAGER" || currentRole === "ADMIN") {
      return true;
    }
    const orderBranchNormalized = o.branch
      .toLowerCase()
      .replace(/nexuscare\s+/g, "")
      .replace(/\s+branch/g, "")
      .trim();
    return orderBranchNormalized === userBranchName;
  });

  // Simulate live orders coming in every 8 seconds
  useEffect(() => {
    const interval = setInterval(() => {
      lastIdRef.current += 1;
      const newOrder = randomOrder(lastIdRef.current - 1);
      setOrders((prev) => [newOrder, ...prev.slice(0, 19)]);
    }, 8000);
    return () => clearInterval(interval);
  }, []);

  const handleRefresh = async () => {
    setIsRefreshing(true);
    await new Promise((r) => setTimeout(r, 800));
    lastIdRef.current += 1;
    const newOrder = randomOrder(lastIdRef.current - 1);
    setOrders((prev) => [newOrder, ...prev.slice(0, 19)]);
    setIsRefreshing(false);
  };

  const handleExport = () => {
    const csv = [
      ["Order ID", "Time", "Branch", "Items", "Total", "Status"],
      ...filteredOrders.map((o) => [o.id, o.time, o.branch, o.items, o.total, o.status]),
    ]
      .map((row) => row.join(","))
      .join("\n");
    const blob = new Blob([csv], { type: "text/csv" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = "nexus_orders.csv";
    a.click();
    URL.revokeObjectURL(url);
  };

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-end">
        <div>
          <h2 className="text-3xl font-bold tracking-tight">Network Orders</h2>
          <p className="text-muted-foreground mt-1">Real-time POS checkout feed. Auto-refreshes every 8 seconds.</p>
        </div>
        <div className="flex gap-2">
          <Button variant="outline" onClick={handleRefresh} disabled={isRefreshing} className="gap-2">
            <RefreshCw className={`w-4 h-4 ${isRefreshing ? "animate-spin" : ""}`} />
            Refresh
          </Button>
          <Button variant="outline" onClick={handleExport} className="gap-2">
            <Download className="w-4 h-4" />
            Export CSV
          </Button>
        </div>
      </div>

      <Card className="bg-card/50 border-border/50">
        <CardContent className="p-0">
          <table className="w-full text-sm text-left">
            <thead className="text-xs text-muted-foreground bg-secondary/50 border-b border-border">
              <tr>
                <th className="px-6 py-4 font-medium">Order ID</th>
                <th className="px-6 py-4 font-medium">Time (IST)</th>
                <th className="px-6 py-4 font-medium">Branch</th>
                <th className="px-6 py-4 font-medium">Items</th>
                <th className="px-6 py-4 font-medium">Total</th>
                <th className="px-6 py-4 font-medium">Status</th>
              </tr>
            </thead>
            <tbody>
              {filteredOrders.map((order, i) => (
                <tr key={order.id} className={`border-b border-border/50 hover:bg-secondary/20 transition-colors ${i === 0 ? "bg-primary/5" : ""}`}>
                  <td className="px-6 py-4 font-medium font-mono text-xs">{order.id}</td>
                  <td className="px-6 py-4 text-muted-foreground">{order.time}</td>
                  <td className="px-6 py-4">{order.branch}</td>
                  <td className="px-6 py-4">{order.items}</td>
                  <td className="px-6 py-4 font-bold">{order.total}</td>
                  <td className="px-6 py-4">
                    <Badge variant="outline" className={`
                      ${order.status.includes("Pending") ? "border-amber-500 text-amber-500 bg-amber-500/10" :
                        order.status === "Processing" ? "border-primary text-primary bg-primary/10" :
                        "border-emerald-500 text-emerald-500 bg-emerald-500/10"}
                    `}>
                      {order.status}
                    </Badge>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </CardContent>
      </Card>
    </div>
  );
}
