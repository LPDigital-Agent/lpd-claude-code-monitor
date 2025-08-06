// BHiveQ Observability Hub - Enhanced Dashboard JS
// 2-column layout with real-time activity feed and agent details

// Global state
let socket;
let dlqQueues = [];
let agents = {};
let investigations = [];
let pullRequests = [];
let activityFeed = [];
let currentFilter = 'all';
let agentDetailsExpanded = false;

// Initialize on DOM ready
document.addEventListener('DOMContentLoaded', function() {
    initializeWebSocket();
    initializeEventHandlers();
    loadInitialData();
    startClock();
    initializeVoiceToggle();
});

// WebSocket connection
function initializeWebSocket() {
    socket = io();
    
    socket.on('connect', function() {
        updateConnectionStatus(true);
        addActivity('system', 'Connected to monitoring service', 'success');
    });
    
    socket.on('disconnect', function() {
        updateConnectionStatus(false);
        addActivity('system', 'Disconnected from monitoring service', 'error');
    });
    
    // Real-time updates
    socket.on('dlq_update', handleDLQUpdate);
    socket.on('agent_update', handleAgentUpdate);
    socket.on('investigation_update', handleInvestigationUpdate);
    socket.on('pr_update', handlePRUpdate);
    socket.on('stats_update', updateStats);
    socket.on('alert', handleAlert);
    socket.on('voice_settings_updated', handleVoiceSettingsUpdate);
}

// Event handlers
function initializeEventHandlers() {
    // Activity filter buttons
    document.querySelectorAll('[data-filter]').forEach(btn => {
        btn.addEventListener('click', function() {
            document.querySelectorAll('[data-filter]').forEach(b => b.classList.remove('active'));
            this.classList.add('active');
            currentFilter = this.dataset.filter;
            renderActivityFeed();
        });
    });
}

// Load initial data
function loadInitialData() {
    fetch('/api/status')
        .then(response => response.json())
        .then(data => {
            if (data.dlqs) renderDLQs(data.dlqs);
            if (data.agents) renderAgents(data.agents);
            if (data.investigations) renderInvestigations(data.investigations);
            if (data.prs) renderPullRequests(data.prs);
            if (data.stats) updateStats(data.stats);
        })
        .catch(error => {
            console.error('Error loading initial data:', error);
            showAlert('Failed to load initial data', 'error');
        });
}

// DLQ Handling
function handleDLQUpdate(dlqs) {
    dlqQueues = dlqs;
    renderDLQs(dlqs);
    updateDLQCounts(dlqs);
    
    // Auto-investigate critical DLQs
    dlqs.forEach(dlq => {
        if (dlq.messages > 100) {
            addActivity('dlq', `Critical: ${dlq.name} has ${dlq.messages} messages`, 'danger');
            if (dlq.messages > 200) {
                triggerInvestigation(dlq.name, dlq.messages);
            }
        }
    });
}

function renderDLQs(dlqs) {
    const panel = document.getElementById('dlq-panel');
    const list = panel.querySelector('.dlq-list');
    
    list.innerHTML = '';
    
    dlqs.forEach(dlq => {
        const item = document.createElement('div');
        item.className = 'dlq-item';
        
        // Determine status
        let statusClass = 'healthy';
        let statusIcon = 'check-circle';
        if (dlq.messages > 100) {
            statusClass = 'critical';
            statusIcon = 'exclamation-triangle';
        } else if (dlq.messages > 50) {
            statusClass = 'warning';
            statusIcon = 'exclamation-circle';
        }
        
        item.classList.add(statusClass);
        
        item.innerHTML = `
            <div class="d-flex justify-content-between align-items-center">
                <div>
                    <div class="dlq-name">${dlq.name}</div>
                    <small class="text-muted">Region: sa-east-1</small>
                </div>
                <div class="dlq-messages text-end">
                    <div class="message-count ${statusClass === 'critical' ? 'text-danger' : ''}">${dlq.messages}</div>
                    <small class="text-muted">messages</small>
                </div>
                <button class="investigate-btn" onclick="investigateDLQ('${dlq.name}', ${dlq.messages})">
                    <i class="fas fa-search"></i> Investigate
                </button>
            </div>
        `;
        
        list.appendChild(item);
    });
}

