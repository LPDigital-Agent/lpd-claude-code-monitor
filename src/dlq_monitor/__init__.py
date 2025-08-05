"""
AWS SQS Dead Letter Queue Monitor - Enhanced for FABIO-PROD

A comprehensive monitoring system for AWS SQS Dead Letter Queues with Claude AI
auto-investigation capabilities, GitHub PR creation, and multi-modal notifications.

This package monitors DLQs across AWS accounts, triggers automated investigations
when messages are detected, and can create GitHub PRs with fixes.
"""

__version__ = "1.0.0"
__author__ = "Fabio Santos"
__email__ = "fabio.santos@example.com"

# Lazy imports to avoid dependency issues at package level
# Import only when actually needed by accessing the module attribute

def __getattr__(name):
    """Lazy import implementation to avoid loading dependencies at package import time."""
    # Handle submodule imports
    if name in ["claude", "core", "dashboards", "notifiers", "utils"]:
        import importlib
        module = importlib.import_module(f".{name}", __name__)
        return module
    
    # Handle class/function imports
    if name in _LAZY_IMPORTS:
        module_path = _LAZY_IMPORTS[name]
        try:
            module = __import__(module_path, fromlist=[name])
            return getattr(module, name)
        except ImportError as e:
            raise ImportError(f"Failed to import {name} from {module_path}: {e}")
    
    raise AttributeError(f"module '{__name__}' has no attribute '{name}'")

# Mapping of public names to their module paths
_LAZY_IMPORTS = {
    # Core classes
    "DLQAlert": "dlq_monitor.core.monitor",
    "MonitorConfig": "dlq_monitor.core.monitor", 
    "MacNotifier": "dlq_monitor.core.monitor",
    "PRAlert": "dlq_monitor.core.monitor",
    "AudioNotifier": "dlq_monitor.core.monitor",
    "PRMonitor": "dlq_monitor.core.monitor",
    "DLQMonitor": "dlq_monitor.core.monitor",
    
    # CLI
    "cli": "dlq_monitor.cli",
    
    # Claude integration
    "LiveClaudeMonitor": "dlq_monitor.claude.live_monitor",
    "ClaudeSessionMonitor": "dlq_monitor.claude.session_manager",
    
    # Dashboards
    "EnhancedLiveMonitor": "dlq_monitor.dashboards.enhanced",
    "UltimateClaudeMonitor": "dlq_monitor.dashboards.ultimate",
    
    # Notifiers
    "PRAudioMonitor": "dlq_monitor.notifiers.pr_audio",
    "GitHubPRMonitor": "dlq_monitor.notifiers.pr_audio", 
    "ElevenLabsTTS": "dlq_monitor.notifiers.pr_audio",
    
    # Utils
    "ProductionMonitor": "dlq_monitor.utils.production_monitor",
}

__all__ = [
    # Core classes
    "DLQAlert",
    "MonitorConfig", 
    "MacNotifier",
    "PRAlert",
    "AudioNotifier",
    "PRMonitor",
    "DLQMonitor",
    
    # CLI
    "cli",
    
    # Claude integration
    "LiveClaudeMonitor",
    "ClaudeSessionMonitor",
    
    # Dashboards
    "EnhancedLiveMonitor",
    "UltimateClaudeMonitor",
    
    # Notifiers
    "PRAudioMonitor",
    "GitHubPRMonitor", 
    "ElevenLabsTTS",
    
    # Utils
    "ProductionMonitor",
    
    # Package metadata
    "__version__",
    "__author__",
    "__email__",
]