#!/usr/bin/env python3
"""
Enhanced Demo DLQ Monitor - Shows DLQ queue names prominently
Simulates FABIO-PROD profile in sa-east-1 region
"""

import time
import logging
import subprocess
import random
from datetime import datetime
from dataclasses import dataclass
from typing import List, Dict


@dataclass
class DLQAlert:
    queue_name: str
    queue_url: str
    message_count: int
    timestamp: datetime
    region: str = "sa-east-1"
    account_id: str = "432817839790"


@dataclass
class DemoConfig:
    aws_profile: str = "FABIO-PROD"
    region: str = "sa-east-1"
    check_interval: int = 10  # Faster for demo
    dlq_patterns: List[str] = None
    notification_sound: bool = True
    
    def __post_init__(self):
        if self.dlq_patterns is None:
            self.dlq_patterns = ["-dlq", "-dead-letter", "-deadletter", "_dlq"]


class MacNotifier:
    """Handle macOS notifications - Demo version with prominent queue names"""
    
    @staticmethod
    def send_notification(title: str, message: str, sound: bool = True) -> bool:
        """Send notification via macOS Notification Center"""
        try:
            cmd = [
                "osascript", "-e",
                f'display notification "{message}" with title "{title}"'
            ]
            
            subprocess.run(cmd, check=True, capture_output=True)
            print(f"📱 NOTIFICATION SENT: {title}")
            print(f"   📝 Message: {message.replace(chr(92)+'n', ' | ')}")
            return True
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to send notification: {e}")
            return False
    
    @staticmethod
    def send_critical_alert(queue_name: str, message_count: int, region: str = "sa-east-1") -> bool:
        """Send critical alert with prominent queue name"""
        title = f"🚨 DLQ ALERT - {queue_name}"
        message = f"Profile: FABIO-PROD\\nRegion: {region}\\nQueue: {queue_name}\\nMessages: {message_count}"
        
        # Announce queue name
        print(f"🔊 ANNOUNCING: Dead letter queue alert for {queue_name}")
        
        return MacNotifier.send_notification(title, message, sound=True)


