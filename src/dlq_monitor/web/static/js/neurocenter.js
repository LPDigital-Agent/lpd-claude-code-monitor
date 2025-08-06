// BHiveQ NeuroCenter - Real-time Dashboard JavaScript

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
    selectedInvestigation: null,
    timelineFilter: 'all',
    soundEnabled: true,
    notificationsEnabled: true,
    settings: {
        autoRefresh: true,
        refreshInterval: 3000,
        alertThreshold: 10
    }
};

// Initialize WebSocket connection
function initializeWebSocket() {
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    neuroState.socket = io(window.location.origin);
    
    // Connection handlers
    neuroState.socket.on('connect', () => {
        console.log('NeuroCenter connected to server');
        updateConnectionStatus('connected');
        requestInitialData();
    });
    
    neuroState.socket.on('disconnect', () => {
        console.log('NeuroCenter disconnected from server');
        updateConnectionStatus('disconnected');
    });
    
    // Data update handlers
    neuroState.socket.on('agent_update', handleAgentUpdate);
    neuroState.socket.on('investigation_update', handleInvestigationUpdate);
    neuroState.socket.on('timeline_event', handleTimelineEvent);
    neuroState.socket.on('dlq_update', handleDLQUpdate);
    neuroState.socket.on('metrics_update', handleMetricsUpdate);
    neuroState.socket.on('alert', handleSystemAlert);
    neuroState.socket.on('pr_created', handlePRCreated);
}

// Request initial data from server
function requestInitialData() {
    neuroState.socket.emit('get_agents');
    neuroState.socket.emit('get_investigations');
    neuroState.socket.emit('get_dlqs');
    neuroState.socket.emit('get_metrics');
    neuroState.socket.emit('get_mappings');
    
    // Start real metrics update
    updateLiveMetrics();
    setInterval(updateLiveMetrics, 5000);
}

// Update connection status indicator
function updateConnectionStatus(status) {
    const indicator = document.querySelector('.pulse-dot');
    const statusText = document.querySelector('.status-text');
    
    if (status === 'connected') {
        indicator.style.background = 'var(--status-success)';
        statusText.textContent = 'OPERATIONAL';
    } else {
        indicator.style.background = 'var(--status-error)';
        statusText.textContent = 'DISCONNECTED';
    }
}

// Live Metrics Update
function updateLiveMetrics() {
    // Calculate real metrics from state
    const activeAgents = neuroState.agents.size;
    const completedInvestigations = Array.from(neuroState.investigations.values())
        .filter(inv => inv.status === 'completed');
    const totalInvestigations = neuroState.investigations.size;
    
    // Calculate average time
    let totalTime = 0;
    let countWithTime = 0;
    completedInvestigations.forEach(inv => {
        if (inv.duration) {
            totalTime += inv.duration;
            countWithTime++;
        }
    });
    const avgTime = countWithTime > 0 ? Math.round(totalTime / countWithTime / 60) : 0;
    
    // Calculate success rate
    const successRate = totalInvestigations > 0 
        ? Math.round((completedInvestigations.length / totalInvestigations) * 100) 
        : 0;
    
    // Count PRs
    const prsGenerated = completedInvestigations.filter(inv => inv.pr_url).length;
    
    // Update metrics in state
    neuroState.metrics = {
        activeAgents,
        avgTime,
        prsGenerated,
        successRate
    };
    
    // Update UI
    document.getElementById('metric-agents').textContent = activeAgents;
    document.getElementById('metric-time').textContent = `${avgTime}m`;
    document.getElementById('metric-prs').textContent = prsGenerated;
    document.getElementById('metric-success').textContent = `${successRate}%`;
    
    // Update charts if they exist
    updateCharts();
}

// Button Handlers
function toggleSound() {
    neuroState.soundEnabled = !neuroState.soundEnabled;
    const btn = document.getElementById('voice-toggle');
    const icon = btn.querySelector('[data-lucide]');
    
    if (neuroState.soundEnabled) {
        icon.setAttribute('data-lucide', 'volume-2');
        lucide.createIcons();
        showNotification('Sound enabled', 'success');
    } else {
        icon.setAttribute('data-lucide', 'volume-x');
        lucide.createIcons();
        showNotification('Sound muted', 'info');
    }
    
    // Save preference
    localStorage.setItem('neurocenter_sound', neuroState.soundEnabled);
}

