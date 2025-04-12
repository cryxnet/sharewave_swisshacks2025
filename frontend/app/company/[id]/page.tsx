"use client";

import { useState, useEffect } from "react";
import { useParams, useRouter } from "next/navigation";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Badge } from "@/components/ui/badge";
import { Skeleton } from "@/components/ui/skeleton";
import { useToast } from "@/hooks/use-toast";
import {
  AlertCircle,
  ArrowRight,
  CheckCircle2,
  ChevronRight,
  Clock,
  Coins,
  DollarSign,
  ExternalLink,
  Percent,
  RefreshCw,
} from "lucide-react";
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";
import ShareholderTable from "@/components/shareholder-table";
import TokenHoldingsChart from "@/components/token-holdings-chart";
import CompanyOverview from "@/components/company-overview";
import StakeholderFundingStatus from "@/components/stakeholder-funding-status";

// Updated interfaces to match the new API response
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

interface Stakeholder {
  wallet_address: string;
  required_rlusd: number;
  has_paid: boolean;
  has_trustline: boolean;
  tokens_distributed: boolean;
  status: string;
}

interface TokenHolder {
  wallet_address: string;
  balance: number;
}

interface AMMInfo {
  amm: {
    account: string;
    amount: {
      currency: string;
      issuer: string;
      value: string;
    };
    amount2: {
      currency: string;
      issuer: string;
      value: string;
    };
    trading_fee: number;
    [key: string]: any;
  };
  [key: string]: any;
}

interface CompanyFullInfo {
  company: Company;
  stats: Stats;
  stakeholders: Stakeholder[];
  token_holders: TokenHolder[];
  amm_info: AMMInfo;
}

