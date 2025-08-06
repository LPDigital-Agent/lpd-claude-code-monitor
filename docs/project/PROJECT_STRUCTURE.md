# Project Structure

This document describes the organization of the LPD Claude Code Monitor project following Python and AI agent development best practices.

## Directory Layout

```
lpd-claude-code-monitor/
├── adk_agents/              # ADK Multi-Agent System components
│   ├── __init__.py
│   ├── coordinator.py       # Main orchestrator agent
│   ├── dlq_monitor.py       # DLQ monitoring agent
│   ├── investigator.py      # Root cause analysis agent
│   ├── code_fixer.py        # Code fix implementation agent
│   ├── pr_manager.py        # GitHub PR management agent
│   └── notifier.py          # Notification agent
│
├── .claude/                 # Claude AI configurations
│   └── agents/              # Claude subagent definitions
│       ├── dlq-analyzer.md
│       ├── debugger.md
│       └── code-reviewer.md
│
├── config/                  # Configuration files
│   ├── config.yaml          # Main DLQ monitor config
│   ├── adk_config.yaml      # ADK system configuration
│   └── mcp_settings.json    # MCP server configurations
│
├── src/                     # Source code (src-layout)
│   └── dlq_monitor/         # Main package
│       ├── core/            # Core monitoring engine
│       ├── claude/          # Claude AI integration
│       ├── dashboards/      # Terminal UI dashboards
│       ├── notifiers/       # Notification systems
│       ├── utils/           # Utilities
│       └── cli.py           # CLI interface
│
├── scripts/                 # Executable scripts
│   ├── monitoring/          # Monitoring scripts
│   │   └── adk_monitor.py   # ADK system entry point
│   ├── setup/               # Setup and configuration
│   │   └── quick_setup.sh   # Quick setup script
│   └── start_monitor.sh     # Main launcher script
│
├── tests/                   # Test suites
│   ├── unit/                # Unit tests
│   ├── integration/         # Integration tests
│   │   └── test_adk_system.py
│   └── validation/          # Validation tests
│       └── test_adk_simple.py
│
├── docs/                    # Documentation
│   ├── api/                 # API documentation
│   ├── guides/              # User guides
│   └── development/         # Developer documentation
│
├── log/                     # Application logs
├── .github/                 # GitHub workflows and actions
└── venv/                    # Virtual environment (excluded from git)
```

## Key Files

### Configuration
- `.env` - Environment variables (not in git)
- `.env.template` - Template for environment setup
- `pyproject.toml` - Package configuration
- `setup.cfg` - Additional package metadata
- `requirements*.txt` - Dependency specifications

### Documentation
- `README.md` - Project overview
- `CLAUDE.md` - Claude AI guidance
- `CHANGELOG.md` - Version history
- `PROJECT_STRUCTURE.md` - This file

### Build & Development
- `Makefile` - Build automation
- `pytest.ini` - Test configuration
- `tox.ini` - Test environment configuration
- `.pre-commit-config.yaml` - Pre-commit hooks

## Best Practices Applied

### 1. **Python Package Structure**
- Uses `src-layout` for clear separation
- Package code isolated in `src/dlq_monitor/`
- Tests outside of package directory
- Configuration separated from code

### 2. **AI Agent Organization**
- Dedicated `adk_agents/` for multi-agent system
- Claude subagents in `.claude/agents/`
- MCP configurations centralized
- Clear agent responsibility separation

### 3. **Script Organization**
- Scripts categorized by purpose
- Monitoring scripts separate from setup
- Main launcher remains accessible
- Clear script documentation

### 4. **Test Structure**
- Tests organized by type (unit/integration/validation)
- Clear test naming conventions
- Separate test configurations
- Documentation for test execution

### 5. **Configuration Management**
- All configs in dedicated directory
- Environment variables via `.env`
- YAML for complex configurations
- JSON for MCP server settings

### 6. **Documentation**
- Comprehensive README files
- API documentation separate
- Developer guides available
- Clear project structure documentation

## Development Workflow

1. **Setup Environment**
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   pip install -e .
   ```

2. **Configure Settings**
   ```bash
   cp .env.template .env
   # Edit .env with your API keys
   ```

3. **Run Tests**
   ```bash
   make test
   python tests/validation/test_adk_simple.py
   ```

4. **Start Monitoring**
   ```bash
   ./scripts/start_monitor.sh adk-production
   ```

## Excluded from Repository

The following are excluded via `.gitignore`:
- Virtual environments (`venv/`, `venv_new/`)
- Python cache (`__pycache__/`, `*.pyc`)
- Environment files (`.env`)
- Log files (`*.log`)
- Build artifacts (`dist/`, `build/`, `*.egg-info`)
- IDE configurations (`.vscode/`, `.idea/`)
- Test coverage reports (`.coverage`, `htmlcov/`)

## Maintenance

- Keep agent code in `adk_agents/`
- Place new scripts in appropriate `scripts/` subdirectory
- Add tests to corresponding `tests/` subdirectory
- Update documentation when adding features
- Follow existing naming conventions