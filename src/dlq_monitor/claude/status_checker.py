#!/usr/bin/env python3
"""
Check the status of auto-investigations and diagnose any issues
"""
import subprocess
import os
import time
from datetime import datetime, timedelta

def check_claude_processes():
    """Check if any Claude processes are running"""
    print("\n🔍 Checking for running Claude processes...")
    print("-" * 50)
    
    try:
        result = subprocess.run(['ps', 'aux'], capture_output=True, text=True)
        lines = result.stdout.split('\n')
        claude_processes = [line for line in lines if 'claude' in line.lower() and 'grep' not in line]
        
        if claude_processes:
            print("✅ Found Claude processes:")
            for proc in claude_processes:
                parts = proc.split()
                if len(parts) > 10:
                    pid = parts[1]
                    cmd = ' '.join(parts[10:])[:100]
                    print(f"   PID {pid}: {cmd}...")
        else:
            print("❌ No Claude processes currently running")
            
    except Exception as e:
        print(f"❌ Error checking processes: {e}")

def check_recent_logs():
    """Check recent log entries for investigation status"""
    print("\n📋 Recent Auto-Investigation Log Entries:")
    print("-" * 50)
    
    log_file = "/Users/fabio.santos/LPD Repos/lpd-claude-code-monitor/dlq_monitor_FABIO-PROD_sa-east-1.log"
    
    try:
        with open(log_file, 'r') as f:
            lines = f.readlines()
            
        # Get last 200 lines
        recent_lines = lines[-200:]
        
        # Filter for investigation-related entries
        investigation_lines = []
        for line in recent_lines:
            if any(keyword in line.lower() for keyword in ['investigation', 'claude', 'triggering', 'auto-']):
                investigation_lines.append(line.strip())
        
        if investigation_lines:
            print("Found investigation entries:")
            for line in investigation_lines[-10:]:  # Last 10 entries
                # Extract timestamp and message
                if ' - ' in line:
                    parts = line.split(' - ', 3)
                    if len(parts) >= 4:
                        timestamp = parts[0]
                        message = parts[-1]
                        print(f"   [{timestamp}] {message}")
        else:
            print("❌ No recent investigation entries found")
            
    except Exception as e:
        print(f"❌ Error reading log file: {e}")

def check_dlq_status():
    """Check current DLQ status"""
    print("\n📊 Current DLQ Status:")
    print("-" * 50)
    
    import sys
    from pathlib import Path
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
        
        if alerts:
            print(f"🚨 Found {len(alerts)} DLQs with messages:")
            for alert in alerts:
                status = "🤖" if alert.queue_name in config.auto_investigate_dlqs else "📋"
                print(f"   {status} {alert.queue_name}: {alert.message_count} messages")
                
                # Check if investigation should trigger
                if alert.queue_name in config.auto_investigate_dlqs:
                    if monitor._should_auto_investigate(alert.queue_name):
                        print(f"      ✅ Eligible for auto-investigation")
                    else:
                        if alert.queue_name in monitor.auto_investigations:
                            last_time = monitor.auto_investigations[alert.queue_name]
                            time_since = datetime.now() - last_time
                            cooldown_left = monitor.investigation_cooldown - time_since.total_seconds()
                            if cooldown_left > 0:
                                print(f"      🕐 Cooldown: {cooldown_left/60:.1f} minutes remaining")
                        if alert.queue_name in monitor.investigation_processes:
                            print(f"      🔄 Investigation currently running")
        else:
            print("✅ All DLQs are empty")
            
    except Exception as e:
        print(f"❌ Error checking DLQ status: {e}")
        import traceback
        traceback.print_exc()

def test_claude_command():
    """Test if Claude command works"""
    print("\n🧪 Testing Claude Command:")
    print("-" * 50)
    
    try:
        # Test simple claude command
        test_prompt = "echo 'Testing Claude command'"
        cmd = ['claude', '-p', test_prompt]
        
        print(f"Testing command: claude -p '{test_prompt}'")
        
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=10
        )
        
        if result.returncode == 0:
            print("✅ Claude command works!")
            if result.stdout:
                print(f"   Output: {result.stdout.strip()[:100]}")
        else:
            print(f"❌ Claude command failed with exit code: {result.returncode}")
            if result.stderr:
                print(f"   Error: {result.stderr.strip()}")
                
    except subprocess.TimeoutExpired:
        print("⏰ Claude command timed out after 10 seconds")
    except FileNotFoundError:
        print("❌ Claude command not found in PATH")
    except Exception as e:
        print(f"❌ Error testing Claude command: {e}")

def main():
    print("=" * 60)
    print("🔍 Auto-Investigation Status Check")
    print("=" * 60)
    
    # Check DLQ status
    check_dlq_status()
    
    # Check recent logs
    check_recent_logs()
    
    # Check running processes
    check_claude_processes()
    
    # Test Claude command
    test_claude_command()
    
    print("\n" + "=" * 60)
    print("📊 Summary:")
    print("-" * 50)
    print("If auto-investigation isn't working, check:")
    print("1. ✅ DLQ has messages in monitored queues")
    print("2. ✅ Not in cooldown period (1 hour)")
    print("3. ✅ Claude command is accessible")
    print("4. ✅ No duplicate alert handling")
    print("=" * 60)

if __name__ == "__main__":
    main()
