"use client";

import { useEffect, useState } from "react";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { useSession } from "@/context/SessionContext";
import { RefreshCw, CheckCircle, XCircle, Search, Pill, ShieldAlert, Clock, ShoppingCart, User, Receipt, FileText, Check } from "lucide-react";
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogDescription, DialogFooter } from "@/components/ui/dialog";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "https://nexusai-production-bd29.up.railway.app";

interface OrderItem {
  id: string;
  medicine_id: string;
  batch_id: string;
  quantity: number;
  unit_price: number;
  net_price: number;
  medicines?: {
    brand_name: string;
    substance_name: string;
  };
}

interface Order {
  id: string;
  order_no: string;
  branch_id: string;
  customer_id: string;
  subtotal: number;
  tax_amount: number;
  total_amount: number;
  status: string;
  created_at: string;
  branches?: {
    name: string;
  };
  customers?: {
    first_name: string;
    last_name: string;
  };
  items?: OrderItem[];
}

export default function PharmacistDashboard() {
  const { currentRole, activeBranch } = useSession();
  const [orders, setOrders] = useState<Order[]>([]);
  const [historyOrders, setHistoryOrders] = useState<Order[]>([]);
  const [selectedOrder, setSelectedOrder] = useState<Order | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isHistoryLoading, setIsHistoryLoading] = useState(false);
  const [isActionLoading, setIsActionLoading] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState<"pending" | "history">("pending");
  const [searchQuery, setSearchQuery] = useState("");
  const [showStatusDialog, setShowStatusDialog] = useState<{ type: "success" | "reject"; message: string } | null>(null);

  const fetchPendingOrders = async () => {
    setIsLoading(true);
    try {
      const url = activeBranch?.id
        ? `${API_BASE_URL}/pharmacist/orders?branch_id=${activeBranch.id}`
        : `${API_BASE_URL}/pharmacist/orders`;
      const res = await fetch(url);
      if (res.ok) {
        const data = await res.json();
        setOrders(data);
      }
    } catch (e) {
      console.error("Failed to fetch pharmacist queue:", e);
    } finally {
      setIsLoading(false);
    }
  };

  const fetchHistory = async () => {
    setIsHistoryLoading(true);
    try {
      const url = activeBranch?.id
        ? `${API_BASE_URL}/pharmacist/history?branch_id=${activeBranch.id}`
        : `${API_BASE_URL}/pharmacist/history`;
      const res = await fetch(url);
      if (res.ok) {
        const data = await res.json();
        setHistoryOrders(data);
      }
    } catch (e) {
      console.error("Failed to fetch history:", e);
    } finally {
      setIsHistoryLoading(false);
    }
  };

  // eslint-disable-next-line react-hooks/exhaustive-deps
  useEffect(() => {
    const timer = setTimeout(() => {
      if (activeTab === "pending") {
        fetchPendingOrders();
      } else {
        fetchHistory();
      }
    }, 0);
    return () => clearTimeout(timer);
  }, [activeTab]);

  const handleDispense = async (orderId: string) => {
    setIsActionLoading(orderId);
    try {
      const res = await fetch(`${API_BASE_URL}/pharmacist/dispense`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ order_id: orderId }),
      });
      if (res.ok) {
        // Success feedback
        setShowStatusDialog({
          type: "success",
          message: `Order successfully dispensed and inventory counts updated.`
        });
        setSelectedOrder(null);
        fetchPendingOrders();
      } else {
        alert("Failed to dispense this order. Please verify stock counts.");
      }
    } catch (e) {
      console.error("Dispense request crashed:", e);
    } finally {
      setIsActionLoading(null);
    }
  };

  const handleReject = async (orderId: string) => {
    if (!window.confirm("Are you sure you want to reject dispensing for this order? This will release reserved inventory.")) return;
    setIsActionLoading(orderId);
    try {
      const res = await fetch(`${API_BASE_URL}/pharmacist/reject`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ order_id: orderId }),
      });
      if (res.ok) {
        setShowStatusDialog({
          type: "reject",
          message: `Dispensing rejected. Stock reservations released.`
        });
        setSelectedOrder(null);
        fetchPendingOrders();
      } else {
        alert("Failed to reject order.");
      }
    } catch (e) {
      console.error("Rejection crashed:", e);
    } finally {
      setIsActionLoading(null);
    }
  };

  const filteredOrders = (activeTab === "pending" ? orders : historyOrders).filter((o) => {
    const term = searchQuery.toLowerCase();
    return (
      o.order_no.toLowerCase().includes(term) ||
      (o.customers ? `${o.customers.first_name} ${o.customers.last_name}`.toLowerCase().includes(term) : false)
    );
  });

  return (
    <div className="space-y-6">
      {/* Upper header */}
      <div className="flex flex-col md:flex-row md:justify-between md:items-end gap-4">
        <div>
          <h2 className="text-3xl font-bold tracking-tight bg-clip-text text-transparent bg-gradient-to-r from-foreground to-gradient-to-r">
            Pharmacist Workspace
          </h2>
          <p className="text-muted-foreground mt-1">
            Audit prescriptions, dispense medicines and manage handover checks.
          </p>
        </div>
        <div className="flex items-center gap-2">
          <Button
            variant="outline"
            size="sm"
            onClick={activeTab === "pending" ? fetchPendingOrders : fetchHistory}
            disabled={isLoading || isHistoryLoading}
            className="h-9 gap-2 border-border/40 hover:bg-secondary/40"
          >
            <RefreshCw className={`w-4 h-4 ${(isLoading || isHistoryLoading) ? "animate-spin" : ""}`} />
            Refresh Queue
          </Button>
        </div>
      </div>

      {/* Tabs list */}
      <div className="flex border-b border-border/40">
        <button
          onClick={() => setActiveTab("pending")}
          className={`px-4 py-2 text-sm font-semibold border-b-2 transition-colors relative ${
            activeTab === "pending"
              ? "border-primary text-primary"
              : "border-transparent text-muted-foreground hover:text-foreground"
          }`}
        >
          Pending Dispensation
          {orders.length > 0 && (
            <Badge className="ml-2 bg-primary/20 text-primary border border-primary/20 hover:bg-primary/20">
              {orders.length}
            </Badge>
          )}
        </button>
        <button
          onClick={() => setActiveTab("history")}
          className={`px-4 py-2 text-sm font-semibold border-b-2 transition-colors ${
            activeTab === "history"
              ? "border-primary text-primary"
              : "border-transparent text-muted-foreground hover:text-foreground"
          }`}
        >
          Dispensed History
        </button>
      </div>

      {/* Search Bar */}
      <div className="relative max-w-md">
        <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-muted-foreground w-4 h-4" />
        <input
          type="text"
          placeholder="Search by Order No or Customer Name..."
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
          className="w-full pl-9 pr-4 py-2 bg-card border border-border/40 rounded-lg text-sm focus:outline-none focus:ring-1 focus:ring-primary/40 bg-zinc-900/10 placeholder-muted-foreground/60"
        />
      </div>

      {/* List Layout */}
      {isLoading || isHistoryLoading ? (
        <div className="flex flex-col items-center justify-center py-20 gap-3">
          <RefreshCw className="w-8 h-8 text-primary animate-spin" />
          <p className="text-sm text-muted-foreground font-medium">Loading checkout details...</p>
        </div>
      ) : filteredOrders.length === 0 ? (
        <Card className="bg-card/30 border-dashed border-border/40 py-16 text-center">
          <CardContent className="flex flex-col items-center justify-center gap-3">
            <ShoppingCart className="w-12 h-12 text-muted-foreground/40" />
            <div className="font-semibold text-lg">No Orders Found</div>
            <p className="text-sm text-muted-foreground max-w-xs">
              {searchQuery ? "No matches fit your active query tags." : "No orders are currently waiting for dispensing in this branch queue."}
            </p>
          </CardContent>
        </Card>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-6">
          {filteredOrders.map((order) => (
            <Card key={order.id} className="bg-card/40 border-border/40 relative overflow-hidden flex flex-col justify-between hover:border-border/80 transition-all shadow-md">
              <CardHeader className="pb-4">
                <div className="flex justify-between items-start">
                  <div className="space-y-1">
                    <span className="font-mono text-xs text-muted-foreground bg-secondary/50 px-2 py-0.5 rounded border border-border/20">
                      {order.order_no}
                    </span>
                    <CardTitle className="text-lg font-bold flex items-center gap-1.5 pt-1">
                      <User className="w-4 h-4 text-muted-foreground" />
                      {order.customers ? `${order.customers.first_name} ${order.customers.last_name}` : "Walk-in Customer"}
                    </CardTitle>
                  </div>
                  <Badge variant="outline" className={
                    order.status === "completed"
                      ? "border-emerald-500 text-emerald-500 bg-emerald-500/10"
                      : order.status === "cancelled"
                      ? "border-rose-500 text-rose-500 bg-rose-500/10"
                      : "border-primary text-primary bg-primary/10"
                  }>
                    {order.status === "pending" ? "READY FOR CHECKOUT" : order.status.toUpperCase()}
                  </Badge>
                </div>
                <CardDescription className="flex items-center gap-1 mt-1 text-xs text-muted-foreground/80">
                  <Clock className="w-3.5 h-3.5" />
                  {new Date(order.created_at).toLocaleString("en-IN", { hour: "numeric", minute: "numeric", hour12: true })} • {order.branches?.name || "Hyderabad Branch"}
                </CardDescription>
              </CardHeader>

              <CardContent className="pb-6">
                <div className="space-y-3 bg-secondary/20 p-3 rounded-lg border border-border/10">
                  <div className="text-xs font-semibold text-muted-foreground tracking-wider uppercase">Prescribed Medicines</div>
                  <div className="space-y-2">
                    {order.items?.map((item) => (
                      <div key={item.id} className="flex justify-between items-center text-sm">
                        <div className="flex items-center gap-1.5 font-medium">
                          <Pill className="w-3.5 h-3.5 text-primary" />
                          <span>{item.medicines?.brand_name || "Unknown SKU"}</span>
                        </div>
                        <div className="text-xs font-semibold text-muted-foreground bg-primary/5 px-1.5 py-0.5 rounded border border-primary/10">
                          Qty: {item.quantity}
                        </div>
                      </div>
                    ))}
                  </div>
                </div>

                <div className="mt-4 flex justify-between items-center bg-zinc-950/20 p-2.5 rounded border border-border/20">
                  <span className="text-xs text-muted-foreground">Total Invoiced</span>
                  <span className="text-base font-bold text-foreground">₹{order.total_amount.toLocaleString("en-IN")}</span>
                </div>
              </CardContent>

              <div className="p-4 pt-0 border-t border-border/20 flex gap-2">
                <Button
                  onClick={() => setSelectedOrder(order)}
                  variant="secondary"
                  size="sm"
                  className="flex-1 text-xs border border-border/30 hover:bg-secondary"
                >
                  View Details
                </Button>
                {order.status === "pending" && (
                  <>
                    <Button
                      onClick={() => handleDispense(order.id)}
                      disabled={isActionLoading !== null}
                      variant="default"
                      size="sm"
                      className="flex-1 text-xs bg-primary hover:bg-primary/90 text-primary-foreground font-semibold"
                    >
                      {isActionLoading === order.id ? (
                        <RefreshCw className="w-3 h-3 animate-spin mr-1" />
                      ) : (
                        <CheckCircle className="w-3.5 h-3.5 mr-1" />
                      )}
                      Dispense
                    </Button>
                  </>
                )}
              </div>
            </Card>
          ))}
        </div>
      )}

      {/* Details Dialog */}
      <Dialog open={selectedOrder !== null} onOpenChange={(open) => !open && setSelectedOrder(null)}>
        {selectedOrder && (
          <DialogContent className="max-w-2xl bg-zinc-950 border border-border/40 text-foreground overflow-hidden">
            <DialogHeader className="border-b border-border/20 pb-4">
              <DialogTitle className="text-2xl font-bold flex items-center gap-2">
                <FileText className="w-6 h-6 text-primary" />
                Prescription & Handover Audit
              </DialogTitle>
              <DialogDescription>
                Verify customers medical records, batch exipry status, and dispense stock keys.
              </DialogDescription>
            </DialogHeader>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-6 my-4 text-sm">
              {/* Left Column: Customer details */}
              <div className="space-y-4">
                <div className="p-4 rounded-lg bg-secondary/10 border border-border/20 space-y-3">
                  <div className="flex items-center gap-2 font-bold text-foreground border-b border-border/10 pb-2">
                    <User className="w-4 h-4 text-primary" />
                    Customer Dossier
                  </div>
                  <div className="grid grid-cols-2 gap-2 text-xs">
                    <span className="text-muted-foreground text-left">Full Name:</span>
                    <span className="font-semibold text-right">{selectedOrder.customers ? `${selectedOrder.customers.first_name} ${selectedOrder.customers.last_name}` : "Walk-in Customer"}</span>
                    <span className="text-muted-foreground text-left">Branch Location:</span>
                    <span className="font-semibold text-right">{selectedOrder.branches?.name || "Hyderabad Local"}</span>
                    <span className="text-muted-foreground text-left">Transaction ID:</span>
                    <span className="font-mono font-semibold text-right text-[10px] truncate">{selectedOrder.id}</span>
                  </div>
                </div>

                <div className="p-4 rounded-lg bg-orange-500/10 border border-orange-500/20 text-orange-400 space-y-2">
                  <div className="flex items-center gap-1.5 font-bold text-sm">
                    <ShieldAlert className="w-4 h-4" />
                    Clinical Safety Warnings
                  </div>
                  <p className="text-xs text-orange-400/80 leading-relaxed">
                    Check if digital prescription requires special cooling chain control or contains narcotics restrictions before confirming physical handover.
                  </p>
                </div>
              </div>

              {/* Right Column: Order items, pricing breakdown */}
              <div className="space-y-4">
                <div className="p-4 rounded-lg bg-secondary/10 border border-border/20 space-y-3">
                  <div className="flex items-center gap-2 font-bold text-foreground border-b border-border/10 pb-2">
                    <Receipt className="w-4 h-4 text-primary" />
                    POS Receipt Breakdown
                  </div>
                  <div className="space-y-2">
                    {selectedOrder.items?.map((item) => (
                      <div key={item.id} className="flex justify-between items-center text-xs">
                        <div className="space-y-0.5">
                          <span className="font-semibold block">{item.medicines?.brand_name}</span>
                          <span className="text-[10px] text-muted-foreground font-mono block">Batch: {item.batch_id.slice(0, 8)}</span>
                        </div>
                        <span className="font-medium text-foreground">₹{item.net_price.toLocaleString("en-IN")} (Qty: {item.quantity})</span>
                      </div>
                    ))}
                  </div>
                  <div className="border-t border-border/10 pt-2 flex justify-between font-bold text-sm text-foreground">
                    <span>Grand Total</span>
                    <span>₹{selectedOrder.total_amount.toLocaleString("en-IN")}</span>
                  </div>
                </div>
              </div>
            </div>

            <DialogFooter className="border-t border-border/20 pt-4 flex gap-2">
              <Button
                variant="outline"
                size="sm"
                onClick={() => setSelectedOrder(null)}
                className="border-border/30 hover:bg-secondary/40 text-xs"
              >
                Close View
              </Button>
              {selectedOrder.status === "pending" && (
                <>
                  <Button
                    onClick={() => handleReject(selectedOrder.id)}
                    disabled={isActionLoading !== null}
                    variant="outline"
                    size="sm"
                    className="border-rose-500/30 text-rose-500 hover:bg-rose-500/10 text-xs"
                  >
                    <XCircle className="w-3.5 h-3.5 mr-1" />
                    Reject Order
                  </Button>
                  <Button
                    onClick={() => handleDispense(selectedOrder.id)}
                    disabled={isActionLoading !== null}
                    variant="default"
                    size="sm"
                    className="bg-primary hover:bg-primary/95 text-primary-foreground font-semibold text-xs"
                  >
                    <CheckCircle className="w-3.5 h-3.5 mr-1" />
                    Approve Handover
                  </Button>
                </>
              )}
            </DialogFooter>
          </DialogContent>
        )}
      </Dialog>

      {/* Success/Rejected Status Dialog */}
      <Dialog open={showStatusDialog !== null} onOpenChange={(open) => !open && setShowStatusDialog(null)}>
        {showStatusDialog && (
          <DialogContent className="max-w-md bg-zinc-950 border border-border/40 text-foreground text-center py-6">
            <div className="flex flex-col items-center gap-4">
              {showStatusDialog.type === "success" ? (
                <div className="h-12 w-12 bg-emerald-500/25 border border-emerald-500/25 text-emerald-500 rounded-full flex items-center justify-center">
                  <Check className="h-6 w-6" />
                </div>
              ) : (
                <div className="h-12 w-12 bg-rose-500/25 border border-rose-500/25 text-rose-500 rounded-full flex items-center justify-center">
                  <XCircle className="h-6 w-6" />
                </div>
              )}
              <h3 className="text-xl font-bold">
                {showStatusDialog.type === "success" ? "Dispensed Successfully" : "Order Cancelled"}
              </h3>
              <p className="text-sm text-muted-foreground">{showStatusDialog.message}</p>
              <Button
                variant="outline"
                onClick={() => setShowStatusDialog(null)}
                className="mt-2 border-border/40 hover:bg-secondary/40 text-xs h-9"
              >
                Okay, continue
              </Button>
            </div>
          </DialogContent>
        )}
      </Dialog>
    </div>
  );
}
