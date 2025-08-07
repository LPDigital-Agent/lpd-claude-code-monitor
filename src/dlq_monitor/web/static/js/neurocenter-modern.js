// NeuroCenter Modern - Glass Room Implementation
// Living AI Observatory with Operational Storytelling

class NeuroCenter {
    constructor() {
        this.state = {
            socket: null,
            currentTab: 'dashboard',
            queues: new Map(),
            agents: new Map(),
            investigations: new Map(),
            metrics: {
                activeAgents: 0,
                avgResolution: 0,
                prsToday: 0,
                successRate: 0
            },
            selectedQueues: new Set(),
            voiceEnabled: true,
            theme: 'dark',
            activityFeed: [],
            storyline: [],
            observeMode: {
                playing: false,
                speed: 1,
                currentAgent: null
            }
        };
        
        // Real production queue names from AWS
        this.productionQueues = [
            'fm-payment-notification-dlq-prod',
            'fm-order-dlq-production',
            'fm-risk-dlq-production',
            'fm-fraud-dlq-production',
            'fm-reconciliation-dlq-prod'
        ];
        
        this.init();
    }
    
    init() {
        this.initWebSocket();
        this.initTabNavigation();
        this.initVoiceToggle();
        this.initQueueTopology();
        this.initGlassRoom();
        this.initObserveMode();
        this.initAITerminal();
        this.initEventListeners();
        this.loadInitialData();
        
        console.log('🚀 Agent NeuroCenter Glass Room initialized');
    }
    
    // WebSocket for Real-time Updates
    initWebSocket() {
        this.state.socket = io(window.location.origin, {
            reconnection: true,
            reconnectionDelay: 1000,
            reconnectionAttempts: 5
        });
        
        this.state.socket.on('connect', () => {
            this.updateStatus('OPERATIONAL');
            this.addToActivityFeed('System', 'Connected to Agent NeuroCenter backend');
        });
        
        this.state.socket.on('disconnect', () => {
            this.updateStatus('DISCONNECTED');
            this.addToActivityFeed('System', 'Disconnected from backend - attempting reconnection...');
        });
        
        // Queue updates
        this.state.socket.on('dlq_update', (data) => {
            this.handleDLQUpdate(data);
        });
        
        // Agent updates
        this.state.socket.on('agent_update', (data) => {
            this.handleAgentUpdate(data);
        });
        
        // Investigation updates
        this.state.socket.on('investigation_update', (data) => {
            this.handleInvestigationUpdate(data);
        });
        
        // Metrics updates
        this.state.socket.on('metrics_update', (data) => {
            this.handleMetricsUpdate(data);
        });
        
        // Alert handling
        this.state.socket.on('alert', (data) => {
            this.handleAlert(data);
        });
        
        // Request initial data
        this.state.socket.emit('get_dlqs');
        this.state.socket.emit('get_agents');
        this.state.socket.emit('get_metrics');
    }
    
    // Tab Navigation
    initTabNavigation() {
        const tabs = document.querySelectorAll('.tab-btn');
        const tabContents = document.querySelectorAll('.tab-content');
        
        tabs.forEach(tab => {
            tab.addEventListener('click', () => {
                const targetTab = tab.dataset.tab;
                
                // Update active tab
                tabs.forEach(t => t.classList.remove('active'));
                tab.classList.add('active');
                
                // Show corresponding content
                tabContents.forEach(content => {
                    content.classList.remove('active');
                });
                
                const targetContent = document.getElementById(`${targetTab}-tab`);
                if (targetContent) {
                    targetContent.classList.add('active');
                }
                
                this.state.currentTab = targetTab;
                
                // Initialize tab-specific features
                if (targetTab === 'glass-room') {
                    this.initGlassRoom();
                } else if (targetTab === 'observe') {
                    this.startObserveMode();
                } else if (targetTab === 'terminal') {
                    this.focusTerminal();
                }
            });
        });
    }
    
