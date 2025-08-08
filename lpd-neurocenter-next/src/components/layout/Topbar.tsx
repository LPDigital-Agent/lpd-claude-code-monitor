'use client'

import { Bell, Settings, Volume2, X } from 'lucide-react'
import Image from 'next/image'
import { useState, useEffect } from 'react'
import { toast } from 'sonner'

export function Topbar() {
  const [voiceEnabled, setVoiceEnabled] = useState(true)
  const [alertCount, setAlertCount] = useState(3)
  const [showNotifications, setShowNotifications] = useState(false)
  const [showSettings, setShowSettings] = useState(false)
  const [notifications, setNotifications] = useState([
    { id: 1, type: 'warning', message: 'High DLQ message count detected', time: '2 min ago' },
    { id: 2, type: 'success', message: 'Investigation completed successfully', time: '15 min ago' },
    { id: 3, type: 'info', message: 'System monitoring active', time: '1 hour ago' }
  ])

  // Load voice preference from localStorage
  useEffect(() => {
    if (typeof window !== 'undefined') {
      const savedVoice = localStorage.getItem('neurocenter-voice-enabled')
      if (savedVoice !== null) {
        setVoiceEnabled(savedVoice === 'true')
      }
    }
  }, [])

  const toggleVoice = () => {
    const newState = !voiceEnabled
    setVoiceEnabled(newState)
    if (typeof window !== 'undefined') {
      localStorage.setItem('neurocenter-voice-enabled', newState.toString())
    }
    toast.success(newState ? 'Voice notifications enabled' : 'Voice notifications disabled')
  }

  const clearNotifications = () => {
    setNotifications([])
    setAlertCount(0)
    toast.info('All notifications cleared')
  }

  const dismissNotification = (id: number) => {
    setNotifications(prev => prev.filter(n => n.id !== id))
    setAlertCount(prev => Math.max(0, prev - 1))
  }

  return (
    <>
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
            onClick={toggleVoice}
            className={`p-2 rounded-lg transition-all duration-200 ${
              voiceEnabled 
                ? 'bg-primary-500/20 text-primary-400 hover:bg-primary-500/30' 
                : 'bg-gray-700/50 text-gray-400 hover:bg-gray-700'
            }`}
            title={voiceEnabled ? "Voice Notifications On" : "Voice Notifications Off"}
          >
            <Volume2 className="w-5 h-5" />
          </button>
          
          <button
            onClick={() => setShowNotifications(!showNotifications)}
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
            onClick={() => setShowSettings(!showSettings)}
            className="p-2 bg-gray-700/50 text-gray-400 rounded-lg hover:bg-gray-700 transition-all duration-200"
            title="Settings"
          >
            <Settings className="w-5 h-5" />
          </button>
        </div>
      </div>

      {/* Notifications Dropdown */}
      {showNotifications && (
        <div className="absolute right-6 top-16 w-80 bg-gray-800 border border-gray-700 rounded-lg shadow-xl z-50">
          <div className="p-4 border-b border-gray-700 flex items-center justify-between">
            <h3 className="text-white font-medium">Notifications</h3>
            <button
              onClick={clearNotifications}
              className="text-xs text-gray-400 hover:text-white transition-colors"
            >
              Clear All
            </button>
          </div>
          <div className="max-h-96 overflow-y-auto">
            {notifications.length === 0 ? (
              <div className="p-8 text-center text-gray-500">
                No notifications
              </div>
            ) : (
              notifications.map(notification => (
                <div
                  key={notification.id}
                  className="p-4 border-b border-gray-700 hover:bg-gray-700/50 transition-colors"
                >
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <p className={`text-sm ${
                        notification.type === 'warning' ? 'text-yellow-400' :
                        notification.type === 'success' ? 'text-green-400' :
                        'text-blue-400'
                      }`}>
                        {notification.message}
                      </p>
                      <p className="text-xs text-gray-500 mt-1">{notification.time}</p>
                    </div>
                    <button
                      onClick={() => dismissNotification(notification.id)}
                      className="ml-2 text-gray-500 hover:text-white transition-colors"
                    >
                      <X className="w-4 h-4" />
                    </button>
                  </div>
                </div>
              ))
            )}
          </div>
        </div>
      )}

      {/* Settings Dropdown */}
      {showSettings && (
        <div className="absolute right-6 top-16 w-64 bg-gray-800 border border-gray-700 rounded-lg shadow-xl z-50">
          <div className="p-4 border-b border-gray-700">
            <h3 className="text-white font-medium">Settings</h3>
          </div>
          <div className="p-4 space-y-3">
            <button
              onClick={() => {
                window.open('/logs', '_blank')
                setShowSettings(false)
              }}
              className="w-full text-left px-3 py-2 text-sm text-gray-300 hover:bg-gray-700 rounded transition-colors"
            >
              View System Logs
            </button>
            <button
              onClick={() => {
                toast.info('Refreshing dashboard...')
                window.location.reload()
                setShowSettings(false)
              }}
              className="w-full text-left px-3 py-2 text-sm text-gray-300 hover:bg-gray-700 rounded transition-colors"
            >
              Refresh Dashboard
            </button>
            <button
              onClick={() => {
                if (typeof window !== 'undefined') {
                  localStorage.clear()
                  toast.success('Settings cleared')
                  window.location.reload()
                }
                setShowSettings(false)
              }}
              className="w-full text-left px-3 py-2 text-sm text-gray-300 hover:bg-gray-700 rounded transition-colors"
            >
              Clear Settings
            </button>
            <div className="pt-3 border-t border-gray-700">
              <p className="text-xs text-gray-500">Version 2.0.0</p>
              <p className="text-xs text-gray-500">© 2025 LPD HIVE</p>
            </div>
          </div>
        </div>
      )}
    </>
  )
}