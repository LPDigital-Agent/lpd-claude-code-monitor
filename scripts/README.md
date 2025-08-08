# Scripts Directory

Organized scripts for the LPD Claude Code Monitor project following Python and AI Agent best practices.

## Directory Structure

```
scripts/
├── launch/              # Main application launchers
│   ├── neurocenter.sh      # BHiveQ NeuroCenter dashboard
│   └── neurocenter_clean.sh # Clean version (suppresses warnings)
│
├── launchers/           # Web dashboard launchers
│   ├── dashboard.sh        # Terminal dashboard
│   ├── start_web_clean.sh  # Web dashboard (clean)
│   ├── start_web_dashboard.sh # Web dashboard
│   └── web.sh              # Simple web launcher
│
├── monitoring/          # ADK and monitoring scripts
│   ├── adk_monitor.py      # ADK Multi-Agent DLQ Monitor System
│   ├── adk_monitor_wrapper.py # ADK wrapper
│   ├── run_adk_monitor.sh  # ADK launcher
│   └── run_clean.sh        # Clean runner
│
├── web/                 # Web-related Python runners
│   ├── run_neurocenter.py  # NeuroCenter Python runner
│   ├── run_silent.py       # Silent web runner
│   ├── run_web.py          # Standard web runner
│   └── start_web.py        # Web starter
│
├── setup/              # Setup and configuration scripts
│   └── quick_setup.sh      # Quick setup script for initial configuration
│
└── Root Scripts
    ├── start_monitor.sh    # Main launcher script for all monitoring modes
    ├── stop_all.sh        # Stop all running services
    └── check_status.sh    # Check service status
```

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