    // Voice Toggle
    initVoiceToggle() {
        const voiceBtn = document.getElementById('voice-btn');
        
        voiceBtn.addEventListener('click', () => {
            this.state.voiceEnabled = !this.state.voiceEnabled;
            
            if (this.state.voiceEnabled) {
                voiceBtn.classList.remove('muted');
                voiceBtn.querySelector('.voice-status').textContent = 'ON';
                this.state.socket.emit('voice_settings', { enabled: true });
            } else {
                voiceBtn.classList.add('muted');
                voiceBtn.querySelector('.voice-status').textContent = 'OFF';
                this.state.socket.emit('voice_settings', { enabled: false });
            }
            
            this.addToActivityFeed('System', `Voice notifications ${this.state.voiceEnabled ? 'enabled' : 'disabled'}`);
        });
    }
    
    // Queue Topology Visualization
    initQueueTopology() {
        const canvas = document.getElementById('queue-topology-canvas');
        if (!canvas) return;
        
        const ctx = canvas.getContext('2d');
        canvas.width = canvas.offsetWidth;
        canvas.height = canvas.offsetHeight;
        
        // Draw topology network
        this.drawTopology(ctx, canvas.width, canvas.height);
    }
    
    drawTopology(ctx, width, height) {
        // Clear canvas
        ctx.clearRect(0, 0, width, height);
        
        // Set style
        ctx.strokeStyle = '#FA4616';
        ctx.fillStyle = '#E7E7E0';
        ctx.font = '12px Poppins';
        
        // Calculate positions for queues
        const centerX = width / 2;
        const centerY = height / 2;
        const radius = Math.min(width, height) * 0.3;
        
        // Draw source queues in a circle
        const sourceQueues = [
            'fm-payment-queue-prod',
            'fm-order-queue-prod',
            'fm-risk-queue-prod'
        ];
        
        const dlqs = [
            'fm-payment-dlq-prod',
            'fm-order-dlq-prod',
            'fm-risk-dlq-prod'
        ];
        
        // Draw connections
        ctx.strokeStyle = 'rgba(250, 70, 22, 0.3)';
        ctx.lineWidth = 2;
        
        sourceQueues.forEach((queue, i) => {
            const angle = (i / sourceQueues.length) * Math.PI * 2;
            const x1 = centerX + Math.cos(angle) * radius;
            const y1 = centerY + Math.sin(angle) * radius;
            const x2 = centerX + Math.cos(angle) * radius * 0.5;
            const y2 = centerY + Math.sin(angle) * radius * 0.5;
            
            // Draw connection line
            ctx.beginPath();
            ctx.moveTo(x1, y1);
            ctx.lineTo(x2, y2);
            ctx.stroke();
            
            // Draw arrow
            this.drawArrow(ctx, x1, y1, x2, y2);
            
            // Draw source queue node
            ctx.fillStyle = '#FA4616';
            ctx.beginPath();
            ctx.arc(x1, y1, 8, 0, Math.PI * 2);
            ctx.fill();
            
            // Draw DLQ node
            ctx.fillStyle = '#551C25';
            ctx.beginPath();
            ctx.arc(x2, y2, 8, 0, Math.PI * 2);
            ctx.fill();
            
            // Labels
            ctx.fillStyle = '#E7E7E0';
            ctx.textAlign = 'center';
            ctx.fillText(queue.split('-')[1], x1, y1 + 20);
            ctx.fillText(dlqs[i].split('-')[1] + '-dlq', x2, y2 + 20);
        });
        
        // Center node (monitoring hub)
        ctx.fillStyle = 'rgba(250, 70, 22, 0.2)';
        ctx.beginPath();
        ctx.arc(centerX, centerY, 15, 0, Math.PI * 2);
        ctx.fill();
        ctx.fillStyle = '#FA4616';
        ctx.textAlign = 'center';
        ctx.fillText('Monitor', centerX, centerY + 30);
    }
    
    drawArrow(ctx, fromX, fromY, toX, toY) {
        const angle = Math.atan2(toY - fromY, toX - fromX);
        const arrowLength = 10;
        
        ctx.beginPath();
        ctx.moveTo(toX, toY);
        ctx.lineTo(
            toX - arrowLength * Math.cos(angle - Math.PI / 6),
            toY - arrowLength * Math.sin(angle - Math.PI / 6)
        );
        ctx.moveTo(toX, toY);
        ctx.lineTo(
            toX - arrowLength * Math.cos(angle + Math.PI / 6),
            toY - arrowLength * Math.sin(angle + Math.PI / 6)
        );
        ctx.stroke();
    }
    
