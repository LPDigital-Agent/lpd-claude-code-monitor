#!/usr/bin/env python3
"""
Claude AI Corrections Live Monitor
Real-time dashboard showing what Claude agents are actually doing, their corrections, and progress
"""
import subprocess
import time
import os
import sys
import json
import requests
import re
from datetime import datetime, timedelta
from collections import defaultdict, deque
import curses
from pathlib import Path

class ClaudeCorrectionsMonitor:
    """Monitor focused on Claude AI corrections and actual work being done"""
    
    def __init__(self):
        self.log_file = "dlq_monitor_FABIO-PROD_sa-east-1.log"
        self.session_file = ".claude_sessions.json"
        self.refresh_interval = 2  # Faster refresh for real-time feel
        
        # GitHub configuration
        self.github_token = os.getenv('GITHUB_TOKEN', '')
        self.github_username = os.getenv('GITHUB_USERNAME', 'fabio-lpd')
        
        # Track Claude activities
        self.claude_agents = {}
        self.corrections_made = deque(maxlen=50)  # Last 50 corrections
        self.issues_found = deque(maxlen=30)  # Last 30 issues
        self.current_actions = {}
        self.pr_created = []
        
    def get_claude_processes_detailed(self):
        """Get detailed info about Claude processes"""
        agents = {}
        try:
            # Get all Claude processes with detailed info
            result = subprocess.run(
                ['ps', 'aux'], 
                capture_output=True, 
                text=True
            )
            
            for line in result.stdout.split('\n'):
                if 'claude' in line.lower() and 'grep' not in line and 'monitor' not in line:
                    parts = line.split(None, 10)
                    if len(parts) > 10:
                        pid = parts[1]
                        cpu = float(parts[2])
                        mem = float(parts[3])
                        start_time = parts[8]
                        runtime = parts[9]
                        command = parts[10]
                        
                        # Determine what the agent is doing
                        agent_action = "Analyzing"
                        if 'investigation' in command.lower():
                            agent_action = "🔍 Investigating Issues"
                        elif 'fix' in command.lower():
                            agent_action = "🔨 Applying Fixes"
                        elif 'test' in command.lower():
                            agent_action = "🧪 Running Tests"
                        elif 'analyze' in command.lower():
                            agent_action = "📊 Analyzing Code"
                        elif 'commit' in command.lower():
                            agent_action = "📝 Committing Changes"
                        elif 'pr' in command.lower() or 'pull' in command.lower():
                            agent_action = "🔧 Creating PR"
                        
                        # Extract the actual command/prompt if visible
                        prompt_match = re.search(r'-p\s+"([^"]+)"', command)
                        if prompt_match:
                            prompt = prompt_match.group(1)[:100]  # First 100 chars
                        else:
                            prompt = "Processing..."
                        
                        agents[pid] = {
                            'pid': pid,
                            'cpu': cpu,
                            'mem': mem,
                            'start_time': start_time,
                            'runtime': runtime,
                            'action': agent_action,
                            'prompt': prompt,
                            'status': 'Active' if cpu > 1.0 else 'Idle'
                        }
        except Exception as e:
            pass
        
        return agents
    
    def parse_corrections_from_logs(self):
        """Parse actual corrections and fixes from logs"""
        corrections = []
        issues = []
        
        try:
            # Look for specific correction patterns in logs
            result = subprocess.run(
                ['tail', '-n', '200', self.log_file],
                capture_output=True,
                text=True
            )
            
            for line in result.stdout.split('\n'):
                # Look for fixes being applied
                if any(keyword in line.lower() for keyword in 
                       ['fix applied', 'correction made', 'updated', 'fixed', 'resolved', 'patched']):
                    
                    # Extract timestamp
                    timestamp_match = re.match(r'(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})', line)
                    if timestamp_match:
                        timestamp = timestamp_match.group(1)
                        
                        # Extract the correction details
                        correction_text = line.split(' - ')[-1] if ' - ' in line else line
                        
                        corrections.append({
                            'time': timestamp,
                            'correction': correction_text[:100],
                            'type': self._determine_correction_type(correction_text)
                        })
                
                # Look for issues found
                if any(keyword in line.lower() for keyword in 
                       ['error found', 'issue detected', 'problem identified', 'bug found', 
                        'validation error', 'typeerror', 'exception']):
                    
                    issue_text = line.split(' - ')[-1] if ' - ' in line else line
                    issues.append({
                        'issue': issue_text[:100],
                        'severity': self._determine_severity(issue_text)
                    })
        
        except Exception as e:
            pass
        
        return corrections, issues
    
    def _determine_correction_type(self, text):
        """Determine what type of correction was made"""
        text_lower = text.lower()
        if 'import' in text_lower:
            return "📦 Import Fix"
        elif 'type' in text_lower or 'typing' in text_lower:
            return "🔤 Type Fix"
        elif 'validation' in text_lower:
            return "✅ Validation Fix"
        elif 'error handling' in text_lower:
            return "🛡️ Error Handling"
        elif 'config' in text_lower:
            return "⚙️ Configuration"
        elif 'dependency' in text_lower:
            return "📚 Dependency"
        else:
            return "🔧 General Fix"
    
    def _determine_severity(self, text):
        """Determine issue severity"""
        text_lower = text.lower()
        if any(word in text_lower for word in ['critical', 'fatal', 'severe']):
            return "🔴 CRITICAL"
        elif any(word in text_lower for word in ['error', 'exception', 'fail']):
            return "🟠 ERROR"
        elif any(word in text_lower for word in ['warning', 'warn']):
            return "🟡 WARNING"
        else:
            return "🔵 INFO"
    
    def get_github_prs(self):
        """Get PRs created by Claude"""
        if not self.github_token:
            return []
        
        prs = []
        try:
            headers = {'Authorization': f'token {self.github_token}'}
            
            # Search for recent PRs
            url = f'https://api.github.com/search/issues?q=author:{self.github_username}+type:pr+created:>{datetime.now().strftime("%Y-%m-%d")}'
            response = requests.get(url, headers=headers, timeout=5)
            
            if response.status_code == 200:
                data = response.json()
                for item in data.get('items', [])[:5]:
                    prs.append({
                        'number': item['number'],
                        'title': item['title'][:60],
                        'state': item['state'],
                        'created': item['created_at'],
                        'url': item['html_url']
                    })
        except:
            pass
        
        return prs
    
    def get_investigation_progress(self):
        """Parse investigation progress from logs"""
        progress = {
            'current_step': 'Unknown',
            'steps_completed': [],
            'percentage': 0
        }
        
        try:
            # Look for investigation steps
            result = subprocess.run(
                ['grep', '-E', 'Step|Phase|Analyzing|Checking|Creating|Committing', self.log_file],
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                lines = result.stdout.strip().split('\n')[-10:]  # Last 10 steps
                
                for line in lines:
                    if 'Step' in line or 'Phase' in line:
                        step_match = re.search(r'(Step|Phase)\s+(\d+)', line)
                        if step_match:
                            step_num = int(step_match.group(2))
                            progress['percentage'] = min(step_num * 10, 100)
                    
                    # Extract action
                    for action in ['Analyzing', 'Checking', 'Creating', 'Committing', 'Testing']:
                        if action in line:
                            progress['current_step'] = action
                            progress['steps_completed'].append(action)
                            break
        except:
            pass
        
        return progress
    
    def display(self, stdscr):
        """Enhanced display focused on Claude corrections"""
        curses.curs_set(0)
        stdscr.nodelay(1)
        stdscr.timeout(100)
        
        # Color pairs
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
            header = "🤖 CLAUDE AI CORRECTIONS MONITOR 🤖"
            subtitle = "Real-time view of what Claude agents are fixing"
            timestamp = datetime.now().strftime("%H:%M:%S")
            
            stdscr.addstr(0, (width - len(header)) // 2, header, curses.A_BOLD | curses.color_pair(4))
            stdscr.addstr(1, (width - len(subtitle)) // 2, subtitle, curses.color_pair(6))
            stdscr.addstr(1, width - 10, timestamp, curses.color_pair(6))
            stdscr.addstr(2, 0, "=" * width, curses.color_pair(4))
            
            row = 4
            
            # Get current data
            agents = self.get_claude_processes_detailed()
            corrections, issues = self.parse_corrections_from_logs()
            progress = self.get_investigation_progress()
            prs = self.get_github_prs()
            
            # CLAUDE AGENTS PANEL (Full Width)
            agent_count = len(agents)
            active_count = sum(1 for a in agents.values() if a['status'] == 'Active')
            
            title = f"🤖 CLAUDE AGENTS ({agent_count} total, {active_count} active)"
            stdscr.addstr(row, 0, title, curses.A_BOLD | curses.color_pair(5))
            row += 1
            stdscr.addstr(row, 0, "-" * width)
            row += 1
            
            if agents:
                # Headers
                headers = "PID     CPU   MEM   Runtime  Status    Action"
                stdscr.addstr(row, 0, headers, curses.A_BOLD | curses.color_pair(6))
                row += 1
                
                # Show agents (sorted by CPU usage)
                for pid, agent in sorted(agents.items(), key=lambda x: x[1]['cpu'], reverse=True)[:8]:
                    # Color based on status
                    color = curses.color_pair(1) if agent['status'] == 'Active' else curses.color_pair(6)
                    
                    agent_line = f"{pid:<7} {agent['cpu']:>4.1f}% {agent['mem']:>4.1f}% {agent['runtime']:<8} {agent['status']:<9} {agent['action']}"
                    stdscr.addstr(row, 0, agent_line[:width-2], color)
                    row += 1
                    
                    # Show what they're working on (indented)
                    if agent['status'] == 'Active' and agent['prompt'] != "Processing...":
                        work_line = f"  └─ {agent['prompt'][:width-5]}..."
                        stdscr.addstr(row, 0, work_line, curses.color_pair(6))
                        row += 1
            else:
                stdscr.addstr(row, 0, "No Claude agents detected", curses.color_pair(3))
                row += 1
            
            row += 2
            
            # Split screen for Issues and Corrections
            panel_width = width // 2
            
            # ISSUES FOUND (Left Panel)
            issues_row = row
            stdscr.addstr(row, 0, "🔍 ISSUES FOUND", curses.A_BOLD | curses.color_pair(2))
            row += 1
            stdscr.addstr(row, 0, "-" * (panel_width - 2))
            row += 1
            
            if issues:
                for issue in issues[:5]:
                    severity_color = curses.color_pair(2) if 'CRITICAL' in issue['severity'] else curses.color_pair(3)
                    issue_line = f"{issue['severity']} {issue['issue'][:panel_width-15]}"
                    stdscr.addstr(row, 0, issue_line[:panel_width-2], severity_color)
                    row += 1
            else:
                stdscr.addstr(row, 0, "No issues detected yet", curses.color_pair(6))
                row += 1
            
            # CORRECTIONS APPLIED (Right Panel)
            row = issues_row
            stdscr.addstr(row, panel_width, "✅ CORRECTIONS APPLIED", curses.A_BOLD | curses.color_pair(1))
            row += 1
            stdscr.addstr(row, panel_width, "-" * (panel_width - 2))
            row += 1
            
            if corrections:
                for correction in corrections[:5]:
                    corr_line = f"{correction['type']} {correction['correction'][:panel_width-20]}"
                    stdscr.addstr(row, panel_width, corr_line[:panel_width-2], curses.color_pair(1))
                    row += 1
            else:
                stdscr.addstr(row, panel_width, "No corrections applied yet", curses.color_pair(6))
                row += 1
            
            # Align rows
            row = max(row, issues_row + 7) + 2
            
            # INVESTIGATION PROGRESS
            stdscr.addstr(row, 0, "📊 INVESTIGATION PROGRESS", curses.A_BOLD | curses.color_pair(4))
            row += 1
            stdscr.addstr(row, 0, "-" * width)
            row += 1
            
            # Progress bar
            progress_width = width - 20
            filled = int(progress_width * (progress['percentage'] / 100))
            progress_bar = f"[{'█' * filled}{'░' * (progress_width - filled)}] {progress['percentage']}%"
            stdscr.addstr(row, 0, "Progress: ", curses.color_pair(6))
            stdscr.addstr(row, 10, progress_bar, curses.color_pair(1))
            row += 1
            
            # Current step
            current_step = f"Current: {progress['current_step']}"
            stdscr.addstr(row, 0, current_step, curses.color_pair(4))
            row += 1
            
            # Completed steps
            if progress['steps_completed']:
                steps_line = "Completed: " + " → ".join(progress['steps_completed'][-5:])
                stdscr.addstr(row, 0, steps_line[:width-2], curses.color_pair(6))
                row += 1
            
            row += 2
            
            # PULL REQUESTS
            if prs:
                stdscr.addstr(row, 0, "🔧 PULL REQUESTS CREATED", curses.A_BOLD | curses.color_pair(5))
                row += 1
                stdscr.addstr(row, 0, "-" * width)
                row += 1
                
                for pr in prs[:3]:
                    pr_color = curses.color_pair(1) if pr['state'] == 'open' else curses.color_pair(6)
                    pr_line = f"  PR #{pr['number']}: {pr['title']} [{pr['state'].upper()}]"
                    stdscr.addstr(row, 0, pr_line[:width-2], pr_color)
                    row += 1
            
            # Footer with statistics
            footer_row = height - 3
            stdscr.addstr(footer_row, 0, "=" * width, curses.color_pair(4))
            
            stats = f"🤖 Agents: {agent_count} ({active_count} active) | 🔍 Issues: {len(issues)} | ✅ Corrections: {len(corrections)} | 🔧 PRs: {len(prs)}"
            stdscr.addstr(footer_row + 1, 2, stats, curses.color_pair(6))
            
            controls = "Press 'q' to quit | 'r' to refresh | Auto-refresh: 2s"
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
        """Run the corrections monitor"""
        try:
            curses.wrapper(self.display)
        except KeyboardInterrupt:
            pass
        except Exception as e:
            print(f"Error: {e}")
            import traceback
            traceback.print_exc()

def main():
    """Main entry point"""
    print("🤖 Starting Claude AI Corrections Monitor...")
    print("📊 This monitor shows what Claude agents are actually fixing")
    print("⏳ Loading...")
    time.sleep(2)
    
    monitor = ClaudeCorrectionsMonitor()
    monitor.run()

if __name__ == "__main__":
    main()
