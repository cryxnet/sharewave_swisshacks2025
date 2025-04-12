"use client";

import { useState } from "react";
import {
  Card,
  CardContent,
  CardDescription,
  CardFooter,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Tabs, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { Badge } from "@/components/ui/badge";
import { useToast } from "@/hooks/use-toast";
import { ArrowDown, ArrowUp } from "lucide-react";
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  ReferenceLine,
} from "recharts";

interface TradingInterfaceProps {
  companyName: string;
  symbol: string;
  currentPrice: number;
}

// Mock data for price chart
const generatePriceData = (basePrice: number) => {
  const data = [];
  let price = basePrice * 0.9;
  const now = new Date();

  for (let i = 30; i >= 0; i--) {
    const date = new Date(now);
    date.setDate(date.getDate() - i);

    // Random price movement with slight upward trend
    const change = (Math.random() - 0.45) * 0.05 * basePrice;
    price += change;

    data.push({
      date: date.toLocaleDateString(),
      price: price.toFixed(4),
    });
  }

  return data;
};

// Mock data for order book
const generateOrderBook = (currentPrice: number) => {
  const asks = [];
  const bids = [];

  // Generate asks (sell orders)
  let askPrice = currentPrice * 1.001;
  for (let i = 0; i < 8; i++) {
    askPrice += Math.random() * 0.002 * currentPrice;
    const size = Math.floor(Math.random() * 1000) + 100;
    asks.push({
      price: askPrice.toFixed(4),
      size,
      total: (askPrice * size).toFixed(2),
    });
  }

  // Generate bids (buy orders)
  let bidPrice = currentPrice * 0.999;
  for (let i = 0; i < 8; i++) {
    bidPrice -= Math.random() * 0.002 * currentPrice;
    const size = Math.floor(Math.random() * 1000) + 100;
    bids.push({
      price: bidPrice.toFixed(4),
      size,
      total: (bidPrice * size).toFixed(2),
    });
  }

  // Sort asks in ascending order and bids in descending order
  asks.sort((a, b) => Number.parseFloat(a.price) - Number.parseFloat(b.price));
  bids.sort((a, b) => Number.parseFloat(b.price) - Number.parseFloat(a.price));

  return { asks, bids };
};

// Mock data for recent trades
const generateRecentTrades = (currentPrice: number) => {
  const trades = [];
  const now = new Date();

  for (let i = 0; i < 10; i++) {
    const priceVariation = (Math.random() - 0.5) * 0.01 * currentPrice;
    const price = currentPrice + priceVariation;
    const size = Math.floor(Math.random() * 500) + 50;
    const isBuy = Math.random() > 0.5;

    const tradeTime = new Date(now);
    tradeTime.setMinutes(
      tradeTime.getMinutes() - i * 2 - Math.floor(Math.random() * 3)
    );

    trades.push({
      time: tradeTime.toLocaleTimeString([], {
        hour: "2-digit",
        minute: "2-digit",
        second: "2-digit",
      }),
      price: price.toFixed(4),
      size,
      value: (price * size).toFixed(2),
      side: isBuy ? "buy" : "sell",
    });
  }

  return trades;
};

