"use client";

import type React from "react";

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
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Skeleton } from "@/components/ui/skeleton";
import { useToast } from "@/hooks/use-toast";
import {
  AlertCircle,
  ArrowLeft,
  ChevronRight,
  ExternalLink,
  RefreshCw,
  Droplets,
  BarChart3,
  Percent,
  Info,
  CheckCircle2,
} from "lucide-react";
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import {
  PieChart,
  Pie,
  Cell,
  ResponsiveContainer,
  Legend,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
} from "recharts";
import { Badge } from "@/components/ui/badge";
import { Separator } from "@/components/ui/separator";
import {
  HoverCard,
  HoverCardContent,
  HoverCardTrigger,
} from "@/components/ui/hover-card";

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
    asset_frozen?: boolean;
    asset2_frozen?: boolean;
    auction_slot?: {
      account: string;
      discounted_fee: number;
      expiration: string;
      price: {
        currency: string;
        issuer: string;
        value: string;
      };
      time_interval: number;
    };
    lp_token?: {
      currency: string;
      issuer: string;
      value: string;
    };
    trading_fee: number;
    vote_slots: Array<{
      account: string;
      trading_fee: number;
      vote_weight: number;
    }>;
    [key: string]: any;
  };
  ledger_current_index: number;
  validated: boolean;
}

interface CompanyInfo {
  name: string;
  symbol: string;
}

