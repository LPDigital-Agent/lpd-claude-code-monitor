'use client'

import { LayoutDashboard, Brain, Eye, Terminal } from 'lucide-react'
import { useState } from 'react'

type Tab = 'dashboard' | 'glass-room' | 'observe' | 'terminal'

interface TabNavigationProps {
  activeTab: Tab
  onTabChange: (tab: Tab) => void
}

export function TabNavigation({ activeTab, onTabChange }: TabNavigationProps) {
  const tabs = [
    { id: 'dashboard' as Tab, label: 'Dashboard', icon: LayoutDashboard },
    { id: 'glass-room' as Tab, label: 'Glass Room', icon: Brain },
    { id: 'observe' as Tab, label: 'Observe Mode', icon: Eye },
    { id: 'terminal' as Tab, label: 'AI Terminal', icon: Terminal },
  ]

  return (
    <div className="h-12 bg-gray-900 border-b border-gray-800 flex items-center px-4">
      <div className="flex gap-1">
        {tabs.map((tab) => {
          const Icon = tab.icon
          const isActive = activeTab === tab.id
          
          return (
            <button
              key={tab.id}
              onClick={() => onTabChange(tab.id)}
              className={`
                px-4 py-2 rounded-t-lg transition-all duration-200 flex items-center gap-2
                ${isActive 
                  ? 'bg-gray-800 text-primary-400 border-t-2 border-primary-500' 
                  : 'text-gray-400 hover:text-gray-200 hover:bg-gray-800/50'
                }
              `}
            >
              <Icon className="w-4 h-4" />
              <span className="text-sm font-medium">{tab.label}</span>
            </button>
          )
        })}
      </div>
    </div>
  )
}