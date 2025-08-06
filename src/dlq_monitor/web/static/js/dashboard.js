// LPD Digital Hive - DLQ Operations Center Dashboard
// Real-time monitoring with WebSocket and agent tracking

// Global variables
let socket;
let agents = {
    investigator: { status: 'idle', lastActivity: null, currentTask: null },
    analyzer: { status: 'idle', lastActivity: null, currentTask: null },
    debugger: { status: 'idle', lastActivity: null, currentTask: null },
    reviewer: { status: 'idle', lastActivity: null, currentTask: null }
};
let dlqData = [];
let investigations = [];
let pullRequests = [];
let recentActions = [];
let stats = {
    messagesProcessed: 0,
    investigationsToday: 0,
    prsCreated: 0,
    issuesResolved: 0
};

// Initialize on page load
document.addEventListener('DOMContentLoaded', function() {
    initializeWebSocket();
    loadInitialData();
    startClock();
    initializeToasts();
});

// WebSocket initialization
function initializeWebSocket() {
    socket = io();
    
    socket.on('connect', function() {
        console.log('Connected to WebSocket');
        updateConnectionStatus(true);
        addToTimeline('System connected to monitoring service');
    });
    
    socket.on('disconnect', function() {
        console.log('Disconnected from WebSocket');
        updateConnectionStatus(false);
        addToTimeline('System disconnected from monitoring service');
    });
    
    // DLQ Updates
    socket.on('dlq_update', function(data) {
        updateDLQStatus(data);
        updateStats(data);
    });
    
    // Agent Updates
    socket.on('agent_update', function(data) {
        updateAgentStatus(data);
    });
    
    // Investigation Updates
    socket.on('investigation_update', function(data) {
        updateInvestigations(data);
    });
    
    // PR Updates
    socket.on('pr_update', function(data) {
        updatePullRequests(data);
    });
    
    // Alert Messages
    socket.on('alert', function(data) {
        showAlert(data.message, data.type);
    });
}

// Load initial data
function loadInitialData() {
    fetch('/api/status')
        .then(response => response.json())
        .then(data => {
            if (data.dlqs) updateDLQStatus(data.dlqs);
            if (data.agents) updateAllAgents(data.agents);
            if (data.investigations) updateInvestigations(data.investigations);
            if (data.prs) updatePullRequests(data.prs);
            if (data.stats) updateStats(data.stats);
        })
        .catch(error => {
            console.error('Error loading initial data:', error);
            showAlert('Failed to load initial data', 'error');
        });
}

// Update Agent Status
function updateAgentStatus(agentData) {
    const agentId = agentData.id;
    const agentCard = document.getElementById(`${agentId}-agent`);
    
    if (!agentCard) return;
    
    // Update agent object
    if (agents[agentId]) {
        agents[agentId] = { ...agents[agentId], ...agentData };
    }
    
    // Update UI
    const statusElement = agentCard.querySelector('.agent-status');
    const lastActivityElement = agentCard.querySelector('.last-activity');
    const taskElement = agentCard.querySelector('.agent-task');
    const taskDescription = agentCard.querySelector('.task-description');
    
    // Update status
    statusElement.setAttribute('data-status', agentData.status);
    statusElement.innerHTML = `<i class="fas fa-circle"></i> ${capitalizeFirst(agentData.status)}`;
    
    // Update last activity
    if (agentData.lastActivity) {
        lastActivityElement.textContent = formatTime(agentData.lastActivity);
    }
    
    // Update current task
    if (agentData.currentTask) {
        taskElement.classList.remove('d-none');
        taskDescription.textContent = agentData.currentTask;
    } else {
        taskElement.classList.add('d-none');
    }
    
    // Update agent count
    updateAgentCount();
    
    // Add to timeline
    if (agentData.status === 'active') {
        addToTimeline(`${agentData.name} started: ${agentData.currentTask}`);
    }
}

