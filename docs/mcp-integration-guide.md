# MCP Server Integration Guide

## Overview

The Model Context Protocol (MCP) servers provide native integration with external services, eliminating the need for custom API implementations. This guide details the configuration, usage, and best practices for each MCP server used in the ADK Multi-Agent System.

## MCP Architecture

```mermaid
graph TB
    subgraph "ADK Agents"
        DLQ[DLQ Monitor]
        INV[Investigation]
        FIX[Code Fixer]
        PR[PR Manager]
    end
    
    subgraph "MCP Servers"
        AWS[aws-api]
        SNS[sns-sqs]
        GH[github]
        THINK[sequential-thinking]
        MEM[memory]
        FS[filesystem]
    end
    
    subgraph "External Services"
        SQS[(AWS SQS)]
        CW[(CloudWatch)]
        GITHUB[(GitHub)]
        GRAPH[(Knowledge Graph)]
        FILES[(Local Files)]
    end
    
    DLQ --> AWS --> SQS
    DLQ --> SNS --> SQS
    INV --> THINK
    INV --> AWS --> CW
    FIX --> MEM --> GRAPH
    PR --> GH --> GITHUB
    FIX --> FS --> FILES
    
    style AWS fill:#ff9966
    style SNS fill:#ff9966
    style GH fill:#66ccff
    style THINK fill:#99ff99
    style MEM fill:#ffcc99
```

## MCP Server Configuration

### Configuration File (`config/mcp_settings.json`)

```json
{
  "mcpServers": {
    "aws-api": {
      "command": "npx",
      "args": ["-y", "@mcp-servers/aws"],
      "env": {
        "AWS_PROFILE": "FABIO-PROD",
        "AWS_REGION": "sa-east-1",
        "AWS_ACCESS_KEY_ID": "${AWS_ACCESS_KEY_ID}",
        "AWS_SECRET_ACCESS_KEY": "${AWS_SECRET_ACCESS_KEY}"
      }
    },
    "sns-sqs": {
      "command": "node",
      "args": ["/Users/fabio.santos/mcp/aws/mcp/packages/sqs-mcp-server/dist/index.js"],
      "env": {
        "AWS_PROFILE": "FABIO-PROD",
        "AWS_REGION": "sa-east-1"
      }
    },
    "github": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-github"],
      "env": {
        "GITHUB_TOKEN": "${GITHUB_TOKEN}"
      }
    },
    "sequential-thinking": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-sequential-thinking"]
    },
    "memory": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-memory"]
    },
    "filesystem": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-filesystem"],
      "env": {
        "WORKSPACE_DIR": "/Users/fabio.santos/LPD Repos/lpd-claude-code-monitor"
      }
    }
  }
}
```

## 1. AWS API MCP Server

### Purpose
Provides native AWS service integration for comprehensive AWS operations.

### Capabilities
- **Services**: EC2, S3, Lambda, DynamoDB, CloudWatch, IAM, etc.
- **Operations**: Full CRUD operations on AWS resources
- **Authentication**: Uses AWS CLI profiles or environment variables

### Usage in Agents

```python
# DLQ Monitor Agent usage
async def list_sqs_queues():
    result = await mcp_client.call_tool(
        server="aws-api",
        tool="aws_sqs_list_queues",
        arguments={}
    )
    return result["QueueUrls"]

async def get_cloudwatch_logs(log_group, start_time):
    result = await mcp_client.call_tool(
        server="aws-api",
        tool="aws_logs_filter_log_events",
        arguments={
            "logGroupName": log_group,
            "startTime": start_time
        }
    )
    return result["events"]
```

### Available Tools

| Tool | Description | Usage |
|------|-------------|-------|
| `aws_sqs_list_queues` | List all SQS queues | DLQ discovery |
| `aws_sqs_get_queue_attributes` | Get queue statistics | Message counting |
| `aws_logs_filter_log_events` | Search CloudWatch logs | Error investigation |
| `aws_lambda_invoke` | Invoke Lambda functions | Trigger processing |

## 2. SNS-SQS MCP Server

### Purpose
Specialized server for Amazon SNS and SQS operations with enhanced DLQ support.

