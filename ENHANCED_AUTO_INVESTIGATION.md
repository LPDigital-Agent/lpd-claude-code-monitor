# 🤖 Enhanced Claude AI Auto-Investigation System

## Overview
The DLQ Monitor now features an **enhanced multi-agent auto-investigation system** that leverages Claude Code's full capabilities with multiple subagents, MCP tools, and ultrathink reasoning.

## 🎯 Key Features

### 1. **Multi-Subagent Architecture**
The system deploys multiple subagents working in parallel:
- **Subagent 1**: Analyzes DLQ messages and error patterns
- **Subagent 2**: Checks CloudWatch logs for related errors
- **Subagent 3**: Reviews codebase for potential issues
- **Subagent 4**: Identifies configuration or deployment problems

### 2. **MCP Tools Integration**
Leverages all available MCP tools:
- **sequential-thinking**: Step-by-step problem solving
- **filesystem**: Code analysis and fixes
- **github**: PR creation and code commits
- **memory**: Investigation progress tracking
- **Other MCPs**: As needed for investigation

### 3. **Ultrathink Reasoning**
- Deep analysis and root cause identification
- Multiple hypothesis generation and validation
- Evidence-based solution selection
- Complex problem-solving capabilities

## 📋 Enhanced Prompt Structure

The improved prompt ensures Claude Code:
1. Uses **CLAUDE CODE** for all operations (not just responses)
2. Deploys **MULTIPLE SUBAGENTS** working in parallel
3. Applies **ULTRATHINK** for deep reasoning
4. Leverages **ALL MCP TOOLS** available
5. Fixes **root causes**, not just symptoms
6. Creates **comprehensive PRs** with full documentation

## 🚀 Automatic Trigger Conditions

Auto-investigation triggers when:
- Messages detected in monitored DLQs:
  - `fm-digitalguru-api-update-dlq-prod`
  - `fm-transaction-processor-dlq-prd`
- Not in cooldown period (1 hour between investigations)
- No investigation currently running for that queue

## 🔧 Configuration

### Monitored Queues
```python
auto_investigate_dlqs = [
    "fm-digitalguru-api-update-dlq-prod",
    "fm-transaction-processor-dlq-prd"
]
```

### Timing Settings
- **Investigation Timeout**: 30 minutes
- **Cooldown Period**: 1 hour between investigations
- **Check Interval**: 30 seconds

## 📊 Investigation Process

1. **Detection**: Monitor detects messages in DLQ
2. **Trigger Check**: Verifies eligibility for auto-investigation
3. **Launch**: Executes Claude with enhanced multi-agent prompt
4. **Investigation**: Claude deploys subagents to investigate
5. **Analysis**: Ultrathink reasoning identifies root cause
6. **Fix**: Code changes made using filesystem MCP
7. **Commit**: Changes committed with descriptive message
8. **PR Creation**: Pull request created with full documentation
9. **DLQ Purge**: Queue cleaned after fixes
10. **Notification**: Status updates sent via Mac notifications

## 🛠️ Manual Testing

### Test Auto-Investigation
```bash
cd "/Users/fabio.santos/LPD Repos/dlq-monitor"
source venv/bin/activate
python test_auto_investigation.py
```

### Manual Trigger
```bash
python manual_investigation.py
# Select queue to investigate
```

### Check Status
```bash
python check_investigation_status.py
```

## 📝 Logs and Monitoring

### Log Files
- Main log: `dlq_monitor_FABIO-PROD_sa-east-1.log`
- Contains all investigation triggers and results

### Key Log Entries
```
🎆 Triggering auto-investigation for {queue_name}
🚀 Starting auto-investigation for {queue_name}
🔍 Executing Claude investigation: claude -p [PROMPT_HIDDEN]
✅ Claude investigation completed successfully
```

## 🔔 Notifications

The system sends Mac notifications for:
- Investigation started
- Investigation completed
- Investigation failed
- Investigation timeout

## ⚡ Important Notes

1. **Production Environment**: The system operates on PRODUCTION queues
2. **Claude Code Required**: Must have `claude` command available in PATH
3. **AWS Credentials**: Requires FABIO-PROD profile configured
4. **Background Execution**: Investigations run in background threads
5. **Non-Blocking**: Monitor continues while investigation runs

## 🚨 Troubleshooting

### Investigation Not Triggering
1. Check if queue is in `auto_investigate_dlqs` list
2. Verify not in cooldown period (1 hour)
3. Ensure no investigation already running
4. Check Claude command availability: `which claude`

### Investigation Fails
1. Check log file for error messages
2. Verify AWS credentials: `aws sts get-caller-identity --profile FABIO-PROD`
3. Test Claude manually: `claude --version`
4. Check system resources (investigations can be resource-intensive)

## 🎯 Best Practices

1. **Monitor Logs**: Keep an eye on investigation logs
2. **Review PRs**: Always review auto-generated PRs before merging
3. **Test Fixes**: Validate fixes in staging before production
4. **Document Issues**: Update this guide with new findings
5. **Adjust Cooldown**: Modify cooldown period based on your needs

## 📊 Success Metrics

A successful investigation will:
- ✅ Identify root cause of DLQ messages
- ✅ Fix the underlying issue in code
- ✅ Add error handling to prevent recurrence
- ✅ Create detailed PR with full documentation
- ✅ Purge DLQ messages after fix
- ✅ Prevent future occurrences

## 🔄 Continuous Improvement

The prompt can be further enhanced by:
- Adding specific error patterns to look for
- Including historical issue resolutions
- Customizing for specific queue types
- Adding integration tests requirements
- Including rollback procedures

---

**Last Updated**: 2025-08-05
**Version**: 2.0 - Enhanced Multi-Agent System
