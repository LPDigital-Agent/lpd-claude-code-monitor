# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### In Development
- Historical metrics graphs for NeuroCenter
- Investigation replay functionality
- Team collaboration features
- Export investigation reports

## [3.1.0] - 2025-08-06

### Added
- **BHiveQ NeuroCenter**: Professional operational intelligence dashboard
  - Real-time agent monitoring with performance metrics
  - Investigation timeline with GitHub Actions-style UI
  - Live metrics dashboard with auto-refresh
  - Agent-DLQ assignment matrix for routing control
  - Drag-and-drop module rearrangement
  - Dark Ops Center theme with orange accents (#FA4616)
  - Browser notifications and audio alerts
  - Settings modal with persistent preferences
- **Database Persistence**: SQLAlchemy models for investigations and metrics
- **Integrated Launcher System**: Comprehensive service management
  - Master launcher with interactive menu
  - Process management with PID tracking
  - Port conflict detection
  - Centralized logging
- **ADK Production Monitor**: Implements documented multi-agent flow
  - Follows sequence diagram exactly
  - 30-second monitoring cycles
  - 30-minute cooldown periods
  - PR reminders every 10 minutes

### Changed
- Reorganized scripts directory structure
  - `scripts/launch/` for service launchers
  - `scripts/web/` for web-related scripts
  - `scripts/monitoring/` for monitoring scripts
- Fixed NeuroCenter service imports after reorganization
- Compact Agent-DLQ Assignment UI for better space usage
- Filter DLQs to show only FABIO-PROD/sa-east-1

### Fixed
- Sound, notifications, and settings button functionality
- Live metrics now show real calculated data
- Import paths corrected for NeuroCenter services
- Blake2 hash warnings handled gracefully

## [3.0.0] - 2025-08-05

### Added
- **BHiveQ Branding**: Complete transformation to BHiveQ Observability Hub
  - LPD Hive orange theme (#FA4616)
  - Professional hexagonal logo
  - Enhanced visual design
  - Brand consistency across dashboards
- **Web Dashboard Enhancements**
  - Real-time WebSocket updates
  - Chart.js visualizations
  - Bootstrap 5 modern UI
  - Responsive design
- **Voice Control Features**
  - Mute/unmute voice notifications
  - Audio feedback for actions
  - ElevenLabs TTS improvements

### Changed
- Rebranded from DLQ Monitor to BHiveQ Observability Hub
- Updated all UI components with new branding
- Enhanced color scheme and visual hierarchy
- Improved dashboard layout and information density

## [2.0.0] - 2025-08-04

### Added
- **ADK Multi-Agent System**: Google ADK integration with 6 specialized agents
  - Coordinator Agent for orchestration
  - DLQ Monitor Agent for AWS SQS monitoring
  - Investigation Agent for root cause analysis
  - Code Fixer Agent for fix implementation
  - PR Manager Agent for GitHub integration
  - Notifier Agent for multi-channel alerts
- **MCP Server Integration**: 5 special MCP tools
  - Context7 for library documentation
  - AWS Documentation for service docs
  - CloudWatch Logs for advanced analysis
  - Lambda Tools for function debugging
  - Sequential Thinking for systematic analysis
- **Claude Subagents**: Enhanced investigation capabilities
  - dlq-analyzer for message analysis
  - debugger for fix implementation
  - code-reviewer for quality assurance
- **Enhanced Investigation Flow**
  - Parallel subagent deployment
  - Systematic root cause analysis
  - Automated fix validation
  - Comprehensive PR descriptions

### Changed
- Complete architecture overhaul to multi-agent system
- Enhanced investigation capabilities with MCP tools
- Improved error pattern recognition
- Better fix quality with code review

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