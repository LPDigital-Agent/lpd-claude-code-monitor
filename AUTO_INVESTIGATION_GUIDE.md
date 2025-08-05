# 🚀 Enhanced DLQ Monitor with Auto-Investigation

## 🎯 **SUCCESSFULLY ENHANCED!** ✅

Your AWS SQS DLQ monitoring system now includes **intelligent auto-investigation** powered by Claude AI!

## 🤖 **Auto-Investigation Features**

### **🎯 Target Queues:**
- **`fm-digitalguru-api-update-dlq-prod`** - Automatically triggers Claude investigation when messages are detected
- **`fm-transaction-processor-dlq-prd`** - Automatically triggers Claude investigation when messages are detected

### **🔄 How It Works:**
1. **Detection**: Monitor detects messages in either target DLQ
2. **Trigger**: Automatically launches Claude with comprehensive investigation prompt
3. **Investigation**: Claude uses MCP tools, subagents, and sequential thinking to:
   - Check DLQ messages and analyze error patterns
   - Examine CloudWatch logs for root cause analysis
   - Verify the entire codebase for potential issues
   - Identify and implement fixes
   - Commit code changes
   - Create Pull Request for review
   - Purge the DLQ after successful resolution

### **🛡️ Smart Controls:**
- **Cooldown Period**: 1 hour between investigations for same queue
- **Process Tracking**: Prevents duplicate investigations
- **Timeout Protection**: 30-minute timeout for investigations
- **Background Processing**: Non-blocking investigation threads
- **Rich Notifications**: Mac notifications for investigation status

## 📊 **Production Commands Updated**

### **🔥 Start Enhanced Production Monitoring:**
```bash
cd "/Users/fabio.santos/LPD Repos/dlq-monitor"

# Start continuous monitoring with auto-investigation
./start_monitor.sh production

# Custom interval with auto-investigation
./start_monitor.sh production --interval 60
```

### **🧪 Test Auto-Investigation:**
```bash
# Test with current active DLQs (should trigger auto-investigation)
./start_monitor.sh test 1 30
```

## 🚨 **Live Production Status**

**Current Active DLQs:**
- ✅ `fm-digitalguru-api-update-dlq-prod`: 2 messages → **AUTO-INVESTIGATION ENABLED**
- ✅ `fm-transaction-processor-dlq-prd`: 6 messages → **AUTO-INVESTIGATION ENABLED**

## 🔔 **Notification Types**

### **🚨 DLQ Alert Notifications:**
- **Title**: `🚨 DLQ ALERT - {queue_name}`
- **Content**: Profile, Region, Queue, Message Count

### **🔍 Auto-Investigation Notifications:**
- **Started**: `🔍 AUTO-INVESTIGATION STARTED`
- **Completed**: `✅ AUTO-INVESTIGATION COMPLETED`
- **Failed**: `❌ AUTO-INVESTIGATION FAILED`
- **Timeout**: `⏰ AUTO-INVESTIGATION TIMEOUT`

## 📋 **Console Output Enhanced**

When `fm-digitalguru-api-update-dlq-prod` receives messages:
```
🚨 DLQ ALERT - QUEUE: fm-digitalguru-api-update-dlq-prod 🚨
📊 Messages: 2
🌍 Region: sa-east-1
⏰ Time: 2025-08-05 12:48:37
==================================================
🔍 🤖 TRIGGERING CLAUDE AUTO-INVESTIGATION for fm-digitalguru-api-update-dlq-prod
📊 Expected duration: up to 30 minutes
🔔 You'll receive notifications when investigation completes
==================================================
```

## ⚙️ **Configuration Options**

The auto-investigation can be customized in the `MonitorConfig`:
```python
config = MonitorConfig(
    aws_profile="FABIO-PROD",
    region="sa-east-1",
    auto_investigate_dlqs=[
        "fm-digitalguru-api-update-dlq-prod",
        "fm-transaction-processor-dlq-prd"
    ],  # Target queues
    claude_command_timeout=1800,  # 30 minutes
)
```

## 🎯 **Claude Investigation Prompt**

When triggered, Claude receives this comprehensive prompt:
```
this is the DLQ -> fm-digitalguru-api-update-dlq-prod,
  use the profile: FABIO-PROD and Region: sa-east-1, also
  use subagents to ultrathink  check the DLQ and logs to check all the errors and verify the whole codebase to make sure is all good.
use the mcp sequence thinking to help also check others mcp tools to help you find the issue and how to fix. After **commit the code** once you're satisfied with the changes, create a PR to merge and purge the DLQ.
```

## 🔧 **System Architecture**

```
DLQ Monitor → Queue Detection → Auto-Investigation Check → Claude Command
     ↓              ↓                      ↓                    ↓
Mac Notifications  Background Thread   Process Tracking    Investigation
     ↓              ↓                      ↓                    ↓
Status Updates     Non-blocking       Cooldown Control      Code Fixes
```

## 📈 **Benefits**

✅ **Automated Issue Resolution**: No manual intervention needed for common issues
✅ **Intelligent Analysis**: Claude uses all available MCP tools for comprehensive investigation
✅ **Non-blocking**: Monitor continues working while investigation runs in background
✅ **Smart Cooldown**: Prevents investigation spam
✅ **Full Audit Trail**: Complete logging of all investigation activities
✅ **Notifications**: Keep you informed of investigation status

## 🎉 **Success Confirmation**

**✅ SYSTEM TESTED AND WORKING:**
- Auto-investigation triggered for `fm-digitalguru-api-update-dlq-prod`
- Background Claude process started successfully
- Mac notifications sent
- Production monitoring continues uninterrupted
- Full logging and error handling active

Your intelligent, self-healing DLQ monitoring system is now **live and operational**! 🚀

**Next**: When `fm-digitalguru-api-update-dlq-prod` receives messages, Claude will automatically investigate, fix issues, commit code, create PRs, and purge the DLQ - all without manual intervention!
