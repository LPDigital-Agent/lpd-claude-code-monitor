// Enhanced DLQ Dashboard JavaScript
// Real-time monitoring with WebSocket and interactive features

// Global variables
let socket;
let messageChart;
let dlqData = [];
let chartData = {
    labels: [],
    datasets: [{
        label: 'Total Messages',
        data: [],
        borderColor: 'rgb(75, 192, 192)',
        backgroundColor: 'rgba(75, 192, 192, 0.2)',
        tension: 0.4
    }]
};
let selectedDLQ = null;
let theme = localStorage.getItem('theme') || 'light';

// Initialize on page load
document.addEventListener('DOMContentLoaded', function() {
    initializeWebSocket();
    initializeChart();
    loadInitialData();
    setupEventListeners();
    applyTheme();
    startClock();
});

// WebSocket initialization
function initializeWebSocket() {
    socket = io();
    
    socket.on('connect', function() {
        console.log('Connected to WebSocket');
        updateConnectionStatus(true);
    });
    
    socket.on('disconnect', function() {
        console.log('Disconnected from WebSocket');
        updateConnectionStatus(false);
    });
    
    socket.on('dlq_update', function(data) {
        updateDLQTable(data);
        updateSummaryCards(data);
        updateChart(data);
    });
    
    socket.on('pr_update', function(data) {
        updatePRList(data);
    });
    
    socket.on('investigation_update', function(data) {
        updateInvestigationList(data);
    });
}

// Initialize Chart.js
function initializeChart() {
    const ctx = document.getElementById('message-chart').getContext('2d');
    messageChart = new Chart(ctx, {
        type: 'line',
        data: chartData,
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: true,
                    position: 'top'
                },
                title: {
                    display: false
                }
            },
            scales: {
                x: {
                    display: true,
                    title: {
                        display: true,
                        text: 'Time'
                    }
                },
                y: {
                    display: true,
                    title: {
                        display: true,
                        text: 'Messages'
                    },
                    beginAtZero: true
                }
            },
            animation: {
                duration: 750
            }
        }
    });
}

// Load initial data
async function loadInitialData() {
    try {
        // Load summary
        const summaryResponse = await fetch('/api/dashboard/summary');
        const summaryData = await summaryResponse.json();
        updateSummaryFromData(summaryData.summary);
        
        // Load DLQs
        const dlqResponse = await fetch('/api/dlqs');
        const dlqData = await dlqResponse.json();
        updateDLQTable(dlqData);
        updateChart(dlqData);
        
        // Load PRs
        const prResponse = await fetch('/api/github/prs');
        const prData = await prResponse.json();
        updatePRList(prData);
        
        // Load Investigations
        const invResponse = await fetch('/api/investigations');
        const invData = await invResponse.json();
        updateInvestigationList(invData);
        
        // Load CloudWatch logs
        refreshLogs();
    } catch (error) {
        console.error('Error loading initial data:', error);
    }
}

// Update DLQ table
function updateDLQTable(data) {
    dlqData = data;
    const tbody = document.getElementById('dlq-tbody');
    tbody.innerHTML = '';
    
    data.forEach(dlq => {
        const row = document.createElement('tr');
        row.className = 'fade-in';
        
        const statusBadge = dlq.messages > 0 
            ? `<span class="badge badge-status-alert">Alert</span>`
            : `<span class="badge badge-status-ok">OK</span>`;
        
        const messageClass = dlq.messages > 0 ? 'text-danger fw-bold' : 'text-success';
        
        row.innerHTML = `
            <td>${dlq.name}</td>
            <td class="${messageClass}">${dlq.messages}</td>
            <td>${statusBadge}</td>
            <td>
                <button class="btn btn-sm btn-primary btn-investigate" 
                        onclick="startInvestigation('${dlq.name}')"
                        ${dlq.messages === 0 ? 'disabled' : ''}>
                    <i class="fas fa-search"></i> Investigate
                </button>
                <button class="btn btn-sm btn-info" 
                        onclick="viewMessages('${dlq.name}')">
                    <i class="fas fa-eye"></i> View
                </button>
            </td>
        `;
        
        tbody.appendChild(row);
    });
    
    // Initialize or reinitialize DataTable
    if ($.fn.DataTable.isDataTable('#dlq-table')) {
        $('#dlq-table').DataTable().destroy();
    }
    
    $('#dlq-table').DataTable({
        pageLength: 10,
        order: [[1, 'desc']],
        responsive: true
    });
}

// Update summary cards
function updateSummaryCards(dlqData) {
    const totalMessages = dlqData.reduce((sum, dlq) => sum + dlq.messages, 0);
    const alertQueues = dlqData.filter(dlq => dlq.messages > 0).length;
    
    document.getElementById('total-dlqs').textContent = dlqData.length;
    document.getElementById('total-messages').textContent = totalMessages;
    document.getElementById('alert-queues').textContent = alertQueues;
    
    // Add animation effect
    ['total-dlqs', 'total-messages', 'alert-queues'].forEach(id => {
        document.getElementById(id).classList.add('alert-flash');
        setTimeout(() => {
            document.getElementById(id).classList.remove('alert-flash');
        }, 500);
    });
}

