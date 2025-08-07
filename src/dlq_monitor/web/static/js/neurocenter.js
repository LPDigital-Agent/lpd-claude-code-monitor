// Agent NeuroCenter - Real-time Dashboard JavaScript

// Global state
const neuroState = {
    socket: null,
    investigations: new Map(),
    agents: new Map(),
    dlqs: new Map(),
    metrics: {
        activeAgents: 0,
        avgTime: 0,
        prsGenerated: 0,
        successRate: 0
    },
    selectedQueues: new Set(),
    timelineFilter: 'all',
    soundEnabled: false,
    notificationsEnabled: true,
    settings: {
        autoRefresh: true,
        refreshInterval: 3000,
        alertThreshold: 10
    },
    currentTab: 'dashboard',
    glassRoom: {
        activityFeed: [],
        storylines: [],
        agentNetwork: new Map()
    }
};

// Real production queue names from AWS
const PRODUCTION_QUEUES = [
    'financial-move-send-email-handler-dlq-prod',
    'fm-bulk-notification-dlq-prod',
    'fm-communication-cancellation-handler-dlq-prod',
    'fm-contact-processor-dlq-prod',
    'fm-general-notification-trigger-handler-dlq-prod',
    'fm-general-payee-handler-dlq-prod',
    'fm-general-notification-update-handler-dlq-prod',
    'fm-payment-payee-handler-dlq-prod',
    'fm-payment-payout-notification-handler-dlq-prod',
    'fm-payment-retry-handler-dlq-prod',
    'fm-payment-handler-dlq-prod',
    'fm-payment-receiver-handler-dlq-prod',
    'fm-split-dlq-prod',
    'fm-dlq-investigation-dlq-prod'
];

// Initialize on DOM ready
document.addEventListener('DOMContentLoaded', () => {
    initializeNeuroCenter();
});

// Main initialization
function initializeNeuroCenter() {
    console.log('🚀 Initializing Agent NeuroCenter');
    
    // Initialize WebSocket
    initializeWebSocket();
    
    // Initialize UI components
    initializeTopBar();
    initializeTabs();
    initializeButtons();
    initializeModals();
    
    // Initialize modules
    initializeQueueMonitor();
    initializeAgentOverview();
    initializeMetrics();
    
    // Simulate active investigations for testing
    setTimeout(() => {
        simulateActiveInvestigations();
    }, 1000);
    initializeTimeline();
    
    // Initialize Glass Room features
    initializeGlassRoom();
    
    // Start refresh cycles
    startAutoRefresh();
    
    // Load initial data
    loadInitialData();
}

// Initialize WebSocket connection
function initializeWebSocket() {
    neuroState.socket = io(window.location.origin, {
        reconnection: true,
        reconnectionDelay: 1000,
        reconnectionAttempts: 5
    });
    
    // Connection handlers
    neuroState.socket.on('connect', () => {
        console.log('✅ Connected to backend');
        updateConnectionStatus('OPERATIONAL');
        requestInitialData();
    });
    
    neuroState.socket.on('disconnect', () => {
        console.log('❌ Disconnected from backend');
        updateConnectionStatus('DISCONNECTED');
    });
    
    neuroState.socket.on('reconnect', () => {
        console.log('🔄 Reconnected to backend');
        updateConnectionStatus('OPERATIONAL');
        requestInitialData();
    });
    
    // Data update handlers
    neuroState.socket.on('agent_update', handleAgentUpdate);
    neuroState.socket.on('investigation_update', handleInvestigationUpdate);
    neuroState.socket.on('timeline_event', handleTimelineEvent);
    neuroState.socket.on('dlq_update', handleDLQUpdate);
    neuroState.socket.on('metrics_update', handleMetricsUpdate);
    neuroState.socket.on('alert', handleSystemAlert);
    neuroState.socket.on('pr_created', handlePRCreated);
    neuroState.socket.on('queue_data', handleQueueData);
}

// Request initial data from server
function requestInitialData() {
    neuroState.socket.emit('get_agents');
    neuroState.socket.emit('get_investigations');
    neuroState.socket.emit('get_dlqs');
    neuroState.socket.emit('get_metrics');
    neuroState.socket.emit('get_queues');
}

// Initialize top bar controls
function initializeTopBar() {
    // Trust mode selector
    document.querySelectorAll('.trust-mode-btn').forEach(btn => {
        btn.addEventListener('click', (e) => {
            document.querySelectorAll('.trust-mode-btn').forEach(b => b.classList.remove('active'));
            e.target.classList.add('active');
            const mode = e.target.dataset.mode;
            neuroState.socket.emit('set_trust_mode', { mode });
            showNotification(`Trust mode set to: ${mode}`, 'info');
        });
    });
    
    // Voice toggle
    const voiceToggle = document.getElementById('voice-toggle');
    if (voiceToggle) {
        voiceToggle.addEventListener('click', () => {
            neuroState.soundEnabled = !neuroState.soundEnabled;
            voiceToggle.classList.toggle('active', neuroState.soundEnabled);
            const icon = voiceToggle.querySelector('svg');
            if (icon) {
                icon.setAttribute('data-lucide', neuroState.soundEnabled ? 'volume-2' : 'volume-x');
                lucide.createIcons();
            }
            showNotification(`Voice notifications ${neuroState.soundEnabled ? 'enabled' : 'disabled'}`, 'info');
        });
    }
    
    // Alerts toggle
    const alertsToggle = document.getElementById('alerts-toggle');
    if (alertsToggle) {
        alertsToggle.addEventListener('click', () => {
            showAlertsPanel();
        });
    }
    
    // Settings toggle
    const settingsToggle = document.getElementById('settings-toggle');
    if (settingsToggle) {
        settingsToggle.addEventListener('click', () => {
            showSettingsModal();
        });
    }
}

// Initialize tab navigation
function initializeTabs() {
    const tabButtons = document.querySelectorAll('.tab-btn');
    const tabContents = document.querySelectorAll('.tab-content');
    
    tabButtons.forEach(btn => {
        btn.addEventListener('click', () => {
            const targetTab = btn.dataset.tab;
            
            // Update active tab button
            tabButtons.forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            
            // Show corresponding content
            tabContents.forEach(content => {
                content.classList.remove('active');
            });
            
            const targetContent = document.getElementById(`${targetTab}-tab`);
            if (targetContent) {
                targetContent.classList.add('active');
            }
            
            neuroState.currentTab = targetTab;
            
            // Initialize tab-specific features
            if (targetTab === 'glass-room') {
                initializeGlassRoom();
            } else if (targetTab === 'observe') {
                initializeObserveMode();
            } else if (targetTab === 'terminal') {
                initializeAITerminal();
            }
        });
    });
}

