"use client";

import type React from "react";
import { useState, useRef, useEffect } from "react";
import { useRouter } from "next/navigation";
import { zodResolver } from "@hookform/resolvers/zod";
import { useForm } from "react-hook-form";
import { z } from "zod";
import {
  X,
  Plus,
  AlertCircle,
  CheckCircle2,
  UploadIcon as FileUpload,
  Upload,
  RefreshCw,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardFooter,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import {
  Form,
  FormControl,
  FormDescription,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from "@/components/ui/form";
import { Input } from "@/components/ui/input";
import { useToast } from "@/hooks/use-toast";
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";

// Define the form schema with validation
const formSchema = z.object({
  name: z.string().min(2, "Company name must be at least 2 characters"),
  symbol: z
    .string()
    .min(1, "Symbol is required")
    .max(10, "Symbol must be 10 characters or less"),
  totalSupply: z.coerce.number().positive("Total supply must be positive"),
  totalValuationUsd: z.coerce.number().positive("Valuation must be positive"),
  liquidityPercent: z.coerce
    .number()
    .min(1, "Liquidity must be at least 1%")
    .max(99, "Liquidity must be less than 100%"),
  shareholders: z.array(
    z.object({
      walletAddress: z.string().min(20, "Enter a valid XRP wallet address"),
      percent: z.coerce.number().positive("Percentage must be positive"),
    })
  ),
});

type FormValues = z.infer<typeof formSchema>;

export default function RegisterPage() {
  const router = useRouter();
  const { toast } = useToast();
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [totalPercentage, setTotalPercentage] = useState(0);
  const [documentUploaded, setDocumentUploaded] = useState(false);
  const [isUploading, setIsUploading] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  // Initialize form with default values
  const form = useForm<FormValues>({
    resolver: zodResolver(formSchema),
    defaultValues: {
      name: "",
      symbol: "",
      totalSupply: 1000000,
      totalValuationUsd: 1000000,
      liquidityPercent: 10,
      shareholders: [{ walletAddress: "", percent: 0 }],
    },
  });

  // Watch for changes to calculate total percentage
  const shareholders = form.watch("shareholders");
  const liquidityPercent = form.watch("liquidityPercent");

  // Calculate total percentage whenever shareholders or liquidity changes
  useEffect(() => {
    const shareholderTotal = shareholders.reduce(
      (sum, shareholder) => sum + (Number(shareholder.percent) || 0),
      0
    );
    setTotalPercentage(shareholderTotal + (Number(liquidityPercent) || 0));
  }, [shareholders, liquidityPercent]);

  // Add a new shareholder field
  const addShareholder = () => {
    const currentShareholders = form.getValues("shareholders");
    form.setValue("shareholders", [
      ...currentShareholders,
      { walletAddress: "", percent: 0 },
    ]);
  };

  // Remove a shareholder field
  const removeShareholder = (index: number) => {
    const currentShareholders = form.getValues("shareholders");
    if (currentShareholders.length > 1) {
      form.setValue(
        "shareholders",
        currentShareholders.filter((_, i) => i !== index)
      );
    }
  };

  // Handle file upload
  const handleFileUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files.length > 0) {
      setIsUploading(true);

      // Simulate upload process with a 3-second delay
      setTimeout(() => {
        setIsUploading(false);
        setDocumentUploaded(true);

        toast({
          title: "Document Uploaded Successfully",
          description: `File: ${e.target.files?.[0].name}`,
        });
      }, 3000);
    }
  };

  // Trigger file input click
  const triggerFileUpload = () => {
    fileInputRef.current?.click();
  };

  // Handle form submission
  const onSubmit = async (data: FormValues) => {
    if (Math.abs(totalPercentage - 100) > 0.01) {
      toast({
        title: "Validation Error",
        description:
          "Total percentage (shareholders + liquidity) must equal 100%",
        variant: "destructive",
      });
      return;
    }

    if (!documentUploaded) {
      toast({
        title: "Document Required",
        description:
          "Please upload the due diligence document before registering",
        variant: "destructive",
      });
      return;
    }

    setIsSubmitting(true);

    try {
      // Format the data for the API
      const apiData = {
        name: data.name,
        symbol: data.symbol,
        total_supply: data.totalSupply,
        total_valuation_usd: data.totalValuationUsd,
        liquidity_percent: data.liquidityPercent,
        shareholders: data.shareholders.map((sh) => ({
          wallet_address: sh.walletAddress,
          percent: sh.percent,
        })),
      };

      // Call the API to register the company
      const response = await fetch("http://localhost:8000/companies", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(apiData),
      });

      const result = await response.json();

      if (!response.ok) {
        throw new Error(result.message || "Failed to register company");
      }

      toast({
        title: "Company Registered Successfully",
        description: `Company ID: ${result.company_id}`,
      });

      // Redirect to the company detail page
      router.push(`/company/${result.company_id}`);
    } catch (error) {
      console.error("Registration error:", error);
      toast({
        title: "Registration Failed",
        description:
          error instanceof Error
            ? error.message
            : "An unexpected error occurred",
        variant: "destructive",
      });
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="container max-w-4xl mx-auto py-8 px-4 md:px-6">
      <h1 className="text-3xl font-bold tracking-tight mb-6">
        Register a New Company
      </h1>

      <Card className="border border-border/50 bg-card/50 backdrop-blur-sm">
        <CardHeader>
          <CardTitle>Company Registration</CardTitle>
          <CardDescription>
            Create a new tokenized company on the XRP Ledger
          </CardDescription>
        </CardHeader>
        <CardContent>
          <Form {...form}>
            <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-6">
              <div className="grid gap-6 md:grid-cols-2">
                <FormField
                  control={form.control}
                  name="name"
                  render={({ field }) => (
                    <FormItem>
                      <FormLabel>Company Name</FormLabel>
                      <FormControl>
                        <Input placeholder="My Company" {...field} />
                      </FormControl>
                      <FormDescription>
                        The full name of your company
                      </FormDescription>
                      <FormMessage />
                    </FormItem>
                  )}
                />

                <FormField
                  control={form.control}
                  name="symbol"
                  render={({ field }) => (
                    <FormItem>
                      <FormLabel>Token Symbol</FormLabel>
                      <FormControl>
                        <Input placeholder="MYCO" {...field} />
                      </FormControl>
                      <FormDescription>
                        A short ticker symbol for your token
                      </FormDescription>
                      <FormMessage />
                    </FormItem>
                  )}
                />
              </div>

              <div className="grid gap-6 md:grid-cols-3">
                <FormField
                  control={form.control}
                  name="totalSupply"
                  render={({ field }) => (
                    <FormItem>
                      <FormLabel>Total Token Supply</FormLabel>
                      <FormControl>
                        <Input type="number" min="1" {...field} />
                      </FormControl>
                      <FormDescription>
                        Number of tokens to create
                      </FormDescription>
                      <FormMessage />
                    </FormItem>
                  )}
                />

                <FormField
                  control={form.control}
                  name="totalValuationUsd"
                  render={({ field }) => (
                    <FormItem>
                      <FormLabel>Total Valuation (USD)</FormLabel>
                      <FormControl>
                        <Input type="number" min="1" {...field} />
                      </FormControl>
                      <FormDescription>
                        Company valuation in USD
                      </FormDescription>
                      <FormMessage />
                    </FormItem>
                  )}
                />

                <FormField
                  control={form.control}
                  name="liquidityPercent"
                  render={({ field }) => (
                    <FormItem>
                      <FormLabel>Liquidity Percentage</FormLabel>
                      <FormControl>
                        <Input
                          type="number"
                          min="1"
                          max="99"
                          step="0.1"
                          {...field}
                          onChange={(e) => {
                            field.onChange(e);
                            setTimeout(() => {
                              const shareholderTotal = shareholders.reduce(
                                (sum, shareholder) =>
                                  sum + (Number(shareholder.percent) || 0),
                                0
                              );
                              setTotalPercentage(
                                shareholderTotal + Number(e.target.value || "0")
                              );
                            }, 100);
                          }}
                        />
                      </FormControl>
                      <FormDescription>Percentage for AMM pool</FormDescription>
                      <FormMessage />
                    </FormItem>
                  )}
                />
              </div>

              {/* Due Diligence Document Upload Section */}
              <div className="space-y-4">
                <div>
                  <h3 className="text-lg font-medium mb-2">
                    Due Diligence Document
                  </h3>
                  <div className="rounded-lg border border-dashed border-border p-6 bg-card/30">
                    <input
                      type="file"
                      ref={fileInputRef}
                      onChange={handleFileUpload}
                      className="hidden"
                      accept=".pdf,.doc,.docx,.xls,.xlsx"
                    />

                    {!documentUploaded ? (
                      <div className="flex flex-col items-center justify-center space-y-4">
                        <div className="h-16 w-16 rounded-full bg-primary/10 flex items-center justify-center">
                          <FileUpload className="h-8 w-8 text-primary" />
                        </div>
                        <div className="text-center">
                          <h4 className="font-medium">
                            Upload Due Diligence Document
                          </h4>
                          <p className="text-sm text-muted-foreground mt-1">
                            Upload a document containing all metadata and due
                            diligence information
                          </p>
                        </div>
                        <Button
                          type="button"
                          variant="outline"
                          onClick={triggerFileUpload}
                          disabled={isUploading}
                          className="flex items-center gap-2"
                        >
                          {isUploading ? (
                            <>
                              <RefreshCw className="h-4 w-4 animate-spin" />
                              Uploading...
                            </>
                          ) : (
                            <>
                              <Upload className="h-4 w-4" />
                              Select Document
                            </>
                          )}
                        </Button>
                      </div>
                    ) : (
                      <div className="flex items-center justify-between">
                        <div className="flex items-center gap-3">
                          <div className="h-10 w-10 rounded-full bg-green-500/20 flex items-center justify-center">
                            <CheckCircle2 className="h-5 w-5 text-green-500" />
                          </div>
                          <div>
                            <h4 className="font-medium">Document Uploaded</h4>
                            <p className="text-sm text-muted-foreground">
                              Due diligence document verified
                            </p>
                          </div>
                        </div>
                        <Button
                          type="button"
                          variant="outline"
                          size="sm"
                          onClick={triggerFileUpload}
                          className="flex items-center gap-1"
                        >
                          <Upload className="h-3 w-3" />
                          Change
                        </Button>
                      </div>
                    )}
                  </div>
                </div>
              </div>

              <div className="space-y-4">
                <div className="flex items-center justify-between">
                  <h3 className="text-lg font-medium">Initial Shareholders</h3>
                  <Button
                    type="button"
                    variant="outline"
                    size="sm"
                    onClick={addShareholder}
                    className="flex items-center gap-1"
                  >
                    <Plus className="h-4 w-4" /> Add Shareholder
                  </Button>
                </div>

                {shareholders.map((_, index) => (
                  <div
                    key={index}
                    className="grid grid-cols-12 gap-4 items-center"
                  >
                    <div className="col-span-7">
                      <FormField
                        control={form.control}
                        name={`shareholders.${index}.walletAddress`}
                        render={({ field }) => (
                          <FormItem>
                            <FormLabel className={index !== 0 ? "sr-only" : ""}>
                              Wallet Address
                            </FormLabel>
                            <FormControl>
                              <Input placeholder="rXYZ..." {...field} />
                            </FormControl>
                            <FormMessage />
                          </FormItem>
                        )}
                      />
                    </div>

                    <div className="col-span-4">
                      <FormField
                        control={form.control}
                        name={`shareholders.${index}.percent`}
                        render={({ field }) => (
                          <FormItem>
                            <FormLabel className={index !== 0 ? "sr-only" : ""}>
                              Percentage
                            </FormLabel>
                            <FormControl>
                              <Input
                                type="number"
                                min="0.1"
                                step="0.1"
                                placeholder="%"
                                {...field}
                                onChange={(e) => {
                                  field.onChange(e);
                                  setTimeout(() => {
                                    const newShareholders =
                                      form.getValues("shareholders");
                                    const shareholderTotal =
                                      newShareholders.reduce(
                                        (sum, sh) =>
                                          sum + (Number(sh.percent) || 0),
                                        0
                                      );
                                    setTotalPercentage(
                                      shareholderTotal +
                                        Number(
                                          form.getValues("liquidityPercent") ||
                                            "0"
                                        )
                                    );
                                  }, 100);
                                }}
                              />
                            </FormControl>
                            <FormMessage />
                          </FormItem>
                        )}
                      />
                    </div>

                    <div className="col-span-1 flex justify-center">
                      {shareholders.length > 1 && (
                        <Button
                          type="button"
                          variant="ghost"
                          size="icon"
                          onClick={() => removeShareholder(index)}
                          className="h-10 w-10 text-muted-foreground hover:text-destructive"
                        >
                          <X className="h-4 w-4" />
                          <span className="sr-only">Remove</span>
                        </Button>
                      )}
                    </div>
                  </div>
                ))}
              </div>

              <div className="rounded-lg border p-4 bg-card/30">
                <div className="flex items-center justify-between">
                  <div>
                    <h4 className="font-medium">Total Allocation</h4>
                    <p className="text-sm text-muted-foreground">
                      Shareholders + Liquidity must equal 100%
                    </p>
                  </div>
                  <div className="flex items-center gap-2">
                    <div
                      className={`text-lg font-bold ${
                        Math.abs(totalPercentage - 100) < 0.01
                          ? "text-green-500"
                          : "text-amber-500"
                      }`}
                    >
                      {Number(totalPercentage).toFixed(1)}%
                    </div>
                    {Math.abs(totalPercentage - 100) < 0.01 ? (
                      <CheckCircle2 className="h-5 w-5 text-green-500" />
                    ) : (
                      <AlertCircle className="h-5 w-5 text-amber-500" />
                    )}
                  </div>
                </div>

                <div className="mt-4 h-2 w-full bg-muted rounded-full overflow-hidden">
                  <div
                    className={`h-full ${
                      Math.abs(totalPercentage - 100) < 0.01
                        ? "bg-green-500"
                        : "bg-amber-500"
                    }`}
                    style={{
                      width: `${Math.min(Number(totalPercentage), 100)}%`,
                    }}
                  />
                </div>
              </div>

              {Math.abs(totalPercentage - 100) > 0.01 && (
                <Alert variant="warning">
                  <AlertCircle className="h-4 w-4" />
                  <AlertTitle>Allocation Warning</AlertTitle>
                  <AlertDescription>
                    Total allocation (shareholders + liquidity) must equal
                    exactly 100%. Current total:{" "}
                    {Number(totalPercentage).toFixed(1)}%
                  </AlertDescription>
                </Alert>
              )}

              {!documentUploaded && (
                <Alert variant="warning">
                  <AlertCircle className="h-4 w-4" />
                  <AlertTitle>Document Required</AlertTitle>
                  <AlertDescription>
                    Please upload the due diligence document to enable
                    registration
                  </AlertDescription>
                </Alert>
              )}

              <CardFooter className="flex justify-end px-0 pb-0">
                <Button
                  type="submit"
                  disabled={
                    isSubmitting ||
                    Math.abs(totalPercentage - 100) > 0.01 ||
                    !documentUploaded
                  }
                  className="bg-gradient-to-r from-blue-600 to-cyan-500 hover:from-blue-700 hover:to-cyan-600"
                >
                  {isSubmitting ? "Registering..." : "Register Company"}
                </Button>
              </CardFooter>
            </form>
          </Form>
        </CardContent>
      </Card>
    </div>
  );
}