function toggleNotifications() {
    neuroState.notificationsEnabled = !neuroState.notificationsEnabled;
    const btn = document.getElementById('alerts-toggle');
    const icon = btn.querySelector('[data-lucide]');
    
    if (neuroState.notificationsEnabled) {
        icon.setAttribute('data-lucide', 'bell');
        lucide.createIcons();
        showNotification('Notifications enabled', 'success');
        
        // Request permission if needed
        if ('Notification' in window && Notification.permission === 'default') {
            Notification.requestPermission();
        }
    } else {
        icon.setAttribute('data-lucide', 'bell-off');
        lucide.createIcons();
        showNotification('Notifications disabled', 'info');
    }
    
    // Save preference
    localStorage.setItem('neurocenter_notifications', neuroState.notificationsEnabled);
}

function openSettings() {
    // Create settings modal
    const modal = document.createElement('div');
    modal.className = 'settings-modal';
    modal.innerHTML = `
        <div class="settings-content">
            <h3>NeuroCenter Settings</h3>
            <div class="settings-group">
                <label>
                    <input type="checkbox" id="setting-autorefresh" ${neuroState.settings.autoRefresh ? 'checked' : ''}>
                    Auto-refresh data
                </label>
            </div>
            <div class="settings-group">
                <label>
                    Refresh interval (seconds):
                    <input type="number" id="setting-interval" value="${neuroState.settings.refreshInterval / 1000}" min="1" max="60">
                </label>
            </div>
            <div class="settings-group">
                <label>
                    Alert threshold (messages):
                    <input type="number" id="setting-threshold" value="${neuroState.settings.alertThreshold}" min="1" max="100">
                </label>
            </div>
            <div class="settings-actions">
                <button onclick="saveSettings()" class="btn-save">Save</button>
                <button onclick="closeSettings()" class="btn-cancel">Cancel</button>
            </div>
        </div>
    `;
    document.body.appendChild(modal);
}

function saveSettings() {
    neuroState.settings.autoRefresh = document.getElementById('setting-autorefresh').checked;
    neuroState.settings.refreshInterval = parseInt(document.getElementById('setting-interval').value) * 1000;
    neuroState.settings.alertThreshold = parseInt(document.getElementById('setting-threshold').value);
    
    localStorage.setItem('neurocenter_settings', JSON.stringify(neuroState.settings));
    showNotification('Settings saved', 'success');
    closeSettings();
}

function closeSettings() {
    const modal = document.querySelector('.settings-modal');
    if (modal) modal.remove();
}

// Agent Management
function handleAgentUpdate(data) {
    neuroState.agents.set(data.id, data);
    renderAgents();
    updateLiveMetrics();
}

function renderAgents() {
    const tbody = document.getElementById('agents-tbody');
    if (!tbody) return;
    
    tbody.innerHTML = '';
    
    neuroState.agents.forEach(agent => {
        const row = document.createElement('tr');
        
        const elapsedTime = agent.elapsed_time ? formatDuration(agent.elapsed_time) : '-';
        const statusClass = getAgentStatusClass(agent.status);
        
        row.innerHTML = `
            <td>
                <div class="agent-name">${agent.name}</div>
                <div class="agent-type">${agent.type || 'investigation'}</div>
            </td>
            <td>
                <span class="agent-status ${statusClass}">
                    <span class="agent-status-dot"></span>
                    ${agent.status}
                </span>
            </td>
            <td>${agent.started_at ? formatTime(agent.started_at) : '-'}</td>
            <td>${elapsedTime}</td>
            <td>
                <div class="agent-dlq">${agent.dlq || '-'}</div>
            </td>
            <td>
                <div class="agent-actions">
                    <button onclick="viewAgentDetails('${agent.id}')" class="btn-action">
                        <i class="lucide lucide-eye"></i>
                    </button>
                </div>
            </td>
        `;
        
        tbody.appendChild(row);
    });
}