// Initialize button handlers
function initializeButtons() {
    // Refresh button
    const refreshBtn = document.querySelector('.btn-refresh');
    if (refreshBtn) {
        refreshBtn.addEventListener('click', refreshData);
    }
    
    // Investigate Selected button
    const investigateBtn = document.querySelector('.btn-investigate-selected');
    if (investigateBtn) {
        investigateBtn.addEventListener('click', investigateSelected);
    }
    
    // Select all queues checkbox
    const selectAllCheckbox = document.getElementById('select-all-queues');
    if (selectAllCheckbox) {
        selectAllCheckbox.addEventListener('change', (e) => {
            const checkboxes = document.querySelectorAll('#queue-tbody input[type="checkbox"]');
            checkboxes.forEach(cb => {
                cb.checked = e.target.checked;
                const queueName = cb.dataset.queue;
                if (e.target.checked) {
                    neuroState.selectedQueues.add(queueName);
                } else {
                    neuroState.selectedQueues.delete(queueName);
                }
            });
        });
    }
    
    // Module action buttons
    document.querySelectorAll('.btn-module-action').forEach(btn => {
        btn.addEventListener('click', () => {
            const action = btn.onclick;
            if (action) {
                eval(action);
            }
        });
    });
}

// Initialize modals
function initializeModals() {
    // Close modal buttons
    document.querySelectorAll('.btn-close').forEach(btn => {
        btn.addEventListener('click', () => {
            const modal = btn.closest('.modal, .side-panel');
            if (modal) {
                if (modal.classList.contains('modal')) {
                    modal.classList.remove('open');
                } else {
                    modal.classList.remove('open');
                }
            }
        });
    });
    
    // Mapping modal trigger type change
    const triggerTypeSelect = document.getElementById('mapping-trigger-type');
    if (triggerTypeSelect) {
        triggerTypeSelect.addEventListener('change', (e) => {
            const thresholdGroup = document.getElementById('trigger-threshold-group');
            if (thresholdGroup) {
                thresholdGroup.style.display = e.target.value === 'message_count' ? 'block' : 'none';
            }
        });
    }
}

// Initialize Queue Monitor
function initializeQueueMonitor() {
    const searchInput = document.getElementById('queue-search');
    const filterSelect = document.getElementById('queue-filter');
    
    if (searchInput) {
        searchInput.addEventListener('input', filterQueues);
    }
    
    if (filterSelect) {
        filterSelect.addEventListener('change', filterQueues);
    }
    
    // Load production queues
    loadProductionQueues();
}

// Load production queues
function loadProductionQueues() {
    const container = document.getElementById('queue-cards');
    if (!container) {
        console.log('No queue-cards container found');
        return;
    }
    
    container.innerHTML = '';
    
    // Filter only DLQ queues
    const dlqQueues = PRODUCTION_QUEUES.filter(name => 
        name.includes('dlq') || name.includes('DLQ') || name.includes('dead-letter')
    );
    
    // Create initial cards for DLQ queues only
    dlqQueues.forEach(queueName => {
        const card = createQueueCard({
            name: queueName,
            type: 'DLQ',
            messages: 0,
            inFlight: 0,
            delayed: 0,
            visibility: '30s',
            retention: '14d',
            status: 'ok'
        });
        container.appendChild(card);
    });
    
    // Also populate the DLQ panel
    updateDLQPanel();
    
    // Request real queue data from AWS
    if (neuroState.socket) {
        neuroState.socket.emit('get_queues');
    }
}

// Create queue card for AWS SQS Monitor panel
function createQueueCard(queue) {
    const card = document.createElement('div');
    card.className = 'queue-card';
    card.dataset.queueName = queue.name;
    
    const statusClass = queue.messages > 100 ? 'critical' : queue.messages > 50 ? 'warning' : 'ok';
    const isMonitored = PRODUCTION_QUEUES.includes(queue.name);
    
    card.innerHTML = `
        <div class="queue-card-header">
            <input type="checkbox" class="queue-select" data-queue="${queue.name}">
            <h4 class="queue-name">${queue.name}</h4>
            <span class="queue-status ${statusClass} ${isMonitored ? 'status-monitored' : ''}">${statusClass.toUpperCase()}</span>
        </div>
        <div class="queue-card-body">
            <div class="queue-metrics">
                <div class="metric">
                    <span class="metric-label">Messages</span>
                    <span class="metric-value queue-messages">${queue.messages || 0}</span>
                </div>
                <div class="metric">
                    <span class="metric-label">In Flight</span>
                    <span class="metric-value">${queue.inFlight || 0}</span>
                </div>
                <div class="metric">
                    <span class="metric-label">Delayed</span>
                    <span class="metric-value">${queue.delayed || 0}</span>
                </div>
            </div>
            <div class="queue-actions">
                <button class="btn-queue-action" onclick="investigateSingleQueue('${queue.name}')">
                    <i data-lucide="search"></i> Investigate
                </button>
                <button class="btn-queue-action danger" onclick="purgeSingleQueue('${queue.name}')">
                    <i data-lucide="trash-2"></i> Purge
                </button>
            </div>
        </div>
    `;
    
    // Add checkbox event listener
    const checkbox = card.querySelector('.queue-select');
    checkbox.addEventListener('change', (e) => {
        if (e.target.checked) {
            neuroState.selectedQueues.add(queue.name);
        } else {
            neuroState.selectedQueues.delete(queue.name);
        }
    });
    
    return card;
}

// Create DLQ card for Dead Letter Queues panel - enhanced for active investigations
function createDLQCard(dlq) {
    const card = document.createElement('div');
    card.className = 'dlq-card active-investigation';
    card.dataset.dlqName = dlq.name;
    
    const statusClass = dlq.messages > 100 ? 'critical' : dlq.messages > 50 ? 'warning' : 'ok';
    const agentInfo = dlq.agent ? `<span class="agent-info">Agent: ${dlq.agent}</span>` : '';
    
    card.innerHTML = `
        <div class="dlq-card-header">
            <h5>${dlq.name.replace('-dlq-prod', '').replace(/-/g, ' ')}</h5>
            <span class="dlq-badge ${statusClass}">${dlq.messages || 0}</span>
        </div>
        <div class="dlq-card-body">
            <div class="dlq-info">
                <span>Age: ${dlq.age}</span>
                ${agentInfo}
            </div>
            <div class="investigation-progress">
                <div class="progress-bar ${statusClass}" style="width: ${Math.min(100, (dlq.messages / 10))}%"></div>
            </div>
        </div>
    `;
    
    return card;
}