// Update summary from API data
function updateSummaryFromData(summary) {
    document.getElementById('total-dlqs').textContent = summary.totalDLQs || 0;
    document.getElementById('total-messages').textContent = summary.totalMessages || 0;
    document.getElementById('alert-queues').textContent = summary.alertQueues || 0;
    document.getElementById('active-prs').textContent = summary.activePRs || 0;
    document.getElementById('active-investigations').textContent = summary.activeInvestigations || 0;
}

// Update chart with new data
function updateChart(dlqData) {
    const now = new Date().toLocaleTimeString();
    const totalMessages = dlqData.reduce((sum, dlq) => sum + dlq.messages, 0);
    
    // Add new data point
    if (chartData.labels.length > 20) {
        chartData.labels.shift();
        chartData.datasets[0].data.shift();
    }
    
    chartData.labels.push(now);
    chartData.datasets[0].data.push(totalMessages);
    
    // Add individual DLQ datasets if not too many
    if (dlqData.length <= 5 && dlqData.length > 0) {
        // Clear existing datasets except the total
        chartData.datasets = [chartData.datasets[0]];
        
        dlqData.forEach((dlq, index) => {
            let dataset = chartData.datasets.find(d => d.label === dlq.name);
            if (!dataset) {
                const colors = [
                    'rgb(255, 99, 132)',
                    'rgb(54, 162, 235)',
                    'rgb(255, 206, 86)',
                    'rgb(75, 192, 192)',
                    'rgb(153, 102, 255)'
                ];
                dataset = {
                    label: dlq.name,
                    data: new Array(chartData.labels.length - 1).fill(0),
                    borderColor: colors[index % colors.length],
                    backgroundColor: colors[index % colors.length].replace('rgb', 'rgba').replace(')', ', 0.2)'),
                    tension: 0.4
                };
                chartData.datasets.push(dataset);
            }
            dataset.data.push(dlq.messages);
        });
    }
    
    messageChart.update();
}

// Update PR list
function updatePRList(prs) {
    const prList = document.getElementById('pr-list');
    prList.innerHTML = '';
    
    if (prs.length === 0) {
        prList.innerHTML = '<div class="text-muted">No open PRs</div>';
        return;
    }
    
    prs.forEach(pr => {
        const prItem = document.createElement('div');
        prItem.className = 'pr-item fade-in';
        
        const created = new Date(pr.created).toLocaleDateString();
        
        prItem.innerHTML = `
            <div>
                <a href="${pr.url}" target="_blank" class="pr-title">
                    #${pr.number} - ${pr.title}
                </a>
                <div class="pr-meta">
                    <i class="fas fa-code-branch"></i> ${pr.repo} | 
                    <i class="fas fa-user"></i> ${pr.author} | 
                    <i class="fas fa-calendar"></i> ${created}
                </div>
            </div>
        `;
        
        prList.appendChild(prItem);
    });
    
    // Update PR count
    document.getElementById('active-prs').textContent = prs.length;
}

// Update investigation list
function updateInvestigationList(investigations) {
    const invList = document.getElementById('investigation-list');
    invList.innerHTML = '';
    
    if (investigations.length === 0) {
        invList.innerHTML = '<div class="text-muted">No active investigations</div>';
        return;
    }
    
    investigations.forEach(inv => {
        const invItem = document.createElement('div');
        invItem.className = 'investigation-item fade-in';
        
        const startTime = new Date(inv.startTime).toLocaleTimeString();
        
        invItem.innerHTML = `
            <div>
                <span class="investigation-status"></span>
                <strong>${inv.dlq}</strong> - Investigation #${inv.id}
                <div class="text-muted small">
                    <i class="fas fa-clock"></i> Started: ${startTime} | 
                    <i class="fas fa-microchip"></i> PID: ${inv.pid} | 
                    Status: ${inv.status}
                </div>
            </div>
        `;
        
        invList.appendChild(invItem);
    });
    
    // Update investigation count
    document.getElementById('active-investigations').textContent = investigations.length;
}

// Start investigation
function startInvestigation(dlqName) {
    selectedDLQ = dlqName;
    document.getElementById('modal-dlq-name').textContent = dlqName;
    const modal = new bootstrap.Modal(document.getElementById('investigationModal'));
    modal.show();
}

