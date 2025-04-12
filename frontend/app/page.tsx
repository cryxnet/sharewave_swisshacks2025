import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardFooter,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Badge } from "@/components/ui/badge";
import {
  ArrowRight,
  ArrowUpRight,
  ChevronRight,
  Search,
  SlidersHorizontal,
  Wallet,
  BarChart3,
  TrendingUp,
} from "lucide-react";
import Link from "next/link";
import Image from "next/image";

// Mock data for marketplace opportunities
const opportunities = [
  {
    id: "1",
    name: "TechVenture Inc.",
    symbol: "TECH",
    description: "Next-generation AI solutions for enterprise customers",
    valuation: 12500000,
    tokenSupply: 10000000,
    liquidityPercent: 15,
    logo: "/abstract-letter-t.png",
  },
  {
    id: "2",
    name: "GreenEnergy Solutions",
    symbol: "GREEN",
    description: "Sustainable energy technology and carbon offset marketplace",
    valuation: 8750000,
    tokenSupply: 5000000,
    liquidityPercent: 20,
    logo: "/abstract-geometric-g.png",
  },
  {
    id: "3",
    name: "HealthTech Innovations",
    symbol: "HLTH",
    description: "Revolutionary healthcare data management and analytics",
    valuation: 15000000,
    tokenSupply: 7500000,
    liquidityPercent: 12,
    logo: "/abstract-letter-h.png",
  },
  {
    id: "4",
    name: "FinBlock Solutions",
    symbol: "FBS",
    description: "Decentralized financial infrastructure for global markets",
    valuation: 20000000,
    tokenSupply: 12000000,
    liquidityPercent: 18,
    logo: "/abstract-letter-f.png",
  },
  {
    id: "5",
    name: "LogisticChain",
    symbol: "LOGX",
    description: "Blockchain-based supply chain management and tracking",
    valuation: 6500000,
    tokenSupply: 8000000,
    liquidityPercent: 25,
    logo: "/Abstract Letter L.png",
  },
  {
    id: "6",
    name: "MetaVerse Realms",
    symbol: "MVR",
    description: "Virtual reality experiences and digital asset marketplace",
    valuation: 18000000,
    tokenSupply: 20000000,
    liquidityPercent: 22,
    logo: "/abstract-letter-f.png",
  },
];

