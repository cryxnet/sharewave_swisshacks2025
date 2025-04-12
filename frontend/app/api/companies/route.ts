import { NextResponse } from "next/server"

export async function POST(request: Request) {
  try {
    const body = await request.json()

    // Validate the request body
    if (!body.name || !body.symbol || !body.total_supply || !body.total_valuation_usd || !body.liquidity_percent) {
      return NextResponse.json({ error: "Missing required fields" }, { status: 400 })
    }

    if (!body.shareholders || !Array.isArray(body.shareholders) || body.shareholders.length === 0) {
      return NextResponse.json({ error: "At least one shareholder is required" }, { status: 400 })
    }

    // Calculate total percentage
    const shareholderTotal = body.shareholders.reduce((sum: number, sh: { percent: number }) => sum + sh.percent, 0)

    if (Math.abs(shareholderTotal + body.liquidity_percent - 100) > 0.01) {
      return NextResponse.json(
        { error: "Total percentage (shareholders + liquidity) must equal 100%" },
        { status: 400 },
      )
    }

    // Mock API response
    return NextResponse.json({
      message: "Company created successfully!",
      company_id: "d068bef1-d458-4881-a300-22670eb741a1",
      issuing_address: "rHb9CJAWyB4rj91VRWn96DkukG4bwdtyTh",
      note: "Shareholders must now send their required RLUSD to this address",
    })
  } catch (error) {
    console.error("Error creating company:", error)
    return NextResponse.json({ error: "Internal server error" }, { status: 500 })
  }
}