    // Glass Room Implementation
    initGlassRoom() {
        this.initAgentActivityFeed();
        this.initContextStoryline();
        this.initAgentConstellation();
        this.initSystemPulse();
    }
    
    initAgentActivityFeed() {
        // Simulate natural language feed updates
        this.addToActivityFeed(
            'Investigation Agent',
            'I\'m noticing an unusual pattern in the payment-dlq. The error rate has increased by 23% in the last hour. Beginning deep analysis...'
        );
        
        setTimeout(() => {
            this.addToActivityFeed(
                'DLQ Analyzer',
                'Found correlation: All failed messages contain malformed JSON in the payment_metadata field. This appears to be a serialization issue.'
            );
        }, 3000);
        
        setTimeout(() => {
            this.addToActivityFeed(
                'Code Debugger',
                'Traced the issue to PaymentProcessor.serialize() at line 234. The new decimal field isn\'t being properly encoded for legacy systems.'
            );
        }, 6000);
    }
    
    addToActivityFeed(agent, message) {
        const feed = document.getElementById('agent-activity-feed');
        if (!feed) return;
        
        const feedItem = document.createElement('div');
        feedItem.className = 'feed-item';
        feedItem.innerHTML = `
            <div class="feed-item-time">${new Date().toLocaleTimeString()}</div>
            <div class="feed-item-content">
                <span class="feed-item-agent">${agent}:</span> ${message}
            </div>
        `;
        
        feed.insertBefore(feedItem, feed.firstChild);
        
        // Keep only last 20 items
        while (feed.children.length > 20) {
            feed.removeChild(feed.lastChild);
        }
        
        // Add to state
        this.state.activityFeed.unshift({ agent, message, time: new Date() });
    }
    
    initContextStoryline() {
        this.addToStoryline(
            'Chapter 1: The Anomaly',
            'At 14:23 UTC, our monitoring systems detected an unusual spike in the payment-dlq. What started as a trickle quickly became a flood...'
        );
        
        setTimeout(() => {
            this.addToStoryline(
                'Chapter 2: The Investigation',
                'Our Investigation Agent dove deep into the message patterns, searching for the common thread that connected these failures...'
            );
        }, 5000);
    }
    
    addToStoryline(title, content) {
        const storyline = document.getElementById('context-storyline');
        if (!storyline) return;
        
        const chapter = document.createElement('div');
        chapter.className = 'story-chapter';
        chapter.innerHTML = `
            <div class="story-title">${title}</div>
            <div class="story-content">${content}</div>
        `;
        
        storyline.appendChild(chapter);
    }
    
    initAgentConstellation() {
        const canvas = document.getElementById('constellation-canvas');
        if (!canvas) return;
        
        const ctx = canvas.getContext('2d');
        canvas.width = canvas.offsetWidth;
        canvas.height = canvas.offsetHeight;
        
        // Animate agent constellation
        this.animateConstellation(ctx, canvas.width, canvas.height);
    }
    
    animateConstellation(ctx, width, height) {
        const agents = [
            { name: 'Investigator', x: width * 0.5, y: height * 0.3, active: true },
            { name: 'Analyzer', x: width * 0.3, y: height * 0.6, active: false },
            { name: 'Debugger', x: width * 0.7, y: height * 0.6, active: false },
            { name: 'Reviewer', x: width * 0.5, y: height * 0.8, active: false }
        ];
        
        const animate = () => {
            ctx.clearRect(0, 0, width, height);
            
            // Draw connections
            ctx.strokeStyle = 'rgba(250, 70, 22, 0.2)';
            ctx.lineWidth = 1;
            
            agents.forEach((agent, i) => {
                agents.forEach((other, j) => {
                    if (i < j) {
                        ctx.beginPath();
                        ctx.moveTo(agent.x, agent.y);
                        ctx.lineTo(other.x, other.y);
                        ctx.stroke();
                    }
                });
            });
            
            // Draw agents
            agents.forEach(agent => {
                ctx.fillStyle = agent.active ? '#FA4616' : '#551C25';
                ctx.beginPath();
                ctx.arc(agent.x, agent.y, 10, 0, Math.PI * 2);
                ctx.fill();
                
                ctx.fillStyle = '#E7E7E0';
                ctx.font = '10px Poppins';
                ctx.textAlign = 'center';
                ctx.fillText(agent.name, agent.x, agent.y + 20);
            });
            
            requestAnimationFrame(animate);
        };
        
        animate();
    }
    
