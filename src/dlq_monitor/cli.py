#!/usr/bin/env python3
"""CLI interface for DLQ Monitor - FABIO-PROD Edition"""

import click
import sys
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.text import Text
from datetime import datetime

console = Console()


@click.group()
def cli():
    """🚨 AWS SQS Dead Letter Queue Monitor - FABIO-PROD Edition"""
    pass


@cli.command()
@click.option('--profile', default='FABIO-PROD', help='AWS profile name', show_default=True)
@click.option('--region', default='sa-east-1', help='AWS region', show_default=True)
@click.option('--interval', default=30, help='Check interval in seconds', show_default=True)
@click.option('--demo', is_flag=True, help='Run in demo mode (no AWS connection)')
def monitor(profile, region, interval, demo):
    """Start DLQ monitoring with prominent queue names"""
    
    if demo:
        console.print(Panel.fit(
            f"[green]Starting DEMO DLQ monitoring[/green]\n"
            f"📋 Profile: {profile}\n"
            f"🌍 Region: {region}\n"
            f"⏱️  Interval: {interval}s\n"
            f"🔔 Queue names will be prominently displayed",
            title="🎭 Demo Mode - FABIO-PROD"
        ))
        
        from demo_dlq_monitor import DemoDLQMonitor, DemoConfig
        
        config = DemoConfig(
            aws_profile=profile,
            region=region,
            check_interval=interval
        )
        
        monitor = DemoDLQMonitor(config)
        monitor.run_demo_monitoring(max_cycles=10)
        
    else:
        console.print(Panel.fit(
            f"[green]Starting PRODUCTION DLQ monitoring[/green]\n"
            f"📋 Profile: {profile}\n"
            f"🌍 Region: {region}\n"
            f"⏱️  Interval: {interval}s\n"
            f"🔔 Queue names will be prominently displayed\n"
            f"📝 Notifications will include queue names\n"
            f"📂 Log: dlq_monitor_{profile}_{region}.log",
            title="🚨 Production Mode - FABIO-PROD"
        ))
        
        try:
            from dlq_monitor import DLQMonitor, MonitorConfig
            
            monitor_config = MonitorConfig(
                aws_profile=profile,
                region=region,
                check_interval=interval
            )
            
            monitor = DLQMonitor(monitor_config)
            monitor.run_continuous_monitoring()
            
        except ImportError as e:
            console.print(f"[red]Error importing production monitor: {e}[/red]")
            console.print("[yellow]Make sure boto3 is installed: pip install boto3[/yellow]")
        except Exception as e:
            console.print(f"[red]Error starting monitor: {e}[/red]")
            console.print("[yellow]Check AWS credentials and connectivity[/yellow]")


@cli.command()
@click.option('--profile', default='FABIO-PROD', help='AWS profile name', show_default=True)
@click.option('--region', default='sa-east-1', help='AWS region', show_default=True)
@click.option('--demo', is_flag=True, help='Use demo data')
def discover(profile, region, demo):
    """Discover all DLQ queues with their names"""
    
    if demo:
        console.print(f"[blue]Demo Discovery - {profile} ({region})[/blue]")
        
        # Demo discovery with realistic FABIO-PROD queues
        demo_queues = [
            {"name": "payment-processing-dlq", "url": f"https://sqs.{region}.amazonaws.com/432817839790/payment-processing-dlq"},
            {"name": "user-notification-deadletter", "url": f"https://sqs.{region}.amazonaws.com/432817839790/user-notification-deadletter"},
            {"name": "order-fulfillment_dlq", "url": f"https://sqs.{region}.amazonaws.com/432817839790/order-fulfillment_dlq"},
            {"name": "email-service-dead-letter", "url": f"https://sqs.{region}.amazonaws.com/432817839790/email-service-dead-letter"},
            {"name": "crypto-transaction-dlq", "url": f"https://sqs.{region}.amazonaws.com/432817839790/crypto-transaction-dlq"},
        ]
        
        table = Table(title=f"DLQ Queues in {profile} ({region})")
        table.add_column("📋 Queue Name", style="cyan", no_wrap=True)
        table.add_column("🔗 Queue URL", style="magenta")
        table.add_column("📊 Messages", style="green")
        
        for queue in demo_queues:
            table.add_row(
                queue['name'],
                queue['url'][:50] + "..." if len(queue['url']) > 50 else queue['url'],
                "0 (demo)"
            )
        
        console.print(table)
        console.print(f"\n[green]✓ Found {len(demo_queues)} DLQ queues[/green]")
        console.print("[yellow]💡 Queue names will be prominently displayed in alerts[/yellow]")
        
    else:
        try:
            from dlq_monitor import DLQMonitor, MonitorConfig
            
            config = MonitorConfig(aws_profile=profile, region=region)
            monitor = DLQMonitor(config)
            
            console.print(f"[blue]Discovering DLQ queues in {profile} ({region})...[/blue]")
            dlq_queues = monitor.discover_dlq_queues()
            
            if dlq_queues:
                table = Table(title=f"DLQ Queues in {profile} ({region})")
                table.add_column("📋 Queue Name", style="cyan", no_wrap=True)
                table.add_column("🔗 Queue URL", style="magenta")
                table.add_column("📊 Messages", style="green")
                
                for queue in dlq_queues:
                    message_count = monitor.get_queue_message_count(queue['url'])
                    status_style = "red" if message_count > 0 else "green"
                    
                    table.add_row(
                        queue['name'],
                        queue['url'][:50] + "..." if len(queue['url']) > 50 else queue['url'],
                        f"[{status_style}]{message_count}[/{status_style}]"
                    )
                
                console.print(table)
                console.print(f"\n[green]✓ Found {len(dlq_queues)} DLQ queues[/green]")
                
                # Show queues with messages
                queues_with_messages = [q for q in dlq_queues if monitor.get_queue_message_count(q['url']) > 0]
                if queues_with_messages:
                    console.print(f"[red]⚠️  {len(queues_with_messages)} queue(s) have messages![/red]")
                    for queue in queues_with_messages:
                        count = monitor.get_queue_message_count(queue['url'])
                        console.print(f"   📋 [red]{queue['name']}[/red]: {count} messages")
                else:
                    console.print("[green]✅ All DLQs are empty[/green]")
                    
            else:
                console.print("[yellow]No DLQ queues found[/yellow]")
                
        except Exception as e:
            console.print(f"[red]Error discovering queues: {e}[/red]")
            console.print("[yellow]Try using --demo flag for demonstration[/yellow]")


