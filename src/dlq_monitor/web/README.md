# 🚀 Enhanced DLQ Web Dashboard

A modern, real-time web dashboard for monitoring AWS SQS Dead Letter Queues with MCP integration.

## Features

### Real-time Monitoring
- **Live DLQ Status**: Monitor all DLQ queues with real-time message counts
- **WebSocket Updates**: Automatic refresh every 5 seconds via WebSocket
- **Interactive Charts**: Chart.js visualizations showing message trends
- **Dark/Light Theme**: Toggle between themes with Ctrl+T

### AWS Integration
- **Direct AWS Access**: Uses boto3 to fetch data directly from AWS
- **CloudWatch Logs**: View and search CloudWatch logs in the dashboard
- **Lambda Functions**: Monitor Lambda functions related to DLQ processing
- **SQS Messages**: View actual messages in DLQ queues

### GitHub Integration
- **PR Tracking**: Monitor open pull requests related to DLQ investigations
- **Auto-Investigation**: Start Claude AI investigations directly from the dashboard
- **PR Status**: Real-time updates on PR status and reviews

### Investigation Management
- **Claude AI Integration**: Launch investigations with one click
- **Session Tracking**: Monitor active Claude investigation sessions
- **Investigation Timeline**: Track investigation history and durations

## Quick Start

### 1. Launch the Dashboard
```bash
./start_web_dashboard.sh
```

The dashboard will automatically:
- Check environment and AWS credentials
- Install required dependencies
- Start Flask server on http://localhost:5001 (port 5001 to avoid macOS AirPlay conflict)
- Open your browser automatically
- Suppress Blake2 hash warnings

### 2. Manual Start
```bash
# Activate virtual environment
source venv/bin/activate

# Install dependencies
pip install Flask Flask-SocketIO Flask-CORS

# Set environment variables
export AWS_PROFILE=FABIO-PROD
export AWS_REGION=sa-east-1
export GITHUB_TOKEN=$(gh auth token)

# Run the Flask app (clean startup without Blake2 warnings)
python3 src/dlq_monitor/web/start_web.py
```

### 3. Access Dashboard
Open http://localhost:5001 in your browser

## Dashboard Layout

```
┌──────────────────────────────────────────────────┐
│                  Summary Cards                    │
│  DLQs | Messages | Alerts | PRs | Investigations │
└──────────────────────────────────────────────────┘

┌─────────────────────┬────────────────────────────┐
│    DLQ Status       │    Message Trends Chart    │
│  (Table with queues)│    (Real-time graph)       │
└─────────────────────┴────────────────────────────┘

┌─────────────────────┬────────────────────────────┐
│   GitHub PRs        │   Claude Investigations    │
│  (Open PRs list)    │   (Active sessions)        │
└─────────────────────┴────────────────────────────┘

┌──────────────────────────────────────────────────┐
│              CloudWatch Logs                     │
│         (Searchable log viewer)                  │
└──────────────────────────────────────────────────┘
```

## Keyboard Shortcuts

- **Ctrl+R**: Refresh all data manually
- **Ctrl+T**: Toggle dark/light theme
- **Ctrl+C**: Stop the server

## API Endpoints

The Flask backend provides these REST API endpoints:

- `GET /` - Main dashboard page
- `GET /api/dashboard/summary` - Dashboard summary statistics
- `GET /api/dlqs` - List all DLQ queues
- `GET /api/dlqs/<queue_name>/messages` - Get messages from specific DLQ
- `GET /api/cloudwatch/logs` - Fetch CloudWatch logs
- `GET /api/github/prs` - Get GitHub pull requests
- `GET /api/lambda/functions` - List Lambda functions
- `GET /api/investigations` - Get active investigations
- `POST /api/investigations/start` - Start new investigation

## WebSocket Events

Real-time updates via Socket.IO:

- `connect` - Client connected
- `disconnect` - Client disconnected
- `dlq_update` - DLQ status update
- `pr_update` - GitHub PR update
- `investigation_update` - Investigation status update
- `request_update` - Manual update request

## Configuration

### Environment Variables
- `AWS_PROFILE` - AWS profile to use (default: FABIO-PROD)
- `AWS_REGION` - AWS region (default: sa-east-1)
- `GITHUB_TOKEN` - GitHub personal access token
- `SECRET_KEY` - Flask secret key
- `FLASK_PORT` - Flask server port (default: 5001)

### Files
- `app.py` - Flask backend application
- `static/js/dashboard.js` - Frontend JavaScript
- `static/css/dashboard.css` - Custom styles
- `templates/dashboard.html` - HTML template

## Troubleshooting

### Dashboard is empty
- Ensure AWS credentials are configured
- Check if DLQ queues exist in the specified region
- Verify the monitoring system is running

### Port already in use
- Port 5000 is used by macOS AirPlay Receiver
- The dashboard now uses port 5001 by default
- To use a different port: `export FLASK_PORT=8080`

### Blake2 hash warnings
- These warnings are harmless and suppressed by default
- Use `start_web.py` instead of running app.py directly

### WebSocket disconnected
- Check Flask server is running
- Verify no firewall blocking port 5001
- Check browser console for errors

### GitHub PRs not showing
- Ensure GITHUB_TOKEN is set
- Verify token has required permissions
- Check GitHub API rate limits

## Technology Stack

- **Backend**: Flask, Flask-SocketIO, boto3
- **Frontend**: HTML5, Bootstrap 5, Chart.js
- **Real-time**: WebSocket (Socket.IO)
- **AWS**: boto3 for SQS, CloudWatch, Lambda
- **Styling**: Bootstrap 5, Font Awesome icons

## Why Web Dashboard?

The web dashboard solves the empty curses dashboard issue by:
1. **Direct AWS Access**: Fetches data directly from AWS instead of parsing log files
2. **Real-time Updates**: WebSocket ensures live data without file dependencies
3. **Rich UX**: Modern web interface with interactive charts and tables
4. **MCP Integration**: Uses MCP servers for enhanced AWS capabilities
5. **Browser-based**: Works on any device with a browser

## Next Steps

- Add more MCP server integrations
- Implement data export functionality
- Add user authentication
- Create dashboard presets
- Add alert configuration UI