export default function CompanyDetailPage() {
  const params = useParams();
  const router = useRouter();
  const { toast } = useToast();
  const companyId = params.id as string;

  const [companyData, setCompanyData] = useState<CompanyFullInfo | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isCheck, setIsCheck] = useState(false);
  const [isDistributing, setIsDistributing] = useState(false);
  const [refreshKey, setRefreshKey] = useState(0);
  const [activeTab, setActiveTab] = useState("stakeholders");

  // Fetch company data from the new endpoint
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

        // Set default tab based on company state
        if (data.company.state === "waiting_funds") {
          setActiveTab("stakeholders");
        } else {
          setActiveTab("overview");
        }
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
  }, [companyId, toast, refreshKey]);

  // Handle distribution action
  const handleDistribute = async () => {
    setIsDistributing(true);
    try {
      const response = await fetch(
        `http://localhost:8000/companies/${companyId}/check_and_distribute`,
        {
          method: "POST",
        }
      );

      const result = await response.json();

      if (!response.ok) {
        throw new Error(result.message || "Distribution failed");
      }

      toast({
        title: "Success",
        description: result.message || "Distribution completed successfully",
      });

      // Refresh data after distribution
      setRefreshKey((prev) => prev + 1);
    } catch (error) {
      console.error("Distribution error:", error);
      toast({
        title: "Distribution Failed",
        description:
          error instanceof Error
            ? error.message
            : "An unexpected error occurred",
        variant: "destructive",
      });
    } finally {
      setIsDistributing(false);
    }
  };

  // Refresh data
  const handleRefresh = () => {
    setRefreshKey((prev) => prev + 1);
  };

  const handleCheckOnly = async () => {
    setIsCheck(true);
    try {
      const response = await fetch(
        `http://localhost:8000/companies/${companyId}/check_stakeholders`,
        {
          method: "POST",
        }
      );

      const result = await response.json();

      if (!response.ok) {
        throw new Error(result.message || "Stakeholder check failed");
      }

      toast({
        title: "Check Complete",
        description: result.message || "All stakeholders are ready.",
      });

      setRefreshKey((prev) => prev + 1);
    } catch (error) {
      console.error("Check error:", error);
      toast({
        title: "Check Failed",
        description:
          error instanceof Error
            ? error.message
            : "An unexpected error occurred",
        variant: "destructive",
      });
    } finally {
      setIsCheck(false);
    }
  };

  if (isLoading) {
    return (
      <div className="container mx-auto py-8 px-4 md:px-6">
        <div className="space-y-6">
          <div className="flex items-center justify-between">
            <Skeleton className="h-10 w-[250px]" />
            <Skeleton className="h-10 w-[120px]" />
          </div>
          <Skeleton className="h-[200px] w-full" />
          <Skeleton className="h-[400px] w-full" />
        </div>
      </div>
    );
  }

  if (!companyData) {
    return (
      <div className="container mx-auto py-8 px-4 md:px-6">
        <Alert variant="destructive">
          <AlertCircle className="h-4 w-4" />
          <AlertTitle>Error</AlertTitle>
          <AlertDescription>
            Company not found or failed to load data.
            <Button
              variant="link"
              className="p-0 h-auto font-normal"
              onClick={() => router.push("/")}
            >
              Return to marketplace
            </Button>
          </AlertDescription>
        </Alert>
      </div>
    );
  }

  const { company, stats, stakeholders, token_holders } = companyData;
  const isDistributed = company.state === "distributed";
  const isWaitingFunds = company.state === "waiting_funds";
  const allStakeholdersReady = stakeholders.every(
    (sh) => sh.has_paid && sh.has_trustline
  );

  // If the company is in waiting_funds state, show the stakeholder funding status prominently
  if (isWaitingFunds) {
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
              <span>Company Details</span>
            </div>
            <h1 className="text-3xl font-bold tracking-tight flex items-center gap-2">
              {company.name}
              <Badge variant="outline" className="ml-2">
                {company.symbol}
              </Badge>
            </h1>
          </div>

          <div className="flex items-center gap-2">
            <Button
              variant="outline"
              size="sm"
              onClick={handleRefresh}
              className="flex items-center gap-1"
            >
              <RefreshCw className="h-4 w-4" />
              Refresh
            </Button>

            <Button
              size="sm"
              onClick={handleCheckOnly}
              className="flex items-center gap-1 bg-gradient-to-r from-blue-600 to-cyan-500 hover:from-blue-700 hover:to-cyan-600"
            >
              {isCheck ? (
                <>
                  <RefreshCw className="h-4 w-4 animate-spin" />
                  Checking...
                </>
              ) : (
                <>
                  <Coins className="h-4 w-4" />
                  Check
                </>
              )}
            </Button>
          </div>
        </div>

        <StakeholderFundingStatus
          company={company}
          stakeholders={stakeholders}
          refreshKey={refreshKey}
          onDistribute={handleDistribute}
          isDistributing={isDistributing}
        />

        <div className="mt-8">
          <Tabs
            value={activeTab}
            onValueChange={setActiveTab}
            className="space-y-6"
          >
            <TabsList className="grid grid-cols-3 md:w-[400px]">
              <TabsTrigger value="stakeholders">Stakeholders</TabsTrigger>
              <TabsTrigger value="overview">Overview</TabsTrigger>
              <TabsTrigger value="holdings">Token Holdings</TabsTrigger>
            </TabsList>

            <TabsContent value="stakeholders">
              <Card>
                <CardHeader>
                  <CardTitle>Stakeholder Status</CardTitle>
                  <CardDescription>
                    Track payment and trustline status for all stakeholders
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <ShareholderTable
                    companyId={companyId}
                    stakeholders={stakeholders}
                    refreshKey={refreshKey}
                    isDistributed={isDistributed}
                  />
                </CardContent>
              </Card>
            </TabsContent>

            <TabsContent value="overview">
              <CompanyOverview
                company={company}
                stats={stats}
                stakeholders={stakeholders}
                isDistributed={isDistributed}
              />
            </TabsContent>

            <TabsContent value="holdings">
              <Card>
                <CardHeader>
                  <CardTitle>Token Holdings</CardTitle>
                  <CardDescription>
                    Current on-chain token distribution
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <TokenHoldingsChart
                    tokenHolders={token_holders}
                    symbol={company.symbol}
                    isDistributed={isDistributed}
                  />
                </CardContent>
              </Card>
            </TabsContent>
          </Tabs>
        </div>
      </div>
    );
  }

  const getInitials = (name: string) => {
    const words = name.trim().split(" ");
    if (words.length === 1) {
      return words[0].substring(0, 2).toUpperCase();
    }
    return (words[0][0] + words[1][0]).toUpperCase();
  };

  const logoInitials = getInitials(company.name);

  // Regular view for distributed companies
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
            <span>Company Details</span>
          </div>
          <h1 className="text-3xl font-bold tracking-tight flex items-center gap-2">
            {/* Logo Badge */}
            <span className="inline-flex items-center justify-center w-9 h-9 rounded-full bg-blue-600 text-white font-semibold text-lg">
              {logoInitials}
            </span>
            {company.name}
            <Badge variant="outline" className="ml-2">
              {company.symbol}
            </Badge>
          </h1>
        </div>

        <div className="flex items-center gap-2">
          <Button
            variant="outline"
            size="sm"
            onClick={handleRefresh}
            className="flex items-center gap-1"
          >
            <RefreshCw className="h-4 w-4" />
            Refresh
          </Button>
        </div>
      </div>

      <div className="grid gap-6 md:grid-cols-3 mb-6">
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground">
              Status
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {isDistributed ? (
                <span className="flex items-center text-green-500">
                  <CheckCircle2 className="mr-2 h-5 w-5" />
                  Distributed
                </span>
              ) : (
                <span className="flex items-center text-amber-500">
                  <Clock className="mr-2 h-5 w-5" />
                  Waiting for Funds
                </span>
              )}
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground">
              Valuation
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold flex items-center">
              <DollarSign className="mr-1 h-5 w-5 text-muted-foreground" />$
              {isDistributed
                ? stats.market_cap_usd.toFixed(2)
                : company.total_valuation_usd.toFixed(2)}
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground">
              Token Supply
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold flex items-center">
              <Coins className="mr-2 h-5 w-5 text-muted-foreground" />
              {company.total_supply.toLocaleString()} {company.symbol}
            </div>
          </CardContent>
        </Card>
      </div>

      <Tabs defaultValue="overview" className="space-y-6">
        <TabsList className="grid grid-cols-2 md:w-[400px]">
          <TabsTrigger value="overview">Overview</TabsTrigger>
          <TabsTrigger value="holdings">Token Holdings</TabsTrigger>
        </TabsList>

        <TabsContent value="overview" className="space-y-6">
          <CompanyOverview
            company={company}
            stats={stats}
            stakeholders={stakeholders}
            isDistributed={isDistributed}
          />

          <div className="grid gap-6 md:grid-cols-2">
            <Card>
              <CardHeader>
                <CardTitle>Issuing Address</CardTitle>
                <CardDescription>
                  The XRP Ledger address that issues the token
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="flex items-center justify-between">
                  <code className="relative rounded bg-muted px-[0.3rem] py-[0.2rem] font-mono text-sm">
                    {company.issuing_address}
                  </code>
                  <Button variant="ghost" size="icon" asChild>
                    <a
                      href={`https://testnet.xrpl.org/accounts/${company.issuing_address}`}
                      target="_blank"
                      rel="noopener noreferrer"
                    >
                      <ExternalLink className="h-4 w-4" />
                      <span className="sr-only">View on XRPL Explorer</span>
                    </a>
                  </Button>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>AMM Pool</CardTitle>
                <CardDescription>
                  Automated Market Maker pool details
                </CardDescription>
              </CardHeader>
              <CardContent>
                {isDistributed ? (
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-2">
                      <Percent className="h-5 w-5 text-muted-foreground" />
                      <div>
                        <div className="font-medium">
                          {company.liquidity_percent}% Liquidity
                        </div>
                        <div className="text-sm text-muted-foreground">
                          RLUSD/{company.symbol} Pool
                        </div>
                      </div>
                    </div>
                    <div className="flex gap-2">
                      <Button asChild variant="outline" size="sm">
                        <a href={`/company/${companyId}/amm`}>
                          View AMM Details
                        </a>
                      </Button>
                      <Button
                        asChild
                        size="sm"
                        className="bg-gradient-to-r from-blue-600 to-cyan-500 hover:from-blue-700 hover:to-cyan-600"
                      >
                        <a href={`/company/${companyId}/trade`}>
                          Trade
                          <ArrowRight className="ml-2 h-4 w-4" />
                        </a>
                      </Button>
                    </div>
                  </div>
                ) : (
                  <div className="flex items-center gap-2 text-muted-foreground">
                    <Clock className="h-5 w-5" />
                    <div>
                      <div className="font-medium">AMM Not Created Yet</div>
                      <div className="text-sm">
                        Will be created after token distribution
                      </div>
                    </div>
                  </div>
                )}
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        <TabsContent value="holdings">
          <Card>
            <CardHeader>
              <CardTitle>Token Holdings</CardTitle>
              <CardDescription>
                Current on-chain token distribution
              </CardDescription>
            </CardHeader>
            <CardContent>
              <TokenHoldingsChart
                tokenHolders={token_holders}
                symbol={company.symbol}
                isDistributed={isDistributed}
              />
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
}
