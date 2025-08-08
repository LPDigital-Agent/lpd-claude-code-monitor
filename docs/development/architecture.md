# System Architecture

This document provides a comprehensive overview of the AWS DLQ Claude Monitor system architecture, including component relationships, data flow, and design decisions.

## 🏗️ High-Level Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   External      │    │   Core System   │    │   Integrations  │
│   Services      │    │                 │    │                 │
├─────────────────┤    ├─────────────────┤    ├─────────────────┤
│ AWS SQS DLQs    │◀──▶│ DLQ Monitor     │◀──▶│ Claude AI       │
│ CloudWatch      │    │ Core Engine     │    │ Auto-Investigate│
│ AWS IAM         │    │                 │    │                 │
├─────────────────┤    ├─────────────────┤    ├─────────────────┤
│ GitHub API      │◀──▶│ Event Handler   │◀──▶│ GitHub PRs      │
│ ElevenLabs API  │    │ & Router        │    │ Issue Tracking  │
│ macOS Notifs    │    │                 │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                               │
                       ┌─────────────────┐
                       │ User Interfaces │
                       ├─────────────────┤
                       │ Enhanced        │
                       │ Dashboard       │
                       │ (Curses UI)     │
                       │                 │
                       │ Ultimate        │
                       │ Monitor         │
                       │ (Advanced UI)   │
                       │                 │
                       │ CLI Interface   │
                       │ Status Commands │
                       └─────────────────┘
```

## 🧩 Component Architecture

### 1. Core Monitoring Engine

#### MonitorService (Primary Orchestrator)
```python
src/dlq_monitor/core/monitor.py
```
- **Responsibilities**: Main monitoring loop, queue discovery, status tracking
- **Key Features**: 
  - Configurable check intervals
  - Pattern-based queue discovery
  - Auto-investigation triggering
  - Event emission
- **Dependencies**: AWS SQS, ConfigurationManager, EventHandler

#### DLQService (AWS Integration Layer)
```python
src/dlq_monitor/core/dlq_service.py
```
- **Responsibilities**: AWS SQS interaction, queue attributes retrieval
- **Key Features**:
  - Boto3 session management
  - Queue filtering and pattern matching
  - Message count retrieval
  - Queue purging capabilities
- **Dependencies**: boto3, AWS credentials

### 2. Claude AI Investigation System

#### Multi-Agent Architecture
```
┌─────────────────────────────────────────────────────────────┐
│                Claude Investigation Engine                   │
├─────────────────┬─────────────────┬─────────────────────────┤
│   Subagent 1    │   Subagent 2    │      Subagent 3         │
│   DLQ Analysis  │   Log Analysis  │   Codebase Review       │
├─────────────────┼─────────────────┼─────────────────────────┤
│   Subagent 4    │   Subagent 5    │      Coordinator        │
│   Config Check  │   Test Runner   │   Result Aggregation    │
└─────────────────┴─────────────────┴─────────────────────────┘
```

#### SessionManager
```python
src/dlq_monitor/claude/session_manager.py
```
- **Responsibilities**: Investigation session tracking, cooldown management
- **Key Features**:
  - Session persistence (.claude_sessions.json)
  - Cooldown period enforcement
  - Process monitoring
  - Timeout handling
- **Data Storage**: JSON file-based session tracking

#### Investigation Flow
1. **Trigger Detection**: Monitor detects DLQ messages
2. **Eligibility Check**: Verify cooldown and concurrent limits
3. **Process Spawning**: Launch Claude subprocess with enhanced prompt
4. **Session Tracking**: Record session details and monitor progress
5. **Result Processing**: Handle completion, failure, or timeout
6. **Cleanup**: Update session state and emit events

### 3. Notification System

#### Multi-Channel Notification Architecture
```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│ Event Source    │───▶│ Notification    │───▶│ Output Channels │
│                 │    │ Router          │    │                 │
├─────────────────┤    ├─────────────────┤    ├─────────────────┤
│ DLQ Messages    │    │ Channel         │    │ macOS Native    │
│ Investigation   │    │ Selection       │    │ Notifications   │
│ PR Updates      │    │ Logic           │    │                 │
│ System Errors   │    │                 │    │ ElevenLabs TTS  │
└─────────────────┘    └─────────────────┘    │ Audio Alerts    │
                                              │                 │
                                              │ Console Output  │
                                              │ (Rich formatted)│
                                              └─────────────────┘
