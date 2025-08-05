# Core Monitor API

The Core Monitor API provides the main monitoring service interfaces for the AWS DLQ Claude Monitor system.

## Overview

The core monitoring system consists of several key components:
- **MonitorService**: Main monitoring orchestrator
- **DLQService**: AWS SQS DLQ interaction layer
- **ConfigurationManager**: System configuration management
- **EventHandler**: Event processing and routing

## MonitorService Class

The primary interface for DLQ monitoring operations.

### Class Definition

```python
from dlq_monitor.core.monitor import MonitorService
from dlq_monitor.core.config import MonitorConfig

class MonitorService:
    def __init__(
        self, 
        config: MonitorConfig = None,
        aws_profile: str = None,
        region: str = None
    ):
        """Initialize monitor service."""
        pass
```

### Constructor Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `config` | `MonitorConfig` | No | Configuration object |
| `aws_profile` | `str` | No | AWS profile name |
| `region` | `str` | No | AWS region |

### Methods

#### start_monitoring()

Starts the main monitoring loop.

```python
def start_monitoring(
    self,
    interval: int = 30,
    max_cycles: int = None,
    auto_investigate: bool = True
) -> MonitorResult:
    """
    Start DLQ monitoring.
    
    Args:
        interval: Check interval in seconds
        max_cycles: Maximum monitoring cycles (None for infinite)
        auto_investigate: Enable auto-investigation
        
    Returns:
        MonitorResult: Monitoring execution result
        
    Raises:
        MonitorError: If monitoring fails to start
        AWSConnectionError: If AWS connection fails
    """
```

**Example Usage:**
```python
from dlq_monitor.core import MonitorService

monitor = MonitorService(
    aws_profile="FABIO-PROD",
    region="sa-east-1"
)

result = monitor.start_monitoring(
    interval=30,
    auto_investigate=True
)

print(f"Monitoring completed: {result.cycles_completed} cycles")
```

#### discover_dlqs()

Discovers all DLQ queues matching configured patterns.

```python
def discover_dlqs(self) -> List[DLQInfo]:
    """
    Discover DLQ queues.
    
    Returns:
        List[DLQInfo]: List of discovered DLL queues
        
    Raises:
        AWSConnectionError: If unable to connect to AWS
        PermissionError: If insufficient AWS permissions
    """
```

**Example Usage:**
```python
dlqs = monitor.discover_dlqs()
for dlq in dlqs:
    print(f"Queue: {dlq.name}, Messages: {dlq.message_count}")
```

#### check_queue_status()

Checks the status of a specific queue.

```python
def check_queue_status(self, queue_name: str) -> QueueStatus:
    """
    Check status of specific queue.
    
    Args:
        queue_name: Name of the queue to check
        
    Returns:
        QueueStatus: Current queue status
        
    Raises:
        QueueNotFoundError: If queue doesn't exist
        AWSConnectionError: If unable to access queue
    """
```

#### trigger_investigation()

Manually triggers investigation for a queue.

```python
def trigger_investigation(
    self, 
    queue_name: str,
    force: bool = False
) -> InvestigationResult:
    """
    Trigger investigation for specific queue.
    
    Args:
        queue_name: Queue to investigate
        force: Skip cooldown checks
        
    Returns:
        InvestigationResult: Investigation execution result
        
    Raises:
        CooldownError: If queue is in cooldown period
        InvestigationError: If investigation fails to start
    """
```

## Data Classes

### MonitorConfig

Configuration class for the monitor service.

```python
@dataclass
class MonitorConfig:
    aws_profile: str
    region: str
    check_interval: int = 30
    notification_threshold: int = 1
    auto_investigate_dlqs: List[str] = None
    claude_command_timeout: int = 1800  # 30 minutes
    cooldown_hours: int = 1
    max_concurrent_investigations: int = 5
    
    # Notification settings
    enable_macos_notifications: bool = True
    enable_audio_notifications: bool = True
    
    # GitHub integration
    github_token: str = None
    github_username: str = None
    monitor_prs: bool = True
```

