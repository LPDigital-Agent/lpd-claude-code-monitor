# 🐝 BHiveQ Observability Hub - LPD Digital Hive

> Enterprise-grade AWS SQS Dead Letter Queue monitoring with Claude AI multi-agent investigation, automated PR generation, and real-time observability dashboard

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue)](https://www.python.org/)
[![AWS](https://img.shields.io/badge/AWS-SQS-orange)](https://aws.amazon.com/sqs/)
[![License](https://img.shields.io/badge/License-MIT-green)](LICENSE)

📁 **Project Organization**: All files are organized following Python and AI agent best practices. Configuration files are in `config/`, requirements in `requirements/`, and documentation in `docs/`. See [Project Structure](docs/project/PROJECT_STRUCTURE.md) for details.

## 🌟 Features

### 🎨 **BHiveQ Observability Hub** (NEW!)
- Professional dark-themed web interface with LPD Digital Hive branding
- Real-time agent status tracking with activity indicators
- Live agent activity log streaming
- Critical alerts with pulsing badges for DLQs over 100 messages
- Force Reinvestigation button for manual triggers
- WebSocket-powered real-time updates
- Bootstrap 5 + responsive design
- Runs locally on http://localhost:5001

### 🤖 **Auto-Investigation with Claude AI & MCP Tools**
- Automatically triggers Claude Code when DLQs receive messages
- Multi-agent architecture with Google ADK framework
- Enhanced with 5 special MCP tools:
  - **Context7**: Library documentation and code examples search
  - **AWS Documentation**: AWS service docs and error code lookup
  - **CloudWatch Logs**: Advanced log analysis with filtering
  - **Lambda Tools**: Lambda function debugging and analysis
  - **Sequential Thinking**: Systematic root cause analysis
- Creates GitHub PRs with fixes automatically
- Smart cooldown and timeout management

### 📊 **Terminal Dashboard**
- Real-time multi-panel monitoring interface
- Tracks DLQ status, Claude agents, and GitHub PRs
- Investigation timeline with duration tracking
- Beautiful curses-based terminal UI

### 🔔 **Smart Notifications**
- Native macOS notifications for DLQ alerts
- ElevenLabs text-to-speech for audio alerts
- PR review reminders with female voice
- Customizable alert thresholds

### 🔧 **GitHub Integration**
- Automatic PR creation for fixes
- PR status tracking and monitoring
- Audio notifications for pending reviews
- Integration with GitHub Actions

## 📋 Prerequisites

- Python 3.8+ (tested with 3.11)
- AWS Account with SQS access (configured profile)
- GitHub account (uses `gh` CLI token)
- Gemini API key for Google ADK agents
- macOS (for notifications)
- Claude Code CLI installed

## 🚀 Quick Start

### 1. Clone the repository
```bash
git clone https://github.com/LPDigital-Agent/lpd-claude-code-monitor.git
cd lpd-claude-code-monitor
```

### 2. Set up virtual environment
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Install Google ADK and additional dependencies
pip install google-adk google-generativeai
pip install -r requirements_adk.txt
```

### 3. Configure environment
```bash
cp .env.template .env
# Edit .env with your settings:
# - GEMINI_API_KEY (required for ADK agents)
# - AWS_PROFILE (default: FABIO-PROD)
# - AWS_REGION (default: sa-east-1)

# GitHub token from gh CLI (automatic)
export GITHUB_TOKEN=$(gh auth token 2>/dev/null)
```

### 4. Start monitoring
```bash
# INTEGRATED MODE - Web Dashboard + ADK Monitor (Recommended)
./scripts/start_integrated.sh
# Starts both ADK multi-agent monitoring and web dashboard
# Open http://localhost:5001 in your browser

# OR Web Dashboard only
./scripts/start_dashboard.sh

# OR Terminal monitoring with auto-investigation
./scripts/start_monitor.sh adk-production

# OR Enhanced terminal dashboard
./scripts/start_monitor.sh enhanced

# Test notifications
./scripts/start_monitor.sh notification-test
```

## 🎯 Usage

### Available Commands

| Command | Description |
|---------|-------------|
| `./scripts/start_integrated.sh` | **🚀 Integrated Mode** - ADK Monitor + Web Dashboard (Best) |
| `./scripts/start_dashboard.sh` | LPD Hive Web Dashboard only |
| `./scripts/start_monitor.sh adk-production` | ADK multi-agent monitoring (terminal) |
| `./scripts/start_monitor.sh production` | Standard production monitoring |
| `./scripts/start_monitor.sh enhanced` | Enhanced terminal dashboard |
| `./scripts/start_monitor.sh discover` | Discover all DLQ queues |
| `./scripts/start_monitor.sh test` | Test mode (3 cycles) |
| `./scripts/start_monitor.sh cli monitor` | CLI monitoring interface |
| `./scripts/start_monitor.sh pr-audio-test` | Test PR audio notifications |
| `python tests/validation/test_adk_simple.py` | Validate ADK system setup |

### Configuration

Edit `config.yaml` to customize:
- AWS region and profile
- DLQ patterns to monitor
- Alert thresholds
- Investigation triggers
- Notification settings

## 🏗️ Architecture

```
┌─────────────────────────────────────────┐
│         DLQ Monitor Service             │
├─────────────┬───────────────────────────┤
│  SQS Poller │   Alert Manager           │
├─────────────┼───────────────────────────┤
│Claude Agent │   GitHub Integration      │
├─────────────┼───────────────────────────┤
│   Notifier  │   Dashboard UI            │
└─────────────┴───────────────────────────┘
```

### Key Components

- **dlq_monitor.py** - Main monitoring service
- **enhanced_live_monitor.py** - Real-time dashboard
- **pr_notifier/** - PR audio notification system
- **claude_live_monitor.py** - Claude investigation tracker

## 📊 Enhanced Dashboard

The enhanced dashboard provides real-time visibility:

```
┌──────────────────┬────────────────────┐
│   🚨 DLQ Status  │  🤖 Claude Agents  │
├──────────────────┴────────────────────┤
│      🔧 GitHub Pull Requests          │
├────────────────────────────────────────┤
│    📜 Investigation Timeline          │
└────────────────────────────────────────┘
```

### Features:
- **DLQ Status**: Real-time queue monitoring with message counts
- **Claude Agents**: Active AI agents and their tasks
- **PR Tracking**: Open pull requests from auto-investigations
- **Timeline**: Event history with timestamps and durations

## 🤖 Auto-Investigation

When configured DLQs receive messages:

1. **Detection** - Monitor detects messages in DLQ
2. **Investigation** - Claude AI analyzes the issue
3. **Fix Generation** - Creates code fixes
4. **PR Creation** - Opens GitHub PR with solution
5. **Notification** - Audio/visual alerts for review

### Configuration Example:
```python
auto_investigate_dlqs = [
    'fm-digitalguru-api-update-dlq-prod',
    'fm-transaction-processor-dlq-prd'
]
```

## 🔔 Notifications

### macOS Notifications
- Native notifications for DLQ alerts
- Non-intrusive with smart grouping

### Audio Alerts
- ElevenLabs TTS integration
- Female voice (Rachel) for announcements
- Customizable alert sounds

### PR Reminders
- Every 10 minutes for open PRs
- Different sounds for auto vs manual PRs
- Celebration sound when PRs are merged

## 🛠️ Development

### Project Structure
```
lpd-claude-code-monitor/
├── dlq_monitor.py           # Main monitor
├── enhanced_live_monitor.py # Dashboard
├── claude_live_monitor.py   # Claude tracker
├── pr_notifier/            # PR notifications
│   ├── __init__.py
│   ├── monitor.py
│   └── tts.py
├── config.yaml             # Configuration
├── requirements.txt        # Dependencies
└── start_monitor.sh       # Launcher script
```

### Adding New Features
1. Create feature branch
2. Implement changes
3. Test thoroughly
4. Submit PR with description

## 📝 Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `AWS_PROFILE` | AWS profile name | Yes |
| `AWS_REGION` | AWS region | Yes |
| `GITHUB_TOKEN` | GitHub PAT | For PRs |
| `GITHUB_USERNAME` | GitHub username | For PRs |
| `ELEVENLABS_API_KEY` | TTS API key | For audio |

## 🐛 Troubleshooting

### Common Issues

**No DLQs found**
- Check AWS credentials
- Verify region setting
- Ensure DLQs exist

**GitHub PRs not showing**
- Verify GITHUB_TOKEN is set
- Check token permissions (repo, read:org)

**No audio notifications**
- Check system audio settings
- Verify ElevenLabs API key
- Test with `./start_monitor.sh voice-test`

## 📚 Documentation

- [Enhanced Dashboard Guide](ENHANCED_DASHBOARD.md)
- [Auto-Investigation Guide](AUTO_INVESTIGATION_GUIDE.md)
- [PR Audio Notifications](PR_AUDIO_NOTIFICATIONS.md)
- [Status Monitoring](STATUS_MONITORING.md)

## 🤝 Contributing

1. Fork the repository
2. Create feature branch
3. Commit changes
4. Push to branch
5. Open pull request

## 📄 License

MIT License - see [LICENSE](LICENSE) file

## 🙏 Acknowledgments

- AWS SDK for Python (Boto3)
- Rich - Terminal formatting
- Click - CLI framework
- ElevenLabs - Text-to-speech
- Claude AI by Anthropic

## 📞 Support

For issues or questions:
- Open an [issue](https://github.com/LPDigital-Agent/lpd-claude-code-monitor/issues)
- Contact: fabio@lpdigital.ai

---

**Built with ❤️ by LPDigital**
