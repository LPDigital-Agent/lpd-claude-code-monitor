#!/usr/bin/env python3
"""
GitHub Integration Setup for DLQ Monitor
Configures GitHub access for PR audio notifications
"""
import os
import subprocess
import json
from pathlib import Path

def setup_github_env():
    """Setup GitHub environment variables"""
    
    print("🔧 GitHub Integration Setup for DLQ Monitor")
    print("=" * 60)
    
    # Your GitHub details (from MCP)
    github_username = "fabio-lpd"
    github_org = "LPDigital-Agent"
    
    print(f"📋 GitHub Account Details:")
    print(f"   Username: {github_username}")
    print(f"   Organization: {github_org}")
    print(f"   Email: fabio@lpdigital.ai")
    print()
    
    # Check current environment
    current_token = os.environ.get('GITHUB_TOKEN', '')
    current_username = os.environ.get('GITHUB_USERNAME', '')
    
    if current_token:
        print(f"✅ GITHUB_TOKEN is set ({len(current_token)} chars)")
        print(f"   Token preview: {current_token[:10]}...{current_token[-4:]}")
    else:
        print("❌ GITHUB_TOKEN not set")
    
    if current_username:
        print(f"✅ GITHUB_USERNAME is set: {current_username}")
    else:
        print(f"⚠️  GITHUB_USERNAME not set, will use: {github_username}")
    
    print()
    
    # Create environment file
    env_file = Path.home() / '.dlq_monitor_env'
    
    print("📝 Creating environment configuration...")
    
    env_content = f"""# DLQ Monitor GitHub Configuration
export GITHUB_USERNAME="{github_username}"
# Add your GitHub Personal Access Token below:
# export GITHUB_TOKEN="ghp_YOUR_TOKEN_HERE"
"""
    
    if not current_token:
        print()
        print("⚠️  GitHub Personal Access Token Required")
        print("-" * 60)
        print()
        print("To create a token:")
        print("1. Open: https://github.com/settings/tokens/new")
        print()
        print("2. Token settings:")
        print("   Name: DLQ Monitor PR Notifications")
        print("   Expiration: 90 days (recommended)")
        print()
        print("3. Select scopes:")
        print("   ✅ repo")
        print("   ✅ read:org")  
        print("   ✅ workflow (if monitoring CI/CD)")
        print("   ✅ read:user")
        print()
        print("4. Generate and copy the token")
        print()
        print("5. Set it in your environment:")
        print(f'   export GITHUB_TOKEN="ghp_YOUR_TOKEN_HERE"')
        print(f'   export GITHUB_USERNAME="{github_username}"')
        print()
        
        # Try to get token interactively
        token_input = input("Paste your GitHub token here (or press Enter to skip): ").strip()
        
        if token_input and token_input.startswith('ghp_'):
            env_content = f"""# DLQ Monitor GitHub Configuration
export GITHUB_USERNAME="{github_username}"
export GITHUB_TOKEN="{token_input}"
"""
            print("✅ Token received and will be saved")
        else:
            print("⏭️  Skipped - you'll need to set it manually")
    else:
        env_content = f"""# DLQ Monitor GitHub Configuration
export GITHUB_USERNAME="{github_username}"
export GITHUB_TOKEN="{current_token}"
"""
    
    # Save environment file
    with open(env_file, 'w') as f:
        f.write(env_content)
    
    print(f"\n✅ Configuration saved to: {env_file}")
    
    # Create a wrapper script
    wrapper_script = Path.cwd() / "start_monitor_with_github.sh"
    
    wrapper_content = f"""#!/bin/bash
# DLQ Monitor with GitHub Integration

# Load GitHub configuration
if [ -f "$HOME/.dlq_monitor_env" ]; then
    source "$HOME/.dlq_monitor_env"
fi

# Verify GitHub token
if [ -z "$GITHUB_TOKEN" ]; then
    echo "⚠️  GITHUB_TOKEN not set"
    echo "Run: python3 setup_github_integration.py"
    exit 1
fi

# Start the monitor
./start_monitor.sh production "$@"
"""
    
    with open(wrapper_script, 'w') as f:
        f.write(wrapper_content)
    
    # Make executable
    subprocess.run(['chmod', '+x', str(wrapper_script)], check=True)
    
    print(f"✅ Created wrapper script: {wrapper_script.name}")
    
    # Update shell profile
    shell = os.environ.get('SHELL', '/bin/zsh')
    
    if 'zsh' in shell:
        profile_file = Path.home() / '.zshrc'
    else:
        profile_file = Path.home() / '.bash_profile'
    
    print()
    print("📋 To make settings permanent, add to your shell profile:")
    print(f"   echo 'source ~/.dlq_monitor_env' >> {profile_file}")
    print(f"   source {profile_file}")
    
    print()
    print("=" * 60)
    print("🚀 Quick Start Commands:")
    print()
    
    if current_token or (token_input and token_input.startswith('ghp_')):
        print("   # Load environment and start monitoring")
        print("   source ~/.dlq_monitor_env")
        print("   ./start_monitor.sh production")
        print()
        print("   # Or use the wrapper script")
        print("   ./start_monitor_with_github.sh")
    else:
        print("   # After setting your token:")
        print(f'   export GITHUB_TOKEN="ghp_YOUR_TOKEN_HERE"')
        print(f'   export GITHUB_USERNAME="{github_username}"')
        print("   ./start_monitor.sh production")
    
    print()
    print("=" * 60)
    
    # Test GitHub access if token is available
    if current_token or (token_input and token_input.startswith('ghp_')):
        test_token = token_input if token_input else current_token
        print()
        print("🧪 Testing GitHub access...")
        
        test_successful = test_github_access(test_token, github_username)
        
        if test_successful:
            print("✅ GitHub integration is ready!")
            print("   PR audio notifications will work")
        else:
            print("⚠️  Could not verify GitHub access")
            print("   Check your token permissions")

def test_github_access(token, username):
    """Test GitHub API access"""
    try:
        import requests
        
        headers = {
            'Authorization': f'token {token}',
            'Accept': 'application/vnd.github.v3+json'
        }
        
        # Test API access
        response = requests.get('https://api.github.com/user', headers=headers, timeout=5)
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Authenticated as: {data.get('login', 'unknown')}")
            
            # Check for PRs
            pr_query = f'is:pr is:open user:{username}'
            pr_response = requests.get(
                f'https://api.github.com/search/issues?q={pr_query}',
                headers=headers,
                timeout=5
            )
            
            if pr_response.status_code == 200:
                pr_data = pr_response.json()
                print(f"✅ Found {pr_data.get('total_count', 0)} open PRs")
                return True
        else:
            print(f"❌ GitHub API returned: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error testing GitHub: {e}")
        return False

if __name__ == "__main__":
    setup_github_env()