function updateDLQCounts(dlqs) {
    let critical = 0, warning = 0, healthy = 0;
    
    dlqs.forEach(dlq => {
        if (dlq.messages > 100) critical++;
        else if (dlq.messages > 50) warning++;
        else healthy++;
    });
    
    document.getElementById('critical-count').textContent = critical;
    document.getElementById('warning-count').textContent = warning;
    document.getElementById('healthy-count').textContent = healthy;
}

// Agent Handling
function handleAgentUpdate(agent) {
    agents[agent.id] = agent;
    renderAgents(agents);
    addActivity('agent', `${agent.name}: ${agent.status}`, agent.status === 'investigating' ? 'warning' : 'info');
    
    // Update active agents stat
    const activeCount = Object.values(agents).filter(a => a.status !== 'idle').length;
    document.getElementById('active-agents-stat').textContent = activeCount;
}

function renderAgents(agentsData) {
    const panel = document.getElementById('agents-panel');
    const container = panel.querySelector('.agent-cards');
    
    container.innerHTML = '';
    
    const agentList = [
        { id: 'investigator', name: 'Investigation Agent', icon: 'search', color: 'orange' },
        { id: 'analyzer', name: 'DLQ Analyzer', icon: 'microscope', color: 'info' },
        { id: 'debugger', name: 'Code Debugger', icon: 'bug', color: 'danger' },
        { id: 'reviewer', name: 'Code Reviewer', icon: 'check-double', color: 'success' }
    ];
    
    agentList.forEach(agentInfo => {
        const agent = agentsData[agentInfo.id] || { status: 'idle', lastActivity: null, currentTask: null };
        
        const card = document.createElement('div');
        card.className = 'agent-card';
        card.id = `agent-${agentInfo.id}`;
        
        if (agentDetailsExpanded && agent.status !== 'idle') {
            card.classList.add('expanded');
        }
        
        const statusColor = agent.status === 'idle' ? 'text-muted' : 
                           agent.status === 'investigating' ? 'text-orange' : 
                           agent.status === 'active' ? 'text-success' : 'text-info';
        
        card.innerHTML = `
            <div class="agent-header">
                <div class="agent-icon">
                    <i class="fas fa-${agentInfo.icon}"></i>
                </div>
                <div class="agent-info flex-grow-1">
                    <h6>${agentInfo.name}</h6>
                    <span class="agent-status ${statusColor}" data-status="${agent.status}">
                        <i class="fas fa-circle"></i> ${agent.status}
                    </span>
                </div>
            </div>
            ${agent.currentTask ? `
                <div class="agent-task mt-2">
                    <small class="text-orange">Current Task:</small>
                    <div class="task-description">${agent.currentTask}</div>
                </div>
            ` : ''}
            ${agentDetailsExpanded && agent.status !== 'idle' ? `
                <div class="agent-logs">
                    ${generateAgentLogs(agentInfo.id)}
                </div>
            ` : ''}
        `;
        
        container.appendChild(card);
    });
    
    // Update agent count
    const activeCount = Object.values(agentsData).filter(a => a.status !== 'idle').length;
    document.getElementById('agent-count').textContent = activeCount;
}

function generateAgentLogs(agentId) {
    // Simulate agent logs with some intelligence
    const logs = {
        investigator: [
            'Analyzing DLQ message patterns...',
            'Identified error type: ValidationException',
            'Searching for similar issues in codebase...',
            'Found potential fix in error handler'
        ],
        analyzer: [
            'Parsing message attributes...',
            'Extracting error stack traces...',
            'Correlating with CloudWatch logs...'
        ],
        debugger: [
            'Setting breakpoints in Lambda function...',
            'Reproducing error conditions...',
            'Testing fix locally...'
        ],
        reviewer: [
            'Reviewing proposed changes...',
            'Running test suite...',
            'Checking code coverage...'
        ]
    };
    
    const agentLogs = logs[agentId] || ['Working...'];
    return agentLogs.map(log => `<div class="agent-log-entry">${log}</div>`).join('');
}