// Investigation Management
function handleInvestigationUpdate(data) {
    neuroState.investigations.set(data.id, data);
    renderInvestigations();
    updateLiveMetrics();
}

function renderInvestigations() {
    const container = document.getElementById('timeline-container');
    if (!container) return;
    
    // Filter investigations
    const investigations = Array.from(neuroState.investigations.values())
        .filter(inv => {
            if (neuroState.timelineFilter === 'all') return true;
            return inv.status === neuroState.timelineFilter;
        })
        .sort((a, b) => new Date(b.created_at) - new Date(a.created_at));
    
    container.innerHTML = '';
    
    investigations.forEach(inv => {
        const entry = createTimelineEntry(inv);
        container.appendChild(entry);
    });
}

function createTimelineEntry(investigation) {
    const entry = document.createElement('div');
    entry.className = `timeline-entry ${investigation.status}`;
    entry.onclick = () => showInvestigationDetails(investigation.id);
    
    const statusIcon = getStatusIcon(investigation.status);
    const timeAgo = formatTimeAgo(investigation.created_at);
    
    entry.innerHTML = `
        <div class="timeline-header">
            <div class="timeline-icon">${statusIcon}</div>
            <div class="timeline-info">
                <div class="timeline-title">${investigation.dlq_name}</div>
                <div class="timeline-meta">
                    <span>${investigation.id}</span>
                    <span>•</span>
                    <span>${timeAgo}</span>
                </div>
            </div>
            <div class="timeline-expand">
                <i class="lucide lucide-chevron-right"></i>
            </div>
        </div>
        <div class="timeline-progress">
            <div class="progress-bar" style="width: ${investigation.progress}%"></div>
        </div>
    `;
    
    return entry;
}

// DLQ Management with compact UI
function handleDLQUpdate(data) {
    // Filter to only FABIO-PROD/sa-east-1 DLQs
    if (data.profile === 'FABIO-PROD' && data.region === 'sa-east-1') {
        neuroState.dlqs.set(data.name, data);
        renderDLQAssignments();
    }
}

function renderDLQAssignments() {
    const container = document.getElementById('dlq-assignments');
    if (!container) return;
    
    // Make the UI more compact
    container.innerHTML = `
        <div class="dlq-assignment-grid">
            ${Array.from(neuroState.dlqs.values()).map(dlq => `
                <div class="dlq-assignment-item">
                    <div class="dlq-name" title="${dlq.name}">${truncateDLQName(dlq.name)}</div>
                    <div class="dlq-stats">
                        <span class="dlq-count ${dlq.messages > 0 ? 'has-messages' : ''}">${dlq.messages}</span>
                    </div>
                    <select class="agent-select" onchange="assignAgent('${dlq.name}', this.value)">
                        <option value="">Auto</option>
                        <option value="investigator">Investigator</option>
                        <option value="analyzer">Analyzer</option>
                        <option value="fixer">Fixer</option>
                    </select>
                </div>
            `).join('')}
        </div>
    `;
}

function truncateDLQName(name) {
    // Remove common prefixes and truncate
    return name.replace(/^fm-|^lpd-|-dlq$|-prod$/g, '').substring(0, 20);
}

function assignAgent(dlqName, agentType) {
    neuroState.socket.emit('assign_agent', { dlq: dlqName, agent: agentType });
    showNotification(`Agent assigned to ${dlqName}`, 'success');
}

// Timeline Event Handler
function handleTimelineEvent(event) {
    console.log('Timeline event:', event);
    
    // Add to timeline
    if (event.investigation_id) {
        const inv = neuroState.investigations.get(event.investigation_id);
        if (inv) {
            if (!inv.events) inv.events = [];
            inv.events.push(event);
            renderInvestigations();
        }
    }
    
    // Show notification
    if (neuroState.notificationsEnabled) {
        showBrowserNotification(event.title, event.description);
    }
    
    // Play sound
    if (neuroState.soundEnabled && event.type === 'alert') {
        playAlertSound();
    }
}

// Metrics Update Handler
function handleMetricsUpdate(data) {
    neuroState.metrics = data;
    updateLiveMetrics();
}

