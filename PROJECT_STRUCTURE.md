# Project Structure

## Root Directory
```
lpd-claude-code-monitor/
├── README.md              # Main project documentation
├── CLAUDE.md             # Claude AI context and guidelines
├── LICENSE               # MIT License
├── start.sh              # Main launcher script
├── Makefile              # Build automation
├── pyproject.toml        # Python package configuration
├── setup.cfg             # Python setup configuration
├── requirements.txt      # Python dependencies
├── requirements_adk.txt  # ADK specific dependencies
├── pytest.ini           # Pytest configuration
└── tox.ini              # Tox testing configuration
```

## Core Directories

### `/src` - Python Source Code
```
src/dlq_monitor/
├── core/                 # Core monitoring engine
├── claude/              # Claude AI integration
├── dashboards/          # Terminal UI dashboards
├── notifiers/           # Notification systems
├── services/            # Business logic services
├── utils/               # Utility functions
└── web/                 # Flask web backend
    └── app.py          # API endpoints
```

### `/lpd-neurocenter-next` - Next.js Frontend
```
lpd-neurocenter-next/
├── src/
│   ├── app/            # Next.js app router
│   ├── components/     # React components
│   │   ├── ui/        # Design system components
│   │   ├── layout/    # Layout components
│   │   └── panels/    # Dashboard panels
│   ├── lib/           # Utilities and tokens
│   └── services/      # API services
├── public/            # Static assets
└── package.json       # Node dependencies
```

### `/adk_agents` - Google ADK Agents
```
adk_agents/
├── coordinator.py      # Main coordinator agent
├── investigator.py     # Investigation agent with MCP tools
├── dlq_monitor.py      # DLQ monitoring agent
├── code_fixer.py       # Code fixing agent
├── pr_manager.py       # GitHub PR management
└── notifier.py         # Notification agent
```

### `/scripts` - All Scripts
```
scripts/
├── launch/             # Main launcher scripts
│   ├── start_integrated.sh
│   ├── start_dashboard.sh
│   └── stop_all.sh
├── launchers/          # Component launchers
├── monitoring/         # Monitoring scripts
├── setup/              # Setup and configuration
│   ├── set_ssl_env.sh # SSL environment fix
│   └── fix_ssl.py     # SSL diagnostic
└── web/               # Web-related scripts
```

### `/config` - Configuration Files
```
config/
├── config.yaml         # Main application config
├── adk_config.yaml     # ADK agent configuration
└── mcp_settings.json   # MCP tools configuration
```

### `/docs` - Documentation
```
docs/
├── guides/             # User guides
├── development/        # Developer documentation
├── api/               # API documentation
└── project/           # Project documentation
```

### `/tests` - Test Suite
```
tests/
├── unit/              # Unit tests
├── integration/       # Integration tests
├── validation/        # Validation tests
├── fixtures/          # Test fixtures
└── mocks/            # Mock objects
```

## Quick Start

```bash
# Set up environment
source scripts/setup/set_ssl_env.sh

# Start everything (recommended)
./start.sh

# Or start specific components
./start.sh dashboard      # Web dashboard only
./start.sh neurocenter   # Next.js frontend only
./start.sh stop          # Stop all services
```

## Key Files

- **Flask Backend**: `src/dlq_monitor/web/app.py` (port 5002)
- **Next.js Frontend**: `lpd-neurocenter-next/` (port 3001)
- **ADK Coordinator**: `adk_agents/coordinator.py`
- **Main Config**: `config/config.yaml`
- **SSL Fix**: `scripts/setup/set_ssl_env.sh`

## Development Workflow

1. **Backend Changes**: Edit files in `src/dlq_monitor/`
2. **Frontend Changes**: Edit files in `lpd-neurocenter-next/src/`
3. **Agent Changes**: Edit files in `adk_agents/`
4. **Config Changes**: Edit files in `config/`
5. **Run Tests**: `pytest tests/`
6. **Build**: `make build`

## Ports Used

- **3001**: Next.js NeuroCenter
- **5001**: Original Web Dashboard
- **5002**: Flask Backend API