    initSystemPulse() {
        // Update pulse metrics periodically
        setInterval(() => {
            this.updatePulseMetrics();
        }, 3000);
    }
    
    updatePulseMetrics() {
        const metrics = [
            { label: 'Queue Health', value: Math.random() * 100 },
            { label: 'Agent Efficiency', value: Math.random() * 100 },
            { label: 'Resolution Rate', value: Math.random() * 100 }
        ];
        
        metrics.forEach(metric => {
            const bar = document.querySelector(`.pulse-metric:has(.pulse-label:contains("${metric.label}")) .pulse-fill`);
            if (bar) {
                bar.style.width = `${metric.value}%`;
            }
        });
    }
    
    // Observe Mode
    initObserveMode() {
        const playBtn = document.getElementById('play-pause');
        const speedBtns = document.querySelectorAll('.btn-speed');
        
        if (playBtn) {
            playBtn.addEventListener('click', () => {
                this.toggleObserveMode();
            });
        }
        
        speedBtns.forEach(btn => {
            btn.addEventListener('click', () => {
                speedBtns.forEach(b => b.classList.remove('active'));
                btn.classList.add('active');
                this.state.observeMode.speed = parseFloat(btn.dataset.speed);
            });
        });
    }
    
    startObserveMode() {
        const canvas = document.getElementById('observe-canvas');
        if (!canvas) return;
        
        const ctx = canvas.getContext('2d');
        canvas.width = canvas.offsetWidth;
        canvas.height = canvas.offsetHeight;
        
        // Cinematic visualization
        this.renderCinematicView(ctx, canvas.width, canvas.height);
    }
    
    renderCinematicView(ctx, width, height) {
        // Create cinematic agent visualization
        let time = 0;
        
        const render = () => {
            if (!this.state.observeMode.playing) return;
            
            ctx.fillStyle = 'rgba(0, 0, 0, 0.1)';
            ctx.fillRect(0, 0, width, height);
            
            // Draw flowing data particles
            for (let i = 0; i < 50; i++) {
                const x = (time * 2 + i * 20) % width;
                const y = height / 2 + Math.sin(time * 0.01 + i) * 100;
                
                ctx.fillStyle = `rgba(250, 70, 22, ${Math.random()})`;
                ctx.beginPath();
                ctx.arc(x, y, 2, 0, Math.PI * 2);
                ctx.fill();
            }
            
            time += this.state.observeMode.speed;
            requestAnimationFrame(render);
        };
        
        render();
    }
    
    toggleObserveMode() {
        this.state.observeMode.playing = !this.state.observeMode.playing;
        const playBtn = document.getElementById('play-pause');
        
        if (playBtn) {
            playBtn.innerHTML = this.state.observeMode.playing ? 
                '<i class="fas fa-pause"></i>' : 
                '<i class="fas fa-play"></i>';
        }
        
        if (this.state.observeMode.playing) {
            this.startObserveMode();
        }
    }
    
    // AI Terminal
    initAITerminal() {
        const input = document.getElementById('terminal-input');
        const output = document.getElementById('terminal-output');
        
        if (input) {
            input.addEventListener('keypress', (e) => {
                if (e.key === 'Enter') {
                    const command = input.value.trim();
                    if (command) {
                        this.processTerminalCommand(command);
                        input.value = '';
                    }
                }
            });
        }
    }
    
    processTerminalCommand(command) {
        const output = document.getElementById('terminal-output');
        
        // Add command to output
        const commandLine = document.createElement('div');
        commandLine.innerHTML = `<span style="color: #FA4616;">neurocenter@ai &gt;</span> ${command}`;
        output.appendChild(commandLine);
        
        // Process command
        const response = this.getTerminalResponse(command);
        
        // Add response
        const responseLine = document.createElement('div');
        responseLine.style.color = '#00ff00';
        responseLine.innerHTML = response;
        output.appendChild(responseLine);
        
        // Scroll to bottom
        output.scrollTop = output.scrollHeight;
    }
    
