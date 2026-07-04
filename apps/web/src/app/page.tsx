import Link from "next/link";
import { Button } from "@/components/ui/button";
import { Activity, Stethoscope, ArrowRight } from "lucide-react";
import * as motion from "framer-motion/client";

export default function LandingPage() {
  return (
    <div className="min-h-screen flex flex-col items-center justify-center relative overflow-hidden bg-background">
      {/* Dynamic Background */}
      <div className="absolute top-0 w-full h-screen bg-[radial-gradient(ellipse_at_top,_var(--tw-gradient-stops))] from-blue-900/20 via-background to-background -z-10" />
      
      <div className="container px-4 md:px-6">
        <div className="flex flex-col items-center space-y-8 text-center">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5 }}
            className="flex items-center space-x-2 bg-muted/50 rounded-full px-4 py-1.5 border border-border/50"
          >
            <span className="flex h-2 w-2 rounded-full bg-primary animate-pulse" />
            <span className="text-sm font-medium text-muted-foreground">NexusCare MVP Network Active</span>
          </motion.div>

          <motion.div
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: 0.1 }}
            className="space-y-4 max-w-4xl"
          >
            <h1 className="text-5xl md:text-7xl font-bold tracking-tighter">
              The AI Operating System for{" "}
              <span className="text-transparent bg-clip-text bg-gradient-to-r from-blue-400 to-primary">
                Pharmacy Networks.
              </span>
            </h1>
            <p className="mx-auto max-w-[700px] text-muted-foreground md:text-xl leading-relaxed">
              Automate localized supply chains, manage cross-branch expiry risks, and interact with a unified AI Digital Workforce.
            </p>
          </motion.div>

          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: 0.2 }}
            className="flex space-x-4"
          >
            <Link href="/login">
              <Button size="lg" className="h-12 px-8 font-medium group">
                Enter Network
                <ArrowRight className="ml-2 w-4 h-4 group-hover:translate-x-1 transition-transform" />
              </Button>
            </Link>
            <Link href="/dashboard/knowledge">
              <Button size="lg" variant="outline" className="h-12 px-8">
                Documentation
              </Button>
            </Link>
          </motion.div>
        </div>
      </div>
    </div>
  );
}