// Alert Handlers
function handleSystemAlert(alert) {
    showNotification(alert.message, alert.type || 'warning');
    
    if (neuroState.notificationsEnabled) {
        showBrowserNotification('NeuroCenter Alert', alert.message);
    }
    
    if (neuroState.soundEnabled) {
        playAlertSound();
    }
}

function handlePRCreated(data) {
    showNotification(`PR Created: ${data.title}`, 'success');
    
    if (neuroState.notificationsEnabled) {
        showBrowserNotification('Pull Request Created', data.title);
    }
    
    if (neuroState.soundEnabled) {
        playSuccessSound();
    }
    
    updateLiveMetrics();
}

// Utility Functions
function formatTime(timestamp) {
    return new Date(timestamp).toLocaleTimeString();
}

function formatTimeAgo(timestamp) {
    const seconds = Math.floor((new Date() - new Date(timestamp)) / 1000);
    
    if (seconds < 60) return `${seconds}s ago`;
    if (seconds < 3600) return `${Math.floor(seconds / 60)}m ago`;
    if (seconds < 86400) return `${Math.floor(seconds / 3600)}h ago`;
    return `${Math.floor(seconds / 86400)}d ago`;
}

function formatDuration(seconds) {
    if (seconds < 60) return `${seconds}s`;
    if (seconds < 3600) return `${Math.floor(seconds / 60)}m`;
    return `${Math.floor(seconds / 3600)}h ${Math.floor((seconds % 3600) / 60)}m`;
}

function getAgentStatusClass(status) {
    const statusMap = {
        'active': 'status-active',
        'idle': 'status-idle',
        'error': 'status-error',
        'completed': 'status-success'
    };
    return statusMap[status] || 'status-idle';
}

function getStatusIcon(status) {
    const icons = {
        'initiated': '<i class="lucide lucide-circle"></i>',
        'analyzing': '<i class="lucide lucide-search"></i>',
        'debugging': '<i class="lucide lucide-bug"></i>',
        'reviewing': '<i class="lucide lucide-eye"></i>',
        'completed': '<i class="lucide lucide-check-circle"></i>',
        'failed': '<i class="lucide lucide-x-circle"></i>'
    };
    return icons[status] || '<i class="lucide lucide-circle"></i>';
}

// Notification Functions
function showNotification(message, type = 'info') {
    const container = document.getElementById('notification-container') || createNotificationContainer();
    
    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    notification.innerHTML = `
        <span>${message}</span>
        <button onclick="this.parentElement.remove()" class="notification-close">×</button>
    `;
    
    container.appendChild(notification);
    
    setTimeout(() => {
        notification.classList.add('fade-out');
        setTimeout(() => notification.remove(), 300);
    }, 5000);
}

function createNotificationContainer() {
    const container = document.createElement('div');
    container.id = 'notification-container';
    container.style.cssText = 'position:fixed;top:20px;right:20px;z-index:9999;';
    document.body.appendChild(container);
    return container;
}

function showBrowserNotification(title, body) {
    if ('Notification' in window && Notification.permission === 'granted') {
        new Notification(title, {
            body: body,
            icon: '/static/brand/symbol.png',
            badge: '/static/brand/symbol.png'
        });
    }
}

// Sound Functions
function playAlertSound() {
    const audio = new Audio('data:audio/wav;base64,UklGRnoGAABXQVZFZm10IBAAAAABAAEAQB8AAEAfAAABAAgAZGF0YQoGAACBhYqFbF1fdJivrJBhNjVgodDbq2EcBj+a2/LDciUFLIHO8tiJNwgZaLvt559NEAxQp+PwtmMcBjiR1/LMeSwFJHfH8N2QQAoUXrTp66hVFApGn+DyvmwhBCxywu3ikUMINGS57OScUgwMVqzn77BdGAg+l9n0wnkpBSNoyO7TmEYMMmO48ua');
    audio.play().catch(e => console.log('Could not play sound:', e));
}

function playSuccessSound() {
    const audio = new Audio('data:audio/wav;base64,UklGRl4GAABXQVZFZm10IBAAAAABAAEAECcAACAnAAABAAgAZGF0YQA=');
    audio.play().catch(e => console.log('Could not play sound:', e));
}

