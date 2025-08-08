#!/usr/bin/env python3
"""
Continuous Production DLQ Monitor for FABIO-PROD with PR Audio Notifications
Runs indefinitely with proper signal handling for production use
"""
import sys
import os
import time
import signal
import logging
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from dlq_monitor.core.monitor import DLQMonitor, MonitorConfig
from dlq_monitor.notifiers.pr_audio import PRAudioMonitor

class ProductionMonitor:
    def __init__(self, interval=30, enable_pr_monitoring=True):
        self.interval = interval
        self.running = True
        self.cycle_count = 0
        
        # Production configuration for FABIO-PROD with auto-investigation
        config = MonitorConfig(
            aws_profile="FABIO-PROD",
            region="sa-east-1",
            check_interval=interval,
            notification_sound=True,
            auto_investigate_dlqs=[
                "fm-digitalguru-api-update-dlq-prod",
                "fm-transaction-processor-dlq-prd"
            ],  # Enable auto-investigation for both critical DLQs
            claude_command_timeout=1800  # 30 minutes timeout for Claude investigation
        )
        self.monitor = DLQMonitor(config)
        
        # Initialize PR Audio Monitor if enabled
        self.pr_monitor = None
        if enable_pr_monitoring:
            github_token = os.getenv("GITHUB_TOKEN")
            github_username = os.getenv("GITHUB_USERNAME", "fabio.santos")
            
            if github_token:
                self.pr_monitor = PRAudioMonitor(
                    github_token=github_token,
                    github_username=github_username,
                    notification_interval=600,  # 10 minutes
                    enable_audio=True
                )
                print(f"🔔 PR Audio Monitoring: Enabled for {github_username}")
            else:
                print(f"⚠️  PR Audio Monitoring: Disabled (set GITHUB_TOKEN environment variable)")
        
        # Set up signal handlers for graceful shutdown
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
    
    def _signal_handler(self, signum, frame):
        print(f"\n🛑 Received signal {signum}, stopping monitor gracefully...")
        self.running = False
        if self.pr_monitor:
            self.pr_monitor.stop()
    
    def run(self):
        """Run continuous DLQ monitoring with PR audio notifications"""
        print(f"🚀 Starting Production DLQ Monitor for Financial Move")
        print(f"🔑 Profile: FABIO-PROD")
        print(f"🌍 Region: sa-east-1")
        print(f"⏱️  Check Interval: {self.interval}s")
        print(f"🤖 Auto-Investigation: Enabled for fm-digitalguru-api-update-dlq-prod & fm-transaction-processor-dlq-prd")
        print(f"⏰ Investigation Timeout: {self.monitor.config.claude_command_timeout/60:.0f} minutes")
        
        # Start PR monitoring if available
        if self.pr_monitor:
            self.pr_monitor.start_background_monitoring()
            print(f"🔊 PR Audio Notifications: Every 10 minutes for open PRs")
        
        print(f"⏰ Started at: {time.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"{'='*60}")
        print(f"🔄 Press Ctrl+C to stop monitoring")
        print(f"{'='*60}\n")
        
        try:
            while self.running:
                cycle_start = time.time()
                self.cycle_count += 1
                
                print(f"🔍 Cycle {self.cycle_count} - {time.strftime('%H:%M:%S')}")
                
                try:
                    # Check all DLQs
                    alerts = self.monitor.check_dlq_messages()
                    
                    if alerts:
                        print(f"🚨 ACTIVE ALERTS: {len(alerts)} DLQ(s) have messages")
                        for alert in alerts:
                            # Note: _handle_alert is already called inside check_dlq_messages()
                            # Just display the alert info here
                            print(f"   📋 {alert.queue_name}: {alert.message_count} messages")
                    else:
                        print(f"✅ All DLQs clean - no messages found")
                    
                    # Show PR status if monitoring is enabled
                    if self.pr_monitor and self.pr_monitor.tracked_prs:
                        print(f"🔔 Active PRs requiring review: {len(self.pr_monitor.tracked_prs)}")
                        for pr in list(self.pr_monitor.tracked_prs.values())[:3]:  # Show first 3
                            pr_type = "🤖" if pr.is_auto_investigation else "👤"
                            print(f"   {pr_type} PR #{pr.pr_id}: {pr.title[:50]}...")
                
                except Exception as e:
                    print(f"❌ Monitoring error: {e}")
                    # Continue monitoring even if one cycle fails
                
                # Calculate sleep time
                if self.running:
                    cycle_duration = time.time() - cycle_start
                    sleep_time = max(0, self.interval - cycle_duration)
                    
                    if sleep_time > 0:
                        print(f"💤 Next check in {sleep_time:.1f}s...\n")
                        time.sleep(sleep_time)
                    else:
                        print(f"⚠️  Cycle took {cycle_duration:.1f}s (longer than {self.interval}s interval)\n")
                
        except KeyboardInterrupt:
            print(f"\n🛑 Monitor stopped by user after {self.cycle_count} cycles")
        except Exception as e:
            print(f"\n❌ Fatal error: {e}")
        
        print(f"✅ Production monitor shutdown complete")
        print(f"📊 Total cycles completed: {self.cycle_count}")
        print(f"⏰ Stopped at: {time.strftime('%Y-%m-%d %H:%M:%S')}")

def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Production DLQ Monitor for Financial Move with PR Audio Notifications')
    parser.add_argument('--interval', type=int, default=30, 
                       help='Check interval in seconds (default: 30)')
    parser.add_argument('--no-pr-monitoring', action='store_true',
                       help='Disable PR audio monitoring')
    
    args = parser.parse_args()
    
    # Check if GitHub token is set and provide instructions if not
    if not args.no_pr_monitoring and not os.getenv('GITHUB_TOKEN'):
        print("⚠️  GitHub token not set. PR audio notifications will be disabled.")
        print("💡 To enable PR notifications:")
        print("   export GITHUB_TOKEN='your_github_personal_access_token'")
        print("   export GITHUB_USERNAME='your_github_username'")
        print("")
    
    monitor = ProductionMonitor(
        interval=args.interval,
        enable_pr_monitoring=not args.no_pr_monitoring
    )
    monitor.run()

if __name__ == "__main__":
    main()
