#!/bin/bash
# Run ADK monitor with clean output (no Blake2 warnings)

# Run Python script and completely filter out error noise
python3 scripts/monitoring/adk_monitor.py "$@" 2>&1 | \
    awk '/^WARNING:src.dlq_monitor|^WARNING:__main__|^====|^🚀|^🔑|^🌍|^🤖|^⏱️|^📅|^Press|^🔍|^✅|^📊|^⏰/ || /^$/ {print}'