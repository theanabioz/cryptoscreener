import { NextResponse } from 'next/server';

export async function GET(request: Request) {
  const { searchParams } = new URL(request.url);
  const ids = searchParams.get('ids');
  
  try {
    const baseUrl = process.env.BACKEND_URL || 'http://localhost:8000';
    const backendUrl = ids 
      ? `${baseUrl}/api/coins?ids=${ids}`
      : `${baseUrl}/api/coins`;

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
