"use client";

import { useState } from "react";
import { Card } from "@/components/ui/card";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Button } from "@/components/ui/button";
import { ExternalLink } from "lucide-react";
import {
  PieChart,
  Pie,
  Cell,
  ResponsiveContainer,
  Tooltip,
  Legend,
} from "recharts";

interface TokenHolder {
  wallet_address: string;
  balance: number;
}

interface TokenHoldingsChartProps {
  tokenHolders: TokenHolder[];
  symbol: string;
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

export default function TokenHoldingsChart({
  tokenHolders,
  symbol,
  isDistributed,
}: TokenHoldingsChartProps) {
  const [activeTab, setActiveTab] = useState("chart");

  // Format wallet address for display
  const formatWalletAddress = (address: string) => {
    if (address.length <= 12) return address;
    return `${address.substring(0, 6)}...${address.substring(
      address.length - 6
    )}`;
  };

  // Calculate total supply
  const totalSupply = tokenHolders.reduce(
    (sum, holder) => sum + holder.balance,
    0
  );

  // Prepare data for the pie chart
  const chartData = tokenHolders.map((holder) => {
    const percentOwnership = (holder.balance / totalSupply) * 100;
    return {
      name: formatWalletAddress(holder.wallet_address),
      value: holder.balance,
      fullAddress: holder.wallet_address,
      balance: holder.balance,
      percent: percentOwnership,
    };
  });

  // Custom tooltip for the pie chart
  const CustomTooltip = ({ active, payload }: any) => {
    if (active && payload && payload.length) {
      const data = payload[0].payload;
      return (
        <Card className="p-3 bg-background border shadow-lg">
          <div className="font-medium">{data.name}</div>
          <div className="text-sm text-muted-foreground">
            {data.fullAddress}
          </div>
          <div className="mt-1 font-medium">
            {data.balance} {symbol} ({data.percent.toFixed(2)}%)
          </div>
        </Card>
      );
    }
    return null;
  };

  if (!isDistributed && tokenHolders.length === 0) {
    return (
      <div className="text-center py-12 text-muted-foreground">
        <p>No token holdings data available yet.</p>
        <p className="text-sm mt-2">Tokens have not been distributed.</p>
      </div>
    );
  }

  return (
    <div>
      <Tabs value={activeTab} onValueChange={setActiveTab} className="w-full">
        <TabsList className="grid w-full grid-cols-2 mb-4">
          <TabsTrigger value="chart">Chart View</TabsTrigger>
          <TabsTrigger value="table">Table View</TabsTrigger>
        </TabsList>

        <TabsContent value="chart" className="pt-4">
          <div className="h-[400px] w-full">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie
                  data={chartData}
                  cx="50%"
                  cy="50%"
                  labelLine={false}
                  outerRadius={150}
                  fill="#8884d8"
                  dataKey="value"
                >
                  {chartData.map((entry, index) => (
                    <Cell
                      key={`cell-${index}`}
                      fill={COLORS[index % COLORS.length]}
                    />
                  ))}
                </Pie>
                <Tooltip content={<CustomTooltip />} />
                <Legend />
              </PieChart>
            </ResponsiveContainer>
          </div>
        </TabsContent>

        <TabsContent value="table">
          <div className="overflow-x-auto">
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Wallet Address</TableHead>
                  <TableHead>Token Balance</TableHead>
                  <TableHead className="text-right">Ownership %</TableHead>
                  <TableHead></TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {chartData.map((holder) => (
                  <TableRow key={holder.fullAddress}>
                    <TableCell className="font-mono text-xs">
                      {holder.name}
                    </TableCell>
                    <TableCell>
                      {holder.balance} {symbol}
                    </TableCell>
                    <TableCell className="text-right">
                      {holder.percent.toFixed(2)}%
                    </TableCell>
                    <TableCell>
                      <Button
                        variant="ghost"
                        size="icon"
                        className="h-8 w-8"
                        asChild
                      >
                        <a
                          href={`https://testnet.xrpl.org/accounts/${holder.fullAddress}`}
                          target="_blank"
                          rel="noopener noreferrer"
                        >
                          <ExternalLink className="h-4 w-4" />
                          <span className="sr-only">View on XRPL Explorer</span>
                        </a>
                      </Button>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </div>
        </TabsContent>
      </Tabs>
    </div>
  );
}
