#!/usr/bin/env python3
"""
Fixed Enhanced DLQ & Claude Investigation Live Monitor
Properly detects all Claude agents and shows real DLQ data
"""
import subprocess
import time
import os
import sys
import json
import requests
import threading
import boto3
from datetime import datetime, timedelta
from collections import defaultdict
import curses
from pathlib import Path
import re

class FixedEnhancedMonitor:
    """Fixed version that properly shows Claude agents and DLQ status"""
    
    def __init__(self):
        self.session_file = ".claude_sessions.json"
        self.log_file = "dlq_monitor_FABIO-PROD_sa-east-1.log"
        self.refresh_interval = 3
        
        # AWS configuration
        self.aws_profile = 'FABIO-PROD'
        self.aws_region = 'sa-east-1'
        
        # GitHub configuration
        self.github_token = os.getenv('GITHUB_TOKEN', '')
        self.github_username = os.getenv('GITHUB_USERNAME', 'fabio-lpd')
        self.github_org = 'LPDigital-Agent'
        
        # Initialize AWS SQS client
        try:
            session = boto3.Session(profile_name=self.aws_profile, region_name=self.aws_region)
            self.sqs = session.client('sqs')
        except:
            self.sqs = None
        
        # Track investigation data
        self.investigation_start_times = {}
        self.dlq_messages = {}
        
    def get_real_dlq_status(self):
        """Get actual DLQ status from AWS"""
        dlqs = {}
        
        if not self.sqs:
            return dlqs
        
        try:
            # List all queues
            response = self.sqs.list_queues()
            
            for queue_url in response.get('QueueUrls', []):
                # Check if it's a DLQ
                if 'dlq' in queue_url.lower():
                    queue_name = queue_url.split('/')[-1]
                    
                    # Get message count
                    try:
                        attrs = self.sqs.get_queue_attributes(
                            QueueUrl=queue_url,
                            AttributeNames=['ApproximateNumberOfMessages']
                        )
                        count = int(attrs['Attributes']['ApproximateNumberOfMessages'])
                        
                        if count > 0:
                            dlqs[queue_name] = {
                                'count': count,
                                'url': queue_url
                            }
                    except:
                        pass
        except Exception as e:
            pass
        
        return dlqs
    
    def get_all_claude_agents(self):
        """Properly detect ALL Claude processes"""
        agents = []
        
        try:
            # Use ps with better filtering
            result = subprocess.run(
                ['ps', 'aux'],
                capture_output=True,
                text=True
            )
            
            for line in result.stdout.split('\n'):
                # Look for claude but exclude grep and monitor processes
                if 'claude' in line.lower():
                    if 'grep' in line or 'monitor' in line.lower():
                        continue
                    
                    parts = line.split(None, 10)
                    if len(parts) > 10:
                        pid = parts[1]
                        cpu = float(parts[2])
                        mem = float(parts[3])
                        start_time = parts[8]
                        runtime = parts[9]
                        cmd = parts[10]
                        
                        # Determine agent type from command
                        agent_type = 'Investigation'
                        if 'fix' in cmd.lower():
                            agent_type = 'Fix Agent'
                        elif 'test' in cmd.lower():
                            agent_type = 'Test Runner'
                        elif 'analyze' in cmd.lower():
                            agent_type = 'Analyzer'
                        elif 'commit' in cmd.lower():
                            agent_type = 'Committer'
                        elif cpu > 5.0:
                            agent_type = 'Active Work'
                        elif cpu > 1.0:
                            agent_type = 'Processing'
                        else:
                            agent_type = 'Idle/Waiting'
                        
                        agents.append({
                            'pid': pid,
                            'cpu': cpu,
                            'mem': mem,
                            'runtime': runtime,
                            'type': agent_type,
                            'status': 'Active' if cpu > 0.5 else 'Idle',
                            'start': start_time
                        })
        except Exception as e:
            pass
        
        return agents
    
    def get_github_prs_detailed(self):
        """Get ALL open PRs from the organization"""
        prs = []
        
        if not self.github_token:
            return prs
        
        try:
            headers = {'Authorization': f'token {self.github_token}'}
            
            # Get organization repos
            org_url = f'https://api.github.com/orgs/{self.github_org}/repos'
            response = requests.get(org_url, headers=headers, timeout=5)
            
            if response.status_code == 200:
                repos = response.json()
                
                for repo in repos[:10]:  # Check first 10 repos
                    # Get PRs for each repo
                    pr_url = f"https://api.github.com/repos/{repo['full_name']}/pulls?state=open"
                    pr_response = requests.get(pr_url, headers=headers, timeout=5)
                    
                    if pr_response.status_code == 200:
                        for pr in pr_response.json():
                            prs.append({
                                'number': pr['number'],
                                'title': pr['title'][:50],
                                'repo': repo['name'],
                                'author': pr['user']['login'],
                                'created': pr['created_at'],
                                'url': pr['html_url']
                            })
        except:
            pass
        
        return prs
    
    def parse_investigation_events(self, lines=50):
        """Parse investigation events from logs"""
        events = []
        
        try:
            result = subprocess.run(
                ['tail', '-n', str(lines), self.log_file],
                capture_output=True,
                text=True
            )
            
            for line in result.stdout.split('\n'):
                # Parse events
                if any(keyword in line.lower() for keyword in 
                       ['investigation', 'claude', 'executing', 'completed', 'failed', 
                        'analyzing', 'fixing', 'creating pr', 'committing']):
                    
                    # Extract timestamp
                    parts = line.split(' - ', 3)
                    if len(parts) >= 4:
                        timestamp_str = parts[0]
                        message = parts[-1]
                        
                        try:
                            event_time = datetime.strptime(timestamp_str, "%Y-%m-%d %H:%M:%S,%f")
                        except:
                            event_time = datetime.now()
                        
                        # Determine event type
                        event_type = 'info'
                        icon = "•"
                        
                        if 'starting' in message.lower():
                            event_type = 'start'
                            icon = "🚀"
                            # Track start time
                            dlq_match = re.search(r'for ([\w-]+)', message)
                            if dlq_match:
                                dlq_name = dlq_match.group(1)
                                self.investigation_start_times[dlq_name] = event_time
                        elif 'completed' in message.lower():
                            event_type = 'success'
                            icon = "✅"
                        elif 'failed' in message.lower():
                            event_type = 'error'
                            icon = "❌"
                        elif 'analyzing' in message.lower():
                            icon = "🔍"
                        elif 'fixing' in message.lower():
                            icon = "🔨"
                        elif 'pr created' in message.lower():
                            icon = "🔧"
                            event_type = 'pr'
                        
                        # Calculate duration if completion
                        duration = None
                        if 'completed' in message.lower():
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
        except:
            pass
        
        return events
    
    def format_duration(self, td):
        """Format timedelta"""
        if not td:
            return ""
        total_seconds = int(td.total_seconds())
        minutes = total_seconds // 60
        seconds = total_seconds % 60
        return f"{minutes:02d}:{seconds:02d}"
    
    def display(self, stdscr):
        """Fixed display with proper data"""
        curses.curs_set(0)
        stdscr.nodelay(1)
        stdscr.timeout(100)
        
        # Initialize colors
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
            header = "🚀 FIXED ENHANCED DLQ & CLAUDE MONITOR 🚀"
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            stdscr.addstr(0, (width - len(header)) // 2, header, curses.A_BOLD | curses.color_pair(5))
            stdscr.addstr(1, (width - len(timestamp)) // 2, timestamp, curses.color_pair(6))
            stdscr.addstr(2, 0, "=" * width, curses.color_pair(4))
            
            row = 4
            
            # Get current data
            dlqs = self.get_real_dlq_status()
            agents = self.get_all_claude_agents()
            prs = self.get_github_prs_detailed()
            events = self.parse_investigation_events(100)
            
            # Split screen
            panel_width = width // 2
            
            # DLQ STATUS (Left)
            stdscr.addstr(row, 0, f"🚨 DLQ STATUS ({len(dlqs)} with messages)", curses.A_BOLD | curses.color_pair(2))
            # CLAUDE AGENTS (Right)
            stdscr.addstr(row, panel_width, f"🤖 CLAUDE AGENTS ({len(agents)} running)", curses.A_BOLD | curses.color_pair(4))
            row += 1
            stdscr.addstr(row, 0, "-" * (panel_width - 1))
            stdscr.addstr(row, panel_width, "-" * (panel_width - 1))
            row += 1
            
            # Display DLQs
            start_row = row
            if dlqs:
                for dlq_name, info in list(dlqs.items())[:6]:
                    color = curses.color_pair(2) if info['count'] > 10 else curses.color_pair(3)
                    icon = "🔴" if info['count'] > 10 else "🟡"
                    dlq_line = f"{icon} {dlq_name[:25]}: {info['count']} msgs"
                    stdscr.addstr(row, 0, dlq_line[:panel_width-2], color)
                    row += 1
            else:
                stdscr.addstr(row, 0, "✅ No DLQ messages", curses.color_pair(1))
                row += 1
            
            # Display Agents
            row = start_row
            if agents:
                # Show summary
                active_agents = [a for a in agents if a['status'] == 'Active']
                if active_agents:
                    stdscr.addstr(row, panel_width, f"Active: {len(active_agents)}", curses.color_pair(1))
                    row += 1
                
                # Show top agents by CPU
                for agent in sorted(agents, key=lambda x: x['cpu'], reverse=True)[:5]:
                    color = curses.color_pair(1) if agent['status'] == 'Active' else curses.color_pair(6)
                    agent_line = f"PID {agent['pid']}: {agent['type']}"
                    stdscr.addstr(row, panel_width, agent_line[:panel_width-2], color)
                    row += 1
                    stats = f"  CPU:{agent['cpu']:.1f}% MEM:{agent['mem']:.1f}% Time:{agent['runtime']}"
                    stdscr.addstr(row, panel_width, stats[:panel_width-2], curses.color_pair(6))
                    row += 1
            else:
                stdscr.addstr(row, panel_width, "No agents detected", curses.color_pair(3))
                row += 1
            
            row = max(row, start_row + 7) + 2
            
            # PULL REQUESTS
            stdscr.addstr(row, 0, f"🔧 OPEN PULL REQUESTS ({len(prs)} total)", curses.A_BOLD | curses.color_pair(3))
            row += 1
            stdscr.addstr(row, 0, "-" * width)
            row += 1
            
            if prs:
                for pr in prs[:3]:
                    pr_line = f"  PR #{pr['number']} in {pr['repo']}: {pr['title']} (by {pr['author']})"
                    stdscr.addstr(row, 0, pr_line[:width-2], curses.color_pair(3))
                    row += 1
            else:
                stdscr.addstr(row, 0, "  No open PRs found", curses.color_pair(6))
                row += 1
            
            row += 2
            
            # INVESTIGATION TIMELINE
            stdscr.addstr(row, 0, "📜 INVESTIGATION TIMELINE", curses.A_BOLD | curses.color_pair(5))
            row += 1
            stdscr.addstr(row, 0, "-" * width)
            row += 1
            
            headers = "Time         Duration  Event"
            stdscr.addstr(row, 0, headers, curses.A_BOLD | curses.color_pair(6))
            row += 1
            
            if events:
                for event in events[-10:]:
                    if row < height - 4:
                        time_str = event['time'].strftime("%H:%M:%S")
                        duration_str = self.format_duration(event['duration']) if event['duration'] else "      "
                        
                        color = curses.color_pair(1)
                        if event['type'] == 'error':
                            color = curses.color_pair(2)
                        elif event['type'] == 'start':
                            color = curses.color_pair(4)
                        elif event['type'] == 'pr':
                            color = curses.color_pair(5)
                        
                        event_line = f"{time_str}  {duration_str}  {event['icon']} {event['message']}"
                        stdscr.addstr(row, 0, event_line[:width-2], color)
                        row += 1
            
            # Footer
            footer_row = height - 3
            stdscr.addstr(footer_row, 0, "=" * width, curses.color_pair(4))
            
            total_messages = sum(d['count'] for d in dlqs.values())
            active_agents = sum(1 for a in agents if a['status'] == 'Active')
            
            stats = f"📊 DLQs: {len(dlqs)} | Messages: {total_messages} | Agents: {len(agents)} ({active_agents} active) | PRs: {len(prs)}"
            stdscr.addstr(footer_row + 1, 2, stats, curses.color_pair(6))
            
            controls = "Press 'q' to quit | 'r' to refresh | Auto-refresh: 3s"
            stdscr.addstr(footer_row + 2, (width - len(controls)) // 2, controls, curses.color_pair(6))
            
            stdscr.refresh()
            
            # Handle input
            key = stdscr.getch()
            if key == ord('q'):
                break
            elif key == ord('r'):
                continue
            
            time.sleep(self.refresh_interval)
    
    def run(self):
        """Run the fixed monitor"""
        try:
            if not self.sqs:
                print("⚠️  AWS SQS not configured - DLQ data will be limited")
                print("💡 Ensure AWS credentials are configured")
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
    print("🚀 Starting Fixed Enhanced Monitor...")
    print("📊 This version properly shows all Claude agents and real DLQ data")
    print("⏳ Loading...")
    time.sleep(2)
    
    monitor = FixedEnhancedMonitor()
    monitor.run()

if __name__ == "__main__":
    main()
