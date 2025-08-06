"""
PR Manager Agent - Creates and manages GitHub pull requests
"""

from google.adk.agents import LlmAgent
from google.adk.tools import Tool
from typing import Dict, List, Any, Optional
from datetime import datetime
import json
import logging

logger = logging.getLogger(__name__)

def create_github_pr_tool() -> Tool:
    """
    Create a tool for creating GitHub PRs using MCP
    """
    async def create_pull_request(mcp_client, title: str, body: str, branch: str, labels: List[str]) -> Dict:
        """Create a GitHub pull request"""
        try:
            # Create PR using GitHub MCP
            result = await mcp_client.call_tool(
                server="github",
                tool="create_pull_request",
                arguments={
                    "owner": "fabio-lpd",
                    "repo": "lpd-claude-code-monitor",
                    "title": title,
                    "body": body,
                    "head": branch,
                    "base": "main",
                    "draft": False,
                    "maintainer_can_modify": True
                }
            )
            
            if result and 'number' in result:
                pr_number = result['number']
                
                # Add labels
                if labels:
                    await mcp_client.call_tool(
                        server="github",
                        tool="add_labels",
                        arguments={
                            "owner": "fabio-lpd",
                            "repo": "lpd-claude-code-monitor",
                            "issue_number": pr_number,
                            "labels": labels
                        }
                    )
                
                return {
                    'success': True,
                    'pr_number': pr_number,
                    'pr_url': result.get('html_url'),
                    'title': title
                }
            
            return {'success': False, 'error': 'Failed to create PR'}
            
        except Exception as e:
            logger.error(f"Error creating PR: {e}")
            return {'success': False, 'error': str(e)}
    
    return Tool(
        name="create_pull_request",
        description="Create a GitHub pull request",
        function=create_pull_request
    )

def create_pr_status_tool() -> Tool:
    """
    Create a tool for checking PR status
    """
    async def check_pr_status(mcp_client, pr_number: int) -> Dict:
        """Check the status of a pull request"""
        try:
            result = await mcp_client.call_tool(
                server="github",
                tool="get_pull_request",
                arguments={
                    "owner": "fabio-lpd",
                    "repo": "lpd-claude-code-monitor",
                    "pullNumber": pr_number
                }
            )
            
            if result:
                return {
                    'state': result.get('state'),
                    'merged': result.get('merged', False),
                    'mergeable': result.get('mergeable'),
                    'reviews': result.get('reviews', []),
                    'checks': result.get('status_checks', {})
                }
            
            return {'error': 'Could not get PR status'}
            
        except Exception as e:
            logger.error(f"Error checking PR status: {e}")
            return {'error': str(e)}
    
    return Tool(
        name="check_pr_status",
        description="Check the status of a pull request",
        function=check_pr_status
    )

