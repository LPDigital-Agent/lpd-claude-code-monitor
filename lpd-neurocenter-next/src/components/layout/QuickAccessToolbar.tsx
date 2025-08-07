'use client'

import { 
  SearchCheck, 
  Trash2, 
  Download, 
  ToggleLeft, 
  FileText, 
  Minimize2 
} from 'lucide-react'

export function QuickAccessToolbar() {
  return (
    <div className="h-10 bg-gray-800/50 border-b border-gray-700 flex items-center px-4 gap-1">
      <button className="px-3 py-1.5 text-xs font-medium text-gray-300 hover:text-white hover:bg-gray-700/50 rounded-md transition-all duration-200 flex items-center gap-1.5">
        <SearchCheck className="w-3.5 h-3.5" />
        <span>Investigate All</span>
      </button>
      
      <button className="px-3 py-1.5 text-xs font-medium text-gray-300 hover:text-white hover:bg-gray-700/50 rounded-md transition-all duration-200 flex items-center gap-1.5">
        <Trash2 className="w-3.5 h-3.5" />
        <span>Purge Queues</span>
      </button>
      
      <button className="px-3 py-1.5 text-xs font-medium text-gray-300 hover:text-white hover:bg-gray-700/50 rounded-md transition-all duration-200 flex items-center gap-1.5">
        <Download className="w-3.5 h-3.5" />
        <span>Export Report</span>
      </button>
      
      <button className="px-3 py-1.5 text-xs font-medium text-gray-300 hover:text-white hover:bg-gray-700/50 rounded-md transition-all duration-200 flex items-center gap-1.5">
        <ToggleLeft className="w-3.5 h-3.5" />
        <span>Auto Mode</span>
      </button>
      
      <button className="px-3 py-1.5 text-xs font-medium text-gray-300 hover:text-white hover:bg-gray-700/50 rounded-md transition-all duration-200 flex items-center gap-1.5">
        <FileText className="w-3.5 h-3.5" />
        <span>View Logs</span>
      </button>
      
      <div className="w-px h-5 bg-gray-600 mx-2" />
      
      <button className="px-3 py-1.5 text-xs font-medium text-gray-300 hover:text-white hover:bg-gray-700/50 rounded-md transition-all duration-200 flex items-center gap-1.5">
        <Minimize2 className="w-3.5 h-3.5" />
        <span>Compact</span>
      </button>
    </div>
  )
}