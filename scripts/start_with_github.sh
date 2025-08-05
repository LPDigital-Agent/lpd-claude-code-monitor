#!/bin/bash
# Start DLQ Monitor with GitHub PR Audio Notifications

# Set GitHub credentials
export GITHUB_USERNAME="fabio-lpd"
# Note: For security, we're using the gh CLI to get the token dynamically
export GITHUB_TOKEN=$(gh auth token 2>/dev/null)

# Check if token was retrieved successfully
if [ -z "$GITHUB_TOKEN" ]; then
    echo "⚠️  Failed to retrieve GitHub token from gh CLI"
    echo "   Please ensure you're logged in with: gh auth login"
    echo "   Or set the token manually: export GITHUB_TOKEN='your_token'"
    exit 1
fi

echo "✅ GitHub credentials configured:"
echo "   Username: $GITHUB_USERNAME"
echo "   Token: [REDACTED - Retrieved from gh CLI]"
echo ""

# Navigate to project directory
cd "/Users/fabio.santos/LPD Repos/lpd-claude-code-monitor"

# Activate virtual environment
if [ -d "venv" ]; then
    source venv/bin/activate
else
    echo "Creating virtual environment..."
    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
fi

# Start the monitor with the provided arguments
echo "🚀 Starting DLQ Monitor with PR Audio Notifications..."
echo "===================================================="
python run_production_monitor.py "$@"
