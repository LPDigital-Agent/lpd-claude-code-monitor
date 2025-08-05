"""
Core Module

This module contains the core monitoring functionality for the DLQ monitoring system.
It provides the main DLQMonitor class along with supporting data structures and
notification capabilities.

Key Components:
- DLQMonitor: Main monitoring service that polls AWS SQS for DLQ messages
- Data classes for alerts and configuration
- Notification system integration (Mac notifications, audio alerts)
- PR monitoring and alerting
"""

# Lazy imports to avoid dependency issues
def __getattr__(name):
    """Lazy import implementation."""
    if name in ["DLQAlert", "MonitorConfig", "MacNotifier", "PRAlert", 
                "AudioNotifier", "PRMonitor", "DLQMonitor"]:
        from .monitor import (
            DLQAlert, MonitorConfig, MacNotifier, PRAlert,
            AudioNotifier, PRMonitor, DLQMonitor
        )
        return locals()[name]
    else:
        raise AttributeError(f"module '{__name__}' has no attribute '{name}'")

__all__ = [
    # Data structures
    "DLQAlert",
    "MonitorConfig",
    "PRAlert",
    
    # Notification classes
    "MacNotifier",
    "AudioNotifier",
    
    # Main monitoring classes
    "PRMonitor",
    "DLQMonitor",
]