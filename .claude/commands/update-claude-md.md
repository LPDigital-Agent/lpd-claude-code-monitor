---
allowed-tools: Read, Edit, Write, Bash(git status:*), Bash(find:*), Bash(grep:*)
argument-hint: [section: overview|architecture|commands|issues]
description: Update CLAUDE.md with current project state and guidance
model: claude-3-5-haiku-20241022
---

# Update CLAUDE.md Command

## Current CLAUDE.md Status
@CLAUDE.md

## Project Changes to Document
!`git status --short | head -10`

## Find Recent Feature Files
!`find . -name "*.py" -newer CLAUDE.md -type f 2>/dev/null | head -10`

## Task

Update the CLAUDE.md file to reflect the current project state. Focus on: $ARGUMENTS

### Sections to Review and Update:

1. **Project Overview**
   - Ensure MCP tools are documented (Context7, AWS Docs, CloudWatch, Lambda, Sequential)
   - Update with Google ADK multi-agent framework details
   - Note the 5 special MCP tools for investigation

2. **Build and Development Commands**
   - Verify all setup commands are current
   - Include `google-adk` and `google-generativeai` installation
   - Add ADK validation test: `python tests/validation/test_adk_simple.py`

3. **High-Level Architecture**
   - Document enhanced Investigation Agent (`adk_agents/investigator.py`)
   - Update with MCP tool functions
   - Include ADK agent coordination

4. **Critical Files and Their Roles**
   - Add `config/mcp_settings.json` - MCP server configurations
   - Add `config/adk_config.yaml` - ADK configuration
   - Add `requirements_adk.txt` - ADK dependencies

5. **Known Issues**
   - Blake2 hash warnings (Python 3.11) - harmless
   - Package names: `google-adk` (correct) vs `google-genai-developer-toolkit` (wrong)
   - Mixed Python version issues

6. **AWS Integration Details**
   - Profile: FABIO-PROD
   - Region: sa-east-1
   - Required permissions for SQS

7. **GitHub Integration**
   - Token from `gh` CLI: `export GITHUB_TOKEN=$(gh auth token 2>/dev/null)`
   - PR creation automation
   - Audio notifications

8. **Claude AI Integration**
   - Command execution details
   - Session tracking in `.claude_sessions.json`
   - Investigation workflow

9. **Testing**
   - ADK validation: `python tests/validation/test_adk_simple.py`
   - Test commands for each component
   - `make test` for full suite

10. **Development Workflow**
    - How to add new MCP tools
    - ADK agent development
    - Dashboard customization

### Key Information to Preserve:
- Voice ID: `19STyYD15bswVz51nqLf` (ElevenLabs)
- AWS Profile: FABIO-PROD
- AWS Region: sa-east-1
- MCP servers configuration in `config/mcp_settings.json`

Update the file comprehensively while maintaining its role as the primary guidance document for Claude Code when working with this repository.