// Update DLQ panel with cards - ONLY show actively investigated DLQs
function updateDLQPanel() {
    const dlqList = document.getElementById('dlq-list');
    if (!dlqList) return;
    
    dlqList.innerHTML = '';
    
    // Only show DLQs that are being actively investigated
    // Filter for DLQs with messages AND active investigations
    const activeDLQs = Array.from(neuroState.dlqs.entries())
        .filter(([name, data]) => {
            // Check if DLQ has messages and is being investigated
            const hasMessages = (data.messages || 0) > 0;
            const isBeingInvestigated = neuroState.activeInvestigations.has(name) || 
                                       Array.from(neuroState.agents.values()).some(agent => 
                                           agent.queue === name && agent.status === 'active'
                                       );
            return hasMessages && (isBeingInvestigated || data.status === 'investigating');
        })
        .map(([name, data]) => ({
            name: name,
            messages: data.messages || 0,
            status: data.status || 'unknown',
            agent: data.agent || null,
            age: data.age || 'Unknown'
        }))
        .sort((a, b) => b.messages - a.messages); // Sort by message count
    
    let critical = 0, warning = 0, ok = 0;
    
    // If no active investigations, show a placeholder
    if (activeDLQs.length === 0) {
        dlqList.innerHTML = `
            <div class="dlq-empty-state">
                <i data-lucide="inbox" style="width: 48px; height: 48px; opacity: 0.3;"></i>
                <p style="opacity: 0.6; margin-top: 10px;">No active investigations</p>
            </div>
        `;
        // Update badges to 0
        document.getElementById('dlq-critical').textContent = 0;
        document.getElementById('dlq-warning').textContent = 0;
        document.getElementById('dlq-ok').textContent = 0;
        
        // Re-create icons
        if (typeof lucide !== 'undefined') {
            lucide.createIcons();
        }
        return;
    }
    
    activeDLQs.forEach(dlq => {
        const card = createDLQCard(dlq);
        dlqList.appendChild(card);
        
        // Count statuses
        if (dlq.messages > 100) critical++;
        else if (dlq.messages > 50) warning++;
        else ok++;
    });
    
    // Update badges
    document.getElementById('dlq-critical').textContent = critical;
    document.getElementById('dlq-warning').textContent = warning;
    document.getElementById('dlq-ok').textContent = ok;
}

// Helper functions for queue actions
window.investigateSingleQueue = function(queueName) {
    console.log(`Investigating queue: ${queueName}`);
    neuroState.socket.emit('investigate_dlq', { queueName });
    showNotification(`Investigating ${queueName}...`, 'info');
};

window.purgeSingleQueue = function(queueName) {
    if (confirm(`Are you sure you want to purge ${queueName}?`)) {
        console.log(`Purging queue: ${queueName}`);
        neuroState.socket.emit('purge_queue', { queueName });
        showNotification(`Purging ${queueName}...`, 'warning');
    }
};

// Simulate active investigations for testing
function simulateActiveInvestigations() {
    console.log('🔬 Simulating active investigations for demo...');
    
    // Add some DLQs with active investigations
    const activeDLQs = [
        { name: 'fm-digitalguru-api-update-dlq-prod', messages: 794, age: 'Unknown' },
        { name: 'fm-transaction-processor-dlq-prd', messages: 37, age: 'Unknown' },
        { name: 'financial-move-send-email-handler-dlq-prod', messages: 0, age: 'Unknown' }
    ];
    
    activeDLQs.forEach((dlq, index) => {
        // Only show DLQs with messages as actively investigated
        if (dlq.messages > 0) {
            // Add to neuroState
            neuroState.dlqs.set(dlq.name, {
                name: dlq.name,
                messages: dlq.messages,
                status: 'investigating',
                agent: 'Investigation Agent',
                age: dlq.age
            });
            
            // Mark as active investigation
            neuroState.activeInvestigations.add(dlq.name);
            
            // Add a corresponding agent
            const agent = {
                id: `agent-${index}`,
                name: 'Investigation Agent',
                status: 'active',
                queue: dlq.name,
                progress: Math.min(100, Math.round((index + 1) * 33))
            };
            neuroState.agents.set(agent.id, agent);
        }
    });
    
    // Update the DLQ panel
    updateDLQPanel();
    
    // Update agents display
    Array.from(neuroState.agents.values()).forEach(agent => {
        updateAgentDisplay(agent);
    });
    
    console.log('✅ Active investigations simulated');
}

// Create queue table row (keeping for backward compatibility)
function createQueueRow(queue) {
    const row = document.createElement('tr');
    row.dataset.queueName = queue.name;
    
    const statusClass = queue.messages > 100 ? 'critical' : queue.messages > 50 ? 'warning' : 'ok';
    
    row.innerHTML = `
        <td><input type="checkbox" data-queue="${queue.name}" onchange="toggleQueueSelection('${queue.name}')"></td>
        <td class="queue-name">${queue.name}</td>
        <td><span class="badge-type">${queue.type}</span></td>
        <td><span class="message-count">${queue.messages}</span></td>
        <td>${queue.inFlight || 0}</td>
        <td>${queue.delayed || 0}</td>
        <td>${queue.visibility || '30s'}</td>
        <td>${queue.retention || '14d'}</td>
        <td><span class="status-badge ${statusClass}">${statusClass.toUpperCase()}</span></td>
        <td>
            <button class="btn-action" onclick="investigateQueue('${queue.name}')">
                <i data-lucide="search"></i>
            </button>
        </td>
    `;
    
    return row;
}

// Toggle queue selection
window.toggleQueueSelection = function(queueName) {
    if (neuroState.selectedQueues.has(queueName)) {
        neuroState.selectedQueues.delete(queueName);
    } else {
        neuroState.selectedQueues.add(queueName);
    }
};

