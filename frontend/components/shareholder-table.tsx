"use client";

import { useState, useEffect } from "react";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { Badge } from "@/components/ui/badge";
import { Skeleton } from "@/components/ui/skeleton";
import { useToast } from "@/hooks/use-toast";
import { AlertCircle, CheckCircle2, ExternalLink, XCircle } from "lucide-react";
import { Button } from "@/components/ui/button";

interface Stakeholder {
  wallet_address: string;
  required_rlusd: number;
  has_paid: boolean;
  has_trustline: boolean;
  tokens_distributed: boolean;
  status: string;
}

interface ShareholderTableProps {
  companyId: string;
  stakeholders: Stakeholder[];
  refreshKey: number;
  isDistributed: boolean;
}

export default function ShareholderTable({
  companyId,
  stakeholders: initialStakeholders,
  refreshKey,
  isDistributed,
}: ShareholderTableProps) {
  const { toast } = useToast();
  const [stakeholders, setStakeholders] =
    useState<Stakeholder[]>(initialStakeholders);
  const [isLoading, setIsLoading] = useState(false);

  // Update stakeholders when props change
  useEffect(() => {
    setStakeholders(initialStakeholders);
  }, [initialStakeholders, refreshKey]);

  // Format wallet address for display
  const formatWalletAddress = (address: string) => {
    if (address.length <= 12) return address;
    return `${address.substring(0, 6)}...${address.substring(
      address.length - 6
    )}`;
  };

  // Get status badge for a stakeholder
  const getStatusBadge = (stakeholder: Stakeholder) => {
    if (stakeholder.tokens_distributed) {
      return (
        <Badge
          variant="success"
          className="bg-green-500/20 text-green-500 hover:bg-green-500/30 hover:text-green-500"
        >
          <CheckCircle2 className="mr-1 h-3 w-3" />
          Completed
        </Badge>
      );
    }

    if (!stakeholder.has_paid && !stakeholder.has_trustline) {
      return (
        <Badge
          variant="destructive"
          className="bg-red-500/20 text-red-500 hover:bg-red-500/30 hover:text-red-500"
        >
          <AlertCircle className="mr-1 h-3 w-3" />
          Missing Payment & Trustline
        </Badge>
      );
    }

    if (!stakeholder.has_paid) {
      return (
        <Badge
          variant="destructive"
          className="bg-red-500/20 text-red-500 hover:bg-red-500/30 hover:text-red-500"
        >
          <AlertCircle className="mr-1 h-3 w-3" />
          Missing Payment
        </Badge>
      );
    }

    if (!stakeholder.has_trustline) {
      return (
        <Badge
          variant="destructive"
          className="bg-red-500/20 text-red-500 hover:bg-red-500/30 hover:text-red-500"
        >
          <AlertCircle className="mr-1 h-3 w-3" />
          Missing Trustline
        </Badge>
      );
    }

    return (
      <Badge
        variant="outline"
        className="bg-amber-500/20 text-amber-500 hover:bg-amber-500/30 hover:text-amber-500"
      >
        <CheckCircle2 className="mr-1 h-3 w-3" />
        Ready for Distribution
      </Badge>
    );
  };

  if (isLoading) {
    return (
      <div className="space-y-4">
        <Skeleton className="h-8 w-full" />
        <Skeleton className="h-8 w-full" />
        <Skeleton className="h-8 w-full" />
      </div>
    );
  }

  return (
    <div className="overflow-x-auto">
      <Table>
        <TableHeader>
          <TableRow>
            <TableHead>Wallet Address</TableHead>
            <TableHead className="text-right">Required RLUSD</TableHead>
            <TableHead className="text-center">Payment</TableHead>
            <TableHead className="text-center">Trustline</TableHead>
            <TableHead>Status</TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          {stakeholders.map((stakeholder) => (
            <TableRow key={stakeholder.wallet_address}>
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
                      <span className="sr-only">View on XRPL Explorer</span>
                    </a>
                  </Button>
                </div>
              </TableCell>
              <TableCell className="text-right">
                {stakeholder.required_rlusd.toLocaleString()} RLUSD
              </TableCell>
              <TableCell className="text-center">
                {stakeholder.has_paid ? (
                  <CheckCircle2 className="h-5 w-5 text-green-500 mx-auto" />
                ) : (
                  <XCircle className="h-5 w-5 text-red-500 mx-auto" />
                )}
              </TableCell>
              <TableCell className="text-center">
                {stakeholder.has_trustline ? (
                  <CheckCircle2 className="h-5 w-5 text-green-500 mx-auto" />
                ) : (
                  <XCircle className="h-5 w-5 text-red-500 mx-auto" />
                )}
              </TableCell>
              <TableCell>
                {stakeholder.status || getStatusBadge(stakeholder)}
              </TableCell>
            </TableRow>
          ))}
        </TableBody>
      </Table>
    </div>
  );
}