### Capabilities
- **SQS Operations**: Queue management, message handling, DLQ monitoring
- **SNS Operations**: Topic management, subscription handling
- **DLQ Features**: Automatic DLQ detection, message replay

### Usage in Agents

```python
# DLQ Monitor Agent usage
async def check_dlq_messages(queue_url):
    result = await mcp_client.call_tool(
        server="sns-sqs",
        tool="sqs_receive_messages",
        arguments={
            "QueueUrl": queue_url,
            "MaxNumberOfMessages": 10,
            "AttributeNames": ["All"],
            "MessageAttributeNames": ["All"]
        }
    )
    return result["Messages"]

async def get_dlq_count(queue_url):
    result = await mcp_client.call_tool(
        server="sns-sqs",
        tool="sqs_get_queue_attributes",
        arguments={
            "QueueUrl": queue_url,
            "AttributeNames": ["ApproximateNumberOfMessages"]
        }
    )
    return int(result["Attributes"]["ApproximateNumberOfMessages"])
```

### DLQ-Specific Features

```mermaid
graph LR
    subgraph "SNS-SQS MCP Features"
        DETECT[DLQ Detection]
        MONITOR[Message Monitoring]
        REPLAY[Message Replay]
        ANALYZE[Error Analysis]
    end
    
    DETECT --> |Pattern Matching| MONITOR
    MONITOR --> |Threshold Check| ANALYZE
    ANALYZE --> |Fix Ready| REPLAY
```

## 3. GitHub MCP Server

### Purpose
Complete GitHub integration for repository management and PR operations.

### Capabilities
- **Repository Operations**: Clone, fork, create
- **PR Management**: Create, update, merge pull requests
- **Issue Tracking**: Create and manage issues
- **Code Operations**: Commit, push, branch management

### Usage in Agents

```python
# PR Manager Agent usage
async def create_pull_request(title, body, branch):
    result = await mcp_client.call_tool(
        server="github",
        tool="github_create_pull_request",
        arguments={
            "owner": "your-org",
            "repo": "lpd-claude-code-monitor",
            "title": title,
            "body": body,
            "head": branch,
            "base": "main"
        }
    )
    return result["number"]

async def add_pr_comment(pr_number, comment):
    await mcp_client.call_tool(
        server="github",
        tool="github_add_pr_comment",
        arguments={
            "owner": "your-org",
            "repo": "lpd-claude-code-monitor",
            "pr_number": pr_number,
            "body": comment
        }
    )
```

### PR Workflow

```mermaid
sequenceDiagram
    participant Agent as PR Manager
    participant MCP as GitHub MCP
    participant GH as GitHub
    
    Agent->>MCP: Create branch
    MCP->>GH: New branch
    Agent->>MCP: Commit files
    MCP->>GH: Push commits
    Agent->>MCP: Create PR
    MCP->>GH: Open PR
    GH-->>MCP: PR #123
    MCP-->>Agent: PR created
    
    loop Every 10 minutes
        Agent->>MCP: Check PR status
        MCP->>GH: Get PR details
        GH-->>MCP: Status
        MCP-->>Agent: Review pending
    end
```

## 4. Sequential Thinking MCP Server

### Purpose
Provides structured problem-solving and analysis capabilities using chain-of-thought reasoning.

### Capabilities
- **Systematic Analysis**: Step-by-step problem decomposition
- **Hypothesis Testing**: Generate and validate hypotheses
- **Root Cause Analysis**: Identify underlying issues
- **Solution Generation**: Create actionable solutions

### Usage in Agents

```python
# Investigation Agent usage
async def analyze_error_pattern(error_messages):
    result = await mcp_client.call_tool(
        server="sequential-thinking",
        tool="analyze_problem",
        arguments={
            "problem": f"Analyze these DLQ errors: {error_messages}",
            "steps": [
                "Identify common patterns",
                "Determine root cause",
                "Suggest fix approach",
                "Evaluate risks"
            ]
        }
    )
    return result["analysis"]

async def generate_hypothesis(symptoms):
    result = await mcp_client.call_tool(
        server="sequential-thinking",
        tool="generate_hypothesis",
        arguments={
            "observations": symptoms,
            "domain": "AWS SQS processing errors"
        }
    )
    return result["hypotheses"]
```

