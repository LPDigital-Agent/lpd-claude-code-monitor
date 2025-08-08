#!/usr/bin/env python3
"""
🚀 ULTIMATE CLAUDE AI LIVE MONITOR - THE TOP TOP VERSION 🚀
Everything you need in one incredible dashboard!
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
from collections import defaultdict, deque
import curses
from pathlib import Path
import re
import psutil

class UltimateClaudeMonitor:
    """The TOP TOP monitor with everything you need!"""
    
    def __init__(self):
        self.log_file = "dlq_monitor_FABIO-PROD_sa-east-1.log"
        self.session_file = ".claude_sessions.json"
        self.refresh_interval = 1  # Super fast refresh!
        
        # AWS configuration
        self.aws_profile = 'FABIO-PROD'
        self.aws_region = 'sa-east-1'
        
        # GitHub configuration
        self.github_token = os.getenv('GITHUB_TOKEN', '')
        self.github_username = os.getenv('GITHUB_USERNAME', 'fabio-lpd')
        self.github_org = 'LPDigital-Agent'
        
        # Initialize AWS
        try:
            session = boto3.Session(profile_name=self.aws_profile, region_name=self.aws_region)
            self.sqs = session.client('sqs')
        except:
            self.sqs = None
        
        # Data tracking
        self.investigation_start_times = {}
        self.claude_activities = deque(maxlen=100)
        self.corrections_made = deque(maxlen=50)
        self.issues_found = deque(maxlen=50)
        self.files_changed = deque(maxlen=30)
        self.tests_run = deque(maxlen=20)
        self.pr_activities = []
        self.agent_history = defaultdict(list)
        
        # Performance tracking
        self.total_cpu_usage = 0
        self.total_memory_usage = 0
        
    def get_complete_claude_info(self):
        """Get COMPLETE information about all Claude processes"""
        agents = {}
        total_cpu = 0
        total_mem = 0
        
        try:
            # Get all processes
            for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent', 'create_time', 'cmdline']):
                try:
                    pinfo = proc.info
                    cmdline = ' '.join(pinfo['cmdline']) if pinfo['cmdline'] else ''
                    
                    if 'claude' in cmdline.lower() and 'monitor' not in cmdline.lower():
                        pid = pinfo['pid']
                        
                        # Get detailed process info
                        proc_obj = psutil.Process(pid)
                        cpu = proc_obj.cpu_percent(interval=0.1)
                        mem = proc_obj.memory_percent()
                        
                        # Calculate runtime
                        create_time = datetime.fromtimestamp(pinfo['create_time'])
                        runtime = datetime.now() - create_time
                        runtime_str = str(runtime).split('.')[0]
                        
                        # Determine what the agent is doing
                        action = self._determine_agent_action(cmdline, cpu)
                        
                        # Extract the task/prompt if visible
                        task = self._extract_task(cmdline)
                        
                        # Determine status
                        if cpu > 10:
                            status = "🔥 Heavy Work"
                        elif cpu > 5:
                            status = "⚡ Active"
                        elif cpu > 1:
                            status = "🔄 Processing"
                        elif cpu > 0.1:
                            status = "💭 Thinking"
                        else:
                            status = "😴 Idle"
                        
                        agents[pid] = {
                            'pid': pid,
                            'cpu': cpu,
                            'mem': mem,
                            'runtime': runtime_str,
                            'action': action,
                            'task': task,
                            'status': status,
                            'create_time': create_time
                        }
                        
                        total_cpu += cpu
                        total_mem += mem
                        
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    pass
        except Exception as e:
            # Fallback to ps command
            result = subprocess.run(['ps', 'aux'], capture_output=True, text=True)
            for line in result.stdout.split('\n'):
                if 'claude' in line.lower() and 'monitor' not in line.lower():
                    parts = line.split(None, 10)
                    if len(parts) > 10:
                        pid = parts[1]
                        cpu = float(parts[2])
                        mem = float(parts[3])
                        runtime = parts[9]
                        cmd = parts[10]
                        
                        agents[pid] = {
                            'pid': pid,
                            'cpu': cpu,
                            'mem': mem,
                            'runtime': runtime,
                            'action': self._determine_agent_action(cmd, cpu),
                            'task': self._extract_task(cmd),
                            'status': "⚡ Active" if cpu > 1 else "😴 Idle",
                            'create_time': datetime.now()
                        }
                        
                        total_cpu += cpu
                        total_mem += mem
        
        self.total_cpu_usage = total_cpu
        self.total_memory_usage = total_mem
        
        return agents
    
    def _determine_agent_action(self, cmd, cpu):
        """Determine what the agent is doing based on command and CPU"""
        cmd_lower = cmd.lower()
        
        if 'investigate' in cmd_lower or 'investigation' in cmd_lower:
            return "🔍 Deep Investigation"
        elif 'fix' in cmd_lower or 'patch' in cmd_lower:
            return "🔨 Applying Fixes"
        elif 'test' in cmd_lower:
            return "🧪 Running Tests"
        elif 'analyze' in cmd_lower or 'analysis' in cmd_lower:
            return "📊 Code Analysis"
        elif 'commit' in cmd_lower or 'git' in cmd_lower:
            return "📝 Git Operations"
        elif 'pr' in cmd_lower or 'pull' in cmd_lower:
            return "🔧 PR Creation"
        elif 'build' in cmd_lower:
            return "🏗️ Building"
        elif 'deploy' in cmd_lower:
            return "🚀 Deploying"
        elif cpu > 10:
            return "🔥 Heavy Processing"
        elif cpu > 5:
            return "⚡ Active Work"
        elif cpu > 1:
            return "🔄 Processing"
        else:
            return "💭 Thinking"
    
    def _extract_task(self, cmd):
        """Extract the actual task from command"""
        # Try to find prompt
        prompt_match = re.search(r'-p\s+"([^"]+)"', cmd)
        if prompt_match:
            return prompt_match.group(1)[:60] + "..."
        
        # Try to find file being worked on
        file_match = re.search(r'([a-zA-Z0-9_-]+\.(py|js|yaml|json|md))', cmd)
        if file_match:
            return f"Working on {file_match.group(1)}"
        
        # Try to find DLQ name
        dlq_match = re.search(r'(fm-[a-zA-Z0-9-]+-dlq-[a-zA-Z0-9]+)', cmd)
        if dlq_match:
            return f"Fixing {dlq_match.group(1)}"
        
        return "Processing task..."
    
    def get_dlq_status(self):
        """Get real DLQ status from AWS"""
        dlqs = {}
        total_messages = 0
        
        if self.sqs:
            try:
                response = self.sqs.list_queues()
                for queue_url in response.get('QueueUrls', []):
                    if 'dlq' in queue_url.lower():
                        queue_name = queue_url.split('/')[-1]
                        try:
                            attrs = self.sqs.get_queue_attributes(
                                QueueUrl=queue_url,
                                AttributeNames=['ApproximateNumberOfMessages']
                            )
                            count = int(attrs['Attributes']['ApproximateNumberOfMessages'])
                            if count > 0:
                                dlqs[queue_name] = count
                                total_messages += count
                        except:
                            pass
            except:
                pass
        
        return dlqs, total_messages
    
    def parse_live_activities(self):
        """Parse live activities from logs"""
        activities = {
            'corrections': [],
            'issues': [],
            'files': [],
            'tests': [],
            'commits': []
        }
        
        try:
            result = subprocess.run(
                ['tail', '-n', '500', self.log_file],
                capture_output=True,
                text=True
            )
            
            for line in result.stdout.split('\n'):
                line_lower = line.lower()
                
                # Corrections/Fixes
                if any(word in line_lower for word in ['fixed', 'corrected', 'patched', 'resolved', 'updated']):
                    correction = line.split(' - ')[-1] if ' - ' in line else line
                    activities['corrections'].append(correction[:80])
                
                # Issues found
                if any(word in line_lower for word in ['error', 'issue', 'problem', 'bug', 'failed']):
                    issue = line.split(' - ')[-1] if ' - ' in line else line
                    activities['issues'].append(issue[:80])
                
                # Files changed
                file_match = re.search(r'([a-zA-Z0-9_/-]+\.(py|js|yaml|json|md|sh))', line)
                if file_match:
                    activities['files'].append(file_match.group(1))
                
                # Tests
                if 'test' in line_lower and any(word in line_lower for word in ['passed', 'failed', 'running']):
                    activities['tests'].append(line.split(' - ')[-1][:80])
                
                # Commits
                if 'commit' in line_lower or 'committed' in line_lower:
                    activities['commits'].append(line.split(' - ')[-1][:80])
        
        except:
            pass
        
        return activities
    
    def get_github_activity(self):
        """Get GitHub activity"""
        prs = []
        commits = []
        
        if self.github_token:
            try:
                headers = {'Authorization': f'token {self.github_token}'}
                
                # Get recent activity
                events_url = f'https://api.github.com/users/{self.github_username}/events'
                response = requests.get(events_url, headers=headers, timeout=3)
                
                if response.status_code == 200:
                    for event in response.json()[:10]:
                        if event['type'] == 'PullRequestEvent':
                            pr = event['payload']['pull_request']
                            prs.append({
                                'action': event['payload']['action'],
                                'title': pr['title'][:50],
                                'number': pr['number'],
                                'repo': event['repo']['name']
                            })
                        elif event['type'] == 'PushEvent':
                            commits.append({
                                'repo': event['repo']['name'],
                                'commits': len(event['payload']['commits']),
                                'message': event['payload']['commits'][0]['message'][:50] if event['payload']['commits'] else 'No message'
                            })
            except:
                pass
        
        return prs, commits
    
    def calculate_investigation_progress(self):
        """Calculate overall investigation progress"""
        try:
            result = subprocess.run(
                ['grep', '-c', 'Step\\|Phase\\|Completed', self.log_file],
                capture_output=True,
                text=True
            )
            steps = int(result.stdout.strip()) if result.stdout.strip().isdigit() else 0
            
            # Estimate progress
            progress = min(steps * 5, 100)  # Each step ~5%
            
            return progress
        except:
            return 0
    
    def display(self, stdscr):
        """The ULTIMATE display with everything!"""
        curses.curs_set(0)
        stdscr.nodelay(1)
        stdscr.timeout(100)
        
        # Colors
        curses.init_pair(1, curses.COLOR_GREEN, curses.COLOR_BLACK)
        curses.init_pair(2, curses.COLOR_RED, curses.COLOR_BLACK)
        curses.init_pair(3, curses.COLOR_YELLOW, curses.COLOR_BLACK)
        curses.init_pair(4, curses.COLOR_CYAN, curses.COLOR_BLACK)
        curses.init_pair(5, curses.COLOR_MAGENTA, curses.COLOR_BLACK)
        curses.init_pair(6, curses.COLOR_WHITE, curses.COLOR_BLACK)
        curses.init_pair(7, curses.COLOR_BLUE, curses.COLOR_BLACK)
        
        while True:
            stdscr.clear()
            height, width = stdscr.getmaxyx()
            
            # Get all data
            agents = self.get_complete_claude_info()
            dlqs, total_messages = self.get_dlq_status()
            activities = self.parse_live_activities()
            prs, commits = self.get_github_activity()
            progress = self.calculate_investigation_progress()
            
            # HEADER
            header = "🚀 ULTIMATE CLAUDE AI MONITOR - TOP TOP VERSION 🚀"
            timestamp = datetime.now().strftime("%H:%M:%S")
            stdscr.addstr(0, (width - len(header)) // 2, header, curses.A_BOLD | curses.color_pair(5))
            stdscr.addstr(1, width - 10, timestamp, curses.color_pair(6))
            
            # System stats bar
            stats_bar = f"CPU: {self.total_cpu_usage:.1f}% | MEM: {self.total_memory_usage:.1f}% | Agents: {len(agents)} | DLQs: {len(dlqs)} | Messages: {total_messages}"
            stdscr.addstr(1, 2, stats_bar, curses.color_pair(4))
            stdscr.addstr(2, 0, "=" * width, curses.color_pair(4))
            
            row = 4
            
            # CLAUDE AGENTS SECTION (Full width, detailed)
            active_agents = [a for a in agents.values() if 'Active' in a['status'] or 'Heavy' in a['status']]
            idle_agents = [a for a in agents.values() if 'Idle' in a['status']]
            
            title = f"🤖 CLAUDE AGENTS ({len(agents)} total: {len(active_agents)} active, {len(idle_agents)} idle)"
            stdscr.addstr(row, 0, title, curses.A_BOLD | curses.color_pair(5))
            row += 1
            stdscr.addstr(row, 0, "-" * width)
            row += 1
            
            if agents:
                # Headers
                headers_line = "PID     CPU    MEM   Runtime       Status        Action                    Task"
                stdscr.addstr(row, 0, headers_line, curses.A_BOLD | curses.color_pair(6))
                row += 1
                
                # Show active agents first
                for agent in sorted(agents.values(), key=lambda x: x['cpu'], reverse=True)[:10]:
                    # Color based on status
                    if '🔥' in agent['status']:
                        color = curses.color_pair(2)
                    elif '⚡' in agent['status']:
                        color = curses.color_pair(3)
                    elif '🔄' in agent['status']:
                        color = curses.color_pair(4)
                    else:
                        color = curses.color_pair(6)
                    
                    agent_line = f"{agent['pid']:<7} {agent['cpu']:>5.1f}% {agent['mem']:>5.1f}% {agent['runtime']:<13} {agent['status']:<13} {agent['action']:<25} {agent['task'][:width-75]}"
                    stdscr.addstr(row, 0, agent_line[:width-2], color)
                    row += 1
            
            row += 1
            
            # Three column layout
            col_width = width // 3
            
            # ISSUES FOUND (Left)
            issues_start = row
            stdscr.addstr(row, 0, "🔍 ISSUES FOUND", curses.A_BOLD | curses.color_pair(2))
            row += 1
            stdscr.addstr(row, 0, "-" * (col_width - 1))
            row += 1
            
            if activities['issues']:
                for issue in activities['issues'][:5]:
                    stdscr.addstr(row, 0, f"• {issue[:col_width-3]}", curses.color_pair(2))
                    row += 1
            else:
                stdscr.addstr(row, 0, "No issues yet", curses.color_pair(6))
                row += 1
            
            # CORRECTIONS APPLIED (Middle)
            row = issues_start
            stdscr.addstr(row, col_width, "✅ CORRECTIONS", curses.A_BOLD | curses.color_pair(1))
            row += 1
            stdscr.addstr(row, col_width, "-" * (col_width - 1))
            row += 1
            
            if activities['corrections']:
                for correction in activities['corrections'][:5]:
                    stdscr.addstr(row, col_width, f"✓ {correction[:col_width-3]}", curses.color_pair(1))
                    row += 1
            else:
                stdscr.addstr(row, col_width, "No corrections yet", curses.color_pair(6))
                row += 1
            
            # FILES CHANGED (Right)
            row = issues_start
            stdscr.addstr(row, col_width * 2, "📁 FILES CHANGED", curses.A_BOLD | curses.color_pair(4))
            row += 1
            stdscr.addstr(row, col_width * 2, "-" * (col_width - 1))
            row += 1
            
            if activities['files']:
                for file in list(set(activities['files']))[:5]:
                    stdscr.addstr(row, col_width * 2, f"📝 {file[:col_width-4]}", curses.color_pair(4))
                    row += 1
            else:
                stdscr.addstr(row, col_width * 2, "No files changed", curses.color_pair(6))
                row += 1
            
            row = max(row, issues_start + 7) + 1
            
            # INVESTIGATION PROGRESS BAR
            stdscr.addstr(row, 0, "📊 OVERALL INVESTIGATION PROGRESS", curses.A_BOLD | curses.color_pair(5))
            row += 1
            
            # Progress bar
            bar_width = width - 10
            filled = int(bar_width * (progress / 100))
            empty = bar_width - filled
            progress_bar = f"[{'█' * filled}{'░' * empty}] {progress}%"
            
            # Color based on progress
            if progress < 30:
                bar_color = curses.color_pair(2)
            elif progress < 70:
                bar_color = curses.color_pair(3)
            else:
                bar_color = curses.color_pair(1)
            
            stdscr.addstr(row, 5, progress_bar, bar_color)
            row += 2
            
            # DLQ & GitHub Section
            half_width = width // 2
            
            # DLQ STATUS (Left)
            dlq_start = row
            stdscr.addstr(row, 0, f"🚨 DLQ STATUS ({len(dlqs)} queues, {total_messages} msgs)", curses.A_BOLD | curses.color_pair(2))
            row += 1
            stdscr.addstr(row, 0, "-" * (half_width - 1))
            row += 1
            
            if dlqs:
                for dlq_name, count in list(dlqs.items())[:4]:
                    color = curses.color_pair(2) if count > 10 else curses.color_pair(3)
                    icon = "🔴" if count > 10 else "🟡"
                    dlq_line = f"{icon} {dlq_name[:30]}: {count} messages"
                    stdscr.addstr(row, 0, dlq_line[:half_width-2], color)
                    row += 1
            else:
                stdscr.addstr(row, 0, "✅ All DLQs clear!", curses.color_pair(1))
                row += 1
            
            # GITHUB ACTIVITY (Right)
            row = dlq_start
            stdscr.addstr(row, half_width, f"🔧 GITHUB ACTIVITY", curses.A_BOLD | curses.color_pair(5))
            row += 1
            stdscr.addstr(row, half_width, "-" * (half_width - 1))
            row += 1
            
            if prs or commits:
                for pr in prs[:2]:
                    pr_line = f"PR: {pr['title'][:half_width-5]}"
                    stdscr.addstr(row, half_width, pr_line, curses.color_pair(5))
                    row += 1
                for commit in commits[:2]:
                    commit_line = f"Commit: {commit['message'][:half_width-9]}"
                    stdscr.addstr(row, half_width, commit_line, curses.color_pair(4))
                    row += 1
            else:
                stdscr.addstr(row, half_width, "No recent GitHub activity", curses.color_pair(6))
                row += 1
            
            # Footer
            footer_row = height - 2
            stdscr.addstr(footer_row, 0, "=" * width, curses.color_pair(4))
            
            controls = "q: Quit | r: Refresh | Auto-refresh: 1s | THE TOP TOP MONITOR!"
            stdscr.addstr(footer_row + 1, (width - len(controls)) // 2, controls, curses.color_pair(6))
            
            stdscr.refresh()
            
            # Handle input
            key = stdscr.getch()
            if key == ord('q'):
                break
            elif key == ord('r'):
                continue
            
            time.sleep(self.refresh_interval)
    
    def run(self):
        """Run the ULTIMATE monitor"""
        try:
            curses.wrapper(self.display)
        except KeyboardInterrupt:
            pass
        except Exception as e:
            print(f"Error: {e}")
            import traceback
            traceback.print_exc()

def main():
    print("🚀 Starting ULTIMATE CLAUDE AI MONITOR - TOP TOP VERSION!")
    print("📊 This is the most comprehensive monitor with EVERYTHING!")
    print("🤖 Showing all agents, corrections, issues, files, progress, DLQs, and GitHub activity!")
    print("⏳ Loading the ultimate dashboard...")
    time.sleep(2)
    
    monitor = UltimateClaudeMonitor()
    monitor.run()

if __name__ == "__main__":
    main()
