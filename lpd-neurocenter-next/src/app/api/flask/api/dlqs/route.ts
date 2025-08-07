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
    return NextResponse.json(
      { error: 'Failed to fetch data from Flask API' },
      { status: 500 }
    )
  }
}