"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { cn } from "@/lib/utils";
import { Button } from "@/components/ui/button";
import { Wallet, BarChart3, PlusCircle, Home } from "lucide-react";
import Image from "next/image";

export default function Navbar() {
  const pathname = usePathname();

  const routes = [
    {
      href: "/",
      label: "Marketplace",
      icon: <Home className="mr-2 h-4 w-4" />,
      active: pathname === "/",
    },
    {
      href: "/register",
      label: "Register Company",
      icon: <PlusCircle className="mr-2 h-4 w-4" />,
      active: pathname === "/register",
    },
    {
      href: "/dashboard",
      label: "Dashboard",
      icon: <BarChart3 className="mr-2 h-4 w-4" />,
      active: pathname.includes("/dashboard") || pathname.includes("/company"),
    },
  ];

  return (
    <nav className="border-b border-border/40 bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
      <div className="flex h-16 items-center px-4 md:px-8">
        <Link href="/" className="flex items-center gap-2 mr-8">
          <Image
            src="logo.png"
            alt="Logo"
            width={32}
            height={32}
            className="h-8 w-8"
          />
          <span className="font-bold text-xl bg-gradient-to-r from-blue-400 to-cyan-300 bg-clip-text text-transparent">
            XRPL Finance
          </span>
        </Link>

        <div className="hidden md:flex items-center space-x-1">
          {routes.map((route) => (
            <Link
              key={route.href}
              href={route.href}
              className={cn(
                "px-4 py-2 rounded-md text-sm font-medium transition-colors flex items-center",
                route.active
                  ? "bg-primary/10 text-primary"
                  : "text-muted-foreground hover:text-primary hover:bg-primary/10"
              )}
            >
              {route.icon}
              {route.label}
            </Link>
          ))}
        </div>

        <div className="ml-auto flex items-center gap-2">
          <Button
            size="sm"
            className="bg-gradient-to-r from-blue-600 to-cyan-500 hover:from-blue-700 hover:to-cyan-600"
          >
            rMC...cwE
          </Button>
        </div>
      </div>
    </nav>
  );
}