class DemoDLQMonitor:
    """Demo DLQ Monitor - Simulates FABIO-PROD behavior with queue names"""
    
    def __init__(self, config: DemoConfig):
        self.config = config
        self.logger = self._setup_logging()
        self.notifier = MacNotifier()
        self.last_alerts: Dict[str, datetime] = {}
        self.cycle_count = 0
        
        # Demo data - realistic DLQ queues from FABIO-PROD
        self.demo_queues = [
            {
                "name": "payment-processing-dlq", 
                "url": f"https://sqs.{config.region}.amazonaws.com/432817839790/payment-processing-dlq"
            },
            {
                "name": "user-notification-deadletter", 
                "url": f"https://sqs.{config.region}.amazonaws.com/432817839790/user-notification-deadletter"
            },
            {
                "name": "order-fulfillment_dlq", 
                "url": f"https://sqs.{config.region}.amazonaws.com/432817839790/order-fulfillment_dlq"
            },
            {
                "name": "email-service-dead-letter", 
                "url": f"https://sqs.{config.region}.amazonaws.com/432817839790/email-service-dead-letter"
            },
            {
                "name": "crypto-transaction-dlq", 
                "url": f"https://sqs.{config.region}.amazonaws.com/432817839790/crypto-transaction-dlq"
            },
        ]
        
    def _setup_logging(self) -> logging.Logger:
        """Configure structured logging"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - [QUEUE: %(queue_name)s] - %(message)s',
            handlers=[
                logging.FileHandler(f'demo_dlq_monitor_{self.config.aws_profile}_{self.config.region}.log'),
                logging.StreamHandler()
            ]
        )
        return logging.getLogger(__name__)
    
    def _is_dlq(self, queue_name: str) -> bool:
        """Check if queue name matches DLQ patterns"""
        return any(pattern in queue_name.lower() for pattern in self.config.dlq_patterns)
    
    def discover_dlq_queues(self) -> List[Dict[str, str]]:
        """Simulate discovering DLQ queues"""
        print(f"🔍 Discovering DLQ queues in {self.config.aws_profile} ({self.config.region})...")
        time.sleep(1)  # Simulate API call
        
        print(f"✅ Found {len(self.demo_queues)} DLQ queues:")
        for queue in self.demo_queues:
            print(f"   📋 {queue['name']}")
        
        self.logger.info(f"Discovered {len(self.demo_queues)} DLQ queues")
        return self.demo_queues
    
    def get_queue_message_count(self, queue_url: str) -> int:
        """Simulate getting message count with realistic patterns"""
        queue_name = queue_url.split('/')[-1]
        
        # Simulate different scenarios based on cycle
        if self.cycle_count < 3:
            return 0
        elif self.cycle_count == 3:
            if "payment" in queue_name:
                return random.randint(1, 5)
            return 0
        elif self.cycle_count == 5:
            if "email" in queue_name:
                return random.randint(2, 8)
            elif "payment" in queue_name:
                return random.randint(0, 2)
            return 0
        elif self.cycle_count == 7:
            if "crypto" in queue_name:
                return random.randint(3, 10)
            return 0
        else:
            # Random behavior
            if random.random() < 0.25:  # 25% chance
                return random.randint(1, 12)
            return 0
    
    def check_dlq_messages(self) -> List[DLQAlert]:
        """Check all DLQs for messages and return alerts with queue names"""
        print(f"\n🔄 Monitoring cycle {self.cycle_count + 1} - {datetime.now().strftime('%H:%M:%S')}")
        print(f"📋 Profile: {self.config.aws_profile} | 🌍 Region: {self.config.region}")
        
        dlq_queues = self.discover_dlq_queues()
        alerts = []
        
        print(f"\n📊 Checking message counts:")
        for queue in dlq_queues:
            message_count = self.get_queue_message_count(queue['url'])
            queue_name = queue['name']
            
            if message_count > 0:
                print(f"   ⚠️  📋 {queue_name}: {message_count} messages")
            else:
                print(f"   ✅ 📋 {queue_name}: {message_count} messages")
            
            if message_count > 0:
                alert = DLQAlert(
                    queue_name=queue_name,
                    queue_url=queue['url'],
                    message_count=message_count,
                    timestamp=datetime.now(),
                    region=self.config.region
                )
                alerts.append(alert)
                
                # Handle alert with prominent queue name
                self._handle_alert(alert)
        
        if not alerts:
            print("   ✅ All DLQs are empty")
        
        self.cycle_count += 1
        return alerts
    
    def _handle_alert(self, alert: DLQAlert) -> None:
        """Handle DLQ alert with prominent queue name display"""
        queue_name = alert.queue_name
        
        # Check cooldown
        should_notify = (
            queue_name not in self.last_alerts or
            (datetime.now() - self.last_alerts[queue_name]).seconds > 60  # 1 min for demo
        )
        
        if should_notify:
            print(f"\n🚨 DLQ ALERT TRIGGERED 🚨")
            print(f"📋 QUEUE NAME: {queue_name}")
            print(f"📊 MESSAGE COUNT: {alert.message_count}")
            print(f"🌍 REGION: {alert.region}")
            print(f"⏰ TIMESTAMP: {alert.timestamp.strftime('%H:%M:%S')}")
            
            self.notifier.send_critical_alert(queue_name, alert.message_count, alert.region)
            self.last_alerts[queue_name] = alert.timestamp
            
            # Log with queue name emphasis
            extra = {'queue_name': queue_name}
            self.logger.warning(
                f"DLQ Alert: {queue_name} has {alert.message_count} messages",
                extra={
                    'queue_name': queue_name,
                    'queue_url': alert.queue_url,
                    'message_count': alert.message_count,
                    'timestamp': alert.timestamp.isoformat()
                }
            )
            print(f"📱 Mac notification sent for queue: {queue_name}")
            print("=" * 60)
    
    def run_demo_monitoring(self, max_cycles: int = 10) -> None:
        """Run demo monitoring with prominent queue name display"""
        print(f"🚀 Starting DEMO DLQ monitoring")
        print(f"📋 AWS Profile: {self.config.aws_profile}")
        print(f"🌍 Region: {self.config.region}")
        print(f"⏱️  Check interval: {self.config.check_interval} seconds")
        print(f"🔢 Demo cycles: {max_cycles}")
        print("=" * 80)
        
        try:
            for cycle in range(max_cycles):
                try:
                    alerts = self.check_dlq_messages()
                    
                    if alerts:
                        print(f"\n⚠️  Found {len(alerts)} DLQ(s) with messages:")
                        for alert in alerts:
                            print(f"   📋 {alert.queue_name}: {alert.message_count} messages")
                        self.logger.info(f"Found {len(alerts)} DLQ(s) with messages")
                    else:
                        print(f"\n✅ All DLQs empty this cycle")
                        self.logger.info("All DLQs are empty")
                    
                    if cycle < max_cycles - 1:
                        print(f"\n⏳ Waiting {self.config.check_interval} seconds until next check...")
                        time.sleep(self.config.check_interval)
                    
                except KeyboardInterrupt:
                    print("\n🛑 Demo monitoring stopped by user")
                    break
                except Exception as e:
                    print(f"❌ Error during monitoring cycle: {e}")
                    self.logger.error(f"Error during monitoring cycle: {e}")
                    
        except Exception as e:
            print(f"💥 Critical error in monitoring loop: {e}")
            self.logger.error(f"Critical error in monitoring loop: {e}")
            raise
        
        print("=" * 80)
        print("🏁 Demo monitoring completed!")
        print(f"📊 Total cycles run: {self.cycle_count}")
        print(f"🚨 Total unique queues alerted: {len(self.last_alerts)}")
        
        if self.last_alerts:
            print("🎯 Queues that generated alerts:")
            for queue_name, timestamp in self.last_alerts.items():
                print(f"   📋 {queue_name} (last alert: {timestamp.strftime('%H:%M:%S')})")
        
        print(f"\n📝 Log file: demo_dlq_monitor_{self.config.aws_profile}_{self.config.region}.log")


def main():
    """Main entry point for demo"""
    print("🎭 DLQ Monitor Demo - FABIO-PROD Edition")
    print("Simulates AWS SQS monitoring with prominent queue names")
    print()
    
    config = DemoConfig(
        aws_profile="FABIO-PROD",
        region="sa-east-1",
        check_interval=5,  # Faster for demo
        notification_sound=True
    )
    
    monitor = DemoDLQMonitor(config)
    monitor.run_demo_monitoring(max_cycles=8)


if __name__ == "__main__":
    main()
