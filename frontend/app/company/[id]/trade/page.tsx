"use client";

import { useState, useEffect } from "react";
import { useParams, useRouter } from "next/navigation";
import { Button } from "@/components/ui/button";
import { Skeleton } from "@/components/ui/skeleton";
import { useToast } from "@/hooks/use-toast";
import { AlertCircle, ArrowLeft, ChevronRight } from "lucide-react";
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";
import TradingInterface from "@/components/trading-interface";

interface Company {
  id: string;
  name: string;
  symbol: string;
  total_supply: number;
  total_valuation_usd: number;
  liquidity_percent: number;
  issuing_address: string;
  state: string;
}

interface Stats {
  price_per_token_usd: number;
  market_cap_usd: number;
  liquidity_usd: number;
  liquidity_token_amount: number;
}

interface CompanyData {
  company: Company;
  stats: Stats;
  [key: string]: any;
}

export default function TradePage() {
  const params = useParams();
  const router = useRouter();
  const { toast } = useToast();
  const companyId = params.id as string;

  const [companyData, setCompanyData] = useState<CompanyData | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  // Fetch company data
  useEffect(() => {
    const fetchCompanyData = async () => {
      setIsLoading(true);
      try {
        const response = await fetch(
          `http://localhost:8000/companies/${companyId}/full_info`
        );
        if (!response.ok) throw new Error("Failed to fetch company data");
        const data = await response.json();
        setCompanyData(data);
      } catch (error) {
        console.error("Error fetching company:", error);
        toast({
          title: "Error",
          description: "Failed to load company data",
          variant: "destructive",
        });
      } finally {
        setIsLoading(false);
      }
    };

    fetchCompanyData();
  }, [companyId, toast]);

  if (isLoading) {
    return (
      <div className="container mx-auto py-8 px-4 md:px-6">
        <div className="space-y-6">
          <div className="flex items-center justify-between">
            <Skeleton className="h-10 w-[250px]" />
            <Skeleton className="h-10 w-[120px]" />
          </div>
          <Skeleton className="h-[300px] w-full" />
          <div className="grid gap-6 lg:grid-cols-3">
            <Skeleton className="h-[200px] w-full lg:col-span-2" />
            <Skeleton className="h-[200px] w-full" />
          </div>
        </div>
      </div>
    );
  }

  if (
    !companyData ||
    !companyData.company ||
    companyData.company.state !== "distributed"
  ) {
    return (
      <div className="container mx-auto py-8 px-4 md:px-6">
        <Alert variant="destructive">
          <AlertCircle className="h-4 w-4" />
          <AlertTitle>Trading Not Available</AlertTitle>
          <AlertDescription>
            Trading is only available for distributed companies.
            <Button
              variant="link"
              className="p-0 h-auto font-normal"
              onClick={() => router.push(`/company/${companyId}`)}
            >
              Return to company details
            </Button>
          </AlertDescription>
        </Alert>
      </div>
    );
  }

  const { company, stats } = companyData;

  return (
    <div className="container mx-auto py-8 px-4 md:px-6">
      <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4 mb-6">
        <div>
          <div className="flex items-center gap-2 text-sm text-muted-foreground mb-1">
            <Button
              variant="link"
              className="p-0 h-auto text-muted-foreground hover:text-primary"
              onClick={() => router.push("/")}
            >
              Marketplace
            </Button>
            <ChevronRight className="h-4 w-4" />
            <Button
              variant="link"
              className="p-0 h-auto text-muted-foreground hover:text-primary"
              onClick={() => router.push(`/company/${companyId}`)}
            >
              Company Details
            </Button>
            <ChevronRight className="h-4 w-4" />
            <span>Trade</span>
          </div>
          <h1 className="text-3xl font-bold tracking-tight">
            Trade {company.name} ({company.symbol})
          </h1>
        </div>

        <Button
          variant="outline"
          size="sm"
          onClick={() => router.push(`/company/${companyId}`)}
          className="flex items-center gap-1"
        >
          <ArrowLeft className="h-4 w-4" />
          Back to Company
        </Button>
      </div>

      <TradingInterface
        companyName={company.name}
        symbol={company.symbol}
        currentPrice={stats.price_per_token_usd}
      />
    </div>
  );
}
