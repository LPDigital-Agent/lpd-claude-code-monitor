# Setup and Deployment Guide

## Quick Start

```bash
# Clone and setup in one command
git clone https://github.com/your-org/lpd-claude-code-monitor.git && \
cd lpd-claude-code-monitor && \
./scripts/setup/quick_setup.sh
```

## Detailed Setup Process

```mermaid
graph TD
    START[Start Setup]
    PREREQ[Check Prerequisites]
    CLONE[Clone Repository]
    ENV[Setup Environment]
    DEPS[Install Dependencies]
    CONFIG[Configure Services]
    VALIDATE[Validate Setup]
    DEPLOY[Deploy System]
    
    START --> PREREQ
    PREREQ --> CLONE
    CLONE --> ENV
    ENV --> DEPS
    DEPS --> CONFIG
    CONFIG --> VALIDATE
    VALIDATE --> DEPLOY
    
    PREREQ --> |Missing| FIX[Install Missing]
    FIX --> PREREQ
    
    VALIDATE --> |Failed| DEBUG[Debug Issues]
    DEBUG --> CONFIG
```

## Prerequisites Installation

### 1. System Requirements

#### macOS (Recommended)
```bash
# Install Homebrew if not present
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Install Python 3.11+
brew install python@3.11

# Install Node.js 18+
brew install node

# Install AWS CLI
brew install awscli

# Install GitHub CLI
brew install gh
```

#### Linux (Ubuntu/Debian)
```bash
# Update package manager
sudo apt update && sudo apt upgrade -y

# Install Python 3.11+
sudo apt install python3.11 python3.11-venv python3-pip

# Install Node.js 18+
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt install nodejs

# Install AWS CLI
sudo apt install awscli

# Install GitHub CLI
sudo apt install gh
```

### 2. API Keys Setup

