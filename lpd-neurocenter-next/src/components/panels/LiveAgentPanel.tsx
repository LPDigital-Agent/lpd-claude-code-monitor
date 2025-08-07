'use client'

import { Users, RefreshCw, Plus, Activity, Clock, CheckCircle } from 'lucide-react'
import { useEffect, useState } from 'react'

interface Agent {
  id: string
  name: string
  dlq: string
  status: 'active' | 'idle' | 'completed'
  progress: number
  duration: string
  messagesProcessed: number
}

export function LiveAgentPanel() {
  const [agents, setAgents] = useState<Agent[]>([])

  useEffect(() => {
    // Will be connected to WebSocket
    setAgents([])
  }, [])

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'active': return <Activity className="w-4 h-4 text-green-400 animate-pulse" />
      case 'idle': return <Clock className="w-4 h-4 text-yellow-400" />
      case 'completed': return <CheckCircle className="w-4 h-4 text-blue-400" />
      default: return null
    }
  }

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'active': return 'bg-green-500/10 border-green-500/30'
      case 'idle': return 'bg-yellow-500/10 border-yellow-500/30'
      case 'completed': return 'bg-blue-500/10 border-blue-500/30'
      default: return 'bg-gray-500/10 border-gray-500/30'
    }
  }

  return (
    <div className="bg-gray-900/50 backdrop-blur-sm rounded-lg border border-gray-800 h-full flex flex-col">
      {/* Header */}
      <div className="px-4 py-3 border-b border-gray-800 bg-gradient-to-r from-blue-900/20 to-purple-900/20">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <Users className="w-5 h-5 text-blue-400 animate-pulse" />
            <div>
              <h3 className="text-white font-semibold">Live Agent Overview</h3>
              <p className="text-xs text-gray-400">Active Investigations</p>
            </div>
          </div>
          <div className="flex gap-2">
            <button className="p-1.5 rounded-md bg-gray-700/50 text-gray-400 hover:bg-gray-700 hover:text-white transition-all duration-200">
              <RefreshCw className="w-4 h-4" />
            </button>
            <button className="p-1.5 rounded-md bg-primary-500/20 text-primary-400 hover:bg-primary-500/30 transition-all duration-200">
              <Plus className="w-4 h-4" />
            </button>
          </div>
        </div>
      </div>

      {/* Body */}
      <div className="flex-1 overflow-y-auto p-4">
        {agents.length === 0 ? (
          <div className="flex flex-col items-center justify-center h-full text-gray-500">
            <Users className="w-12 h-12 mb-3 opacity-30" />
            <p className="text-sm font-medium">No Active Agents</p>
            <p className="text-xs mt-1">Agents will appear when investigations start</p>
          </div>
        ) : (
          <div className="grid gap-3">
            {agents.map((agent) => (
              <div
                key={agent.id}
                className={`p-4 rounded-lg border transition-all duration-200 hover:scale-[1.02] ${getStatusColor(agent.status)}`}
              >
                <div className="flex items-start justify-between mb-3">
                  <div>
                    <h4 className="font-medium text-white flex items-center gap-2">
                      {getStatusIcon(agent.status)}
                      {agent.name}
                    </h4>
                    <p className="text-xs text-gray-400 mt-1">
                      Processing: {agent.dlq}
                    </p>
                  </div>
                  <span className="text-xs text-gray-400">
                    {agent.duration}
                  </span>
                </div>

                <div className="space-y-2">
                  <div className="flex justify-between text-xs">
                    <span className="text-gray-500">Progress</span>
                    <span className="text-gray-400">{agent.progress}%</span>
                  </div>
                  <div className="w-full bg-gray-700 rounded-full h-1.5">
                    <div
                      className={`h-1.5 rounded-full transition-all duration-500 ${
                        agent.status === 'active' ? 'bg-green-500' :
                        agent.status === 'idle' ? 'bg-yellow-500' :
                        'bg-blue-500'
                      }`}
                      style={{ width: `${agent.progress}%` }}
                    />
                  </div>
                  <div className="flex justify-between text-xs mt-2">
                    <span className="text-gray-500">Messages</span>
                    <span className="text-gray-400">{agent.messagesProcessed}</span>
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