// Confirm investigation
async function confirmInvestigation() {
    if (!selectedDLQ) return;
    
    try {
        const response = await fetch('/api/investigations/start', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ dlq_name: selectedDLQ })
        });
        
        const data = await response.json();
        
        if (response.ok) {
            showNotification('Investigation started successfully', 'success');
            bootstrap.Modal.getInstance(document.getElementById('investigationModal')).hide();
            
            // Request update
            socket.emit('request_update');
        } else {
            showNotification('Failed to start investigation: ' + data.error, 'danger');
        }
    } catch (error) {
        showNotification('Error starting investigation', 'danger');
        console.error('Error:', error);
    }
}

// View DLQ messages
async function viewMessages(dlqName) {
    try {
        const response = await fetch(`/api/dlqs/${dlqName}/messages`);
        const messages = await response.json();
        
        // Display messages in log viewer temporarily
        const logViewer = document.getElementById('log-viewer');
        logViewer.innerHTML = `<h5>Messages from ${dlqName}:</h5>`;
        
        if (messages.length === 0) {
            logViewer.innerHTML += '<div class="text-muted">No messages in queue</div>';
        } else {
            messages.forEach(msg => {
                const msgDiv = document.createElement('div');
                msgDiv.className = 'log-entry';
                msgDiv.innerHTML = `
                    <span class="log-timestamp">${msg.id}</span>
                    <pre>${JSON.stringify(msg.body, null, 2)}</pre>
                `;
                logViewer.appendChild(msgDiv);
            });
        }
        
        // Scroll to log viewer
        logViewer.scrollIntoView({ behavior: 'smooth' });
    } catch (error) {
        console.error('Error fetching messages:', error);
        showNotification('Failed to fetch messages', 'danger');
    }
}

// Refresh CloudWatch logs
async function refreshLogs() {
    try {
        const response = await fetch('/api/cloudwatch/logs');
        const logs = await response.json();
        
        const logViewer = document.getElementById('log-viewer');
        logViewer.innerHTML = '';
        
        if (logs.length === 0) {
            logViewer.innerHTML = '<div class="text-muted">No recent logs</div>';
        } else {
            logs.forEach(log => {
                const logDiv = document.createElement('div');
                logDiv.className = 'log-entry';
                
                // Determine log level
                let levelClass = 'log-level-info';
                if (log.message.includes('ERROR')) levelClass = 'log-level-error';
                else if (log.message.includes('WARNING')) levelClass = 'log-level-warning';
                
                logDiv.innerHTML = `
                    <span class="log-timestamp">${log.timestamp}</span>
                    <span class="${levelClass}">${log.message}</span>
                `;
                
                logViewer.appendChild(logDiv);
            });
        }
    } catch (error) {
        console.error('Error fetching logs:', error);
    }
}

// Update connection status
function updateConnectionStatus(connected) {
    const statusBadge = document.getElementById('connection-status');
    if (connected) {
        statusBadge.innerHTML = '<i class="fas fa-circle"></i> Connected';
        statusBadge.className = 'badge bg-success me-3 connected';
    } else {
        statusBadge.innerHTML = '<i class="fas fa-exclamation-circle"></i> Disconnected';
        statusBadge.className = 'badge bg-danger me-3 disconnected';
    }
}

// Theme toggle
function toggleTheme() {
    theme = theme === 'light' ? 'dark' : 'light';
    localStorage.setItem('theme', theme);
    applyTheme();
}

function applyTheme() {
    const body = document.body;
    const icon = document.getElementById('theme-icon');
    
    if (theme === 'dark') {
        body.classList.add('dark-theme');
        icon.className = 'fas fa-sun';
    } else {
        body.classList.remove('dark-theme');
        icon.className = 'fas fa-moon';
    }
}

// Show notification
function showNotification(message, type = 'info') {
    const notification = document.createElement('div');
    notification.className = `alert alert-${type} alert-dismissible fade show position-fixed top-0 end-0 m-3`;
    notification.style.zIndex = '9999';
    notification.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    document.body.appendChild(notification);
    
    setTimeout(() => {
        notification.remove();
    }, 5000);
}

// Start clock
function startClock() {
    function updateClock() {
        const now = new Date();
        document.getElementById('last-update').textContent = now.toLocaleTimeString();
    }
    
    updateClock();
    setInterval(updateClock, 1000);
}

// Setup event listeners
function setupEventListeners() {
    // Refresh button
    window.refreshLogs = refreshLogs;
    
    // Keyboard shortcuts
    document.addEventListener('keydown', function(e) {
        if (e.key === 'r' && e.ctrlKey) {
            e.preventDefault();
            socket.emit('request_update');
            showNotification('Refreshing data...', 'info');
        }
        if (e.key === 't' && e.ctrlKey) {
            e.preventDefault();
            toggleTheme();
        }
    });
    
    // Auto-refresh every 30 seconds
    setInterval(() => {
        socket.emit('request_update');
    }, 30000);
}

// Export functions for global access
window.startInvestigation = startInvestigation;
window.confirmInvestigation = confirmInvestigation;
window.viewMessages = viewMessages;
window.refreshLogs = refreshLogs;
window.toggleTheme = toggleTheme;