### Thinking Process

```mermaid
graph TD
    subgraph "Sequential Thinking Process"
        INPUT[Error Data]
        DECOMPOSE[Decompose Problem]
        ANALYZE[Analyze Components]
        PATTERN[Identify Patterns]
        HYPOTHESIS[Generate Hypotheses]
        TEST[Test Hypotheses]
        CONCLUDE[Draw Conclusions]
        SOLUTION[Propose Solution]
    end
    
    INPUT --> DECOMPOSE
    DECOMPOSE --> ANALYZE
    ANALYZE --> PATTERN
    PATTERN --> HYPOTHESIS
    HYPOTHESIS --> TEST
    TEST --> CONCLUDE
    CONCLUDE --> SOLUTION
```

## 5. Memory MCP Server

### Purpose
Maintains a knowledge graph for tracking investigations, patterns, and solutions.

### Capabilities
- **Entity Management**: Create and manage entities
- **Relationship Tracking**: Define relationships between entities
- **Pattern Recognition**: Identify recurring issues
- **Solution Database**: Store successful fixes

### Usage in Agents

```python
# Code Fixer Agent usage
async def store_investigation(queue_name, error_type, fix):
    # Create entity for investigation
    await mcp_client.call_tool(
        server="memory",
        tool="create_entity",
        arguments={
            "name": f"Investigation_{queue_name}_{timestamp}",
            "type": "Investigation",
            "properties": {
                "queue": queue_name,
                "error_type": error_type,
                "fix_applied": fix,
                "timestamp": timestamp
            }
        }
    )
    
    # Create relationship
    await mcp_client.call_tool(
        server="memory",
        tool="create_relationship",
        arguments={
            "from": queue_name,
            "to": f"Investigation_{queue_name}_{timestamp}",
            "type": "has_investigation"
        }
    )

async def find_similar_fixes(error_type):
    result = await mcp_client.call_tool(
        server="memory",
        tool="query_graph",
        arguments={
            "query": f"MATCH (i:Investigation) WHERE i.error_type = '{error_type}' RETURN i.fix_applied"
        }
    )
    return result["fixes"]
```

### Knowledge Graph Structure

```mermaid
graph LR
    subgraph "Knowledge Graph"
        Q1[Queue: payment-dlq]
        Q2[Queue: order-dlq]
        
        I1[Investigation 1]
        I2[Investigation 2]
        I3[Investigation 3]
        
        E1[Error: Timeout]
        E2[Error: Validation]
        
        F1[Fix: Retry Logic]
        F2[Fix: Input Validation]
        
        Q1 --> I1
        Q1 --> I2
        Q2 --> I3
        
        I1 --> E1
        I2 --> E2
        I3 --> E1
        
        E1 --> F1
        E2 --> F2
    end
```

## 6. Filesystem MCP Server

### Purpose
Provides file system operations for code modifications and file management.

### Capabilities
- **File Operations**: Read, write, delete files
- **Directory Management**: Create, list, remove directories
- **Code Modification**: Edit source files
- **Configuration Updates**: Modify config files

### Usage in Agents

```python
# Code Fixer Agent usage
async def apply_fix_to_file(file_path, original_code, fixed_code):
    # Read current file
    current = await mcp_client.call_tool(
        server="filesystem",
        tool="read_file",
        arguments={"path": file_path}
    )
    
    # Apply fix
    updated = current.replace(original_code, fixed_code)
    
    # Write updated file
    await mcp_client.call_tool(
        server="filesystem",
        tool="write_file",
        arguments={
            "path": file_path,
            "content": updated
        }
    )

async def backup_file(file_path):
    await mcp_client.call_tool(
        server="filesystem",
        tool="copy_file",
        arguments={
            "source": file_path,
            "destination": f"{file_path}.backup"
        }
    )
```

## MCP Server Best Practices

### 1. Error Handling

