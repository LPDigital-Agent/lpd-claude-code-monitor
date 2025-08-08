'use client'

import { Activity, Brain, Clock, CheckCircle, AlertCircle, XCircle, RefreshCw } from 'lucide-react'
import { useState, useEffect } from 'react'
import { useQuery } from '@tanstack/react-query'
import { toast } from 'sonner'

interface AgentActivity {
  id: string
  timestamp: string
  agent: string
  action: string
  status: 'running' | 'completed' | 'failed'
  details?: string
}

async function fetchAgentActivities(): Promise<AgentActivity[]> {
  try {
    const response = await fetch('/api/flask/api/agent-activities', {
      headers: {
        'Content-Type': 'application/json',
        'Cache-Control': 'no-cache',
      },
    })
    
    if (!response.ok) {
      throw new Error(`Failed to fetch activities: ${response.status}`)
    }
    
    const data = await response.json()
    return data || []
  } catch (error) {
    console.error('[GlassRoom] Error fetching activities:', error)
    // Return empty array on error to prevent crash
    return []
  }
}

export function GlassRoomPanel() {
  const [filter, setFilter] = useState<'all' | 'running' | 'completed' | 'failed'>('all')
  
  // Fetch real agent activities from backend
  const { data: activities = [], isLoading, refetch } = useQuery({
    queryKey: ['agent-activities'],
    queryFn: fetchAgentActivities,
    refetchInterval: 5000, // Refresh every 5 seconds for real-time updates
    retry: 2,
    onError: (error) => {
      console.error('[GlassRoom] Query error:', error)
    }
  })

  const filteredActivities = activities.filter(activity => 
    filter === 'all' || activity.status === filter
  )

  const getStatusIcon = (status: string) => {
    switch(status) {
      case 'running':
        return <Activity className="w-4 h-4 text-blue-400 animate-pulse" />
      case 'completed':
        return <CheckCircle className="w-4 h-4 text-green-400" />
      case 'failed':
        return <XCircle className="w-4 h-4 text-red-400" />
      default:
        return <AlertCircle className="w-4 h-4 text-gray-400" />
    }
  }

  const getStatusColor = (status: string) => {
    switch(status) {
      case 'running':
        return 'text-blue-400 bg-blue-900/20'
      case 'completed':
        return 'text-green-400 bg-green-900/20'
      case 'failed':
        return 'text-red-400 bg-red-900/20'
      default:
        return 'text-gray-400 bg-gray-900/20'
    }
  }

  const formatTime = (timestamp: string) => {
    const date = new Date(timestamp)
    const now = new Date()
    const diff = now.getTime() - date.getTime()
    const minutes = Math.floor(diff / 60000)
    
    if (minutes < 1) return 'Just now'
    if (minutes < 60) return `${minutes}m ago`
    const hours = Math.floor(minutes / 60)
    if (hours < 24) return `${hours}h ago`
    return `${Math.floor(hours / 24)}d ago`
  }

  return (
    <div className="h-full bg-gray-900/50 backdrop-blur-sm rounded-lg border border-gray-800 flex flex-col">
      {/* Header */}
      <div className="px-6 py-4 border-b border-gray-800 bg-gradient-to-r from-gray-800/50 to-gray-900/50">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <Brain className="w-6 h-6 text-primary-400" />
            <div>
              <h2 className="text-xl font-bold text-white">Glass Room</h2>
              <p className="text-xs text-gray-400">Real-time Agent Activity & Context</p>
            </div>
          </div>
          
          <div className="flex items-center gap-3">
            {/* Refresh Button */}
            <button
              onClick={() => refetch()}
              disabled={isLoading}
              className="p-2 rounded-lg bg-gray-700/30 text-gray-400 hover:bg-gray-700/50 transition-all disabled:opacity-50"
              title="Refresh activities"
            >
              <RefreshCw className={`w-4 h-4 ${isLoading ? 'animate-spin' : ''}`} />
            </button>
            
            {/* Filter Buttons */}
            <div className="flex gap-2">
              {(['all', 'running', 'completed', 'failed'] as const).map(status => (
                <button
                  key={status}
                  onClick={() => setFilter(status)}
                  className={`px-3 py-1 rounded-md text-xs font-medium transition-all ${
                    filter === status
                      ? 'bg-primary-500/20 text-primary-400 border border-primary-500/50'
                      : 'bg-gray-700/30 text-gray-400 hover:bg-gray-700/50'
                  }`}
                >
                  {status.charAt(0).toUpperCase() + status.slice(1)}
                </button>
              ))}
            </div>
          </div>
        </div>
      </div>

      {/* Activity Feed */}
      <div className="flex-1 overflow-y-auto p-4 space-y-3">
        {isLoading ? (
          <div className="flex flex-col items-center justify-center h-full text-gray-500">
            <RefreshCw className="w-12 h-12 mb-3 opacity-30 animate-spin" />
            <p className="text-sm">Loading agent activities...</p>
          </div>
        ) : filteredActivities.length === 0 ? (
          <div className="flex flex-col items-center justify-center h-full text-gray-500">
            <Brain className="w-12 h-12 mb-3 opacity-30" />
            <p className="text-sm">No activities to display</p>
            <p className="text-xs mt-2">Waiting for agent actions...</p>
          </div>
        ) : (
          filteredActivities.map(activity => (
            <div
              key={activity.id}
              className="bg-gray-800/30 rounded-lg p-4 border border-gray-700/50 hover:border-gray-600 transition-all"
            >
              <div className="flex items-start gap-3">
                {getStatusIcon(activity.status)}
                <div className="flex-1">
                  <div className="flex items-center justify-between mb-1">
                    <div className="flex items-center gap-2">
                      <span className="text-primary-400 font-medium text-sm">
                        {activity.agent}
                      </span>
                      <span className={`px-2 py-0.5 rounded-full text-xs ${getStatusColor(activity.status)}`}>
                        {activity.status}
                      </span>
                    </div>
                    <span className="text-xs text-gray-500 flex items-center gap-1">
                      <Clock className="w-3 h-3" />
                      {formatTime(activity.timestamp)}
                    </span>
                  </div>
                  <p className="text-gray-300 text-sm">{activity.action}</p>
                  {activity.details && (
                    <p className="text-gray-500 text-xs mt-1">{activity.details}</p>
                  )}
                </div>
              </div>
            </div>
          ))
        )}
      </div>

      {/* Footer Stats */}
      <div className="px-6 py-3 border-t border-gray-800 bg-gray-900/50">
        <div className="flex items-center justify-between text-xs">
          <div className="flex gap-4">
            <span className="text-blue-400">
              Running: {activities.filter(a => a.status === 'running').length}
            </span>
            <span className="text-green-400">
              Completed: {activities.filter(a => a.status === 'completed').length}
            </span>
            <span className="text-red-400">
              Failed: {activities.filter(a => a.status === 'failed').length}
            </span>
          </div>
          <span className="text-gray-500">
            Total Activities: {activities.length}
          </span>
        </div>
      </div>
    </div>
  )
}