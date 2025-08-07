import { io, Socket } from 'socket.io-client'

class WebSocketService {
  private socket: Socket | null = null
  private listeners: Map<string, Set<Function>> = new Map()

  connect(url: string = 'http://localhost:5002') {
    if (this.socket?.connected) {
      return
    }

    this.socket = io(url, {
      transports: ['websocket'],
      reconnection: true,
      reconnectionAttempts: 5,
      reconnectionDelay: 1000,
    })

    this.socket.on('connect', () => {
      console.log('WebSocket connected')
      this.emit('connection_status', { connected: true })
    })

    this.socket.on('disconnect', () => {
      console.log('WebSocket disconnected')
      this.emit('connection_status', { connected: false })
    })

    // Forward all events to listeners
    const events = [
      'queue_data',
      'investigation_update',
      'agent_update',
      'dlq_update',
      'timeline_event',
      'metric_update',
      'alert',
      'logs_data',
    ]

    events.forEach(event => {
      this.socket?.on(event, (data) => {
        this.emit(event, data)
      })
    })
  }

  disconnect() {
    this.socket?.disconnect()
    this.socket = null
  }

  on(event: string, callback: Function) {
    if (!this.listeners.has(event)) {
      this.listeners.set(event, new Set())
    }
    this.listeners.get(event)?.add(callback)
  }

  off(event: string, callback: Function) {
    this.listeners.get(event)?.delete(callback)
  }

  emit(event: string, data: any) {
    this.listeners.get(event)?.forEach(callback => callback(data))
  }

  send(event: string, data: any) {
    this.socket?.emit(event, data)
  }
}

export const websocketService = new WebSocketService()