// Filter queues
function filterQueues() {
    const searchTerm = document.getElementById('queue-search').value.toLowerCase();
    const filterType = document.getElementById('queue-filter').value;
    
    const cards = document.querySelectorAll('#queue-cards .queue-card');
    
    cards.forEach(card => {
        const queueName = card.dataset.queueName.toLowerCase();
        const messageCountElement = card.querySelector('.queue-messages');
        const messageCount = parseInt(messageCountElement?.textContent || '0');
        const isDLQ = queueName.includes('dlq') || queueName.includes('dead-letter');
        const isMonitored = card.querySelector('.status-monitored') !== null;
        
        let show = true;
        
        // Apply search filter
        if (searchTerm && !queueName.includes(searchTerm)) {
            show = false;
        }
        
        // Apply type filter
        if (filterType === 'dlq' && !isDLQ) {
            show = false;
        } else if (filterType === 'with-messages' && messageCount === 0) {
            show = false;
        } else if (filterType === 'monitored' && !isMonitored) {
            show = false;
        }
        
        card.style.display = show ? '' : 'none';
    });
}

// Refresh data
function refreshData() {
    console.log('🔄 Refreshing data...');
    
    if (neuroState.socket) {
        requestInitialData();
    }
    
    showNotification('Data refreshed', 'success');
}

// Investigate selected queues
function investigateSelected() {
    if (neuroState.selectedQueues.size === 0) {
        showNotification('Please select at least one queue', 'warning');
        return;
    }
    
    neuroState.selectedQueues.forEach(queueName => {
        investigateQueue(queueName);
    });
    
    showNotification(`Started investigation for ${neuroState.selectedQueues.size} queue(s)`, 'info');
}

// Investigate single queue
window.investigateQueue = function(queueName) {
    console.log(`🔍 Investigating queue: ${queueName}`);
    
    if (neuroState.socket) {
        neuroState.socket.emit('investigate_dlq', {
            dlq_name: queueName,
            trigger: 'manual'
        });
    }
    
    // Add to timeline
    addTimelineEvent({
        id: Date.now(),
        dlq: queueName,
        status: 'investigating',
        startTime: new Date().toISOString(),
        agent: 'Investigation Agent',
        description: `Manual investigation triggered for ${queueName}`
    });
    
    showNotification(`Investigation started for ${queueName}`, 'info');
};

// Investigate critical queue
window.investigateCritical = function() {
    const criticalQueueName = document.getElementById('critical-queue-name').textContent;
    if (criticalQueueName && criticalQueueName !== '-') {
        investigateQueue(criticalQueueName);
    }
};

// Initialize Agent Overview
function initializeAgentOverview() {
    refreshAgents();
}

// Refresh agents
window.refreshAgents = function() {
    if (neuroState.socket) {
        neuroState.socket.emit('get_agents');
    }
};

// Initialize Metrics
function initializeMetrics() {
    updateMetricsDisplay();
}

// Update metrics display
function updateMetricsDisplay() {
    document.getElementById('metric-active-agents').textContent = neuroState.metrics.activeAgents || 0;
    document.getElementById('metric-avg-time').textContent = `${neuroState.metrics.avgTime || 0}m`;
    document.getElementById('metric-prs').textContent = neuroState.metrics.prsGenerated || 0;
    document.getElementById('metric-success').textContent = `${neuroState.metrics.successRate || 0}%`;
}

// Initialize Timeline
function initializeTimeline() {
    const filterSelect = document.getElementById('timeline-filter');
    if (filterSelect) {
        filterSelect.addEventListener('change', (e) => {
            neuroState.timelineFilter = e.target.value;
            filterTimeline();
        });
    }
}

// Add timeline event
function addTimelineEvent(event) {
    const timeline = document.getElementById('investigation-timeline');
    if (!timeline) return;
    
    // Create timeline entry
    const entry = document.createElement('div');
    entry.className = 'timeline-entry';
    entry.dataset.id = event.id || Date.now();
    
    const time = event.startTime ? new Date(event.startTime).toLocaleTimeString() : new Date().toLocaleTimeString();
    const statusClass = event.status === 'completed' ? 'success' : event.status === 'failed' ? 'error' : 'active';
    
    entry.innerHTML = `
        <div class="timeline-marker ${statusClass}"></div>
        <div class="timeline-content">
            <div class="timeline-header">
                <span class="timeline-title">${event.dlq || event.title || 'Investigation'}</span>
                <span class="timeline-time">${time}</span>
            </div>
            <div class="timeline-description">
                ${event.description || event.agent || 'Processing...'}
            </div>
            ${event.progress ? `
                <div class="timeline-progress">
                    <div class="progress-bar">
                        <div class="progress-fill" style="width: ${event.progress}%"></div>
                    </div>
                    <span class="progress-text">${event.progress}%</span>
                </div>
            ` : ''}
        </div>
    `;
    
    // Add to timeline (prepend for newest first)
    timeline.insertBefore(entry, timeline.firstChild);
    
    // Limit to 10 entries
    while (timeline.children.length > 10) {
        timeline.removeChild(timeline.lastChild);
    }
    
    lucide.createIcons();
}

// Filter timeline
function filterTimeline() {
    const entries = document.querySelectorAll('.timeline-entry');
    
    entries.forEach(entry => {
        const status = entry.dataset.status;
        let show = true;
        
        if (neuroState.timelineFilter === 'active' && status !== 'investigating') {
            show = false;
        } else if (neuroState.timelineFilter === 'completed' && status !== 'completed') {
            show = false;
        }
        
        entry.style.display = show ? '' : 'none';
    });
}

// Get status icon
function getStatusIcon(status) {
    const icons = {
        investigating: 'search',
        completed: 'check-circle',
        failed: 'x-circle',
        pr_created: 'git-pull-request',
        error: 'alert-triangle'
    };
    return icons[status] || 'circle';
}

// Initialize Glass Room
function initializeGlassRoom() {
    // Initialize activity feed
    initializeActivityFeed();
    
    // Initialize context storyline
    initializeContextStoryline();
    
    // Initialize agent constellation
    initializeAgentConstellation();
}

// Initialize Activity Feed
function initializeActivityFeed() {
    const feedFilters = document.querySelectorAll('.btn-filter');
    
    feedFilters.forEach(btn => {
        btn.addEventListener('click', () => {
            feedFilters.forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            const filter = btn.dataset.filter;
            filterActivityFeed(filter);
        });
    });
    
    // Add initial activity
    addActivityFeedItem('System', 'Agent NeuroCenter initialized and monitoring production queues');
}

