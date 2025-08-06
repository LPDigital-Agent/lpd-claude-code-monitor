---
allowed-tools: mcp__memory__create_entities, mcp__memory__create_relations, mcp__memory__add_observations, mcp__awslabs-code-doc-gen__prepare_repository, mcp__awslabs-code-doc-gen__create_context, mcp__awslabs-code-doc-gen__plan_documentation, mcp__awslabs-code-doc-gen__generate_documentation, Edit, Write, Read, Bash(git status:*), Bash(git diff:*), Bash(git log:*)
argument-hint: [focus-area]
description: Sync project state - Update MCP memory, CLAUDE.md, and generate documentation
model: claude-3-5-sonnet-20241022
---

# Project Sync Command

## Current Git Status
!`git status --short`

## Recent Changes
!`git diff --stat HEAD~1..HEAD 2>/dev/null || echo "No recent commits"`

## Recent Commits
!`git log --oneline -5 2>/dev/null || echo "No commit history"`

## Your Task

Perform a comprehensive project sync with the following steps:

### 1. Update MCP Memory (Knowledge Graph)

Analyze the current project state and recent changes to:
- Create or update entities for new components, features, and systems
- Add relations between components (uses, depends on, implements, etc.)
- Add observations about recent enhancements and fixes
- Focus on: $ARGUMENTS

Key areas to track in memory:
- Investigation Agent with 5 MCP tools (Context7, AWS Docs, CloudWatch, Lambda, Sequential)
- Google ADK multi-agent framework
- AWS SQS DLQ monitoring system
- GitHub PR automation
- Voice notifications (ElevenLabs ID: 19STyYD15bswVz51nqLf)
- Recent fixes and enhancements

### 2. Update CLAUDE.md

Review and update the CLAUDE.md file to ensure it reflects:
- Current project architecture
- Latest MCP tool integrations
- Known issues (Blake2 warnings, package names)
- Development workflow updates
- Critical configuration files
- Testing procedures

Include any specific focus area: $ARGUMENTS

### 3. Generate Documentation (if needed)

If significant changes warrant documentation updates:
1. Use `prepare_repository` to analyze the codebase
2. Create a DocumentationContext with `create_context`
3. Plan documentation with `plan_documentation`
4. Generate comprehensive documentation with `generate_documentation`

Focus especially on:
- New MCP tool integrations
- ADK agent enhancements
- Configuration changes
- API documentation

### Output Format

Provide a summary of:
1. **Memory Updates**: Number of entities, relations, and observations added
2. **CLAUDE.md Changes**: Key sections updated
3. **Documentation Generated**: Files created or updated
4. **Next Steps**: Any recommended actions

Remember to be thorough but concise. This command helps maintain project coherence and documentation quality.