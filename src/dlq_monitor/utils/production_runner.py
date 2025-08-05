#!/usr/bin/env python3
"""
Production DLQ Monitor Runner
Automatically activates virtual environment and runs production monitoring
"""

import os
import sys
import subprocess
import time
from pathlib import Path


def activate_venv_and_run():
    """Activate virtual environment and run production monitor"""
    
    # Get script directory
    script_dir = Path(__file__).parent.absolute()
    venv_path = script_dir / "venv"
    python_path = venv_path / "bin" / "python3"
    
    print("🚀 DLQ Monitor - Production Mode")
    print(f"📂 Working directory: {script_dir}")
    
    # Check if virtual environment exists
    if not venv_path.exists():
        print("❌ Virtual environment not found!")
        print("   Run: python3 -m venv venv && pip install -r requirements.txt")
        sys.exit(1)
    
    # Check if python exists in venv
    if not python_path.exists():
        print("❌ Python not found in virtual environment!")
        sys.exit(1)
    
    print(f"✅ Using Python: {python_path}")
    
    # Prepare environment
    env = os.environ.copy()
    env['VIRTUAL_ENV'] = str(venv_path)
    env['PATH'] = f"{venv_path / 'bin'}:{env['PATH']}"
    
    try:
        print("🔍 Starting DLQ monitoring for FABIO-PROD profile...")
        print("⏱️  Check interval: 30 seconds")
        print("🔔 Mac notifications: Enabled")
        print("📊 Logging: dlq_monitor_FABIO-PROD.log")
        print("=" * 60)
        
        # Run the production monitor
        subprocess.run([
            str(python_path), 
            "dlq_monitor.py"
        ], cwd=script_dir, env=env, check=True)
        
    except KeyboardInterrupt:
        print("\n🛑 Monitoring stopped by user")
    except subprocess.CalledProcessError as e:
        print(f"\n❌ Error running monitor: {e}")
        print("\n💡 Troubleshooting:")
        print("   1. Check AWS credentials: aws configure list --profile FABIO-PROD")
        print("   2. Test AWS access: aws sqs list-queues --profile FABIO-PROD --region sa-east-1")
        print("   3. Run setup check: ./start_monitor.sh cli.py setup")
    except Exception as e:
        print(f"\n💥 Unexpected error: {e}")


if __name__ == "__main__":
    activate_venv_and_run()
