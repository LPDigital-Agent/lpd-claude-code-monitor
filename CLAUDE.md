# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

AWS SQS Dead Letter Queue (DLQ) monitoring system with Claude AI auto-investigation capabilities. The system monitors DLQs in AWS accounts, triggers automated investigations when messages are detected, and creates GitHub PRs with fixes.

## Build and Development Commands

### Setup
```bash
# Create virtual environment and install dependencies
make dev              # Full dev setup with pre-commit hooks
make install          # Production dependencies only

# Manual setup
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.template .env  # Configure GitHub and AWS credentials
```

### Testing
```bash
# Run tests with coverage
make test             # Full test suite with coverage report
make test-quick       # Quick tests without coverage
pytest tests/unit/test_specific.py::test_function  # Run single test

# Test specific components
./start_monitor.sh test-claude      # Test Claude Code integration
./start_monitor.sh test-execution   # Test Claude execution
./start_monitor.sh pr-audio-test    # Test PR audio notifications
./start_monitor.sh notification-test # Test macOS notifications
```

### Code Quality
```bash
make lint             # Run ruff and mypy
make format           # Format with black and isort
make qa               # Run format + lint + test
make clean            # Clean build artifacts and cache
```

### Running the Monitor
```bash
# Production monitoring with auto-investigation
./start_monitor.sh production

# Dashboard variants (curses-based terminal UI)
./start_monitor.sh enhanced   # Original enhanced dashboard
./start_monitor.sh ultimate   # Most comprehensive dashboard
./start_monitor.sh fixed      # Fixed enhanced monitor

# CLI interface
dlq-monitor          # Main CLI entry point (after pip install -e .)
dlq-dashboard        # Launch dashboard
dlq-investigate      # Manual investigation
```

## High-Level Architecture

### Package Structure (src-layout)
```
src/dlq_monitor/
├── core/           # Core monitoring engine (AWS SQS polling)
├── claude/         # Claude AI integration layer
├── dashboards/     # Terminal UI dashboards (curses-based)
├── notifiers/      # Notification systems (audio, macOS)
├── utils/          # Utilities (GitHub, production runners)
└── cli.py          # Click-based CLI with Rich formatting
```

### Key Architectural Patterns

#### 1. **Monitoring Loop Architecture**
The system uses a polling-based architecture with state tracking:
- `core/monitor.py` polls AWS SQS queues matching DLQ patterns
- Maintains state in memory and compares with previous iterations
- Triggers actions when thresholds are exceeded
- All monitors inherit this pattern with different UI presentations

#### 2. **Claude Investigation Flow**
Multi-process architecture for auto-investigation:
```python
# Pattern used across claude/ modules
1. DLQ threshold trigger → 
2. Spawn subprocess: claude code --task "investigate" →
3. Track in .claude_sessions.json →
4. Monitor progress via log parsing →
5. Create GitHub PR with fix
```

#### 3. **Dashboard Architecture (Curses-based)**
All dashboards follow a multi-panel pattern:
```python
# Common structure in dashboards/
- Panel layout: DLQs | Agents | PRs | Timeline
- Update loop: refresh every 3 seconds
- State tracking: in-memory with file persistence
- Keyboard handling: q=quit, r=refresh
```

#### 4. **Notification Pipeline**
Layered notification system:
```python
# notifiers/ pattern
Event → Priority Check → Channel Selection → Delivery
- macOS: Native notifications via osascript
- Audio: ElevenLabs TTS or pygame sounds
- PR: GitHub API + audio announcements
```

## Critical Files and Their Roles

### State Management
- `.claude_sessions.json`: Active Claude investigation tracking
- `dlq_monitor_FABIO-PROD_sa-east-1.log`: Main application log
- `.env`: GitHub and AWS credentials (from .env.template)

### Configuration
- `config/config.yaml`: Main configuration (AWS profile, DLQ patterns, thresholds)
- `pyproject.toml`: Package configuration and tool settings
- `setup.cfg`: Additional package metadata

### Entry Points
Console scripts defined in `pyproject.toml`:
- `dlq-monitor`: CLI interface (`cli.py`)
- `dlq-dashboard`: Enhanced dashboard (`dashboards/enhanced.py`)
- `dlq-investigate`: Manual investigation (`claude/manual_investigation.py`)
- `dlq-setup`: GitHub setup utility (`utils/github_setup.py`)

## AWS Integration Details

- **Profile**: FABIO-PROD (configured in AWS CLI)
- **Region**: sa-east-1 (São Paulo)
- **Required Permissions**: `sqs:ListQueues`, `sqs:GetQueueAttributes`
- **DLQ Detection**: Pattern matching on queue names (config.yaml)

## GitHub Integration

- **Token Requirements**: `repo` and `read:org` scopes
- **PR Creation**: Automated via GitHub API
- **Audio Notifications**: ElevenLabs TTS for PR reminders
- **Token Sources**: Environment variable, .env file, or gh CLI

## Claude AI Integration

The system spawns Claude Code CLI as a subprocess:
- Command: `claude code --task "{investigation_prompt}"`
- Working directory: Current repository
- Session tracking: Updates `.claude_sessions.json`
- Timeout: Configurable per investigation type
- Cooldown: Prevents investigation loops

## Development Workflow

### Adding New Features
1. Create feature branch
2. Update relevant module in `src/dlq_monitor/`
3. Add tests in `tests/unit/` or `tests/integration/`
4. Run `make qa` to ensure quality
5. Update documentation if needed

### Modifying Dashboards
Dashboards use curses library - test in different terminal sizes:
- Minimum: 80x24 characters
- Optimal: 120x40 characters
- Color support: 256 colors preferred

### Testing AWS Integration
Use demo mode for local development:
```python
# In config.yaml, demo section simulates DLQ behavior
demo:
  sample_queues: ["payment-dlq", "order-dlq"]
  simulate_realistic_patterns: true
```

## Project Organization Guidelines

- Keep the project organized according to best practices for Python and agent AI projects
- Do not leave files on the root directory
- Maintain a clean and structured project layout