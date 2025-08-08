"""
Utils Module

This module provides utility functions and classes that support the main DLQ monitoring
functionality. It includes GitHub integration, production monitoring utilities, and
various helper functions.

Key Components:
- GitHub integration and authentication setup
- Production monitoring with limited cycles
- Environment and configuration management
- Helper functions for AWS and external service integration

Utilities:
- GitHub API authentication and testing
- Production environment setup and execution
- Limited monitoring for testing purposes
- Configuration and environment helpers
"""

# Lazy imports to avoid dependency issues
def __getattr__(name):
    """Lazy import implementation."""
    if name == "setup_github_env":
        from .github_integration import setup_github_env
        return setup_github_env
    elif name == "test_github_access":
        from .github_integration import test_github_access
        return test_github_access
    elif name == "ProductionMonitor":
        from .production_monitor import ProductionMonitor
        return ProductionMonitor
    elif name == "LimitedMonitor":
        from .limited_monitor import LimitedMonitor
        return LimitedMonitor
    elif name == "activate_venv_and_run":
        from .production_runner import activate_venv_and_run
        return activate_venv_and_run
    else:
        raise AttributeError(f"module '{__name__}' has no attribute '{name}'")

__all__ = [
    # GitHub utilities
    "setup_github_env",
    "test_github_access",
    
    # Production monitoring
    "ProductionMonitor", 
    "LimitedMonitor",
    
    # Runtime utilities
    "activate_venv_and_run",
]