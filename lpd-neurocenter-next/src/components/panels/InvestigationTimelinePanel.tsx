'use client'

import { Activity, Clock, CheckCircle, XCircle, AlertCircle } from 'lucide-react'
import { useEffect, useState } from 'react'

interface TimelineEvent {
  id: string
  timestamp: string
  dlq: string
  agent: string
  status: 'started' | 'in_progress' | 'completed' | 'failed'
  message: string
  duration?: string
}

export function InvestigationTimelinePanel() {
  const [events, setEvents] = useState<TimelineEvent[]>([])
  const [filter, setFilter] = useState('all')

  useEffect(() => {
    // Will be connected to WebSocket
    setEvents([])
  }, [])

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'started': return <Clock className="w-4 h-4 text-blue-400" />
      case 'in_progress': return <Activity className="w-4 h-4 text-yellow-400 animate-pulse" />
      case 'completed': return <CheckCircle className="w-4 h-4 text-green-400" />
      case 'failed': return <XCircle className="w-4 h-4 text-red-400" />
      default: return <AlertCircle className="w-4 h-4 text-gray-400" />
    }
  }

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'started': return 'border-l-blue-500'
      case 'in_progress': return 'border-l-yellow-500'
      case 'completed': return 'border-l-green-500'
      case 'failed': return 'border-l-red-500'
      default: return 'border-l-gray-500'
    }
  }

  const filteredEvents = filter === 'all' 
    ? events 
    : events.filter(e => e.status === filter || (filter === 'active' && e.status === 'in_progress'))

  return (
    <div className="bg-gray-900/50 backdrop-blur-sm rounded-lg border border-gray-800 h-full flex flex-col">
      {/* Header */}
      <div className="px-4 py-3 border-b border-gray-800">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <Activity className="w-5 h-5 text-gray-400" />
            <h3 className="text-white font-semibold">Investigation Timeline</h3>
          </div>
          <select
            value={filter}
            onChange={(e) => setFilter(e.target.value)}
            className="px-2 py-1 bg-gray-800/50 border border-gray-700 rounded text-xs text-white focus:outline-none focus:border-primary-500"
          >
            <option value="all">All</option>
            <option value="active">Active</option>
            <option value="completed">Completed</option>
          </select>
        </div>
      </div>

      {/* Body */}
      <div className="flex-1 overflow-y-auto p-4">
        {filteredEvents.length === 0 ? (
          <div className="flex flex-col items-center justify-center h-full text-gray-500">
            <Activity className="w-12 h-12 mb-3 opacity-30" />
            <p className="text-sm font-medium">No Investigation Events</p>
            <p className="text-xs mt-1">Timeline will update when investigations start</p>
          </div>
        ) : (
          <div className="space-y-3">
            {filteredEvents.map((event) => (
              <div
                key={event.id}
                className={`pl-4 border-l-2 ${getStatusColor(event.status)} hover:bg-gray-800/30 transition-colors duration-200 py-2`}
              >
                <div className="flex items-start gap-3">
                  <div className="mt-0.5">
                    {getStatusIcon(event.status)}
                  </div>
                  <div className="flex-1 min-w-0">
                    <div className="flex items-start justify-between gap-2">
                      <div className="flex-1">
                        <p className="text-sm text-white font-medium">
                          {event.dlq}
                        </p>
                        <p className="text-xs text-gray-400 mt-0.5">
                          {event.message}
                        </p>
                        <p className="text-xs text-gray-500 mt-1">
                          Agent: {event.agent}
                        </p>
                      </div>
                      <div className="text-right">
                        <p className="text-xs text-gray-500">
                          {event.timestamp}
                        </p>
                        {event.duration && (
                          <p className="text-xs text-gray-600 mt-0.5">
                            {event.duration}
                          </p>
                        )}
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}