// Update all agents at once
function updateAllAgents(agentsData) {
    Object.keys(agentsData).forEach(agentId => {
        updateAgentStatus({ id: agentId, ...agentsData[agentId] });
    });
}

// Update DLQ Status
function updateDLQStatus(dlqs) {
    dlqData = dlqs;
    const dlqPanel = document.getElementById('dlq-status-panel');
    const dlqList = dlqPanel.querySelector('.dlq-list');
    
    // Clear existing items
    dlqList.innerHTML = '';
    
    // Count by status
    let critical = 0, warning = 0, healthy = 0;
    
    dlqs.forEach(dlq => {
        const status = getDLQStatus(dlq.messages);
        if (status === 'critical') critical++;
        else if (status === 'warning') warning++;
        else healthy++;
        
        const dlqItem = createDLQItem(dlq, status);
        dlqList.appendChild(dlqItem);
    });
    
    // Update counters
    document.getElementById('critical-count').textContent = critical;
    document.getElementById('warning-count').textContent = warning;
    document.getElementById('healthy-count').textContent = healthy;
}

// Create DLQ Item element
function createDLQItem(dlq, status) {
    const div = document.createElement('div');
    const isCriticalAlert = dlq.messages >= 100;
    
    // Add critical alert class if messages >= 100
    div.className = `dlq-item ${status} ${isCriticalAlert ? 'critical-alert' : ''}`;
    div.innerHTML = `
        <div>
            <div class="dlq-name">
                ${dlq.name}
                ${isCriticalAlert ? '<span class="badge bg-danger pulse-danger ms-2">CRITICAL</span>' : ''}
            </div>
            <small class="text-muted">${dlq.region || 'sa-east-1'}</small>
        </div>
        <div class="dlq-messages">
            <span class="message-count text-${getStatusColor(status)}">${dlq.messages}</span>
            <small class="text-muted">msgs</small>
        </div>
    `;
    
    // Add click handler for investigation
    if (status !== 'healthy') {
        div.style.cursor = 'pointer';
        div.onclick = () => startInvestigation(dlq);
    }
    
    return div;
}

// Update Investigations
function updateInvestigations(investigationsData) {
    investigations = investigationsData;
    const panel = document.getElementById('investigations-panel');
    const list = panel.querySelector('.investigation-list');
    
    // Clear existing
    list.innerHTML = '';
    
    // Update count
    document.getElementById('investigation-count').textContent = investigationsData.length;
    
    investigationsData.forEach(inv => {
        const item = createInvestigationItem(inv);
        list.appendChild(item);
    });
}

// Create Investigation Item
function createInvestigationItem(inv) {
    const div = document.createElement('div');
    div.className = 'investigation-item';
    div.innerHTML = `
        <div class="d-flex justify-content-between align-items-center">
            <div>
                <div class="fw-semibold">${inv.dlq}</div>
                <small class="text-muted">${inv.agent} • Started ${formatTime(inv.startTime)}</small>
            </div>
            <div class="text-orange">
                <i class="fas fa-spinner fa-spin"></i>
            </div>
        </div>
        <div class="investigation-progress mt-2">
            <div class="investigation-progress-bar" style="width: ${inv.progress || 0}%"></div>
        </div>
    `;
    return div;
}

// Update Pull Requests
function updatePullRequests(prs) {
    pullRequests = prs;
    const panel = document.getElementById('pr-panel');
    const list = panel.querySelector('.pr-list');
    
    // Clear existing
    list.innerHTML = '';
    
    // Update count
    document.getElementById('pr-count').textContent = prs.length;
    
    prs.forEach(pr => {
        const item = createPRItem(pr);
        list.appendChild(item);
    });
}

