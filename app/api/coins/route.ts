import { NextResponse } from 'next/server';

export async function GET() {
  try {
    const res = await fetch('http://142.93.171.76:8000/api/coins', {
      cache: 'no-store' // Всегда свежие данные
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
