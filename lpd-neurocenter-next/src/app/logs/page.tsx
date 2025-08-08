'use client'

import { useState, useEffect } from 'react'
import { ArrowLeft, RefreshCw, Download } from 'lucide-react'

export default function LogsPage() {
  const [logs, setLogs] = useState<string>('')
  const [loading, setLoading] = useState(true)
  const [autoRefresh, setAutoRefresh] = useState(false)

  const fetchLogs = async () => {
    setLoading(true)
    try {
      const response = await fetch('/api/flask/api/logs?level=all')
      const data = await response.json()
      setLogs(data.logs || 'No logs available')
    } catch (error) {
      setLogs('Error fetching logs')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchLogs()
  }, [])

  useEffect(() => {
    if (autoRefresh) {
      const interval = setInterval(fetchLogs, 5000)
      return () => clearInterval(interval)
    }
  }, [autoRefresh])

  const downloadLogs = () => {
    const blob = new Blob([logs], { type: 'text/plain' })
    const url = window.URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `neurocenter-logs-${new Date().toISOString()}.log`
    document.body.appendChild(a)
    a.click()
    document.body.removeChild(a)
    window.URL.revokeObjectURL(url)
  }

  return (
    <div className="min-h-screen bg-gray-950 flex flex-col">
      {/* Header */}
      <div className="h-14 bg-gray-900 border-b border-gray-800 flex items-center justify-between px-4">
        <div className="flex items-center gap-4">
          <button 
            onClick={() => window.close()}
            className="p-2 hover:bg-gray-800 rounded-lg transition-colors"
          >
            <ArrowLeft className="w-5 h-5 text-gray-400" />
          </button>
          <h1 className="text-lg font-semibold text-white">System Logs</h1>
        </div>
        
        <div className="flex items-center gap-2">
          <button
            onClick={() => setAutoRefresh(!autoRefresh)}
            className={`p-2 rounded-lg transition-colors ${
              autoRefresh ? 'bg-primary-500/20 text-primary-400' : 'hover:bg-gray-800 text-gray-400'
            }`}
            title="Auto refresh"
          >
            <RefreshCw className={`w-4 h-4 ${autoRefresh ? 'animate-spin' : ''}`} />
          </button>
          
          <button
            onClick={fetchLogs}
            disabled={loading}
            className="p-2 hover:bg-gray-800 rounded-lg transition-colors text-gray-400"
            title="Refresh logs"
          >
            <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
          </button>
          
          <button
            onClick={downloadLogs}
            className="p-2 hover:bg-gray-800 rounded-lg transition-colors text-gray-400"
            title="Download logs"
          >
            <Download className="w-4 h-4" />
          </button>
        </div>
      </div>

      {/* Logs Content */}
      <div className="flex-1 p-4">
        <div className="h-full bg-black rounded-lg border border-gray-800 p-4 overflow-auto">
          <pre className="font-mono text-xs text-gray-300 whitespace-pre-wrap">
            {loading ? 'Loading logs...' : logs}
          </pre>
        </div>
      </div>
    </div>
  )
}