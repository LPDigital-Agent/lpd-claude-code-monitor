# API Documentation

This directory contains technical API documentation for developers integrating with or extending the AWS DLQ Claude Monitor system.

## API Reference

### 🏗️ Core Components
- **[Core Monitor API](./core-monitor.md)** - Main monitoring service APIs and interfaces
- **[DLQ Service API](./dlq-service.md)** - AWS SQS DLQ interaction APIs
- **[Configuration API](./configuration.md)** - System configuration and settings APIs

### 🤖 Claude Integration
- **[Claude Integration API](./claude-integration.md)** - Claude AI auto-investigation APIs
- **[Session Manager API](./session-manager.md)** - Investigation session management
- **[Multi-Agent API](./multi-agent.md)** - Subagent deployment and coordination

### 🔗 External Integrations
- **[GitHub Integration API](./github-integration.md)** - GitHub PR creation and management
- **[AWS Services API](./aws-services.md)** - AWS service interaction wrappers
- **[Notification System API](./notification-system.md)** - Notification and alert APIs

### 📊 Data & Analytics
- **[Metrics API](./metrics.md)** - System metrics and analytics
- **[Logging API](./logging.md)** - Structured logging and audit trails
- **[Dashboard API](./dashboard.md)** - Dashboard data and updates

## API Design Principles

### RESTful Design
- Consistent HTTP methods and status codes
- Resource-based URLs
- JSON request/response format
- Proper error handling and messaging

### Async Operations
- Non-blocking investigation triggers
- Background process management
- Event-driven architecture
- Progress tracking and status updates

### Security
- Authentication and authorization
- API key management
- Rate limiting and throttling
- Input validation and sanitization

## Common Patterns

### Response Format
```json
{
  "success": true,
  "data": { ... },
  "message": "Operation completed successfully",
  "timestamp": "2025-08-05T15:30:45Z"
}
```

### Error Format
```json
{
  "success": false,
  "error": {
    "code": "INVESTIGATION_TIMEOUT",
    "message": "Investigation exceeded timeout limit",
    "details": { ... }
  },
  "timestamp": "2025-08-05T15:30:45Z"
}
```

### Pagination
```json
{
  "data": [ ... ],
  "pagination": {
    "page": 1,
    "limit": 50,
    "total": 150,
    "has_next": true
  }
}
```

## Authentication

### API Keys
Most APIs require authentication via environment variables:
- `GITHUB_TOKEN`: GitHub Personal Access Token
- `ELEVEN_LABS_API_KEY`: ElevenLabs TTS API key
- AWS credentials via AWS CLI profile

### Example Usage
```python
import os
from dlq_monitor.core import MonitorService

# Initialize with configuration
monitor = MonitorService(
    aws_profile=os.getenv('AWS_PROFILE'),
    github_token=os.getenv('GITHUB_TOKEN')
)

# Start monitoring
result = monitor.start_monitoring(
    interval=30,
    auto_investigate=True
)
```

## Rate Limits

### AWS Services
- SQS: 3000 requests per second per region
- CloudWatch: 150 requests per second

### External APIs
- GitHub: 5000 requests per hour (authenticated)
- ElevenLabs: Varies by plan

### Internal Limits
- Investigation cooldown: 1 hour per queue
- Max concurrent investigations: 5
- Dashboard refresh: 3 seconds minimum

## Webhooks & Events

### Event Types
- `dlq.message_received`: New messages in DLQ
- `investigation.started`: Auto-investigation triggered
- `investigation.completed`: Investigation finished
- `pr.created`: GitHub PR created
- `notification.sent`: Notification delivered

### Webhook Format
```json
{
  "event": "investigation.completed",
  "data": {
    "queue_name": "fm-digitalguru-api-update-dlq-prod",
    "status": "success",
    "duration": 485,
    "pr_url": "https://github.com/user/repo/pull/123"
  },
  "timestamp": "2025-08-05T15:30:45Z"
}
```

## SDK Examples

### Python SDK
```python
from dlq_monitor import DLQMonitor, InvestigationConfig

# Initialize monitor
monitor = DLQMonitor(
    profile='FABIO-PROD',
    region='sa-east-1'
)

# Configure auto-investigation
config = InvestigationConfig(
    auto_investigate_dlqs=[
        'fm-digitalguru-api-update-dlq-prod',
        'fm-transaction-processor-dlq-prd'
    ],
    timeout_minutes=30,
    cooldown_hours=1
)

# Start monitoring
monitor.start(config)
```

## Testing APIs

### Unit Tests
```bash
# Run API unit tests
pytest tests/unit/test_api.py -v

# Run integration tests
pytest tests/integration/test_api_integration.py -v
```

### Manual Testing
```bash
# Test core monitor API
python -m dlq_monitor.core.test_api

# Test Claude integration
python -m dlq_monitor.claude.test_integration

# Test GitHub integration
python -m dlq_monitor.utils.test_github
```

## Versioning

The API follows semantic versioning:
- **Major**: Breaking changes
- **Minor**: New features, backward compatible
- **Patch**: Bug fixes, backward compatible

Current version: `2.0.0`

## Deprecation Policy

- Deprecated endpoints marked with `@deprecated` decorator
- 6-month deprecation notice before removal
- Migration guides provided for breaking changes
- Backward compatibility maintained for 2 major versions

---

**Last Updated**: 2025-08-05
**API Version**: 2.0.0