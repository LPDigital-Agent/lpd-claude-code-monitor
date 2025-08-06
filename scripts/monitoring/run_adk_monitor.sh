#!/bin/bash
# Run ADK monitor with Blake2 warnings suppressed

# Suppress Python warnings
export PYTHONWARNINGS="ignore::UserWarning"
export PYTHONHASHSEED=0

# Run the monitor
exec python3 scripts/monitoring/adk_monitor.py "$@"