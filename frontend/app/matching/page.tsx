"use client";

import { useState, useEffect } from "react";
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
  Wallet,
} from "lucide-react";
import Image from "next/image";

interface Investor {
  id: string;
  name: string;
  investor_type: string;
  preferred_industries: string[];
  preferred_stages: string[];
  preferred_locations: string[];
  min_investment_usd: number;
  max_investment_usd: number;
  profile_summary: string;
  preferred_founder_types: string[];
}

interface Match {
  entity_id: string;
  name: string;
  score: number;
  details: {
    industry: string;
    sub_industries: string[];
    stage: string;
    location: string;
    valuation: string;
    revenue_stage: string;
    business_model: string;
    esg_focus: string;
    exit_strategy: string;
  };
}

export default function MatchingPage() {
  const [investors, setInvestors] = useState<Investor[]>([]);
  const [selectedInvestor, setSelectedInvestor] = useState<string | null>(null);
  const [investorDetails, setInvestorDetails] = useState<Investor | null>(null);
  const [matchingCompanies, setMatchingCompanies] = useState<Match[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [isLoadingMatches, setIsLoadingMatches] = useState(false);

  useEffect(() => {
    const fetchAll = async () => {
      setIsLoading(true);
      try {
        const res = await fetch("http://localhost:8000/matching/all");
        const data = await res.json();
        setInvestors(data.investors);
      } catch (e) {
        console.error("Error fetching all:", e);
      } finally {
        setIsLoading(false);
      }
    };
    fetchAll();
  }, []);

  useEffect(() => {
    if (!selectedInvestor) return;
    setIsLoadingMatches(true);

    const fetchMatches = async () => {
      try {
        const res = await fetch(
          `http://localhost:8000/matching/investor/${selectedInvestor}`
        );
        const data = await res.json();
        setMatchingCompanies(data.matches);
        const inv = investors.find((i) => i.id === selectedInvestor) || null;
        setInvestorDetails(inv);
      } catch (e) {
        console.error("Error fetching matches:", e);
      } finally {
        setIsLoadingMatches(false);
      }
    };
    fetchMatches();
  }, [selectedInvestor]);

  const getMatchQualityBadge = (score: number) => {
    if (score >= 70) {
      return (
        <Badge className="bg-green-500/20 text-green-500">
          Excellent Match
        </Badge>
      );
    } else if (score >= 55) {
      return <Badge className="bg-blue-500/20 text-blue-500">Good Match</Badge>;
    } else {
      return (
        <Badge className="bg-amber-500/20 text-amber-500">
          Potential Match
        </Badge>
      );
    }
  };

  const getInitials = (name: string) => {
    return name?.slice(0, 2).toUpperCase();
  };

  if (isLoading) {
    return (
      <div className="p-8">
        <Skeleton className="h-8 w-64" />
      </div>
    );
  }

  return (
    <div className="container mx-auto py-8 px-4 md:px-6">
      <div className="mb-8">
        <h1 className="text-3xl font-bold">AI Investor Matching</h1>
        <p className="text-muted-foreground">
          Select an investor to see matched startups
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
        <div className="space-y-6">
          <Select
            value={selectedInvestor || ""}
            onValueChange={setSelectedInvestor}
          >
            <SelectTrigger className="w-full">
              <SelectValue placeholder="Choose Investor Profile" />
            </SelectTrigger>
            <SelectContent>
              {investors.map((inv) => (
                <SelectItem key={inv.id} value={inv.id}>
                  {inv.name}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>

          {!selectedInvestor && (
            <Card className="bg-muted/30 border-dashed border">
              <CardContent className="py-6 text-center">
                <p className="text-sm text-muted-foreground">
                  Investor stats will appear here once selected.
                </p>
              </CardContent>
            </Card>
          )}

          {investorDetails && (
            <Card>
              <CardHeader>
                <CardTitle>{investorDetails.name}</CardTitle>
                <CardDescription>
                  {investorDetails.investor_type}
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-2 text-sm">
                <div>
                  <strong>Stages:</strong>{" "}
                  {investorDetails.preferred_stages.join(", ")}
                </div>
                <div>
                  <strong>Industries:</strong>{" "}
                  {investorDetails.preferred_industries.join(", ")}
                </div>
                <div>
                  <strong>Locations:</strong>{" "}
                  {investorDetails.preferred_locations.join(", ")}
                </div>
                <div>
                  <strong>Investment:</strong> $
                  {investorDetails.min_investment_usd / 1_000_000}M - $
                  {investorDetails.max_investment_usd / 1_000_000}M
                </div>
                <div>
                  <strong>Founders:</strong>{" "}
                  {investorDetails.preferred_founder_types.join(", ")}
                </div>
                <div>
                  <strong>Summary:</strong> {investorDetails.profile_summary}
                </div>
              </CardContent>
            </Card>
          )}
        </div>

        <div className="md:col-span-2 space-y-6">
          <h2 className="text-xl font-semibold">Recommended Companies</h2>
          {isLoadingMatches ? (
            <Skeleton className="h-6 w-full" />
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {matchingCompanies.map((match) => (
                <Card key={match.entity_id}>
                  <CardHeader className="flex items-center gap-3">
                    <div className="h-10 w-10 rounded-md bg-primary/20 flex items-center justify-center text-primary font-semibold text-sm">
                      {getInitials(match.name)}
                    </div>
                    <div>
                      <CardTitle>{match.name}</CardTitle>
                      <CardDescription className="text-xs">
                        {match.details.industry} – {match.details.stage} –{" "}
                        {match.details.location}
                      </CardDescription>
                    </div>
                  </CardHeader>
                  <CardContent className="space-y-1 text-sm">
                    <div>
                      <strong>Valuation:</strong> {match.details.valuation}
                    </div>
                    <div>
                      <strong>Revenue:</strong> {match.details.revenue_stage}
                    </div>
                    <div>
                      <strong>Model:</strong> {match.details.business_model}
                    </div>
                    <div>
                      <strong>ESG:</strong> {match.details.esg_focus}
                    </div>
                    <div>
                      <strong>Exit:</strong> {match.details.exit_strategy}
                    </div>
                    <div className="flex flex-wrap gap-2 pt-2">
                      {match.details.sub_industries.map((s, i) => (
                        <Badge key={i} variant="outline" className="text-xs">
                          {s}
                        </Badge>
                      ))}
                    </div>
                  </CardContent>
                  <CardFooter className="flex flex-col gap-2 items-start">
                    <div className="flex justify-between w-full">
                      <span className="text-sm font-semibold">
                        Score: {match.score.toFixed(2)}
                      </span>
                      {getMatchQualityBadge(match.score)}
                    </div>
                    <Button size="sm" className="w-full">
                      Buy Shares
                    </Button>
                  </CardFooter>
                </Card>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