@cli.command()
def test_notification():
    """Test Mac notification system with queue name"""
    console.print("🧪 Testing Mac notification system...")
    
    try:
        from dlq_monitor import MacNotifier
        
        notifier = MacNotifier()
        
        # Test with a sample queue name
        test_queue_name = "payment-processing-dlq"
        test_message_count = 5
        
        console.print(f"📋 Testing notification for queue: [cyan]{test_queue_name}[/cyan]")
        
        success = notifier.send_critical_alert(
            test_queue_name,
            test_message_count,
            "sa-east-1"
        )
        
        if success:
            console.print("[green]✓ Notification sent successfully[/green]")
            console.print(f"   📋 Queue name: [cyan]{test_queue_name}[/cyan]")
            console.print(f"   📊 Message count: [yellow]{test_message_count}[/yellow]")
            console.print(f"   🌍 Region: [blue]sa-east-1[/blue]")
        else:
            console.print("[red]✗ Failed to send notification[/red]")
            
    except Exception as e:
        console.print(f"[red]Error testing notifications: {e}[/red]")


@cli.command()
def setup():
    """Setup and validate environment for FABIO-PROD"""
    console.print(Panel.fit(
        "[blue]DLQ Monitor Setup & Validation[/blue]\n[yellow]FABIO-PROD Profile Configuration[/yellow]",
        title="🔧 Setup"
    ))
    
    # Check Python version
    import sys
    console.print(f"✓ Python version: {sys.version}")
    
    # Check required packages
    required_packages = ['boto3', 'click', 'rich']
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
            console.print(f"✓ {package} installed")
        except ImportError:
            console.print(f"✗ {package} missing")
            missing_packages.append(package)
    
    if missing_packages:
        console.print(f"\n[yellow]Install missing packages:[/yellow]")
        console.print(f"pip install {' '.join(missing_packages)}")
    
    # Check AWS CLI and FABIO-PROD profile
    import subprocess
    try:
        result = subprocess.run(['aws', '--version'], capture_output=True, text=True)
        console.print(f"✓ AWS CLI: {result.stdout.strip()}")
        
        # Check FABIO-PROD profile specifically
        try:
            profile_result = subprocess.run([
                'aws', 'configure', 'list', '--profile', 'FABIO-PROD'
            ], capture_output=True, text=True, timeout=10)
            
            if profile_result.returncode == 0:
                console.print("✓ FABIO-PROD profile configured")
                
                # Test SQS access
                try:
                    sqs_test = subprocess.run([
                        'aws', 'sqs', 'list-queues', 
                        '--profile', 'FABIO-PROD', 
                        '--region', 'sa-east-1',
                        '--max-items', '1'
                    ], capture_output=True, text=True, timeout=15)
                    
                    if sqs_test.returncode == 0:
                        console.print("✓ SQS access confirmed for FABIO-PROD")
                    else:
                        console.print(f"⚠️  SQS access test failed: {sqs_test.stderr.strip()}")
                        
                except subprocess.TimeoutExpired:
                    console.print("⚠️  SQS access test timed out")
                except Exception as e:
                    console.print(f"⚠️  SQS access test error: {e}")
                    
            else:
                console.print("✗ FABIO-PROD profile not found or misconfigured")
                console.print("   Configure with: aws configure --profile FABIO-PROD")
                
        except subprocess.TimeoutExpired:
            console.print("⚠️  Profile check timed out")
        except Exception as e:
            console.print(f"⚠️  Could not check FABIO-PROD profile: {e}")
            
    except FileNotFoundError:
        console.print("✗ AWS CLI not found")
    
    # Check macOS
    import platform
    if platform.system() == 'Darwin':
        console.print("✓ macOS detected - notifications supported")
    else:
        console.print("⚠️  Not macOS - notifications may not work")
    
    console.print("\n[blue]Configuration Summary:[/blue]")
    console.print("📋 Default Profile: FABIO-PROD")
    console.print("🌍 Default Region: sa-east-1")
    console.print("🔔 Queue names will be prominently displayed in all alerts")


if __name__ == '__main__':
    cli()