```python
async def safe_mcp_call(server, tool, arguments):
    try:
        result = await mcp_client.call_tool(server, tool, arguments)
        return result
    except MCPServerError as e:
        logger.error(f"MCP server error: {e}")
        # Fallback logic
        return None
    except TimeoutError:
        logger.warning(f"MCP call timed out: {server}.{tool}")
        # Retry with backoff
        return await retry_with_backoff(server, tool, arguments)
```

### 2. Connection Management

```python
class MCPConnectionPool:
    def __init__(self):
        self.connections = {}
        self.max_retries = 3
    
    async def get_connection(self, server):
        if server not in self.connections:
            self.connections[server] = await self.create_connection(server)
        return self.connections[server]
    
    async def health_check(self):
        for server, conn in self.connections.items():
            if not await conn.ping():
                await self.reconnect(server)
```

### 3. Performance Optimization

```python
# Batch operations
async def batch_sqs_operations(operations):
    tasks = []
    for op in operations:
        task = mcp_client.call_tool(
            server="sns-sqs",
            tool=op["tool"],
            arguments=op["arguments"]
        )
        tasks.append(task)
    
    results = await asyncio.gather(*tasks)
    return results

# Caching
@cache(ttl=300)  # 5 minute cache
async def get_queue_attributes_cached(queue_url):
    return await mcp_client.call_tool(
        server="sns-sqs",
        tool="sqs_get_queue_attributes",
        arguments={"QueueUrl": queue_url}
    )
```

### 4. Security Considerations

```python
# Environment variable validation
def validate_mcp_config():
    required_env = {
        "aws-api": ["AWS_PROFILE", "AWS_REGION"],
        "github": ["GITHUB_TOKEN"],
        "filesystem": ["WORKSPACE_DIR"]
    }
    
    for server, vars in required_env.items():
        for var in vars:
            if not os.getenv(var):
                raise ConfigError(f"Missing {var} for {server}")

# Sanitize inputs
def sanitize_mcp_arguments(arguments):
    # Remove sensitive data from logs
    safe_args = arguments.copy()
    if "token" in safe_args:
        safe_args["token"] = "***"
    return safe_args
```

## Monitoring MCP Servers

### Health Checks

```python
async def check_mcp_health():
    health_status = {}
    
    for server in ["aws-api", "sns-sqs", "github", "sequential-thinking", "memory"]:
        try:
            result = await mcp_client.call_tool(
                server=server,
                tool="health_check",
                arguments={}
            )
            health_status[server] = "healthy"
        except Exception as e:
            health_status[server] = f"unhealthy: {e}"
    
    return health_status
```

### Metrics Collection

```mermaid
graph TB
    subgraph "MCP Metrics"
        LATENCY[Response Latency]
        ERRORS[Error Rate]
        THROUGHPUT[Request Throughput]
        AVAILABILITY[Server Availability]
    end
    
    subgraph "Monitoring"
        COLLECT[Collect Metrics]
        ANALYZE[Analyze Trends]
        ALERT[Alert on Issues]
        REPORT[Generate Reports]
    end
    
    LATENCY --> COLLECT
    ERRORS --> COLLECT
    THROUGHPUT --> COLLECT
    AVAILABILITY --> COLLECT
    
    COLLECT --> ANALYZE
    ANALYZE --> ALERT
    ANALYZE --> REPORT
```

## Troubleshooting MCP Servers

### Common Issues

| Issue | Cause | Solution |
|-------|-------|----------|
| "MCP server not found" | Server not installed | Run `npm install -g @server-name` |
| "Authentication failed" | Missing credentials | Check environment variables |
| "Connection timeout" | Network issues | Check firewall/proxy settings |
| "Rate limit exceeded" | Too many requests | Implement rate limiting |
| "Invalid arguments" | Schema mismatch | Validate against server schema |

### Debug Commands

```bash
# Test MCP server directly
npx @mcp-servers/aws --test

# Check server logs
tail -f ~/.mcp/logs/aws-api.log

# Validate configuration
python -c "import json; json.load(open('config/mcp_settings.json'))"

# Test connection
curl -X POST http://localhost:3000/health
```