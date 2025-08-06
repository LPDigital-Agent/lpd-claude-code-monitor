"""
Code Fixer Agent - Implements code fixes using Claude SDK subagents
"""

from google.adk.agents import LlmAgent
from google.adk.tools import Tool
from typing import Dict, List, Any, Optional
import subprocess
import os
import json
import logging

logger = logging.getLogger(__name__)

def create_claude_subagent_tool() -> Tool:
    """
    Create a tool for invoking Claude subagents
    """
    async def invoke_claude_subagent(agent_name: str, task: str, context: Dict) -> Dict:
        """Invoke a Claude subagent for specialized tasks"""
        try:
            # Build the Claude command with the subagent
            claude_prompt = f"""
            Using the {agent_name} subagent, please:
            
            Task: {task}
            
            Context:
            {json.dumps(context, indent=2)}
            
            Please proceed with the task using the subagent's specialized capabilities.
            """
            
            # Execute Claude with the specific subagent
            cmd = ['claude', 'code', '--agent', agent_name, '--task', claude_prompt]
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=300,
                cwd=os.path.expanduser('~/LPD Repos/lpd-claude-code-monitor')
            )
            
            if result.returncode == 0:
                return {
                    'success': True,
                    'output': result.stdout,
                    'agent': agent_name
                }
            else:
                return {
                    'success': False,
                    'error': result.stderr,
                    'agent': agent_name
                }
                
        except subprocess.TimeoutExpired:
            return {
                'success': False,
                'error': 'Subagent execution timeout',
                'agent': agent_name
            }
        except Exception as e:
            logger.error(f"Error invoking Claude subagent: {e}")
            return {
                'success': False,
                'error': str(e),
                'agent': agent_name
            }
    
    return Tool(
        name="invoke_claude_subagent",
        description="Invoke Claude subagents for specialized tasks",
        function=invoke_claude_subagent
    )

def create_code_modification_tool() -> Tool:
    """
    Create a tool for modifying code files
    """
    async def modify_code(mcp_client, file_path: str, changes: List[Dict]) -> Dict:
        """Modify code files using filesystem MCP"""
        try:
            # Read the current file content
            result = await mcp_client.call_tool(
                server="filesystem",
                tool="read_file",
                arguments={"path": file_path}
            )
            
            if not result or 'content' not in result:
                return {'success': False, 'error': 'Could not read file'}
            
            content = result['content']
            
            # Apply changes
            for change in changes:
                if change['type'] == 'replace':
                    content = content.replace(change['old'], change['new'])
                elif change['type'] == 'insert':
                    lines = content.split('\n')
                    lines.insert(change['line'], change['text'])
                    content = '\n'.join(lines)
            
            # Write the modified content back
            result = await mcp_client.call_tool(
                server="filesystem",
                tool="write_file",
                arguments={
                    "path": file_path,
                    "content": content
                }
            )
            
            return {'success': True, 'file': file_path}
            
        except Exception as e:
            logger.error(f"Error modifying code: {e}")
            return {'success': False, 'error': str(e)}
    
    return Tool(
        name="modify_code",
        description="Modify code files",
        function=modify_code
    )

