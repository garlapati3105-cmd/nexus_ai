"use client";

import { useEffect, useState } from "react";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { useSession } from "@/context/SessionContext";
import { Search, ShoppingCart, User, Plus, Trash2, CreditCard, CheckCircle, RefreshCw, XCircle, FileText, Check } from "lucide-react";
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogDescription, DialogFooter } from "@/components/ui/dialog";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "https://nexusai-production-bd29.up.railway.app";
const MOCK_BRANCH_ID = "b1111111-1111-4111-9111-111111111111"; // Banjara Hills fallbacks

interface Customer {
  id: string;
  first_name: string;
  last_name: string;
  phone: string;
  email: string;
  loyalty_points: number;
}

interface Medicine {
  id: string;
  brand_name: string;
  substance_name: string;
  sku: string;
  mrp: number;
  available_stock: number;
  batches: Array<{
    id: string;
    batch_number: string;
    expiry_date: string;
  }>;
}

interface CartItem {
  medicine: Medicine;
  quantity: number;
  selectedBatchId: string;
}

export default function CashierPOS() {
  const { activeBranch } = useSession();
  const activeBranchId = activeBranch?.id || MOCK_BRANCH_ID;

  // State Management
  const [customers, setCustomers] = useState<Customer[]>([]);
  const [selectedCustomer, setSelectedCustomer] = useState<Customer | null>(null);
  const [customerSearch, setCustomerSearch] = useState("");
  const [showAddCustomer, setShowAddCustomer] = useState(false);
  
  // New Customer Form State
  const [newCustFirst, setNewCustFirst] = useState("");
  const [newCustLast, setNewCustLast] = useState("");
  const [newCustPhone, setNewCustPhone] = useState("");
  const [newCustEmail, setNewCustEmail] = useState("");
  const [newCustAddress, setNewCustAddress] = useState("");
  const [newCustGender, setNewCustGender] = useState("Unspecified");

  const [medicines, setMedicines] = useState<Medicine[]>([]);
  const [medQuery, setMedQuery] = useState("");
  const [cart, setCart] = useState<CartItem[]>([]);
  
  // Payment Mode
  const [paymentMethods, setPaymentMethods] = useState<Array<{ id: string, name: string }>>([
    { id: "11111111-1111-1111-1111-111111111111", name: "Cash" },
    { id: "22222222-2222-2222-2222-222222222222", name: "Credit Card" },
    { id: "33333333-3333-3333-3333-333333333333", name: "UPI (Google Pay / PhonePe)" }
  ]);
  const [selectedMethodId, setSelectedMethodId] = useState("");
  const [draftOrder, setDraftOrder] = useState<any | null>(null);
  
  // Dialog Controllers
  const [showPaymentDialog, setShowPaymentDialog] = useState(false);
  const [showInvoiceDialog, setShowInvoiceDialog] = useState<any | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);

  // Search Customers
  const handleCustomerSearch = async () => {
    try {
      const res = await fetch(`${API_BASE_URL}/cashier/customers?search=${encodeURIComponent(customerSearch)}`);
      if (res.ok) {
        const data = await res.json();
        setCustomers(data);
      }
    } catch (e) {
      console.error("Customers search failed:", e);
    }
  };

  // Add Customer
  const handleAddNewCustomer = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!newCustFirst || !newCustLast || !newCustPhone) {
      alert("Please fill first name, last name, and phone.");
      return;
    }
    setIsSubmitting(true);
    try {
      const res = await fetch(`${API_BASE_URL}/cashier/customer`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          first_name: newCustFirst,
          last_name: newCustLast,
          phone: newCustPhone,
          email: newCustEmail,
          address: newCustAddress,
          gender: newCustGender
        }),
      });
      if (res.ok) {
        const saved = await res.json();
        setSelectedCustomer(saved);
        setShowAddCustomer(false);
        // Clear fields
        setNewCustFirst("");
        setNewCustLast("");
        setNewCustPhone("");
        setNewCustEmail("");
        setNewCustAddress("");
      } else {
        alert("Email or Phone already registered.");
      }
    } catch (err) {
      console.error("Save client crashed:", err);
    } finally {
      setIsSubmitting(false);
    }
  };

  // Query Medicines stocks
  const queryMedicines = async () => {
    setIsLoading(true);
    try {
      const res = await fetch(`${API_BASE_URL}/cashier/medicines?search=${encodeURIComponent(medQuery)}&branch_id=${activeBranchId}`);
      if (res.ok) {
        const data = await res.json();
        setMedicines(data);
      }
    } catch (e) {
      console.error("Medicines error:", e);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    queryMedicines();
  }, [medQuery]);

  // Cart operations
  const addToCart = (med: Medicine) => {
    if (med.available_stock <= 0) {
      alert("No available stock in this batch.");
      return;
    }
    const defaultBatch = med.batches[0]?.id || "";
    // Check if duplicate
    const index = cart.findIndex((item) => item.medicine.id === med.id);
    if (index > -1) {
      const currentQty = cart[index].quantity;
      if (currentQty >= med.available_stock) {
        alert("Cannot add more units than stock availability.");
        return;
      }
      const updated = [...cart];
      updated[index].quantity += 1;
      setCart(updated);
    } else {
      setCart([...cart, { medicine: med, quantity: 1, selectedBatchId: defaultBatch }]);
    }
  };

  const updateCartQty = (medId: string, delta: number) => {
    const updated = [...cart];
    const index = updated.findIndex((item) => item.medicine.id === medId);
    if (index > -1) {
      const newQty = updated[index].quantity + delta;
      if (newQty <= 0) {
        updated.splice(index, 1);
      } else if (newQty > updated[index].medicine.available_stock) {
        alert("Cannot add more units than stock availability.");
        return;
      } else {
        updated[index].quantity = newQty;
      }
      setCart(updated);
    }
  };

  const removeFromCart = (medId: string) => {
    setCart(cart.filter((item) => item.medicine.id !== medId));
  };

  // Totals calculations
  const subtotal = cart.reduce((sum, item) => sum + item.medicine.mrp * item.quantity, 0);
  const tax = subtotal * 0.12; // 12% GST
  const grandTotal = subtotal + tax;

  // Checkout and draft order
  const handleProceedToPayment = async () => {
    if (!selectedCustomer) {
      alert("Please select or register a customer first.");
      return;
    }
    if (cart.length === 0) {
      alert("Your shopping cart is empty.");
      return;
    }
    
    setIsSubmitting(true);
    try {
      const itemsPayload = cart.map((item) => ({
        medicine_id: item.medicine.id,
        batch_id: item.selectedBatchId,
        quantity: item.quantity
      }));
      
      const res = await fetch(`${API_BASE_URL}/cashier/order`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          branch_id: activeBranchId,
          customer_id: selectedCustomer.id,
          items: itemsPayload
        })
      });
      
      if (res.ok) {
        const orderData = await res.json();
        setDraftOrder(orderData);
        setSelectedMethodId(paymentMethods[0].id);
        setShowPaymentDialog(true);
      } else {
        alert("Stock out during draft checkout checkout lock.");
      }
    } catch (e) {
      console.error("Payment drafts failed:", e);
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleConfirmPayment = async () => {
    if (!draftOrder || !selectedMethodId) return;
    setIsSubmitting(true);
    try {
      const res = await fetch(`${API_BASE_URL}/cashier/payment`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          order_id: draftOrder.id,
          payment_method_id: selectedMethodId,
          amount: grandTotal
        })
      });
      if (res.ok) {
        const invoiceData = await res.json();
        setShowPaymentDialog(false);
        setShowInvoiceDialog(invoiceData);
        // Reset POS billing view
        setCart([]);
        setSelectedCustomer(null);
        setDraftOrder(null);
        queryMedicines();
      } else {
        alert("Payment process failed.");
      }
    } catch (e) {
      console.error("Payment error:", e);
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="space-y-6">
      {/* Upper header view */}
      <div>
        <h2 className="text-3xl font-bold tracking-tight bg-clip-text text-transparent bg-gradient-to-r from-foreground to-foreground/80">
          Point of Sale (POS)
        </h2>
        <p className="text-muted-foreground mt-1">
          Create customer profiles, search active medicines, and receipt orders.
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left Side: Medicine search list and customer selection (2 columns on lg) */}
        <div className="lg:col-span-2 space-y-6">
          {/* Customer Lookup Card */}
          <Card className="bg-card/40 border-border/40">
            <CardHeader className="pb-4">
              <CardTitle className="text-lg flex items-center gap-2">
                <User className="w-5 h-5 text-primary" />
                Customer Registration
              </CardTitle>
              <CardDescription>Select customer profile to record purchase loyalty points.</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              {selectedCustomer ? (
                <div className="flex justify-between items-center bg-primary/5 border border-primary/20 p-3 rounded-lg">
                  <div className="text-sm">
                    <span className="font-semibold block">{selectedCustomer.first_name} {selectedCustomer.last_name}</span>
                    <span className="text-xs text-muted-foreground">{selectedCustomer.phone} • {selectedCustomer.email || "No email"}</span>
                  </div>
                  <Button variant="ghost" size="sm" onClick={() => setSelectedCustomer(null)} className="text-rose-500 hover:text-rose-600 hover:bg-rose-500/10">
                    Change
                  </Button>
                </div>
              ) : (
                <div className="space-y-3">
                  <div className="flex gap-2">
                    <div className="relative flex-1">
                      <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-muted-foreground w-4 h-4" />
                      <input
                        type="text"
                        placeholder="Search by phone number or first name..."
                        value={customerSearch}
                        onChange={(e) => setCustomerSearch(e.target.value)}
                        onKeyDown={(e) => e.key === "Enter" && handleCustomerSearch()}
                        className="w-full pl-9 pr-4 py-2 bg-zinc-900/40 border border-border/40 rounded-lg text-sm focus:outline-none focus:ring-1 focus:ring-primary/40 bg-zinc-900/10 placeholder-muted-foreground/60 text-foreground"
                      />
                    </div>
                    <Button onClick={handleCustomerSearch} className="h-9">Search</Button>
                    <Button onClick={() => setShowAddCustomer(true)} variant="outline" className="h-9 gap-1 hover:bg-secondary/40 border-border/40">
                      <Plus className="w-3.5 h-3.5" /> Register
                    </Button>
                  </div>

                  {customers.length > 0 && (
                    <div className="border border-border/20 rounded-lg max-h-40 overflow-y-auto divide-y divide-border/20">
                      {customers.map((c) => (
                        <div key={c.id} onClick={() => setSelectedCustomer(c)} className="p-3 hover:bg-secondary/20 cursor-pointer flex justify-between items-center transition-colors">
                          <span className="text-sm font-semibold">{c.first_name} {c.last_name}</span>
                          <span className="text-xs text-muted-foreground">{c.phone}</span>
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              )}
            </CardContent>
          </Card>

          {/* Medicines SKU Catalog Lookup */}
          <Card className="bg-card/40 border-border/40">
            <CardHeader>
              <CardTitle className="text-lg flex items-center gap-2">
                <ShoppingCart className="w-5 h-5 text-primary" />
                SKU Master Lookup
              </CardTitle>
              <CardDescription>Search pharmaceutical formula catalogs and batch MRPs.</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="relative">
                <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-muted-foreground w-4 h-4" />
                <input
                  type="text"
                  placeholder="Query brand (e.g. Paracetamol, Montelukast)..."
                  value={medQuery}
                  onChange={(e) => setMedQuery(e.target.value)}
                  className="w-full pl-9 pr-4 py-2 bg-zinc-900/40 border border-border/40 rounded-lg text-sm focus:outline-none focus:ring-1 focus:ring-primary/40 bg-zinc-900/10 placeholder-muted-foreground/60 text-foreground"
                />
              </div>

              {isLoading ? (
                <div className="flex justify-center items-center py-10">
                  <RefreshCw className="w-6 h-6 animate-spin text-primary" />
                </div>
              ) : medicines.length === 0 ? (
                <p className="text-xs text-muted-foreground text-center py-6">No medicines match current search constraints.</p>
              ) : (
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4 max-h-[360px] overflow-y-auto pr-1">
                  {medicines.map((med) => (
                    <div key={med.id} className="p-3 rounded-lg border border-border/20 bg-secondary/10 hover:border-border/60 transition-colors flex justify-between items-center text-sm">
                      <div className="space-y-1 pr-2">
                        <span className="font-semibold block text-foreground truncate max-w-[170px]">{med.brand_name}</span>
                        <span className="text-[10px] text-muted-foreground block font-mono truncate max-w-[170px]">{med.substance_name}</span>
                        <div className="flex gap-2 pt-1">
                          <Badge variant="outline" className="text-[9px] border-primary/20 text-primary">
                            Stock: {med.available_stock}
                          </Badge>
                          <Badge variant="outline" className="text-[9px] border-border/30">
                            MRP: ₹{med.mrp.toFixed(2)}
                          </Badge>
                        </div>
                      </div>
                      <Button
                        size="sm"
                        onClick={() => addToCart(med)}
                        disabled={med.available_stock <= 0}
                        className="bg-primary hover:bg-primary/90 text-primary-foreground text-xs font-semibold px-2.5 h-8 gap-0.5"
                      >
                        <Plus className="w-3.5 h-3.5" /> Add
                      </Button>
                    </div>
                  ))}
                </div>
              )}
            </CardContent>
          </Card>
        </div>

        {/* Right Side: Shopping Cart Billing calculations (1 column) */}
        <div className="space-y-6">
          <Card className="bg-card/40 border-border/40 flex flex-col justify-between h-full min-h-[580px] shadow-lg">
            <CardHeader className="border-b border-border/20 pb-4">
              <CardTitle className="text-lg flex justify-between items-center">
                <span>POS shopping Cart</span>
                {cart.length > 0 && (
                  <Badge className="bg-primary/20 text-primary border border-primary/20">
                    {cart.reduce((sum, item) => sum + item.quantity, 0)} Items
                  </Badge>
                )}
              </CardTitle>
              <CardDescription>Adjust dosage quantities to invoice total checkout levels.</CardDescription>
            </CardHeader>

            <CardContent className="flex-1 overflow-y-auto py-4 space-y-4 max-h-[360px]">
              {cart.length === 0 ? (
                <div className="flex flex-col items-center justify-center py-20 text-center text-muted-foreground">
                  <ShoppingCart className="w-12 h-12 text-muted-foreground/30 mb-2" />
                  <span className="text-sm font-semibold">Empty Cart</span>
                  <p className="text-xs text-muted-foreground max-w-xs mt-1">Add items from medicine search catalog on the left to start billing.</p>
                </div>
              ) : (
                <div className="divide-y divide-border/25">
                  {cart.map((item) => (
                    <div key={item.medicine.id} className="py-3 flex justify-between items-start gap-2 text-sm first:pt-0 last:pb-0">
                      <div className="space-y-0.5 flex-1 min-w-0">
                        <span className="font-semibold text-foreground block truncate">{item.medicine.brand_name}</span>
                        <span className="text-[10px] text-muted-foreground block truncate">Unit MRP: ₹{item.medicine.mrp}</span>
                        {item.medicine.batches.length > 0 && (
                          <span className="text-[9px] text-amber-500 font-mono block">Expires: {new Date(item.medicine.batches[0].expiry_date).toLocaleDateString()}</span>
                        )}
                      </div>
                      
                      <div className="flex flex-col items-end gap-1.5 min-w-[70px]">
                        <span className="font-bold text-foreground">₹{(item.medicine.mrp * item.quantity).toFixed(2)}</span>
                        <div className="flex items-center gap-1.5 border border-border/30 rounded bg-secondary/20 p-0.5">
                          <button onClick={() => updateCartQty(item.medicine.id, -1)} className="px-1 py-0.5 hover:bg-secondary/40 text-xs text-muted-foreground rounded">-</button>
                          <span className="text-xs font-semibold px-0.5">{item.quantity}</span>
                          <button onClick={() => updateCartQty(item.medicine.id, 1)} className="px-1 py-0.5 hover:bg-secondary/40 text-xs text-muted-foreground rounded">+</button>
                        </div>
                      </div>

                      <button onClick={() => removeFromCart(item.medicine.id)} className="text-muted-foreground/60 hover:text-rose-500 transition-colors pt-1">
                        <Trash2 className="w-4 h-4" />
                      </button>
                    </div>
                  ))}
                </div>
              )}
            </CardContent>

            <div className="border-t border-border/20 p-4 space-y-4 bg-zinc-950/20">
              <div className="space-y-2 text-xs">
                <div className="flex justify-between text-muted-foreground">
                  <span>Subtotal</span>
                  <span>₹{subtotal.toFixed(2)}</span>
                </div>
                <div className="flex justify-between text-muted-foreground">
                  <span>GST Taxation (12%)</span>
                  <span>₹{tax.toFixed(2)}</span>
                </div>
                <div className="flex justify-between font-bold text-sm text-foreground pt-1 border-t border-border/10">
                  <span>Grand Total</span>
                  <span>₹{grandTotal.toFixed(2)}</span>
                </div>
              </div>

              <Button
                onClick={handleProceedToPayment}
                disabled={cart.length === 0 || isSubmitting}
                className="w-full bg-primary hover:bg-primary/95 text-primary-foreground font-bold h-10 gap-1.5 text-sm"
              >
                {isSubmitting ? (
                  <RefreshCw className="w-4 h-4 animate-spin" />
                ) : (
                  <CreditCard className="w-4 h-4" />
                )}
                Lock draft & Pay
              </Button>
            </div>
          </Card>
        </div>
      </div>

      {/* Add Customer Overlay Dialog */}
      <Dialog open={showAddCustomer} onOpenChange={(open) => !open && setShowAddCustomer(false)}>
        <DialogContent className="max-w-md bg-zinc-950 border border-border/40 text-foreground">
          <DialogHeader>
            <DialogTitle className="text-xl font-bold">Register Customer</DialogTitle>
            <DialogDescription>Create a profile loyalty file for billing records.</DialogDescription>
          </DialogHeader>
          <form onSubmit={handleAddNewCustomer} className="space-y-4 my-2 text-sm">
            <div className="grid grid-cols-2 gap-3">
              <div className="space-y-1">
                <label className="text-xs text-muted-foreground">First Name *</label>
                <input
                  type="text" required
                  value={newCustFirst}
                  onChange={(e) => setNewCustFirst(e.target.value)}
                  className="w-full px-3 py-2 bg-zinc-900 border border-border/40 rounded focus:outline-none focus:ring-1 focus:ring-primary bg-zinc-900/10"
                />
              </div>
              <div className="space-y-1">
                <label className="text-xs text-muted-foreground">Last Name *</label>
                <input
                  type="text" required
                  value={newCustLast}
                  onChange={(e) => setNewCustLast(e.target.value)}
                  className="w-full px-3 py-2 bg-zinc-900 border border-border/40 rounded focus:outline-none focus:ring-1 focus:ring-primary bg-zinc-900/10"
                />
              </div>
            </div>
            
            <div className="space-y-1">
              <label className="text-xs text-muted-foreground">Phone Number *</label>
              <input
                type="text" required
                value={newCustPhone}
                onChange={(e) => setNewCustPhone(e.target.value)}
                className="w-full px-3 py-2 bg-zinc-900 border border-border/40 rounded focus:outline-none focus:ring-1 focus:ring-primary bg-zinc-900/10"
              />
            </div>
            <div className="space-y-1">
              <label className="text-xs text-muted-foreground">Email Address (Optional)</label>
              <input
                type="email"
                value={newCustEmail}
                onChange={(e) => setNewCustEmail(e.target.value)}
                className="w-full px-3 py-2 bg-zinc-900 border border-border/40 rounded focus:outline-none focus:ring-1 focus:ring-primary bg-zinc-900/10"
              />
            </div>
            <div className="space-y-1">
              <label className="text-xs text-muted-foreground">Gender</label>
              <select
                value={newCustGender}
                onChange={(e) => setNewCustGender(e.target.value)}
                className="w-full px-3 py-2 bg-zinc-900 border border-border/40 rounded focus:outline-none focus:ring-1 focus:ring-primary bg-zinc-900/10"
              >
                <option value="Male">Male</option>
                <option value="Female">Female</option>
                <option value="Unspecified">Unspecified</option>
              </select>
            </div>
            <div className="space-y-1">
              <label className="text-xs text-muted-foreground">Address Details</label>
              <textarea
                value={newCustAddress}
                onChange={(e) => setNewCustAddress(e.target.value)}
                rows={2}
                className="w-full px-3 py-2 bg-zinc-900 border border-border/40 rounded focus:outline-none focus:ring-1 focus:ring-primary bg-zinc-900/10"
              />
            </div>

            <DialogFooter className="pt-2">
              <Button type="button" variant="outline" onClick={() => setShowAddCustomer(false)} className="border-border/30 h-9 text-xs">
                Cancel
              </Button>
              <Button type="submit" disabled={isSubmitting} className="h-9 text-xs">
                {isSubmitting ? "Creating..." : "Save Registry"}
              </Button>
            </DialogFooter>
          </form>
        </DialogContent>
      </Dialog>

      {/* Payment Selection Dialog */}
      <Dialog open={showPaymentDialog} onOpenChange={(open) => !open && setShowPaymentDialog(false)}>
        <DialogContent className="max-w-md bg-zinc-950 border border-border/40 text-foreground">
          <DialogHeader>
            <DialogTitle className="text-xl font-bold flex items-center gap-2">
              <CreditCard className="w-5 h-5 text-primary" />
              Collect Payment
            </DialogTitle>
            <DialogDescription>Select the client payment method gateway.</DialogDescription>
          </DialogHeader>

          <div className="space-y-4 my-2 text-sm">
            <div className="bg-secondary/15 p-4 rounded-lg border border-border/20 text-center">
              <span className="text-xs text-muted-foreground block">Amount Due</span>
              <span className="text-3xl font-extrabold text-foreground">₹{grandTotal.toFixed(2)}</span>
            </div>

            <div className="space-y-2">
              <label className="text-xs text-muted-foreground">Payment Method</label>
              <div className="grid grid-cols-1 gap-2">
                {paymentMethods.map((m) => (
                  <label
                    key={m.id}
                    className={`p-3 rounded-lg border flex items-center justify-between cursor-pointer transition-colors ${
                      selectedMethodId === m.id
                        ? "border-primary bg-primary/5 text-primary-foreground font-semibold"
                        : "border-border/20 hover:bg-secondary/25"
                    }`}
                  >
                    <span>{m.name}</span>
                    <input
                      type="radio"
                      name="payment_choice"
                      value={m.id}
                      checked={selectedMethodId === m.id}
                      onChange={() => setSelectedMethodId(m.id)}
                      className="accent-primary h-4 w-4"
                    />
                  </label>
                ))}
              </div>
            </div>
          </div>

          <DialogFooter className="pt-2">
            <Button variant="outline" onClick={() => setShowPaymentDialog(false)} className="border-border/30 h-9 text-xs">
              Back to POS
            </Button>
            <Button onClick={handleConfirmPayment} disabled={isSubmitting} className="bg-primary hover:bg-primary/95 text-primary-foreground h-9 text-xs font-semibold">
              {isSubmitting ? "Processing..." : "Confirm Checkout"}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* Invoice Receipt Receipt Dialog */}
      <Dialog open={showInvoiceDialog !== null} onOpenChange={(open) => !open && setShowInvoiceDialog(null)}>
        {showInvoiceDialog && (
          <DialogContent className="max-w-md bg-zinc-950 border border-border/40 text-foreground py-6 text-center">
            <div className="flex flex-col items-center gap-4 text-center">
              <div className="h-12 w-12 bg-emerald-500/25 border border-emerald-500/25 text-emerald-500 rounded-full flex items-center justify-center">
                <Check className="h-6 w-6" />
              </div>
              <div>
                <h3 className="text-xl font-bold">POS Billing Complete</h3>
                <p className="text-xs text-muted-foreground mt-1">Invoice number: {showInvoiceDialog.invoice?.invoice_no || "INV-001"}</p>
              </div>

              <div className="w-full bg-secondary/10 border border-border/20 p-4 rounded-lg text-left text-xs space-y-2 mt-2">
                <div className="flex justify-between border-b border-border/10 pb-1.5 font-semibold text-foreground">
                  <span>Summary Details</span>
                  <span>Ready for Pharmacist</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-muted-foreground">Order Ref:</span>
                  <span className="font-mono text-foreground">{showInvoiceDialog.invoice?.order_id?.slice(0, 8) || "N/A"}</span>
                </div>
                <div className="flex justify-between font-bold pt-1.5 border-t border-border/10 text-foreground">
                  <span>Paid Total</span>
                  <span>₹{showInvoiceDialog.invoice?.total_amount?.toLocaleString("en-IN") || grandTotal.toFixed(2)}</span>
                </div>
              </div>

              <div className="flex gap-2 w-full mt-4">
                <Button
                  variant="outline"
                  onClick={() => setShowInvoiceDialog(null)}
                  className="flex-1 border-border/30 h-9 text-xs"
                >
                  Close Print
                </Button>
                <Button
                  onClick={() => {
                    const csv = [
                      ["Item", "Invoice", "Total"],
                      ["Pharmacy checkout order", showInvoiceDialog.invoice?.invoice_no, showInvoiceDialog.invoice?.total_amount]
                    ].map(r => r.join(",")).join("\n");
                    const blob = new Blob([csv], { type: "text/csv" });
                    const url = URL.createObjectURL(blob);
                    const a = document.createElement("a");
                    a.href = url;
                    a.download = `invoice_${showInvoiceDialog.invoice?.invoice_no}.csv`;
                    a.click();
                    URL.revokeObjectURL(url);
                  }}
                  className="flex-1 bg-primary hover:bg-primary/95 text-primary-foreground h-9 text-xs"
                >
                  Export Invoice Receipt
                </Button>
              </div>
            </div>
          </DialogContent>
        )}
      </Dialog>
    </div>
  );
}
