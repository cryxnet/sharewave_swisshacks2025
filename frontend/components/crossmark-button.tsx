"use client";

import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Coins, RefreshCw } from "lucide-react";
import { useToast } from "@/hooks/use-toast";
import sdk from "@crossmarkio/sdk";

interface CrossmarkPayButtonProps {
  destination: string;
  currency: string;
  issuer: string;
  value: string;
}

export default function CrossmarkPayButton({
  destination,
  currency,
  issuer,
  value,
}: CrossmarkPayButtonProps) {
  const { toast } = useToast();
  const [isPaying, setIsPaying] = useState(false);

  const handlePay = async () => {
    setIsPaying(true);

    try {
      // Step 1: Sign in to get the user's wallet address
      const signInResp = await sdk.methods.signInAndWait();
      const account = signInResp.response.address;

      // Step 2: Prepare the transaction
      const tx = {
        TransactionType: "Payment",
        Account: account,
        Destination: destination,
        Amount: {
          currency,
          issuer,
          value,
        },
      };

      // Step 3: Sign and submit the transaction
      const { response } = await sdk.methods.signAndSubmitAndWait(tx);

      // Step 4: Handle the response
      const txHash = response.data.resp.result.hash;

      toast({
        title: "Transaction Sent",
        description: `TX Hash: ${txHash}`,
      });
    } catch (error: any) {
      console.error("Crossmark error:", error);
      toast({
        title: "Payment Failed",
        description:
          error?.message || "Something went wrong during Crossmark payment",
        variant: "destructive",
      });
    } finally {
      setIsPaying(false);
    }
  };

  return (
    <Button
      disabled={isPaying}
      onClick={handlePay}
      className="w-full bg-gradient-to-r from-blue-600 to-cyan-500 hover:from-blue-700 hover:to-cyan-600"
    >
      {isPaying ? (
        <>
          <RefreshCw className="mr-2 h-4 w-4 animate-spin" />
          Waiting for Wallet...
        </>
      ) : (
        <>
          <Coins className="mr-2 h-4 w-4" />
          Pay with Crossmark
        </>
      )}
    </Button>
  );
}
