# Command Reference

## Monitor Commands

### Production Monitoring

#### `./start_monitor.sh production`
Start production DLQ monitoring with Claude AI auto-investigation.
- Monitors all DLQ queues
- Triggers Claude investigations automatically
- Creates GitHub PRs with fixes
- Runs continuously until stopped

#### `./start_monitor.sh adk-production`
Start ADK multi-agent monitoring with MCP tools.
- Uses Google ADK framework
- Enhanced with 5 special MCP tools
- Multi-agent coordination
- Advanced investigation capabilities

### Dashboard Commands

#### `./start_monitor.sh enhanced`
Launch the enhanced terminal dashboard.
- Real-time multi-panel interface
- Shows DLQs, agents, PRs, and timeline
- Curses-based terminal UI
- Keyboard shortcuts: q=quit, r=refresh

#### `./start_monitor.sh ultimate`
Launch the most comprehensive dashboard.
- All features of enhanced dashboard
- Additional monitoring metrics
- Extended timeline view

#### `./start_monitor.sh fixed`
Launch the fixed enhanced monitor.
- Stable version of enhanced dashboard
- Bug fixes and improvements

### Testing Commands

#### `./start_monitor.sh test`
Run in test mode (3 cycles).
- Limited run for testing
- Exits after 3 monitoring cycles
- Useful for validation

#### `./start_monitor.sh adk-test`
Test ADK multi-agent system.
- Validates ADK configuration
- Tests MCP tool connections
- Runs limited cycles

#### `./start_monitor.sh test-claude`
Test Claude Code integration.
- Validates Claude CLI is installed
- Tests investigation triggering
- Checks session tracking

#### `./start_monitor.sh test-execution`
Test Claude execution flow.
- Full investigation test
- Subprocess spawning validation
- Log parsing verification

### Notification Testing

#### `./start_monitor.sh notification-test`
Test macOS notifications.
- Sends test notification
- Validates notification permissions
- Tests sound alerts

#### `./start_monitor.sh pr-audio-test`
Test PR audio notifications.
- Tests ElevenLabs TTS
- Validates voice ID configuration
- Plays sample PR reminder

### Discovery Commands

#### `./start_monitor.sh discover`
Discover all DLQ queues in AWS account.
- Lists all queues matching DLQ patterns
- Shows message counts
- Displays queue attributes

### CLI Interface Commands

#### `./start_monitor.sh cli monitor`
Start CLI monitoring interface.
- Text-based monitoring
- No curses UI
- Simple output format

## Python CLI Commands

After installation with `pip install -e .`, these commands are available:

### Main Commands

#### `dlq-monitor`
Main CLI entry point.
- Rich formatted output
- Subcommands for different operations
- Help: `dlq-monitor --help`

#### `dlq-dashboard`
Launch the enhanced dashboard directly.
- Same as `./start_monitor.sh enhanced`
- Terminal UI interface

#### `dlq-investigate`
Trigger manual investigation.
- Investigates specific DLQ
- Interactive prompts
- Creates GitHub PR

#### `dlq-production`
Start production monitoring.
- Direct Python entry point
- Production configuration

#### `dlq-limited`
Start limited monitoring.
- Reduced feature set
- Lower resource usage

#### `dlq-ultimate`
Launch ultimate dashboard.
- Direct Python entry point
- All features enabled

#### `dlq-corrections`
Launch corrections dashboard.
- Specialized for error corrections
- Focus on fix tracking

#### `dlq-fixed`
Launch fixed enhanced dashboard.
- Stable version
- Direct Python entry point

#### `dlq-live`
Start live monitoring.
- Real-time updates
- Minimal UI

#### `dlq-status`
Check system status.
- Shows active investigations
- Lists current DLQs
- Displays PR status

#### `dlq-setup`
GitHub setup utility.
- Configure GitHub integration
- Validate token
- Set repository settings

## Validation Commands

### System Validation

#### `python tests/validation/test_adk_simple.py`
Run complete system validation.
- Checks environment variables
- Validates configuration files
- Tests agent files
- Verifies MCP servers
- Tests ADK package
- Validates scripts

Expected output:
```
🎉 All tests passed! System components are ready.
```

### Component Testing

#### Test AWS Connection
```bash
aws sqs list-queues --profile FABIO-PROD --region sa-east-1
```

#### Test GitHub Authentication
```bash
gh auth status
```

#### Test Gemini API
```bash
python -c "import google.generativeai as genai; import os; genai.configure(api_key=os.getenv('GEMINI_API_KEY')); print('✅ Gemini OK')"
```

#### Test Google ADK
```bash
python -c "from google.adk import Agent, Runner; print('✅ ADK OK')"
```

## Environment Setup Commands

### Export GitHub Token
```bash
export GITHUB_TOKEN=$(gh auth token 2>/dev/null)
```

### Load Environment Variables
```bash
source .env
```

### Activate Virtual Environment
```bash
source venv/bin/activate
```

## Installation Commands

### Quick Setup
```bash
./scripts/setup/quick_setup.sh
```

### Manual Installation
```bash
# Create virtual environment
python3.11 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
pip install google-adk google-generativeai
pip install -r requirements_adk.txt
pip install -e .
```

## Makefile Commands

### Development
- `make dev` - Full dev setup with pre-commit hooks
- `make install` - Production dependencies only

### Testing
- `make test` - Full test suite with coverage
- `make test-quick` - Quick tests without coverage

### Code Quality
- `make lint` - Run ruff and mypy
- `make format` - Format with black and isort
- `make qa` - Run format + lint + test
- `make clean` - Clean build artifacts and cache

## Background Execution

### Using nohup
```bash
nohup ./start_monitor.sh adk-production > monitor.log 2>&1 &
```

### Using screen
```bash
screen -S adk-monitor
./start_monitor.sh adk-production
# Detach: Ctrl+A, D
# Reattach: screen -r adk-monitor
```

### Using tmux
```bash
tmux new -s adk-monitor
./start_monitor.sh adk-production
# Detach: Ctrl+B, D
# Reattach: tmux attach -t adk-monitor
```

## Log Files

### View Logs
```bash
# Main application log
tail -f dlq_monitor_FABIO-PROD_sa-east-1.log

# ADK monitor log
tail -f logs/adk_monitor.log

# Claude sessions
cat .claude_sessions.json | jq .
```

### Clear Logs
```bash
# Clear all logs
rm -f *.log logs/*.log

# Clear Claude sessions
echo "{}" > .claude_sessions.json
```

## Keyboard Shortcuts

### Dashboard Controls
- `q` - Quit application
- `r` - Refresh display
- `↑/↓` - Navigate panels
- `Enter` - Select item
- `Esc` - Cancel operation

## Exit Codes

- `0` - Success
- `1` - General error
- `2` - Configuration error
- `3` - AWS connection error
- `4` - GitHub authentication error
- `5` - Gemini API error