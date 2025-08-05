# Troubleshooting Guide

This guide covers common issues and their solutions when using the AWS DLQ Claude Monitor system.

## 🚨 Common Issues

### 1. AWS Connection Issues

#### Problem: "Unable to locate credentials"
```
botocore.exceptions.NoCredentialsError: Unable to locate credentials
```

**Solutions:**
```bash
# Check if AWS CLI is configured
aws configure list --profile FABIO-PROD

# If not configured, set it up
aws configure --profile FABIO-PROD

# Verify credentials work
aws sts get-caller-identity --profile FABIO-PROD
```

#### Problem: "Access Denied" errors
```
botocore.exceptions.ClientError: An error occurred (AccessDenied)
```

**Solutions:**
1. **Check IAM permissions**:
   ```bash
   # Test SQS access
   aws sqs list-queues --profile FABIO-PROD --region sa-east-1
   ```

2. **Required permissions**:
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

#### Problem: Wrong region errors
```
The specified queue does not exist for this wsdl version
```

**Solutions:**
```bash
# Check current region
aws configure get region --profile FABIO-PROD

# Set correct region
aws configure set region sa-east-1 --profile FABIO-PROD

# Or specify in config.yaml
aws:
  region: "sa-east-1"
```

### 2. Claude Integration Issues

#### Problem: "claude: command not found"
```bash
./scripts/start_monitor.sh test-claude
# bash: claude: command not found
```

**Solutions:**
```bash
# Check if Claude is installed
which claude

# Install Claude Code CLI (follow official docs)
# Verify installation
claude --version

# Check PATH
echo $PATH

# Add Claude to PATH if needed (add to ~/.bashrc or ~/.zshrc)
export PATH="/path/to/claude:$PATH"
```

#### Problem: Claude investigation hangs
Auto-investigation starts but never completes.

**Solutions:**
```bash
# Check running Claude processes
ps aux | grep claude

# Kill stuck processes
./scripts/start_monitor.sh status
# Note the PID and kill it
kill -9 <PID>

# Check timeout settings in config.yaml
auto_investigation:
  timeout_minutes: 30  # Adjust if needed

# Clear session file to reset cooldown
rm .claude_sessions.json
```

#### Problem: Investigation fails immediately
```
❌ AUTO-INVESTIGATION FAILED for queue-name
```

**Solutions:**
```bash
# Check logs for error details
tail -50 dlq_monitor_FABIO-PROD_sa-east-1.log | grep ERROR

# Test Claude manually
claude --version
claude "test prompt"

# Check system resources
free -h  # Memory
df -h    # Disk space
```

### 3. GitHub Integration Issues

#### Problem: "Bad credentials" error
```
github.GithubException.BadCredentialsException: 401
```

**Solutions:**
```bash
# Check if token is set
echo $GITHUB_TOKEN

# Verify token has correct permissions
curl -H "Authorization: token $GITHUB_TOKEN" https://api.github.com/user

# Create new token with required scopes:
# - repo (full repository access)
# - read:org (read organization data)
```

#### Problem: PRs not being detected
PR monitoring shows no PRs despite having open PRs.

**Solutions:**
```bash
# Test GitHub connection
./scripts/start_monitor.sh pr-audio-test

# Check GitHub username
echo $GITHUB_USERNAME

# Verify PR patterns in code
# PRs must contain keywords: dlq, dead letter, investigation, auto-fix, etc.

# Debug PR fetching
python3 -c "
from src.dlq_monitor.utils.github_integration import get_user_prs
prs = get_user_prs()
print(f'Found {len(prs)} PRs')
for pr in prs[:5]: print(pr['title'])
"
```

#### Problem: PR creation fails
Auto-investigation completes but no PR is created.

**Solutions:**
1. **Check Claude prompt**: Ensure it includes PR creation instructions
2. **Verify repository access**: Token must have write access to target repo
3. **Check logs**: Look for GitHub API errors in logs

### 4. Notification Issues

