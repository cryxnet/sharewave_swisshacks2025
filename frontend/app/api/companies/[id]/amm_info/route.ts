import { NextResponse } from "next/server"

// Mock AMM info data
const mockAMMInfo = {
  amm_info: {
    Liquidity: "1500000",
    TradingFee: 500,
    Owner: "rHb9CJAWyB4rj91VRWn96DkukG4bwdtyTh",
    LedgerIndex: "13F1A95D7AAB7108D5CE7EECC8F62E3FC65B336AC4F390B30061CC8DE585E74D",
    Asset: {
      currency: "TECH",
      issuer: "rHb9CJAWyB4rj91VRWn96DkukG4bwdtyTh",
    },
    Asset2: {
      currency: "RLUSD",
      issuer: "rHb9CJAWyB4rj91VRWn96DkukG4bwdtyTh",
    },
    Amount: {
      currency: "TECH",
      issuer: "rHb9CJAWyB4rj91VRWn96DkukG4bwdtyTh",
      value: "1500000",
    },
    Amount2: {
      currency: "RLUSD",
      issuer: "rHb9CJAWyB4rj91VRWn96DkukG4bwdtyTh",
      value: "1875000",
    },
    VoteSlots: [
      {
        VoteEntry: {
          Account: "rHb9CJAWyB4rj91VRWn96DkukG4bwdtyTh",
          TradingFee: 500,
          VoteWeight: 1000,
        },
      },
    ],
  },
}

export async function GET(request: Request, { params }: { params: { id: string } }) {
  try {
    const id = params.id
    const { searchParams } = new URL(request.url)
    const account = searchParams.get("account")

    // In a real implementation, you would fetch the AMM info from the XRPL
    // For this mock, we'll just return the mock data

    // If an account is provided, we could customize the response
    // For this mock, we'll just return the same data

    return NextResponse.json(mockAMMInfo)
  } catch (error) {
    console.error("Error fetching AMM info:", error)
    return NextResponse.json({ error: "Internal server error" }, { status: 500 })
  }
}