// Chart Functions
function updateCharts() {
    // Update any charts if implemented
    if (window.updateMetricsChart) {
        window.updateMetricsChart(neuroState.metrics);
    }
}

// Investigation Details
function showInvestigationDetails(investigationId) {
    const investigation = neuroState.investigations.get(investigationId);
    if (!investigation) return;
    
    neuroState.selectedInvestigation = investigationId;
    
    const panel = document.getElementById('details-panel');
    if (!panel) return;
    
    panel.innerHTML = `
        <div class="details-header">
            <h3>Investigation Details</h3>
            <button onclick="closeDetails()" class="btn-close">
                <i class="lucide lucide-x"></i>
            </button>
        </div>
        <div class="details-content">
            <div class="detail-group">
                <label>ID:</label>
                <span>${investigation.id}</span>
            </div>
            <div class="detail-group">
                <label>DLQ:</label>
                <span>${investigation.dlq_name}</span>
            </div>
            <div class="detail-group">
                <label>Status:</label>
                <span class="status-badge ${investigation.status}">${investigation.status}</span>
            </div>
            <div class="detail-group">
                <label>Progress:</label>
                <div class="progress-bar-container">
                    <div class="progress-bar" style="width: ${investigation.progress}%"></div>
                </div>
            </div>
            <div class="detail-group">
                <label>Started:</label>
                <span>${formatTimeAgo(investigation.created_at)}</span>
            </div>
            ${investigation.pr_url ? `
                <div class="detail-group">
                    <label>PR:</label>
                    <a href="${investigation.pr_url}" target="_blank" class="pr-link">
                        View Pull Request
                    </a>
                </div>
            ` : ''}
        </div>
    `;
    
    panel.classList.add('active');
}

function closeDetails() {
    const panel = document.getElementById('details-panel');
    if (panel) {
        panel.classList.remove('active');
        neuroState.selectedInvestigation = null;
    }
}

// Load saved preferences
function loadPreferences() {
    const sound = localStorage.getItem('neurocenter_sound');
    if (sound !== null) neuroState.soundEnabled = sound === 'true';
    
    const notifications = localStorage.getItem('neurocenter_notifications');
    if (notifications !== null) neuroState.notificationsEnabled = notifications === 'true';
    
    const settings = localStorage.getItem('neurocenter_settings');
    if (settings) {
        try {
            neuroState.settings = JSON.parse(settings);
        } catch (e) {
            console.error('Failed to load settings:', e);
        }
    }
}

// Initialize drag and drop for modules
function initializeDragAndDrop() {
    const grid = document.querySelector('.dashboard-grid');
    if (grid && typeof Sortable !== 'undefined') {
        new Sortable(grid, {
            animation: 150,
            ghostClass: 'module-ghost',
            onEnd: function() {
                saveModuleLayout();
            }
        });
    }
}

function saveModuleLayout() {
    const modules = document.querySelectorAll('.module-card');
    const layout = Array.from(modules).map(m => m.id);
    localStorage.setItem('neurocenter_layout', JSON.stringify(layout));
}

// Initialize on page load
document.addEventListener('DOMContentLoaded', function() {
    console.log('NeuroCenter initializing...');
    
    // Load preferences
    loadPreferences();
    
    // Initialize WebSocket
    initializeWebSocket();
    
    // Initialize drag and drop
    initializeDragAndDrop();
    
    // Setup event listeners with correct IDs
    const soundBtn = document.getElementById('voice-toggle');
    if (soundBtn) soundBtn.addEventListener('click', toggleSound);
    
    const notifBtn = document.getElementById('alerts-toggle');
    if (notifBtn) notifBtn.addEventListener('click', toggleNotifications);
    
    const settingsBtn = document.getElementById('settings-toggle');
    if (settingsBtn) settingsBtn.addEventListener('click', openSettings);
    
    // Setup timeline filter
    const filterBtns = document.querySelectorAll('.timeline-filter');
    filterBtns.forEach(btn => {
        btn.addEventListener('click', function() {
            neuroState.timelineFilter = this.dataset.filter;
            filterBtns.forEach(b => b.classList.remove('active'));
            this.classList.add('active');
            renderInvestigations();
        });
    });
    
    console.log('NeuroCenter initialized successfully');
});