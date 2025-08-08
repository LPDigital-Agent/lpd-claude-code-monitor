import { NextResponse } from 'next/server'

export async function GET() {
  try {
    const response = await fetch('http://localhost:5002/api/dlqs', {
      headers: {
        'Content-Type': 'application/json',
      },
    })

    if (!response.ok) {
      throw new Error(`Flask API error: ${response.status}`)
    }

    const data = await response.json()
    return NextResponse.json(data)
  } catch (error) {
    console.error('Error fetching from Flask API:', error)
    
    // Return empty data structure when backend is not available
    // This allows the UI to render without crashing
    return NextResponse.json({
      dlqs: [],
      timestamp: new Date().toISOString(),
      error: 'Backend service unavailable'
    })
  }
}