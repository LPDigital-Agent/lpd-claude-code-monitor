'use client'

import { Eye, Zap, Activity, Database, GitBranch, Code, AlertTriangle } from 'lucide-react'
import { useState, useEffect } from 'react'

interface Node {
  id: string
  label: string
  type: 'agent' | 'service' | 'database' | 'queue'
  status: 'active' | 'idle' | 'error'
  x: number
  y: number
  connections: string[]
}

export function ObserveModePanel() {
  const [nodes] = useState<Node[]>([
    {
      id: 'dlq-monitor',
      label: 'DLQ Monitor',
      type: 'agent',
      status: 'active',
      x: 20,
      y: 30,
      connections: ['aws-sqs']
    },
    {
      id: 'aws-sqs',
      label: 'AWS SQS',
      type: 'queue',
      status: 'active',
      x: 50,
      y: 30,
      connections: ['investigator']
    },
    {
      id: 'investigator',
      label: 'Claude Investigator',
      type: 'agent',
      status: 'active',
      x: 80,
      y: 30,
      connections: ['github']
    },
    {
      id: 'github',
      label: 'GitHub',
      type: 'service',
      status: 'idle',
      x: 50,
      y: 60,
      connections: []
    },
    {
      id: 'database',
      label: 'Investigation DB',
      type: 'database',
      status: 'active',
      x: 20,
      y: 60,
      connections: ['investigator']
    }
  ])

  const [pulseAnimation, setPulseAnimation] = useState(0)
  const [selectedNode, setSelectedNode] = useState<string | null>(null)

  useEffect(() => {
    const interval = setInterval(() => {
      setPulseAnimation(prev => (prev + 1) % 100)
    }, 50)
    return () => clearInterval(interval)
  }, [])

  const getNodeIcon = (type: string) => {
    switch(type) {
      case 'agent':
        return <Zap className="w-6 h-6" />
      case 'service':
        return <GitBranch className="w-6 h-6" />
      case 'database':
        return <Database className="w-6 h-6" />
      case 'queue':
        return <Activity className="w-6 h-6" />
      default:
        return <Code className="w-6 h-6" />
    }
  }

  const getNodeColor = (status: string, type: string) => {
    if (status === 'error') return 'text-red-400 bg-red-900/20 border-red-500/50'
    if (status === 'idle') return 'text-gray-400 bg-gray-900/20 border-gray-700'
    
    switch(type) {
      case 'agent':
        return 'text-primary-400 bg-primary-900/20 border-primary-500/50'
      case 'service':
        return 'text-green-400 bg-green-900/20 border-green-500/50'
      case 'database':
        return 'text-blue-400 bg-blue-900/20 border-blue-500/50'
      case 'queue':
        return 'text-yellow-400 bg-yellow-900/20 border-yellow-500/50'
      default:
        return 'text-gray-400 bg-gray-900/20 border-gray-700'
    }
  }

  return (
    <div className="h-full bg-gray-900/50 backdrop-blur-sm rounded-lg border border-gray-800 flex flex-col">
      {/* Header */}
      <div className="px-6 py-4 border-b border-gray-800 bg-gradient-to-r from-gray-800/50 to-gray-900/50">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <Eye className="w-6 h-6 text-primary-400" />
            <div>
              <h2 className="text-xl font-bold text-white">Observe Mode</h2>
              <p className="text-xs text-gray-400">System Architecture Visualization</p>
            </div>
          </div>
          <div className="flex items-center gap-3 text-xs">
            <div className="flex items-center gap-1">
              <div className="w-2 h-2 rounded-full bg-primary-400 animate-pulse" />
              <span className="text-gray-400">Active</span>
            </div>
            <div className="flex items-center gap-1">
              <div className="w-2 h-2 rounded-full bg-gray-400" />
              <span className="text-gray-400">Idle</span>
            </div>
            <div className="flex items-center gap-1">
              <div className="w-2 h-2 rounded-full bg-red-400" />
              <span className="text-gray-400">Error</span>
            </div>
          </div>
        </div>
      </div>

      {/* Visualization Area */}
      <div className="flex-1 relative overflow-hidden bg-gray-950/50">
        {/* Grid Background */}
        <div 
          className="absolute inset-0 opacity-10"
          style={{
            backgroundImage: `
              linear-gradient(rgba(59, 130, 246, 0.2) 1px, transparent 1px),
              linear-gradient(90deg, rgba(59, 130, 246, 0.2) 1px, transparent 1px)
            `,
            backgroundSize: '40px 40px'
          }}
        />

        {/* Connection Lines */}
        <svg className="absolute inset-0 w-full h-full">
          {nodes.map(node => 
            node.connections.map(targetId => {
              const target = nodes.find(n => n.id === targetId)
              if (!target) return null
              
              return (
                <g key={`${node.id}-${targetId}`}>
                  <line
                    x1={`${node.x}%`}
                    y1={`${node.y}%`}
                    x2={`${target.x}%`}
                    y2={`${target.y}%`}
                    stroke="rgba(59, 130, 246, 0.3)"
                    strokeWidth="2"
                    strokeDasharray="5,5"
                    className="animate-pulse"
                  />
                  {/* Animated dot */}
                  <circle
                    r="3"
                    fill="rgba(59, 130, 246, 0.8)"
                    className="animate-pulse"
                  >
                    <animateMotion
                      dur="3s"
                      repeatCount="indefinite"
                      path={`M ${node.x * window.innerWidth / 100},${node.y * window.innerHeight / 100} L ${target.x * window.innerWidth / 100},${target.y * window.innerHeight / 100}`}
                    />
                  </circle>
                </g>
              )
            })
          )}
        </svg>

        {/* Nodes */}
        {nodes.map(node => (
          <div
            key={node.id}
            className={`absolute transform -translate-x-1/2 -translate-y-1/2 cursor-pointer transition-all duration-300 ${
              selectedNode === node.id ? 'scale-110 z-10' : 'hover:scale-105'
            }`}
            style={{ left: `${node.x}%`, top: `${node.y}%` }}
            onClick={() => setSelectedNode(node.id === selectedNode ? null : node.id)}
          >
            <div className={`
              p-4 rounded-lg border-2 backdrop-blur-sm
              ${getNodeColor(node.status, node.type)}
              ${node.status === 'active' ? 'animate-pulse' : ''}
            `}>
              <div className="flex flex-col items-center gap-2">
                {getNodeIcon(node.type)}
                <span className="text-xs font-medium whitespace-nowrap">{node.label}</span>
                {node.status === 'active' && (
                  <div className="absolute -inset-4 rounded-lg bg-current opacity-20 animate-ping" />
                )}
              </div>
            </div>
          </div>
        ))}

        {/* Selected Node Details */}
        {selectedNode && (
          <div className="absolute bottom-4 left-4 right-4 bg-gray-800/90 backdrop-blur-sm rounded-lg p-4 border border-gray-700">
            <div className="flex items-start justify-between">
              <div>
                <h3 className="text-white font-medium mb-1">
                  {nodes.find(n => n.id === selectedNode)?.label}
                </h3>
                <p className="text-xs text-gray-400">
                  Type: {nodes.find(n => n.id === selectedNode)?.type}
                </p>
                <p className="text-xs text-gray-400">
                  Status: {nodes.find(n => n.id === selectedNode)?.status}
                </p>
                {nodes.find(n => n.id === selectedNode)?.connections.length > 0 && (
                  <p className="text-xs text-gray-400 mt-2">
                    Connected to: {nodes.find(n => n.id === selectedNode)?.connections.join(', ')}
                  </p>
                )}
              </div>
              <button
                onClick={() => setSelectedNode(null)}
                className="text-gray-400 hover:text-white"
              >
                ×
              </button>
            </div>
          </div>
        )}
      </div>

      {/* Footer */}
      <div className="px-6 py-3 border-t border-gray-800 bg-gray-900/50">
        <div className="flex items-center justify-between text-xs">
          <span className="text-gray-400">
            {nodes.filter(n => n.status === 'active').length} Active Components
          </span>
          <span className="text-gray-400">
            {nodes.reduce((acc, n) => acc + n.connections.length, 0)} Connections
          </span>
          <span className="text-gray-400">
            System Health: <span className="text-green-400">Operational</span>
          </span>
        </div>
      </div>
    </div>
  )
}