```

#### PRNotifier (Audio System)
```python
src/dlq_monitor/notifiers/pr_audio.py
```
- **Responsibilities**: PR monitoring, audio generation, playback
- **Key Features**:
  - GitHub API integration
  - ElevenLabs TTS synthesis
  - Audio caching and playback
  - Reminder scheduling
- **Dependencies**: requests, pygame, elevenlabs-api

### 4. Dashboard System

#### Multi-Panel Dashboard Architecture
```
┌─────────────────────────────────────────────────────────────┐
│                     Enhanced Dashboard                      │
├─────────────────────┬───────────────────────────────────────┤
│   DLQ Status Panel  │          Claude Agents Panel         │
│   ┌─────────────┐   │   ┌─────────────┐ ┌─────────────┐     │
│   │ Queue Names │   │   │ Agent PIDs  │ │ CPU Usage   │     │
│   │ Msg Counts  │   │   │ Runtime     │ │ Memory      │     │
│   │ Color Codes │   │   │ Queue       │ │ Status      │     │
│   └─────────────┘   │   └─────────────┘ └─────────────┘     │
├─────────────────────┴───────────────────────────────────────┤
│                    GitHub PRs Panel                         │
│   ┌─────────────┐ ┌─────────────┐ ┌─────────────┐           │
│   │ PR Number   │ │ Repository  │ │ Title       │           │
│   │ Status      │ │ Author      │ │ Age         │           │
│   └─────────────┘ └─────────────┘ └─────────────┘           │
├─────────────────────────────────────────────────────────────┤
│                Investigation Timeline                       │
│  [15:58:56] [08:52] ✅ Investigation completed              │
│  [16:02:14] [02:31] 🔧 PR created #127                     │
│  [16:05:23] [--:--] 🚨 New DLQ messages detected           │
└─────────────────────────────────────────────────────────────┘
```

#### Dashboard Components
- **Enhanced Monitor**: Multi-panel real-time dashboard
- **Ultimate Monitor**: Advanced analytics and metrics
- **Status Monitor**: Investigation-focused view
- **CLI Interface**: Command-line status and control

### 5. Configuration Management

#### Hierarchical Configuration System
```
Environment Variables (.env)
         ↓
System Config (config.yaml)
         ↓
Runtime Configuration
         ↓
Component-Specific Settings
```

#### Configuration Sources
1. **Environment Variables**: Secrets and credentials
2. **YAML Configuration**: System settings and preferences
3. **Command Line Arguments**: Runtime overrides
4. **Default Values**: Fallback configurations

### 6. Data Flow Architecture

#### Primary Data Flow
```
AWS SQS DLQs → MonitorService → EventHandler → [Notifications + Investigations]
     ↓                            ↓                        ↓
Queue Attributes → Status Updates → Dashboard Updates → User Interface
     ↓                            ↓                        ↓
Message Counts → Investigation → Claude AI Process → GitHub PR Creation
```

#### Event-Driven Architecture
```python
# Event emission example
event = Event(
    type=EventType.DLQ_MESSAGE_DETECTED,
    data={
        'queue_name': queue_name,
        'message_count': count,
        'timestamp': datetime.now()
    },
    source='MonitorService'
)
event_handler.emit_event(event)
```

## 🔄 Process Architecture

### 1. Main Monitor Process
- **Lifecycle**: Long-running daemon process
- **Responsibilities**: Core monitoring loop, event coordination
- **Resource Usage**: Low CPU/memory baseline
- **Recovery**: Automatic restart on failure

### 2. Investigation Subprocess
- **Lifecycle**: Short-lived (5-30 minutes)
- **Responsibilities**: Claude AI interaction, code analysis
- **Resource Usage**: High CPU/memory during execution
- **Recovery**: Timeout handling, session cleanup

### 3. Dashboard Processes
- **Lifecycle**: User-initiated, interactive
- **Responsibilities**: Real-time UI updates, user interaction
- **Resource Usage**: Moderate CPU for UI rendering
- **Recovery**: Graceful degradation on errors

### 4. Notification Background Tasks
- **Lifecycle**: Event-driven, short-lived
- **Responsibilities**: Message delivery, audio generation
- **Resource Usage**: Minimal baseline, spikes during notification
- **Recovery**: Retry logic, fallback channels

## 🗃️ Data Architecture

### 1. Session Storage
```json
// .claude_sessions.json
{
  "sessions": [
    {
      "queue_name": "fm-digitalguru-api-update-dlq-prod",
      "status": "running",
      "pid": 12345,
      "start_time": "2025-08-05T15:25:22Z",
      "timeout_at": "2025-08-05T15:55:22Z",
      "cooldown_until": "2025-08-05T16:25:22Z"
    }
  ]
}
```

### 2. Configuration Data
```yaml
# config/config.yaml
aws:
  profile: "FABIO-PROD"
  region: "sa-east-1"

