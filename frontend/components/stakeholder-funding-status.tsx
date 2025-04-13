"use client";
import { Card, CardContent } from "@/components/ui/card";
import { Progress } from "@/components/ui/progress";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import {
  Coins,
  AlertCircle,
  CheckCircle2,
  XCircle,
  ExternalLink,
  RefreshCw,
  Clock,
} from "lucide-react";
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";
import CrossmarkPayButton from "@/components/crossmark-button";

// Define types
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

interface Stakeholder {
  wallet_address: string;
  required_rlusd: number;
  has_paid: boolean;
  has_trustline: boolean;
  tokens_distributed: boolean;
  status?: string;
}

interface StakeholderFundingStatusProps {
  company: Company;
  stakeholders: Stakeholder[];
  refreshKey: number;
  onDistribute: () => void;
  isDistributing: boolean;
}

// Define the Crossmark wallet URL.
// You can override this by defining NEXT_PUBLIC_CROSSMARK_WALLET_URL in your environment.
const CROSSMARK_WALLET_URL =
  process.env.NEXT_PUBLIC_CROSSMARK_WALLET_URL ||
  "https://wallet.crossmark.example.com";

export default function StakeholderFundingStatus({
  company,
  stakeholders,
  refreshKey,
  onDistribute,
  isDistributing,
}: StakeholderFundingStatusProps) {
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

  const allStakeholdersReady = stakeholders.every(
    (sh) => sh.has_paid && sh.has_trustline
  );

  // Format wallet address for display
  const formatWalletAddress = (address: string) => {
    if (address.length <= 12) return address;
    return `${address.substring(0, 6)}...${address.substring(
      address.length - 6
    )}`;
  };

  return (
    <div className="space-y-6">
      <Card className="bg-gradient-to-br from-blue-900/30 to-cyan-900/30 border-blue-500/20">
        <CardContent className="pt-6">
          <div className="grid gap-6 md:grid-cols-2">
            <div>
              <div className="flex items-center gap-3 mb-4">
                <div className="h-10 w-10 rounded-full bg-blue-500/20 flex items-center justify-center">
                  <Clock className="h-5 w-5 text-blue-400" />
                </div>
                <div>
                  <h2 className="text-xl font-bold">Waiting for Funds</h2>
                  <p className="text-muted-foreground">
                    {readyStakeholders} of {totalStakeholders} stakeholders
                    ready
                  </p>
                </div>
              </div>

              <div className="space-y-4">
                <div>
                  <div className="flex items-center justify-between mb-1">
                    <div className="text-sm font-medium flex items-center gap-1.5">
                      <div className="h-2 w-2 rounded-full bg-green-500"></div>
                      Payment Status
                    </div>
                    <div className="text-sm text-muted-foreground">
                      {paidStakeholders} of {totalStakeholders} paid
                    </div>
                  </div>
                  <Progress value={paidPercentage} className="h-2" />
                </div>

                <div>
                  <div className="flex items-center justify-between mb-1">
                    <div className="text-sm font-medium flex items-center gap-1.5">
                      <div className="h-2 w-2 rounded-full bg-blue-500"></div>
                      Trustline Status
                    </div>
                    <div className="text-sm text-muted-foreground">
                      {trustlineStakeholders} of {totalStakeholders} trustlined
                    </div>
                  </div>
                  <Progress value={trustlinePercentage} className="h-2" />
                </div>

                <div>
                  <div className="flex items-center justify-between mb-1">
                    <div className="text-sm font-medium flex items-center gap-1.5">
                      <div className="h-2 w-2 rounded-full bg-cyan-500"></div>
                      Ready for Distribution
                    </div>
                    <div className="text-sm text-muted-foreground">
                      {readyStakeholders} of {totalStakeholders} ready
                    </div>
                  </div>
                  <Progress value={readyPercentage} className="h-2" />
                </div>
              </div>
            </div>

            <div className="flex flex-col justify-center">
              <div className="space-y-4">
                <div className="text-center">
                  <div className="inline-flex items-center justify-center h-20 w-20 rounded-full bg-blue-500/20 mb-3">
                    <div className="text-2xl font-bold">
                      {readyPercentage.toFixed(0)}%
                    </div>
                  </div>
                  <h3 className="text-lg font-medium">Completion Status</h3>
                </div>

                {allStakeholdersReady ? (
                  <Alert className="bg-green-500/20 border-green-500/30">
                    <CheckCircle2 className="h-4 w-4 text-green-500" />
                    <AlertTitle>All Stakeholders Ready</AlertTitle>
                    <AlertDescription>
                      All stakeholders have paid and established trustlines.
                      Ready to distribute tokens.
                    </AlertDescription>
                  </Alert>
                ) : (
                  <Alert className="bg-amber-500/20 border-amber-500/30">
                    <AlertCircle className="h-4 w-4 text-amber-500" />
                    <AlertTitle>Waiting for Stakeholders</AlertTitle>
                    <AlertDescription>
                      Some stakeholders still need to complete payment or
                      establish trustlines.
                    </AlertDescription>
                  </Alert>
                )}

                <Button
                  onClick={onDistribute}
                  disabled={isDistributing || !allStakeholdersReady}
                  className="w-full bg-gradient-to-r from-blue-600 to-cyan-500 hover:from-blue-700 hover:to-cyan-600"
                >
                  {isDistributing ? (
                    <>
                      <RefreshCw className="mr-2 h-4 w-4 animate-spin" />
                      Processing...
                    </>
                  ) : (
                    <>
                      <Coins className="mr-2 h-4 w-4" />
                      Distribute Tokens
                    </>
                  )}
                </Button>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>

      <div className="bg-card rounded-lg border shadow-sm">
        <div className="p-6">
          <h2 className="text-xl font-bold mb-4">Stakeholder Payment Status</h2>
          <div className="overflow-x-auto">
            <Table>
              <TableHeader>
                <TableRow className="bg-muted/50">
                  <TableHead className="w-[30%]">Wallet Address</TableHead>
                  <TableHead className="text-right">Required Payment</TableHead>
                  <TableHead className="text-center">Payment</TableHead>
                  <TableHead className="text-center">Trustline</TableHead>
                  <TableHead>Status</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {stakeholders.map((stakeholder) => (
                  <TableRow
                    key={stakeholder.wallet_address}
                    className="hover:bg-muted/30"
                  >
                    <TableCell className="font-mono text-xs">
                      <div className="flex items-center gap-1">
                        {formatWalletAddress(stakeholder.wallet_address)}
                        <Button
                          variant="ghost"
                          size="icon"
                          className="h-6 w-6"
                          asChild
                        >
                          <a
                            href={`https://testnet.xrpl.org/accounts/${stakeholder.wallet_address}`}
                            target="_blank"
                            rel="noopener noreferrer"
                          >
                            <ExternalLink className="h-3 w-3" />
                            <span className="sr-only">
                              View on XRPL Explorer
                            </span>
                          </a>
                        </Button>
                      </div>
                    </TableCell>
                    <TableCell className="text-right font-medium">
                      {stakeholder.required_rlusd.toLocaleString()} RLUSD
                    </TableCell>
                    <TableCell className="text-center">
                      {stakeholder.has_paid ? (
                        <div className="flex items-center justify-center">
                          <Badge
                            variant="outline"
                            className="bg-green-500/20 text-green-500 border-green-500/30"
                          >
                            <CheckCircle2 className="mr-1 h-3 w-3" />
                            Paid
                          </Badge>
                        </div>
                      ) : (
                        <div className="flex items-center justify-center">
                          <Badge
                            variant="outline"
                            className="bg-red-500/20 text-red-500 border-red-500/30"
                          >
                            <XCircle className="mr-1 h-3 w-3" />
                            Unpaid
                          </Badge>
                        </div>
                      )}
                    </TableCell>
                    <TableCell className="text-center">
                      {stakeholder.has_trustline ? (
                        <div className="flex items-center justify-center">
                          <Badge
                            variant="outline"
                            className="bg-green-500/20 text-green-500 border-green-500/30"
                          >
                            <CheckCircle2 className="mr-1 h-3 w-3" />
                            Established
                          </Badge>
                        </div>
                      ) : (
                        <div className="flex items-center justify-center">
                          <Badge
                            variant="outline"
                            className="bg-red-500/20 text-red-500 border-red-500/30"
                          >
                            <XCircle className="mr-1 h-3 w-3" />
                            Missing
                          </Badge>
                        </div>
                      )}
                    </TableCell>
                    <TableCell>
                      {stakeholder.has_paid && stakeholder.has_trustline ? (
                        <Badge className="bg-green-500/20 text-green-500 hover:bg-green-500/30 hover:text-green-500 border-green-500/30">
                          <CheckCircle2 className="mr-1 h-3 w-3" />
                          Ready
                        </Badge>
                      ) : !stakeholder.has_paid &&
                        !stakeholder.has_trustline ? (
                        <Badge
                          variant="destructive"
                          className="bg-red-500/20 text-red-500 border-red-500/30"
                        >
                          <AlertCircle className="mr-1 h-3 w-3" />
                          Action Required
                        </Badge>
                      ) : (
                        <Badge
                          variant="outline"
                          className="bg-amber-500/20 text-amber-500 border-amber-500/30"
                        >
                          <AlertCircle className="mr-1 h-3 w-3" />
                          Partially Complete
                        </Badge>
                      )}
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </div>
        </div>
      </div>

      {/* CTA Button to redirect to Crossmark Wallet */}
      <div className="mt-6 text-center">
        <CrossmarkPayButton
          destination="rLpXb2V556Mg3oYKVUqPgEaSqhK1LfcRZ1"
          currency="524C555344000000000000000000000000000000"
          issuer="rQhWct2fv4Vc4KRjRgMrxa8xPN9Zx9iLKV"
          value="8.89"
        />
      </div>
    </div>
  );
}
