# 🎆 Enhanced DLQ Investigation Dashboard

## Overview
The Enhanced Live Monitor provides a real-time, comprehensive dashboard for monitoring DLQ investigations, Claude agents, GitHub PRs, and investigation timelines - all in one beautiful interface!

## Features

### 🚨 **DLQ Status Panel** (Top Left)
- Real-time DLQ queue monitoring
- Message count with color coding:
  - 🔴 Red: > 10 messages (critical)
  - 🟡 Yellow: 1-10 messages (warning)
  - ✅ Green: No messages
- Auto-refreshes every 3 seconds

### 🤖 **Claude Agents Panel** (Top Right)
- Shows all active Claude processes
- Agent types detected:
  - Investigation agents
  - Fix agents
  - Analyzers
  - Test runners
- Real-time CPU, Memory, and runtime stats
- Process IDs for debugging

### 🔧 **Pull Requests Panel** (Middle)
- Tracks DLQ-related PRs across your repos
- Shows PR number, repository, and title
- Auto-detects PRs with keywords:
  - "dlq", "dead letter", "investigation"
  - "auto-fix", "automated"
- Links to GitHub for quick access

### 📜 **Investigation Timeline** (Bottom)
- **NEW: Actual event times displayed!**
- **Duration tracking** - Shows how long investigations take
- Color-coded events:
  - 🚀 Blue: Investigation starting
  - ✅ Green: Successful completion
  - ❌ Red: Failures
  - ⏰ Yellow: Timeouts
  - 🔧 Magenta: PR created
  - 🚨 Alert: DLQ alerts
- Format: `HH:MM:SS  MM:SS  [icon] [message]`
  - First time: When event occurred
  - Duration: How long it took (for completions)

### 📊 **Live Statistics Bar**
- Active agent count
- Total DLQ queues with messages
- Total messages across all DLQs
- Open PR count

## Usage

### Start the Enhanced Dashboard:
```bash
cd "/Users/fabio.santos/LPD Repos/dlq-monitor"
./start_monitor.sh enhanced
```

Or directly:
```bash
python3 enhanced_live_monitor.py
```

### Controls:
- **`q`** - Quit the dashboard
- **`r`** - Force refresh (manual)
- **Auto-refresh** - Every 3 seconds

## What Makes It "Enhanced"?

1. **Multi-Panel View**: See everything at once
2. **Real-Time Updates**: 3-second refresh cycle
3. **Smart Event Parsing**: Understands investigation flow
4. **Duration Tracking**: Know how long things take
5. **GitHub Integration**: PR tracking built-in
6. **Agent Detection**: See what each Claude agent is doing
7. **Color Coding**: Quick visual status understanding
8. **Actual Times**: See when events happened, not just durations

## Example Timeline Entry:
```
15:58:56  08:52  ✅ Claude investigation completed for fm-digitalguru-dlq
   ↑       ↑     ↑
   |       |     └── Event description with icon
   |       └── Duration (8 minutes 52 seconds)
   └── Actual time event occurred (3:58:56 PM)
```

## Requirements:
- Python 3.x with curses support
- GitHub token (for PR tracking)
- Active DLQ monitoring session

## Tips:
1. Run alongside production monitoring for best results
2. Keep terminal window wide (>100 chars) for best display
3. GitHub token enables full PR tracking
4. Use with `tmux` for persistent monitoring

## Troubleshooting:
- If PRs don't show: Check GITHUB_TOKEN is set
- If no agents show: Ensure Claude investigations are running
- If DLQs don't update: Check main monitoring is active
- Terminal too small: Resize window or use smaller font

## Architecture:
```
┌─────────────────────────────────────────┐
│         Enhanced Dashboard              │
├──────────────┬──────────────────────────┤
│  DLQ Status  │    Claude Agents         │
│   (Top Left) │     (Top Right)          │
├──────────────┴──────────────────────────┤
│         GitHub Pull Requests            │
│             (Middle)                    │
├─────────────────────────────────────────┤
│       Investigation Timeline            │
│           (Bottom, scrolling)           │
├─────────────────────────────────────────┤
│    Statistics Bar (Active/DLQs/PRs)     │
└─────────────────────────────────────────┘
```

## Future Enhancements:
- [ ] Click on PR to open in browser
- [ ] Sound alerts for critical events
- [ ] Export timeline to file
- [ ] Historical data graphs
- [ ] Multi-region support
- [ ] Agent command details
- [ ] DLQ message preview

---
Created: 2025-08-05
Version: 2.0 - Enhanced with actual times and multi-panel view
