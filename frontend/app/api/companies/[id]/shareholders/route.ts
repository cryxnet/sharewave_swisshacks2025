import { NextResponse } from "next/server"

// Mock shareholders data
const mockShareholders = {
  company_name: "TechVenture Inc.",
  symbol: "TECH",
  issuing_address: "rHb9CJAWyB4rj91VRWn96DkukG4bwdtyTh",
  shareholders: [
    {
      wallet_address: "rDrr8Lh4hgPu8yqrJ7x7ZMW74HzJvKsNS7",
      required_rlusd: 2500000.0,
      has_paid: true,
      has_trustline: true,
      tokens_distributed: false,
    },
    {
      wallet_address: "rJRi8WW24gt9X85PHAxfWNPCizMMhqUQwg",
      required_rlusd: 3750000.0,
      has_paid: true,
      has_trustline: false,
      tokens_distributed: false,
    },
    {
      wallet_address: "rLDYrujdKUfVx28T9vRDAbyJ7G2WVXKo4K",
      required_rlusd: 4375000.0,
      has_paid: false,
      has_trustline: false,
      tokens_distributed: false,
    },
  ],
}

export async function GET(request: Request, { params }: { params: { id: string } }) {
  try {
    const id = params.id

    // In a real implementation, you would fetch the shareholders from a database
    // For this mock, we'll just return the mock data

    return NextResponse.json(mockShareholders)
  } catch (error) {
    console.error("Error fetching shareholders:", error)
    return NextResponse.json({ error: "Internal server error" }, { status: 500 })
  }
}
