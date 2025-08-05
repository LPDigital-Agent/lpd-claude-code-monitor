#!/usr/bin/env python3
"""
Real-time Claude Investigation Monitor
Shows live status of Claude sessions with auto-refresh
"""
import subprocess
import time
import os
import sys
import json
from datetime import datetime
import curses
from pathlib import Path

class LiveClaudeMonitor:
    """Live monitoring interface for Claude investigations"""
    
    def __init__(self):
        self.session_file = ".claude_sessions.json"
        self.log_file = "dlq_monitor_FABIO-PROD_sa-east-1.log"
        self.refresh_interval = 5  # seconds
        
    def get_claude_processes(self):
        """Get current Claude processes"""
        processes = []
        try:
            result = subprocess.run(['ps', 'aux'], capture_output=True, text=True)
            lines = result.stdout.split('\n')
            
            for line in lines:
                if 'claude' in line.lower() and 'grep' not in line:
                    parts = line.split(None, 10)
                    if len(parts) > 10:
                        processes.append({
                            'pid': parts[1],
                            'cpu': parts[2],
                            'mem': parts[3],
                            'start': parts[8],
                            'time': parts[9],
                            'cmd': parts[10][:50] + '...' if len(parts[10]) > 50 else parts[10]
                        })
        except:
            pass
        return processes
    
    def get_recent_logs(self, lines=20):
        """Get recent investigation logs"""
        events = []
        try:
            result = subprocess.run(
                ['grep', '-i', 'investigation\\|claude', self.log_file],
                capture_output=True, text=True
            )
            if result.returncode == 0:
                log_lines = result.stdout.strip().split('\n')
                for line in log_lines[-lines:]:
                    if line:
                        # Extract timestamp and message
                        parts = line.split(' - ', 3)
                        if len(parts) >= 4:
                            timestamp = parts[0]
                            message = parts[-1]
                            
                            # Determine event type
                            event_type = 'info'
                            if 'Starting' in message:
                                event_type = 'start'
                            elif 'completed successfully' in message:
                                event_type = 'success'
                            elif 'failed' in message:
                                event_type = 'error'
                            elif 'timeout' in message:
                                event_type = 'timeout'
                            
                            events.append({
                                'time': timestamp,
                                'type': event_type,
                                'message': message[:80]
                            })
        except:
            pass
        return events
    
    def display(self, stdscr):
        """Main display loop using curses"""
        curses.curs_set(0)  # Hide cursor
        stdscr.nodelay(1)    # Non-blocking input
        stdscr.timeout(100)  # Refresh timeout
        
        # Color pairs
        curses.init_pair(1, curses.COLOR_GREEN, curses.COLOR_BLACK)
        curses.init_pair(2, curses.COLOR_RED, curses.COLOR_BLACK)
        curses.init_pair(3, curses.COLOR_YELLOW, curses.COLOR_BLACK)
        curses.init_pair(4, curses.COLOR_CYAN, curses.COLOR_BLACK)
        curses.init_pair(5, curses.COLOR_MAGENTA, curses.COLOR_BLACK)
        
        while True:
            stdscr.clear()
            height, width = stdscr.getmaxyx()
            
            # Header
            header = "🤖 CLAUDE INVESTIGATION LIVE MONITOR 🤖"
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            stdscr.addstr(0, (width - len(header)) // 2, header, curses.A_BOLD)
            stdscr.addstr(1, (width - len(timestamp)) // 2, timestamp)
            stdscr.addstr(2, 0, "=" * width)
            
            row = 4
            
            # Active Processes Section
            processes = self.get_claude_processes()
            stdscr.addstr(row, 0, "📊 ACTIVE CLAUDE PROCESSES", curses.A_BOLD | curses.color_pair(4))
            row += 1
            stdscr.addstr(row, 0, "-" * width)
            row += 1
            
            if processes:
                # Header row
                stdscr.addstr(row, 0, "PID      CPU    MEM    TIME      STATUS")
                row += 1
                
                for proc in processes:
                    status_line = f"{proc['pid']:<8} {proc['cpu']:<6} {proc['mem']:<6} {proc['time']:<10} Running"
                    stdscr.addstr(row, 0, status_line, curses.color_pair(1))
                    row += 1
                    cmd_line = f"  └─ {proc['cmd']}"
                    stdscr.addstr(row, 0, cmd_line[:width-2])
                    row += 1
            else:
                stdscr.addstr(row, 0, "No active Claude processes", curses.color_pair(3))
                row += 1
            
            row += 2
            
            # Recent Events Section
            events = self.get_recent_logs(10)
            stdscr.addstr(row, 0, "📜 RECENT INVESTIGATION EVENTS", curses.A_BOLD | curses.color_pair(5))
            row += 1
            stdscr.addstr(row, 0, "-" * width)
            row += 1
            
            if events:
                for event in events[-8:]:  # Show last 8 events
                    # Choose color based on event type
                    color = curses.color_pair(1)  # Default green
                    icon = "•"
                    if event['type'] == 'start':
                        icon = "▶"
                        color = curses.color_pair(4)
                    elif event['type'] == 'success':
                        icon = "✓"
                        color = curses.color_pair(1)
                    elif event['type'] == 'error':
                        icon = "✗"
                        color = curses.color_pair(2)
                    elif event['type'] == 'timeout':
                        icon = "⏰"
                        color = curses.color_pair(3)
                    
                    event_line = f"{icon} {event['time'][-8:]} {event['message']}"
                    if row < height - 4:
                        stdscr.addstr(row, 0, event_line[:width-2], color)
                        row += 1
            else:
                stdscr.addstr(row, 0, "No recent events", curses.color_pair(3))
                row += 1
            
            # Footer
            footer_row = height - 2
            stdscr.addstr(footer_row, 0, "=" * width)
            controls = "Press 'q' to quit | 'r' to refresh | Auto-refresh: 5s"
            stdscr.addstr(footer_row + 1, (width - len(controls)) // 2, controls)
            
            stdscr.refresh()
            
            # Handle input
            key = stdscr.getch()
            if key == ord('q'):
                break
            elif key == ord('r'):
                continue  # Force refresh
            
            # Auto-refresh
            time.sleep(self.refresh_interval)
    
    def run(self):
        """Run the live monitor"""
        try:
            curses.wrapper(self.display)
        except KeyboardInterrupt:
            pass
        except Exception as e:
            print(f"Error: {e}")

def simple_status():
    """Simple status check without curses"""
    print("🤖 CLAUDE INVESTIGATION STATUS")
    print("=" * 70)
    print(f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Check processes
    result = subprocess.run(['ps', 'aux'], capture_output=True, text=True)
    lines = result.stdout.split('\n')
    claude_procs = [line for line in lines if 'claude' in line.lower() and 'grep' not in line]
    
    if claude_procs:
        print(f"✅ Found {len(claude_procs)} Claude process(es):")
        for proc in claude_procs:
            parts = proc.split(None, 10)
            if len(parts) > 10:
                print(f"  PID {parts[1]}: CPU {parts[2]}%, MEM {parts[3]}%")
                print(f"    Command: {parts[10][:60]}...")
    else:
        print("❌ No active Claude processes")
    
    print()
    
    # Recent logs
    print("📜 Recent Investigation Activity:")
    result = subprocess.run(
        ['grep', '-i', 'investigation\\|claude', 'dlq_monitor_FABIO-PROD_sa-east-1.log'],
        capture_output=True, text=True
    )
    
    if result.returncode == 0:
        log_lines = result.stdout.strip().split('\n')[-5:]
        for line in log_lines:
            if line:
                print(f"  • {line[:100]}...")
    else:
        print("  No recent activity")
    
    print()
    print("=" * 70)

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == '--simple':
        simple_status()
    else:
        print("Starting live monitor... (Press Ctrl+C to exit)")
        print("For simple output, use: python claude_live_monitor.py --simple")
        time.sleep(2)
        monitor = LiveClaudeMonitor()
        monitor.run()
