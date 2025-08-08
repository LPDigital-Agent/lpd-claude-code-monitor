'use client'

import { AlertTriangle, Activity, Clock, GitPullRequest } from 'lucide-react'
import { useEffect, useState } from 'react'
import { Card, CardHeader, CardContent, CardFooter } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'

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

  const getStatusTone = (status: string): 'critical' | 'warning' | 'success' | 'neutral' => {
    switch (status) {
      case 'critical': return 'critical'
      case 'warning': return 'warning'
      case 'ok': return 'success'
      default: return 'neutral'
    }
  }

  return (
    <Card elevation="md" variant="glass" className="h-full flex flex-col bg-neutral-900/80">
      <CardHeader
        className="bg-gradient-to-r from-critical-900/20 to-brand-900/20 border-b border-neutral-800"
        aside={
          <div className="flex gap-2">
            <Badge 
              tone={stats.critical > 0 ? 'critical' : 'neutral'}
              pulse={stats.critical > 0}
              size="sm"
            >
              {stats.critical}
            </Badge>
            <Badge 
              tone={stats.warning > 0 ? 'warning' : 'neutral'}
              size="sm"
            >
              {stats.warning}
            </Badge>
            <Badge 
              tone={stats.ok > 0 ? 'success' : 'neutral'}
              size="sm"
            >
              {stats.ok}
            </Badge>
          </div>
        }
      >
        <div className="flex items-center gap-3">
          <AlertTriangle className="w-5 h-5 text-critical-400 animate-pulse" />
          <div>
            <h3 className="text-neutral-0 font-heading font-semibold">Dead Letter Queues</h3>
            <p className="text-xs text-neutral-400">Active Investigations Only</p>
          </div>
        </div>
      </CardHeader>

      <CardContent className="flex-1 overflow-y-auto">
        {dlqs.length === 0 ? (
          <div className="flex flex-col items-center justify-center h-full text-neutral-500">
            <AlertTriangle className="w-12 h-12 mb-3 opacity-30" />
            <p className="text-sm font-medium">No Active Investigations</p>
            <p className="text-xs mt-1">DLQs with active agents will appear here</p>
          </div>
        ) : (
          <div className="space-y-3">
            {dlqs.map((dlq) => (
              <Card
                key={dlq.id}
                elevation="sm"
                className="p-3 transition-all duration-200 hover:scale-[1.02]"
              >
                <div className="flex items-start justify-between mb-2">
                  <div>
                    <h4 className="font-medium text-neutral-0">{dlq.name}</h4>
                    <p className="text-xs text-neutral-400 mt-1">
                      {dlq.messages} messages
                    </p>
                  </div>
                  <Badge tone={getStatusTone(dlq.status)} size="sm">
                    {dlq.status.toUpperCase()}
                  </Badge>
                </div>
                
                {dlq.agent && (
                  <div className="mt-3 pt-3 border-t border-neutral-800/50">
                    <div className="flex items-center justify-between text-xs">
                      <span className="text-neutral-400">Agent: {dlq.agent}</span>
                      <span className="text-neutral-400">{dlq.startTime}</span>
                    </div>
                    {dlq.progress !== undefined && (
                      <div className="mt-2">
                        <div className="w-full bg-neutral-700 rounded-full h-1.5">
                          <div
                            className="bg-brand-600 h-1.5 rounded-full transition-all duration-500"
                            style={{ width: `${dlq.progress}%` }}
                          />
                        </div>
                      </div>
                    )}
                  </div>
                )}
              </Card>
            ))}
          </div>
        )}
      </CardContent>
    </Card>
  )
}