#### Problem: No macOS notifications appear
**Solutions:**
```bash
# Check notification permissions
# System Preferences > Notifications > Terminal (allow notifications)

# Test notification manually
osascript -e 'display notification "Test" with title "DLQ Monitor"'

# Check if notification function works
python3 -c "
from src.dlq_monitor.notifiers.pr_audio import send_mac_notification
send_mac_notification('Test', 'Test message')
"
```

#### Problem: Audio notifications not working
ElevenLabs audio fails to play.

**Solutions:**
```bash
# Check API key
echo $ELEVENLABS_API_KEY

# Test API connection
curl -H "xi-api-key: $ELEVENLABS_API_KEY" \
     https://api.elevenlabs.io/v1/voices

# Test audio system
./scripts/start_monitor.sh voice-test

# Check audio dependencies
pip install pygame  # Required for audio playback

# Test manual audio
python3 -c "
from src.dlq_monitor.notifiers.pr_audio import PRNotifier
notifier = PRNotifier()
notifier.speak('Test message')
"
```

### 5. Dashboard Issues

#### Problem: Dashboard appears corrupted or misaligned
**Solutions:**
```bash
# Check terminal size
echo "Cols: $COLUMNS, Lines: $LINES"

# Minimum requirements: 80x24
# Recommended: 120x40

# Clear terminal and restart
clear
./scripts/start_monitor.sh enhanced

# Use alternative simple mode if issues persist
python3 src/dlq_monitor/claude/live_monitor.py --simple
```

#### Problem: Dashboard freezes or stops updating
**Solutions:**
```bash
# Check if main process is running
ps aux | grep dlq_monitor

# Restart dashboard
# Press 'q' to quit, then restart
./scripts/start_monitor.sh enhanced

# Check for errors in logs
tail -20 dlq_monitor_FABIO-PROD_sa-east-1.log
```

### 6. Performance Issues

#### Problem: High CPU usage
Monitor consumes excessive CPU resources.

**Solutions:**
```bash
# Check running processes
top -p $(pgrep -f dlq_monitor)

# Increase check interval to reduce CPU usage
./scripts/start_monitor.sh production --interval 60  # 60 seconds

# Monitor resource usage
htop  # or Activity Monitor on macOS
```

#### Problem: Memory leaks
Memory usage keeps increasing over time.

**Solutions:**
```bash
# Monitor memory usage
while true; do
  ps aux | grep dlq_monitor | grep -v grep
  sleep 60
done

# Restart monitoring periodically (workaround)
# Add to crontab to restart daily:
# 0 0 * * * pkill -f dlq_monitor && cd /path/to/project && ./scripts/start_monitor.sh production
```

### 7. Configuration Issues

#### Problem: Config file not found
```
FileNotFoundError: config/config.yaml not found
```

**Solutions:**
```bash
# Check if config file exists
ls -la config/config.yaml

# Create from template if missing
cp config/config.yaml.template config/config.yaml

# Verify YAML syntax
python3 -c "import yaml; yaml.safe_load(open('config/config.yaml'))"
```

#### Problem: Invalid configuration values
**Solutions:**
```bash
# Validate config file
python3 -c "
import yaml
with open('config/config.yaml') as f:
    config = yaml.safe_load(f)
    print('Config loaded successfully')
    print(f'AWS Profile: {config.get(\"aws\", {}).get(\"profile\")}')
    print(f'Target queues: {config.get(\"auto_investigation\", {}).get(\"target_queues\")}')
"
```

## 🔧 Diagnostic Commands

### System Health Check
```bash
# Comprehensive system check
./scripts/start_monitor.sh status

# Or manual checks:
echo "=== AWS Connection ==="
aws sts get-caller-identity --profile FABIO-PROD

echo "=== Claude CLI ==="
which claude && claude --version

echo "=== GitHub Token ==="
curl -s -H "Authorization: token $GITHUB_TOKEN" https://api.github.com/user | jq '.login'

echo "=== Python Environment ==="
python3 --version
pip list | grep -E "(boto3|requests|pyyaml)"

echo "=== DLQ Discovery ==="
./scripts/start_monitor.sh discover
```