// Activity Feed
function addActivity(type, message, severity = 'info') {
    const entry = {
        type: type,
        message: message,
        severity: severity,
        timestamp: new Date()
    };
    
    activityFeed.unshift(entry);
    if (activityFeed.length > 100) activityFeed.pop();
    
    renderActivityFeed();
}

function renderActivityFeed() {
    const feed = document.getElementById('activity-feed');
    feed.innerHTML = '';
    
    const filtered = currentFilter === 'all' ? activityFeed : 
                    activityFeed.filter(a => {
                        if (currentFilter === 'agents') return a.type === 'agent';
                        if (currentFilter === 'investigations') return a.type === 'investigation';
                        if (currentFilter === 'prs') return a.type === 'pr';
                        return true;
                    });
    
    filtered.slice(0, 50).forEach(activity => {
        const entry = document.createElement('div');
        entry.className = `activity-entry ${activity.type}`;
        
        const time = new Date(activity.timestamp).toLocaleTimeString();
        
        entry.innerHTML = `
            <div class="activity-timestamp">${time}</div>
            <div class="activity-title">${activity.type.toUpperCase()}</div>
            <div class="activity-content">${activity.message}</div>
        `;
        
        feed.appendChild(entry);
    });
}

// Investigations
function handleInvestigationUpdate(investigations) {
    renderInvestigations(investigations);
    addActivity('investigation', `${investigations.length} active investigations`, 'info');
}

function renderInvestigations(investigations) {
    const panel = document.getElementById('investigations-panel');
    const list = panel.querySelector('.investigation-list');
    
    list.innerHTML = '';
    
    if (investigations.length === 0) {
        list.innerHTML = '<div class="text-muted text-center">No active investigations</div>';
    } else {
        investigations.forEach(inv => {
            const card = document.createElement('div');
            card.className = 'investigation-card';
            
            const progress = Math.floor(Math.random() * 100); // Simulate progress
            
            card.innerHTML = `
                <div class="investigation-header">
                    <div class="investigation-dlq">${inv.dlq}</div>
                    <div class="investigation-status active">Active</div>
                </div>
                <div class="investigation-progress">
                    <div class="investigation-progress-bar" style="width: ${progress}%"></div>
                </div>
                <small class="text-muted">Started: ${new Date(inv.startTime).toLocaleTimeString()}</small>
            `;
            
            list.appendChild(card);
        });
    }
    
    document.getElementById('investigation-count').textContent = investigations.length;
}

// Pull Requests
function handlePRUpdate(prs) {
    pullRequests = prs;
    renderPullRequests(prs);
    addActivity('pr', `${prs.length} open pull requests`, 'warning');
}

function renderPullRequests(prs) {
    const panel = document.getElementById('pr-panel');
    const list = panel.querySelector('.pr-list');
    
    list.innerHTML = '';
    
    const displayPrs = prs.slice(0, 3); // Show only 3 PRs
    
    displayPrs.forEach(pr => {
        const item = document.createElement('div');
        item.className = 'pr-item';
        item.onclick = () => window.open(pr.url, '_blank');
        
        item.innerHTML = `
            <div class="pr-status open"></div>
            <div class="flex-grow-1">
                <div class="pr-title">${pr.title}</div>
                <small class="text-muted">#${pr.number} - ${pr.repo}</small>
            </div>
        `;
        
        list.appendChild(item);
    });
    
    if (prs.length > 3) {
        list.innerHTML += `<div class="text-center mt-2"><small class="text-muted">+${prs.length - 3} more</small></div>`;
    }
    
    document.getElementById('pr-count').textContent = prs.length;
}

// Stats
function updateStats(stats) {
    // Update stats with animation
    animateNumber('messages-processed', stats.messagesProcessed || 0);
    animateNumber('investigations-today', stats.investigationsToday || 0);
    animateNumber('prs-created', stats.prsCreated || 0);
    animateNumber('issues-resolved', stats.issuesResolved || 0);
}

