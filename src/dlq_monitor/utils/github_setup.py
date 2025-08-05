#!/usr/bin/env python3
"""
Quick GitHub setup for DLQ Monitor
Sets environment variables for the current session
"""
import os
import sys

# Your GitHub details
GITHUB_USERNAME = "fabio-lpd"
GITHUB_ORG = "LPDigital-Agent"

print("🔧 Quick GitHub Setup for DLQ Monitor")
print("=" * 60)
print()
print(f"GitHub Username: {GITHUB_USERNAME}")
print(f"Organization: {GITHUB_ORG}")
print()

# Set for current session
os.environ['GITHUB_USERNAME'] = GITHUB_USERNAME

print("✅ GITHUB_USERNAME set for current session")
print()
print("⚠️  You still need a GitHub Personal Access Token")
print()
print("📝 Quick Setup Instructions:")
print("-" * 40)
print()
print("1. Create a token at:")
print("   https://github.com/settings/tokens/new")
print()
print("2. Required permissions:")
print("   • repo (for PR access)")
print("   • read:org (for organization repos)")
print()
print("3. After creating, run this command:")
print("   export GITHUB_TOKEN='ghp_YOUR_TOKEN_HERE'")
print()
print("4. Then start the monitor:")
print("   ./start_monitor.sh production")
print()
print("=" * 60)
print()
print("💡 Alternative: Create a .env file")
print("-" * 40)
print()
print("Create a file called '.env' in the lpd-claude-code-monitor directory:")
print()
print(f"GITHUB_USERNAME={GITHUB_USERNAME}")
print("GITHUB_TOKEN=ghp_YOUR_TOKEN_HERE")
print()

# Create a sample .env file
env_template = f"""# GitHub Configuration for DLQ Monitor
GITHUB_USERNAME={GITHUB_USERNAME}
GITHUB_TOKEN=ghp_YOUR_TOKEN_HERE

# Instructions:
# 1. Replace ghp_YOUR_TOKEN_HERE with your actual GitHub token
# 2. Get a token from: https://github.com/settings/tokens/new
# 3. Save this file as .env in the lpd-claude-code-monitor directory
"""

with open('.env.template', 'w') as f:
    f.write(env_template)

print("✅ Created .env.template file")
print("   Copy it to .env and add your token")
print()

# Create a modified start script that loads .env
start_script = """#!/bin/bash

# Load environment variables from .env if it exists
if [ -f ".env" ]; then
    export $(cat .env | grep -v '^#' | xargs)
    echo "✅ Loaded GitHub configuration from .env"
fi

# Check if GitHub token is set
if [ -z "$GITHUB_TOKEN" ]; then
    echo "⚠️  GITHUB_TOKEN not set"
    echo ""
    echo "Options:"
    echo "1. Set token: export GITHUB_TOKEN='ghp_YOUR_TOKEN'"
    echo "2. Create .env file with GITHUB_TOKEN=ghp_YOUR_TOKEN"
    echo "3. Run without PR monitoring (DLQ monitoring will still work)"
    echo ""
    read -p "Continue without GitHub integration? (y/n): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
else
    echo "✅ GitHub token configured"
fi

# Set username if not already set
if [ -z "$GITHUB_USERNAME" ]; then
    export GITHUB_USERNAME="fabio-lpd"
fi

# Run the original start script
./start_monitor.sh "$@"
"""

with open('start_with_github.sh', 'w') as f:
    f.write(start_script)

os.chmod('start_with_github.sh', 0o755)

print("✅ Created start_with_github.sh script")
print()
print("🚀 Usage:")
print("   1. Copy .env.template to .env")
print("   2. Add your GitHub token to .env")
print("   3. Run: ./start_with_github.sh production")
print()
print("This will automatically load your GitHub credentials!")
