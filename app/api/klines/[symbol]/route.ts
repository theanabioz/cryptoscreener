import { NextRequest, NextResponse } from 'next/server';

export async function GET(
  request: NextRequest,
  { params }: { params: Promise<{ symbol: string }> }
) {
  const symbol = (await params).symbol;
  const searchParams = request.nextUrl.searchParams;
  const interval = searchParams.get('interval') || '1h';
  const limit = searchParams.get('limit') || '500';

  const backendUrl = `http://142.93.171.76:8000/api/klines/${symbol}?interval=${interval}&limit=${limit}`;
  console.log(`Fetching klines from: ${backendUrl}`);

  try {
    const res = await fetch(backendUrl, {
      cache: 'no-store',
      headers: {
        'Accept': 'application/json',
      }
    });
    
    if (!res.ok) {
      const errorText = await res.text();
      console.error(`Backend Error: ${res.status} - ${errorText}`);
      throw new Error(`Backend responded with ${res.status}`);
    }

    const data = await res.json();
    console.log(`Successfully fetched ${data.length} klines for ${symbol}`);
    return NextResponse.json(data);
  } catch (error) {
    console.error("Proxy Klines Error details:", error);
    return NextResponse.json({ error: "Failed to fetch klines" }, { status: 500 });
  }
}
