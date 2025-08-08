# Project Documentation

This directory contains all project-level documentation and specifications.

## Contents

- **CHANGELOG.md** - Version history and release notes
- **CLAUDE.md** - Claude AI guidance and instructions
- **PROJECT_STRUCTURE.md** - Complete project organization guide
- **.docs-manifest.md** - Documentation manifest and index

## Project Organization

The project follows Python and AI agent development best practices:

```
lpd-claude-code-monitor/
├── adk_agents/          # ADK Multi-Agent System
├── src/dlq_monitor/     # Core monitoring package
├── config/              # All configuration files
│   ├── python/          # Python/build configs
│   ├── testing/         # Test configurations
│   └── *.yaml/json      # Runtime configs
├── docs/                # Documentation
│   ├── project/         # Project-level docs
│   ├── api/             # API documentation
│   └── guides/          # User guides
├── requirements/        # Dependency specifications
├── scripts/             # Executable scripts
├── tests/               # Test suites
└── .claude/             # Claude AI configurations
```

## Key Documents

### CHANGELOG.md
Track all changes, features, and fixes for each version.

### CLAUDE.md
Guidance for Claude AI when working with this codebase, including:
- Build commands
- Testing procedures
- Architecture patterns
- Critical files

### PROJECT_STRUCTURE.md
Complete guide to the project organization following best practices for:
- Python package structure (src-layout)
- AI agent organization
- Configuration management
- Documentation structure

## Development Workflow

1. All configuration files are in `config/` subdirectories
2. Requirements are organized in `requirements/` directory
3. Documentation is categorized in `docs/` subdirectories
4. No loose files in the root directory
5. Symbolic links maintain backward compatibility