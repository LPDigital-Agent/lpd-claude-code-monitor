# Context Window Prime - ADK Agent

## Purpose
This command ADK google agent developer kit context window with essential documentation about how create AI Agents with enhanced MCP tool integration.

## THINKING TOOLS
Activate advanced reasoning capabilities:
- ultrathink
- mcp sequential thinking
- mcp memory
- Context7 for documentation search
- AWS Documentation for service docs

## READ FILES
Load critical project files in priority order:

### 1. DOCUMENTATION REFERENCES
Best practices and guidelines:
```
https://github.com/google/adk-docs
https://github.com/google/adk-python
https://google.github.io/adk-docs/
https://cloud.google.com/vertex-ai/generative-ai/docs/agent-builder/
https://developers.googleblog.com/en/agent-development-kit-easy-to-build-multi-agent-applications/
```

### 2. MCP SERVER REFERENCES
Enhanced MCP Tools for Investigation:
```
Context7: https://github.com/upstash/context7
AWS Documentation: https://github.com/awslabs/aws-documentation-mcp-server
CloudWatch Logs: https://github.com/awslabs/cloudwatch-logs-mcp-server
Lambda Tools: https://github.com/awslabs/lambda-tools-mcp-server
Sequential Thinking: https://github.com/modelcontextprotocol/server-sequential-thinking
```

### 3. INVESTIGATION AGENT ENHANCEMENTS
The Investigation Agent (adk_agents/investigator.py) now includes:
- **Context7 Tool**: Search documentation and code examples for error patterns
- **AWS Docs Tool**: Look up AWS error codes and solutions
- **CloudWatch Tool**: Advanced log analysis with filtering and insights
- **Lambda Tool**: Analyze Lambda function configurations and issues
- **Sequential Analysis**: Systematic root cause analysis

Tool Functions Created:
1. `create_context7_tool()` - Library documentation search
2. `create_aws_docs_tool()` - AWS service documentation lookup
3. `create_enhanced_cloudwatch_tool()` - Advanced CloudWatch log analysis
4. `create_lambda_analysis_tool()` - Lambda function issue detection
5. `create_sequential_analysis_tool()` - Step-by-step root cause analysis

### 4. CONFIGURATION
MCP servers configured in config/mcp_settings.json:
- AWS Profile: FABIO-PROD
- Region: sa-east-1
- All tools have proper authentication
- Environment variables properly set

### 5. INVESTIGATION WORKFLOW
Enhanced workflow with MCP tools:
1. Start with sequential_analysis to structure the investigation
2. Parse DLQ messages for error patterns
3. Use Context7 to find relevant documentation
4. Search AWS documentation for error codes
5. Analyze CloudWatch logs for patterns
6. If Lambda-related, analyze function configuration
7. Synthesize findings into actionable report

### 6. TESTING
Test scripts available:
- `tests/test_investigator_mcp.py` - Verify MCP tool integration
- `tests/test_voice_id.py` - Test ElevenLabs voice configuration
- `python3 tests/test_investigator_mcp.py` - Run MCP integration tests