### DLQInfo

Information about a discovered DLQ.

```python
@dataclass
class DLQInfo:
    name: str
    url: str
    message_count: int
    approximate_age_of_oldest_message: int
    last_modified: datetime
    attributes: Dict[str, Any]
    
    @property
    def is_empty(self) -> bool:
        return self.message_count == 0
        
    @property
    def needs_attention(self) -> bool:
        return self.message_count > 0
```

### QueueStatus

Current status of a queue.

```python
@dataclass
class QueueStatus:
    queue_name: str
    message_count: int
    messages_available: int
    messages_in_flight: int
    oldest_message_age: int
    last_checked: datetime
    
    # Investigation status
    investigation_active: bool = False
    last_investigation: datetime = None
    investigation_cooldown_until: datetime = None
    
    @property
    def in_cooldown(self) -> bool:
        if not self.investigation_cooldown_until:
            return False
        return datetime.now() < self.investigation_cooldown_until
```

### MonitorResult

Result of monitoring operation.

```python
@dataclass
class MonitorResult:
    success: bool
    cycles_completed: int
    errors: List[str]
    start_time: datetime
    end_time: datetime
    total_dlqs_checked: int
    dlqs_with_messages: int
    investigations_triggered: int
    
    @property
    def duration(self) -> timedelta:
        return self.end_time - self.start_time
        
    @property
    def average_cycle_time(self) -> float:
        if self.cycles_completed == 0:
            return 0.0
        return self.duration.total_seconds() / self.cycles_completed
```

## Event Handling

### EventHandler Class

Handles system events and routing.

```python
class EventHandler:
    def __init__(self):
        self._handlers = {}
    
    def register_handler(self, event_type: str, handler: Callable):
        """Register event handler."""
        
    def emit_event(self, event: Event):
        """Emit event to registered handlers."""
        
    def remove_handler(self, event_type: str, handler: Callable):
        """Remove event handler."""
```

### Event Types

```python
class EventType:
    DLQ_MESSAGE_DETECTED = "dlq.message_detected"
    INVESTIGATION_STARTED = "investigation.started"
    INVESTIGATION_COMPLETED = "investigation.completed"
    INVESTIGATION_FAILED = "investigation.failed"
    INVESTIGATION_TIMEOUT = "investigation.timeout"
    PR_CREATED = "pr.created"
    NOTIFICATION_SENT = "notification.sent"
```

### Event Class

```python
@dataclass
class Event:
    type: str
    data: Dict[str, Any]
    timestamp: datetime
    source: str
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "type": self.type,
            "data": self.data,
            "timestamp": self.timestamp.isoformat(),
            "source": self.source
        }
```

## Error Handling

### Exception Hierarchy

```python
class MonitorError(Exception):
    """Base exception for monitor errors."""
    pass

class AWSConnectionError(MonitorError):
    """AWS connection or authentication error."""
    pass

class QueueNotFoundError(MonitorError):
    """Specified queue not found."""
    pass

class InvestigationError(MonitorError):
    """Investigation execution error."""
    pass

class CooldownError(MonitorError):
    """Operation blocked by cooldown period."""
    pass

class ConfigurationError(MonitorError):
    """Configuration validation error."""
    pass
```

### Error Response Format

```python
@dataclass
class ErrorResponse:
    success: bool = False
    error_code: str = None
    error_message: str = None
    error_details: Dict[str, Any] = None
    timestamp: datetime = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "success": self.success,
            "error": {
                "code": self.error_code,
                "message": self.error_message,
                "details": self.error_details
            },
            "timestamp": self.timestamp.isoformat()
        }
```

## Configuration Management

### ConfigurationManager Class

```python
class ConfigurationManager:
    def __init__(self, config_path: str = "config/config.yaml"):
        self.config_path = config_path
        self._config = None
    
    def load_config(self) -> MonitorConfig:
        """Load configuration from file."""
        
    def validate_config(self, config: MonitorConfig) -> List[str]:
        """Validate configuration and return errors."""
        
    def save_config(self, config: MonitorConfig):
        """Save configuration to file."""
        
    def get_default_config(self) -> MonitorConfig:
        """Get default configuration."""
```

