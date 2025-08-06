#!/bin/bash
# Quick kill command for BHiveQ monitoring

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
"$SCRIPT_DIR/stop_all.sh"