monitoring:
  check_interval: 30
  notification_threshold: 1

auto_investigation:
  enabled: true
  target_queues:
    - "fm-digitalguru-api-update-dlq-prod"
    - "fm-transaction-processor-dlq-prd"
  timeout_minutes: 30
  cooldown_hours: 1
```

### 3. Log Data Structure
```
2025-08-05 15:25:22 [INFO] DLQ Check - Queue: fm-digitalguru-api-update-dlq-prod, Messages: 8
2025-08-05 15:25:23 [INFO] 🎆 Triggering auto-investigation for fm-digitalguru-api-update-dlq-prod
2025-08-05 15:25:24 [INFO] 🚀 Starting auto-investigation for fm-digitalguru-api-update-dlq-prod
```

## 🔐 Security Architecture

### 1. Credential Management
- **AWS Credentials**: IAM roles/profiles, no hardcoded keys
- **API Keys**: Environment variables, encrypted at rest
- **GitHub Tokens**: Fine-grained permissions, regular rotation

### 2. Network Security
- **HTTPS**: All external API communications
- **Rate Limiting**: Respect API limits, implement backoff
- **Validation**: Input sanitization, output encoding

### 3. Process Security
- **Isolation**: Subprocess isolation for investigations
- **Timeout Protection**: Prevent resource exhaustion
- **Privilege Separation**: Minimal required permissions

## 🚀 Scalability Architecture

### 1. Horizontal Scaling
- **Multi-Instance**: Multiple monitor instances per region
- **Load Distribution**: Queue-based workload distribution
- **State Sharing**: Shared session storage for coordination

### 2. Vertical Scaling
- **Resource Tuning**: Configurable timeouts and limits
- **Process Optimization**: Efficient subprocess management
- **Memory Management**: Garbage collection and cleanup

### 3. Performance Optimizations
- **Connection Pooling**: Reuse AWS connections
- **Caching**: Cache queue metadata and attributes
- **Async Operations**: Non-blocking investigations
- **Batch Processing**: Group API calls when possible

## 🔍 Monitoring & Observability

### 1. Metrics Collection
- **System Metrics**: CPU, memory, disk usage
- **Application Metrics**: Queue counts, investigation success rates
- **Business Metrics**: MTTR, investigation effectiveness

### 2. Logging Strategy
- **Structured Logging**: JSON format for machine processing
- **Log Levels**: DEBUG, INFO, WARN, ERROR, CRITICAL
- **Log Rotation**: Automatic cleanup and archival
- **Correlation IDs**: Track requests across components

### 3. Health Checks
- **AWS Connectivity**: Regular connection validation
- **Claude Availability**: CLI command verification
- **GitHub Integration**: API token validation
- **System Resources**: Memory and disk monitoring

## 🧪 Testing Architecture

### 1. Unit Testing
- **Component Isolation**: Mock external dependencies
- **Test Coverage**: >80% code coverage target
- **Fast Execution**: Millisecond-level test execution

### 2. Integration Testing
- **AWS Integration**: Test with real AWS services
- **End-to-End**: Full workflow validation
- **Performance Testing**: Load and stress testing

### 3. Testing Infrastructure
- **Test Fixtures**: Reusable test data and mocks
- **CI/CD Integration**: Automated testing pipeline
- **Environment Management**: Isolated test environments

## 📊 Deployment Architecture

### 1. Deployment Models
- **Single Instance**: Development and small-scale deployment
- **Multi-Instance**: Production with high availability
- **Containerized**: Docker-based deployment option
- **Serverless**: AWS Lambda for event-driven scaling

### 2. Configuration Management
- **Environment-Specific**: Dev, staging, production configs
- **Secret Management**: AWS Secrets Manager integration
- **Feature Flags**: Runtime feature toggling
- **Blue-Green Deployment**: Zero-downtime updates

### 3. Monitoring Deployment
- **Health Endpoints**: Application health checks
- **Metrics Export**: Prometheus/CloudWatch integration
- **Alerting**: Threshold-based alerts and notifications
- **Dashboard**: Grafana/CloudWatch dashboards

---

**Last Updated**: 2025-08-05
**Architecture Version**: 2.0 - Multi-Agent Enhanced System