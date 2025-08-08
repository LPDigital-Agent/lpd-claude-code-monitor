# Release Notes: MCP Tool Enhancements

## Version: 2.0.0
## Date: January 2025

## Summary
Major enhancement of the Investigation Agent with 5 special MCP tools for comprehensive DLQ root cause analysis. The system now provides advanced documentation search, AWS service lookups, deep log analysis, Lambda debugging, and systematic investigation capabilities.

## New Features

### 🚀 Enhanced Investigation Agent
- **5 New MCP Tools Integrated**:
  1. **Context7**: Library documentation and code examples search
  2. **AWS Documentation**: AWS service docs and error code lookup
  3. **CloudWatch Logs**: Advanced log analysis with filtering and insights
  4. **Lambda Tools**: Lambda function configuration and issue analysis
  5. **Sequential Thinking**: Systematic step-by-step root cause analysis

### 🔊 Voice Configuration
- **ElevenLabs Voice ID**: `19STyYD15bswVz51nqLf`
- Configured for all audio notifications
- Integrated with PR announcements and DLQ alerts

### 📚 AWS Best Practices
- Implemented retry logic with exponential backoff
- Added pagination for large queue listings
- Comprehensive error handling for AWS API calls
- Batch operations for efficient message processing

## Files Modified

### Core Files
- `adk_agents/investigator.py` - Complete rewrite with 5 new tool functions
- `config/mcp_settings.json` - Added 4 new MCP server configurations
- `src/dlq_monitor/utils/aws_sqs_helper.py` - AWS SQS best practices implementation
- `src/dlq_monitor/notifiers/macos_notifier.py` - macOS notifications with TTS

### Documentation
- `.claude/commands/adk.md` - Updated with MCP tool references
- `.claude/commands/claude_subagent.md` - Enhanced with investigation subagent
- `.claude/commands/prime.md` - Added investigation capabilities
- `docs/investigation-enhancements.md` - Comprehensive enhancement documentation
- `docs/RELEASE_NOTES_MCP_ENHANCEMENTS.md` - This file

### Tests
- `tests/test_investigator_mcp.py` - MCP integration tests
- `tests/test_voice_id.py` - Voice configuration verification

## Configuration Details

### MCP Servers
```json
{
  "context7": {
    "command": "npx",
    "args": ["-y", "@upstash/context7-mcp-server"]
  },
  "aws-documentation": {
    "command": "python",
    "args": ["-m", "awslabs.aws_documentation_mcp_server.server"],
    "env": {"AWS_REGION": "sa-east-1"}
  },
  "cloudwatch-logs": {
    "command": "python",
    "args": ["-m", "awslabs.cloudwatch_mcp_server.server"],
    "env": {"AWS_PROFILE": "FABIO-PROD", "AWS_REGION": "sa-east-1"}
  },
  "lambda-tools": {
    "command": "python",
    "args": ["-m", "awslabs.lambda_tool_mcp_server.server"],
    "env": {"AWS_PROFILE": "FABIO-PROD", "AWS_REGION": "sa-east-1"}
  }
}
```

### Investigation Workflow
1. **Trigger**: DLQ message threshold exceeded
2. **Sequential Analysis**: Structure investigation approach
3. **Error Parsing**: Extract patterns from DLQ messages
4. **Documentation Search**: Use Context7 for relevant docs
5. **AWS Lookup**: Search AWS documentation for error codes
6. **Log Analysis**: Deep CloudWatch log investigation
7. **Lambda Check**: Analyze function configurations
8. **Report Generation**: Comprehensive findings with fixes

## Output Format
The enhanced agent provides structured JSON output with:
- Root cause analysis with confidence levels
- Evidence from multiple sources
- Prioritized recommended fixes
- Documentation references
- Prevention measures

## Testing

### Test Commands
```bash
# Test MCP configuration
python3 tests/test_investigator_mcp.py

# Verify voice configuration
python3 tests/test_voice_id.py

# Run full test suite
make test
```

### Test Results
- ✅ MCP Configuration: All 10 servers configured
- ✅ Voice ID: Correctly set to `19STyYD15bswVz51nqLf`
- ✅ Investigation Workflow: All components integrated
- ✅ Tool Functions: All 5 tools created successfully

## Breaking Changes
None - All enhancements are backward compatible

## Migration Guide
No migration required. The system will automatically use the enhanced investigation capabilities when DLQ thresholds are triggered.

## Known Issues
- Blake2 hash warnings in Python 3.11 (cosmetic, doesn't affect functionality)
- Google ADK import requires FunctionTool alias

## Contributors
- Enhanced by Claude Code with special MCP tool integration
- Voice configuration by user specification

## References
- Context7: https://github.com/upstash/context7
- AWS Documentation MCP: https://github.com/awslabs/aws-documentation-mcp-server
- CloudWatch Logs MCP: https://github.com/awslabs/cloudwatch-logs-mcp-server
- Lambda Tools MCP: https://github.com/awslabs/lambda-tools-mcp-server
- Sequential Thinking: https://github.com/modelcontextprotocol/server-sequential-thinking

## Support
For issues or questions, please check:
- `docs/investigation-enhancements.md` for detailed documentation
- `.claude/commands/` for command references
- `tests/` directory for usage examples

---
*This release significantly enhances the DLQ monitoring system's investigation capabilities, providing comprehensive tools for root cause analysis and automated problem resolution.*