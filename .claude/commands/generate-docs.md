---
allowed-tools: mcp__awslabs-code-doc-gen__prepare_repository, mcp__awslabs-code-doc-gen__create_context, mcp__awslabs-code-doc-gen__plan_documentation, mcp__awslabs-code-doc-gen__generate_documentation, Read, Write, Glob, Bash(find:*)
argument-hint: [doc-type: readme|api|setup|architecture]
description: Generate comprehensive documentation using MCP doc gen
model: claude-3-5-sonnet-20241022
---

# Generate Documentation Command

## Project Structure
!`find . -type f -name "*.py" | head -20`

## Existing Documentation
!`find docs -name "*.md" -type f 2>/dev/null | head -10`

## Task

Generate comprehensive documentation for the project using the MCP documentation generator:

### Step 1: Prepare Repository
Use `prepare_repository` to analyze the codebase structure and get statistics.

### Step 2: Analyze and Create Context
Based on the repository structure:
1. Read key files (README.md, pyproject.toml, requirements.txt)
2. Identify project type, features, and dependencies
3. Create a ProjectAnalysis with:
   - project_type: "DLQ Monitoring System with AI Investigation"
   - features: [MCP tools, ADK agents, AWS integration, etc.]
   - primary_languages: ["Python"]
   - has_infrastructure_as_code: True (if CDK/Terraform detected)

### Step 3: Create Documentation Context
Use `create_context` with the completed ProjectAnalysis.

### Step 4: Plan Documentation
Use `plan_documentation` to determine what documentation is needed.
Focus on: $ARGUMENTS

### Step 5: Generate Documentation
Use `generate_documentation` to create the documentation structure.
Then write comprehensive content for each section including:
- Project overview and purpose
- Installation and setup
- Architecture and design
- API documentation
- Configuration guide
- Troubleshooting
- Examples and use cases

### Documentation Types
Based on argument provided ($ARGUMENTS):
- **readme**: Update main README with current features
- **api**: Generate API documentation for all modules
- **setup**: Create detailed setup and deployment guide
- **architecture**: Document system architecture and design

### Output
Generate well-structured markdown documentation with:
- Clear headings and sections
- Code examples
- Configuration samples
- Diagrams (if applicable)
- Cross-references to related docs