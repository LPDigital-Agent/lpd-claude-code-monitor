# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Complete package configuration setup with pyproject.toml
- Comprehensive testing framework with pytest and moto
- Development tooling with black, ruff, mypy, isort
- Package building and publishing configuration

### Changed
- Enhanced project structure with src/ layout
- Improved documentation organization

### Fixed
- Package metadata and dependency management

## [1.0.0] - 2025-01-XX

### Added
- AWS SQS Dead Letter Queue monitoring system
- Claude AI auto-investigation capabilities
- GitHub PR creation with automated fixes
- Real-time curses-based dashboards
  - Enhanced live monitor with multi-panel layout
  - Ultimate monitor with comprehensive tracking
  - Demo and legacy monitor variants
- Audio notification system with ElevenLabs TTS integration
- macOS native notifications for DLQ alerts
- Multi-modal PR notification system
- Claude session management and tracking
- Production monitoring with cooldown periods

### Features
- **Core Monitoring**: Real-time DLQ message detection across AWS accounts
- **Auto-Investigation**: Automated Claude Code CLI integration for issue analysis
- **GitHub Integration**: Automatic PR creation with proposed fixes
- **Dashboard System**: Multiple terminal-based monitoring interfaces
- **Notification System**: Audio and visual alerts for DLQ events and PR status
- **Session Tracking**: Comprehensive logging of Claude investigation sessions
- **Configuration Management**: YAML-based configuration with environment variable support

### Components
- **dlq_monitor.core**: Core monitoring functionality
- **dlq_monitor.claude**: Claude AI integration and session management
- **dlq_monitor.dashboards**: Multiple monitoring dashboard variants
- **dlq_monitor.notifiers**: Audio and visual notification systems
- **dlq_monitor.utils**: GitHub integration and production utilities
- **dlq_monitor.cli**: Command-line interface for all operations

### Console Scripts
- `dlq-monitor`: Main CLI entry point
- `dlq-dashboard`: Enhanced monitoring dashboard
- `dlq-investigate`: Manual Claude investigation trigger
- `dlq-setup`: GitHub integration setup utility

### Dependencies
- **AWS Integration**: boto3 for SQS monitoring
- **AI Integration**: subprocess calls to claude CLI
- **UI Framework**: curses for terminal dashboards, rich for formatting
- **Notifications**: pygame for audio, macOS osascript for native alerts
- **Configuration**: PyYAML for config management
- **GitHub API**: requests for PR management

### Supported Platforms
- macOS (primary target with native notifications)
- Linux (limited notification support)
- AWS Regions: Configurable, default sa-east-1

[Unreleased]: https://github.com/fabiosantos/lpd-claude-code-monitor/compare/v1.0.0...HEAD
[1.0.0]: https://github.com/fabiosantos/lpd-claude-code-monitor/releases/tag/v1.0.0