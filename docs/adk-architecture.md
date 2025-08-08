# ADK Multi-Agent DLQ Monitor Architecture

## Overview

The ADK Multi-Agent DLQ Monitor is a sophisticated autonomous system that monitors AWS Dead Letter Queues, investigates issues, implements fixes, and creates pull requests - all without human intervention.

## System Architecture

```mermaid
graph TB
    subgraph "ADK Multi-Agent System"
        COORD[Coordinator Agent<br/>Main Orchestrator]
        DLQ[DLQ Monitor Agent<br/>AWS SQS Monitor]
        INV[Investigation Agent<br/>Root Cause Analysis]
        FIX[Code Fixer Agent<br/>Fix Implementation]
        PR[PR Manager Agent<br/>GitHub Integration]
        NOTIFY[Notifier Agent<br/>Alerts & Updates]
    end
    
    subgraph "Claude Subagents"
        ANALYZER[dlq-analyzer<br/>Message Analysis]
        DEBUG[debugger<br/>Fix Implementation]
        REVIEW[code-reviewer<br/>Quality Assurance]
    end
    
    subgraph "MCP Servers"
        AWS[aws-api & sns-sqs<br/>AWS Operations]
        GH[github<br/>PR Management]
        THINK[sequential-thinking<br/>Analysis]
        MEM[memory<br/>Knowledge Graph]
    end
    
    subgraph "External Systems"
        SQS[(AWS SQS<br/>DLQs)]
        GITHUB[(GitHub<br/>Repository)]
        MAC[macOS<br/>Notifications]
        VOICE[ElevenLabs<br/>TTS]
    end
    
    COORD -->|triggers| DLQ
    COORD -->|initiates| INV
    COORD -->|requests| NOTIFY
    
    DLQ -->|reports| COORD
    DLQ <-->|monitors| SQS
    DLQ -.->|uses| AWS
    
    INV -->|analysis| FIX
    INV -.->|uses| THINK
    
    FIX -->|fixes| PR
    FIX -->|invokes| ANALYZER
    FIX -->|invokes| DEBUG
    FIX -->|invokes| REVIEW
    FIX -.->|uses| MEM
    
    PR <-->|manages| GITHUB
    PR -.->|uses| GH
    
    NOTIFY -->|sends| MAC
    NOTIFY -->|speaks| VOICE
    
    style COORD fill:#f9f,stroke:#333,stroke-width:4px
    style DLQ fill:#bbf,stroke:#333,stroke-width:2px
    style INV fill:#bbf,stroke:#333,stroke-width:2px
    style FIX fill:#bbf,stroke:#333,stroke-width:2px
    style PR fill:#bbf,stroke:#333,stroke-width:2px
    style NOTIFY fill:#bbf,stroke:#333,stroke-width:2px
```

## Agent Workflow

```mermaid
sequenceDiagram
    participant C as Coordinator
    participant D as DLQ Monitor
    participant I as Investigation
    participant F as Code Fixer
    participant P as PR Manager
    participant N as Notifier
    
    loop Every 30 seconds
        C->>D: Check DLQs
        D->>D: Query AWS SQS
        D-->>C: Report status
        
        alt Messages found in critical DLQ
            C->>C: Check cooldown
            alt Not in cooldown
                C->>N: Send alert
                C->>I: Start investigation
                I->>I: Analyze messages
                I->>I: Check CloudWatch
                I-->>F: Root cause
                F->>F: Invoke Claude subagents
                F->>F: Implement fix
                F-->>P: Send fix
                P->>P: Create PR
                P-->>N: PR created
                N->>N: Voice notification
                
                loop Every 10 minutes
                    N->>N: PR reminder
                end
            end
        end
    end
```

## Component Details

### 1. Coordinator Agent (`coordinator.py`)
- **Role**: Main orchestrator
- **Responsibilities**:
  - Trigger monitoring cycles
  - Manage investigation state
  - Prevent duplicate investigations
  - Coordinate agent interactions
- **Key Features**:
  - 1-hour cooldown between investigations
  - State tracking for active investigations
  - Priority handling for critical DLQs

### 2. DLQ Monitor Agent (`dlq_monitor.py`)
- **Role**: AWS SQS monitoring
- **MCP Integration**: aws-api, sns-sqs
- **Operations**:
  - List queues matching DLQ patterns
  - Get queue attributes
  - Check message counts
  - Report alerts to coordinator

### 3. Investigation Agent (`investigator.py`)
- **Role**: Root cause analysis
- **MCP Integration**: sequential-thinking
- **Analysis Types**:
  - Timeout errors
  - Validation failures
  - Authentication issues
  - Network problems
  - Database errors
- **Output**: Detailed investigation report

### 4. Code Fixer Agent (`code_fixer.py`)
- **Role**: Fix implementation
- **Claude Subagents**:
  - `dlq-analyzer`: Message analysis
  - `debugger`: Fix implementation
  - `code-reviewer`: Quality assurance
- **Fix Patterns**:
  - Retry logic with exponential backoff
  - Input validation improvements
  - Token refresh mechanisms
  - Connection pooling
  - Error handling enhancements