#### Gemini API Key
1. Visit [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Click "Create API Key"
3. Copy the key (starts with `AIza...`)
4. Save for later configuration

#### GitHub Token
```bash
# Option 1: Use GitHub CLI (Recommended)
gh auth login
# Follow prompts, select:
# - GitHub.com
# - HTTPS
# - Login with web browser
# - Authorize with required scopes

# Option 2: Create Personal Access Token
# Visit: https://github.com/settings/tokens/new
# Scopes required: repo, read:org
# Copy token and save
```

#### AWS Credentials
```bash
# Configure AWS CLI
aws configure --profile FABIO-PROD

# Enter:
# AWS Access Key ID: [your-key]
# AWS Secret Access Key: [your-secret]
# Default region: sa-east-1
# Default output format: json

# Verify
aws sts get-caller-identity --profile FABIO-PROD
```

#### ElevenLabs API Key (Optional)
1. Visit [ElevenLabs](https://elevenlabs.io)
2. Sign up/Login
3. Go to Profile → API Keys
4. Generate and copy key

## Installation Steps

### 1. Clone Repository

```bash
# Clone repository
git clone https://github.com/your-org/lpd-claude-code-monitor.git
cd lpd-claude-code-monitor

# Verify structure
ls -la
# Should see: src/, adk_agents/, config/, scripts/, etc.
```

### 2. Python Environment Setup

```bash
# Create virtual environment
python3.11 -m venv venv

# Activate environment
source venv/bin/activate  # macOS/Linux
# or
venv\Scripts\activate  # Windows

# Upgrade pip
pip install --upgrade pip

# Install dependencies
pip install -r requirements.txt
pip install -r requirements_adk.txt
pip install -e .  # Install package in development mode
```

### 3. Environment Configuration

```bash
# Copy template
cp .env.template .env

# Edit .env file
nano .env  # or vim, code, etc.
```

`.env` file content:
```bash
# Required API Keys
GEMINI_API_KEY=AIzaSyCUWoLo3bV7XxKwvuzGeiO_SKkikdGI0i4
GITHUB_TOKEN=gho_xxxxxxxxxxxxxxxxxxxx  # Or leave empty for gh CLI

# AWS Configuration
AWS_PROFILE=FABIO-PROD
AWS_REGION=sa-east-1

# Optional
ELEVENLABS_API_KEY=your_elevenlabs_key
GITHUB_USERNAME=your-github-username
```

### 4. MCP Server Installation

```bash
# Install global MCP servers
npm install -g @mcp-servers/aws
npm install -g @modelcontextprotocol/server-github
npm install -g @modelcontextprotocol/server-sequential-thinking
npm install -g @modelcontextprotocol/server-memory
npm install -g @modelcontextprotocol/server-filesystem

# For local AWS MCP (if using local version)
cd /Users/fabio.santos/mcp/aws/mcp
npm install
npm run build
```

### 5. Configuration Files

#### ADK Configuration (`config/adk_config.yaml`)
```yaml
model:
  provider: gemini
  default_model: gemini-2.0-flash
  temperature: 0.7
  max_tokens: 4096

monitoring:
  check_interval_seconds: 30
  max_cycles: 0  # 0 for infinite
  critical_dlqs:
    - fm-digitalguru-api-update-dlq-prod
    - fm-transaction-processor-dlq-prd

agents:
  coordinator:
    cooldown_hours: 1
    max_concurrent_investigations: 3
  
  dlq_monitor:
    batch_size: 10
    visibility_timeout: 30
  
  investigator:
    max_messages_to_analyze: 20
    cloudwatch_lookback_minutes: 60
  
  code_fixer:
    max_fix_attempts: 3
    test_before_commit: true
  
  pr_manager:
    auto_merge_on_tests_pass: false
    require_reviews: 1
  
  notifier:
    voice_enabled: true
    reminder_interval_minutes: 10

session:
  persist_state: true
  state_file: .adk_state.json

evaluation:
  enable_tracing: true
  log_level: INFO
```

#### MCP Settings (`config/mcp_settings.json`)
```json
{
  "mcpServers": {
    "aws-api": {
      "command": "npx",
      "args": ["-y", "@mcp-servers/aws"],
      "env": {
        "AWS_PROFILE": "FABIO-PROD",
        "AWS_REGION": "sa-east-1"
      }
    },
    "sns-sqs": {
      "command": "node",
      "args": ["/Users/fabio.santos/mcp/aws/mcp/packages/sqs-mcp-server/dist/index.js"],
      "env": {
        "AWS_PROFILE": "FABIO-PROD",
        "AWS_REGION": "sa-east-1"
      }
    },
    "github": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-github"],
      "env": {
        "GITHUB_TOKEN": "${GITHUB_TOKEN}"
      }
    },
    "sequential-thinking": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-sequential-thinking"]
    },
    "memory": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-memory"],
      "env": {
        "MEMORY_STORE_PATH": "./memory_store"
      }
    },
    "filesystem": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-filesystem"],
      "env": {
        "WORKSPACE_DIR": "${PWD}"
      }
    }
  }
}
```

## Validation

### 1. Run Validation Script

```bash
# Activate environment
source venv/bin/activate

# Load environment
source .env
export GITHUB_TOKEN=$(gh auth token 2>/dev/null)

# Run validation
python tests/validation/test_adk_simple.py
```

Expected output:
```
🧪 ADK Multi-Agent DLQ Monitor - System Validation
============================================================
✅ Environment: All variables set
✅ Config Files: All configs found and valid
✅ Agent Files: All agent files present
✅ Claude Subagents: All subagents valid
✅ MCP Servers: All servers configured
✅ ADK Package: ADK components available
✅ Scripts: All scripts configured

🎉 All tests passed! System components are ready.
```

### 2. Test Individual Components

```bash
# Test AWS connection
aws sqs list-queues --profile FABIO-PROD --region sa-east-1

# Test GitHub connection
gh auth status

# Test Gemini API
python -c "import google.generativeai as genai; genai.configure(api_key='$GEMINI_API_KEY'); print('Gemini OK')"

# Test MCP servers
npx @mcp-servers/aws --version
npx @modelcontextprotocol/server-github --version
```

### 3. Dry Run

```bash
# Run in test mode (3 cycles)
./scripts/start_monitor.sh adk-test 3

# Check logs
tail -f logs/adk_monitor.log
```

## Deployment

### 1. Production Deployment

```bash
# Start production monitoring
./scripts/start_monitor.sh adk-production

# Run in background with nohup
nohup ./scripts/start_monitor.sh adk-production > monitor.log 2>&1 &

# Or use screen/tmux
screen -S adk-monitor
./scripts/start_monitor.sh adk-production
# Detach: Ctrl+A, D
# Reattach: screen -r adk-monitor
```

### 2. Systemd Service (Linux)

Create `/etc/systemd/system/adk-monitor.service`:
```ini
[Unit]
Description=ADK Multi-Agent DLQ Monitor
After=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/home/ubuntu/lpd-claude-code-monitor
Environment="PATH=/home/ubuntu/.local/bin:/usr/bin"
EnvironmentFile=/home/ubuntu/lpd-claude-code-monitor/.env
ExecStart=/home/ubuntu/lpd-claude-code-monitor/scripts/start_monitor.sh adk-production
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Enable and start:
```bash
sudo systemctl daemon-reload
sudo systemctl enable adk-monitor
sudo systemctl start adk-monitor
sudo systemctl status adk-monitor
```

### 3. Docker Deployment

`Dockerfile`:
```dockerfile
FROM python:3.11-slim

# Install Node.js
RUN apt-get update && apt-get install -y nodejs npm curl

# Set working directory
WORKDIR /app

# Copy requirements
COPY requirements*.txt ./

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt -r requirements_adk.txt

# Install MCP servers globally
RUN npm install -g @mcp-servers/aws \
    @modelcontextprotocol/server-github \
    @modelcontextprotocol/server-sequential-thinking \
    @modelcontextprotocol/server-memory \
    @modelcontextprotocol/server-filesystem

# Copy application
COPY . .

# Install package
RUN pip install -e .

# Run monitoring
CMD ["./scripts/start_monitor.sh", "adk-production"]
```

Build and run:
```bash
docker build -t adk-monitor .
docker run -d \
  --name adk-monitor \
  --env-file .env \
  -v ~/.aws:/root/.aws:ro \
  adk-monitor
```

### 4. Kubernetes Deployment

`k8s-deployment.yaml`:
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: adk-monitor
spec:
  replicas: 1
  selector:
    matchLabels:
      app: adk-monitor
  template:
    metadata:
      labels:
        app: adk-monitor
    spec:
      containers:
      - name: monitor
        image: adk-monitor:latest
        envFrom:
        - secretRef:
            name: adk-secrets
        volumeMounts:
        - name: aws-creds
          mountPath: /root/.aws
          readOnly: true
      volumes:
      - name: aws-creds
        secret:
          secretName: aws-credentials
---
apiVersion: v1
kind: Secret
metadata:
  name: adk-secrets
stringData:
  GEMINI_API_KEY: "your-key"
  GITHUB_TOKEN: "your-token"
  AWS_PROFILE: "FABIO-PROD"
  AWS_REGION: "sa-east-1"
```

## Monitoring & Maintenance

### 1. Health Checks

```bash
# Check if running
ps aux | grep adk_monitor

# Check logs
tail -f logs/adk_monitor.log

# Check agent status
cat .adk_state.json | jq .

# Check investigations
cat .claude_sessions.json | jq .
```

### 2. Log Rotation

```bash
# Setup logrotate
sudo nano /etc/logrotate.d/adk-monitor
```

Content:
```
/home/ubuntu/lpd-claude-code-monitor/logs/*.log {
    daily
    rotate 7
    compress
    delaycompress
    notifempty
    create 644 ubuntu ubuntu
    sharedscripts
    postrotate
        systemctl reload adk-monitor
    endscript
}
```

### 3. Backup

```bash
# Backup script
#!/bin/bash
BACKUP_DIR="/backup/adk-monitor"
mkdir -p $BACKUP_DIR

# Backup configs
cp -r config/ $BACKUP_DIR/
cp .env $BACKUP_DIR/

# Backup state
cp .adk_state.json $BACKUP_DIR/
cp .claude_sessions.json $BACKUP_DIR/

# Backup memory store
cp -r memory_store/ $BACKUP_DIR/

# Create archive
tar -czf $BACKUP_DIR/backup-$(date +%Y%m%d).tar.gz $BACKUP_DIR/*
```

## Troubleshooting Deployment

### Common Issues

| Issue | Solution |
|-------|----------|
| Port conflicts | Change ports in config |
| Memory issues | Increase system RAM or adjust agent limits |
| Network timeouts | Check firewall rules and AWS security groups |
| Permission denied | Fix file permissions: `chmod +x scripts/*.sh` |
| Module not found | Reinstall dependencies: `pip install -r requirements.txt` |

### Debug Mode

```bash
# Enable debug logging
export LOG_LEVEL=DEBUG

# Run with verbose output
python scripts/monitoring/adk_monitor.py --mode production --verbose

# Test specific agent
python -c "from adk_agents import coordinator; print(coordinator)"
```

### Recovery Procedures

```bash
# Reset state
rm .adk_state.json .claude_sessions.json

# Clear logs
rm logs/*.log

# Reinstall dependencies
pip install --force-reinstall -r requirements_adk.txt

# Full reset
deactivate
rm -rf venv/
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt -r requirements_adk.txt
pip install -e .
```

## Security Best Practices

### 1. Secrets Management
- Never commit `.env` file
- Use AWS Secrets Manager for production
- Rotate API keys regularly
- Use IAM roles when possible

### 2. Network Security
- Restrict AWS security groups
- Use VPC endpoints for AWS services
- Enable CloudTrail logging
- Implement rate limiting

### 3. Access Control
- Use least privilege IAM policies
- Enable MFA for AWS accounts
- Restrict GitHub token scopes
- Audit access logs regularly

### 4. Monitoring Security
- Set up CloudWatch alarms
- Monitor for unusual API usage
- Track failed authentication attempts
- Regular security audits