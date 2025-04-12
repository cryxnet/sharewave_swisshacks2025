"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import {
  Card,
  CardContent,
  CardDescription,
  CardFooter,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Skeleton } from "@/components/ui/skeleton";
import {
  ArrowUpRight,
  Sparkles,
  Users,
  Building2,
  Briefcase,
  TrendingUp,
  Wallet,
} from "lucide-react";
import Image from "next/image";

// Types for the API responses
interface Investor {
  id: string;
  name: string;
  investor_type: string;
  focus_industries: string[];
  investment_stage: string;
  min_investment: number;
  max_investment: number;
  portfolio_size: number;
  location: string;
  description?: string;
}

interface Company {
  id: string;
  name: string;
  industry: string;
  stage: string;
  valuation: number;
  funding_needed: number;
  location: string;
  description?: string;
  logo?: string;
}

interface Match {
  entity_id: string;
  name: string;
  score: number;
  details: {
    industry_match: boolean;
    stage_match: boolean;
    valuation_match: boolean;
    location_match: boolean;
    [key: string]: any;
  };
  // Additional fields from the company data
  industry?: string;
  stage?: string;
  valuation?: number;
  funding_needed?: number;
  location?: string;
  description?: string;
  logo?: string;
}

interface MatchResponse {
  matches: Match[];
  count: number;
  entity_type: string;
  entity_name: string;
}

