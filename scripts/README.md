# Scripts Directory

This directory contains all executable scripts for the LPD Claude Code Monitor project.

## Structure

### `/monitoring/`
Main monitoring and orchestration scripts.
- `adk_monitor.py` - ADK Multi-Agent DLQ Monitor System main entry point

### `/setup/`
Setup and configuration scripts.
- `quick_setup.sh` - Quick setup script for initial configuration

### Root Scripts
- `start_monitor.sh` - Main launcher script for all monitoring modes

## Usage

### Start ADK Monitoring
```bash
./scripts/start_monitor.sh adk-production
```

### Test ADK System
```bash
./scripts/start_monitor.sh adk-test
```

### Quick Setup
```bash
./scripts/setup/quick_setup.sh
```

## Available Commands

The `start_monitor.sh` script provides multiple monitoring modes:

- **Production Monitoring**: `production`, `adk-production`
- **Testing**: `test`, `adk-test`
- **Dashboards**: `enhanced`, `ultimate`, `fixed`
- **CLI Interface**: `cli discover`, `cli monitor`
- **Notifications**: `notification-test`, `voice-test`, `pr-audio-test`
- **Claude Testing**: `test-claude`, `test-execution`
- **Status**: `status`, `logs`

Run `./scripts/start_monitor.sh` without arguments to see all available commands.