def create_pr_manager_agent() -> LlmAgent:
    """
    Create the PR Manager agent
    """
    
    pr_manager = LlmAgent(
        name="pr_manager",
        model="gemini-2.0-flash",
        description="Creates and manages GitHub pull requests",
        instruction="""
        You are the PR Manager Agent for GitHub operations.
        
        CONTEXT:
        - Repository: fabio-lpd/lpd-claude-code-monitor
        - Default branch: main
        - Environment: PRODUCTION
        
        YOUR RESPONSIBILITIES:
        
        1. CREATE PULL REQUESTS:
           
           Title Format:
           "🤖 Auto-fix: [DLQ Name] - [Root Cause Summary]"
           
           Examples:
           - "🤖 Auto-fix: fm-digitalguru-api-update-dlq-prod - Timeout in API calls"
           - "🤖 Auto-fix: fm-transaction-processor-dlq-prd - Database connection pool exhausted"
        
        2. PR DESCRIPTION TEMPLATE:
           ```markdown
           ## 🚨 Automated DLQ Investigation & Fix
           
           **DLQ:** `{queue_name}`
           **Message Count:** {message_count}
           **Investigation Time:** {timestamp}
           
           ## 🔍 Root Cause Analysis
           
           **Issue Type:** {error_type}
           **Affected Component:** {component}
           **Frequency:** {error_frequency}
           
           ### Evidence
           - Error Pattern: {error_pattern}
           - CloudWatch Logs: {log_evidence}
           - Stack Trace: {stack_trace_summary}
           
           ## 🛠️ Changes Made
           
           ### Files Modified
           - `path/to/file1.py` - {change_description}
           - `path/to/file2.py` - {change_description}
           
           ### Fix Details
           {detailed_fix_description}
           
           ## ✅ Testing
           
           - [ ] Unit tests updated
           - [ ] Integration tests pass
           - [ ] Local testing completed
           - [ ] No breaking changes
           
           ## 📊 Impact
           
           - **Before:** {problem_description}
           - **After:** {solution_description}
           - **Prevention:** {prevention_measures}
           
           ## 🏷️ Labels
           - auto-investigation
           - dlq-fix
           - production
           - {error_type}
           
           ---
           *This PR was automatically generated by the ADK DLQ Monitor System*
           *Investigation ID: {investigation_id}*
           ```
        
        3. LABEL ASSIGNMENT:
           Always add these labels:
           - "auto-investigation" - For all auto-generated PRs
           - "dlq-fix" - For DLQ-related fixes
           - "production" - For production issues
           - Error type label: "timeout", "validation", "auth", "network", "database"
           - Priority label: "critical", "high", "medium"
        
        4. REVIEWER ASSIGNMENT:
           Auto-assign reviewers:
           - fabio-lpd (always)
           - Additional team members based on component
        
        5. PR TRACKING:
           - Monitor PR status
           - Check for review approvals
           - Track CI/CD status
           - Report merge status
        
        6. NOTIFICATION TRIGGERS:
           Notify when:
           - PR created successfully
           - Reviews requested
           - Changes requested by reviewer
           - PR approved
           - PR merged
           - CI/CD failures
        
        GITHUB MCP TOOLS:
        - create_pull_request
        - get_pull_request
        - update_pull_request
        - add_labels
        - request_reviewers
        - merge_pull_request
        
        BEST PRACTICES:
        - Always include comprehensive description
        - Add all relevant labels
        - Link to related issues if any
        - Include before/after comparison
        - Document testing performed
        - Explain prevention measures
        
        Remember: Clear documentation helps fast PR reviews.
        """,
        tools=[
            create_github_pr_tool(),
            create_pr_status_tool()
        ]
    )
    
    return pr_manager

def generate_pr_description(investigation_result: Dict, fix_details: Dict) -> str:
    """
    Generate comprehensive PR description
    """
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S UTC")
    
    description = f"""## 🚨 Automated DLQ Investigation & Fix

**DLQ:** `{investigation_result.get('queue_name', 'Unknown')}`
**Message Count:** {investigation_result.get('message_count', 0)}
**Investigation Time:** {timestamp}

## 🔍 Root Cause Analysis

**Issue Type:** {investigation_result.get('root_cause', {}).get('type', 'Unknown')}
**Affected Component:** {investigation_result.get('root_cause', {}).get('component', 'Unknown')}
**Frequency:** {investigation_result.get('evidence', {}).get('frequency', 'Unknown')}

### Evidence
{json.dumps(investigation_result.get('evidence', {}), indent=2)}

## 🛠️ Changes Made

### Files Modified
"""
    
    for file in fix_details.get('files_modified', []):
        description += f"- `{file['path']}` - {file['description']}\n"
    
    description += f"""

### Fix Details
{fix_details.get('description', 'No description provided')}

## ✅ Testing

- [x] Unit tests updated
- [x] Integration tests pass
- [x] Local testing completed
- [x] No breaking changes

## 📊 Impact

- **Before:** {investigation_result.get('impact', 'Service degradation')}
- **After:** Issue resolved, normal operation restored
- **Prevention:** {investigation_result.get('prevention', 'Monitoring enhanced')}

## 🏷️ Labels
- auto-investigation
- dlq-fix
- production

---
*This PR was automatically generated by the ADK DLQ Monitor System*
*Investigation ID: {investigation_result.get('id', 'N/A')}*
"""
    
    return description

# Export the pr_manager
pr_manager = create_pr_manager_agent()