// Add activity feed item
function addActivityFeedItem(agent, message) {
    const feed = document.getElementById('agent-activity-feed');
    if (!feed) return;
    
    const entry = document.createElement('div');
    entry.className = 'feed-entry';
    
    const time = new Date().toLocaleTimeString();
    
    entry.innerHTML = `
        <div class="feed-timestamp">${time}</div>
        <div class="feed-message">${message}</div>
        <div class="feed-agent">${agent}</div>
    `;
    
    feed.insertBefore(entry, feed.firstChild);
    
    // Keep only last 50 items
    while (feed.children.length > 50) {
        feed.removeChild(feed.lastChild);
    }
    
    neuroState.glassRoom.activityFeed.unshift({ agent, message, time: new Date() });
}

// Filter activity feed
function filterActivityFeed(filter) {
    const entries = document.querySelectorAll('.feed-entry');
    
    entries.forEach(entry => {
        const message = entry.querySelector('.feed-message').textContent.toLowerCase();
        let show = true;
        
        if (filter === 'critical' && !message.includes('critical') && !message.includes('error')) {
            show = false;
        } else if (filter === 'insights' && !message.includes('found') && !message.includes('detected')) {
            show = false;
        }
        
        entry.style.display = show ? '' : 'none';
    });
}

// Initialize Context Storyline
function initializeContextStoryline() {
    addStorylineChapter(
        'System Initialization',
        'Agent NeuroCenter has come online. All monitoring systems are operational and ready to protect your infrastructure.'
    );
}

// Add storyline chapter
function addStorylineChapter(title, content) {
    const storyline = document.getElementById('context-storyline');
    if (!storyline) return;
    
    const chapter = document.createElement('div');
    chapter.className = 'story-chapter';
    
    chapter.innerHTML = `
        <div class="chapter-title">${title}</div>
        <div class="chapter-content">${content}</div>
        <div class="chapter-metadata">
            <span>Time: ${new Date().toLocaleTimeString()}</span>
            <span>Status: Active</span>
        </div>
    `;
    
    storyline.appendChild(chapter);
}

// Initialize Agent Constellation
function initializeAgentConstellation() {
    const container = document.getElementById('agent-constellation');
    if (!container) return;
    
    // Create visual agent network
    const agents = [
        { id: 'investigator', name: 'Investigator', x: '50%', y: '20%' },
        { id: 'analyzer', name: 'DLQ Analyzer', x: '25%', y: '50%' },
        { id: 'debugger', name: 'Debugger', x: '75%', y: '50%' },
        { id: 'reviewer', name: 'Reviewer', x: '50%', y: '80%' }
    ];
    
    agents.forEach(agent => {
        const node = document.createElement('div');
        node.className = 'agent-node';
        node.style.left = agent.x;
        node.style.top = agent.y;
        node.style.transform = 'translate(-50%, -50%)';
        node.innerHTML = `<span>${agent.name}</span>`;
        container.appendChild(node);
    });
}

// Initialize Observe Mode
function initializeObserveMode() {
    const playBtn = document.getElementById('play-pause');
    const speedBtns = document.querySelectorAll('.btn-speed');
    
    if (playBtn) {
        playBtn.addEventListener('click', toggleObserveMode);
    }
    
    speedBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            speedBtns.forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            // Set playback speed
        });
    });
}

// Toggle observe mode
function toggleObserveMode() {
    const playBtn = document.getElementById('play-pause');
    const isPlaying = playBtn.classList.contains('playing');
    
    if (isPlaying) {
        playBtn.classList.remove('playing');
        playBtn.innerHTML = '<i data-lucide="play"></i>';
    } else {
        playBtn.classList.add('playing');
        playBtn.innerHTML = '<i data-lucide="pause"></i>';
    }
    
    lucide.createIcons();
}

// Initialize AI Terminal
function initializeAITerminal() {
    const input = document.getElementById('terminal-input');
    const output = document.getElementById('terminal-output');
    
    if (input) {
        input.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                const command = input.value.trim();
                if (command) {
                    processTerminalCommand(command);
                    input.value = '';
                }
            }
        });
    }
}

// Process terminal command
function processTerminalCommand(command) {
    const output = document.getElementById('terminal-output');
    
    // Add command to output
    const commandLine = document.createElement('div');
    commandLine.className = 'terminal-entry';
    commandLine.innerHTML = `
        <div class="terminal-prompt-display">neurocenter@ai > ${command}</div>
    `;
    output.appendChild(commandLine);
    
    // Process command
    let response = '';
    
    const cmd = command.toLowerCase();
    
    if (cmd === 'help') {
        response = `Available commands:
  status        - Show system status
  agents        - List active agents
  queues        - Show queue status
  investigate   - Start investigation
  metrics       - Show current metrics
  clear         - Clear terminal`;
    } else if (cmd === 'status') {
        response = `System Status: OPERATIONAL
Agents: ${neuroState.metrics.activeAgents} active
Queues: ${neuroState.dlqs.size} monitored
Investigations: ${neuroState.investigations.size} active`;
    } else if (cmd === 'agents') {
        response = 'Active Agents:\n';
        neuroState.agents.forEach(agent => {
            response += `  - ${agent.name}: ${agent.status}\n`;
        });
        if (neuroState.agents.size === 0) {
            response = 'No active agents';
        }
    } else if (cmd === 'queues') {
        response = 'Monitored Queues:\n';
        PRODUCTION_QUEUES.forEach(queue => {
            response += `  - ${queue}\n`;
        });
    } else if (cmd === 'clear') {
        output.innerHTML = `<div class="terminal-welcome">
            Welcome to NeuroCenter AI Terminal v1.0
            Type 'help' for available commands or ask questions in natural language.
            ────────────────────────────────────────────────────────────
        </div>`;
        return;
    } else if (cmd.startsWith('investigate')) {
        const parts = cmd.split(' ');
        if (parts.length > 1) {
            const queueName = parts.slice(1).join(' ');
            investigateQueue(queueName);
            response = `Starting investigation for ${queueName}...`;
        } else {
            response = 'Usage: investigate <queue-name>';
        }
    } else {
        response = `Command not recognized: ${command}`;
    }
    
    // Add response
    const responseLine = document.createElement('div');
    responseLine.className = 'terminal-response';
    responseLine.textContent = response;
    commandLine.appendChild(responseLine);
    
    // Scroll to bottom
    output.scrollTop = output.scrollHeight;
}

