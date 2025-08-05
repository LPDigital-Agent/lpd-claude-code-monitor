# Development Documentation

This directory contains technical documentation for developers contributing to the AWS DLQ Claude Monitor system.

## 🏗️ Development Resources

### 🚀 Getting Started
- **[Development Setup](./setup.md)** - Development environment setup and configuration
- **[Local Development](./local-development.md)** - Running and debugging locally
- **[IDE Configuration](./ide-configuration.md)** - VSCode, PyCharm, and other IDE setup

### 🏛️ Architecture & Design
- **[Architecture Overview](./architecture.md)** - System architecture, components, and data flow
- **[Enhanced Auto-Investigation](./enhanced-auto-investigation.md)** - Multi-agent auto-investigation system
- **[Design Patterns](./design-patterns.md)** - Code patterns and architectural decisions
- **[Database Schema](./database-schema.md)** - Data models and storage design

### 🧪 Testing & Quality
- **[Testing Guide](./testing.md)** - Testing strategies, frameworks, and best practices
- **[Code Quality](./code-quality.md)** - Linting, formatting, and code standards
- **[Performance Testing](./performance-testing.md)** - Load testing and performance optimization
- **[Security Testing](./security-testing.md)** - Security testing and vulnerability assessment

### 🚀 Deployment & Operations
- **[Deployment Guide](./deployment.md)** - Production deployment procedures
- **[Monitoring & Observability](./monitoring.md)** - Application monitoring and logging
- **[Troubleshooting](./troubleshooting-dev.md)** - Developer-specific troubleshooting
- **[Performance Optimization](./performance.md)** - System optimization techniques

### 🤝 Contributing
- **[Contributing Guidelines](./contributing.md)** - How to contribute to the project
- **[Code Style Guide](./code-style.md)** - Coding standards and conventions
- **[Pull Request Process](./pr-process.md)** - PR templates and review process
- **[Release Process](./release-process.md)** - Version management and release procedures

## 📋 Quick Reference

### Development Commands
```bash
# Setup development environment
make dev-setup

# Run tests
make test
make test-integration
make test-coverage

# Code quality checks
make lint
make format
make type-check

# Build and package
make build
make package

# Local development
make dev-run
make dev-debug
```

### Project Structure
```
src/dlq_monitor/
├── core/                 # Core monitoring logic
├── claude/              # Claude AI integration
├── dashboards/          # UI dashboards
├── notifiers/           # Notification systems
├── utils/               # Utilities and helpers
└── py.typed            # Type information

tests/
├── unit/               # Unit tests
├── integration/        # Integration tests
├── fixtures/           # Test data
└── mocks/              # Mock objects

docs/
├── api/                # API documentation
├── guides/             # User guides
└── development/        # This directory

scripts/                # Utility scripts
config/                 # Configuration files
```

## 🛠️ Development Environment

### Prerequisites
- Python 3.8+
- Node.js 16+ (for documentation tools)
- Docker (for containerized testing)
- AWS CLI configured
- GitHub CLI (optional but recommended)

### Virtual Environment Setup
```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install development dependencies
pip install -r requirements-dev.txt
pip install -r requirements-test.txt

# Install pre-commit hooks
pre-commit install
```

### Environment Variables
```bash
# Copy development environment template
cp .env.dev.template .env.dev

# Required for development
export PYTHONPATH="${PWD}/src:${PYTHONPATH}"
export DLQ_MONITOR_ENV=development
export AWS_PROFILE=FABIO-PROD
export GITHUB_TOKEN=your_token_here
```

## 🏗️ Architecture Principles

### Modularity
- **Separation of Concerns**: Each module has a single responsibility
- **Loose Coupling**: Modules communicate through well-defined interfaces
- **High Cohesion**: Related functionality grouped together

### Scalability
- **Async Processing**: Non-blocking operations where possible
- **Resource Management**: Efficient memory and CPU usage
- **Horizontal Scaling**: Support for multi-instance deployment

### Reliability
- **Error Handling**: Comprehensive error handling and recovery
- **Monitoring**: Built-in metrics and health checks
- **Testing**: High test coverage with unit and integration tests

