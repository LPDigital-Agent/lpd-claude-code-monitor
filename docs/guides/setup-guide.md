# Complete Setup and Configuration Guide

This comprehensive guide will walk you through setting up the AWS DLQ Claude Monitor system from scratch.

## 📋 Prerequisites

Before you begin, ensure you have:

### System Requirements
- **Operating System**: macOS 10.15+ or Linux (Ubuntu 18.04+)
- **Python**: 3.8 or higher
- **Memory**: Minimum 4GB RAM (8GB recommended)
- **Storage**: At least 2GB free space

### Required Accounts & Services
- **AWS Account** with SQS access and DLQ permissions
- **GitHub Account** with repository access
- **ElevenLabs Account** (optional, for audio notifications)
- **Claude Code CLI** installed and configured

### Required Permissions
- **AWS**: `sqs:ListQueues`, `sqs:GetQueueAttributes`, `sqs:PurgeQueue`
- **GitHub**: `repo`, `read:org` permissions for Personal Access Token

## 🚀 Installation

### Step 1: Clone Repository
```bash
git clone <repository-url>
cd lpd-claude-code-monitor
```

### Step 2: Python Environment Setup
```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment (macOS/Linux)
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
pip install -r requirements-dev.txt  # For development
```

### Step 3: Claude Code CLI Installation
```bash
# Install Claude Code CLI (if not already installed)
# Follow instructions at https://claude.ai/code

# Verify installation
claude --version
```

## ⚙️ Configuration

### Step 1: Environment Variables
```bash
# Copy template
cp .env.template .env

# Edit .env file with your credentials
nano .env
```

Required environment variables:
```bash
# GitHub Integration
GITHUB_TOKEN=ghp_your_github_personal_access_token
GITHUB_USERNAME=your_github_username

# ElevenLabs (Optional - for audio notifications)
ELEVENLABS_API_KEY=your_elevenlabs_api_key

# Application Settings
DLQ_MONITOR_ENV=production
LOG_LEVEL=INFO
```

### Step 2: AWS Configuration
```bash
# Configure AWS CLI with your profile
aws configure --profile FABIO-PROD
# Enter your AWS Access Key ID
# Enter your AWS Secret Access Key
# Enter your region (e.g., sa-east-1)
# Enter output format (json)

# Verify configuration
aws sts get-caller-identity --profile FABIO-PROD
```

### Step 3: System Configuration
Edit `config/config.yaml`:
```yaml
aws:
  profile: "FABIO-PROD"
  region: "sa-east-1"
  
monitoring:
  check_interval: 30  # seconds
  notification_threshold: 1  # messages
  
auto_investigation:
  enabled: true
  target_queues:
    - "fm-digitalguru-api-update-dlq-prod"
    - "fm-transaction-processor-dlq-prd"
  timeout_minutes: 30
  cooldown_hours: 1
  
notifications:
  macos_notifications: true
  audio_notifications: true
  pr_monitoring: true
  
github:
  monitor_prs: true
  pr_reminder_interval: 600  # 10 minutes
```

## 🧪 Testing Setup

### Step 1: Verify AWS Connection
```bash
./scripts/start_monitor.sh discover
```
This should list all your DLQ queues.

### Step 2: Test Notifications
```bash
./scripts/start_monitor.sh notification-test
```
You should see a macOS notification appear.

### Step 3: Test Audio (if configured)
```bash
./scripts/start_monitor.sh voice-test
```
You should hear a test audio message.

### Step 4: Test Claude Integration
```bash
./scripts/start_monitor.sh test-claude
```
This verifies Claude Code CLI is accessible.

### Step 5: Run Test Monitor
```bash
./scripts/start_monitor.sh test
```
Runs 3 monitoring cycles to verify everything works.

## 🎯 Queue Configuration

### Auto-Investigation Queues
Configure which DLQs should trigger automatic investigation:

1. **List existing DLQs**:
   ```bash
   ./scripts/start_monitor.sh discover
   ```

2. **Update configuration**:
   Edit `config/config.yaml` and add queue names to `auto_investigation.target_queues`.

3. **Test auto-investigation**:
   ```bash
   # This will trigger investigation if any target queue has messages
   ./scripts/start_monitor.sh test 1 30
   ```

### Pattern Matching
You can also use patterns to automatically detect DLQs:
```yaml
dlq_patterns:
  - ".*-dlq-.*"
  - ".*-deadletter.*"
  - ".*-failed.*"
```

## 🔔 Notification Setup

### macOS Notifications
Automatically enabled on macOS. No additional setup required.