    getTerminalResponse(command) {
        const cmd = command.toLowerCase();
        
        if (cmd === 'help') {
            return `Available commands:
  status        - Show system status
  agents        - List active agents
  queues        - Show queue status
  investigate   - Start investigation
  metrics       - Show current metrics
  clear         - Clear terminal`;
        } else if (cmd === 'status') {
            return `System Status: OPERATIONAL
Agents: ${this.state.metrics.activeAgents} active
Queues: ${this.state.queues.size} monitored
Investigations: ${this.state.investigations.size} active`;
        } else if (cmd === 'agents') {
            let agentList = 'Active Agents:\n';
            this.state.agents.forEach(agent => {
                agentList += `  - ${agent.name}: ${agent.status}\n`;
            });
            return agentList || 'No active agents';
        } else if (cmd === 'clear') {
            const output = document.getElementById('terminal-output');
            output.innerHTML = '';
            return '';
        } else if (cmd.startsWith('investigate')) {
            const queue = cmd.split(' ')[1];
            if (queue) {
                this.startInvestigation(queue);
                return `Starting investigation for ${queue}...`;
            } else {
                return 'Usage: investigate <queue-name>';
            }
        } else {
            return `Command not recognized: ${command}`;
        }
    }
    
    focusTerminal() {
        const input = document.getElementById('terminal-input');
        if (input) {
            input.focus();
        }
    }
    
    // Event Listeners
    initEventListeners() {
        // Refresh buttons
        document.querySelectorAll('.btn-refresh').forEach(btn => {
            btn.addEventListener('click', () => {
                this.refreshData();
            });
        });
        
        // Investigate button
        const investigateBtn = document.querySelector('.btn-investigate');
        if (investigateBtn) {
            investigateBtn.addEventListener('click', () => {
                this.investigateSelected();
            });
        }
        
        // Queue selection
        document.getElementById('select-all-queues')?.addEventListener('change', (e) => {
            const checkboxes = document.querySelectorAll('#queue-tbody input[type="checkbox"]');
            checkboxes.forEach(cb => cb.checked = e.target.checked);
        });
    }
    
    // Load Initial Data
    loadInitialData() {
        // Request real data from backend
        if (this.state.socket) {
            this.state.socket.emit('get_dlqs');
            this.state.socket.emit('get_agents');
            this.state.socket.emit('get_metrics');
            this.state.socket.emit('get_investigations');
        }
        
        // Load production queues
        this.loadProductionQueues();
    }
    
    loadProductionQueues() {
        const tbody = document.getElementById('queue-tbody');
        if (!tbody) return;
        
        // Use real production queue names
        const queues = [
            { name: 'fm-payment-notification-dlq-prod', messages: 0, status: 'ok', type: 'DLQ' },
            { name: 'fm-order-dlq-production', messages: 0, status: 'ok', type: 'DLQ' },
            { name: 'fm-risk-dlq-production', messages: 0, status: 'ok', type: 'DLQ' },
            { name: 'fm-fraud-dlq-production', messages: 0, status: 'ok', type: 'DLQ' },
            { name: 'fm-reconciliation-dlq-prod', messages: 0, status: 'ok', type: 'DLQ' }
        ];
        
        tbody.innerHTML = '';
        queues.forEach(queue => {
            const row = document.createElement('tr');
            row.innerHTML = `
                <td><input type="checkbox" data-queue="${queue.name}"></td>
                <td>${queue.name}</td>
                <td><span class="badge-type">${queue.type}</span></td>
                <td><span class="message-count">${queue.messages}</span></td>
                <td><span class="status-badge ${queue.status}">${queue.status.toUpperCase()}</span></td>
                <td>
                    <button class="btn-action" onclick="neuroCenter.investigateQueue('${queue.name}')">
                        <i class="fas fa-search"></i>
                    </button>
                </td>
            `;
            tbody.appendChild(row);
        });
    }
    
