---
allowed-tools: mcp__memory__create_entities, mcp__memory__create_relations, mcp__memory__add_observations, mcp__memory__read_graph, mcp__memory__search_nodes, Read, Bash(git diff:*), Bash(git log:*)
argument-hint: [component-or-feature]
description: Quick update to MCP memory graph with recent changes
model: claude-3-5-haiku-20241022
---

# Update Memory Command

## Recent Changes
!`git diff --name-only HEAD~1..HEAD 2>/dev/null || echo "No recent changes"`

## Latest Commit
!`git log -1 --pretty=format:"%h - %s (%cr)" 2>/dev/null || echo "No commits"`

## Task

Update the MCP memory knowledge graph with recent project changes:

1. **Analyze Changes**: Review recent modifications, especially: $ARGUMENTS

2. **Update Entities**: 
   - Add new components, features, or systems
   - Update existing entities with new capabilities

3. **Update Relations**:
   - Connect new components to existing systems
   - Update dependency relationships

4. **Add Observations**:
   - Record fixes, enhancements, and improvements
   - Note configuration changes or new integrations

Focus areas:
- MCP tool integrations (Context7, AWS Docs, CloudWatch, Lambda, Sequential Thinking)
- Google ADK agents and configuration
- AWS SQS monitoring enhancements
- Documentation updates
- Bug fixes and performance improvements

Keep updates concise and relevant to maintaining project knowledge.