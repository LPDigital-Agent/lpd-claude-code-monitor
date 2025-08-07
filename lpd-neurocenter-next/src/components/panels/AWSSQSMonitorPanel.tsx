'use client'

import { Database, RefreshCw, Search, ChevronDown } from 'lucide-react'
import { useEffect, useState } from 'react'
import { useQuery } from '@tanstack/react-query'

interface Queue {
  id: string
  name: string
  url: string
  messages: number
  inFlight: number
  region: string
  isDLQ: boolean
  selected: boolean
}

async function fetchQueues(): Promise<Queue[]> {
  const response = await fetch('/api/flask/api/dlqs')
  if (!response.ok) throw new Error('Failed to fetch queues')
  const data = await response.json()
  
  // The API returns an array directly
  const queues = Array.isArray(data) ? data : (data.dlqs || [])
  
  return queues
    .filter((q: any) => q.isDLQ !== false) // Only show DLQs
    .sort((a: any, b: any) => b.messages - a.messages)
    .map((q: any) => ({
      id: q.url || q.name,
      name: q.name,
      url: q.url || q.name,
      messages: q.messages || 0,
      inFlight: q.messagesNotVisible || 0,
      region: q.region || 'sa-east-1',
      isDLQ: true,
      selected: false
    }))
}

export function AWSSQSMonitorPanel() {
  const [searchTerm, setSearchTerm] = useState('')
  const [filter, setFilter] = useState('dlq')
  const [collapsed, setCollapsed] = useState(false)
  
  const { data: queues = [], isLoading, refetch } = useQuery({
    queryKey: ['production-queues'],
    queryFn: fetchQueues,
    refetchInterval: 30000,
  })

  const filteredQueues = queues.filter(queue => {
    if (searchTerm && !queue.name.toLowerCase().includes(searchTerm.toLowerCase())) {
      return false
    }
    if (filter === 'with-messages' && queue.messages === 0) {
      return false
    }
    return true
  })

  const handleInvestigate = async (queueId: string) => {
    // Trigger investigation for selected queue
    console.log('Investigating queue:', queueId)
  }

  return (
    <div className="bg-gray-900/50 backdrop-blur-sm rounded-lg border border-gray-800 flex flex-col">
      {/* Header */}
      <div className="px-4 py-3 border-b border-gray-800 bg-gradient-to-r from-gray-800/50 to-gray-900/50">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <button
              onClick={() => setCollapsed(!collapsed)}
              className="p-1 hover:bg-gray-700/50 rounded transition-all duration-200"
            >
              <ChevronDown className={`w-4 h-4 text-gray-400 transition-transform duration-200 ${collapsed ? '-rotate-90' : ''}`} />
            </button>
            <Database className="w-5 h-5 text-gray-400" />
            <div>
              <h3 className="text-white font-semibold">AWS SQS Queue Monitor</h3>
              <p className="text-xs text-gray-500">
                Account: 432817839790 | Region: sa-east-1
              </p>
            </div>
          </div>
          <div className="flex gap-2">
            <button 
              onClick={() => refetch()}
              className="p-1.5 rounded-md bg-gray-700/50 text-gray-400 hover:bg-gray-700 hover:text-white transition-all duration-200"
            >
              <RefreshCw className={`w-4 h-4 ${isLoading ? 'animate-spin' : ''}`} />
            </button>
            <button className="px-3 py-1.5 rounded-md bg-primary-500/20 text-primary-400 hover:bg-primary-500/30 transition-all duration-200 text-sm font-medium flex items-center gap-1.5">
              <Search className="w-3.5 h-3.5" />
              Investigate
            </button>
          </div>
        </div>
      </div>

      {/* Body */}
      {!collapsed && (
        <div className="flex-1">
          {/* Controls */}
          <div className="px-4 py-3 border-b border-gray-800 flex gap-3">
            <input
              type="text"
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              placeholder="Search queues..."
              className="flex-1 px-3 py-1.5 bg-gray-800/50 border border-gray-700 rounded-md text-sm text-white placeholder-gray-500 focus:outline-none focus:border-primary-500 transition-colors duration-200"
            />
            <select
              value={filter}
              onChange={(e) => setFilter(e.target.value)}
              className="px-3 py-1.5 bg-gray-800/50 border border-gray-700 rounded-md text-sm text-white focus:outline-none focus:border-primary-500 transition-colors duration-200"
            >
              <option value="all">All Queues</option>
              <option value="dlq">DLQ Only</option>
              <option value="with-messages">With Messages</option>
              <option value="monitored">Monitored</option>
            </select>
          </div>

          {/* Queue Cards */}
          <div className="p-4 overflow-y-auto max-h-96">
            {isLoading ? (
              <div className="flex items-center justify-center py-8">
                <RefreshCw className="w-8 h-8 text-gray-500 animate-spin" />
              </div>
            ) : filteredQueues.length === 0 ? (
              <div className="flex flex-col items-center justify-center py-8 text-gray-500">
                <Database className="w-12 h-12 mb-3 opacity-30" />
                <p className="text-sm font-medium">No DLQ Queues Found</p>
                <p className="text-xs mt-1">Waiting for DLQ queues to appear</p>
              </div>
            ) : (
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
                {filteredQueues.map((queue) => (
                  <div
                    key={queue.id}
                    className={`p-3 rounded-lg border transition-all duration-200 hover:scale-[1.02] cursor-pointer ${
                      queue.messages > 0 
                        ? 'bg-red-900/20 border-red-500/30 hover:border-red-500/50' 
                        : 'bg-gray-800/30 border-gray-700 hover:border-gray-600'
                    }`}
                    onClick={() => handleInvestigate(queue.id)}
                  >
                    <div className="flex items-start justify-between mb-2">
                      <h4 className="text-sm font-medium text-white truncate pr-2">
                        {queue.name}
                      </h4>
                      {queue.isDLQ && (
                        <span className="px-1.5 py-0.5 bg-orange-500/20 text-orange-400 text-xs rounded">
                          DLQ
                        </span>
                      )}
                    </div>
                    <div className="space-y-1">
                      <div className="flex justify-between text-xs">
                        <span className="text-gray-500">Messages</span>
                        <span className={queue.messages > 0 ? 'text-red-400 font-medium' : 'text-gray-400'}>
                          {queue.messages}
                        </span>
                      </div>
                      <div className="flex justify-between text-xs">
                        <span className="text-gray-500">In Flight</span>
                        <span className="text-gray-400">{queue.inFlight}</span>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  )
}