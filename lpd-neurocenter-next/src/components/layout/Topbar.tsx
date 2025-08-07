'use client'

import { Bell, Settings, Volume2 } from 'lucide-react'
import Image from 'next/image'
import { useState } from 'react'

export function Topbar() {
  const [voiceEnabled, setVoiceEnabled] = useState(true)
  const [alertCount] = useState(3)

  return (
    <div className="h-14 bg-gradient-to-r from-gray-900 via-gray-800 to-gray-900 border-b border-primary-500/20 flex items-center justify-between px-6">
      {/* Left Section - Branding */}
      <div className="flex items-center gap-3">
        <div className="w-8 h-8 relative">
          <div className="absolute inset-0 bg-primary-500 rounded-lg opacity-20 animate-pulse" />
          <div className="relative w-full h-full flex items-center justify-center">
            <span className="text-primary-500 font-bold text-xl">⬢</span>
          </div>
        </div>
        <div className="flex items-center gap-2">
          <span className="text-primary-500 font-bold text-lg">LPD HIVE</span>
          <span className="text-gray-400 text-sm">|</span>
          <span className="text-white font-medium">Agent NeuroCenter</span>
        </div>
      </div>

      {/* Center Section - Status */}
      <div className="flex items-center gap-2">
        <span className="relative flex h-3 w-3">
          <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-green-400 opacity-75"></span>
          <span className="relative inline-flex rounded-full h-3 w-3 bg-green-500"></span>
        </span>
        <span className="text-green-400 text-sm font-medium uppercase tracking-wider">
          OPERATIONAL
        </span>
      </div>

      {/* Right Section - Actions */}
      <div className="flex items-center gap-2">
        <button
          onClick={() => setVoiceEnabled(!voiceEnabled)}
          className={`p-2 rounded-lg transition-all duration-200 ${
            voiceEnabled 
              ? 'bg-primary-500/20 text-primary-400 hover:bg-primary-500/30' 
              : 'bg-gray-700/50 text-gray-400 hover:bg-gray-700'
          }`}
          title="Voice Notifications"
        >
          <Volume2 className="w-5 h-5" />
        </button>
        
        <button
          className="relative p-2 bg-gray-700/50 text-gray-400 rounded-lg hover:bg-gray-700 transition-all duration-200"
          title="System Alerts"
        >
          <Bell className="w-5 h-5" />
          {alertCount > 0 && (
            <span className="absolute -top-1 -right-1 bg-red-500 text-white text-xs rounded-full w-5 h-5 flex items-center justify-center font-medium">
              {alertCount}
            </span>
          )}
        </button>
        
        <button
          className="p-2 bg-gray-700/50 text-gray-400 rounded-lg hover:bg-gray-700 transition-all duration-200"
          title="Settings"
        >
          <Settings className="w-5 h-5" />
        </button>
      </div>
    </div>
  )
}