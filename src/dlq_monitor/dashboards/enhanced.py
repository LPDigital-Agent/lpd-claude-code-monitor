#!/usr/bin/env python3
"""
Enhanced DLQ & Claude Investigation Live Monitor
Real-time dashboard showing DLQs, PRs, Claude agents, and investigation status
"""
import subprocess
import time
import os
import sys
import json
import requests
import threading
from datetime import datetime, timedelta
from collections import defaultdict
import curses
from pathlib import Path
import re

class EnhancedLiveMonitor:
    """Enhanced live monitoring with DLQ, PR, and Agent tracking"""
    
    def __init__(self):
        self.session_file = ".claude_sessions.json"
        self.log_file = "dlq_monitor_FABIO-PROD_sa-east-1.log"
        self.refresh_interval = 3  # seconds
        
        # GitHub configuration
        self.github_token = os.getenv('GITHUB_TOKEN', '')
        self.github_username = os.getenv('GITHUB_USERNAME', 'fabio-lpd')
        self.github_org = 'LPDigital-Agent'
        
        # Track investigation start times
        self.investigation_start_times = {}
        self.active_agents = {}
        self.dlq_status = {}
        self.open_prs = []
        
        # Colors for different statuses
        self.status_colors = {
            'running': 1,  # Green
            'error': 2,     # Red
            'warning': 3,   # Yellow
            'info': 4,      # Cyan
            'special': 5,   # Magenta
            'dim': 6,       # White/dim
        }
        
    def get_github_prs(self):
        """Get open PRs related to DLQ investigations"""
        if not self.github_token:
            return []
        
        prs = []
        try:
            # Search for PRs with DLQ-related titles
            headers = {'Authorization': f'token {self.github_token}'}
            
            # Get user's repos
            url = f'https://api.github.com/user/repos'
            response = requests.get(url, headers=headers, timeout=5)
            
            if response.status_code == 200:
                repos = response.json()
                
                for repo in repos[:10]:  # Check first 10 repos
                    pr_url = f"https://api.github.com/repos/{repo['full_name']}/pulls?state=open"
                    pr_response = requests.get(pr_url, headers=headers, timeout=5)
                    
                    if pr_response.status_code == 200:
                        for pr in pr_response.json():
                            # Check if PR is DLQ-related
                            if any(keyword in pr['title'].lower() for keyword in 
                                   ['dlq', 'dead letter', 'investigation', 'auto-fix', 'automated']):
                                prs.append({
                                    'number': pr['number'],
                                    'title': pr['title'][:50],
                                    'repo': repo['name'],
                                    'created': pr['created_at'],
                                    'url': pr['html_url'],
                                    'author': pr['user']['login']
                                })
        except Exception as e:
            pass
        
        return prs
    
    def get_dlq_messages(self):
        """Get current DLQ message counts"""
        dlqs = {}
        try:
            # Parse recent logs for DLQ status
            result = subprocess.run(
                ['grep', '-E', 'ALERT|messages in DLQ|Checking DLQ', self.log_file],
                capture_output=True, text=True
            )
            
            if result.returncode == 0:
                lines = result.stdout.strip().split('\n')[-20:]  # Last 20 lines
                
                for line in lines:
                    # Extract DLQ name and message count
                    if 'messages in DLQ' in line:
                        match = re.search(r'(\d+) messages in DLQ: ([\w-]+)', line)
                        if match:
                            count = int(match.group(1))
                            dlq_name = match.group(2)
                            dlqs[dlq_name] = count
                    elif 'ALERT' in line and 'Queue:' in line:
                        match = re.search(r'Queue: ([\w-]+).*?(\d+) messages', line)
                        if match:
                            dlq_name = match.group(1)
                            count = int(match.group(2))
                            dlqs[dlq_name] = count
        except:
            pass
        
        return dlqs
    
    def get_claude_agents(self):
        """Get status of Claude agents/processes"""
        agents = []
        try:
            # Get Claude processes
            result = subprocess.run(['ps', 'aux'], capture_output=True, text=True)
            lines = result.stdout.split('\n')
            
            for line in lines:
                if 'claude' in line.lower() and 'grep' not in line:
                    parts = line.split(None, 10)
                    if len(parts) > 10:
                        # Extract agent type from command
                        cmd = parts[10]
                        agent_type = 'Unknown'
                        
                        if 'investigation' in cmd.lower():
                            agent_type = 'Investigation'
                        elif 'fix' in cmd.lower():
                            agent_type = 'Fix Agent'
                        elif 'analyze' in cmd.lower():
                            agent_type = 'Analyzer'
                        elif 'test' in cmd.lower():
                            agent_type = 'Test Runner'
                        
                        agents.append({
                            'pid': parts[1],
                            'cpu': float(parts[2]),
                            'mem': float(parts[3]),
                            'runtime': parts[9],
                            'type': agent_type,
                            'status': 'Running'
                        })
        except:
            pass
        
        return agents
    
    def parse_investigation_logs(self, lines=30):
        """Parse investigation logs with timing info"""
        events = []
        try:
            result = subprocess.run(
                ['tail', '-n', str(lines), self.log_file],
                capture_output=True, text=True
            )
            
            if result.returncode == 0:
                log_lines = result.stdout.strip().split('\n')
                
                for line in log_lines:
                    if any(keyword in line.lower() for keyword in 
                           ['investigation', 'claude', 'dlq', 'alert', 'pr created']):
                        
                        # Extract timestamp and message
                        parts = line.split(' - ', 3)
                        if len(parts) >= 4:
                            timestamp_str = parts[0]
                            message = parts[-1]
                            
                            # Parse actual time
                            try:
                                event_time = datetime.strptime(timestamp_str, "%Y-%m-%d %H:%M:%S,%f")
                            except:
                                event_time = datetime.now()
                            
                            # Determine event type and icon
                            event_type = 'info'
                            icon = "•"
                            
                            if 'starting' in message.lower():
                                event_type = 'start'
                                icon = "🚀"
                                # Track investigation start
                                if 'investigation for' in message.lower():
                                    dlq_match = re.search(r'for ([\w-]+)', message)
                                    if dlq_match:
                                        dlq_name = dlq_match.group(1)
                                        self.investigation_start_times[dlq_name] = event_time
                            elif 'completed successfully' in message.lower():
                                event_type = 'success'
                                icon = "✅"
                            elif 'failed' in message.lower():
                                event_type = 'error'
                                icon = "❌"
                            elif 'timeout' in message.lower():
                                event_type = 'timeout'
                                icon = "⏰"
                            elif 'pr created' in message.lower():
                                event_type = 'pr'
                                icon = "🔧"
                            elif 'alert' in message.lower():
                                event_type = 'alert'
                                icon = "🚨"
                            elif 'analyzing' in message.lower():
                                icon = "🔍"
                            elif 'fixing' in message.lower():
                                icon = "🔨"
                            
                            # Calculate duration if this is a completion
                            duration = None
                            if 'completed' in message.lower() and 'investigation for' in message.lower():
                                dlq_match = re.search(r'for ([\w-]+)', message)
                                if dlq_match:
                                    dlq_name = dlq_match.group(1)
                                    if dlq_name in self.investigation_start_times:
                                        duration = event_time - self.investigation_start_times[dlq_name]
                            
                            events.append({
                                'time': event_time,
                                'type': event_type,
                                'message': message[:80],
                                'icon': icon,
                                'duration': duration
                            })
        except Exception as e:
            pass
        
        return events
    
    def format_duration(self, td):
        """Format timedelta to MM:SS"""
        if not td:
            return ""
        total_seconds = int(td.total_seconds())
        minutes = total_seconds // 60
        seconds = total_seconds % 60
        return f"{minutes:02d}:{seconds:02d}"
    
    def display(self, stdscr):
        """Enhanced display with multiple panels"""
        curses.curs_set(0)  # Hide cursor
        stdscr.nodelay(1)    # Non-blocking input
        stdscr.timeout(100)  # Refresh timeout
        
        # Initialize color pairs
        curses.init_pair(1, curses.COLOR_GREEN, curses.COLOR_BLACK)
        curses.init_pair(2, curses.COLOR_RED, curses.COLOR_BLACK)
        curses.init_pair(3, curses.COLOR_YELLOW, curses.COLOR_BLACK)
        curses.init_pair(4, curses.COLOR_CYAN, curses.COLOR_BLACK)
        curses.init_pair(5, curses.COLOR_MAGENTA, curses.COLOR_BLACK)
        curses.init_pair(6, curses.COLOR_WHITE, curses.COLOR_BLACK)
        
        while True:
            stdscr.clear()
            height, width = stdscr.getmaxyx()
            
            # Header
            header = "🚀 ENHANCED DLQ INVESTIGATION DASHBOARD 🚀"
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            stdscr.addstr(0, (width - len(header)) // 2, header, curses.A_BOLD | curses.color_pair(5))
            stdscr.addstr(1, (width - len(timestamp)) // 2, timestamp, curses.color_pair(6))
            stdscr.addstr(2, 0, "=" * width, curses.color_pair(4))
            
            row = 4
            
            # Split screen into panels
            panel_width = width // 2
            
            # LEFT PANEL - DLQ Status
            stdscr.addstr(row, 0, "🚨 DLQ STATUS", curses.A_BOLD | curses.color_pair(2))
            stdscr.addstr(row, panel_width, "🤖 CLAUDE AGENTS", curses.A_BOLD | curses.color_pair(4))
            row += 1
            stdscr.addstr(row, 0, "-" * (panel_width - 1))
            stdscr.addstr(row, panel_width, "-" * (panel_width - 1))
            row += 1
            
            # Get current data
            dlqs = self.get_dlq_messages()
            agents = self.get_claude_agents()
            
            # Display DLQs
            start_row = row
            if dlqs:
                for dlq_name, count in list(dlqs.items())[:5]:
                    if count > 0:
                        color = curses.color_pair(2) if count > 10 else curses.color_pair(3)
                        icon = "🔴" if count > 10 else "🟡"
                        dlq_display = f"{icon} {dlq_name[:30]}: {count} msgs"
                        stdscr.addstr(row, 0, dlq_display[:panel_width-2], color)
                        row += 1
            else:
                stdscr.addstr(row, 0, "✅ No DLQ alerts", curses.color_pair(1))
                row += 1
            
            # Display Agents (right side)
            row = start_row
            if agents:
                for agent in agents[:5]:
                    agent_line = f"🤖 {agent['type']}: PID {agent['pid']}"
                    stdscr.addstr(row, panel_width, agent_line[:panel_width-2], curses.color_pair(1))
                    row += 1
                    stats_line = f"   CPU: {agent['cpu']}% MEM: {agent['mem']}% Time: {agent['runtime']}"
                    stdscr.addstr(row, panel_width, stats_line[:panel_width-2], curses.color_pair(6))
                    row += 1
            else:
                stdscr.addstr(row, panel_width, "💤 No active agents", curses.color_pair(6))
                row += 1
            
            # Align rows
            row = max(row, start_row + 6) + 2
            
            # PULL REQUESTS Panel
            stdscr.addstr(row, 0, "🔧 OPEN PULL REQUESTS", curses.A_BOLD | curses.color_pair(3))
            row += 1
            stdscr.addstr(row, 0, "-" * width)
            row += 1
            
            prs = self.get_github_prs()
            if prs:
                for pr in prs[:3]:
                    pr_line = f"  PR #{pr['number']} in {pr['repo']}: {pr['title']}"
                    stdscr.addstr(row, 0, pr_line[:width-2], curses.color_pair(3))
                    row += 1
            else:
                stdscr.addstr(row, 0, "  ✅ No open DLQ-related PRs", curses.color_pair(1))
                row += 1
            
            row += 2
            
            # INVESTIGATION TIMELINE
            stdscr.addstr(row, 0, "📜 INVESTIGATION TIMELINE", curses.A_BOLD | curses.color_pair(5))
            row += 1
            stdscr.addstr(row, 0, "-" * width)
            row += 1
            
            # Column headers
            headers = "Time         Duration  Event"
            stdscr.addstr(row, 0, headers, curses.A_BOLD | curses.color_pair(6))
            row += 1
            
            events = self.parse_investigation_logs(50)
            if events:
                # Show last 10 events
                for event in events[-10:]:
                    if row < height - 4:
                        # Format time
                        time_str = event['time'].strftime("%H:%M:%S")
                        
                        # Format duration
                        duration_str = self.format_duration(event['duration']) if event['duration'] else "      "
                        
                        # Choose color
                        color = curses.color_pair(1)  # Default green
                        if event['type'] == 'error':
                            color = curses.color_pair(2)
                        elif event['type'] == 'warning' or event['type'] == 'timeout':
                            color = curses.color_pair(3)
                        elif event['type'] == 'start':
                            color = curses.color_pair(4)
                        elif event['type'] == 'pr':
                            color = curses.color_pair(5)
                        
                        # Build event line
                        event_line = f"{time_str}  {duration_str}  {event['icon']} {event['message']}"
                        stdscr.addstr(row, 0, event_line[:width-2], color)
                        row += 1
            else:
                stdscr.addstr(row, 0, "  No recent events", curses.color_pair(6))
                row += 1
            
            # Footer with stats
            footer_row = height - 3
            stdscr.addstr(footer_row, 0, "=" * width, curses.color_pair(4))
            
            # Calculate stats
            active_investigations = len([a for a in agents if a['type'] == 'Investigation'])
            total_dlq_messages = sum(dlqs.values()) if dlqs else 0
            
            stats_line = f"📊 Active: {active_investigations} agents | DLQs: {len(dlqs)} queues | Messages: {total_dlq_messages} | PRs: {len(prs)}"
            stdscr.addstr(footer_row + 1, 2, stats_line, curses.color_pair(6))
            
            controls = "Press 'q' to quit | 'r' to refresh | Auto-refresh: 3s"
            stdscr.addstr(footer_row + 2, (width - len(controls)) // 2, controls, curses.color_pair(6))
            
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
        """Run the enhanced monitor"""
        try:
            # Check for GitHub token
            if not self.github_token:
                print("⚠️  GitHub token not set - PR tracking will be limited")
                print("💡 Set GITHUB_TOKEN environment variable for full features")
                time.sleep(2)
            
            curses.wrapper(self.display)
        except KeyboardInterrupt:
            pass
        except Exception as e:
            print(f"Error: {e}")
            import traceback
            traceback.print_exc()

def main():
    """Main entry point"""
    print("🚀 Starting Enhanced DLQ Investigation Dashboard...")
    print("📊 Features: DLQ Status | Claude Agents | PR Tracking | Investigation Timeline")
    print("⏳ Loading...")
    time.sleep(2)
    
    monitor = EnhancedLiveMonitor()
    monitor.run()

if __name__ == "__main__":
    main()
