#!/bin/bash
# Run ADK monitor with clean output (no Blake2 warnings)

# Set environment to suppress warnings
export PYTHONWARNINGS="ignore::UserWarning:_blake2"
export AWS_PROFILE=FABIO-PROD
export AWS_REGION=sa-east-1

# Run Python script with warnings suppressed
python3 -W ignore scripts/monitoring/adk_production_monitor.py "$@" 2>&1 | \
    grep -v "blake2" | grep -v "^ERROR:root" | \
    awk '/^WARNING:src.dlq_monitor|^WARNING:__main__|^====|^🚀|^🔑|^🌍|^🤖|^⏱️|^📅|^Press|^🔍|^✅|^📊|^⏰|^📋|^╔|^║|^╠|^╚/ || /^$/ {print}'