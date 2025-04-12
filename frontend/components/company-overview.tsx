"use client";

import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Progress } from "@/components/ui/progress";
import { Coins, DollarSign, Percent, Users } from "lucide-react";
import {
  PieChart,
  Pie,
  Cell,
  ResponsiveContainer,
  Tooltip,
  Legend,
} from "recharts";

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

interface CompanyOverviewProps {
  company: Company;
  stats: Stats;
  stakeholders: Stakeholder[];
  isDistributed: boolean;
}

// Generate colors for the pie chart
const COLORS = [
  "#3b82f6",
  "#0ea5e9",
  "#06b6d4",
  "#0891b2",
  "#0e7490",
  "#155e75",
  "#1e40af",
  "#1d4ed8",
  "#2563eb",
  "#3b82f6",
];

export default function CompanyOverview({
  company,
  stats,
  stakeholders,
  isDistributed,
}: CompanyOverviewProps) {
  // Format wallet address for display
  const formatWalletAddress = (address: string) => {
    if (address.length <= 8) return address;
    return `${address.substring(0, 4)}...${address.substring(
      address.length - 4
    )}`;
  };

  // Calculate metrics
  const totalStakeholders = stakeholders.length;
  const paidStakeholders = stakeholders.filter((sh) => sh.has_paid).length;
  const trustlineStakeholders = stakeholders.filter(
    (sh) => sh.has_trustline
  ).length;
  const readyStakeholders = stakeholders.filter(
    (sh) => sh.has_paid && sh.has_trustline
  ).length;

  const paidPercentage = (paidStakeholders / totalStakeholders) * 100;
  const trustlinePercentage = (trustlineStakeholders / totalStakeholders) * 100;
  const readyPercentage = (readyStakeholders / totalStakeholders) * 100;

  // Prepare data for the pie chart
  const distributionData = [
    ...stakeholders.map((sh, index) => ({
      name: formatWalletAddress(sh.wallet_address),
      value: (100 - company.liquidity_percent) / stakeholders.length, // Distribute remaining percentage evenly
      type: "Stakeholder",
    })),
    {
      name: "Liquidity Pool",
      value: company.liquidity_percent,
      type: "Liquidity",
    },
  ];

  // Custom tooltip for the pie chart
  const CustomTooltip = ({ active, payload }: any) => {
    if (active && payload && payload.length) {
      const data = payload[0].payload;
      return (
        <div className="p-2 bg-background border rounded-md shadow-lg">
          <div className="font-medium">{data.name}</div>
          <div className="text-sm text-muted-foreground">{data.type}</div>
          <div className="mt-1 font-medium">{data.value.toFixed(2)}%</div>
        </div>
      );
    }
    return null;
  };

  return (
    <div className="grid gap-6 md:grid-cols-2">
      <Card>
        <CardHeader>
          <CardTitle>Token Distribution</CardTitle>
          <CardDescription>
            Allocation of {company.symbol} tokens
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="h-[300px]">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie
                  data={distributionData}
                  cx="50%"
                  cy="50%"
                  labelLine={false}
                  outerRadius={120}
                  fill="#8884d8"
                  dataKey="value"
                >
                  {distributionData.map((entry, index) => (
                    <Cell
                      key={`cell-${index}`}
                      fill={
                        entry.type === "Liquidity"
                          ? "#10b981"
                          : COLORS[index % COLORS.length]
                      }
                    />
                  ))}
                </Pie>
                <Tooltip content={<CustomTooltip />} />
                <Legend />
              </PieChart>
            </ResponsiveContainer>
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Company Metrics</CardTitle>
          <CardDescription>
            Key financial and distribution metrics
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-6">
          <div className="grid grid-cols-2 gap-4">
            <div className="flex items-center gap-2">
              <DollarSign className="h-5 w-5 text-muted-foreground" />
              <div>
                <div className="text-sm font-medium text-muted-foreground">
                  Token Price
                </div>
                <div className="font-medium">
                  $
                  {isDistributed
                    ? stats.price_per_token_usd.toFixed(4)
                    : (
                        company.total_valuation_usd / company.total_supply
                      ).toFixed(4)}
                </div>
              </div>
            </div>

            <div className="flex items-center gap-2">
              <Coins className="h-5 w-5 text-muted-foreground" />
              <div>
                <div className="text-sm font-medium text-muted-foreground">
                  Market Cap
                </div>
                <div className="font-medium">
                  ${company.total_valuation_usd.toLocaleString()}
                </div>
              </div>
            </div>

            <div className="flex items-center gap-2">
              <Percent className="h-5 w-5 text-muted-foreground" />
              <div>
                <div className="text-sm font-medium text-muted-foreground">
                  Liquidity
                </div>
                <div className="font-medium">{company.liquidity_percent}%</div>
              </div>
            </div>

            <div className="flex items-center gap-2">
              <Users className="h-5 w-5 text-muted-foreground" />
              <div>
                <div className="text-sm font-medium text-muted-foreground">
                  Stakeholders
                </div>
                <div className="font-medium">{stakeholders.length}</div>
              </div>
            </div>
          </div>

          {!isDistributed && (
            <div className="space-y-4">
              <div>
                <div className="flex items-center justify-between mb-1">
                  <div className="text-sm font-medium">Payment Status</div>
                  <div className="text-sm text-muted-foreground">
                    {paidStakeholders} of {totalStakeholders} paid
                  </div>
                </div>
                <Progress value={paidPercentage} className="h-2" />
              </div>

              <div>
                <div className="flex items-center justify-between mb-1">
                  <div className="text-sm font-medium">Trustline Status</div>
                  <div className="text-sm text-muted-foreground">
                    {trustlineStakeholders} of {totalStakeholders} trustlined
                  </div>
                </div>
                <Progress value={trustlinePercentage} className="h-2" />
              </div>

              <div>
                <div className="flex items-center justify-between mb-1">
                  <div className="text-sm font-medium">
                    Ready for Distribution
                  </div>
                  <div className="text-sm text-muted-foreground">
                    {readyStakeholders} of {totalStakeholders} ready
                  </div>
                </div>
                <Progress value={readyPercentage} className="h-2" />
              </div>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
