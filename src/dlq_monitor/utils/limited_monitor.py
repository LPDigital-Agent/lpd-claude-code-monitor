#!/usr/bin/env python3
"""
Limited Production DLQ Monitor
Runs for a specific number of cycles to demonstrate real production monitoring
"""
import sys
import os
import time
import signal
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from dlq_monitor import DLQMonitor, MonitorConfig

class LimitedMonitor:
    def __init__(self, max_cycles=3, interval=30):
        self.max_cycles = max_cycles
        self.interval = interval
        self.cycles_completed = 0
        config = MonitorConfig(
            aws_profile="FABIO-PROD",
            region="sa-east-1",
            check_interval=self.interval
        )
        self.monitor = DLQMonitor(config)
        self.running = True
        
        # Set up signal handlers for graceful shutdown
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
    
    def _signal_handler(self, signum, frame):
        print(f"\n🛑 Received signal {signum}, stopping monitor gracefully...")
        self.running = False
    
    def run(self):
        print(f"🚀 Starting Limited Production DLQ Monitor")
        print(f"📊 Will run for {self.max_cycles} cycles, {self.interval}s interval")
        print(f"🔑 Profile: FABIO-PROD")
        print(f"🌍 Region: sa-east-1")
        print(f"⏰ Starting at: {time.strftime('%H:%M:%S')}\n")
        
        try:
            while self.running and self.cycles_completed < self.max_cycles:
                cycle_start = time.time()
                
                print(f"\n{'='*60}")
                print(f"🔄 CYCLE {self.cycles_completed + 1}/{self.max_cycles} - {time.strftime('%H:%M:%S')}")
                print(f"{'='*60}")
                
                # Run the monitoring check
                alerts = self.monitor.check_dlq_messages()
                
                if alerts:
                    print(f"🚨 Found {len(alerts)} DLQ alerts:")
                    for alert in alerts:
                        self.monitor._handle_alert(alert)
                        print(f"   📋 {alert.queue_name}: {alert.message_count} messages")
                else:
                    print(f"✅ All DLQs are clear - no messages found")
                
                self.cycles_completed += 1
                
                if self.cycles_completed < self.max_cycles and self.running:
                    cycle_duration = time.time() - cycle_start
                    sleep_time = max(0, self.interval - cycle_duration)
                    
                    if sleep_time > 0:
                        print(f"\n💤 Sleeping for {sleep_time:.1f}s until next cycle...")
                        time.sleep(sleep_time)
                
        except KeyboardInterrupt:
            print(f"\n🛑 Monitor stopped by user after {self.cycles_completed} cycles")
        except Exception as e:
            print(f"\n❌ Monitor error: {e}")
        
        print(f"\n✅ Monitor completed {self.cycles_completed} cycles")
        print(f"⏰ Finished at: {time.strftime('%H:%M:%S')}")
        
        return self.cycles_completed

if __name__ == "__main__":
    # Parse command line arguments
    max_cycles = 3
    interval = 30
    
    if len(sys.argv) > 1:
        try:
            max_cycles = int(sys.argv[1])
        except ValueError:
            print("❌ Invalid cycles number, using default: 3")
    
    if len(sys.argv) > 2:
        try:
            interval = int(sys.argv[2])
        except ValueError:
            print("❌ Invalid interval, using default: 30")
    
    monitor = LimitedMonitor(max_cycles=max_cycles, interval=interval)
    monitor.run()