### 5. PR Manager Agent (`pr_manager.py`)
- **Role**: GitHub integration
- **MCP Integration**: github
- **Features**:
  - Create comprehensive PRs
  - Include investigation details
  - Add fix explanations
  - Track PR status

### 6. Notifier Agent (`notifier.py`)
- **Role**: Multi-channel notifications
- **Channels**:
  - macOS native notifications
  - ElevenLabs voice announcements
  - PR reminders
- **Alert Types**:
  - DLQ message detection
  - Investigation start/complete
  - PR creation
  - Review reminders

## MCP Server Integration

```mermaid
graph LR
    subgraph "MCP Servers"
        AWS[aws-api]
        SNS[sns-sqs]
        GH[github]
        THINK[sequential-thinking]
        MEM[memory]
    end
    
    subgraph "Operations"
        SQS_OPS[SQS Operations<br/>- List queues<br/>- Get attributes<br/>- Receive messages]
        GH_OPS[GitHub Operations<br/>- Create PR<br/>- Add comments<br/>- Track status]
        ANALYSIS[Analysis<br/>- Chain of thought<br/>- Problem solving<br/>- Hypothesis testing]
        KNOWLEDGE[Knowledge Graph<br/>- Track investigations<br/>- Store patterns<br/>- Learn from fixes]
    end
    
    AWS --> SQS_OPS
    SNS --> SQS_OPS
    GH --> GH_OPS
    THINK --> ANALYSIS
    MEM --> KNOWLEDGE
```

## Claude Subagent Architecture

```mermaid
graph TD
    subgraph "Claude Subagents"
        ANALYZER[dlq-analyzer.md]
        DEBUG[debugger.md]
        REVIEW[code-reviewer.md]
    end
    
    subgraph "dlq-analyzer"
        A1[Analyze DLQ messages]
        A2[Identify error patterns]
        A3[Check CloudWatch logs]
        A4[Generate root cause]
    end
    
    subgraph "debugger"
        D1[Implement fixes]
        D2[Add error handling]
        D3[Apply retry logic]
        D4[Test implementation]
    end
    
    subgraph "code-reviewer"
        R1[Review changes]
        R2[Check quality]
        R3[Verify tests]
        R4[Ensure production ready]
    end
    
    ANALYZER --> A1 --> A2 --> A3 --> A4
    DEBUG --> D1 --> D2 --> D3 --> D4
    REVIEW --> R1 --> R2 --> R3 --> R4
```

## Configuration

### Environment Variables
```bash
GEMINI_API_KEY=your_gemini_key       # Google AI API key
GITHUB_TOKEN=your_github_token       # GitHub access token
AWS_PROFILE=FABIO-PROD               # AWS profile
AWS_REGION=sa-east-1                 # AWS region
```

### ADK Configuration (`config/adk_config.yaml`)
```yaml
model:
  provider: gemini
  default_model: gemini-2.0-flash
  temperature: 0.7

agents:
  coordinator:
    check_interval: 30
    cooldown_hours: 1
  
monitoring:
  critical_dlqs:
    - fm-digitalguru-api-update-dlq-prod
    - fm-transaction-processor-dlq-prd
```

### MCP Settings (`config/mcp_settings.json`)
```json
{
  "mcpServers": {
    "aws-api": {
      "command": "npx",
      "args": ["-y", "@mcp-servers/aws"],
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
    }
  }
}
```

## Deployment

### Prerequisites
1. Python 3.11+
2. Google ADK installed
3. AWS credentials configured
4. GitHub token with repo access
5. Gemini API key

### Installation
```bash
# Clone repository
git clone <repository>
cd lpd-claude-code-monitor

# Setup environment
python3 -m venv venv
source venv/bin/activate
pip install -r requirements_adk.txt

# Configure
cp .env.template .env
# Edit .env with your credentials

# Validate setup
python tests/validation/test_adk_simple.py
```

### Running
```bash
# Production monitoring
./scripts/start_monitor.sh adk-production

# Test mode (3 cycles)
./scripts/start_monitor.sh adk-test 3
```

## Monitoring & Observability

### Logs
- Location: `logs/adk_monitor.log`
- Includes agent interactions
- Investigation details
- Error tracking

### State Files
- `.claude_sessions.json`: Active Claude sessions
- Investigation tracking
- PR status monitoring

### Metrics
- DLQ message counts
- Investigation frequency
- Fix success rate
- PR creation/merge rate

## Security Considerations

1. **Credentials**: All sensitive data in environment variables
2. **AWS Access**: Limited to specific profile and region
3. **GitHub Scope**: Repository access only
4. **Code Review**: All fixes go through PR process
5. **Cooldown**: Prevents investigation loops

## Performance

- **Monitoring Interval**: 30 seconds
- **Investigation Cooldown**: 1 hour
- **PR Reminders**: Every 10 minutes
- **Agent Response**: < 5 seconds typical
- **Fix Generation**: 30-60 seconds
- **PR Creation**: < 10 seconds

## Future Enhancements

1. **Machine Learning**: Pattern recognition for common issues
2. **Auto-merge**: Automatic PR merging after tests pass
3. **Multi-region**: Support for multiple AWS regions
4. **Slack Integration**: Team notifications
5. **Metrics Dashboard**: Real-time monitoring UI
6. **A/B Testing**: Compare fix effectiveness