## Usage Examples

### Basic Monitoring

```python
from dlq_monitor.core import MonitorService, MonitorConfig

# Create configuration
config = MonitorConfig(
    aws_profile="FABIO-PROD",
    region="sa-east-1",
    auto_investigate_dlqs=[
        "fm-digitalguru-api-update-dlq-prod",
        "fm-transaction-processor-dlq-prd"
    ]
)

# Initialize monitor
monitor = MonitorService(config)

# Start monitoring
result = monitor.start_monitoring(interval=30)
print(f"Monitoring completed after {result.cycles_completed} cycles")
```

### Event-Driven Monitoring

```python
from dlq_monitor.core import MonitorService, EventHandler, EventType

def on_dlq_message(event):
    print(f"DLQ message detected: {event.data['queue_name']}")

def on_investigation_completed(event):
    print(f"Investigation completed: {event.data['result']}")

# Setup event handling
handler = EventHandler()
handler.register_handler(EventType.DLQ_MESSAGE_DETECTED, on_dlq_message)
handler.register_handler(EventType.INVESTIGATION_COMPLETED, on_investigation_completed)

# Start monitoring with event handling
monitor = MonitorService(event_handler=handler)
monitor.start_monitoring()
```

### Queue Discovery and Status

```python
from dlq_monitor.core import MonitorService

monitor = MonitorService(aws_profile="FABIO-PROD", region="sa-east-1")

# Discover all DLQs
dlqs = monitor.discover_dlqs()
print(f"Found {len(dlqs)} DLQ queues")

# Check specific queue status
status = monitor.check_queue_status("fm-digitalguru-api-update-dlq-prod")
print(f"Queue has {status.message_count} messages")
print(f"In cooldown: {status.in_cooldown}")

# Trigger investigation if needed
if status.message_count > 0 and not status.in_cooldown:
    result = monitor.trigger_investigation(status.queue_name)
    print(f"Investigation triggered: {result.success}")
```

## Performance Considerations

### Resource Usage
- **Memory**: ~50-100MB baseline, +50MB per active investigation
- **CPU**: Low usage during idle, moderate during investigations
- **Network**: AWS API calls every check interval

### Optimization Tips
- Increase check intervals for large-scale deployments
- Use queue patterns instead of explicit queue lists
- Implement connection pooling for high-frequency checks
- Monitor resource usage and adjust timeouts accordingly

### Scaling Guidelines
- Single instance handles 100+ queues efficiently
- Use multiple instances for different AWS regions
- Implement load balancing for high-availability setups
- Consider rate limiting for AWS API calls

## Testing

### Unit Testing

```python
import pytest
from unittest.mock import Mock, patch
from dlq_monitor.core import MonitorService, MonitorConfig

def test_monitor_initialization():
    config = MonitorConfig(
        aws_profile="test-profile",
        region="us-east-1"
    )
    monitor = MonitorService(config)
    assert monitor.config.aws_profile == "test-profile"

@patch('dlq_monitor.core.boto3')
def test_discover_dlqs(mock_boto3):
    mock_sqs = Mock()
    mock_boto3.Session().client.return_value = mock_sqs
    mock_sqs.list_queues.return_value = {
        'QueueUrls': ['https://sqs.us-east-1.amazonaws.com/123/test-dlq']
    }
    
    monitor = MonitorService(aws_profile="test", region="us-east-1")
    dlqs = monitor.discover_dlqs()
    
    assert len(dlqs) == 1
    assert "test-dlq" in dlqs[0].name
```

### Integration Testing

```python
def test_full_monitoring_cycle():
    """Test complete monitoring cycle with mocked AWS."""
    # Implementation would test full monitoring flow
    pass

def test_investigation_trigger():
    """Test auto-investigation triggering."""
    # Implementation would test investigation trigger logic
    pass
```

---

**Last Updated**: 2025-08-05
**API Version**: 2.0.0