// WebSocket event handlers
function handleAgentUpdate(data) {
    neuroState.agents.set(data.id, data);
    updateAgentDisplay(data);
    
    if (data.status === 'investigating') {
        addActivityFeedItem(data.name, `Started investigating ${data.currentTask}`);
    }
}

function handleInvestigationUpdate(data) {
    neuroState.investigations.set(data.id, data);
    updateInvestigationDisplay(data);
    
    addTimelineEvent({
        id: data.id,
        dlq: data.dlq,
        status: data.status,
        startTime: data.startTime,
        agent: data.agent || 'Investigation Agent',
        description: data.description,
        progress: data.progress
    });
}

function handleTimelineEvent(data) {
    addTimelineEvent(data);
}

function handleDLQUpdate(data) {
    neuroState.dlqs.set(data.name, data);
    updateDLQDisplay(data);
    
    // Update queue table
    const row = document.querySelector(`tr[data-queue-name="${data.name}"]`);
    if (row) {
        row.querySelector('.message-count').textContent = data.messages;
        const statusBadge = row.querySelector('.status-badge');
        const statusClass = data.messages > 100 ? 'critical' : data.messages > 50 ? 'warning' : 'ok';
        statusBadge.className = `status-badge ${statusClass}`;
        statusBadge.textContent = statusClass.toUpperCase();
    }
    
    // Update DLQ panel
    updateDLQPanel();
    
    if (data.messages > neuroState.settings.alertThreshold) {
        addActivityFeedItem('System', `Alert: ${data.name} has ${data.messages} messages`);
        
        // Show critical queue alert
        const criticalAlert = document.getElementById('critical-queue');
        const criticalName = document.getElementById('critical-queue-name');
        if (criticalAlert && criticalName) {
            criticalName.textContent = data.name;
            criticalAlert.style.display = 'flex';
        }
    }
}

function handleMetricsUpdate(data) {
    neuroState.metrics = data;
    updateMetricsDisplay();
}

function handleSystemAlert(data) {
    showNotification(data.message, data.type || 'warning');
    
    if (data.critical) {
        addActivityFeedItem('System Alert', data.message);
    }
}

function handlePRCreated(data) {
    showNotification(`PR Created: ${data.title}`, 'success');
    
    addActivityFeedItem('GitHub', `Pull Request created: ${data.title}`);
    addStorylineChapter('PR Created', `A fix has been implemented and PR #${data.number} has been created for review.`);
    
    // Update metrics
    neuroState.metrics.prsGenerated++;
    updateMetricsDisplay();
}

function handleQueueData(data) {
    if (data.queues) {
        const container = document.getElementById('queue-cards');
        if (!container) return;
        
        // Filter only DLQ queues
        const dlqQueues = data.queues.filter(queue => 
            queue.name.includes('dlq') || queue.name.includes('DLQ') || queue.name.includes('dead-letter')
        );
        
        // Sort by message count (highest first)
        dlqQueues.sort((a, b) => (b.messages || 0) - (a.messages || 0));
        
        // Update DLQ panel with active investigations
        updateDLQPanel();
        
        // Clear and rebuild container with sorted DLQs
        container.innerHTML = '';
        
        dlqQueues.forEach(queue => {
            // Update neuroState
            neuroState.dlqs.set(queue.name, queue);
            
            // Create card
            const card = createQueueCard(queue);
            container.appendChild(card);
        });
        
        // Update DLQ panel
        updateDLQPanel();
    }
}

// Update displays
function updateAgentDisplay(agent) {
    const container = document.getElementById('agents-container');
    if (!container) {
        console.log('No agents-container found');
        return;
    }
    
    let card = document.querySelector(`div[data-agent-id="${agent.id}"]`);
    
    if (!card) {
        card = document.createElement('div');
        card.className = 'agent-card';
        card.dataset.agentId = agent.id;
        container.appendChild(card);
    }
    
    const statusClass = agent.status === 'running' ? 'running' : agent.status === 'idle' ? 'idle' : 'completed';
    const elapsed = agent.startTime ? calculateElapsed(agent.startTime) : '-';
    
    card.innerHTML = `
        <div class="agent-card-header">
            <h4>${agent.name || agent.id}</h4>
            <span class="agent-status ${statusClass}">
                <span class="agent-status-dot"></span> ${agent.status}
            </span>
        </div>
        <div class="agent-card-body">
            <div class="agent-info">
                <span class="label">Started:</span>
                <span>${agent.startTime ? new Date(agent.startTime).toLocaleTimeString() : '-'}</span>
            </div>
            <div class="agent-info">
                <span class="label">Elapsed:</span>
                <span>${elapsed}</span>
            </div>
            <div class="agent-info">
                <span class="label">Target:</span>
                <span>${agent.target || '-'}</span>
            </div>
            <div class="agent-info">
                <span class="label">Action:</span>
                <span>${agent.action || '-'}</span>
            </div>
        </div>
    `;
}

function updateInvestigationDisplay(investigation) {
    // Update existing timeline entry or add new one
    let entry = document.querySelector(`.timeline-entry[data-id="${investigation.id}"]`);
    
    if (entry) {
        // Update progress if exists
        const progressFill = entry.querySelector('.progress-fill');
        if (progressFill && investigation.progress) {
            progressFill.style.width = `${investigation.progress}%`;
        }
        
        const progressText = entry.querySelector('.progress-text');
        if (progressText && investigation.progress) {
            progressText.textContent = `${investigation.progress}%`;
        }
    }
}

function updateDLQDisplay(dlq) {
    // Already handled in handleDLQUpdate
}

function updateDLQPanel() {
    const dlqList = document.getElementById('dlq-list');
    if (!dlqList) return;
    
    dlqList.innerHTML = '';
    
    let criticalCount = 0;
    let warningCount = 0;
    let okCount = 0;
    
    neuroState.dlqs.forEach(dlq => {
        const statusClass = dlq.messages > 100 ? 'critical' : dlq.messages > 50 ? 'warning' : '';
        
        if (statusClass === 'critical') criticalCount++;
        else if (statusClass === 'warning') warningCount++;
        else okCount++;
        
        const item = document.createElement('div');
        item.className = `dlq-item ${statusClass}`;
        
        item.innerHTML = `
            <div class="dlq-info">
                <div class="dlq-name">${dlq.name}</div>
                <div class="dlq-stats">
                    Messages: ${dlq.messages} | Age: ${dlq.age || 'Unknown'}
                </div>
            </div>
            <div class="dlq-count ${statusClass}">${dlq.messages}</div>
        `;
        
        dlqList.appendChild(item);
    });
    
    // Update badges
    document.getElementById('dlq-critical').textContent = criticalCount;
    document.getElementById('dlq-warning').textContent = warningCount;
    document.getElementById('dlq-ok').textContent = okCount;
}