export default function TradingInterface({
  companyName,
  symbol,
  currentPrice,
}: TradingInterfaceProps) {
  const { toast } = useToast();
  const [tradeType, setTradeType] = useState<"buy" | "sell">("buy");
  const [quantity, setQuantity] = useState("");
  const [price, setPrice] = useState(currentPrice.toFixed(4));
  const [orderType, setOrderType] = useState("limit");

  // Generate mock data
  const priceData = generatePriceData(currentPrice);
  const { asks, bids } = generateOrderBook(currentPrice);
  const recentTrades = generateRecentTrades(currentPrice);

  // Calculate total value
  const totalValue =
    quantity && price
      ? (Number.parseFloat(quantity) * Number.parseFloat(price)).toFixed(2)
      : "0.00";

  // Handle trade submission
  const handleSubmitTrade = () => {
    if (!quantity || Number.parseFloat(quantity) <= 0) {
      toast({
        title: "Invalid quantity",
        description: "Please enter a valid quantity",
        variant: "destructive",
      });
      return;
    }

    toast({
      title: "Order submitted",
      description: `${
        tradeType === "buy" ? "Buy" : "Sell"
      } ${quantity} ${symbol} at $${price} per token`,
    });

    // Reset form
    setQuantity("");
  };

  return (
    <div className="grid gap-6 lg:grid-cols-3">
      {/* Price Chart */}
      <Card className="lg:col-span-2">
        <CardHeader>
          <CardTitle className="flex items-center justify-between">
            <span>
              {companyName} ({symbol})
            </span>
            <div className="text-xl">
              <span className="mr-2">${currentPrice.toFixed(4)}</span>
              <Badge
                variant={Math.random() > 0.5 ? "success" : "destructive"}
                className="text-xs"
              >
                {Math.random() > 0.5 ? "+" : "-"}
                {(Math.random() * 2).toFixed(2)}%
              </Badge>
            </div>
          </CardTitle>
          <CardDescription>Price chart (30 days)</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="h-[300px] w-full">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={priceData}>
                <CartesianGrid
                  strokeDasharray="3 3"
                  stroke="rgba(255,255,255,0.1)"
                />
                <XAxis
                  dataKey="date"
                  tick={{ fontSize: 12 }}
                  tickFormatter={(value) => {
                    const date = new Date(value);
                    return `${date.getDate()}/${date.getMonth() + 1}`;
                  }}
                />
                <YAxis
                  domain={["auto", "auto"]}
                  tick={{ fontSize: 12 }}
                  tickFormatter={(value) => `$${value}`}
                />
                <Tooltip
                  formatter={(value) => [`$${value}`, "Price"]}
                  labelFormatter={(label) => `Date: ${label}`}
                  contentStyle={{
                    backgroundColor: "rgba(22, 22, 22, 0.9)",
                    border: "1px solid #333",
                  }}
                />
                <ReferenceLine
                  y={currentPrice}
                  stroke="#888"
                  strokeDasharray="3 3"
                />
                <Line
                  type="monotone"
                  dataKey="price"
                  stroke="#3b82f6"
                  strokeWidth={2}
                  dot={false}
                  activeDot={{ r: 6 }}
                />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </CardContent>
      </Card>

      {/* Trade Form */}
      <Card>
        <CardHeader>
          <CardTitle>Trade {symbol}</CardTitle>
          <CardDescription>Buy or sell tokenized shares</CardDescription>
        </CardHeader>
        <CardContent>
          <Tabs
            defaultValue="limit"
            className="w-full"
            onValueChange={(value) => setOrderType(value)}
          >
            <TabsList className="grid w-full grid-cols-2 mb-4">
              <TabsTrigger value="limit">Limit</TabsTrigger>
              <TabsTrigger value="market">Market</TabsTrigger>
            </TabsList>

            <div className="space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <Button
                  variant={tradeType === "buy" ? "default" : "outline"}
                  className={
                    tradeType === "buy" ? "bg-green-600 hover:bg-green-700" : ""
                  }
                  onClick={() => setTradeType("buy")}
                >
                  <ArrowDown className="mr-2 h-4 w-4" />
                  Buy
                </Button>
                <Button
                  variant={tradeType === "sell" ? "default" : "outline"}
                  className={
                    tradeType === "sell" ? "bg-red-600 hover:bg-red-700" : ""
                  }
                  onClick={() => setTradeType("sell")}
                >
                  <ArrowUp className="mr-2 h-4 w-4" />
                  Sell
                </Button>
              </div>

              <div className="space-y-2">
                <Label htmlFor="quantity">Quantity</Label>
                <Input
                  id="quantity"
                  type="number"
                  placeholder="0"
                  value={quantity}
                  onChange={(e) => setQuantity(e.target.value)}
                />
              </div>

              {orderType === "limit" && (
                <div className="space-y-2">
                  <Label htmlFor="price">Price per token</Label>
                  <Input
                    id="price"
                    type="number"
                    placeholder={currentPrice.toString()}
                    value={price}
                    onChange={(e) => setPrice(e.target.value)}
                    step="0.0001"
                  />
                </div>
              )}

              <div className="pt-2 border-t border-border/50">
                <div className="flex justify-between text-sm mb-2">
                  <span className="text-muted-foreground">Total Value:</span>
                  <span className="font-medium">${totalValue} RLUSD</span>
                </div>
                <div className="flex justify-between text-sm">
                  <span className="text-muted-foreground">Fee (0.5%):</span>
                  <span className="font-medium">
                    ${(Number.parseFloat(totalValue) * 0.005).toFixed(2)} RLUSD
                  </span>
                </div>
              </div>
            </div>
          </Tabs>
        </CardContent>
        <CardFooter>
          <Button
            className="w-full"
            onClick={handleSubmitTrade}
            disabled={!quantity || Number.parseFloat(quantity) <= 0}
            variant={tradeType === "buy" ? "default" : "destructive"}
          >
            {tradeType === "buy" ? "Buy" : "Sell"} {symbol}
          </Button>
        </CardFooter>
      </Card>

      {/* Order Book */}
      <Card className="lg:col-span-2">
        <CardHeader>
          <CardTitle>Order Book</CardTitle>
          <CardDescription>Current buy and sell orders</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-2 gap-4">
            <div>
              <div className="flex justify-between text-sm font-medium text-muted-foreground mb-2">
                <span>Price (RLUSD)</span>
                <span>Size ({symbol})</span>
                <span>Total</span>
              </div>
              <div className="space-y-1">
                {asks.map((ask, index) => (
                  <div
                    key={index}
                    className="flex justify-between text-sm text-red-500"
                  >
                    <span>${ask.price}</span>
                    <span>{ask.size}</span>
                    <span>${ask.total}</span>
                  </div>
                ))}
              </div>
            </div>

            <div>
              <div className="flex justify-between text-sm font-medium text-muted-foreground mb-2">
                <span>Price (RLUSD)</span>
                <span>Size ({symbol})</span>
                <span>Total</span>
              </div>
              <div className="space-y-1">
                {bids.map((bid, index) => (
                  <div
                    key={index}
                    className="flex justify-between text-sm text-green-500"
                  >
                    <span>${bid.price}</span>
                    <span>{bid.size}</span>
                    <span>${bid.total}</span>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Recent Trades */}
      <Card>
        <CardHeader>
          <CardTitle>Recent Trades</CardTitle>
          <CardDescription>Latest market activity</CardDescription>
        </CardHeader>
        <CardContent>
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Time</TableHead>
                <TableHead>Price</TableHead>
                <TableHead>Size</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {recentTrades.map((trade, index) => (
                <TableRow key={index}>
                  <TableCell className="text-xs">{trade.time}</TableCell>
                  <TableCell
                    className={
                      trade.side === "buy" ? "text-green-500" : "text-red-500"
                    }
                  >
                    ${trade.price}
                  </TableCell>
                  <TableCell>{trade.size}</TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </CardContent>
      </Card>
    </div>
  );
}
