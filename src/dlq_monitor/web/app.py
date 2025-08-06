#!/usr/bin/env python3
"""
Enhanced DLQ Web Dashboard - Flask Backend with MCP Integration
Real-time monitoring dashboard for AWS SQS Dead Letter Queues
"""
import os
import json
import subprocess
import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from flask import Flask, render_template, jsonify, request
from flask_socketio import SocketIO, emit
from flask_cors import CORS
import boto3
import requests
from threading import Thread
import time
import logging

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dlq-monitor-secret-key-2025')
CORS(app)
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='threading')

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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
    
    def get_dlq_queues(self) -> List[Dict[str, Any]]:
        """Get all DLQ queues with message counts"""
        try:
            response = self.sqs_client.list_queues()
            queues = []
            
            if 'QueueUrls' in response:
                for queue_url in response['QueueUrls']:
                    if 'dlq' in queue_url.lower():
                        queue_name = queue_url.split('/')[-1]
                        
                        attrs = self.sqs_client.get_queue_attributes(
                            QueueUrl=queue_url,
                            AttributeNames=['All']
                        )['Attributes']
                        
                        queues.append({
                            'name': queue_name,
                            'url': queue_url,
                            'messages': int(attrs.get('ApproximateNumberOfMessages', 0)),
                            'messagesNotVisible': int(attrs.get('ApproximateNumberOfMessagesNotVisible', 0)),
                            'messagesDelayed': int(attrs.get('ApproximateNumberOfMessagesDelayed', 0)),
                            'createdTimestamp': attrs.get('CreatedTimestamp', ''),
                            'lastModifiedTimestamp': attrs.get('LastModifiedTimestamp', ''),
                            'status': 'alert' if int(attrs.get('ApproximateNumberOfMessages', 0)) > 0 else 'ok'
                        })
            
            return sorted(queues, key=lambda x: x['messages'], reverse=True)
        except Exception as e:
            logger.error(f"Error fetching DLQ queues: {e}")
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
                with open(self.session_file, 'r') as f:
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
def get_logs():
    """Get CloudWatch logs"""
    log_group = request.args.get('logGroup', '/aws/lambda/dlq-processor')
    limit = int(request.args.get('limit', 100))
    return jsonify(mcp_service.get_cloudwatch_logs(log_group, limit))

@app.route('/api/github/prs')
def get_prs():
    """Get GitHub PRs"""
    return jsonify(mcp_service.get_github_prs())

@app.route('/api/lambda/functions')
def get_lambda_functions():
    """Get Lambda functions"""
    return jsonify(mcp_service.get_lambda_functions())

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
            
            time.sleep(5)
        except Exception as e:
            logger.error(f"Background monitor error: {e}")
            time.sleep(10)

@socketio.on('connect')
def handle_connect():
    """Handle WebSocket connection"""
    emit('connected', {'data': 'Connected to DLQ Monitor'})
    logger.info('Client connected')

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
            with open(adk_log_path, 'r') as f:
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
    
    # Use port 5001 to avoid conflict with macOS AirPlay Receiver
    port = int(os.environ.get('FLASK_PORT', 5001))
    logger.info(f"🚀 Starting Enhanced DLQ Web Dashboard on http://localhost:{port}")
    socketio.run(app, debug=True, host='0.0.0.0', port=port)