export default function MatchingPage() {
  const router = useRouter();
  const [investors, setInvestors] = useState<Investor[]>([]);
  const [companies, setCompanies] = useState<Company[]>([]);
  const [selectedInvestor, setSelectedInvestor] = useState<string | null>(null);
  const [investorDetails, setInvestorDetails] = useState<Investor | null>(null);
  const [matchingCompanies, setMatchingCompanies] = useState<Match[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [isLoadingMatches, setIsLoadingMatches] = useState(false);

  // Fetch all companies and investors on page load
  useEffect(() => {
    const fetchAllEntities = async () => {
      setIsLoading(true);
      try {
        // In a real implementation, this would be an API call to the backend
        // const response = await fetch("/api/matching/all")
        // const data = await response.json()

        // Mock data for demonstration
        const mockData = {
          investors: [
            {
              id: "inv-001",
              name: "Sequoia Capital",
              investor_type: "Venture Capital",
              focus_industries: [
                "Technology",
                "Healthcare",
                "Financial Services",
              ],
              investment_stage: "Series A, Series B",
              min_investment: 1000000,
              max_investment: 10000000,
              portfolio_size: 42,
              location: "Silicon Valley, CA",
              description:
                "Leading global investment firm focused on technology and healthcare sectors.",
            },
            {
              id: "inv-002",
              name: "Andreessen Horowitz",
              investor_type: "Venture Capital",
              focus_industries: ["Software", "Fintech", "Crypto"],
              investment_stage: "Seed, Series A",
              min_investment: 500000,
              max_investment: 5000000,
              portfolio_size: 35,
              location: "Menlo Park, CA",
              description:
                "Venture capital firm that backs bold entrepreneurs building the future through technology.",
            },
            {
              id: "inv-003",
              name: "Y Combinator",
              investor_type: "Accelerator",
              focus_industries: ["Technology", "B2B", "Consumer"],
              investment_stage: "Seed",
              min_investment: 125000,
              max_investment: 500000,
              portfolio_size: 120,
              location: "Mountain View, CA",
              description:
                "Seed accelerator providing funding, advice, and network to early-stage startups.",
            },
            {
              id: "inv-004",
              name: "Accel Partners",
              investor_type: "Venture Capital",
              focus_industries: [
                "Enterprise Software",
                "Infrastructure",
                "Consumer",
              ],
              investment_stage: "Series A, Series B",
              min_investment: 2000000,
              max_investment: 15000000,
              portfolio_size: 28,
              location: "Palo Alto, CA",
              description:
                "Global venture capital firm that partners with exceptional founders.",
            },
            {
              id: "inv-005",
              name: "SoftBank Vision Fund",
              investor_type: "Venture Capital",
              focus_industries: ["AI", "Robotics", "Transportation"],
              investment_stage: "Growth, Late Stage",
              min_investment: 100000000,
              max_investment: 1000000000,
              portfolio_size: 15,
              location: "Tokyo, Japan",
              description:
                "The world's largest technology-focused venture capital fund.",
            },
          ],
          companies: [
            {
              id: "comp-001",
              name: "TechVenture Inc.",
              industry: "Technology",
              stage: "Series A",
              valuation: 12500000,
              funding_needed: 3000000,
              location: "San Francisco, CA",
              description:
                "Next-generation AI solutions for enterprise customers",
              logo: "/abstract-letter-t.png",
            },
            {
              id: "comp-002",
              name: "GreenEnergy Solutions",
              industry: "Clean Energy",
              stage: "Seed",
              valuation: 8750000,
              funding_needed: 1500000,
              location: "Austin, TX",
              description:
                "Sustainable energy technology and carbon offset marketplace",
              logo: "/abstract-geometric-g.png",
            },
          ],
        };

        setInvestors(mockData.investors);
        setCompanies(mockData.companies);
      } catch (error) {
        console.error("Error fetching entities:", error);
      } finally {
        setIsLoading(false);
      }
    };

    fetchAllEntities();
  }, []);

  // Fetch matching companies when an investor is selected
  useEffect(() => {
    if (!selectedInvestor) return;

    const fetchMatches = async () => {
      setIsLoadingMatches(true);
      try {
        // In a real implementation, this would be an API call to the backend
        // const response = await fetch(`/api/matching/investor/${selectedInvestor}?limit=5&min_score=0.5`)
        // const data = await response.json()

        // Find the selected investor details
        const investor =
          investors.find((inv) => inv.id === selectedInvestor) || null;
        setInvestorDetails(investor);

        // Mock matching response
        const mockMatches: Match[] = companies.map((company) => {
          // Generate a random score between 1 and 5
          const score = Math.random() * 4 + 1;

          // Determine matches based on investor focus
          const industryMatch =
            investor?.focus_industries.includes(company.industry) || false;
          const stageMatch =
            investor?.investment_stage.includes(company.stage) || false;
          const valuationMatch =
            company.funding_needed >= (investor?.min_investment || 0) &&
            company.funding_needed <= (investor?.max_investment || 0);
          const locationMatch = company.location === investor?.location;

          return {
            entity_id: company.id,
            name: company.name,
            score: Number.parseFloat(score.toFixed(2)),
            details: {
              industry_match: industryMatch,
              stage_match: stageMatch,
              valuation_match: valuationMatch,
              location_match: locationMatch,
            },
            industry: company.industry,
            stage: company.stage,
            valuation: company.valuation,
            funding_needed: company.funding_needed,
            location: company.location,
            description: company.description,
            logo: company.logo,
          };
        });

        // Sort by score descending
        mockMatches.sort((a, b) => b.score - a.score);

        setMatchingCompanies(mockMatches);
      } catch (error) {
        console.error("Error fetching matches:", error);
      } finally {
        setIsLoadingMatches(false);
      }
    };

    fetchMatches();
  }, [selectedInvestor, investors, companies]);

  // Helper function to get match quality badge based on score
  const getMatchQualityBadge = (score: number) => {
    if (score >= 4) {
      return (
        <Badge className="bg-green-500/20 text-green-500 hover:bg-green-500/30">
          Winner Match
        </Badge>
      );
    } else if (score >= 3) {
      return (
        <Badge className="bg-blue-500/20 text-blue-500 hover:bg-blue-500/30">
          Good Match
        </Badge>
      );
    } else {
      return (
        <Badge className="bg-amber-500/20 text-amber-500 hover:bg-amber-500/30">
          Opportunity
        </Badge>
      );
    }
  };

  if (isLoading) {
    return (
      <div className="container mx-auto py-8 px-4 md:px-6">
        <div className="mb-8">
          <Skeleton className="h-10 w-[250px]" />
          <Skeleton className="h-5 w-[350px] mt-2" />
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
          <div className="md:col-span-1 space-y-6">
            <Skeleton className="h-12 w-full" />
            <Skeleton className="h-[300px] w-full rounded-lg" />
          </div>

          <div className="md:col-span-2 space-y-6">
            <Skeleton className="h-8 w-[200px]" />
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <Skeleton className="h-[250px] w-full rounded-lg" />
              <Skeleton className="h-[250px] w-full rounded-lg" />
              <Skeleton className="h-[250px] w-full rounded-lg" />
              <Skeleton className="h-[250px] w-full rounded-lg" />
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="container mx-auto py-8 px-4 md:px-6">
      <div className="mb-8">
        <h1 className="text-3xl font-bold tracking-tight">
          AI Investor Matching
        </h1>
        <p className="text-muted-foreground mt-1">
          Find the perfect investors for your startup using our AI matching
          algorithm
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
        {/* Left Column - Investor Selection */}
        <div className="md:col-span-1 space-y-6">
          <div>
            <label
              htmlFor="investor-select"
              className="block text-sm font-medium mb-2"
            >
              Select Investor Profile
            </label>
            <Select
              value={selectedInvestor || ""}
              onValueChange={(value) => setSelectedInvestor(value)}
            >
              <SelectTrigger id="investor-select" className="w-full">
                <SelectValue placeholder="Choose an investor" />
              </SelectTrigger>
              <SelectContent>
                {investors.map((investor) => (
                  <SelectItem key={investor.id} value={investor.id}>
                    {investor.name}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>

          {investorDetails ? (
            <Card className="border-primary/20">
              <CardHeader className="pb-3">
                <CardTitle className="text-xl">
                  {investorDetails.name}
                </CardTitle>
                <CardDescription>
                  {investorDetails.investor_type}
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="space-y-2">
                  <div className="flex items-center gap-2 text-sm">
                    <Briefcase className="h-4 w-4 text-muted-foreground" />
                    <span className="text-muted-foreground">
                      Investment Stage:
                    </span>
                    <span className="font-medium">
                      {investorDetails.investment_stage}
                    </span>
                  </div>

                  <div className="flex items-center gap-2 text-sm">
                    <Building2 className="h-4 w-4 text-muted-foreground" />
                    <span className="text-muted-foreground">
                      Focus Industries:
                    </span>
                    <div className="flex flex-wrap gap-1">
                      {investorDetails.focus_industries.map(
                        (industry, index) => (
                          <Badge
                            key={index}
                            variant="outline"
                            className="text-xs"
                          >
                            {industry}
                          </Badge>
                        )
                      )}
                    </div>
                  </div>

                  <div className="flex items-center gap-2 text-sm">
                    <Wallet className="h-4 w-4 text-muted-foreground" />
                    <span className="text-muted-foreground">
                      Investment Range:
                    </span>
                    <span className="font-medium">
                      ${(investorDetails.min_investment / 1000000).toFixed(1)}M
                      - ${(investorDetails.max_investment / 1000000).toFixed(1)}
                      M
                    </span>
                  </div>

                  <div className="flex items-center gap-2 text-sm">
                    <Users className="h-4 w-4 text-muted-foreground" />
                    <span className="text-muted-foreground">
                      Portfolio Size:
                    </span>
                    <span className="font-medium">
                      {investorDetails.portfolio_size} companies
                    </span>
                  </div>
                </div>

                <div className="pt-2 border-t border-border/50">
                  <p className="text-sm">{investorDetails.description}</p>
                </div>
              </CardContent>
              <CardFooter>
                <Button variant="outline" size="sm" className="w-full">
                  View Full Profile
                </Button>
              </CardFooter>
            </Card>
          ) : (
            <Card className="border-dashed border-border/50 bg-muted/30">
              <CardContent className="flex flex-col items-center justify-center py-12">
                <div className="h-16 w-16 rounded-full bg-primary/10 flex items-center justify-center mb-4">
                  <Users className="h-8 w-8 text-primary" />
                </div>
                <h3 className="text-lg font-medium mb-2">Select an Investor</h3>
                <p className="text-sm text-muted-foreground text-center">
                  Choose an investor profile to see matching companies
                </p>
              </CardContent>
            </Card>
          )}
        </div>

        {/* Right Column - Matching Companies */}
        <div className="md:col-span-2">
          <div className="flex items-center justify-between mb-6">
            <h2 className="text-xl font-bold flex items-center gap-2">
              <Sparkles className="h-5 w-5 text-primary" />
              Recommended Companies
            </h2>

            {selectedInvestor && (
              <Badge variant="outline" className="text-sm">
                {matchingCompanies.length} matches found
              </Badge>
            )}
          </div>

          {isLoadingMatches ? (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <Skeleton className="h-[250px] w-full rounded-lg" />
              <Skeleton className="h-[250px] w-full rounded-lg" />
              <Skeleton className="h-[250px] w-full rounded-lg" />
              <Skeleton className="h-[250px] w-full rounded-lg" />
            </div>
          ) : selectedInvestor ? (
            matchingCompanies.length > 0 ? (
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                {matchingCompanies.map((match) => (
                  <Card
                    key={match.entity_id}
                    className="h-full overflow-hidden transition-all duration-200 hover:shadow-lg hover:shadow-primary/20 hover:border-primary/50 cursor-pointer group"
                  >
                    <CardHeader className="pb-3">
                      <div className="flex items-start justify-between">
                        <div className="flex items-center gap-3">
                          <div className="relative h-12 w-12 rounded-md overflow-hidden bg-gradient-to-br from-blue-500 to-cyan-400 flex items-center justify-center">
                            <Image
                              src={
                                match.logo ||
                                "/placeholder.svg?height=48&width=48"
                              }
                              alt={match.name}
                              width={48}
                              height={48}
                              className="object-cover"
                            />
                          </div>
                          <div>
                            <CardTitle className="text-lg">
                              {match.name}
                            </CardTitle>
                            <CardDescription className="flex items-center gap-2">
                              {match.industry}
                              <span className="inline-block h-1 w-1 rounded-full bg-muted-foreground"></span>
                              {match.stage}
                            </CardDescription>
                          </div>
                        </div>
                        <div className="flex flex-col items-end">
                          {getMatchQualityBadge(match.score)}
                          <span className="text-sm font-medium mt-1">
                            Score: {match.score}
                          </span>
                        </div>
                      </div>
                    </CardHeader>
                    <CardContent className="pb-3">
                      <p className="text-sm text-muted-foreground line-clamp-2 mb-4">
                        {match.description || "No description available."}
                      </p>

                      <div className="grid grid-cols-2 gap-4 text-sm">
                        <div>
                          <p className="text-muted-foreground">Valuation</p>
                          <p className="font-medium">
                            ${(match.valuation! / 1000000).toFixed(1)}M
                          </p>
                        </div>
                        <div>
                          <p className="text-muted-foreground">
                            Funding Needed
                          </p>
                          <p className="font-medium">
                            ${(match.funding_needed! / 1000000).toFixed(1)}M
                          </p>
                        </div>
                      </div>
                    </CardContent>
                    <CardFooter className="pt-0">
                      <div className="w-full space-y-2">
                        <div className="flex flex-wrap gap-1">
                          {match.details.industry_match && (
                            <Badge
                              variant="outline"
                              className="text-xs bg-green-500/10 text-green-500 border-green-500/20"
                            >
                              Industry Match
                            </Badge>
                          )}
                          {match.details.stage_match && (
                            <Badge
                              variant="outline"
                              className="text-xs bg-green-500/10 text-green-500 border-green-500/20"
                            >
                              Stage Match
                            </Badge>
                          )}
                          {match.details.valuation_match && (
                            <Badge
                              variant="outline"
                              className="text-xs bg-green-500/10 text-green-500 border-green-500/20"
                            >
                              Investment Range Match
                            </Badge>
                          )}
                          {match.details.location_match && (
                            <Badge
                              variant="outline"
                              className="text-xs bg-green-500/10 text-green-500 border-green-500/20"
                            >
                              Location Match
                            </Badge>
                          )}
                        </div>

                        <Button
                          variant="ghost"
                          size="sm"
                          className="w-full group-hover:bg-primary/10 group-hover:text-primary"
                        >
                          View Company
                          <ArrowUpRight className="ml-2 h-4 w-4 transition-transform group-hover:translate-x-1 group-hover:-translate-y-1" />
                        </Button>
                      </div>
                    </CardFooter>
                  </Card>
                ))}
              </div>
            ) : (
              <div className="flex flex-col items-center justify-center py-12 border rounded-lg border-dashed">
                <div className="h-16 w-16 rounded-full bg-muted/50 flex items-center justify-center mb-4">
                  <TrendingUp className="h-8 w-8 text-muted-foreground" />
                </div>
                <h3 className="text-lg font-medium mb-2">No Matches Found</h3>
                <p className="text-sm text-muted-foreground text-center max-w-md">
                  We couldn't find any companies that match this investor's
                  criteria. Try selecting a different investor.
                </p>
              </div>
            )
          ) : (
            <div className="flex flex-col items-center justify-center py-12 border rounded-lg border-dashed">
              <div className="h-16 w-16 rounded-full bg-primary/10 flex items-center justify-center mb-4">
                <Sparkles className="h-8 w-8 text-primary" />
              </div>
              <h3 className="text-lg font-medium mb-2">AI Matching Engine</h3>
              <p className="text-sm text-muted-foreground text-center max-w-md">
                Select an investor from the dropdown to see AI-recommended
                companies based on investment preferences, industry focus, and
                more.
              </p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