// Create PR Item
function createPRItem(pr) {
    const div = document.createElement('div');
    div.className = 'pr-item';
    div.innerHTML = `
        <div class="pr-status ${pr.status}"></div>
        <div class="flex-grow-1">
            <div class="fw-semibold">#${pr.number}: ${pr.title}</div>
            <small class="text-muted">${pr.author} • ${formatTime(pr.createdAt)}</small>
        </div>
        <i class="fas fa-external-link-alt text-muted"></i>
    `;
    
    div.onclick = () => window.open(pr.url, '_blank');
    return div;
}

// Add to Timeline
function addToTimeline(message) {
    const timeline = document.querySelector('.timeline');
    if (!timeline) return;
    
    // Add to recent actions array
    recentActions.unshift({
        time: new Date(),
        message: message
    });
    
    // Keep only last 10 actions
    if (recentActions.length > 10) {
        recentActions.pop();
    }
    
    // Rebuild timeline
    timeline.innerHTML = '';
    recentActions.forEach(action => {
        const item = document.createElement('div');
        item.className = 'timeline-item';
        item.innerHTML = `
            <div class="timeline-time">${formatTime(action.time)}</div>
            <div class="timeline-content">${action.message}</div>
        `;
        timeline.appendChild(item);
    });
}

// Update Stats
function updateStats(data) {
    if (data.messagesProcessed !== undefined) {
        document.getElementById('messages-processed').textContent = data.messagesProcessed;
        stats.messagesProcessed = data.messagesProcessed;
    }
    if (data.investigationsToday !== undefined) {
        document.getElementById('investigations-today').textContent = data.investigationsToday;
        stats.investigationsToday = data.investigationsToday;
    }
    if (data.prsCreated !== undefined) {
        document.getElementById('prs-created').textContent = data.prsCreated;
        stats.prsCreated = data.prsCreated;
    }
    if (data.issuesResolved !== undefined) {
        document.getElementById('issues-resolved').textContent = data.issuesResolved;
        stats.issuesResolved = data.issuesResolved;
    }
}

// Update Connection Status
function updateConnectionStatus(connected) {
    const statusBadge = document.getElementById('connection-status');
    if (connected) {
        statusBadge.className = 'badge bg-success pulse';
        statusBadge.innerHTML = '<i class="fas fa-circle"></i> Connected';
    } else {
        statusBadge.className = 'badge bg-danger';
        statusBadge.innerHTML = '<i class="fas fa-circle"></i> Disconnected';
    }
}

// Update Agent Count
function updateAgentCount() {
    const activeAgents = Object.values(agents).filter(a => a.status !== 'idle').length;
    document.getElementById('agent-count').textContent = activeAgents;
}

// Start Investigation
function startInvestigation(dlq) {
    socket.emit('start_investigation', {
        dlq: dlq.name,
        messages: dlq.messages
    });
    
    showAlert(`Investigation started for ${dlq.name}`, 'info');
    addToTimeline(`Manual investigation triggered for ${dlq.name}`);
}

// Show Alert Toast
function showAlert(message, type = 'info') {
    const toast = document.getElementById('alert-toast');
    const toastBody = toast.querySelector('.toast-body');
    
    // Set message
    toastBody.textContent = message;
    
    // Set color based on type
    toast.className = `toast border-${type === 'error' ? 'danger' : type}`;
    
    // Show toast
    const bsToast = new bootstrap.Toast(toast);
    bsToast.show();
}

// Initialize Toasts
function initializeToasts() {
    const toastElList = [].slice.call(document.querySelectorAll('.toast'));
    toastElList.map(function (toastEl) {
        return new bootstrap.Toast(toastEl);
    });
}

// Start Clock
function startClock() {
    updateClock();
    setInterval(updateClock, 1000);
}

// Update Clock
function updateClock() {
    const now = new Date();
    const timeString = now.toLocaleTimeString('en-US', { 
        hour12: false,
        hour: '2-digit',
        minute: '2-digit',
        second: '2-digit'
    });
    
    const lastUpdate = document.getElementById('last-update');
    if (lastUpdate) {
        lastUpdate.textContent = timeString;
    }
}

