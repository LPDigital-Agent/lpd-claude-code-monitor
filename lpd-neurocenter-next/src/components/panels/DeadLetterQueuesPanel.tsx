'use client'

import { AlertTriangle, Activity, Clock, GitPullRequest } from 'lucide-react'
import { useEffect, useState } from 'react'

interface DLQItem {
  id: string
  name: string
  messages: number
  status: 'critical' | 'warning' | 'ok'
  agent?: string
  startTime?: string
  progress?: number
}

export function DeadLetterQueuesPanel() {
  const [dlqs, setDlqs] = useState<DLQItem[]>([])
  const [stats, setStats] = useState({ critical: 0, warning: 0, ok: 0 })

  useEffect(() => {
    // This will be connected to WebSocket for real-time updates
    // For now, showing empty state
    setDlqs([])
    setStats({ critical: 0, warning: 0, ok: 0 })
  }, [])

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'critical': return 'bg-red-500/20 border-red-500 text-red-400'
      case 'warning': return 'bg-yellow-500/20 border-yellow-500 text-yellow-400'
      case 'ok': return 'bg-green-500/20 border-green-500 text-green-400'
      default: return 'bg-gray-500/20 border-gray-500 text-gray-400'
    }
  }

  return (
    <div className="bg-gray-900/50 backdrop-blur-sm rounded-lg border border-gray-800 h-full flex flex-col">
      {/* Header */}
      <div className="px-4 py-3 border-b border-gray-800 bg-gradient-to-r from-red-900/20 to-orange-900/20">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <AlertTriangle className="w-5 h-5 text-red-400 animate-pulse" />
            <div>
              <h3 className="text-white font-semibold">Dead Letter Queues</h3>
              <p className="text-xs text-gray-400">Active Investigations Only</p>
            </div>
          </div>
          <div className="flex gap-2">
            <span className={`px-2 py-1 rounded-md text-xs font-medium ${stats.critical > 0 ? 'bg-red-500/20 text-red-400 animate-pulse' : 'bg-gray-700/50 text-gray-500'}`}>
              {stats.critical}
            </span>
            <span className={`px-2 py-1 rounded-md text-xs font-medium ${stats.warning > 0 ? 'bg-yellow-500/20 text-yellow-400' : 'bg-gray-700/50 text-gray-500'}`}>
              {stats.warning}
            </span>
            <span className={`px-2 py-1 rounded-md text-xs font-medium ${stats.ok > 0 ? 'bg-green-500/20 text-green-400' : 'bg-gray-700/50 text-gray-500'}`}>
              {stats.ok}
            </span>
          </div>
        </div>
      </div>

      {/* Body */}
      <div className="flex-1 overflow-y-auto p-4">
        {dlqs.length === 0 ? (
          <div className="flex flex-col items-center justify-center h-full text-gray-500">
            <AlertTriangle className="w-12 h-12 mb-3 opacity-30" />
            <p className="text-sm font-medium">No Active Investigations</p>
            <p className="text-xs mt-1">DLQs with active agents will appear here</p>
          </div>
        ) : (
          <div className="space-y-3">
            {dlqs.map((dlq) => (
              <div
                key={dlq.id}
                className={`p-3 rounded-lg border transition-all duration-200 hover:scale-[1.02] ${getStatusColor(dlq.status)}`}
              >
                <div className="flex items-start justify-between mb-2">
                  <div>
                    <h4 className="font-medium text-white">{dlq.name}</h4>
                    <p className="text-xs opacity-75 mt-1">
                      {dlq.messages} messages
                    </p>
                  </div>
                  <span className={`px-2 py-1 rounded text-xs font-medium ${getStatusColor(dlq.status)}`}>
                    {dlq.status.toUpperCase()}
                  </span>
                </div>
                
                {dlq.agent && (
                  <div className="mt-3 pt-3 border-t border-white/10">
                    <div className="flex items-center justify-between text-xs">
                      <span className="text-gray-400">Agent: {dlq.agent}</span>
                      <span className="text-gray-400">{dlq.startTime}</span>
                    </div>
                    {dlq.progress !== undefined && (
                      <div className="mt-2">
                        <div className="w-full bg-gray-700 rounded-full h-1.5">
                          <div
                            className="bg-primary-500 h-1.5 rounded-full transition-all duration-500"
                            style={{ width: `${dlq.progress}%` }}
                          />
                        </div>
                      </div>
                    )}
                  </div>
                )}
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}