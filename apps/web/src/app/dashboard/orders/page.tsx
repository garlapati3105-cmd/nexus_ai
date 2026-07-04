"use client";

import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";

export default function OrdersPage() {
  const orders = [
    { id: "ORD-9921", time: "10:42 AM", branch: "Banjara Hills", items: 3, total: "₹450.00", status: "Completed" },
    { id: "ORD-9922", time: "10:45 AM", branch: "Jubilee Hills", items: 1, total: "₹120.00", status: "Completed" },
    { id: "ORD-9923", time: "10:48 AM", branch: "Banjara Hills", items: 2, total: "₹890.00", status: "Pending (Out of Stock)" },
    { id: "ORD-9924", time: "10:51 AM", branch: "Madhapur", items: 5, total: "₹2,100.00", status: "Completed" },
  ];

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-end">
        <div>
          <h2 className="text-3xl font-bold tracking-tight">Network Orders</h2>
          <p className="text-muted-foreground mt-1">Real-time POS checkout feed.</p>
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
              {orders.map((order, i) => (
                <tr key={i} className="border-b border-border/50 hover:bg-secondary/20 transition-colors">
                  <td className="px-6 py-4 font-medium">{order.id}</td>
                  <td className="px-6 py-4 text-muted-foreground">{order.time}</td>
                  <td className="px-6 py-4">{order.branch}</td>
                  <td className="px-6 py-4">{order.items}</td>
                  <td className="px-6 py-4 font-bold">{order.total}</td>
                  <td className="px-6 py-4">
                    <Badge variant="outline" className={`
                      ${order.status.includes("Pending") ? "border-amber-500 text-amber-500 bg-amber-500/10" : "border-emerald-500 text-emerald-500 bg-emerald-500/10"}
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