    // Handle Updates
    handleDLQUpdate(data) {
        this.state.queues.set(data.name, data);
        this.updateQueueDisplay(data);
        
        if (data.messages > 0) {
            this.addToActivityFeed(
                'System',
                `Queue ${data.name} now has ${data.messages} messages`
            );
        }
    }
    
    handleAgentUpdate(data) {
        this.state.agents.set(data.id, data);
        this.updateAgentDisplay(data);
        
        if (data.status === 'investigating') {
            this.addToActivityFeed(
                data.name,
                `Started investigating ${data.currentTask}`
            );
        }
    }
    
    handleInvestigationUpdate(data) {
        this.state.investigations.set(data.id, data);
        this.updateInvestigationTimeline(data);
    }
    
    handleMetricsUpdate(data) {
        this.state.metrics = data;
        this.updateMetricsDisplay();
    }
    
    handleAlert(data) {
        const alertBar = document.getElementById('alerts-bar');
        const alertText = document.getElementById('alert-text');
        
        if (alertBar && alertText) {
            alertText.textContent = data.message;
            alertBar.style.display = 'block';
            
            setTimeout(() => {
                alertBar.style.display = 'none';
            }, 10000);
        }
    }
    
    // Update Displays
    updateQueueDisplay(queue) {
        const row = document.querySelector(`tr:has(td:contains("${queue.name}"))`);
        if (row) {
            row.querySelector('.message-count').textContent = queue.messages;
            row.querySelector('.status-badge').className = `status-badge ${queue.status}`;
            row.querySelector('.status-badge').textContent = queue.status.toUpperCase();
        }
    }
    
    updateAgentDisplay(agent) {
        const card = document.querySelector(`[data-agent="${agent.id}"]`);
        if (card) {
            card.querySelector('.agent-status').className = `agent-status ${agent.status}`;
            card.querySelector('.agent-task').textContent = agent.currentTask || 'Idle';
        }
    }
    
    updateInvestigationTimeline(investigation) {
        const timeline = document.getElementById('investigation-timeline');
        if (!timeline) return;
        
        const entry = document.createElement('div');
        entry.className = 'timeline-entry';
        entry.innerHTML = `
            <div class="timeline-time">${new Date(investigation.startTime).toLocaleTimeString()}</div>
            <div class="timeline-content">
                <strong>${investigation.dlq}</strong> - ${investigation.status}
            </div>
        `;
        
        timeline.insertBefore(entry, timeline.firstChild);
    }
    
    updateMetricsDisplay() {
        document.getElementById('metric-active-agents').textContent = this.state.metrics.activeAgents;
        document.getElementById('metric-avg-time').textContent = `${this.state.metrics.avgTime}m`;
        document.getElementById('metric-prs').textContent = this.state.metrics.prsGenerated;
        document.getElementById('metric-success').textContent = `${this.state.metrics.successRate}%`;
    }
    
    updateStatus(status) {
        const statusText = document.querySelector('.status-text');
        if (statusText) {
            statusText.textContent = status;
        }
    }
    
    // Actions
    refreshData() {
        if (this.state.socket) {
            this.state.socket.emit('request_update');
        }
    }
    
    investigateSelected() {
        const selected = document.querySelectorAll('#queue-tbody input[type="checkbox"]:checked');
        selected.forEach(cb => {
            const queue = cb.dataset.queue;
            if (queue) {
                this.investigateQueue(queue);
            }
        });
    }
    
    investigateQueue(queueName) {
        if (this.state.socket) {
            this.state.socket.emit('investigate_dlq', { dlq_name: queueName });
            this.addToActivityFeed('System', `Investigation requested for ${queueName}`);
        }
    }
    
    investigateCritical() {
        // Find queue with most messages
        let criticalQueue = null;
        let maxMessages = 0;
        
        this.state.queues.forEach(queue => {
            if (queue.messages > maxMessages) {
                maxMessages = queue.messages;
                criticalQueue = queue.name;
            }
        });
        
        if (criticalQueue) {
            this.investigateQueue(criticalQueue);
        }
    }
    
    startInvestigation(queueName) {
        this.investigateQueue(queueName);
    }
    
    showNotification(message, type = 'info') {
        console.log(`[${type.toUpperCase()}] ${message}`);
    }
}

// Initialize NeuroCenter when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    window.neuroCenter = new NeuroCenter();
});