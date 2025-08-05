# 🚀 LPD Claude Code Monitor

> Advanced DLQ monitoring system with Claude AI auto-investigation, PR tracking, and real-time dashboard for AWS SQS Dead Letter Queues

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue)](https://www.python.org/)
[![AWS](https://img.shields.io/badge/AWS-SQS-orange)](https://aws.amazon.com/sqs/)
[![License](https://img.shields.io/badge/License-MIT-green)](LICENSE)

## 🌟 Features

### 🤖 **Auto-Investigation with Claude AI**
- Automatically triggers Claude Code when DLQs receive messages
- Multi-agent architecture with subagents for comprehensive analysis
- Creates GitHub PRs with fixes automatically
- Smart cooldown and timeout management

### 📊 **Enhanced Live Dashboard**
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

- Python 3.8+
- AWS Account with SQS access
- GitHub account with Personal Access Token
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
```

### 3. Configure environment
```bash
cp .env.template .env
# Edit .env with your settings:
# - GITHUB_USERNAME
# - AWS credentials
```

### 4. Start monitoring
```bash
# Production monitoring with auto-investigation
./start_monitor.sh production

# Enhanced dashboard
./start_monitor.sh enhanced

# Test notifications
./start_monitor.sh notification-test
```

## 🎯 Usage

### Available Commands

| Command | Description |
|---------|-------------|
| `./start_monitor.sh production` | Start production DLQ monitoring |
| `./start_monitor.sh enhanced` | Launch enhanced dashboard |
| `./start_monitor.sh discover` | Discover all DLQ queues |
| `./start_monitor.sh test` | Test mode (3 cycles) |
| `./start_monitor.sh cli monitor` | CLI monitoring interface |
| `./start_monitor.sh pr-audio-test` | Test PR audio notifications |

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
