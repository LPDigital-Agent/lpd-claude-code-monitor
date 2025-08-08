'use client'

import { useState, useEffect } from 'react'
import { 
  ToggleLeft,
  ToggleRight,
  FileText, 
  Minimize2,
  Maximize2
} from 'lucide-react'
import { toast } from 'sonner'

export function QuickAccessToolbar() {
  const [autoMode, setAutoMode] = useState(false)
  const [compactMode, setCompactMode] = useState(false)
  const [logsVisible, setLogsVisible] = useState(false)

  const toggleAutoMode = () => {
    setAutoMode(!autoMode)
    toast.success(autoMode ? 'Auto Mode disabled' : 'Auto Mode enabled')
    // Store preference in localStorage
    if (typeof window !== 'undefined') {
      localStorage.setItem('neurocenter-auto-mode', (!autoMode).toString())
    }
  }

  const toggleCompactMode = () => {
    setCompactMode(!compactMode)
    toast.success(compactMode ? 'Expanded view' : 'Compact view')
    // Dispatch event for panels to listen to
    window.dispatchEvent(new CustomEvent('compact-mode-change', { 
      detail: { compact: !compactMode } 
    }))
    if (typeof window !== 'undefined') {
      localStorage.setItem('neurocenter-compact-mode', (!compactMode).toString())
    }
  }

  const openLogs = () => {
    // Open logs in new window or modal
    setLogsVisible(true)
    window.open('/logs', '_blank', 'width=800,height=600')
    toast.info('Opening logs viewer...')
  }

  // Load saved preferences on mount - client side only
  useEffect(() => {
    if (typeof window !== 'undefined') {
      const savedAutoMode = localStorage.getItem('neurocenter-auto-mode')
      const savedCompactMode = localStorage.getItem('neurocenter-compact-mode')
      
      if (savedAutoMode === 'true') setAutoMode(true)
      if (savedCompactMode === 'true') {
        setCompactMode(true)
        window.dispatchEvent(new CustomEvent('compact-mode-change', { 
          detail: { compact: true } 
        }))
      }
    }
  }, [])

  return (
    <div className="h-10 bg-gray-800/50 border-b border-gray-700 flex items-center px-4 gap-1">
      <button 
        onClick={toggleAutoMode}
        className={`px-3 py-1.5 text-xs font-medium rounded-md transition-all duration-200 flex items-center gap-1.5 ${
          autoMode 
            ? 'bg-primary-500/20 text-primary-400 hover:bg-primary-500/30' 
            : 'text-gray-300 hover:text-white hover:bg-gray-700/50'
        }`}
        title={autoMode ? 'Disable Auto Mode' : 'Enable Auto Mode'}
      >
        {autoMode ? (
          <ToggleRight className="w-3.5 h-3.5" />
        ) : (
          <ToggleLeft className="w-3.5 h-3.5" />
        )}
        <span>Auto Mode</span>
      </button>
      
      <button 
        onClick={openLogs}
        className="px-3 py-1.5 text-xs font-medium text-gray-300 hover:text-white hover:bg-gray-700/50 rounded-md transition-all duration-200 flex items-center gap-1.5"
        title="View system logs"
      >
        <FileText className="w-3.5 h-3.5" />
        <span>View Logs</span>
      </button>
      
      <div className="w-px h-5 bg-gray-600 mx-2" />
      
      <button 
        onClick={toggleCompactMode}
        className={`px-3 py-1.5 text-xs font-medium rounded-md transition-all duration-200 flex items-center gap-1.5 ${
          compactMode 
            ? 'bg-blue-500/20 text-blue-400 hover:bg-blue-500/30' 
            : 'text-gray-300 hover:text-white hover:bg-gray-700/50'
        }`}
        title={compactMode ? 'Switch to expanded view' : 'Switch to compact view'}
      >
        {compactMode ? (
          <Maximize2 className="w-3.5 h-3.5" />
        ) : (
          <Minimize2 className="w-3.5 h-3.5" />
        )}
        <span>{compactMode ? 'Expand' : 'Compact'}</span>
      </button>
    </div>
  )
}