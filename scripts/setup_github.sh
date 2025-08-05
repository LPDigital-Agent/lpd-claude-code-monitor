#!/bin/bash

# GitHub Configuration for DLQ Monitor PR Audio Notifications
# This script sets up the required environment variables

echo "🔧 Setting up GitHub configuration for PR monitoring..."
echo "=================================================="

# GitHub Username (from MCP)
export GITHUB_USERNAME="fabio-lpd"

# Note: We need to create a Personal Access Token
# Since I can't create tokens via MCP, you'll need to do this manually

echo ""
echo "📋 Your GitHub Configuration:"
echo "   Username: fabio-lpd"
echo "   Organization: LPDigital-Agent"
echo ""

# Check if token already exists
if [ -z "$GITHUB_TOKEN" ]; then
    echo "⚠️  GITHUB_TOKEN not set"
    echo ""
    echo "📝 To create a GitHub Personal Access Token:"
    echo ""
    echo "1. Go to: https://github.com/settings/tokens/new"
    echo "2. Give it a name: 'DLQ Monitor PR Notifications'"
    echo "3. Select expiration (recommend: 90 days)"
    echo "4. Select scopes:"
    echo "   ✅ repo (Full control of private repositories)"
    echo "   ✅ read:org (Read org and team membership)"
    echo "   ✅ read:user (Read user profile data)"
    echo "5. Click 'Generate token'"
    echo "6. Copy the token (starts with ghp_)"
    echo ""
    echo "Then run this command with your token:"
    echo "   export GITHUB_TOKEN='ghp_YOUR_TOKEN_HERE'"
    echo ""
    
    # Offer to save to profile
    echo "💡 To make it permanent, add to your shell profile:"
    echo ""
    echo "For zsh (default on macOS):"
    echo "   echo 'export GITHUB_USERNAME=\"fabio-lpd\"' >> ~/.zshrc"
    echo "   echo 'export GITHUB_TOKEN=\"ghp_YOUR_TOKEN_HERE\"' >> ~/.zshrc"
    echo "   source ~/.zshrc"
    echo ""
    echo "For bash:"
    echo "   echo 'export GITHUB_USERNAME=\"fabio-lpd\"' >> ~/.bash_profile"
    echo "   echo 'export GITHUB_TOKEN=\"ghp_YOUR_TOKEN_HERE\"' >> ~/.bash_profile"
    echo "   source ~/.bash_profile"
else
    echo "✅ GITHUB_TOKEN is already set"
    echo "   Token: ${GITHUB_TOKEN:0:10}...${GITHUB_TOKEN: -4}"
fi

echo ""
echo "=================================================="
