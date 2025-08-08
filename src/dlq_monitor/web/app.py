#!/usr/bin/env python3
"""
Enhanced DLQ Web Dashboard - Flask Backend with MCP Integration
Real-time monitoring dashboard for AWS SQS Dead Letter Queues
"""
import json
import logging
import os
import subprocess
import sys
import time
import warnings
from datetime import datetime, timedelta
from pathlib import Path
from threading import Lock, Thread
from typing import Any, Dict, List, Optional, Tuple

import boto3
import requests
from flask import Flask, jsonify, render_template, request
from flask_cors import CORS
from flask_socketio import SocketIO, emit

# Suppress blake2 hash warnings
warnings.filterwarnings("ignore", category=UserWarning, module='_blake2')
warnings.filterwarnings("ignore", message=".*blake2.*")
os.environ['PYTHONWARNINGS'] = 'ignore'

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
sys.path.insert(0, str(Path(__file__).parent.parent))

# Import NeuroCenter services
try:
    from dlq_monitor.services.database_service import get_database_service
    from dlq_monitor.services.investigation_service import get_investigation_service
    neurocenter_enabled = True
    db_service = get_database_service()
    investigation_service = get_investigation_service()
except ImportError as e:
    neurocenter_enabled = False
    db_service = None
    investigation_service = None
    logger = logging.getLogger(__name__)
    logger.warning(f"NeuroCenter services not available - running in legacy mode: {e}")

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dlq-monitor-secret-key-2025')
CORS(app)
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='threading')

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global voice notification state
voice_notifications_enabled = True

# Background thread for periodic updates
background_thread = None
stop_thread = False

