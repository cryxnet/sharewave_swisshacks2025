import { NextResponse } from "next/server"

// Mock token holdings data
const mockTokenHoldings = {
  token_holdings: [
    {
      "Wallet Address": "rDrr8Lh4hgPu8yqrJ7x7ZMW74HzJvKsNS7",
      "Token Balance": "2350000",
      "Percent Ownership": 23.5,
      "Trustline Active": true,
    },
    {
      "Wallet Address": "rJRi8WW24gt9X85PHAxfWNPCizMMhqUQwg",
      "Token Balance": "3530000",
      "Percent Ownership": 35.3,
      "Trustline Active": true,
    },
    {
      "Wallet Address": "rLDYrujdKUfVx28T9vRDAbyJ7G2WVXKo4K",
      "Token Balance": "4120000",
      "Percent Ownership": 41.2,
      "Trustline Active": true,
    },
  ],
}

// Empty token holdings for companies that haven't distributed yet
const emptyTokenHoldings = {
  token_holdings: [],
}

export async function GET(request: Request, { params }: { params: { id: string } }) {
  try {
    const id = params.id

    // In a real implementation, you would fetch the token holdings from the XRPL
    // For this mock, we'll just return the mock data

    // For demonstration purposes, let's return empty data for a specific ID
    if (id === "empty") {
      return NextResponse.json(emptyTokenHoldings)
    }

    return NextResponse.json(mockTokenHoldings)
  } catch (error) {
    console.error("Error fetching token holdings:", error)
    return NextResponse.json({ error: "Internal server error" }, { status: 500 })
  }
}
