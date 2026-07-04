"use client";

import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Label } from "@/components/ui/label";
import { Input } from "@/components/ui/input";
import { useSession } from "@/context/SessionContext";
import { useRouter } from "next/navigation";

export default function SettingsPage() {
  const { profile, currentRole, activeBranch, activeOrg, signOut } = useSession();
  const router = useRouter();

  const handleSignOut = async () => {
    await signOut();
    router.push("/login");
  };

  return (
    <div className="space-y-6 max-w-4xl">
      <div>
        <h2 className="text-3xl font-bold tracking-tight">Platform Settings</h2>
        <p className="text-muted-foreground mt-1">Configure your enterprise Nexus AI instance.</p>
      </div>

      {/* Active Session Info */}
      <Card className="bg-card/50 border-border/50">
        <CardHeader>
          <CardTitle>Account Identity</CardTitle>
          <CardDescription>Your active session credentials.</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="grid gap-2">
            <Label>Email</Label>
            <Input value={profile?.email || "—"} className="bg-background max-w-md" readOnly />
          </div>
          <div className="grid gap-2">
            <Label>Active Role</Label>
            <Input value={currentRole || "Guest"} className="bg-background max-w-md" readOnly disabled />
          </div>
          <div className="grid gap-2">
            <Label>Branch Assignment</Label>
            <Input value={activeBranch?.name || "Global (No Branch)"} className="bg-background max-w-md" readOnly disabled />
          </div>
          <div className="grid gap-2">
            <Label>Organization</Label>
            <Input value={activeOrg?.name || "—"} className="bg-background max-w-md" readOnly disabled />
          </div>
          <Button variant="destructive" onClick={handleSignOut}>Sign Out</Button>
        </CardContent>
      </Card>

      <Card className="bg-card/50 border-border/50">
        <CardHeader>
          <CardTitle>Global Identity</CardTitle>
          <CardDescription>Network-wide naming and presentation config.</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="grid gap-2">
            <Label>Organization Name</Label>
            <Input defaultValue={activeOrg?.name || "NexusCare Pharmacy"} className="bg-background max-w-md" />
          </div>
          <div className="grid gap-2">
            <Label>Operating Region</Label>
            <Input defaultValue="Hyderabad, IN" className="bg-background max-w-md" disabled />
          </div>
          <Button>Save Preferences</Button>
        </CardContent>
      </Card>

      <Card className="bg-card/50 border-border/50">
        <CardHeader>
          <CardTitle className="text-destructive">Danger Zone</CardTitle>
          <CardDescription>Destructive network actions.</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="flex items-center justify-between p-4 border border-destructive/20 bg-destructive/5 rounded-lg">
            <div>
              <h4 className="font-semibold text-sm">Purge Vector Database</h4>
              <p className="text-xs text-muted-foreground mt-1">Erase all ChromaDB embeddings causing complete AI amnesia.</p>
            </div>
            <Button variant="destructive">Factory Purge</Button>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