class MCPService:
    """Service to interact with MCP servers for AWS data"""

    def __init__(self):
        self.aws_profile = os.environ.get('AWS_PROFILE', 'FABIO-PROD')
        self.aws_region = os.environ.get('AWS_REGION', 'sa-east-1')
        self.github_token = os.environ.get('GITHUB_TOKEN', '')

        # Create boto3 session with profile
        session = boto3.Session(profile_name=self.aws_profile)
        self.sqs_client = session.client('sqs', region_name=self.aws_region)
        self.cloudwatch_client = session.client('logs', region_name=self.aws_region)

        # Cache for DLQ data with TTL
        self._dlq_cache: Optional[Tuple[List[Dict[str, Any]], datetime]] = None
        self._cache_lock = Lock()
        self._cache_ttl = timedelta(seconds=10)  # Cache for 10 seconds

    def get_all_queues(self) -> List[Dict[str, Any]]:
        """Get all SQS queues with their attributes"""
        try:
            response = self.sqs_client.list_queues()
            queues = []

            if 'QueueUrls' in response:
                for queue_url in response['QueueUrls']:
                    queue_name = queue_url.split('/')[-1]

                    # Get queue attributes
                    attrs = self.sqs_client.get_queue_attributes(
                        QueueUrl=queue_url,
                        AttributeNames=['All']
                    )['Attributes']

                    queues.append({
                        'name': queue_name,
                        'url': queue_url,
                        'messages': int(attrs.get('ApproximateNumberOfMessages', 0)),
                        'inFlight': int(attrs.get('ApproximateNumberOfMessagesNotVisible', 0)),
                        'delayed': int(attrs.get('ApproximateNumberOfMessagesDelayed', 0)),
                        'visibility': attrs.get('VisibilityTimeout', '30') + 's',
                        'retention': str(int(attrs.get('MessageRetentionPeriod', 345600)) // 86400) + 'd',
                        'type': 'DLQ' if 'dlq' in queue_name.lower() else 'Standard'
                    })

            return queues
        except Exception as e:
            logger.error(f"Error getting all queues: {e}")
            return []

    def get_dlq_queues(self) -> List[Dict[str, Any]]:
        """Get ALL queues with detailed information - optimized with caching and batch operations"""
        with self._cache_lock:
            # Check cache first
            if self._dlq_cache is not None:
                cached_data, cache_time = self._dlq_cache
                if datetime.now() - cache_time < self._cache_ttl:
                    logger.debug(f"Returning cached DLQ data ({len(cached_data)} queues)")
                    return cached_data

        start_time = time.time()
        logger.info("Fetching fresh DLQ data from AWS...")

        try:
            # First, just get the list of queues (fast operation)
            response = self.sqs_client.list_queues()
            queues = []

            if 'QueueUrls' not in response:
                logger.info("No queues found in AWS account")
                return []

            queue_urls = response['QueueUrls']
            logger.info(f"Found {len(queue_urls)} queues, fetching attributes...")

            # Filter to only DLQ queues to reduce API calls
            dlq_urls = [url for url in queue_urls if 'dlq' in url.lower() or 'dead' in url.lower()]
            logger.info(f"Filtered to {len(dlq_urls)} DLQ queues")

            # Process DLQ queues with minimal attributes for speed
            for queue_url in dlq_urls:
                queue_name = queue_url.split('/')[-1]

                try:
                    # Only get essential attributes for performance
                    attrs = self.sqs_client.get_queue_attributes(
                        QueueUrl=queue_url,
                        AttributeNames=[
                            'ApproximateNumberOfMessages',
                            'ApproximateNumberOfMessagesNotVisible',
                            'ApproximateNumberOfMessagesDelayed',
                            'QueueArn'
                        ]
                    )['Attributes']

                    messages = int(attrs.get('ApproximateNumberOfMessages', 0))

                    queue_data = {
                        'name': queue_name,
                        'url': queue_url,
                        'arn': attrs.get('QueueArn', ''),
                        'messages': messages,
                        'messagesNotVisible': int(attrs.get('ApproximateNumberOfMessagesNotVisible', 0)),
                        'messagesDelayed': int(attrs.get('ApproximateNumberOfMessagesDelayed', 0)),
                        'createdTimestamp': '',
                        'lastModifiedTimestamp': '',
                        'visibilityTimeout': 30,
                        'maximumMessageSize': 262144,
                        'messageRetentionPeriod': 345600,
                        'receiveMessageWaitTime': 0,
                        'isDLQ': True,
                        'hasDLQConfig': False,
                        'oldestMessageAge': None,
                        'status': 'critical' if messages > 100 else
                                 'warning' if messages > 10 else
                                 'alert' if messages > 0 else 'ok',
                        'accountId': '432817839790',
                        'region': self.aws_region
                    }

                    queues.append(queue_data)
                except Exception as e:
                    logger.warning(f"Error fetching attributes for queue {queue_name}: {e}")
                    # Add queue with minimal data even if attributes fail
                    queues.append({
                        'name': queue_name,
                        'url': queue_url,
                        'messages': 0,
                        'messagesNotVisible': 0,
                        'isDLQ': True,
                        'status': 'unknown',
                        'region': self.aws_region
                    })

            # Sort by message count (highest first)
            sorted_queues = sorted(queues, key=lambda x: -x.get('messages', 0))

            # Update cache
            with self._cache_lock:
                self._dlq_cache = (sorted_queues, datetime.now())

            elapsed_time = time.time() - start_time
            logger.info(f"DLQ fetch completed in {elapsed_time:.2f} seconds for {len(sorted_queues)} queues")

            return sorted_queues

        except Exception as e:
            logger.error(f"Error fetching DLQ queues: {e}")
            # Return cached data if available, even if expired
            if self._dlq_cache is not None:
                logger.warning("Returning stale cached data due to error")
                return self._dlq_cache[0]
            return []

    def get_cloudwatch_logs(self, log_group: str, limit: int = 100) -> List[Dict[str, Any]]:
        """Get CloudWatch logs for a specific log group"""
        try:
            response = self.cloudwatch_client.describe_log_streams(
                logGroupName=log_group,
                orderBy='LastEventTime',
                descending=True,
                limit=5
            )

            logs = []
            for stream in response.get('logStreams', []):
                events = self.cloudwatch_client.get_log_events(
                    logGroupName=log_group,
                    logStreamName=stream['logStreamName'],
                    limit=limit // 5
                )

                for event in events.get('events', []):
                    logs.append({
                        'timestamp': datetime.fromtimestamp(event['timestamp'] / 1000).isoformat(),
                        'message': event['message'],
                        'stream': stream['logStreamName']
                    })

            return sorted(logs, key=lambda x: x['timestamp'], reverse=True)
        except Exception as e:
            logger.error(f"Error fetching CloudWatch logs: {e}")
            return []

    def get_github_prs(self) -> List[Dict[str, Any]]:
        """Get GitHub PRs related to DLQ investigations"""
        if not self.github_token:
            return []

        try:
            headers = {'Authorization': f'token {self.github_token}'}
            url = 'https://api.github.com/user/repos'
            response = requests.get(url, headers=headers, timeout=5)

            prs = []
            if response.status_code == 200:
                repos = response.json()[:10]

                for repo in repos:
                    pr_url = f"https://api.github.com/repos/{repo['full_name']}/pulls?state=open"
                    pr_response = requests.get(pr_url, headers=headers, timeout=5)

                    if pr_response.status_code == 200:
                        for pr in pr_response.json():
                            if any(kw in pr['title'].lower() for kw in ['dlq', 'dead letter', 'investigation']):
                                prs.append({
                                    'number': pr['number'],
                                    'title': pr['title'],
                                    'repo': repo['name'],
                                    'created': pr['created_at'],
                                    'updated': pr['updated_at'],
                                    'url': pr['html_url'],
                                    'author': pr['user']['login'],
                                    'state': pr['state']
                                })

            return sorted(prs, key=lambda x: x['updated'], reverse=True)
        except Exception as e:
            logger.error(f"Error fetching GitHub PRs: {e}")
            return []

    def get_lambda_functions(self) -> List[Dict[str, Any]]:
        """Get Lambda functions related to DLQ processing"""
        try:
            session = boto3.Session(profile_name=self.aws_profile)
            lambda_client = session.client('lambda', region_name=self.aws_region)

            response = lambda_client.list_functions()
            functions = []

            for func in response.get('Functions', []):
                if 'dlq' in func['FunctionName'].lower() or 'dead' in func['FunctionName'].lower():
                    functions.append({
                        'name': func['FunctionName'],
                        'runtime': func['Runtime'],
                        'lastModified': func['LastModified'],
                        'codeSize': func['CodeSize'],
                        'memorySize': func['MemorySize'],
                        'timeout': func['Timeout'],
                        'state': func.get('State', 'Active')
                    })

            return functions
        except Exception as e:
            logger.error(f"Error fetching Lambda functions: {e}")
            return []

mcp_service = MCPService()

class InvestigationTracker:
    """Track active Claude investigations"""

    def __init__(self):
        self.active_investigations = {}
        self.completed_investigations = []
        self.session_file = ".claude_sessions.json"

    def load_sessions(self) -> Dict[str, Any]:
        """Load active Claude sessions"""
        try:
            if os.path.exists(self.session_file):
                with open(self.session_file) as f:
                    return json.load(f)
        except Exception as e:
            logger.error(f"Error loading sessions: {e}")
        return {}

    def get_active_investigations(self) -> List[Dict[str, Any]]:
        """Get list of active investigations"""
        sessions = self.load_sessions()
        active = []

        for session_id, session_data in sessions.items():
            if session_data.get('status') == 'active':
                active.append({
                    'id': session_id,
                    'dlq': session_data.get('dlq_name', 'Unknown'),
                    'startTime': session_data.get('start_time', ''),
                    'pid': session_data.get('pid', 0),
                    'status': 'running'
                })

        return active

investigation_tracker = InvestigationTracker()

@app.route('/')
def index():
    """Serve the main dashboard page"""
    return render_template('dashboard.html')

@app.route('/neurocenter')
def neurocenter():
    """Serve the NeuroCenter dashboard"""
    if not neurocenter_enabled:
        return "NeuroCenter services not available", 503
    return render_template('neurocenter.html')

@app.route('/neurocenter-modern')
def neurocenter_modern():
    """Serve the ultra-modern professional NeuroCenter dashboard"""
    if not neurocenter_enabled:
        return "NeuroCenter services not available", 503
    return render_template('neurocenter-modern.html')

@app.route('/api/dashboard/summary')
def dashboard_summary():
    """Get dashboard summary data"""
    dlqs = mcp_service.get_dlq_queues()
    prs = mcp_service.get_github_prs()
    investigations = investigation_tracker.get_active_investigations()

    total_messages = sum(q['messages'] for q in dlqs)
    alert_queues = [q for q in dlqs if q['status'] == 'alert']

    return jsonify({
        'summary': {
            'totalDLQs': len(dlqs),
            'totalMessages': total_messages,
            'alertQueues': len(alert_queues),
            'activePRs': len(prs),
            'activeInvestigations': len(investigations)
        },
        'timestamp': datetime.now().isoformat()
    })

@app.route('/api/status')
def get_status():
    """Get comprehensive system status for LPD Hive dashboard"""
    return jsonify({
        'dlqs': mcp_service.get_dlq_queues(),
        'agents': get_agent_status(),
        'prs': mcp_service.get_github_prs(),
        'investigations': investigation_tracker.get_active_investigations(),
        'stats': get_system_stats(),
        'timestamp': datetime.now().isoformat()
    })

@app.route('/api/dlqs')
def get_dlqs():
    """Get all DLQ queues with details"""
    # Check if this is a force refresh request
    force_refresh = request.args.get('refresh', 'false').lower() == 'true'

    if force_refresh:
        logger.info("Force refresh requested - bypassing cache")
        # Clear the cache to force fresh data
        with mcp_service._cache_lock:
            mcp_service._dlq_cache = None

    return jsonify(mcp_service.get_dlq_queues())

@app.route('/api/dlqs/<queue_name>/messages')
def get_dlq_messages(queue_name):
    """Get messages from a specific DLQ"""
    try:
        queues = mcp_service.get_dlq_queues()
        queue = next((q for q in queues if q['name'] == queue_name), None)

        if not queue:
            return jsonify({'error': 'Queue not found'}), 404

        response = mcp_service.sqs_client.receive_message(
            QueueUrl=queue['url'],
            MaxNumberOfMessages=10,
            VisibilityTimeout=0,
            WaitTimeSeconds=0
        )

        messages = []
        for msg in response.get('Messages', []):
            messages.append({
                'id': msg['MessageId'],
                'body': json.loads(msg['Body']) if msg['Body'].startswith('{') else msg['Body'],
                'attributes': msg.get('Attributes', {}),
                'receivedTimestamp': msg.get('Attributes', {}).get('SentTimestamp', '')
            })

        return jsonify(messages)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/cloudwatch/logs')
def get_cloudwatch_logs_endpoint():
    """Get CloudWatch logs"""
    log_group = request.args.get('logGroup', '/aws/lambda/dlq-processor')
    limit = int(request.args.get('limit', 100))
    return jsonify(mcp_service.get_cloudwatch_logs(log_group, limit))

@app.route('/api/logs')
def get_logs():
    """Get system logs from all available log files"""
    try:
        level = request.args.get('level', 'all').lower()
        lines = int(request.args.get('lines', 1000))  # Increased default

        logs = []
        base_path = Path(__file__).parent.parent.parent.parent

        # List of all log files to check
        log_files = [
            ('Main Monitor', 'dlq_monitor_FABIO-PROD_sa-east-1.log'),
            ('NeuroCenter Backend', 'logs/neurocenter_backend.log'),
            ('NeuroCenter Frontend', 'logs/neurocenter_next.log'),
            ('ADK Monitor', 'logs/adk_monitor.log'),
            ('Web Dashboard', 'logs/web_dashboard.log'),
            ('DLQ Monitor', 'logs/dlq_monitor.log')
        ]

        # Collect logs from all available files
        for log_name, log_file in log_files:
            log_path = base_path / log_file

            if log_path.exists():
                try:
                    with open(log_path) as f:
                        all_lines = f.readlines()
                        # Get last N lines from each log - increased to show more content
                        lines_per_file = 200  # Show up to 200 lines per file
                        recent_lines = all_lines[-lines_per_file:] if len(all_lines) > lines_per_file else all_lines

                        # Add header for this log file
                        if recent_lines:
                            logs.append(f"\n{'='*60}")
                            logs.append(f"[{log_name}] - {log_file}")
                            logs.append(f"{'='*60}")

                            # Filter by level if needed
                            for line in recent_lines:
                                if level == 'all':
                                    logs.append(line.strip())
                                elif level in line.lower():
                                    logs.append(line.strip())
                except Exception as e:
                    logs.append(f"[{log_name}] Error reading file: {e}")

        # If no logs found at all
        if not logs:
            logs.append("No log files found. Available paths checked:")
            for log_name, log_file in log_files:
                logs.append(f"  - {log_file}")

        return jsonify({
            'logs': '\n'.join(logs),
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        logger.error(f"Error fetching logs: {e}")
        return jsonify({
            'logs': f'Error fetching logs: {str(e)}',
            'timestamp': datetime.now().isoformat()
        }), 500

@app.route('/api/github/prs')
def get_prs():
    """Get GitHub PRs"""
    return jsonify(mcp_service.get_github_prs())

@app.route('/api/lambda/functions')
def get_lambda_functions():
    """Get Lambda functions"""
    return jsonify(mcp_service.get_lambda_functions())

@app.route('/api/voice-settings', methods=['GET', 'POST'])
def voice_settings():
    """Get or set voice notification settings"""
    global voice_notifications_enabled

    if request.method == 'POST':
        data = request.json
        voice_notifications_enabled = data.get('enabled', True)
        os.environ['VOICE_NOTIFICATIONS_ENABLED'] = str(voice_notifications_enabled)
        return jsonify({'enabled': voice_notifications_enabled})

    return jsonify({'enabled': voice_notifications_enabled})

@app.route('/api/investigations')
def get_investigations():
    """Get active investigations"""
    return jsonify(investigation_tracker.get_active_investigations())

@app.route('/api/investigations/start', methods=['POST'])
def start_investigation():
    """Start a new Claude investigation"""
    data = request.json
    dlq_name = data.get('dlq_name')

    if not dlq_name:
        return jsonify({'error': 'DLQ name required'}), 400

    try:
        cmd = f"claude code --task 'Investigate DLQ {dlq_name} and create fix'"
        process = subprocess.Popen(cmd, shell=True)

        investigation_id = f"inv_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        session_data = {
            investigation_id: {
                'dlq_name': dlq_name,
                'start_time': datetime.now().isoformat(),
                'pid': process.pid,
                'status': 'active'
            }
        }

        sessions = investigation_tracker.load_sessions()
        sessions.update(session_data)

        with open(investigation_tracker.session_file, 'w') as f:
            json.dump(sessions, f, indent=2)

        return jsonify({
            'investigation_id': investigation_id,
            'status': 'started',
            'pid': process.pid
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/investigate', methods=['POST'])
def investigate_queues():
    """Trigger investigation for multiple queues"""
    data = request.json
    queues = data.get('queues', [])

    if not queues:
        return jsonify({'error': 'No queues specified'}), 400

    # Import the manual investigation module
    try:
        manual_investigation_path = Path(__file__).parent.parent / 'claude' / 'manual_investigation.py'

        # Track active investigations globally
        if not hasattr(app, 'active_investigations'):
            app.active_investigations = {}

        results = []
        for queue_name in queues:
            try:
                # Start investigation for each queue
                cmd = [
                    sys.executable,
                    str(manual_investigation_path),
                    queue_name
                ]

                process = subprocess.Popen(
                    cmd,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True
                )

                investigation_id = f"inv_{queue_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

                # Track this investigation
                app.active_investigations[investigation_id] = {
                    'queue': queue_name,
                    'pid': process.pid,
                    'status': 'active',
                    'start_time': datetime.now().isoformat(),
                    'messages_processed': 0,
                    'progress': 0
                }

                results.append({
                    'queue': queue_name,
                    'investigation_id': investigation_id,
                    'status': 'started',
                    'pid': process.pid
                })

                logger.info(f"Started investigation for queue {queue_name} with PID {process.pid}")

            except Exception as e:
                logger.error(f"Failed to start investigation for {queue_name}: {e}")
                results.append({
                    'queue': queue_name,
                    'status': 'failed',
                    'error': str(e)
                })

        return jsonify({
            'message': f'Started investigations for {len([r for r in results if r.get("status") == "started"])} queue(s)',
            'results': results
        })

    except Exception as e:
        logger.error(f"Investigation error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/active-investigations', methods=['GET'])
def get_active_investigations():
    """Get all active investigations"""
    try:
        import psutil

        if not hasattr(app, 'active_investigations'):
            app.active_investigations = {}

        # Update investigation status based on process status
        for inv_id, inv_data in list(app.active_investigations.items()):
            try:
                # Check if process is still running
                if psutil.pid_exists(inv_data['pid']):
                    proc = psutil.Process(inv_data['pid'])
                    if proc.status() == psutil.STATUS_ZOMBIE:
                        inv_data['status'] = 'completed'
                        inv_data['progress'] = 100
                    else:
                        # Simulate progress (in real scenario, read from logs or status file)
                        if inv_data['progress'] < 90:
                            inv_data['progress'] += 10
                            inv_data['messages_processed'] += 5
                else:
                    # Process no longer exists
                    inv_data['status'] = 'completed'
                    inv_data['progress'] = 100
            except psutil.NoSuchProcess:
                inv_data['status'] = 'completed'
                inv_data['progress'] = 100

        # Convert to list format for frontend
        active_agents = []
        for inv_id, inv_data in app.active_investigations.items():
            if inv_data['status'] == 'active':
                # Calculate duration
                start_time = datetime.fromisoformat(inv_data['start_time'])
                duration = datetime.now() - start_time
                duration_str = f"{int(duration.total_seconds() // 60)}m {int(duration.total_seconds() % 60)}s"

                active_agents.append({
                    'id': inv_id,
                    'name': f"Agent-{inv_data['pid']}",
                    'dlq': inv_data['queue'],
                    'status': 'active',
                    'progress': inv_data['progress'],
                    'duration': duration_str,
                    'messagesProcessed': inv_data['messages_processed']
                })

        return jsonify(active_agents)
    except Exception as e:
        logger.error(f"Error getting active investigations: {e}")
        return jsonify([])

def background_monitor():
    """Background thread to emit real-time updates"""
    while True:
        try:
            # Emit DLQ updates
            dlqs = mcp_service.get_dlq_queues()
            socketio.emit('dlq_update', dlqs)

            # Emit investigation updates
            investigations = investigation_tracker.get_active_investigations()
            socketio.emit('investigation_update', investigations)

            # Emit agent status updates
            agents = get_agent_status()
            for agent_id, agent_data in agents.items():
                socketio.emit('agent_update', {
                    'id': agent_id,
                    'name': agent_data['name'],
                    'status': agent_data['status'],
                    'lastActivity': agent_data['lastActivity'],
                    'currentTask': agent_data['currentTask']
                })

            # Emit PR updates
            prs = mcp_service.get_github_prs()
            socketio.emit('pr_update', prs)

            # Emit stats updates
            stats = get_system_stats()
            socketio.emit('stats_update', stats)

            # Emit NeuroCenter updates if enabled
            if neurocenter_enabled and db_service:
                # Emit DLQ updates for NeuroCenter
                for dlq in dlqs:
                    socketio.emit('dlq_update', {
                        'name': dlq['name'],
                        'message_count': dlq['messages'],
                        'region': 'sa-east-1',
                        'oldest_message': 'unknown'
                    })

                # Emit metrics for NeuroCenter
                metrics = db_service.get_metrics_summary(hours=24)
                socketio.emit('metrics_update', {
                    'activeAgents': metrics['active_agents'],
                    'avgTime': metrics['average_investigation_time'],
                    'prsGenerated': metrics['prs_created'],
                    'successRate': metrics['success_rate']
                })

                # Emit active investigations from NeuroCenter
                if investigation_service:
                    nc_investigations = investigation_service.get_active_investigations()
                    for inv in nc_investigations:
                        socketio.emit('investigation_update', inv)

            time.sleep(5)
        except Exception as e:
            logger.error(f"Background monitor error: {e}")
            time.sleep(10)

def neurocenter_background_updates():
    """Background thread to send periodic updates to NeuroCenter"""
    while not stop_thread:
        try:
            with app.app_context():
                # Send DLQ updates with enhanced data
                dlqs = mcp_service.get_dlq_queues()
                for dlq in dlqs:
                    socketio.emit('dlq_update', {
                        'name': dlq['name'],
                        'messages': dlq['messages'],
                        'messagesNotVisible': dlq.get('messagesNotVisible', 0),
                        'messagesDelayed': dlq.get('messagesDelayed', 0),
                        'profile': 'FABIO-PROD',
                        'region': dlq['region'],
                        'accountId': dlq['accountId'],
                        'url': dlq.get('url', ''),
                        'arn': dlq.get('arn', ''),
                        'isDLQ': dlq.get('isDLQ', False),
                        'hasDLQConfig': dlq.get('hasDLQConfig', False),
                        'critical': dlq['messages'] >= 100,
                        'warning': dlq['messages'] >= 10,
                        'status': dlq.get('status', 'ok'),
                        'visibilityTimeout': dlq.get('visibilityTimeout', 30),
                        'messageRetentionPeriod': dlq.get('messageRetentionPeriod', 345600),
                        'oldestMessageAge': dlq.get('oldestMessageAge')
                    })

                # Send metrics update
                if db_service:
                    metrics = db_service.get_metrics_summary(hours=24)
                    socketio.emit('metrics_update', {
                        'activeAgents': metrics['active_agents'],
                        'avgTime': metrics['average_investigation_time'],
                        'prsGenerated': metrics['prs_created'],
                        'successRate': metrics['success_rate']
                    })

                time.sleep(10)  # Update every 10 seconds
        except Exception as e:
            logger.error(f"Error in background updates: {e}")
            time.sleep(10)

@socketio.on('connect')
def handle_connect():
    """Handle WebSocket connection"""
    global background_thread, stop_thread

    emit('connected', {'data': 'Connected to DLQ Monitor'})
    logger.info('Client connected')

    # Start background thread if not already running
    if background_thread is None or not background_thread.is_alive():
        stop_thread = False
        background_thread = Thread(target=neurocenter_background_updates)
        background_thread.daemon = True
        background_thread.start()
        logger.info('Started background updates thread')

@socketio.on('disconnect')
def handle_disconnect():
    """Handle WebSocket disconnection"""
    logger.info('Client disconnected')

@socketio.on('request_update')
def handle_update_request():
    """Handle manual update request"""
    dlqs = mcp_service.get_dlq_queues()
    emit('dlq_update', dlqs)

    prs = mcp_service.get_github_prs()
    emit('pr_update', prs)

    investigations = investigation_tracker.get_active_investigations()
    emit('investigation_update', investigations)

@socketio.on('voice_settings')
def handle_voice_settings(data):
    """Handle voice notification settings from web dashboard"""
    global voice_notifications_enabled
    voice_notifications_enabled = data.get('enabled', True)

    # Set environment variable for other processes
    os.environ['VOICE_NOTIFICATIONS_ENABLED'] = 'True' if voice_notifications_enabled else 'False'

    # Write to a file for persistence across processes
    voice_state_file = '/tmp/bhiveq/voice_state'
    os.makedirs('/tmp/bhiveq', exist_ok=True)
    with open(voice_state_file, 'w') as f:
        f.write('enabled' if voice_notifications_enabled else 'disabled')

    logger.info(f"Voice notifications {'enabled' if voice_notifications_enabled else 'disabled'}")
    emit('voice_settings_updated', {'enabled': voice_notifications_enabled})

@socketio.on('start_investigation')
def handle_start_investigation(data):
    """Handle investigation request from web dashboard"""
    dlq_name = data.get('dlq')
    messages = data.get('messages', 0)

    logger.info(f"Web dashboard requested investigation for {dlq_name} with {messages} messages")

    # Trigger ADK investigation by writing to a trigger file
    trigger_file = os.path.join(os.path.dirname(__file__), '../../../.dlq_investigation_trigger')
    with open(trigger_file, 'w') as f:
        json.dump({
            'dlq': dlq_name,
            'messages': messages,
            'timestamp': datetime.now().isoformat(),
            'source': 'web_dashboard'
        }, f)

    emit('alert', {
        'message': f'Investigation triggered for {dlq_name}',
        'type': 'success'
    })

    # Update agent status immediately
    emit('agent_update', {
        'id': 'investigator',
        'name': 'Investigation Agent',
        'status': 'investigating',
        'lastActivity': datetime.now().isoformat(),
        'currentTask': f'Investigating {dlq_name} ({messages} messages)'
    })

# NeuroCenter WebSocket Handlers
@socketio.on('get_agents')
def handle_get_agents():
    """Get all agents from database"""
    if db_service:
        agents = db_service.get_all_agents()
        for agent in agents:
            emit('agent_update', agent)

@socketio.on('get_investigations')
def handle_get_investigations():
    """Get active investigations"""
    if investigation_service:
        investigations = investigation_service.get_active_investigations()
        for inv in investigations:
            emit('investigation_update', inv)

@socketio.on('get_dlqs')
def handle_get_dlqs():
    """Get DLQ status"""
    dlqs = mcp_service.get_dlq_queues()
    for dlq in dlqs:
        emit('dlq_update', {
            'name': dlq['name'],
            'messages': dlq['messages'],
            'profile': 'FABIO-PROD',
            'region': 'sa-east-1',
            'url': dlq.get('url', ''),
            'critical': dlq['messages'] >= 10,
            'status': dlq.get('status', 'ok')
        })

@socketio.on('get_queues')
def handle_get_queues():
    """Get all SQS queues including DLQs"""
    try:
        # Get all queues from AWS
        queues = mcp_service.get_all_queues()

        # Send queue data
        emit('queue_data', {
            'queues': [
                {
                    'name': queue['name'],
                    'type': 'DLQ' if 'dlq' in queue['name'].lower() else 'Standard',
                    'messages': queue.get('messages', 0),
                    'inFlight': queue.get('inFlight', 0),
                    'delayed': queue.get('delayed', 0),
                    'visibility': queue.get('visibility', '30s'),
                    'retention': queue.get('retention', '14d'),
                    'status': 'critical' if queue.get('messages', 0) > 100 else 'warning' if queue.get('messages', 0) > 50 else 'ok'
                }
                for queue in queues
            ]
        })
    except Exception as e:
        logger.error(f"Error fetching queues: {e}")
        emit('error', {'message': 'Failed to fetch queues'})

@socketio.on('get_metrics')
def handle_get_metrics():
    """Get system metrics"""
    if db_service:
        metrics = db_service.get_metrics_summary(hours=24)
        emit('metrics_update', {
            'activeAgents': metrics['active_agents'],
            'avgTime': metrics['average_investigation_time'],
            'prsGenerated': metrics['prs_created'],
            'successRate': metrics['success_rate']
        })

@socketio.on('get_logs')
def handle_get_logs(data):
    """Get system logs"""
    try:
        lines = data.get('lines', 100)
        log_level = data.get('level', 'all')

        # Get the log file path
        log_dir = os.path.join(os.path.dirname(__file__), '../../../logs')
        log_file = os.path.join(log_dir, 'neurocenter.log')

        # Read the log file
        log_content = []
        if os.path.exists(log_file):
            with open(log_file) as f:
                # Read last N lines
                all_lines = f.readlines()
                recent_lines = all_lines[-lines:] if len(all_lines) > lines else all_lines

                # Filter by log level if needed
                for line in recent_lines:
                    if log_level == 'all' or log_level.upper() in line.upper():
                        log_content.append(line.strip())
        else:
            log_content = ["Log file not found. Checking alternative locations..."]

            # Try alternative log locations
            alt_locations = [
                'dlq_monitor_FABIO-PROD_sa-east-1.log',
                'adk_monitor.log',
                'web_dashboard.log'
            ]

            for alt_log in alt_locations:
                alt_path = os.path.join(log_dir, alt_log)
                if os.path.exists(alt_path):
                    with open(alt_path) as f:
                        all_lines = f.readlines()
                        recent_lines = all_lines[-50:] if len(all_lines) > 50 else all_lines
                        log_content.extend([f"--- {alt_log} ---"])
                        log_content.extend([line.strip() for line in recent_lines])
                        break

        # Send logs back to frontend
        emit('logs_data', {
            'logs': '\n'.join(log_content) if log_content else 'No logs available',
            'timestamp': datetime.now().isoformat()
        })

    except Exception as e:
        logger.error(f"Error fetching logs: {e}")
        emit('logs_data', {
            'logs': f'Error fetching logs: {str(e)}',
            'timestamp': datetime.now().isoformat()
        })

@socketio.on('get_mappings')
def handle_get_mappings():
    """Get agent-DLQ mappings"""
    if db_service:
        mappings = db_service.get_dlq_mappings()
        emit('mappings_update', mappings)

@socketio.on('create_mapping')
def handle_create_mapping(data):
    """Create new agent-DLQ mapping"""
    if db_service:
        success = db_service.create_dlq_mapping(
            agent_id=data.get('agent'),
            dlq_pattern=data.get('pattern'),
            trigger_type=data.get('trigger_type'),
            trigger_rule={'threshold': int(data.get('threshold', 50))},
            environment=data.get('environment', 'all')
        )
        if success:
            emit('alert', {
                'type': 'success',
                'title': 'Mapping Created',
                'message': 'Agent-DLQ mapping has been created successfully'
            })
            handle_get_mappings()

@socketio.on('investigate_dlq')
def handle_investigate_dlq(data):
    """Start investigation for a specific DLQ"""
    dlq_name = data.get('dlq_name')

    if investigation_service:
        # Get DLQ details
        dlqs = mcp_service.get_dlq_queues()
        dlq = next((q for q in dlqs if q['name'] == dlq_name), None)

        if dlq:
            # Start investigation using NeuroCenter service
            investigation_id = investigation_service.start_investigation(
                dlq_name=dlq_name,
                message_count=dlq['messages']
            )

            emit('alert', {
                'type': 'info',
                'title': 'Investigation Started',
                'message': f'Investigation {investigation_id} started for {dlq_name}'
            })

            # Simulate investigation progress for demo
            if investigation_id:
                thread = Thread(target=lambda: investigation_service.simulate_investigation(dlq_name, dlq['messages']))
                thread.daemon = True
                thread.start()

@socketio.on('start_agent')
def handle_start_agent(data):
    """Start a specific agent"""
    agent_id = data.get('agent_id')
    if db_service:
        db_service.update_agent_status(agent_id, 'running')
        emit('agent_update', {'id': agent_id, 'status': 'running'})

@socketio.on('stop_agent')
def handle_stop_agent(data):
    """Stop a specific agent"""
    agent_id = data.get('agent_id')
    if db_service:
        db_service.update_agent_status(agent_id, 'idle')
        emit('agent_update', {'id': agent_id, 'status': 'idle'})

def get_agent_status():
    """Get status of all agents - checks ADK monitor log for real status"""
    agents = {
        'investigator': {
            'name': 'Investigation Agent',
            'status': 'idle',
            'lastActivity': None,
            'currentTask': None
        },
        'analyzer': {
            'name': 'DLQ Analyzer',
            'status': 'idle',
            'lastActivity': None,
            'currentTask': None
        },
        'debugger': {
            'name': 'Code Debugger',
            'status': 'idle',
            'lastActivity': None,
            'currentTask': None
        },
        'reviewer': {
            'name': 'Code Reviewer',
            'status': 'idle',
            'lastActivity': None,
            'currentTask': None
        }
    }

    # Check ADK monitor log for agent activity
    try:
        adk_log_path = os.path.join(os.path.dirname(__file__), '../../../logs/adk_monitor.log')
        if os.path.exists(adk_log_path):
            # Read last 100 lines of log
            with open(adk_log_path) as f:
                lines = f.readlines()[-100:]

            # Parse for agent activity
            for line in reversed(lines):
                if 'Investigation Agent' in line and 'investigating' in line.lower():
                    agents['investigator']['status'] = 'investigating'
                    agents['investigator']['lastActivity'] = datetime.now().isoformat()
                    if 'DLQ:' in line:
                        dlq_name = line.split('DLQ:')[1].strip().split()[0]
                        agents['investigator']['currentTask'] = f'Investigating {dlq_name}'
                elif 'DLQ Analyzer' in line and 'analyzing' in line.lower():
                    agents['analyzer']['status'] = 'active'
                    agents['analyzer']['lastActivity'] = datetime.now().isoformat()
                elif 'Code Debugger' in line and 'debugging' in line.lower():
                    agents['debugger']['status'] = 'active'
                    agents['debugger']['lastActivity'] = datetime.now().isoformat()
                elif 'Code Reviewer' in line and 'reviewing' in line.lower():
                    agents['reviewer']['status'] = 'active'
                    agents['reviewer']['lastActivity'] = datetime.now().isoformat()
    except Exception as e:
        logger.debug(f"Could not read ADK monitor log: {e}")

    return agents

def get_system_stats():
    """Get system statistics"""
    try:
        dlqs = mcp_service.get_dlq_queues()
        total_messages = sum(dlq['messages'] for dlq in dlqs)

        # Get today's investigations from sessions
        sessions = investigation_tracker.load_sessions()
        today = datetime.now().date()
        today_investigations = sum(
            1 for inv in sessions.values()
            if datetime.fromisoformat(inv['start_time']).date() == today
        )

        return {
            'messagesProcessed': total_messages,
            'investigationsToday': today_investigations,
            'prsCreated': len(mcp_service.get_github_prs()),
            'issuesResolved': 0  # TODO: Track resolved issues
        }
    except Exception as e:
        logger.error(f"Error getting system stats: {e}")
        return {
            'messagesProcessed': 0,
            'investigationsToday': 0,
            'prsCreated': 0,
            'issuesResolved': 0
        }

if __name__ == '__main__':
    thread = Thread(target=background_monitor)
    thread.daemon = True
    thread.start()

    # Use port from environment or default
    port = int(os.environ.get('FLASK_PORT', 5001))

    # Determine which dashboard we're running
    dashboard_type = "NeuroCenter" if neurocenter_enabled else "Enhanced DLQ Web Dashboard"
    logger.info(f"🚀 Starting {dashboard_type} on http://localhost:{port}")
    if neurocenter_enabled:
        logger.info(f"   NeuroCenter: http://localhost:{port}/neurocenter")

    # Allow unsafe werkzeug for local development
    # In production, use a proper WSGI server like gunicorn
    socketio.run(app, debug=False, host='0.0.0.0', port=port,
                 allow_unsafe_werkzeug=True, log_output=False)