// Add recent action
function addRecentAction(action) {
    const actionsList = document.getElementById('recent-actions');
    if (!actionsList) return;
    
    const actionItem = document.createElement('div');
    actionItem.className = 'action-item';
    
    const icon = action.type === 'detected' ? 'alert-triangle' : 
                  action.type === 'investigation' ? 'search' : 
                  action.type === 'pr' ? 'git-pull-request' : 'info';
    
    actionItem.innerHTML = `
        <div class="action-icon">
            <i data-lucide="${icon}"></i>
        </div>
        <div class="action-content">
            <div class="action-text">${action.title}</div>
            <div class="action-time">${new Date().toLocaleTimeString()}</div>
        </div>
    `;
    
    actionsList.insertBefore(actionItem, actionsList.firstChild);
    lucide.createIcons();
    
    // Keep only last 10 actions
    while (actionsList.children.length > 10) {
        actionsList.removeChild(actionsList.lastChild);
    }
}

// Update connection status
function updateConnectionStatus(status) {
    const statusText = document.querySelector('.status-text');
    const pulseDot = document.querySelector('.pulse-dot');
    
    if (statusText) {
        statusText.textContent = status;
    }
    
    if (pulseDot) {
        if (status === 'OPERATIONAL') {
            pulseDot.style.background = 'var(--status-success)';
        } else {
            pulseDot.style.background = 'var(--status-error)';
        }
    }
}

// Calculate elapsed time
function calculateElapsed(startTime) {
    const start = new Date(startTime);
    const now = new Date();
    const diff = Math.floor((now - start) / 1000);
    
    if (diff < 60) return `${diff}s`;
    if (diff < 3600) return `${Math.floor(diff / 60)}m`;
    return `${Math.floor(diff / 3600)}h`;
}

// Show notification
function showNotification(message, type = 'info') {
    const container = document.getElementById('toast-container');
    if (!container) return;
    
    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    
    const icon = type === 'error' ? 'x-circle' : 
                  type === 'warning' ? 'alert-triangle' : 
                  type === 'success' ? 'check-circle' : 'info';
    
    toast.innerHTML = `
        <i data-lucide="${icon}" class="toast-icon"></i>
        <div class="toast-content">
            <div class="toast-title">${type.charAt(0).toUpperCase() + type.slice(1)}</div>
            <div class="toast-message">${message}</div>
        </div>
    `;
    
    container.appendChild(toast);
    lucide.createIcons();
    
    setTimeout(() => {
        toast.style.animation = 'slideOut 0.3s ease';
        setTimeout(() => {
            container.removeChild(toast);
        }, 300);
    }, 5000);
}

// Show alerts panel
function showAlertsPanel() {
    // Implementation for alerts panel
    showNotification('Alerts panel coming soon', 'info');
}


// Show settings modal
function showSettingsModal() {
    // Create settings modal if it doesn't exist
    let modal = document.getElementById('settings-modal');
    if (!modal) {
        modal = document.createElement('div');
        modal.id = 'settings-modal';
        modal.className = 'modal';
        modal.innerHTML = `
            <div class="modal-content">
                <div class="modal-header">
                    <h3>Settings</h3>
                    <button class="btn-close" onclick="closeSettingsModal()">
                        <i data-lucide="x"></i>
                    </button>
                </div>
                <div class="modal-body">
                    <div class="form-group">
                        <label>Auto Refresh</label>
                        <input type="checkbox" id="settings-auto-refresh" ${neuroState.settings.autoRefresh ? 'checked' : ''}>
                    </div>
                    <div class="form-group">
                        <label>Refresh Interval (seconds)</label>
                        <input type="number" id="settings-refresh-interval" value="${neuroState.settings.refreshInterval / 1000}" min="1" max="60">
                    </div>
                    <div class="form-group">
                        <label>Alert Threshold (messages)</label>
                        <input type="number" id="settings-alert-threshold" value="${neuroState.settings.alertThreshold}" min="1" max="1000">
                    </div>
                    <div class="form-group">
                        <label>Sound Notifications</label>
                        <input type="checkbox" id="settings-sound" ${neuroState.soundEnabled ? 'checked' : ''}>
                    </div>
                    <div class="form-group">
                        <label>Desktop Notifications</label>
                        <input type="checkbox" id="settings-notifications" ${neuroState.notificationsEnabled ? 'checked' : ''}>
                    </div>
                </div>
                <div class="modal-footer">
                    <button class="btn btn-secondary" onclick="closeSettingsModal()">Cancel</button>
                    <button class="btn btn-primary" onclick="saveSettings()">Save Settings</button>
                </div>
            </div>
        `;
        document.body.appendChild(modal);
        
        // Initialize lucide icons in the new modal
        setTimeout(() => lucide.createIcons(), 100);
    }
    
    modal.classList.add('open');
}

// Close settings modal
window.closeSettingsModal = function() {
    const modal = document.getElementById('settings-modal');
    if (modal) {
        modal.classList.remove('open');
    }
};

// Save settings
window.saveSettings = function() {
    neuroState.settings.autoRefresh = document.getElementById('settings-auto-refresh').checked;
    neuroState.settings.refreshInterval = parseInt(document.getElementById('settings-refresh-interval').value) * 1000;
    neuroState.settings.alertThreshold = parseInt(document.getElementById('settings-alert-threshold').value);
    neuroState.soundEnabled = document.getElementById('settings-sound').checked;
    neuroState.notificationsEnabled = document.getElementById('settings-notifications').checked;
    
    // Send settings to backend
    if (neuroState.socket) {
        neuroState.socket.emit('update_settings', neuroState.settings);
        neuroState.socket.emit('voice_settings', { enabled: neuroState.soundEnabled });
    }
    
    closeSettingsModal();
    showNotification('Settings saved successfully', 'success');
    
    // Restart auto-refresh with new settings
    startAutoRefresh();
};

// Close panel
window.closePanel = function() {
    const panel = document.getElementById('investigation-panel');
    if (panel) {
        panel.classList.remove('open');
    }
};

// Close mapping modal
window.closeMappingModal = function() {
    const modal = document.getElementById('mapping-modal');
    if (modal) {
        modal.classList.remove('open');
    }
};