### Log Analysis
```bash
# View recent errors
grep -i error dlq_monitor_FABIO-PROD_sa-east-1.log | tail -20

# View investigation activity
grep -i investigation dlq_monitor_FABIO-PROD_sa-east-1.log | tail -20

# View notification activity
grep -i notification dlq_monitor_FABIO-PROD_sa-east-1.log | tail -20

# Monitor logs in real-time
tail -f dlq_monitor_FABIO-PROD_sa-east-1.log | grep --color=auto -E "(ERROR|WARN|Investigation|PR)"
```

### Process Monitoring
```bash
# Find all related processes
ps aux | grep -E "(dlq_monitor|claude|python)" | grep -v grep

# Check resource usage
top -p $(pgrep -f dlq_monitor) -d 5

# Monitor network connections
netstat -an | grep -E "(github|amazonaws|elevenlabs)"
```

## 🆘 Emergency Procedures

### 1. Stop All Monitoring
```bash
# Kill all related processes
pkill -f dlq_monitor
pkill -f claude.*investigation
pkill -f enhanced_live_monitor

# Verify all stopped
ps aux | grep -E "(dlq_monitor|claude)" | grep -v grep
```

### 2. Reset System State
```bash
# Clear session data
rm -f .claude_sessions.json

# Clear log files (backup first)
cp dlq_monitor_FABIO-PROD_sa-east-1.log dlq_monitor_backup.log
> dlq_monitor_FABIO-PROD_sa-east-1.log

# Reset virtual environment
deactivate
rm -rf venv
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 3. Factory Reset
```bash
# Complete reset (WARNING: loses all data)
git clean -fdx  # Removes all untracked files
git reset --hard HEAD  # Resets to last commit

# Reconfigure from scratch
cp .env.template .env
# Edit .env with your credentials
./scripts/start_monitor.sh discover  # Test setup
```

## 📞 Getting Help

### Before Seeking Help
1. **Check this troubleshooting guide**
2. **Review recent logs**: `tail -50 dlq_monitor_FABIO-PROD_sa-east-1.log`
3. **Test individual components**: Use test commands
4. **Check system resources**: CPU, memory, disk space
5. **Verify configuration**: AWS, GitHub, environment variables

### Information to Provide
When reporting issues, include:
- **Error message**: Full error text
- **Steps to reproduce**: What were you doing when it failed?
- **System info**: OS, Python version, AWS region
- **Configuration**: Relevant config.yaml settings (redact sensitive data)
- **Logs**: Recent log entries around the time of failure
- **Environment**: Virtual environment, dependencies versions

### Log Collection Script
```bash
#!/bin/bash
# Collect diagnostic information
echo "=== System Info ===" > debug_info.txt
uname -a >> debug_info.txt
python3 --version >> debug_info.txt
pip list >> debug_info.txt

echo -e "\n=== Configuration ===" >> debug_info.txt
cat config/config.yaml >> debug_info.txt

echo -e "\n=== Recent Logs ===" >> debug_info.txt
tail -100 dlq_monitor_FABIO-PROD_sa-east-1.log >> debug_info.txt

echo -e "\n=== Process Status ===" >> debug_info.txt
ps aux | grep -E "(dlq_monitor|claude)" >> debug_info.txt

echo "Debug info collected in debug_info.txt"
```

## 📚 Additional Resources

- **AWS SQS Documentation**: https://docs.aws.amazon.com/sqs/
- **Claude API Documentation**: https://docs.anthropic.com/
- **GitHub API Documentation**: https://docs.github.com/en/rest
- **ElevenLabs API Documentation**: https://docs.elevenlabs.io/
- **Python boto3 Documentation**: https://boto3.amazonaws.com/v1/documentation/api/latest/

---

**Last Updated**: 2025-08-05
**Version**: 2.0 - Comprehensive Troubleshooting Guide