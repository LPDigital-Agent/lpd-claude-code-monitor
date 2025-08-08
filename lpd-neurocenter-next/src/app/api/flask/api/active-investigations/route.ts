import { NextRequest, NextResponse } from 'next/server'

const FLASK_BACKEND = process.env.FLASK_BACKEND_URL || 'http://localhost:5002'

export async function GET() {
  try {
    const response = await fetch(`${FLASK_BACKEND}/api/active-investigations`, {
      headers: {
        'Content-Type': 'application/json',
      },
      cache: 'no-store'
    })

    if (!response.ok) {
      const error = await response.text()
      return NextResponse.json(
        { error: error || 'Failed to fetch active investigations' },
        { status: response.status }
      )
    }

    const data = await response.json()
    return NextResponse.json(data)
  } catch (error) {
    console.error('Active investigations API error:', error)
    return NextResponse.json(
      { error: 'Failed to fetch active investigations' },
      { status: 500 }
    )
  }
}