function animateNumber(elementId, target) {
    const element = document.getElementById(elementId);
    const current = parseInt(element.textContent) || 0;
    const increment = (target - current) / 20;
    let value = current;
    
    const timer = setInterval(() => {
        value += increment;
        if ((increment > 0 && value >= target) || (increment < 0 && value <= target)) {
            value = target;
            clearInterval(timer);
        }
        element.textContent = Math.floor(value);
    }, 50);
}

// Helper Functions
function updateConnectionStatus(connected) {
    const status = document.getElementById('connection-status');
    if (connected) {
        status.className = 'badge bg-success pulse';
        status.innerHTML = '<i class="fas fa-circle"></i> Connected';
    } else {
        status.className = 'badge bg-danger pulse-danger';
        status.innerHTML = '<i class="fas fa-circle"></i> Disconnected';
    }
}

function startClock() {
    setInterval(() => {
        document.getElementById('last-update').textContent = new Date().toLocaleTimeString();
    }, 1000);
}

function showAlert(message, type = 'info') {
    const toast = document.getElementById('alert-toast');
    const toastBody = toast.querySelector('.toast-body');
    toastBody.textContent = message;
    
    const bsToast = new bootstrap.Toast(toast);
    bsToast.show();
    
    addActivity('system', message, type);
}

function handleAlert(data) {
    showAlert(data.message, data.type);
}

function handleVoiceSettingsUpdate(data) {
    const icon = document.getElementById('voice-icon');
    if (data.enabled) {
        icon.className = 'fas fa-volume-up';
    } else {
        icon.className = 'fas fa-volume-mute';
    }
}

// Voice Toggle
function initializeVoiceToggle() {
    const toggle = document.getElementById('voice-toggle');
    let voiceEnabled = localStorage.getItem('voiceNotifications') !== 'false';
    
    updateVoiceIcon(voiceEnabled);
    socket.emit('voice_settings', { enabled: voiceEnabled });
    
    toggle.addEventListener('click', function() {
        voiceEnabled = !voiceEnabled;
        localStorage.setItem('voiceNotifications', voiceEnabled.toString());
        updateVoiceIcon(voiceEnabled);
        socket.emit('voice_settings', { enabled: voiceEnabled });
        showAlert(`Voice notifications ${voiceEnabled ? 'enabled' : 'disabled'}`, 'info');
    });
}

function updateVoiceIcon(enabled) {
    const icon = document.getElementById('voice-icon');
    if (enabled) {
        icon.className = 'fas fa-volume-up';
        document.getElementById('voice-toggle').classList.remove('btn-muted');
    } else {
        icon.className = 'fas fa-volume-mute';
        document.getElementById('voice-toggle').classList.add('btn-muted');
    }
}

// Action Functions
function refreshDLQs() {
    socket.emit('request_update');
    showAlert('Refreshing DLQ status...', 'info');
}

function toggleAgentDetails() {
    agentDetailsExpanded = !agentDetailsExpanded;
    const icon = document.getElementById('agent-expand-icon');
    icon.className = agentDetailsExpanded ? 'fas fa-compress-alt' : 'fas fa-expand-alt';
    renderAgents(agents);
}

function investigateDLQ(dlqName, messageCount) {
    socket.emit('start_investigation', { dlq: dlqName, messages: messageCount });
    showAlert(`Starting investigation for ${dlqName}`, 'success');
}

function triggerInvestigation(dlqName, messageCount) {
    if (messageCount > 100) {
        socket.emit('start_investigation', { dlq: dlqName, messages: messageCount });
        addActivity('investigation', `Auto-investigating ${dlqName} (${messageCount} messages)`, 'warning');
    }
}

function forceReinvestigation() {
    const criticalDlq = dlqQueues.find(dlq => dlq.messages > 100);
    if (criticalDlq) {
        investigateDLQ(criticalDlq.name, criticalDlq.messages);
    } else {
        showAlert('No critical DLQs to investigate', 'info');
    }
}

// Export functions for global access
window.refreshDLQs = refreshDLQs;
window.toggleAgentDetails = toggleAgentDetails;
window.investigateDLQ = investigateDLQ;
window.forceReinvestigation = forceReinvestigation;