export default function AMMInfoPage() {
  const params = useParams();
  const router = useRouter();
  const { toast } = useToast();
  const companyId = params.id as string;

  const [ammInfo, setAmmInfo] = useState<AMMInfo | null>(null);
  const [companyInfo, setCompanyInfo] = useState<CompanyInfo | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [customAccount, setCustomAccount] = useState("");
  const [refreshKey, setRefreshKey] = useState(0);

  // Fetch company info
  useEffect(() => {
    const fetchCompanyInfo = async () => {
      try {
        const response = await fetch(
          `http://localhost:8000/companies/${companyId}/full_info`
        );
        if (!response.ok) throw new Error("Failed to fetch company info");
        const data = await response.json();
        setCompanyInfo({
          name: data.company.name,
          symbol: data.company.symbol,
        });
      } catch (error) {
        console.error("Error fetching company info:", error);
      }
    };

    fetchCompanyInfo();
  }, [companyId]);

  // Fetch AMM info
  useEffect(() => {
    const fetchAMMInfo = async () => {
      setIsLoading(true);
      try {
        const url = customAccount
          ? `/api/companies/${companyId}/amm_info?account=${customAccount}`
          : `http://localhost:8000/companies/${companyId}/full_info`;

        const response = await fetch(url);
        if (!response.ok) throw new Error("Failed to fetch AMM info");
        const data = await response.json();

        // Handle different response structures
        if (data.amm_info) {
          setAmmInfo(data.amm_info);
        } else if (data.amm) {
          setAmmInfo(data);
        }
      } catch (error) {
        console.error("Error fetching AMM info:", error);
        toast({
          title: "Error",
          description: "Failed to load AMM information",
          variant: "destructive",
        });
        setAmmInfo(null);
      } finally {
        setIsLoading(false);
      }
    };

    fetchAMMInfo();
  }, [companyId, customAccount, toast, refreshKey]);

  // Handle refresh
  const handleRefresh = () => {
    setRefreshKey((prev) => prev + 1);
  };

  // Handle custom account search
  const handleCustomAccountSearch = (e: React.FormEvent) => {
    e.preventDefault();
    // Refresh will trigger the useEffect
    setRefreshKey((prev) => prev + 1);
  };

  // Prepare data for liquidity pie chart
  const getLiquidityChartData = () => {
    if (!ammInfo || !ammInfo.amm || !ammInfo.amm.amount || !ammInfo.amm.amount2)
      return [];

    const token1Value = Number.parseFloat(ammInfo.amm.amount.value);
    const token2Value = Number.parseFloat(ammInfo.amm.amount2.value);

    return [
      {
        name: "RLUSD",
        value: token1Value,
        color: "#3b82f6",
      },
      {
        name: companyInfo?.symbol || "Token",
        value: token2Value,
        color: "#10b981",
      },
    ];
  };

  // Prepare data for vote weight chart
  const getVoteWeightData = () => {
    if (!ammInfo || !ammInfo.amm || !ammInfo.amm.vote_slots) return [];

    return ammInfo.amm.vote_slots.map((slot, index) => ({
      name: formatWalletAddress(slot.account),
      weight: slot.vote_weight / 1000, // Convert from basis points to percentage
      fee: slot.trading_fee / 10000, // Convert from basis points to percentage
      color: `#${(index * 3 + 3).toString(16)}${(index * 5 + 5).toString(
        16
      )}82f6`,
    }));
  };

  // Format wallet address for display
  const formatWalletAddress = (address: string) => {
    if (!address || address.length <= 12) return address;
    return `${address.substring(0, 6)}...${address.substring(
      address.length - 6
    )}`;
  };

  // Format currency code for display
  const formatCurrencyCode = (code: string) => {
    if (!code) return "Unknown";

    // If it's a hex string (likely a currency code), try to convert to ASCII
    if (/^[0-9A-F]+$/i.test(code)) {
      try {
        // Convert hex to ASCII, skipping every other character (assuming it's padded)
        let result = "";
        for (let i = 0; i < code.length; i += 2) {
          const hexChar = code.substr(i, 2);
          const charCode = Number.parseInt(hexChar, 16);
          if (charCode > 32 && charCode < 127) {
            // Printable ASCII
            result += String.fromCharCode(charCode);
          }
        }
        if (result.length > 0) return result.trim();
      } catch (e) {
        // Fall back to original if conversion fails
      }
    }

    return code;
  };

  // Custom tooltip for pie chart
  const CustomTooltip = ({ active, payload }: any) => {
    if (active && payload && payload.length) {
      return (
        <div className="bg-background border rounded-md p-3 shadow-md">
          <p className="font-medium">{payload[0].name}</p>
          <p className="text-sm">{`Amount: ${payload[0].value}`}</p>
        </div>
      );
    }
    return null;
  };

  if (isLoading) {
    return (
      <div className="container mx-auto py-8 px-4 md:px-6">
        <div className="space-y-6">
          <div className="flex items-center justify-between">
            <Skeleton className="h-10 w-[250px]" />
            <Skeleton className="h-10 w-[120px]" />
          </div>
          <div className="grid gap-6 md:grid-cols-2">
            <Skeleton className="h-[300px] w-full" />
            <Skeleton className="h-[300px] w-full" />
          </div>
          <Skeleton className="h-[200px] w-full" />
        </div>
      </div>
    );
  }

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
            <span>AMM Information</span>
          </div>
          <h1 className="text-3xl font-bold tracking-tight flex items-center gap-2">
            AMM Pool Details
            {companyInfo && (
              <Badge variant="outline" className="ml-2">
                {companyInfo.symbol}
              </Badge>
            )}
          </h1>
        </div>

        <div className="flex items-center gap-2">
          <Button
            variant="outline"
            size="sm"
            onClick={() => router.push(`/company/${companyId}`)}
            className="flex items-center gap-1"
          >
            <ArrowLeft className="h-4 w-4" />
            Back to Company
          </Button>

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

      {!ammInfo || !ammInfo.amm ? (
        <Alert variant="destructive">
          <AlertCircle className="h-4 w-4" />
          <AlertTitle>AMM Not Found</AlertTitle>
          <AlertDescription>
            No AMM information available. The pool may not have been created
            yet.
          </AlertDescription>
        </Alert>
      ) : (
        <Tabs defaultValue="overview" className="space-y-6">
          <TabsList className="grid grid-cols-3 md:w-[400px]">
            <TabsTrigger value="overview">Overview</TabsTrigger>
            <TabsTrigger value="liquidity">Liquidity</TabsTrigger>
            <TabsTrigger value="governance">Governance</TabsTrigger>
          </TabsList>

          <TabsContent value="overview" className="space-y-6">
            <div className="grid gap-6 md:grid-cols-3">
              <Card>
                <CardHeader className="pb-2">
                  <CardTitle className="text-sm font-medium text-muted-foreground flex items-center gap-2">
                    <Percent className="h-4 w-4" />
                    Trading Fee
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold">
                    {(ammInfo.amm.trading_fee / 10000).toFixed(2)}%
                  </div>
                  <p className="text-sm text-muted-foreground">Fee per trade</p>
                </CardContent>
              </Card>

              <Card>
                <CardHeader className="pb-2">
                  <CardTitle className="text-sm font-medium text-muted-foreground flex items-center gap-2">
                    <Droplets className="h-4 w-4" />
                    Liquidity
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold">
                    {ammInfo.amm.amount && `${ammInfo.amm.amount.value} RLUSD`}
                  </div>
                  <p className="text-sm text-muted-foreground">
                    {ammInfo.amm.amount2 &&
                      `${ammInfo.amm.amount2.value} ${
                        companyInfo?.symbol || "Tokens"
                      }`}
                  </p>
                </CardContent>
              </Card>

              <Card>
                <CardHeader className="pb-2">
                  <CardTitle className="text-sm font-medium text-muted-foreground flex items-center gap-2">
                    <BarChart3 className="h-4 w-4" />
                    Status
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="flex items-center gap-2">
                    <div className="h-3 w-3 rounded-full bg-green-500"></div>
                    <div className="text-xl font-bold">Active</div>
                  </div>
                  <p className="text-sm text-muted-foreground">
                    Ledger Index: {ammInfo.ledger_current_index}
                  </p>
                </CardContent>
              </Card>
            </div>

            <Card>
              <CardHeader>
                <CardTitle>Pool Information</CardTitle>
                <CardDescription>
                  Key details about the Automated Market Maker pool
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="grid gap-4 md:grid-cols-2">
                  <div className="space-y-4">
                    <div>
                      <h3 className="text-sm font-medium text-muted-foreground mb-2">
                        Pool Account
                      </h3>
                      <div className="flex items-center gap-2">
                        <code className="relative rounded bg-muted px-[0.3rem] py-[0.2rem] font-mono text-sm flex-1 overflow-hidden text-ellipsis">
                          {ammInfo.amm.account}
                        </code>
                        <Button
                          variant="ghost"
                          size="icon"
                          asChild
                          className="h-8 w-8"
                        >
                          <a
                            href={`https://testnet.xrpl.org/accounts/${ammInfo.amm.account}`}
                            target="_blank"
                            rel="noopener noreferrer"
                          >
                            <ExternalLink className="h-4 w-4" />
                          </a>
                        </Button>
                      </div>
                    </div>

                    {ammInfo.amm.auction_slot && (
                      <div>
                        <h3 className="text-sm font-medium text-muted-foreground mb-2 flex items-center gap-1">
                          Auction Slot
                          <HoverCard>
                            <HoverCardTrigger asChild>
                              <Button
                                variant="ghost"
                                size="icon"
                                className="h-5 w-5 p-0"
                              >
                                <Info className="h-3.5 w-3.5" />
                              </Button>
                            </HoverCardTrigger>
                            <HoverCardContent className="w-80">
                              <div className="space-y-2">
                                <h4 className="text-sm font-semibold">
                                  Auction Slot
                                </h4>
                                <p className="text-sm">
                                  Auction slots allow traders to bid for
                                  discounted trading fees for a limited time.
                                </p>
                              </div>
                            </HoverCardContent>
                          </HoverCard>
                        </h3>
                        <div className="space-y-1 text-sm">
                          <div className="flex justify-between">
                            <span className="text-muted-foreground">
                              Owner:
                            </span>
                            <span className="font-mono">
                              {formatWalletAddress(
                                ammInfo.amm.auction_slot.account
                              )}
                            </span>
                          </div>
                          <div className="flex justify-between">
                            <span className="text-muted-foreground">
                              Discounted Fee:
                            </span>
                            <span>
                              {(
                                ammInfo.amm.auction_slot.discounted_fee / 10000
                              ).toFixed(2)}
                              %
                            </span>
                          </div>
                          <div className="flex justify-between">
                            <span className="text-muted-foreground">
                              Expires:
                            </span>
                            <span>
                              {new Date(
                                ammInfo.amm.auction_slot.expiration
                              ).toLocaleString()}
                            </span>
                          </div>
                        </div>
                      </div>
                    )}
                  </div>

                  <div className="space-y-4">
                    <div>
                      <h3 className="text-sm font-medium text-muted-foreground mb-2 flex items-center gap-1">
                        LP Token
                        <HoverCard>
                          <HoverCardTrigger asChild>
                            <Button
                              variant="ghost"
                              size="icon"
                              className="h-5 w-5 p-0"
                            >
                              <Info className="h-3.5 w-3.5" />
                            </Button>
                          </HoverCardTrigger>
                          <HoverCardContent className="w-80">
                            <div className="space-y-2">
                              <h4 className="text-sm font-semibold">
                                Liquidity Provider Token
                              </h4>
                              <p className="text-sm">
                                LP tokens represent your share of the liquidity
                                pool. They are issued when you provide liquidity
                                and can be redeemed to withdraw your share.
                              </p>
                            </div>
                          </HoverCardContent>
                        </HoverCard>
                      </h3>
                      {ammInfo.amm.lp_token && (
                        <div className="space-y-1 text-sm">
                          <div className="flex justify-between">
                            <span className="text-muted-foreground">
                              Currency:
                            </span>
                            <span className="font-mono">
                              {formatCurrencyCode(
                                ammInfo.amm.lp_token.currency
                              )}
                            </span>
                          </div>
                          <div className="flex justify-between">
                            <span className="text-muted-foreground">
                              Issuer:
                            </span>
                            <span className="font-mono">
                              {formatWalletAddress(ammInfo.amm.lp_token.issuer)}
                            </span>
                          </div>
                          <div className="flex justify-between">
                            <span className="text-muted-foreground">
                              Total Supply:
                            </span>
                            <span>{ammInfo.amm.lp_token.value}</span>
                          </div>
                        </div>
                      )}
                    </div>

                    <div>
                      <h3 className="text-sm font-medium text-muted-foreground mb-2">
                        Asset Status
                      </h3>
                      <div className="flex gap-4">
                        <div className="flex items-center gap-2">
                          <div
                            className={`h-2 w-2 rounded-full ${
                              ammInfo.amm.asset_frozen
                                ? "bg-red-500"
                                : "bg-green-500"
                            }`}
                          ></div>
                          <span className="text-sm">
                            RLUSD:{" "}
                            {ammInfo.amm.asset_frozen ? "Frozen" : "Active"}
                          </span>
                        </div>
                        <div className="flex items-center gap-2">
                          <div
                            className={`h-2 w-2 rounded-full ${
                              ammInfo.amm.asset2_frozen
                                ? "bg-red-500"
                                : "bg-green-500"
                            }`}
                          ></div>
                          <span className="text-sm">
                            {companyInfo?.symbol || "Token"}:{" "}
                            {ammInfo.amm.asset2_frozen ? "Frozen" : "Active"}
                          </span>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>Custom Account Lookup</CardTitle>
                <CardDescription>
                  View AMM information from a specific account's perspective
                </CardDescription>
              </CardHeader>
              <CardContent>
                <form
                  onSubmit={handleCustomAccountSearch}
                  className="flex items-center gap-2"
                >
                  <div className="grid flex-1 gap-2">
                    <Label htmlFor="account">XRP Ledger Account</Label>
                    <Input
                      id="account"
                      placeholder="rXYZ..."
                      value={customAccount}
                      onChange={(e) => setCustomAccount(e.target.value)}
                    />
                  </div>
                  <Button type="submit" className="mt-8">
                    Search
                  </Button>
                </form>
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="liquidity" className="space-y-6">
            <Card>
              <CardHeader>
                <CardTitle>Liquidity Distribution</CardTitle>
                <CardDescription>
                  Current assets in the liquidity pool
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="grid gap-6 md:grid-cols-2">
                  <div className="h-[300px]">
                    <ResponsiveContainer width="100%" height="100%">
                      <PieChart>
                        <Pie
                          data={getLiquidityChartData()}
                          cx="50%"
                          cy="50%"
                          innerRadius={60}
                          outerRadius={120}
                          fill="#8884d8"
                          paddingAngle={5}
                          dataKey="value"
                          label={({ name, percent }) =>
                            `${name} ${(percent * 100).toFixed(0)}%`
                          }
                        >
                          {getLiquidityChartData().map((entry, index) => (
                            <Cell key={`cell-${index}`} fill={entry.color} />
                          ))}
                        </Pie>
                        <Tooltip content={<CustomTooltip />} />
                        <Legend />
                      </PieChart>
                    </ResponsiveContainer>
                  </div>

                  <div className="flex flex-col justify-center space-y-6">
                    <div className="space-y-2">
                      <h3 className="text-lg font-medium">Pool Composition</h3>
                      <Separator />

                      <div className="grid grid-cols-2 gap-4 mt-4">
                        <div className="bg-blue-500/10 rounded-lg p-4 border border-blue-500/20">
                          <div className="text-sm text-muted-foreground">
                            RLUSD
                          </div>
                          <div className="text-2xl font-bold mt-1">
                            {ammInfo.amm.amount
                              ? ammInfo.amm.amount.value
                              : "0"}
                          </div>
                        </div>

                        <div className="bg-green-500/10 rounded-lg p-4 border border-green-500/20">
                          <div className="text-sm text-muted-foreground">
                            {companyInfo?.symbol || "Token"}
                          </div>
                          <div className="text-2xl font-bold mt-1">
                            {ammInfo.amm.amount2
                              ? ammInfo.amm.amount2.value
                              : "0"}
                          </div>
                        </div>
                      </div>
                    </div>

                    <div className="space-y-2">
                      <h3 className="text-lg font-medium">Exchange Rate</h3>
                      <Separator />

                      <div className="grid grid-cols-2 gap-4 mt-4">
                        <div className="bg-card/50 rounded-lg p-4 border border-border/50">
                          <div className="text-sm text-muted-foreground">
                            1 RLUSD =
                          </div>
                          <div className="text-xl font-bold mt-1">
                            {ammInfo.amm.amount && ammInfo.amm.amount2
                              ? (
                                  Number.parseFloat(ammInfo.amm.amount2.value) /
                                  Number.parseFloat(ammInfo.amm.amount.value)
                                ).toFixed(4)
                              : "0"}{" "}
                            {companyInfo?.symbol || "Token"}
                          </div>
                        </div>

                        <div className="bg-card/50 rounded-lg p-4 border border-border/50">
                          <div className="text-sm text-muted-foreground">
                            1 {companyInfo?.symbol || "Token"} =
                          </div>
                          <div className="text-xl font-bold mt-1">
                            {ammInfo.amm.amount && ammInfo.amm.amount2
                              ? (
                                  Number.parseFloat(ammInfo.amm.amount.value) /
                                  Number.parseFloat(ammInfo.amm.amount2.value)
                                ).toFixed(4)
                              : "0"}{" "}
                            RLUSD
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>Provide Liquidity</CardTitle>
                <CardDescription>
                  Add liquidity to earn trading fees
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="grid gap-6 md:grid-cols-2">
                  <div className="space-y-4">
                    <div className="space-y-2">
                      <Label htmlFor="rlusd-amount">RLUSD Amount</Label>
                      <Input
                        id="rlusd-amount"
                        type="number"
                        placeholder="0.00"
                      />
                    </div>

                    <div className="space-y-2">
                      <Label htmlFor="token-amount">
                        {companyInfo?.symbol || "Token"} Amount
                      </Label>
                      <Input
                        id="token-amount"
                        type="number"
                        placeholder="0.00"
                      />
                    </div>

                    <Button className="w-full bg-gradient-to-r from-blue-600 to-cyan-500 hover:from-blue-700 hover:to-cyan-600">
                      Add Liquidity
                    </Button>
                  </div>

                  <div className="bg-card/30 rounded-lg p-6 border border-border/50 flex flex-col justify-center">
                    <h3 className="text-lg font-medium mb-4">
                      Benefits of Providing Liquidity
                    </h3>
                    <ul className="space-y-2">
                      <li className="flex items-start gap-2">
                        <div className="rounded-full bg-green-500/20 p-1 mt-0.5">
                          <CheckCircle2 className="h-3 w-3 text-green-500" />
                        </div>
                        <span className="text-sm">
                          Earn a share of the 0.5% trading fees
                        </span>
                      </li>
                      <li className="flex items-start gap-2">
                        <div className="rounded-full bg-green-500/20 p-1 mt-0.5">
                          <CheckCircle2 className="h-3 w-3 text-green-500" />
                        </div>
                        <span className="text-sm">
                          Receive LP tokens representing your share of the pool
                        </span>
                      </li>
                      <li className="flex items-start gap-2">
                        <div className="rounded-full bg-green-500/20 p-1 mt-0.5">
                          <CheckCircle2 className="h-3 w-3 text-green-500" />
                        </div>
                        <span className="text-sm">
                          Withdraw your liquidity at any time
                        </span>
                      </li>
                      <li className="flex items-start gap-2">
                        <div className="rounded-full bg-amber-500/20 p-1 mt-0.5">
                          <AlertCircle className="h-3 w-3 text-amber-500" />
                        </div>
                        <span className="text-sm">
                          Be aware of impermanent loss risks
                        </span>
                      </li>
                    </ul>
                  </div>
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="governance" className="space-y-6">
            <Card>
              <CardHeader>
                <CardTitle>Vote Distribution</CardTitle>
                <CardDescription>
                  Current voting power in the AMM governance
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="h-[300px]">
                  <ResponsiveContainer width="100%" height="100%">
                    <BarChart data={getVoteWeightData()}>
                      <CartesianGrid
                        strokeDasharray="3 3"
                        stroke="rgba(255,255,255,0.1)"
                      />
                      <XAxis dataKey="name" />
                      <YAxis
                        label={{
                          value: "Vote Weight (%)",
                          angle: -90,
                          position: "insideLeft",
                        }}
                      />
                      <Tooltip
                        formatter={(value, name, props) => [
                          `${value}%`,
                          "Vote Weight",
                        ]}
                        labelFormatter={(label) => `Account: ${label}`}
                        contentStyle={{
                          backgroundColor: "rgba(22, 22, 22, 0.9)",
                          border: "1px solid #333",
                        }}
                      />
                      <Bar dataKey="weight" fill="#3b82f6" />
                    </BarChart>
                  </ResponsiveContainer>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>Vote Slots</CardTitle>
                <CardDescription>
                  Accounts with voting power in the AMM
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="overflow-x-auto">
                  <table className="w-full">
                    <thead>
                      <tr className="border-b border-border/50">
                        <th className="text-left py-3 px-4 font-medium text-muted-foreground">
                          Account
                        </th>
                        <th className="text-center py-3 px-4 font-medium text-muted-foreground">
                          Vote Weight
                        </th>
                        <th className="text-center py-3 px-4 font-medium text-muted-foreground">
                          Proposed Fee
                        </th>
                        <th className="text-right py-3 px-4 font-medium text-muted-foreground">
                          Actions
                        </th>
                      </tr>
                    </thead>
                    <tbody>
                      {ammInfo.amm.vote_slots.map((slot, index) => (
                        <tr key={index} className="border-b border-border/50">
                          <td className="py-3 px-4 font-mono text-sm">
                            <div className="flex items-center gap-1">
                              {formatWalletAddress(slot.account)}
                              <Button
                                variant="ghost"
                                size="icon"
                                className="h-6 w-6"
                                asChild
                              >
                                <a
                                  href={`https://testnet.xrpl.org/accounts/${slot.account}`}
                                  target="_blank"
                                  rel="noopener noreferrer"
                                >
                                  <ExternalLink className="h-3 w-3" />
                                </a>
                              </Button>
                            </div>
                          </td>
                          <td className="py-3 px-4 text-center">
                            {(slot.vote_weight / 1000).toFixed(2)}%
                          </td>
                          <td className="py-3 px-4 text-center">
                            {(slot.trading_fee / 10000).toFixed(2)}%
                          </td>
                          <td className="py-3 px-4 text-right">
                            <Button variant="outline" size="sm">
                              Vote
                            </Button>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>Cast Vote</CardTitle>
                <CardDescription>
                  Propose a new trading fee (requires LP tokens)
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="grid gap-6 md:grid-cols-2">
                  <div className="space-y-4">
                    <div className="space-y-2">
                      <Label htmlFor="fee-proposal">
                        Proposed Trading Fee (%)
                      </Label>
                      <Input
                        id="fee-proposal"
                        type="number"
                        placeholder="0.50"
                        min="0.01"
                        max="1.00"
                        step="0.01"
                      />
                      <p className="text-xs text-muted-foreground">
                        Fee must be between 0.01% and 1.00%
                      </p>
                    </div>

                    <Button className="w-full">Cast Vote</Button>
                  </div>

                  <div className="bg-card/30 rounded-lg p-6 border border-border/50 flex flex-col justify-center">
                    <h3 className="text-lg font-medium mb-4">
                      Voting Information
                    </h3>
                    <div className="space-y-3 text-sm">
                      <p>
                        <span className="text-muted-foreground">
                          Your LP Tokens:
                        </span>{" "}
                        0.00
                      </p>
                      <p>
                        <span className="text-muted-foreground">
                          Potential Vote Weight:
                        </span>{" "}
                        0.00%
                      </p>
                      <p>
                        <span className="text-muted-foreground">
                          Current Fee:
                        </span>{" "}
                        {(ammInfo.amm.trading_fee / 10000).toFixed(2)}%
                      </p>
                      <p className="text-xs text-muted-foreground mt-4">
                        Note: Voting power is proportional to your LP token
                        holdings. You need LP tokens to cast a vote.
                      </p>
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>
      )}
    </div>
  );
}