### Maintainability
- **Clean Code**: Readable, self-documenting code
- **Documentation**: Comprehensive inline and external documentation
- **Refactoring**: Regular code improvements and technical debt reduction

## 🧪 Testing Strategy

### Test Pyramid
1. **Unit Tests** (70%): Fast, isolated tests for individual components
2. **Integration Tests** (20%): Tests for component interactions
3. **End-to-End Tests** (10%): Full system workflow tests

### Test Categories
- **Core Logic**: Monitor, Claude integration, notifications
- **AWS Integration**: SQS, CloudWatch, IAM interactions
- **GitHub Integration**: PR creation, API interactions
- **UI/Dashboard**: Curses-based interface testing
- **Performance**: Load and stress testing

### Mocking Strategy
```python
# Example test with mocking
import pytest
from unittest.mock import Mock, patch
from dlq_monitor.core import MonitorService

@patch('dlq_monitor.core.boto3')
def test_monitor_service_initialization(mock_boto3):
    mock_boto3.Session.return_value = Mock()
    
    service = MonitorService(
        aws_profile='test-profile',
        region='us-east-1'
    )
    
    assert service.aws_profile == 'test-profile'
    assert service.region == 'us-east-1'
```

## 📊 Code Metrics

### Quality Gates
- **Test Coverage**: > 80%
- **Complexity**: Cyclomatic complexity < 10
- **Duplication**: < 3% duplicate code
- **Security**: No high/critical vulnerabilities

### Performance Targets
- **DLQ Check**: < 5 seconds per check
- **Investigation Trigger**: < 2 seconds
- **Dashboard Refresh**: < 1 second
- **Memory Usage**: < 500MB baseline

## 🔧 Development Tools

### Code Quality
- **Black**: Code formatting
- **isort**: Import sorting
- **flake8**: Linting
- **mypy**: Type checking
- **bandit**: Security linting

### Testing
- **pytest**: Test framework
- **pytest-cov**: Coverage reporting
- **pytest-mock**: Mocking utilities
- **pytest-asyncio**: Async test support

### Documentation
- **Sphinx**: API documentation generation
- **mkdocs**: User documentation
- **pre-commit**: Git hooks for quality checks

## 🐛 Debugging

### Local Debugging
```bash
# Debug mode with verbose logging
export DLQ_MONITOR_DEBUG=true
export LOG_LEVEL=DEBUG

# Run with debugger
python -m pdb src/dlq_monitor/cli.py monitor

# Run specific component
python -m dlq_monitor.core.monitor --debug
```

### Remote Debugging
```bash
# Enable remote debugging
export REMOTE_DEBUG=true
export DEBUG_PORT=5678

# Connect with IDE debugger
# VSCode: Python debugger on localhost:5678
```

### Log Analysis
```bash
# Tail application logs
tail -f dlq_monitor_FABIO-PROD_sa-east-1.log

# Filter for specific events
grep "investigation" dlq_monitor_*.log | tail -20

# JSON log parsing
cat dlq_monitor_*.log | jq '.level == "ERROR"'
```

## 🚀 Release Process

### Versioning
- **Semantic Versioning**: MAJOR.MINOR.PATCH
- **Pre-release**: alpha, beta, rc suffixes
- **Development**: .dev suffix for development builds

### Release Checklist
1. [ ] Update version numbers
2. [ ] Update CHANGELOG.md
3. [ ] Run full test suite
4. [ ] Update documentation
5. [ ] Create release PR
6. [ ] Tag release
7. [ ] Deploy to production
8. [ ] Monitor post-deployment

## 📞 Getting Help

### Internal Resources
- Architecture diagrams in `/docs/diagrams/`
- Design documents in `/docs/design/`
- Meeting notes in `/docs/meetings/`

### External Resources
- **Claude API**: https://docs.anthropic.com/
- **AWS SQS**: https://docs.aws.amazon.com/sqs/
- **GitHub API**: https://docs.github.com/en/rest
- **ElevenLabs**: https://docs.elevenlabs.io/

### Community
- **Discussions**: GitHub Discussions
- **Issues**: GitHub Issues
- **Chat**: Internal Slack/Discord (if applicable)

---

**Last Updated**: 2025-08-05
**Development Version**: 2.0.0-dev