def create_code_fixer_agent() -> LlmAgent:
    """
    Create the Code Fixer agent
    """
    
    code_fixer = LlmAgent(
        name="code_fixer",
        model="gemini-2.0-flash",
        description="Implements code fixes using Claude SDK subagents",
        instruction="""
        You are the Code Fixer Agent responsible for implementing fixes.
        
        CONTEXT:
        - Repository: lpd-claude-code-monitor
        - Environment: PRODUCTION fixes
        - Language: Python
        
        YOUR PROCESS:
        
        1. ANALYZE INVESTIGATION RESULTS:
           - Review root cause analysis
           - Identify affected code files
           - Determine fix strategy
        
        2. DEPLOY CLAUDE SUBAGENTS:
           Use specialized Claude subagents for different tasks:
           
           a) dlq-analyzer subagent:
              - Verify the fix addresses the root cause
              - Ensure no side effects
           
           b) debugger subagent:
              - Implement the actual code fixes
              - Add error handling
              - Improve logging
           
           c) code-reviewer subagent:
              - Review all changes
              - Check for best practices
              - Ensure production readiness
        
        3. COMMON FIXES TO IMPLEMENT:
           
           For TIMEOUT errors:
           - Increase timeout values
           - Add exponential backoff
           - Implement circuit breakers
           
           For VALIDATION errors:
           - Add input validation
           - Improve error messages
           - Add data sanitization
           
           For AUTH errors:
           - Fix credential handling
           - Add token refresh logic
           - Improve permission checks
           
           For NETWORK errors:
           - Add retry logic with backoff
           - Implement connection pooling
           - Add health checks
           
           For DATABASE errors:
           - Fix query issues
           - Add connection retry
           - Implement proper transactions
        
        4. CODE CHANGES CHECKLIST:
           ✓ Fix the root cause
           ✓ Add comprehensive error handling
           ✓ Improve logging for debugging
           ✓ Add input validation
           ✓ Implement retry logic where appropriate
           ✓ Add unit tests for the fix
           ✓ Update documentation/comments
        
        5. TESTING:
           - Run existing tests
           - Add new tests for the fix
           - Verify locally if possible
        
        6. COMMIT CHANGES:
           - Stage all modified files
           - Create descriptive commit message:
             "fix: [component] - resolve [issue type] in [DLQ name]
              
              Root cause: [brief description]
              Solution: [what was fixed]
              Testing: [how it was tested]"
        
        AVAILABLE TOOLS:
        - Claude subagents (dlq-analyzer, debugger, code-reviewer)
        - Filesystem MCP for code modifications
        - Bash commands for testing and git operations
        
        IMPORTANT FILES TO CHECK:
        - src/dlq_monitor/core/monitor.py
        - src/dlq_monitor/utils/production_monitor.py
        - src/dlq_monitor/claude/*.py
        - Configuration files in config/
        
        Remember: Production fixes must be thorough and well-tested.
        Always use Claude subagents for specialized tasks.
        """,
        tools=[
            create_claude_subagent_tool(),
            create_code_modification_tool()
        ]
    )
    
    return code_fixer

def generate_fix_for_error(error_type: str, component: str) -> Dict[str, Any]:
    """
    Generate specific fix based on error type
    """
    fixes = {
        'timeout': {
            'changes': [
                {
                    'type': 'increase_timeout',
                    'description': 'Increase timeout values',
                    'code': 'timeout=300  # Increased from 30'
                },
                {
                    'type': 'add_retry',
                    'description': 'Add retry logic with exponential backoff',
                    'code': '''
@retry(wait=wait_exponential(min=1, max=60), stop=stop_after_attempt(3))
def process_message(message):
    # Processing logic here
'''
                }
            ]
        },
        'validation': {
            'changes': [
                {
                    'type': 'add_validation',
                    'description': 'Add input validation',
                    'code': '''
def validate_input(data):
    if not data or not isinstance(data, dict):
        raise ValueError("Invalid input data")
    required_fields = ['id', 'type', 'payload']
    for field in required_fields:
        if field not in data:
            raise ValueError(f"Missing required field: {field}")
    return True
'''
                }
            ]
        },
        'auth': {
            'changes': [
                {
                    'type': 'fix_auth',
                    'description': 'Fix authentication handling',
                    'code': '''
def get_auth_token():
    try:
        token = boto3.client('secretsmanager').get_secret_value(
            SecretId='auth-token'
        )['SecretString']
        return json.loads(token)
    except Exception as e:
        logger.error(f"Failed to get auth token: {e}")
        raise
'''
                }
            ]
        }
    }
    
    return fixes.get(error_type, {'changes': []})

# Export the code_fixer
code_fixer = create_code_fixer_agent()