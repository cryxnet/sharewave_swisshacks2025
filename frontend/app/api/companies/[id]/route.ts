import { NextResponse } from "next/server"

// Mock company data
const mockCompany = {
  company_id: "d068bef1-d458-4881-a300-22670eb741a1",
  name: "TechVenture Inc.",
  symbol: "TECH",
  total_supply: 10000000,
  total_valuation_usd: 12500000,
  liquidity_percent: 15.0,
  issuing_address: "rHb9CJAWyB4rj91VRWn96DkukG4bwdtyTh",
  state: "waiting_funds",
  shareholders: [
    {
      wallet_address: "rDrr8Lh4hgPu8yqrJ7x7ZMW74HzJvKsNS7",
      percent: 20.0,
      adjusted_percent: 23.5,
      required_rlusd: 2500000.0,
      has_paid: true,
      has_trustline: true,
      tokens_distributed: false,
    },
    {
      wallet_address: "rJRi8WW24gt9X85PHAxfWNPCizMMhqUQwg",
      percent: 30.0,
      adjusted_percent: 35.3,
      required_rlusd: 3750000.0,
      has_paid: true,
      has_trustline: false,
      tokens_distributed: false,
    },
    {
      wallet_address: "rLDYrujdKUfVx28T9vRDAbyJ7G2WVXKo4K",
      percent: 35.0,
      adjusted_percent: 41.2,
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

    // In a real implementation, you would fetch the company from a database
    // For this mock, we'll just return the mock data

    return NextResponse.json(mockCompany)
  } catch (error) {
    console.error("Error fetching company:", error)
    return NextResponse.json({ error: "Internal server error" }, { status: 500 })
  }
}
