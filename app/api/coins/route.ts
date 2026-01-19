import { NextResponse } from 'next/server';

export async function GET(request: Request) {
  const { searchParams } = new URL(request.url);
  const ids = searchParams.get('ids');
  
  try {
    const backendUrl = ids 
      ? `http://142.93.171.76:8000/api/coins?ids=${ids}`
      : 'http://142.93.171.76:8000/api/coins';

    const res = await fetch(backendUrl, {
      cache: 'no-store',
    });
    
    if (!res.ok) {
      throw new Error(`Backend responded with ${res.status}`);
    }

    const data = await res.json();
    
    return NextResponse.json(data, {
      headers: {
        'Cache-Control': 'no-store, no-cache, must-revalidate, proxy-revalidate',
        'Pragma': 'no-cache',
        'Expires': '0',
      }
    });
  } catch (error) {
    console.error("Proxy Error:", error);
    return NextResponse.json({ error: "Failed to fetch coins" }, { status: 500 });
  }
}