### Audio Notifications (ElevenLabs)
1. **Get API Key**: Sign up at https://elevenlabs.io/
2. **Add to .env**: Set `ELEVENLABS_API_KEY`
3. **Test**: Run `./scripts/start_monitor.sh voice-test`

### GitHub PR Notifications
1. **Create GitHub Token**: 
   - Go to GitHub Settings > Developer settings > Personal access tokens
   - Create token with `repo` and `read:org` permissions
2. **Add to .env**: Set `GITHUB_TOKEN` and `GITHUB_USERNAME`
3. **Test**: Run `./scripts/start_monitor.sh pr-audio-test`

## 🚀 Running the System

### Production Mode (Recommended)
```bash
./scripts/start_monitor.sh production
```
Features:
- Continuous monitoring
- Auto-investigation enabled
- All notifications active
- Enhanced logging

### Enhanced Dashboard Mode
```bash
./scripts/start_monitor.sh enhanced
```
Features:
- Real-time dashboard
- Multi-panel view
- Agent monitoring
- PR tracking

### Ultimate Monitor Mode
```bash
./scripts/start_monitor.sh ultimate
```
Features:
- Most comprehensive dashboard
- All monitoring features
- Advanced analytics
- Timeline view

## 🔧 Advanced Configuration

### Custom Check Intervals
```bash
# Check every 60 seconds instead of default 30
./scripts/start_monitor.sh production --interval 60
```

### Disable Specific Features
```bash
# Disable PR monitoring
./scripts/start_monitor.sh production --no-pr-monitoring

# Disable audio notifications
export ELEVENLABS_API_KEY=""
./scripts/start_monitor.sh production
```

### Debug Mode
```bash
export DLQ_MONITOR_DEBUG=true
export LOG_LEVEL=DEBUG
./scripts/start_monitor.sh production
```

## 📊 Monitoring Status

### Check Investigation Status
```bash
./scripts/start_monitor.sh status
```

### View Live Dashboard
```bash
./scripts/start_monitor.sh live
```

### Tail Logs
```bash
./scripts/start_monitor.sh logs
```

## 🔒 Security Considerations

### API Keys
- Store all API keys in `.env` file (never commit to git)
- Use least privilege principle for AWS permissions
- Rotate tokens regularly

### AWS Permissions
Minimum required permissions:
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "sqs:ListQueues",
        "sqs:GetQueueAttributes",
        "sqs:PurgeQueue"
      ],
      "Resource": "*"
    }
  ]
}
```

### GitHub Token
- Use Fine-grained personal access tokens when possible
- Limit token scope to specific repositories
- Set appropriate expiration dates

## 🐛 Troubleshooting Setup

### Common Issues

#### AWS Authentication Failed
```bash
# Check AWS credentials
aws sts get-caller-identity --profile FABIO-PROD

# Reconfigure if necessary
aws configure --profile FABIO-PROD
```

#### Claude Command Not Found
```bash
# Check if Claude is in PATH
which claude

# Install if missing (follow Claude Code CLI documentation)
```

#### Python Dependencies Issues
```bash
# Upgrade pip
pip install --upgrade pip

# Reinstall dependencies
pip install -r requirements.txt --force-reinstall
```

#### Permission Denied on Scripts
```bash
# Make scripts executable
chmod +x scripts/*.sh
```

### Getting Help
1. Check the [troubleshooting guide](./troubleshooting.md)
2. Review logs in `dlq_monitor_FABIO-PROD_sa-east-1.log`
3. Run tests to isolate issues
4. Check GitHub issues for known problems

## ✅ Verification Checklist

After setup, verify:
- [ ] AWS connection works (`./scripts/start_monitor.sh discover`)
- [ ] Claude CLI accessible (`claude --version`)
- [ ] Notifications work (`./scripts/start_monitor.sh notification-test`)
- [ ] Audio works (`./scripts/start_monitor.sh voice-test`) - if configured
- [ ] Test monitoring runs successfully (`./scripts/start_monitor.sh test`)
- [ ] GitHub integration works (check PR detection)
- [ ] Auto-investigation triggers for target queues

## 🎉 Next Steps

Once setup is complete:
1. **Start production monitoring**: `./scripts/start_monitor.sh production`
2. **Set up monitoring dashboard**: `./scripts/start_monitor.sh enhanced`
3. **Review auto-investigation guide**: [Auto-Investigation Guide](./auto-investigation.md)
4. **Configure alerts and notifications**: [Notification Configuration](./notification-config.md)

---

**Last Updated**: 2025-08-05
**Setup Version**: 2.0 - Complete Configuration Guide