export default function MarketplacePage() {
  return (
    <div className="container mx-auto px-4 md:px-6">
      {/* Hero Banner */}
      <div className="relative overflow-hidden rounded-2xl mb-12 mt-8">
        <div className="absolute inset-0 bg-gradient-to-r from-blue-600/90 to-cyan-500/90 z-10"></div>
        <div className="absolute inset-0 bg-[url('/interconnected-nodes.png')] bg-cover bg-center opacity-40 mix-blend-overlay"></div>

        <div className="relative z-20 px-6 py-16 md:py-24 md:px-12 flex flex-col md:flex-row items-center">
          <div className="md:w-2/3 mb-8 md:mb-0 md:pr-8">
            <h1 className="text-4xl md:text-5xl font-bold text-white mb-4 leading-tight">
              Tokenize Your Company <br />
              on the Blockchain
            </h1>
            <p className="text-lg md:text-xl text-white/90 mb-6 max-w-2xl">
              Access global liquidity, enable fractional ownership and create
              new opportunities for investors with our tokenization platform.
            </p>
            <div className="flex flex-col sm:flex-row gap-4">
              <Button
                size="lg"
                className="bg-white text-blue-600 hover:bg-white/90 font-medium"
                asChild
              >
                <Link href="/register">
                  <Wallet className="mr-2 h-5 w-5" />
                  Register Your Company
                </Link>
              </Button>
              <Button
                variant="outline"
                size="lg"
                className="border-white text-white hover:bg-white/10"
                asChild
              >
                <Link href="/dashboard">
                  <BarChart3 className="mr-2 h-5 w-5" />
                  View Dashboard
                </Link>
              </Button>
            </div>
          </div>

          <div className="md:w-1/3 flex justify-center">
            <div className="relative w-64 h-64 md:w-80 md:h-80">
              <div className="absolute inset-0 bg-white/10 backdrop-blur-sm rounded-2xl border border-white/20 shadow-xl"></div>
              <div className="absolute inset-0 flex items-center justify-center p-8">
                <div className="w-full h-full relative">
                  <div className="absolute top-0 left-0 w-16 h-16 bg-blue-500/30 rounded-full flex items-center justify-center">
                    <TrendingUp className="h-8 w-8 text-white" />
                  </div>
                  <div className="absolute bottom-0 right-0 w-20 h-20 bg-cyan-500/30 rounded-full flex items-center justify-center">
                    <Wallet className="h-10 w-10 text-white" />
                  </div>
                  <div className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 w-24 h-24 bg-white/20 rounded-full flex items-center justify-center">
                    <div className="h-16 w-16 rounded-full flex items-center justify-center">
                      <Image
                        src="/logo.png"
                        alt="XRP Logo"
                        width={60}
                        height={60}
                        className="object-contain"
                      />
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Stats Bar */}
        <div className="relative z-20 bg-white/10 backdrop-blur-md border-t border-white/20">
          <div className="grid grid-cols-2 md:grid-cols-4 divide-x divide-white/20">
            <div className="p-4 md:p-6 text-center">
              <p className="text-white/70 text-sm">Companies</p>
              <p className="text-white text-2xl font-bold">120+</p>
            </div>
            <div className="p-4 md:p-6 text-center">
              <p className="text-white/70 text-sm">Total Value Locked</p>
              <p className="text-white text-2xl font-bold">$48.5M</p>
            </div>
            <div className="p-4 md:p-6 text-center">
              <p className="text-white/70 text-sm">Investors</p>
              <p className="text-white text-2xl font-bold">3,500+</p>
            </div>
            <div className="p-4 md:p-6 text-center">
              <p className="text-white/70 text-sm">Trading Volume</p>
              <p className="text-white text-2xl font-bold">$12.8M</p>
            </div>
          </div>
        </div>
      </div>

      <div className="flex flex-col space-y-4 md:space-y-0 md:flex-row md:items-center md:justify-between mb-8">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">
            Discover Markets
          </h1>
          <p className="text-muted-foreground mt-1">
            Opening private markets to everyone.
          </p>
        </div>
        <div className="flex flex-col sm:flex-row gap-4">
          <div className="relative">
            <Search className="absolute left-2.5 top-2.5 h-4 w-4 text-muted-foreground" />
            <Input
              type="search"
              placeholder="Search opportunities..."
              className="pl-8 w-full sm:w-[250px]"
            />
          </div>
          <div className="flex items-center gap-2">
            <Select defaultValue="newest">
              <SelectTrigger className="w-full sm:w-[180px]">
                <SelectValue placeholder="Sort by" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="newest">Newest First</SelectItem>
                <SelectItem value="valuation-high">
                  Highest Valuation
                </SelectItem>
                <SelectItem value="valuation-low">Lowest Valuation</SelectItem>
                <SelectItem value="liquidity-high">
                  Highest Liquidity
                </SelectItem>
              </SelectContent>
            </Select>
            <Button variant="outline" size="icon">
              <SlidersHorizontal className="h-4 w-4" />
            </Button>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mb-12">
        {opportunities.map((opportunity) => (
          <Link href={`/company/${opportunity.id}`} key={opportunity.id}>
            <Card className="h-full overflow-hidden transition-all duration-200 hover:shadow-lg hover:shadow-primary/20 hover:border-primary/50 cursor-pointer group">
              <CardHeader className="pb-4">
                <div className="flex items-start justify-between">
                  <div className="flex items-center gap-3">
                    <div className="relative h-12 w-12 rounded-md overflow-hidden bg-gradient-to-br from-blue-500 to-cyan-400">
                      <Image
                        src={opportunity.logo || "/placeholder.svg"}
                        alt={opportunity.name}
                        fill
                        className="object-cover"
                      />
                    </div>
                    <div>
                      <CardTitle className="text-lg flex items-center gap-1">
                        {opportunity.name}
                        <Badge
                          variant="outline"
                          className="ml-2 text-xs font-normal"
                        >
                          {opportunity.symbol}
                        </Badge>
                        <span className="ml-1 inline-flex h-4 w-4 items-center justify-center rounded-full bg-blue-500 text-white text-[10px] font-bold">
                          ✓
                        </span>
                      </CardTitle>
                      <CardDescription className="line-clamp-1 mt-1">
                        {opportunity.description}
                      </CardDescription>
                    </div>
                  </div>
                </div>
              </CardHeader>
              <CardContent className="pb-4">
                <div className="grid grid-cols-3 gap-4 text-sm">
                  <div>
                    <p className="text-muted-foreground">Valuation</p>
                    <p className="font-medium">
                      ${(opportunity.valuation / 1000000).toFixed(1)}M
                    </p>
                  </div>
                  <div>
                    <p className="text-muted-foreground">Supply</p>
                    <p className="font-medium">
                      {(opportunity.tokenSupply / 1000000).toFixed(1)}M
                    </p>
                  </div>
                  <div>
                    <p className="text-muted-foreground">Liquidity</p>
                    <p className="font-medium">
                      {opportunity.liquidityPercent}%
                    </p>
                  </div>
                </div>
              </CardContent>
              <CardFooter className="pt-0">
                <Button
                  variant="ghost"
                  size="sm"
                  className="w-full group-hover:bg-primary/10 group-hover:text-primary"
                >
                  View Details
                  <ArrowUpRight className="ml-2 h-4 w-4 transition-transform group-hover:translate-x-1 group-hover:-translate-y-1" />
                </Button>
              </CardFooter>
            </Card>
          </Link>
        ))}
      </div>

      {/* Featured Section */}
      <div className="mb-12 rounded-xl overflow-hidden border bg-card/50">
        <div className="grid md:grid-cols-2">
          <div className="p-8 md:p-12 flex flex-col justify-center">
            <h2 className="text-2xl md:text-3xl font-bold mb-4">
              Ready to tokenize your company?
            </h2>
            <p className="text-muted-foreground mb-6">
              Join the growing number of companies leveraging blockchain
              technology to access global liquidity and enable fractional
              ownership.
            </p>
            <div className="space-y-4">
              <div className="flex items-start gap-3">
                <div className="h-6 w-6 rounded-full bg-blue-500/20 flex items-center justify-center mt-0.5">
                  <ChevronRight className="h-4 w-4 text-blue-500" />
                </div>
                <div>
                  <p className="font-medium">Simplified Onboarding</p>
                  <p className="text-sm text-muted-foreground">
                    Quick and easy registration process
                  </p>
                </div>
              </div>
              <div className="flex items-start gap-3">
                <div className="h-6 w-6 rounded-full bg-blue-500/20 flex items-center justify-center mt-0.5">
                  <ChevronRight className="h-4 w-4 text-blue-500" />
                </div>
                <div>
                  <p className="font-medium">Automated Market Making</p>
                  <p className="text-sm text-muted-foreground">
                    Built-in liquidity through XRP Ledger AMM
                  </p>
                </div>
              </div>
              <div className="flex items-start gap-3">
                <div className="h-6 w-6 rounded-full bg-blue-500/20 flex items-center justify-center mt-0.5">
                  <ChevronRight className="h-4 w-4 text-blue-500" />
                </div>
                <div>
                  <p className="font-medium">Global Investor Access</p>
                  <p className="text-sm text-muted-foreground">
                    Connect with investors worldwide
                  </p>
                </div>
              </div>
            </div>
            <div className="mt-8">
              <Button
                asChild
                className="bg-gradient-to-r from-blue-600 to-cyan-500 hover:from-blue-700 hover:to-cyan-600"
              >
                <Link href="/register">
                  Get Started
                  <ArrowRight className="ml-2 h-4 w-4" />
                </Link>
              </Button>
            </div>
          </div>
          <div className="relative hidden md:block">
            <div className="absolute inset-0 bg-gradient-to-br from-blue-600/90 to-cyan-500/90"></div>
            <div className="absolute inset-0 bg-[url('/collaborative-strategy-session.png')] bg-cover bg-center opacity-40 mix-blend-overlay"></div>
            <div className="relative h-full flex items-center justify-center p-12">
              <div className="bg-white/10 backdrop-blur-sm rounded-xl border border-white/20 p-8 max-w-md">
                <h3 className="text-2xl font-bold text-white mb-4">
                  Success Stories
                </h3>
                <div className="space-y-4">
                  <div className="flex items-center gap-3">
                    <div className="h-10 w-10 rounded-full bg-white/20 flex items-center justify-center">
                      <Image
                        src="/abstract-letter-t.png"
                        alt="TechVenture"
                        width={24}
                        height={24}
                        className="object-contain"
                      />
                    </div>
                    <div>
                      <p className="font-medium text-white">TechVenture Inc.</p>
                      <p className="text-sm text-white/80">
                        Raised $12.5M through tokenization
                      </p>
                    </div>
                  </div>
                  <div className="flex items-center gap-3">
                    <div className="h-10 w-10 rounded-full bg-white/20 flex items-center justify-center">
                      <Image
                        src="/abstract-geometric-g.png"
                        alt="GreenEnergy"
                        width={24}
                        height={24}
                        className="object-contain"
                      />
                    </div>
                    <div>
                      <p className="font-medium text-white">
                        GreenEnergy Solutions
                      </p>
                      <p className="text-sm text-white/80">
                        Expanded to 3 new markets after tokenizing
                      </p>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
