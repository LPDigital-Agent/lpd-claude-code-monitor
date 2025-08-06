# Context Window Prime - DLQ Monitor Project

## Purpose
This command primes Claude's context window with essential project knowledge for the LPD Claude Code Monitor system.

## THINKING TOOLS
Activate advanced reasoning capabilities:
- ultrathink
- mcp sequential thinking
- mcp memory
- Context7 for documentation search
- AWS Documentation for service docs
- CloudWatch Logs for advanced analysis
- Lambda Tools for function debugging
- Sequential Thinking for systematic root cause analysis

## RUN COMMANDS
Execute these to understand project state:

```bash
# Project structure overview
git ls-files | head -20
tree -L 2 -I 'venv|__pycache__|*.pyc|.git' 2>/dev/null || find . -type d -maxdepth 2 | grep -v __pycache__ | sort

# Current git state
git status --short
git branch --show-current
git log --oneline -5

# Python environment check
test -d venv && echo "✓ Virtual environment exists" || echo "✗ No virtual environment"
test -f .env && echo "✓ .env configured" || echo "✗ .env missing (copy from .env.template)"

# Available commands
make help 2>/dev/null || echo "Makefile targets available - run 'make help' for details"
grep -E "^[a-zA-Z_-]+:" Makefile | cut -d: -f1 | head -10

# Package entry points
grep -A5 "\[project.scripts\]" pyproject.toml
```

## READ FILES
Load critical project files in priority order:

### 1. PROJECT DOCUMENTATION
Essential understanding of the system:
```
CLAUDE.md                           # Claude-specific guidance
README.md                           # Project overview and quick start
docs/index.md                       # Main documentation hub
```

### 2. CONFIGURATION
How the system is configured:
```
config/config.yaml                  # Main runtime configuration
pyproject.toml                      # Package configuration
setup.cfg                           # Additional package metadata
.env.template                       # Environment variable template
```

### 3. CORE ARCHITECTURE
Key modules that demonstrate the system design:
```
src/dlq_monitor/core/monitor.py    # Core monitoring engine
src/dlq_monitor/claude/session_manager.py  # Claude AI integration
src/dlq_monitor/cli.py             # CLI interface with Rich
src/dlq_monitor/dashboards/ultimate.py     # Most comprehensive dashboard
adk_agents/investigator.py         # Enhanced investigation agent with MCP tools
src/dlq_monitor/utils/aws_sqs_helper.py  # AWS SQS best practices implementation
```

### 4. INTEGRATION POINTS
External system integrations:
```
src/dlq_monitor/utils/github_integration.py  # GitHub PR creation
src/dlq_monitor/notifiers/pr_audio.py       # Audio notification system (Voice: 19STyYD15bswVz51nqLf)
src/dlq_monitor/notifiers/macos_notifier.py # macOS notifications with TTS
config/mcp_settings.json           # MCP server configurations
```

### 5. DEVELOPMENT TOOLS
Build and test infrastructure:
```
Makefile                            # Development automation
scripts/start_monitor.sh            # Main launcher script
tests/conftest.py                   # Test fixtures and configuration
```

### 6. DOCUMENTATION REFERENCES
Best practices and guidelines:
```
https://www.anthropic.com/engineering/claude-code-best-practices
https://docs.anthropic.com/en/docs/build-with-claude/prompt-engineering/chain-of-thought
https://docs.anthropic.com/en/docs/build-with-claude/prompt-engineering/extended-thinking-tips
https://docs.anthropic.com/en/docs/claude-code/sub-agents
```

## PROJECT CONTEXT SUMMARY

### System Purpose
Monitor AWS SQS Dead Letter Queues (DLQs) and automatically investigate issues using Claude AI, creating GitHub PRs with fixes.

### Key Components
1. **AWS Monitoring**: Polls SQS queues for DLQ messages
2. **Claude Integration**: Spawns Claude Code CLI for auto-investigation
3. **GitHub Automation**: Creates PRs with proposed fixes
4. **Dashboard UI**: Multiple curses-based terminal interfaces
5. **Notifications**: macOS alerts and ElevenLabs TTS audio

### Architecture Pattern
- **Polling Loop**: Monitor → Detect → Investigate → Fix → Notify
- **Multi-Process**: Main monitor + Claude subprocesses
- **State Tracking**: JSON files for session management
- **Event-Driven**: Threshold-based triggers

### Development Workflow
```bash
make dev        # Setup development environment
make test       # Run tests with coverage
make qa         # Format + Lint + Test
./start_monitor.sh production  # Run in production mode
```

### Critical Files
- `.claude_sessions.json` - Active investigation tracking
- `dlq_monitor_FABIO-PROD_sa-east-1.log` - Main application log
- `.env` - Credentials (GitHub token, AWS profile)

## CONSTRAINTS & REQUIREMENTS

### AWS
- Profile: FABIO-PROD
- Region: sa-east-1 (São Paulo)
- Permissions: sqs:ListQueues, sqs:GetQueueAttributes

### GitHub
- Token scopes: repo, read:org
- PR creation via API
- Audio notifications for reviews

### Environment
- Python 3.8+
- macOS (for notifications)
- Claude Code CLI installed
- Virtual environment recommended

## MCP TOOLS AVAILABLE
Remember to utilize MCP tools when appropriate:
- mcp memory - For persistent context
- mcp sequential thinking - For complex reasoning
- mcp Context7 - For library documentation and code examples
- mcp AWS Documentation - For AWS service docs and error codes
- mcp CloudWatch Logs - For advanced log analysis with filtering
- mcp Lambda Tools - For Lambda function configuration analysis
- mcp GitHub - For repository operations
- mcp ActiveCampaign - For marketing automation (if needed)

### ENHANCED INVESTIGATION CAPABILITIES
The Investigation Agent now includes:
1. **Context7 Integration**: Search documentation for error patterns
2. **AWS Documentation Lookup**: Find solutions for AWS error codes
3. **CloudWatch Advanced Analysis**: Deep log pattern analysis with insights
4. **Lambda Function Debugging**: Check configurations, timeouts, memory
5. **Sequential Thinking**: Systematic step-by-step root cause analysis

## COMMON TASKS
When asked to work on this project, consider:
1. Check monitoring status: `./start_monitor.sh status`
2. View logs: `tail -f dlq_monitor_*.log`
3. Test changes: `make test-quick`
4. Format code: `make format`
5. Launch dashboard: `./start_monitor.sh ultimate`

---
This prime command provides comprehensive context for effective work on the DLQ Monitor project.