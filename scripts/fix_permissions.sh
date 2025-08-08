#!/bin/bash

# Fix permissions for all scripts in the project
echo "🔧 Fixing script permissions..."

# Make all shell scripts executable
find . -name "*.sh" -type f -exec chmod +x {} \;

# Make Python scripts in scripts/ executable
find scripts/ -name "*.py" -type f -exec chmod +x {} \;

# Make specific monitoring scripts executable
chmod +x scripts/start_monitor.sh
chmod +x scripts/monitoring/adk_monitor.py
chmod +x scripts/setup/quick_setup.sh
chmod +x scripts/check_status.sh
chmod +x scripts/setup_github.sh
chmod +x scripts/setup_pr_audio.sh
chmod +x scripts/make_executable.sh

echo "✅ All script permissions fixed!"
echo ""
echo "You can now run:"
echo "  ./scripts/start_monitor.sh adk-production"