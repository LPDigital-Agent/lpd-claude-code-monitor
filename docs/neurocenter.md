# 🧠 BHiveQ NeuroCenter Documentation

## Overview

The BHiveQ NeuroCenter is a state-of-the-art operational intelligence dashboard that provides real-time monitoring and control of the DLQ monitoring system. Built with a professional "Dark Ops Center" theme, it offers complete transparency and traceability for autonomous agent operations.

## Access

- **URL**: http://localhost:5002/neurocenter
- **Port**: 5002 (separate from main web dashboard on 5001)
- **Launch**: `./launcher.sh` → Option 2 or `./neurocenter.sh`

## Features

### 🎯 Real-Time Agent Monitoring
- Live status of all ADK agents (Coordinator, DLQ Monitor, Investigator, Code Fixer, PR Manager, Notifier)
- Agent performance metrics and elapsed time tracking
- Visual status indicators with color-coded states
- Agent-DLQ assignment matrix for routing control

### 📊 Investigation Timeline
- GitHub Actions-style timeline with expandable entries
- Status progression tracking (initiated → analyzing → debugging → reviewing → completed)
- Real-time progress bars for active investigations
- Filterable by status (all, active, completed, failed)

### 📈 Live Metrics Dashboard
- **Active Agents**: Number of agents currently working
- **Average Investigation Time**: Mean time to resolution
- **PRs Generated**: Total pull requests created
- **Success Rate**: Percentage of successful investigations
- Auto-updates every 5 seconds with real data

### 🔄 Agent-DLQ Assignment Matrix
- Compact grid layout for efficient space usage
- Shows only FABIO-PROD/sa-east-1 DLQs
- Visual message count indicators
- Dropdown agent assignment per DLQ
- Automatic truncation of long DLQ names

### 🎛️ Control Panel
- **Sound Button**: Toggle audio alerts on/off
- **Notifications Button**: Enable/disable browser notifications
- **Settings Button**: Configure refresh intervals, thresholds, and preferences
- All settings persist in localStorage

### 🎨 Professional Dark Theme
- Primary color: Orange (#FA4616)
- Dark background (#0a0a0a)
- Hexagonal logo and patterns
- Smooth animations and transitions
- Optimized for long monitoring sessions

## Architecture

### Frontend Components
- **neurocenter.html**: Main dashboard template
- **neurocenter.js**: Real-time WebSocket communication and state management
- **neurocenter.css**: Professional dark theme styling

### Backend Integration
- **Flask Routes**: `/neurocenter` endpoint with WebSocket support
- **Database Services**: SQLAlchemy models for persistence
- **Investigation Service**: Manages investigation lifecycle
- **WebSocket Events**: Real-time updates for all dashboard components

### Database Schema
```python
- investigations: Complete investigation tracking
- timeline_events: Granular event logging
- agents: Agent registration and status
- agent_performance: Performance metrics
- dlq_mappings: Agent-DLQ assignments
- notifications: Alert history
- metrics: Aggregated statistics
- pr_tracking: GitHub PR status
```

## WebSocket Events

### Client → Server
- `get_agents`: Request agent list
- `get_investigations`: Request investigation history
- `get_dlqs`: Request DLQ status
- `get_metrics`: Request current metrics
- `get_mappings`: Request agent-DLQ mappings
- `assign_agent`: Assign agent to DLQ

### Server → Client
- `agent_update`: Agent status change
- `investigation_update`: Investigation progress
- `timeline_event`: New timeline entry
- `dlq_update`: DLQ message count change
- `metrics_update`: Metrics refresh
- `alert`: System alert
- `pr_created`: PR creation notification

## Configuration

### Settings Modal
- **Auto-refresh**: Toggle automatic data updates
- **Refresh Interval**: Configure update frequency (1-60 seconds)
- **Alert Threshold**: Set DLQ message count for alerts

### Persistent Preferences
All user preferences are stored in browser localStorage:
- Sound enabled/disabled state
- Notification preferences
- Custom settings
- Module layout (drag-and-drop positions)

## Drag-and-Drop Modules

The dashboard supports rearrangeable modules:
1. Agent Monitoring
2. Investigation Timeline
3. Live Metrics
4. Agent-DLQ Assignment
5. Recent Actions
6. System Status

Drag any module to reorder. Layout persists across sessions.

## Notifications

### Browser Notifications
- Requires permission (requested on first toggle)
- Shows for: Investigations, PR creation, Alerts
- Includes NeuroCenter icon

### Audio Alerts
- Alert sound for critical events
- Success sound for PR creation
- Can be muted via control panel

## Integration with ADK System

The NeuroCenter integrates seamlessly with the ADK multi-agent system:

1. **DLQ Monitor Agent** → Updates DLQ status in real-time
2. **Investigation Agent** → Creates timeline entries
3. **Code Fixer Agent** → Updates progress during fix implementation
4. **PR Manager Agent** → Notifies on PR creation
5. **Notifier Agent** → Triggers alerts and notifications
6. **Coordinator Agent** → Orchestrates all updates

## Launch Methods

### Standalone
```bash
./neurocenter.sh
```

### Via Launcher Menu
```bash
./launcher.sh
# Select option 2
```

### With All Services
```bash
./scripts/launch/start_integrated.sh
```

### Dashboard Only
```bash
./scripts/launch/start_dashboard.sh
```

## Troubleshooting

### NeuroCenter Not Loading
- Check if port 5002 is available: `lsof -i:5002`
- Verify database initialization: Check for `src/dlq_monitor/database/neurocenter.db`
- Ensure services are imported correctly in `app.py`

### Real-time Updates Not Working
- Check WebSocket connection in browser console
- Verify Flask-SocketIO is installed: `pip install flask-socketio`
- Check if background monitor thread is running

### Metrics Not Updating
- Verify ADK monitor is running
- Check database for investigation records
- Ensure WebSocket events are being emitted

## Development

### Adding New Metrics
1. Update `updateLiveMetrics()` in neurocenter.js
2. Add calculation logic
3. Update UI element with new metric

### Adding New WebSocket Events
1. Define event in neurocenter.js
2. Add handler function
3. Implement server-side emission in app.py

### Customizing Theme
- Primary color: `--primary-orange` in CSS
- Background: `--bg-primary`, `--bg-secondary`, `--bg-tertiary`
- Status colors: `--status-success`, `--status-warning`, `--status-error`

## Future Enhancements

- [ ] Historical metrics graphs
- [ ] Investigation replay functionality
- [ ] Team collaboration features
- [ ] Export investigation reports
- [ ] Mobile responsive design
- [ ] Dark/Light theme toggle
- [ ] Integration with monitoring tools (DataDog, New Relic)
- [ ] Custom alert rules
- [ ] Investigation templates
- [ ] Performance analytics dashboard