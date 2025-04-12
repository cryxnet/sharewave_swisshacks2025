import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Badge } from "@/components/ui/badge"
import { ArrowUpRight, Search, SlidersHorizontal } from "lucide-react"
import Link from "next/link"
import Image from "next/image"

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
    logo: "/placeholder.svg?height=80&width=80&query=M",
  },
]

export default function MarketplacePage() {
  return (
    <div className="container mx-auto py-8 px-4 md:px-6">
      <div className="flex flex-col space-y-4 md:space-y-0 md:flex-row md:items-center md:justify-between mb-8">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Marketplace</h1>
          <p className="text-muted-foreground mt-1">Discover and invest in tokenized companies on the XRP Ledger</p>
        </div>
        <div className="flex flex-col sm:flex-row gap-4">
          <div className="relative">
            <Search className="absolute left-2.5 top-2.5 h-4 w-4 text-muted-foreground" />
            <Input type="search" placeholder="Search opportunities..." className="pl-8 w-full sm:w-[250px]" />
          </div>
          <div className="flex items-center gap-2">
            <Select defaultValue="newest">
              <SelectTrigger className="w-full sm:w-[180px]">
                <SelectValue placeholder="Sort by" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="newest">Newest First</SelectItem>
                <SelectItem value="valuation-high">Highest Valuation</SelectItem>
                <SelectItem value="valuation-low">Lowest Valuation</SelectItem>
                <SelectItem value="liquidity-high">Highest Liquidity</SelectItem>
              </SelectContent>
            </Select>
            <Button variant="outline" size="icon">
              <SlidersHorizontal className="h-4 w-4" />
            </Button>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {opportunities.map((opportunity) => (
          <Link href={`/company/${opportunity.id}`} key={opportunity.id}>
            <Card className="h-full overflow-hidden transition-all duration-200 hover:shadow-lg hover:shadow-primary/20 hover:border-primary/50 cursor-pointer group">
              <CardHeader className="pb-4">
                <div className="flex items-start justify-between">
                  <div className="flex items-center gap-3">
                    <div className="relative h-12 w-12 rounded-md overflow-hidden bg-gradient-to-br from-blue-500 to-cyan-400 flex items-center justify-center">
                      <Image
                        src={opportunity.logo || "/placeholder.svg"}
                        alt={opportunity.name}
                        width={48}
                        height={48}
                        className="object-cover"
                      />
                    </div>
                    <div>
                      <CardTitle className="text-lg flex items-center gap-1">
                        {opportunity.name}
                        <Badge variant="outline" className="ml-2 text-xs font-normal">
                          {opportunity.symbol}
                        </Badge>
                      </CardTitle>
                      <CardDescription className="line-clamp-1 mt-1">{opportunity.description}</CardDescription>
                    </div>
                  </div>
                </div>
              </CardHeader>
              <CardContent className="pb-4">
                <div className="grid grid-cols-3 gap-4 text-sm">
                  <div>
                    <p className="text-muted-foreground">Valuation</p>
                    <p className="font-medium">${(opportunity.valuation / 1000000).toFixed(1)}M</p>
                  </div>
                  <div>
                    <p className="text-muted-foreground">Supply</p>
                    <p className="font-medium">{(opportunity.tokenSupply / 1000000).toFixed(1)}M</p>
                  </div>
                  <div>
                    <p className="text-muted-foreground">Liquidity</p>
                    <p className="font-medium">{opportunity.liquidityPercent}%</p>
                  </div>
                </div>
              </CardContent>
              <CardFooter className="pt-0">
                <Button variant="ghost" size="sm" className="w-full group-hover:bg-primary/10 group-hover:text-primary">
                  View Details
                  <ArrowUpRight className="ml-2 h-4 w-4 transition-transform group-hover:translate-x-1 group-hover:-translate-y-1" />
                </Button>
              </CardFooter>
            </Card>
          </Link>
        ))}
      </div>
    </div>
  )
}
