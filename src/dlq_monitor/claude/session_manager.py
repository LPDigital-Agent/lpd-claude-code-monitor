#!/usr/bin/env python3
"""
Enhanced Claude Investigation Status Monitor
Shows detailed status of all Claude sessions and their activities
"""
import subprocess
import os
import json
import time
import psutil
from datetime import datetime, timedelta
from pathlib import Path
import re

class ClaudeSessionMonitor:
    """Monitor and track Claude investigation sessions"""
    
    def __init__(self):
        self.log_file = "/Users/fabio.santos/LPD Repos/lpd-claude-code-monitor/dlq_monitor_FABIO-PROD_sa-east-1.log"
        self.session_file = "/Users/fabio.santos/LPD Repos/lpd-claude-code-monitor/.claude_sessions.json"
        self.sessions = self.load_sessions()
    
    def load_sessions(self):
        """Load session data from file"""
        if os.path.exists(self.session_file):
            try:
                with open(self.session_file, 'r') as f:
                    return json.load(f)
            except:
                return {}
        return {}
    
    def save_sessions(self):
        """Save session data to file"""
        with open(self.session_file, 'w') as f:
            json.dump(self.sessions, f, indent=2, default=str)
    
    def check_claude_processes(self):
        """Check all running Claude processes with detailed info"""
        print("\n🔍 ACTIVE CLAUDE PROCESSES")
        print("=" * 70)
        
        claude_processes = []
        
        try:
            # Get all processes
            for proc in psutil.process_iter(['pid', 'name', 'cmdline', 'create_time', 'status']):
                try:
                    # Check if it's a Claude process
                    cmdline = proc.info.get('cmdline', [])
                    if cmdline and any('claude' in str(cmd).lower() for cmd in cmdline):
                        # Get process details
                        pid = proc.info['pid']
                        status = proc.info['status']
                        create_time = datetime.fromtimestamp(proc.info['create_time'])
                        runtime = datetime.now() - create_time
                        
                        # Extract queue name from command if possible
                        queue_name = "Unknown"
                        for cmd in cmdline:
                            if 'dlq' in cmd.lower():
                                # Try to extract queue name
                                match = re.search(r'(fm-[a-z0-9-]+dlq[a-z0-9-]*)', cmd, re.IGNORECASE)
                                if match:
                                    queue_name = match.group(1)
                                    break
                        
                        # Get CPU and memory usage
                        cpu_percent = proc.cpu_percent(interval=0.1)
                        memory_info = proc.memory_info()
                        memory_mb = memory_info.rss / 1024 / 1024
                        
                        claude_processes.append({
                            'pid': pid,
                            'queue': queue_name,
                            'status': status,
                            'runtime': runtime,
                            'cpu': cpu_percent,
                            'memory_mb': memory_mb,
                            'create_time': create_time
                        })
                        
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
            
            if claude_processes:
                print(f"Found {len(claude_processes)} active Claude session(s):\n")
                
                for i, proc in enumerate(claude_processes, 1):
                    print(f"📊 Session {i}:")
                    print(f"   PID: {proc['pid']}")
                    print(f"   Queue: {proc['queue']}")
                    print(f"   Status: {proc['status']}")
                    print(f"   Runtime: {self.format_duration(proc['runtime'])}")
                    print(f"   CPU Usage: {proc['cpu']:.1f}%")
                    print(f"   Memory: {proc['memory_mb']:.1f} MB")
                    print(f"   Started: {proc['create_time'].strftime('%H:%M:%S')}")
                    
                    # Update session tracking
                    self.sessions[str(proc['pid'])] = {
                        'queue': proc['queue'],
                        'start_time': proc['create_time'],
                        'last_seen': datetime.now(),
                        'status': 'running'
                    }
                    print()
            else:
                print("❌ No active Claude processes found")
                
        except Exception as e:
            print(f"❌ Error checking processes: {e}")
            # Fallback to ps command
            self.check_processes_fallback()
        
        self.save_sessions()
        return claude_processes
    
    def check_processes_fallback(self):
        """Fallback method using ps command"""
        try:
            result = subprocess.run(['ps', 'aux'], capture_output=True, text=True)
            lines = result.stdout.split('\n')
            claude_lines = [line for line in lines if 'claude' in line.lower() and 'grep' not in line]
            
            if claude_lines:
                print("\nFallback process list:")
                for line in claude_lines:
                    parts = line.split()
                    if len(parts) > 10:
                        pid = parts[1]
                        cpu = parts[2]
                        mem = parts[3]
                        cmd = ' '.join(parts[10:])[:80]
                        print(f"   PID {pid}: CPU {cpu}%, MEM {mem}%, CMD: {cmd}...")
            
        except Exception as e:
            print(f"Fallback also failed: {e}")
    
    def analyze_recent_logs(self):
        """Analyze recent investigation activities from logs"""
        print("\n📋 RECENT INVESTIGATION ACTIVITIES")
        print("=" * 70)
        
        try:
            with open(self.log_file, 'r') as f:
                lines = f.readlines()
            
            # Get last 500 lines for analysis
            recent_lines = lines[-500:]
            
            # Track investigation events
            investigations = {}
            
            for line in recent_lines:
                # Parse timestamp
                timestamp_match = re.match(r'(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})', line)
                if not timestamp_match:
                    continue
                    
                timestamp = datetime.strptime(timestamp_match.group(1), '%Y-%m-%d %H:%M:%S')
                
                # Check for investigation events
                if 'Starting auto-investigation for' in line:
                    match = re.search(r'Starting auto-investigation for (.+)', line)
                    if match:
                        queue = match.group(1)
                        investigations[queue] = {
                            'status': 'started',
                            'start_time': timestamp,
                            'events': [f"Started at {timestamp.strftime('%H:%M:%S')}"]
                        }
                
                elif 'Executing Claude investigation' in line:
                    for queue in investigations:
                        if queue in line or (timestamp - investigations[queue]['start_time']).seconds < 10:
                            investigations[queue]['status'] = 'executing'
                            investigations[queue]['events'].append(f"Executing at {timestamp.strftime('%H:%M:%S')}")
                            break
                
                elif 'investigation completed successfully' in line:
                    match = re.search(r'investigation completed successfully for (.+)', line)
                    if match:
                        queue = match.group(1)
                        if queue in investigations:
                            investigations[queue]['status'] = 'completed'
                            investigations[queue]['end_time'] = timestamp
                            investigations[queue]['events'].append(f"Completed at {timestamp.strftime('%H:%M:%S')}")
                
                elif 'investigation failed' in line:
                    match = re.search(r'investigation failed for (.+)', line)
                    if match:
                        queue = match.group(1)
                        if queue in investigations:
                            investigations[queue]['status'] = 'failed'
                            investigations[queue]['end_time'] = timestamp
                            investigations[queue]['events'].append(f"Failed at {timestamp.strftime('%H:%M:%S')}")
                
                elif 'investigation timed out' in line:
                    match = re.search(r'investigation timed out for (.+)', line)
                    if match:
                        queue = match.group(1)
                        if queue in investigations:
                            investigations[queue]['status'] = 'timeout'
                            investigations[queue]['end_time'] = timestamp
                            investigations[queue]['events'].append(f"Timed out at {timestamp.strftime('%H:%M:%S')}")
            
            if investigations:
                print(f"Found {len(investigations)} investigation(s) in recent logs:\n")
                
                for queue, info in investigations.items():
                    status_icon = {
                        'started': '🔄',
                        'executing': '⚙️',
                        'completed': '✅',
                        'failed': '❌',
                        'timeout': '⏰'
                    }.get(info['status'], '❓')
                    
                    print(f"{status_icon} Queue: {queue}")
                    print(f"   Status: {info['status'].upper()}")
                    print(f"   Started: {info['start_time'].strftime('%Y-%m-%d %H:%M:%S')}")
                    
                    if 'end_time' in info:
                        duration = info['end_time'] - info['start_time']
                        print(f"   Duration: {self.format_duration(duration)}")
                    else:
                        runtime = datetime.now() - info['start_time']
                        print(f"   Running for: {self.format_duration(runtime)}")
                    
                    print(f"   Timeline:")
                    for event in info['events'][-5:]:  # Show last 5 events
                        print(f"     • {event}")
                    print()
            else:
                print("No recent investigations found in logs")
                
        except Exception as e:
            print(f"❌ Error analyzing logs: {e}")
    
    def check_queue_status(self):
        """Check current DLQ queue status"""
        print("\n📊 CURRENT DLQ QUEUE STATUS")
        print("=" * 70)
        
        import sys
        sys.path.insert(0, str(Path(__file__).parent))
        
        try:
            from dlq_monitor import DLQMonitor, MonitorConfig
            
            config = MonitorConfig(
                aws_profile="FABIO-PROD",
                region="sa-east-1",
                auto_investigate_dlqs=[
                    "fm-digitalguru-api-update-dlq-prod",
                    "fm-transaction-processor-dlq-prd"
                ]
            )
            
            monitor = DLQMonitor(config)
            alerts = monitor.check_dlq_messages()
            
            monitored_queues = {
                "fm-digitalguru-api-update-dlq-prod": "🤖",
                "fm-transaction-processor-dlq-prd": "🤖"
            }
            
            if alerts:
                print(f"Found {len(alerts)} queue(s) with messages:\n")
                for alert in alerts:
                    icon = monitored_queues.get(alert.queue_name, "📋")
                    print(f"{icon} {alert.queue_name}")
                    print(f"   Messages: {alert.message_count}")
                    
                    if alert.queue_name in monitored_queues:
                        if monitor._should_auto_investigate(alert.queue_name):
                            print(f"   Status: ✅ Ready for auto-investigation")
                        else:
                            if alert.queue_name in monitor.auto_investigations:
                                last_time = monitor.auto_investigations[alert.queue_name]
                                time_since = datetime.now() - last_time
                                cooldown_left = monitor.investigation_cooldown - time_since.total_seconds()
                                if cooldown_left > 0:
                                    print(f"   Status: 🕐 Cooldown ({cooldown_left/60:.1f} min remaining)")
                            if alert.queue_name in monitor.investigation_processes:
                                print(f"   Status: 🔄 Investigation running")
                    print()
            else:
                print("✅ All DLQ queues are empty")
                
        except Exception as e:
            print(f"❌ Error checking queue status: {e}")
    
    def get_investigation_summary(self):
        """Get summary of all investigations"""
        print("\n📈 INVESTIGATION SUMMARY")
        print("=" * 70)
        
        # Clean up old sessions
        current_time = datetime.now()
        active_sessions = 0
        completed_sessions = 0
        
        for pid, session in list(self.sessions.items()):
            if isinstance(session['last_seen'], str):
                session['last_seen'] = datetime.fromisoformat(session['last_seen'])
            
            time_since_seen = current_time - session['last_seen']
            
            if time_since_seen.seconds < 60:  # Seen in last minute
                active_sessions += 1
            else:
                completed_sessions += 1
                session['status'] = 'completed'
        
        print(f"📊 Statistics:")
        print(f"   Active Sessions: {active_sessions}")
        print(f"   Completed Today: {completed_sessions}")
        print(f"   Total Tracked: {len(self.sessions)}")
        
        # Show recent completions
        if completed_sessions > 0:
            print(f"\n   Recent Completions:")
            for pid, session in self.sessions.items():
                if session.get('status') == 'completed':
                    print(f"     • {session.get('queue', 'Unknown')} - PID {pid}")
    
    def format_duration(self, duration):
        """Format duration in human-readable format"""
        if isinstance(duration, timedelta):
            total_seconds = int(duration.total_seconds())
        else:
            total_seconds = int(duration)
        
        hours = total_seconds // 3600
        minutes = (total_seconds % 3600) // 60
        seconds = total_seconds % 60
        
        if hours > 0:
            return f"{hours}h {minutes}m {seconds}s"
        elif minutes > 0:
            return f"{minutes}m {seconds}s"
        else:
            return f"{seconds}s"
    
    def show_help(self):
        """Show available commands and tips"""
        print("\n💡 MONITORING TIPS")
        print("=" * 70)
        print("• Active processes show real-time CPU and memory usage")
        print("• Investigations in cooldown won't trigger for 1 hour")
        print("• Check logs for detailed error messages if investigations fail")
        print("• Use 'ps aux | grep claude' for manual process checking")
        print("• Session data is stored in .claude_sessions.json")
        print("\n🔧 USEFUL COMMANDS:")
        print("   tail -f dlq_monitor_FABIO-PROD_sa-east-1.log  # Watch logs")
        print("   ps aux | grep claude                          # Check processes")
        print("   kill -9 <PID>                                 # Stop investigation")
        print("   ./start_monitor.sh production                 # Restart monitor")

def main():
    """Main monitoring function"""
    print("=" * 70)
    print("🤖 CLAUDE INVESTIGATION STATUS MONITOR")
    print(f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70)
    
    monitor = ClaudeSessionMonitor()
    
    # Check active Claude processes
    processes = monitor.check_claude_processes()
    
    # Analyze recent logs
    monitor.analyze_recent_logs()
    
    # Check queue status
    monitor.check_queue_status()
    
    # Get summary
    monitor.get_investigation_summary()
    
    # Show help
    monitor.show_help()
    
    print("\n" + "=" * 70)
    if processes:
        print(f"⚠️  {len(processes)} Claude investigation(s) currently running")
        print("Monitor will continue checking DLQs while investigations run")
    else:
        print("✅ No active Claude investigations")
        print("System ready for new investigations")
    print("=" * 70)

if __name__ == "__main__":
    main()
