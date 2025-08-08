import { NextRequest, NextResponse } from 'next/server'

const FLASK_BACKEND = process.env.FLASK_BACKEND_URL || 'http://localhost:5002'

export async function POST(request: NextRequest) {
  try {
    const body = await request.json()
    
    // Forward the request to Flask backend
    const response = await fetch(`${FLASK_BACKEND}/api/investigate`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(body),
    })

    if (!response.ok) {
      const error = await response.text()
      return NextResponse.json(
        { error: error || 'Failed to trigger investigation' },
        { status: response.status }
      )
    }

    const data = await response.json()
    return NextResponse.json(data)
  } catch (error) {
    console.error('Investigation API error:', error)
    return NextResponse.json(
      { error: 'Failed to trigger investigation' },
      { status: 500 }
    )
  }
}