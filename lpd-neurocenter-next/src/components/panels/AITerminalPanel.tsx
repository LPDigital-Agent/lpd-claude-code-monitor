'use client'

import { Terminal, Send, Loader2, ChevronRight } from 'lucide-react'
import { useState, useRef, useEffect, KeyboardEvent } from 'react'

interface CommandHistory {
  id: string
  command: string
  response: string
  timestamp: Date
  type: 'command' | 'response' | 'error' | 'info'
}

export function AITerminalPanel() {
  const [input, setInput] = useState('')
  const [history, setHistory] = useState<CommandHistory[]>([
    {
      id: '1',
      command: '',
      response: 'Welcome to NeuroCenter AI Terminal v2.0',
      timestamp: new Date(),
      type: 'info'
    },
    {
      id: '2',
      command: '',
      response: 'Type "help" for available commands or ask questions in natural language.',
      timestamp: new Date(),
      type: 'info'
    },
    {
      id: '3',
      command: '',
      response: '────────────────────────────────────────────────────────────',
      timestamp: new Date(),
      type: 'info'
    }
  ])
  const [isProcessing, setIsProcessing] = useState(false)
  const [commandHistoryIndex, setCommandHistoryIndex] = useState(-1)
  const [commandHistoryList, setCommandHistoryList] = useState<string[]>([])
  
  const terminalRef = useRef<HTMLDivElement>(null)
  const inputRef = useRef<HTMLInputElement>(null)

  useEffect(() => {
    if (terminalRef.current) {
      terminalRef.current.scrollTop = terminalRef.current.scrollHeight
    }
  }, [history])

  const processCommand = async (command: string) => {
    if (!command.trim()) return
    
    // Add command to history
    const commandEntry: CommandHistory = {
      id: Date.now().toString(),
      command: command,
      response: '',
      timestamp: new Date(),
      type: 'command'
    }
    
    setHistory(prev => [...prev, commandEntry])
    setIsProcessing(true)

    try {
      // Special handling for clear command
      if (command.trim().toLowerCase() === 'clear') {
        setHistory([
          {
            id: Date.now().toString(),
            command: '',
            response: 'Welcome to NeuroCenter AI Terminal v2.0',
            timestamp: new Date(),
            type: 'info'
          },
          {
            id: Date.now().toString() + '1',
            command: '',
            response: 'Type "help" for available commands or ask questions in natural language.',
            timestamp: new Date(),
            type: 'info'
          }
        ])
        setIsProcessing(false)
        return
      }

      // Send command to backend - using direct Flask URL due to Next.js proxy issues
      const response = await fetch('http://localhost:5002/api/terminal/execute', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ command })
      })

      const data = await response.json()
      
      // Handle clear command from backend
      if (data.type === 'clear') {
        setHistory([
          {
            id: Date.now().toString(),
            command: '',
            response: 'Welcome to NeuroCenter AI Terminal v2.0',
            timestamp: new Date(),
            type: 'info'
          },
          {
            id: Date.now().toString() + '1',
            command: '',
            response: 'Type "help" for available commands or ask questions in natural language.',
            timestamp: new Date(),
            type: 'info'
          }
        ])
      } else {
        // Add response to history
        const responseEntry: CommandHistory = {
          id: Date.now().toString() + '_response',
          command: '',
          response: data.response || 'No response',
          timestamp: new Date(),
          type: data.type || 'response'
        }
        
        setHistory(prev => [...prev, responseEntry])
      }
    } catch (error) {
      // Add error to history
      const errorEntry: CommandHistory = {
        id: Date.now().toString() + '_error',
        command: '',
        response: `Error: ${error instanceof Error ? error.message : 'Command failed'}`,
        timestamp: new Date(),
        type: 'error'
      }
      
      setHistory(prev => [...prev, errorEntry])
    } finally {
      setIsProcessing(false)
    }
  }

  const handleSubmit = async () => {
    if (input.trim() && !isProcessing) {
      const command = input
      setCommandHistoryList(prev => [...prev, command])
      setCommandHistoryIndex(-1)
      setInput('')
      await processCommand(command)
    }
  }

  const handleKeyDown = (e: KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Enter') {
      handleSubmit()
    } else if (e.key === 'ArrowUp') {
      e.preventDefault()
      if (commandHistoryList.length > 0) {
        const newIndex = commandHistoryIndex < commandHistoryList.length - 1 
          ? commandHistoryIndex + 1 
          : commandHistoryIndex
        setCommandHistoryIndex(newIndex)
        setInput(commandHistoryList[commandHistoryList.length - 1 - newIndex])
      }
    } else if (e.key === 'ArrowDown') {
      e.preventDefault()
      if (commandHistoryIndex > 0) {
        const newIndex = commandHistoryIndex - 1
        setCommandHistoryIndex(newIndex)
        setInput(commandHistoryList[commandHistoryList.length - 1 - newIndex])
      } else if (commandHistoryIndex === 0) {
        setCommandHistoryIndex(-1)
        setInput('')
      }
    }
  }

  const formatResponse = (text: string) => {
    // Preserve formatting for multi-line responses
    return text.split('\n').map((line, i) => (
      <div key={i} className="leading-relaxed">
        {line || '\u00A0'}
      </div>
    ))
  }

  return (
    <div className="h-full bg-gray-900/50 backdrop-blur-sm rounded-lg border border-gray-800 flex flex-col">
      {/* Header */}
      <div className="px-6 py-4 border-b border-gray-800 bg-gradient-to-r from-gray-800/50 to-gray-900/50">
        <div className="flex items-center gap-3">
          <Terminal className="w-6 h-6 text-primary-400" />
          <div>
            <h2 className="text-xl font-bold text-white">AI Terminal</h2>
            <p className="text-xs text-gray-400">Natural Language Command Interface</p>
          </div>
        </div>
      </div>

      {/* Terminal Output */}
      <div 
        ref={terminalRef}
        className="flex-1 overflow-y-auto p-4 font-mono text-sm space-y-2"
        onClick={() => inputRef.current?.focus()}
      >
        {history.map(entry => (
          <div key={entry.id} className="group">
            {entry.command && (
              <div className="flex items-start gap-2 text-green-400">
                <ChevronRight className="w-4 h-4 mt-0.5 flex-shrink-0" />
                <span className="break-all">{entry.command}</span>
              </div>
            )}
            {entry.response && (
              <div className={`pl-6 ${
                entry.type === 'error' ? 'text-red-400' :
                entry.type === 'info' ? 'text-blue-400' :
                'text-gray-300'
              }`}>
                {formatResponse(entry.response)}
              </div>
            )}
          </div>
        ))}
        
        {/* Current Input Line */}
        <div className="flex items-start gap-2">
          <ChevronRight className={`w-4 h-4 mt-0.5 flex-shrink-0 ${
            isProcessing ? 'text-yellow-400 animate-pulse' : 'text-green-400'
          }`} />
          <div className="flex-1 flex items-center gap-2">
            <span className="text-green-400">neurocenter@ai</span>
            <span className="text-gray-500">{'>'}</span>
            <input
              ref={inputRef}
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={handleKeyDown}
              disabled={isProcessing}
              className="flex-1 bg-transparent text-gray-300 outline-none placeholder-gray-600"
              placeholder={isProcessing ? 'Processing...' : 'Type a command or ask a question...'}
              autoFocus
            />
            {isProcessing && <Loader2 className="w-4 h-4 text-yellow-400 animate-spin" />}
          </div>
        </div>
      </div>

      {/* Footer */}
      <div className="px-6 py-3 border-t border-gray-800 bg-gray-800/30">
        <div className="flex items-center justify-between text-xs text-gray-500">
          <div className="flex items-center gap-4">
            <span>Press Enter to submit</span>
            <span>Use ↑↓ for history</span>
            <span>Type "help" for commands</span>
          </div>
          <button
            onClick={handleSubmit}
            disabled={isProcessing || !input.trim()}
            className="flex items-center gap-1 px-3 py-1 rounded bg-primary-500/20 text-primary-400 hover:bg-primary-500/30 disabled:opacity-50 disabled:cursor-not-allowed transition-all"
          >
            <Send className="w-3 h-3" />
            <span>Send</span>
          </button>
        </div>
      </div>
    </div>
  )
}