// Utility Functions
function getDLQStatus(messageCount) {
    if (messageCount >= 100) return 'critical';
    if (messageCount >= 10) return 'warning';
    return 'healthy';
}

function getStatusColor(status) {
    switch(status) {
        case 'critical': return 'danger';
        case 'warning': return 'warning';
        case 'healthy': return 'success';
        default: return 'secondary';
    }
}

function formatTime(timestamp) {
    if (!timestamp) return 'Never';
    
    const date = new Date(timestamp);
    const now = new Date();
    const diff = now - date;
    
    if (diff < 60000) return 'Just now';
    if (diff < 3600000) return `${Math.floor(diff / 60000)}m ago`;
    if (diff < 86400000) return `${Math.floor(diff / 3600000)}h ago`;
    
    return date.toLocaleDateString('en-US', { 
        month: 'short', 
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    });
}

function capitalizeFirst(str) {
    return str.charAt(0).toUpperCase() + str.slice(1);
}

// Force Reinvestigation
function forceReinvestigation() {
    if (dlqData.length === 0) {
        showAlert('No DLQs to investigate', 'warning');
        return;
    }
    
    // Find the DLQ with most messages
    const targetDLQ = dlqData.reduce((prev, current) => 
        (prev.messages > current.messages) ? prev : current
    );
    
    if (targetDLQ.messages === 0) {
        showAlert('No messages in DLQs to investigate', 'info');
        return;
    }
    
    startInvestigation(targetDLQ);
    showAlert(`Force investigation started for ${targetDLQ.name}`, 'success');
}

// Add log entry to stream
function addLogEntry(message, type = 'info') {
    const logStream = document.querySelector('.log-stream');
    if (!logStream) return;
    
    const entry = document.createElement('div');
    entry.className = `log-entry ${type}`;
    entry.innerHTML = `<span class="text-muted">${formatTime(new Date())}</span> ${message}`;
    
    // Add to top of stream
    logStream.insertBefore(entry, logStream.firstChild);
    
    // Keep only last 50 entries
    while (logStream.children.length > 50) {
        logStream.removeChild(logStream.lastChild);
    }
}

// Simulate agent activity logs
function simulateAgentLogs() {
    const messages = [
        { text: 'Investigation Agent scanning DLQ queues...', type: 'info' },
        { text: 'DLQ Analyzer processing message patterns', type: 'info' },
        { text: 'Code Debugger identified potential fix', type: 'success' },
        { text: 'Code Reviewer validating changes', type: 'info' },
        { text: 'High message count detected in payment-dlq', type: 'error' },
        { text: 'Agent coordination successful', type: 'success' }
    ];
    
    // Add random log every 3-8 seconds
    setInterval(() => {
        if (Math.random() > 0.7) {
            const msg = messages[Math.floor(Math.random() * messages.length)];
            addLogEntry(msg.text, msg.type);
        }
    }, 5000);
}

// Initialize log streaming
document.addEventListener('DOMContentLoaded', function() {
    simulateAgentLogs();
    
    // Listen for real agent updates and add to log
    socket.on('agent_update', function(data) {
        if (data.status === 'active' || data.status === 'investigating') {
            addLogEntry(`${data.name} is now ${data.status}: ${data.currentTask || 'Processing...'}`, 'success');
        }
    });
    
    socket.on('dlq_update', function(data) {
        data.forEach(dlq => {
            if (dlq.messages >= 100) {
                addLogEntry(`⚠️ CRITICAL: ${dlq.name} has ${dlq.messages} messages!`, 'error');
            }
        });
    });
});

// Export for testing
if (typeof module !== 'undefined' && module.exports) {
    module.exports = {
        updateAgentStatus,
        updateDLQStatus,
        formatTime,
        forceReinvestigation,
        addLogEntry
    };
}