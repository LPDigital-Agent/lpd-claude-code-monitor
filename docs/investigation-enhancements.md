# Investigation Agent Enhancements

## Overview
The Investigation Agent has been significantly enhanced with special MCP (Model Context Protocol) tools to provide comprehensive root cause analysis for DLQ messages. These enhancements enable the agent to search documentation, analyze logs, inspect Lambda functions, and conduct systematic investigations.

## Enhanced MCP Tools

### 1. Context7 MCP
**Purpose**: Search library documentation and code examples  
**GitHub**: https://github.com/upstash/context7  
**Functions**:
- `resolve-library-id`: Resolve library names to Context7-compatible IDs
- `get-library-docs`: Fetch documentation for specific libraries/frameworks

**Use Cases**:
- Finding solutions for specific error types
- Looking up best practices for libraries
- Getting code examples for error handling

### 2. AWS Documentation MCP
**Purpose**: Access AWS service documentation and error codes  
**GitHub**: https://github.com/awslabs/aws-documentation-mcp-server  
**Functions**:
- `search_documentation`: Search AWS docs for error codes and solutions
- `read_documentation`: Read specific AWS documentation pages
- `recommend`: Get related documentation recommendations

**Use Cases**:
- Looking up AWS error codes
- Finding service-specific troubleshooting guides
- Identifying AWS best practices violations

### 3. CloudWatch Logs MCP
**Purpose**: Advanced log analysis with filtering and insights  
**GitHub**: https://github.com/awslabs/cloudwatch-logs-mcp-server  
**Functions**:
- `filter_log_events`: Filter logs with advanced patterns
- `start_query`: Run CloudWatch Insights queries
- Pattern analysis and error frequency tracking

**Use Cases**:
- Correlating errors with system events
- Identifying error patterns over time
- Generating insights from log data

### 4. Lambda Tools MCP
**Purpose**: Analyze Lambda function configurations and issues  
**GitHub**: https://github.com/awslabs/lambda-tools-mcp-server  
**Functions**:
- `get_function_configuration`: Retrieve Lambda configuration
- `list_function_errors`: Get recent invocation errors
- `get_function_metrics`: Analyze performance metrics

**Use Cases**:
- Detecting timeout issues
- Identifying memory constraints
- Checking DLQ configurations
- Analyzing environment variables

### 5. Sequential Thinking MCP
**Purpose**: Systematic step-by-step root cause analysis  
**GitHub**: https://github.com/modelcontextprotocol/server-sequential-thinking  
**Functions**:
- `sequentialthinking`: Multi-step analytical reasoning
- Hypothesis generation and validation
- Structured problem-solving approach

**Use Cases**:
- Breaking down complex issues
- Systematic root cause analysis
- Building evidence-based conclusions

## Implementation Details

### File Locations
- **Agent Definition**: `adk_agents/investigator.py`
- **MCP Configuration**: `config/mcp_settings.json`
- **Test Suite**: `tests/test_investigator_mcp.py`

### Tool Functions Created
1. `create_context7_tool()` - Documentation and code search
2. `create_aws_docs_tool()` - AWS documentation lookup
3. `create_enhanced_cloudwatch_tool()` - Advanced log analysis
4. `create_lambda_analysis_tool()` - Lambda function debugging
5. `create_sequential_analysis_tool()` - Systematic analysis

### Configuration
All MCP servers are configured with:
- **AWS Profile**: FABIO-PROD
- **AWS Region**: sa-east-1
- **Authentication**: Environment variables and AWS credentials

## Investigation Workflow

### Enhanced Process Flow
```
1. Trigger: DLQ message threshold exceeded
2. Sequential Analysis: Structure the investigation
3. Error Parsing: Extract patterns from DLQ messages
4. Documentation Search: Use Context7 for relevant docs
5. AWS Lookup: Search AWS documentation for error codes
6. Log Analysis: Deep CloudWatch log investigation
7. Lambda Check: Analyze function configurations (if applicable)
8. Report Generation: Comprehensive findings with fixes
```

### Output Format
The enhanced agent provides structured output:
```json
{
    "queue_name": "string",
    "message_count": number,
    "root_cause": {
        "primary": "string",
        "secondary": ["string"],
        "confidence": "high|medium|low"
    },
    "evidence": {
        "error_patterns": {},
        "log_analysis": {},
        "documentation_references": [],
        "lambda_issues": []
    },
    "recommended_fixes": [
        {
            "action": "string",
            "priority": "high|medium|low",
            "documentation": "url"
        }
    ],
    "prevention_measures": ["string"]
}
```

## Testing

### Running Tests
```bash
# Test MCP configuration
python3 tests/test_investigator_mcp.py

# Verify voice configuration
python3 tests/test_voice_id.py

# Run full test suite
make test
```

### Test Coverage
- MCP server configuration validation
- Tool function creation verification
- Investigation workflow validation
- Voice ID configuration check

## Voice Configuration

### ElevenLabs TTS
- **Voice ID**: `19STyYD15bswVz51nqLf`
- **Files**: 
  - `src/dlq_monitor/notifiers/pr_audio.py`
  - `src/dlq_monitor/notifiers/macos_notifier.py`
- **Usage**: All audio notifications use this custom voice

## AWS SQS Best Practices

### Implementation
The system now follows AWS SQS best practices:
- **Retry Logic**: Exponential backoff with jitter
- **Pagination**: Handle large queue listings
- **Error Handling**: Comprehensive AWS API error management
- **Batch Operations**: Efficient message processing
- **Resource Management**: Proper connection cleanup

### Helper Module
`src/dlq_monitor/utils/aws_sqs_helper.py` implements:
- `list_dlq_queues()`: List DLQs with pagination
- `get_queue_messages()`: Batch message retrieval
- `get_queue_attributes_batch()`: Batch attribute fetching
- Retry decorators with exponential backoff

## Benefits

### Improved Investigation Quality
- Comprehensive documentation search
- AWS-specific error resolution
- Deep log pattern analysis
- Lambda configuration insights
- Systematic root cause identification

### Faster Resolution
- Parallel tool execution
- Cached documentation lookups
- Batch AWS operations
- Structured investigation workflow

### Better Reporting
- Evidence-based findings
- Documentation references
- Prioritized recommendations
- Prevention measures

## Future Enhancements

### Potential Additions
- X-Ray trace analysis MCP
- RDS/DynamoDB investigation tools
- Cost optimization recommendations
- Performance profiling tools
- Security vulnerability scanning

### Workflow Improvements
- Machine learning for pattern recognition
- Historical trend analysis
- Automated fix implementation
- Cross-account investigation support

## Troubleshooting

### Common Issues
1. **MCP Server Not Found**: Check `config/mcp_settings.json`
2. **Authentication Errors**: Verify AWS credentials
3. **Tool Import Errors**: Ensure ADK is installed
4. **Voice Not Working**: Check ElevenLabs API key

### Debug Commands
```bash
# Check MCP configuration
cat config/mcp_settings.json | jq .

# Test investigation agent
python3 -c "from adk_agents.investigator import create_investigator_agent; agent = create_investigator_agent(); print(f'Agent created: {agent.name}')"

# Verify voice ID
grep -r "19STyYD15bswVz51nqLf" src/

# Check AWS credentials
aws sts get-caller-identity --profile FABIO-PROD
```

## Conclusion
The enhanced Investigation Agent with special MCP tools provides a comprehensive solution for DLQ root cause analysis. By integrating documentation search, AWS service lookups, advanced log analysis, Lambda debugging, and systematic thinking, the agent can effectively identify and resolve complex issues in distributed systems.