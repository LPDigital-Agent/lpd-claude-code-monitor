#!/usr/bin/env python3
"""
Enhanced Claude Investigation Monitor with Better Colors
Optimized for dark terminal visibility
"""
import curses
import time
import subprocess
import os
from datetime import datetime
from pathlib import Path

class InvestigationMonitor:
    def __init__(self):
        self.log_file = "dlq_monitor_FABIO-PROD_sa-east-1.log"
        
    def setup_colors(self, stdscr):
        """Setup color pairs optimized for dark terminals"""
        curses.start_color()
        curses.use_default_colors()
        
        # Define color pairs with better visibility
        # Avoid pure red on dark background - use bright red or magenta
        curses.init_pair(1, curses.COLOR_GREEN, -1)      # Success - Green
        curses.init_pair(2, curses.COLOR_MAGENTA, -1)    # Errors - Magenta (instead of red)
        curses.init_pair(3, curses.COLOR_YELLOW, -1)     # Warnings - Yellow
        curses.init_pair(4, curses.COLOR_CYAN, -1)       # Info - Cyan
        curses.init_pair(5, curses.COLOR_WHITE, -1)      # Headers - White
        curses.init_pair(6, 9, -1)                       # Bright Red (if terminal supports)
        curses.init_pair(7, curses.COLOR_BLUE, -1)       # Blue for secondary info
        
        # Return color map for easy reference
        return {
            'success': curses.color_pair(1) | curses.A_BOLD,
            'error': curses.color_pair(2) | curses.A_BOLD,    # Magenta instead of red
            'warning': curses.color_pair(3) | curses.A_BOLD,
            'info': curses.color_pair(4),
            'header': curses.color_pair(5) | curses.A_BOLD,
            'bright_error': curses.color_pair(6) | curses.A_BOLD,  # Bright red if available
            'secondary': curses.color_pair(7),
            'normal': curses.A_NORMAL
        }
    
    def get_investigation_status(self):
        """Get current investigation status"""
        status = {
            'processes': [],
            'issues': [],
            'corrections': "No corrections yet",
            'files_changed': "No files changed"
        }
        
        # Check for Claude processes
        try:
            result = subprocess.run(['ps', 'aux'], capture_output=True, text=True)
            for line in result.stdout.split('\n'):
                if 'claude' in line.lower() and 'grep' not in line:
                    parts = line.split(None, 10)
                    if len(parts) > 10:
                        status['processes'].append({
                            'pid': parts[1],
                            'cpu': float(parts[2]),
                            'mem': float(parts[3]),
                            'cmd': parts[10][:50]
                        })
        except:
            pass
        
        # Parse recent logs for issues
        try:
            result = subprocess.run(
                ['tail', '-50', self.log_file],
                capture_output=True,
                text=True
            )
            for line in result.stdout.split('\n'):
                if 'failed' in line.lower() or 'error' in line.lower():
                    status['issues'].append(line[-80:])
                elif 'correction' in line.lower() or 'fix' in line.lower():
                    status['corrections'] = line[-80:]
        except:
            pass
        
        return status
    
    def display(self, stdscr):
        """Main display with better colors"""
        colors = self.setup_colors(stdscr)
        stdscr.nodelay(1)
        stdscr.timeout(1000)
        
        while True:
            try:
                stdscr.clear()
                height, width = stdscr.getmaxyx()
                
                # Header
                header = "🤖 CLAUDE INVESTIGATION MONITOR"
                timestamp = datetime.now().strftime("%H:%M:%S")
                stdscr.addstr(0, (width - len(header)) // 2, header, colors['header'])
                stdscr.addstr(1, (width - len(timestamp)) // 2, timestamp, colors['secondary'])
                
                # Get status
                status = self.get_investigation_status()
                
                row = 3
                
                # Process status
                stdscr.addstr(row, 0, "📊 INVESTIGATION STATUS", colors['header'])
                row += 1
                stdscr.addstr(row, 0, "─" * min(width, 80), colors['normal'])
                row += 2
                
                if status['processes']:
                    for proc in status['processes']:
                        # Use color based on CPU usage
                        if proc['cpu'] > 50:
                            color = colors['warning']
                        elif proc['cpu'] > 80:
                            color = colors['error']  # This will be magenta
                        else:
                            color = colors['success']
                        
                        proc_line = f"PID {proc['pid']}  CPU: {proc['cpu']:5.1f}%  MEM: {proc['mem']:5.1f}%"
                        stdscr.addstr(row, 2, "●", color)
                        stdscr.addstr(row, 4, proc_line, colors['info'])
                        row += 1
                        
                        stdscr.addstr(row, 4, f"└─ Thinking", colors['secondary'])
                        for i in range(3):
                            if int(time.time()) % 3 == i:
                                stdscr.addstr(row, 15 + i*2, "●", colors['info'])
                            else:
                                stdscr.addstr(row, 15 + i*2, "○", colors['secondary'])
                        
                        stdscr.addstr(row, 23, "Processing task...", colors['secondary'])
                        row += 2
                else:
                    stdscr.addstr(row, 2, "⚠", colors['warning'])
                    stdscr.addstr(row, 4, "No active Claude processes", colors['warning'])
                    row += 2
                
                # Issues section - using better colors
                row += 1
                if status['issues']:
                    # Use magenta/warning instead of red for better visibility
                    stdscr.addstr(row, 0, "⚠ ISSUES FOUND", colors['error'])  # This is magenta
                    row += 1
                    stdscr.addstr(row, 0, "─" * min(width, 80), colors['normal'])
                    row += 1
                    
                    for issue in status['issues'][:3]:
                        stdscr.addstr(row, 2, "!", colors['warning'])
                        # Truncate and display issue
                        issue_text = issue[:width-5] if len(issue) > width-5 else issue
                        stdscr.addstr(row, 4, issue_text, colors['warning'])
                        row += 1
                else:
                    stdscr.addstr(row, 0, "✓ CORRECTIONS", colors['success'])
                    row += 1
                    stdscr.addstr(row, 0, "─" * min(width, 80), colors['normal'])
                    row += 1
                    stdscr.addstr(row, 2, status['corrections'], colors['info'])
                    row += 1
                
                row += 2
                
                # Files changed section
                stdscr.addstr(row, 0, "📁 FILES CHANGED", colors['header'])
                row += 1
                stdscr.addstr(row, 0, "─" * min(width, 80), colors['normal'])
                row += 1
                stdscr.addstr(row, 2, status['files_changed'], colors['secondary'])
                row += 2
                
                # Progress bar
                row = height - 4
                stdscr.addstr(row, 0, "─" * min(width, 80), colors['normal'])
                row += 1
                stdscr.addstr(row, 0, "⚙ OVERALL INVESTIGATION PROGRESS", colors['header'])
                row += 1
                
                # Animated progress bar
                progress_width = min(width - 4, 76)
                progress = int((time.time() % 10) / 10 * progress_width)
                stdscr.addstr(row, 2, "[", colors['normal'])
                stdscr.addstr(row, 3, "=" * progress, colors['success'])
                stdscr.addstr(row, 3 + progress, ">", colors['info'])
                stdscr.addstr(row, 3 + progress_width, "]", colors['normal'])
                
                # Status line with better colors
                row += 1
                activity_text = "🔍 GITHUB ACTIVITY"
                stdscr.addstr(row, width - len(activity_text) - 20, activity_text, colors['info'])
                
                stdscr.refresh()
                
                # Check for quit
                key = stdscr.getch()
                if key == ord('q'):
                    break
                elif key == ord('r'):
                    continue
                    
            except KeyboardInterrupt:
                break
            except curses.error:
                # Handle resize or other curses errors
                pass
    
    def run(self):
        """Run the monitor"""
        try:
            curses.wrapper(self.display)
        except KeyboardInterrupt:
            print("\n✅ Monitor stopped")
        except Exception as e:
            print(f"Error: {e}")

def main():
    print("Starting Enhanced Claude Investigation Monitor...")
    print("Colors optimized for dark terminals")
    print("Press 'q' to quit, 'r' to refresh")
    time.sleep(2)
    
    monitor = InvestigationMonitor()
    monitor.run()

if __name__ == "__main__":
    main()
