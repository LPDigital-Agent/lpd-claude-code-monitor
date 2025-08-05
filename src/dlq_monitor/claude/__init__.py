"""
Claude AI Integration Module

This module provides Claude AI integration capabilities for the DLQ monitoring system.
It handles automated investigations, session management, status checking, and live monitoring
of Claude processes.

Key Features:
- Automated Claude Code CLI investigation triggers
- Session tracking and management
- Live monitoring of Claude processes
- Status checking and health monitoring
- Manual investigation capabilities
"""

# Lazy imports to avoid dependency issues
def __getattr__(name):
    """Lazy import implementation."""
    if name == "LiveClaudeMonitor":
        from .live_monitor import LiveClaudeMonitor
        return LiveClaudeMonitor
    elif name == "simple_status":
        from .live_monitor import simple_status
        return simple_status
    elif name == "ClaudeSessionMonitor":
        from .session_manager import ClaudeSessionMonitor
        return ClaudeSessionMonitor
    elif name == "check_claude_processes":
        from .status_checker import check_claude_processes
        return check_claude_processes
    elif name == "check_recent_logs":
        from .status_checker import check_recent_logs
        return check_recent_logs
    elif name == "check_dlq_status":
        from .status_checker import check_dlq_status
        return check_dlq_status
    elif name == "test_claude_command":
        from .status_checker import test_claude_command
        return test_claude_command
    elif name == "trigger_investigation":
        from .manual_investigation import trigger_investigation
        return trigger_investigation
    else:
        raise AttributeError(f"module '{__name__}' has no attribute '{name}'")

__all__ = [
    # Live monitoring
    "LiveClaudeMonitor",
    "simple_status",
    
    # Session management
    "ClaudeSessionMonitor",
    
    # Status checking functions
    "check_claude_processes",
    "check_recent_logs", 
    "check_dlq_status",
    "test_claude_command",
    
    # Manual controls
    "trigger_investigation",
]