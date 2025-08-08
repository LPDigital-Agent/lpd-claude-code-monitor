"""
Dashboards Module

This module provides various dashboard implementations for monitoring DLQs, Claude processes,
and GitHub PRs. All dashboards use the curses library for terminal-based UI with real-time
updates and interactive features.

Dashboard Types:
- Enhanced: Real-time multi-panel dashboard showing DLQs, agents, and PRs
- Ultimate: Most comprehensive monitoring dashboard with timeline views
- Demo: Demonstration mode with simulated data
- Fixed Enhanced: Corrected version of enhanced dashboard
- Corrections: Dashboard focused on Claude correction tracking

All dashboards feature:
- Multi-panel layouts with color-coded status indicators
- Real-time updates every 3 seconds
- Keyboard shortcuts for navigation
- Terminal-based curses UI interface
"""

# Lazy imports to avoid dependency issues
def __getattr__(name):
    """Lazy import implementation."""
    if name == "EnhancedLiveMonitor":
        from .enhanced import EnhancedLiveMonitor
        return EnhancedLiveMonitor
    elif name == "UltimateClaudeMonitor":
        from .ultimate import UltimateClaudeMonitor
        return UltimateClaudeMonitor
    elif name == "DemoDLQMonitor":
        from .demo import DemoDLQMonitor
        return DemoDLQMonitor
    elif name == "FixedEnhancedMonitor":
        from .fixed_enhanced import FixedEnhancedMonitor
        return FixedEnhancedMonitor
    elif name == "ClaudeCorrectionsMonitor":
        from .corrections import ClaudeCorrectionsMonitor
        return ClaudeCorrectionsMonitor
    else:
        raise AttributeError(f"module '{__name__}' has no attribute '{name}'")

__all__ = [
    # Main dashboard classes
    "EnhancedLiveMonitor",
    "UltimateClaudeMonitor",
    "DemoDLQMonitor",
    "FixedEnhancedMonitor",
    "ClaudeCorrectionsMonitor",
]