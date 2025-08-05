# 📊 Claude Investigation Status Monitoring

## Overview
Comprehensive monitoring system to track Claude AI auto-investigation sessions, their status, and activities in real-time.

## 🚀 Quick Start

### Check Investigation Status
```bash
./start_monitor.sh status
# or
./check_status.sh
```

### Live Monitoring Dashboard
```bash
./start_monitor.sh live
```

### Tail Investigation Logs
```bash
./start_monitor.sh logs
```

## 📋 Available Commands

### 1. Full Status Check
```bash
./start_monitor.sh status
```
Shows:
- Active Claude processes with CPU/Memory usage
- Recent investigation activities from logs
- Current DLQ queue status
- Investigation timeline and events
- Summary statistics

### 2. Live Monitoring
```bash
./start_monitor.sh live
```
Features:
- Real-time process monitoring
- Auto-refresh every 5 seconds
- Color-coded event tracking
- Interactive terminal UI
- Press 'q' to quit, 'r' to refresh

### 3. Log Monitoring
```bash
./start_monitor.sh logs
```
- Tails investigation logs in real-time
- Filters for Claude-related events
- Color highlighting for easy reading

### 4. Simple Status
```bash
python claude_live_monitor.py --simple
```
- Quick text-based status output
- No curses UI required
- Good for scripts and automation

## 📊 Status Information Displayed

### Process Information
- **PID**: Process ID
- **CPU Usage**: Current CPU percentage
- **Memory Usage**: RAM consumption in MB
- **Runtime**: How long the investigation has been running
- **Queue**: Which DLQ is being investigated
- **Status**: Running, completed, failed, or timeout

### Investigation Events
- 🔄 **Started**: Investigation initiated
- ⚙️ **Executing**: Claude command running
- ✅ **Completed**: Successfully finished
- ❌ **Failed**: Investigation failed
- ⏰ **Timeout**: Exceeded 30-minute limit

### Queue Status
- 🤖 **Auto-monitored queues**: Eligible for auto-investigation
- 📋 **Regular queues**: Manual investigation only
- 🕐 **Cooldown**: Time remaining before next investigation
- 📊 **Message count**: Current messages in each DLQ

## 🎨 Color Coding

### In Terminal Output
- 🟢 **Green**: Success, completed, running
- 🔴 **Red**: Errors, failures
- 🟡 **Yellow**: Warnings, timeouts, cooldown
- 🔵 **Blue**: Information, headers
- 🟣 **Purple**: Log entries
- 🟦 **Cyan**: Process details

## 📁 Data Storage

### Session Tracking
- File: `.claude_sessions.json`
- Tracks all Claude sessions
- Persists between monitoring runs
- Auto-cleanup of old sessions

### Log Files
- Main log: `dlq_monitor_FABIO-PROD_sa-east-1.log`
- Contains all investigation details
- Rotates automatically

## 🔧 Advanced Features

### Process Monitoring with psutil
```python
# The system uses psutil for detailed process monitoring
- Real-time CPU usage
- Memory consumption
- Process creation time
- Command line arguments
- Process status (running, sleeping, etc.)
```

### Log Analysis
```python
# Automatic log parsing for:
- Investigation start times
- Completion status
- Error messages
- Timeout events
- Queue identification
```

### Session Management
```python
# Tracks sessions across:
- Multiple investigations
- Cooldown periods
- Historical completions
- Failed attempts
```

## 🛠️ Troubleshooting

### No Processes Found
```bash
# Check if Claude is in PATH
which claude

# Check if any investigations are running
ps aux | grep claude

# Check recent logs for issues
grep -i error dlq_monitor_FABIO-PROD_sa-east-1.log | tail -20
```

### Status Check Fails
```bash
# Ensure virtual environment is activated
source venv/bin/activate

# Install required packages
pip install psutil boto3

# Check AWS credentials
aws sts get-caller-identity --profile FABIO-PROD
```

### Live Monitor Issues
```bash
# Use simple mode if terminal doesn't support curses
python claude_live_monitor.py --simple

# Check terminal size (needs at least 80x24)
echo "Columns: $COLUMNS, Lines: $LINES"
```

## 📈 Monitoring Best Practices

1. **Regular Checks**: Run status check every 30 minutes
2. **Live Monitor**: Use during active investigations
3. **Log Tailing**: Keep open during troubleshooting
4. **Process Limits**: Monitor if investigations exceed 30 minutes
5. **Cooldown Tracking**: Check before manual triggers

## 🔍 What to Look For

### Healthy Investigation
- ✅ Process running with stable CPU/memory
- ✅ Recent "Executing" log entry
- ✅ No error messages
- ✅ Runtime under 30 minutes

### Problem Signs
- ❌ No process but status shows "running"
- ❌ High memory usage (>2GB)
- ❌ Runtime exceeding 30 minutes
- ❌ Multiple failed attempts
- ❌ Repeated timeouts

## 💡 Tips

1. **Kill Stuck Investigation**:
   ```bash
   # Find PID from status check
   ./start_monitor.sh status
   # Kill the process
   kill -9 <PID>
   ```

2. **Reset Cooldown**:
   ```bash
   # Remove session file to reset
   rm .claude_sessions.json
   ```

3. **Check Specific Queue**:
   ```bash
   # Grep logs for specific queue
   grep "fm-digitalguru-api-update-dlq-prod" dlq_monitor_FABIO-PROD_sa-east-1.log | tail -20
   ```

4. **Monitor Multiple Queues**:
   ```bash
   # Open multiple terminals
   # Terminal 1: Main monitor
   ./start_monitor.sh production
   
   # Terminal 2: Status monitoring
   ./start_monitor.sh live
   
   # Terminal 3: Log tailing
   ./start_monitor.sh logs
   ```

## 📊 Example Output

### Status Check
```
🤖 CLAUDE INVESTIGATION STATUS MONITOR
📅 2025-08-05 15:30:45
======================================================================

🔍 ACTIVE CLAUDE PROCESSES
Found 1 active Claude session(s):

📊 Session 1:
   PID: 12345
   Queue: fm-digitalguru-api-update-dlq-prod
   Status: running
   Runtime: 5m 23s
   CPU Usage: 12.3%
   Memory: 245.6 MB
   Started: 15:25:22

📋 RECENT INVESTIGATION ACTIVITIES
✅ Queue: fm-digitalguru-api-update-dlq-prod
   Status: EXECUTING
   Started: 2025-08-05 15:25:22
   Running for: 5m 23s

📊 CURRENT DLQ QUEUE STATUS
🤖 fm-digitalguru-api-update-dlq-prod
   Messages: 8
   Status: 🔄 Investigation running
```

## 🔄 Integration with Main Monitor

The status monitoring integrates seamlessly with the main DLQ monitor:

1. **Automatic Tracking**: All investigations are tracked automatically
2. **Shared Logs**: Uses same log files as main monitor
3. **Session Persistence**: Maintains state between restarts
4. **Real-time Updates**: Shows live investigation progress

---

**Last Updated**: 2025-08-05
**Version**: 1.0 - Enhanced Status Monitoring System
