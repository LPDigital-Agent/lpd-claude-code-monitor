'use client'

import { useState } from 'react'
import { Topbar } from '@/components/layout/Topbar'
import { QuickAccessToolbar } from '@/components/layout/QuickAccessToolbar'
import { TabNavigation } from '@/components/layout/TabNavigation'
import { DeadLetterQueuesPanel } from '@/components/panels/DeadLetterQueuesPanel'
import { LiveAgentPanel } from '@/components/panels/LiveAgentPanel'
import { AWSSQSMonitorPanel } from '@/components/panels/AWSSQSMonitorPanel'
import { InvestigationTimelinePanel } from '@/components/panels/InvestigationTimelinePanel'
import { GlassRoomPanel } from '@/components/panels/GlassRoomPanel'
import { ObserveModePanel } from '@/components/panels/ObserveModePanel'
import { AITerminalPanel } from '@/components/panels/AITerminalPanel'

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
          <div className="h-full">
            <GlassRoomPanel />
          </div>
        </div>
      )}
      
      {/* Observe Mode Tab */}
      {activeTab === 'observe' && (
        <div className="flex-1 p-4">
          <div className="h-full">
            <ObserveModePanel />
          </div>
        </div>
      )}
      
      {/* AI Terminal Tab */}
      {activeTab === 'terminal' && (
        <div className="flex-1 p-4">
          <div className="h-full">
            <AITerminalPanel />
          </div>
        </div>
      )}
    </div>
  )
}