import { NextRequest, NextResponse } from 'next/server'

const FLASK_API_URL = process.env.FLASK_API_URL || 'http://localhost:5002'

export async function GET(request: NextRequest) {
  try {
    const searchParams = request.nextUrl.searchParams
    const level = searchParams.get('level') || 'all'
    
    // Use Node.js native fetch without any size limits
    const controller = new AbortController()
    const timeoutId = setTimeout(() => controller.abort(), 30000)
    
    const response = await fetch(`${FLASK_API_URL}/api/logs?level=${level}`, {
      headers: {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
      },
      signal: controller.signal,
      // Explicitly set no compression to ensure we get full data
      compress: false,
    })
    
    clearTimeout(timeoutId)

    if (!response.ok) {
      throw new Error(`Failed to fetch logs: ${response.statusText}`)
    }

    // Read the response as a stream to handle large data
    const chunks: Uint8Array[] = []
    const reader = response.body?.getReader()
    
    if (!reader) {
      throw new Error('No response body')
    }
    
    while (true) {
      const { done, value } = await reader.read()
      if (done) break
      chunks.push(value)
    }
    
    // Combine all chunks
    const fullData = new Uint8Array(chunks.reduce((acc, chunk) => acc + chunk.length, 0))
    let offset = 0
    for (const chunk of chunks) {
      fullData.set(chunk, offset)
      offset += chunk.length
    }
    
    // Convert to string
    const text = new TextDecoder().decode(fullData)
    
    // Parse the JSON from the text
    const data = JSON.parse(text)
    
    // Log the actual size for debugging
    console.log(`Logs API: received ${text.length} chars, logs field: ${data.logs?.length || 0} chars`)
    
    return NextResponse.json(data)
  } catch (error) {
    console.error('Logs API error:', error)
    return NextResponse.json(
      { logs: 'Error fetching logs', error: error instanceof Error ? error.message : 'Unknown error' },
      { status: 500 }
    )
  }
}