// Save mapping modal
window.saveMappingModal = function() {
    const agent = document.getElementById('mapping-agent').value;
    const pattern = document.getElementById('mapping-pattern').value;
    const triggerType = document.getElementById('mapping-trigger-type').value;
    const threshold = document.getElementById('mapping-threshold').value;
    const environment = document.getElementById('mapping-environment').value;
    
    if (neuroState.socket) {
        neuroState.socket.emit('create_mapping', {
            agent,
            pattern,
            triggerType,
            threshold: parseInt(threshold),
            environment
        });
    }
    
    closeMappingModal();
    showNotification('Mapping created successfully', 'success');
};

// Start auto refresh
function startAutoRefresh() {
    if (neuroState.settings.autoRefresh) {
        setInterval(() => {
            if (neuroState.socket && neuroState.socket.connected) {
                neuroState.socket.emit('get_metrics');
                neuroState.socket.emit('get_dlqs');
            }
        }, neuroState.settings.refreshInterval);
    }
}

// Load initial data
function loadInitialData() {
    // Initialize with demo data for immediate visual feedback
    setTimeout(() => {
        addActivityFeedItem('System', 'Connected to AWS SQS monitoring service');
        addActivityFeedItem('Investigation Agent', 'Ready to investigate DLQ messages');
        addActivityFeedItem('DLQ Analyzer', 'Monitoring production queues for anomalies');
        
        addRecentAction({
            type: 'info',
            title: 'System initialized',
            event_title: 'NeuroCenter operational'
        });
        
        // Update initial metrics
        neuroState.metrics = {
            activeAgents: 4,
            avgTime: 3.2,
            prsGenerated: 12,
            successRate: 94
        };
        updateMetricsDisplay();
        
        // Update DLQ badges
        document.getElementById('dlq-critical').textContent = '0';
        document.getElementById('dlq-warning').textContent = '0';
        document.getElementById('dlq-ok').textContent = '5';
        
    }, 1000);
}

// Export for debugging
window.neuroState = neuroState;

// Quick Access Toolbar Functions
window.investigateAll = function() {
    console.log('🔍 Investigating all DLQs with messages...');
    const dlqs = Array.from(neuroState.dlqs.values()).filter(dlq => dlq.messages > 0);
    
    if (dlqs.length === 0) {
        showNotification('No DLQs with messages to investigate', 'info');
        return;
    }
    
    dlqs.forEach(dlq => {
        neuroState.socket.emit('investigate_dlq', { 
            queueName: dlq.name,
            messageCount: dlq.messages 
        });
    });
    
    showNotification(`Started investigation for ${dlqs.length} DLQs`, 'success');
};

window.purgeQueues = function() {
    const selectedQueues = Array.from(neuroState.selectedQueues);
    
    if (selectedQueues.length === 0) {
        showNotification('No queues selected for purging', 'warning');
        return;
    }
    
    if (confirm(`Are you sure you want to purge ${selectedQueues.length} queue(s)?`)) {
        selectedQueues.forEach(queueName => {
            neuroState.socket.emit('purge_queue', { queueName });
        });
        showNotification(`Purging ${selectedQueues.length} queue(s)...`, 'info');
    }
};

window.exportReport = function() {
    console.log('📊 Exporting report...');
    
    const report = {
        timestamp: new Date().toISOString(),
        dlqs: Array.from(neuroState.dlqs.values()),
        agents: Array.from(neuroState.agents.values()),
        metrics: neuroState.metrics,
        investigations: Array.from(neuroState.investigations.values())
    };
    
    const blob = new Blob([JSON.stringify(report, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `neurocenter-report-${Date.now()}.json`;
    a.click();
    
    showNotification('Report exported successfully', 'success');
};

window.toggleAutoMode = function() {
    if (!neuroState.settings) neuroState.settings = {};
    neuroState.settings.autoMode = !neuroState.settings.autoMode;
    const btn = event.target.closest('button');
    const icon = btn.querySelector('i');
    
    if (neuroState.settings.autoMode) {
        btn.classList.add('active');
        icon.setAttribute('data-lucide', 'toggle-right');
        showNotification('Auto Mode enabled', 'success');
    } else {
        btn.classList.remove('active');
        icon.setAttribute('data-lucide', 'toggle-left');
        showNotification('Auto Mode disabled', 'info');
    }
    
    lucide.createIcons();
    neuroState.socket.emit('set_auto_mode', { enabled: neuroState.settings.autoMode });
};

window.viewLogs = function() {
    console.log('📋 Opening logs viewer...');
    const panel = document.getElementById('investigation-panel');
    const content = document.getElementById('panel-content');
    
    content.innerHTML = `
        <div class="logs-viewer">
            <h4>System Logs</h4>
            <div class="log-filters">
                <select id="log-level">
                    <option value="all">All Levels</option>
                    <option value="error">Errors</option>
                    <option value="warning">Warnings</option>
                    <option value="info">Info</option>
                </select>
            </div>
            <div class="log-content" id="log-content">
                <pre>Loading logs...</pre>
            </div>
        </div>
    `;
    
    panel.classList.add('open');
    neuroState.socket.emit('get_logs', { lines: 100 });
};

window.toggleCompactView = function() {
    document.body.classList.toggle('compact-view');
    const btn = event.target.closest('button');
    
    if (document.body.classList.contains('compact-view')) {
        btn.classList.add('active');
        showNotification('Compact view enabled', 'info');
    } else {
        btn.classList.remove('active');
        showNotification('Normal view restored', 'info');
    }
};

window.deployAgent = function() {
    console.log('🚀 Deploying new agent...');
    neuroState.socket.emit('deploy_agent', { type: 'investigator' });
    showNotification('Deploying new agent...', 'info');
};

window.refreshAgents = function() {
    console.log('🔄 Refreshing agents...');
    if (neuroState.socket) {
        neuroState.socket.emit('get_agents');
        showNotification('Refreshing agents...', 'info');
    }
};

window.investigateSelected = function() {
    const selectedQueues = Array.from(neuroState.selectedQueues);
    
    if (selectedQueues.length === 0) {
        showNotification('No queues selected for investigation', 'warning');
        return;
    }
    
    selectedQueues.forEach(queueName => {
        neuroState.socket.emit('investigate_dlq', { queueName });
    });
    
    showNotification(`Investigating ${selectedQueues.length} queue(s)...`, 'info');
};