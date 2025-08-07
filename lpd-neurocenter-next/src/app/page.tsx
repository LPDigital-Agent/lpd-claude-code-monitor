'use client'

import { useState } from 'react'
import { Topbar } from '@/components/layout/Topbar'
import { QuickAccessToolbar } from '@/components/layout/QuickAccessToolbar'
import { TabNavigation } from '@/components/layout/TabNavigation'
import { DeadLetterQueuesPanel } from '@/components/panels/DeadLetterQueuesPanel'
import { LiveAgentPanel } from '@/components/panels/LiveAgentPanel'
import { AWSSQSMonitorPanel } from '@/components/panels/AWSSQSMonitorPanel'
import { InvestigationTimelinePanel } from '@/components/panels/InvestigationTimelinePanel'

type Tab = 'dashboard' | 'glass-room' | 'observe' | 'terminal'

export default function NeuroCenterPage() {
  const [activeTab, setActiveTab] = useState<Tab>('dashboard')

  return (
    <div className="min-h-screen bg-gray-950 flex flex-col">
      <Topbar />
      <QuickAccessToolbar />
      <TabNavigation activeTab={activeTab} onTabChange={setActiveTab} />
      
      {/* Dashboard Tab */}
      {activeTab === 'dashboard' && (
        <div className="flex-1 p-4">
          <div className="h-full grid grid-cols-2 grid-rows-2 gap-4">
            {/* Top Left - Dead Letter Queues */}
            <div className="row-span-1">
              <DeadLetterQueuesPanel />
            </div>
            
            {/* Top Right - Live Agents */}
            <div className="row-span-1">
              <LiveAgentPanel />
            </div>
            
            {/* Bottom Left - AWS SQS Monitor */}
            <div className="row-span-1">
              <AWSSQSMonitorPanel />
            </div>
            
            {/* Bottom Right - Investigation Timeline */}
            <div className="row-span-1">
              <InvestigationTimelinePanel />
            </div>
          </div>
        </div>
      )}
      
      {/* Glass Room Tab */}
      {activeTab === 'glass-room' && (
        <div className="flex-1 p-4">
          <div className="h-full bg-gray-900/50 backdrop-blur-sm rounded-lg border border-gray-800 flex items-center justify-center">
            <div className="text-center">
              <h2 className="text-2xl font-bold text-white mb-2">Glass Room</h2>
              <p className="text-gray-400">Agent Activity Feed & Context Storyline</p>
            </div>
          </div>
        </div>
      )}
      
      {/* Observe Mode Tab */}
      {activeTab === 'observe' && (
        <div className="flex-1 p-4">
          <div className="h-full bg-gray-900/50 backdrop-blur-sm rounded-lg border border-gray-800 flex items-center justify-center">
            <div className="text-center">
              <h2 className="text-2xl font-bold text-white mb-2">Observe Mode</h2>
              <p className="text-gray-400">Cinematic Agent Visualization</p>
            </div>
          </div>
        </div>
      )}
      
      {/* AI Terminal Tab */}
      {activeTab === 'terminal' && (
        <div className="flex-1 p-4">
          <div className="h-full bg-gray-900/50 backdrop-blur-sm rounded-lg border border-gray-800 p-4">
            <div className="h-full flex flex-col">
              <div className="flex-1 bg-black rounded-lg p-4 font-mono text-sm overflow-y-auto">
                <div className="text-green-400">
                  Welcome to NeuroCenter AI Terminal v1.0<br />
                  Type 'help' for available commands or ask questions in natural language.<br />
                  ────────────────────────────────────────────────────────────<br />
                </div>
              </div>
              <div className="mt-4 flex items-center gap-2">
                <span className="text-green-400 font-mono">neurocenter@ai &gt;</span>
                <input
                  type="text"
                  className="flex-1 bg-transparent border-b border-gray-700 text-white font-mono text-sm focus:outline-none focus:border-primary-500 transition-colors duration-200"
                  placeholder="Ask about agents, incidents, or type commands..."
                />
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}