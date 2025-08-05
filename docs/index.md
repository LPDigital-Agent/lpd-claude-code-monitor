# AWS DLQ Claude Monitor Documentation

Welcome to the comprehensive documentation for the AWS SQS Dead Letter Queue (DLQ) monitoring system with Claude AI auto-investigation capabilities.

## 🚀 Project Overview

This system provides intelligent monitoring of AWS SQS Dead Letter Queues with automated investigation and resolution capabilities powered by Claude AI. When DLQ messages are detected, the system can automatically trigger comprehensive investigations, identify root causes, implement fixes, and create GitHub pull requests for review.

## ✨ Key Features

- **Real-time DLQ Monitoring**: Continuous monitoring of AWS SQS Dead Letter Queues
- **Claude AI Auto-Investigation**: Automated root cause analysis and fix implementation
- **GitHub Integration**: Automatic PR creation for fixes and improvements
- **Audio Notifications**: ElevenLabs TTS notifications for PR status updates
- **Enhanced Dashboards**: Real-time curses-based monitoring interfaces
- **Comprehensive Logging**: Detailed audit trails for all investigations
- **Multi-Agent Architecture**: Parallel subagent deployment for complex investigations

## 🏁 Quick Start Guide

### Prerequisites
- Python 3.8+
- AWS CLI configured with appropriate permissions
- GitHub Personal Access Token
- Claude Code CLI installed

### Installation

1. **Clone and Setup Environment**
   ```bash
   git clone <repository-url>
   cd lpd-claude-code-monitor
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

2. **Configure Environment Variables**
   ```bash
   # Copy and configure environment file
   cp .env.template .env
   # Edit .env with your credentials:
   # - GITHUB_TOKEN
   # - GITHUB_USERNAME
   # - ELEVENLABS_API_KEY (optional)
   ```

3. **Configure AWS Profile**
   ```bash
   aws configure --profile FABIO-PROD
   ```

4. **Start Monitoring**
   ```bash
   # Start production monitoring with auto-investigation
   ./scripts/start_monitor.sh production
   
   # Launch enhanced dashboard
   ./scripts/start_monitor.sh enhanced
   
   # Test mode (3 cycles)
   ./scripts/start_monitor.sh test
   ```

## 📚 Documentation Structure

### 🎯 [User Guides](./guides/)
Step-by-step guides for common tasks and workflows:
- [Setup and Configuration Guide](./guides/setup-guide.md)
- [Auto-Investigation Guide](./guides/auto-investigation.md)
- [Dashboard Usage Guide](./guides/dashboard-usage.md)
- [Troubleshooting Guide](./guides/troubleshooting.md)

### 🔧 [API Documentation](./api/)
Technical reference for developers:
- [Core Monitor API](./api/core-monitor.md)
- [Claude Integration API](./api/claude-integration.md)
- [GitHub Integration API](./api/github-integration.md)
- [Notification System API](./api/notification-system.md)

### 👨‍💻 [Development Documentation](./development/)
Resources for contributors and developers:
- [Development Setup](./development/setup.md)
- [Architecture Overview](./development/architecture.md)
- [Testing Guide](./development/testing.md)
- [Contributing Guidelines](./development/contributing.md)

## 🎛️ Available Commands

### Core Monitoring
- `./scripts/start_monitor.sh production` - Start production monitoring with auto-investigation
- `./scripts/start_monitor.sh enhanced` - Launch enhanced dashboard
- `./scripts/start_monitor.sh ultimate` - Most comprehensive monitoring dashboard
- `./scripts/start_monitor.sh discover` - Discover all DLQ queues

### Testing & Development
- `./scripts/start_monitor.sh test` - Test mode (3 cycles)
- `./scripts/start_monitor.sh notification-test` - Test notifications
- `./scripts/start_monitor.sh voice-test` - Test ElevenLabs voice
- `./scripts/start_monitor.sh test-claude` - Test Claude Code integration

### Status & Monitoring
- `./scripts/start_monitor.sh status` - Check Claude investigation status
- `./scripts/start_monitor.sh logs` - Tail investigation logs
- `./scripts/start_monitor.sh live` - Live monitoring dashboard

## 🏗️ System Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   AWS SQS DLQs  │───▶│  DLQ Monitor    │───▶│ Claude AI       │
│                 │    │                 │    │ Investigation   │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                               │                        │
                               ▼                        ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│  Notifications  │◀───│   Dashboard     │◀───│  GitHub PRs     │
│  (Audio/Visual) │    │   (Curses UI)   │    │  (Auto-created) │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## 🔧 Configuration

The system is primarily configured through:
- **config.yaml**: Main configuration file with DLQ patterns, thresholds, and investigation settings
- **.env**: Environment variables for API keys and credentials
- **scripts/**: Shell scripts for common operations

## 🆘 Getting Help

- **Issues**: Check the [troubleshooting guide](./guides/troubleshooting.md) first
- **Development**: See [development documentation](./development/) for technical details
- **API Reference**: Consult [API documentation](./api/) for integration details

## 📝 Recent Updates

- **v2.0**: Enhanced multi-agent investigation system
- **v1.5**: Added ElevenLabs audio notifications
- **v1.4**: Implemented ultimate monitoring dashboard
- **v1.3**: Enhanced GitHub integration with PR tracking
- **v1.2**: Added cooldown mechanisms and session management

## 🤝 Contributing

We welcome contributions! Please see our [contributing guidelines](./development/contributing.md) for details on:
- Code style and standards
- Testing requirements
- Pull request process
- Issue reporting

---

**Last Updated**: 2025-08-05
**Version**: 2.0 - Enhanced Documentation Structure