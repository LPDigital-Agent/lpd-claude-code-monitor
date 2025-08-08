"""
Investigation Agent - Analyzes DLQ messages and finds root causes
Enhanced with special MCP tools for comprehensive investigation
"""

from google.adk.agents import LlmAgent
from google.adk.tools import FunctionTool as Tool
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import json
import logging

logger = logging.getLogger(__name__)

def create_context7_tool() -> Tool:
    """
    Create a tool for searching documentation and code examples using Context7
    """
    async def search_documentation(mcp_client, error_type: str, technology: str) -> Dict:
        """Search for documentation and solutions using Context7"""
        try:
            # First resolve library ID
            result = await mcp_client.call_tool(
                server="context7",
                tool="resolve-library-id",
                arguments={
                    "libraryName": technology
                }
            )
            
            if result and 'library_id' in result:
                # Get library documentation
                docs_result = await mcp_client.call_tool(
                    server="context7",
                    tool="get-library-docs",
                    arguments={
                        "context7CompatibleLibraryID": result['library_id'],
                        "topic": error_type,
                        "tokens": 5000
                    }
                )
                
                return {
                    'library': technology,
                    'documentation': docs_result.get('content', ''),
                    'relevant_sections': docs_result.get('sections', [])
                }
            
            return {'error': 'Library not found', 'library': technology}
            
        except Exception as e:
            logger.error(f"Error searching documentation with Context7: {e}")
            return {'error': str(e)}
    
    return Tool(
        name="search_documentation",
        description="Search for documentation and solutions using Context7",
        function=search_documentation
    )

def create_aws_docs_tool() -> Tool:
    """
    Create a tool for searching AWS documentation
    """
    async def search_aws_documentation(mcp_client, service: str, error_code: str) -> Dict:
        """Search AWS documentation for error codes and solutions"""
        try:
            # Search AWS documentation
            search_result = await mcp_client.call_tool(
                server="aws-documentation",
                tool="search_documentation",
                arguments={
                    "search_phrase": f"{service} {error_code}",
                    "limit": 10
                }
            )
            
            relevant_docs = []
            if search_result and 'results' in search_result:
                for doc in search_result['results'][:5]:
                    # Read the documentation content
                    content = await mcp_client.call_tool(
                        server="aws-documentation",
                        tool="read_documentation",
                        arguments={
                            "url": doc['url'],
                            "max_length": 3000
                        }
                    )
                    
                    relevant_docs.append({
                        'title': doc.get('title', ''),
                        'url': doc.get('url', ''),
                        'content': content.get('content', '')[:1000] if content else '',
                        'context': doc.get('context', '')
                    })
            
            return {
                'service': service,
                'error_code': error_code,
                'documentation': relevant_docs,
                'total_results': len(relevant_docs)
            }
            
        except Exception as e:
            logger.error(f"Error searching AWS documentation: {e}")
            return {'error': str(e), 'service': service}
    
    return Tool(
        name="search_aws_documentation",
        description="Search AWS documentation for error codes and solutions",
        function=search_aws_documentation
    )

def create_enhanced_cloudwatch_tool() -> Tool:
    """
    Create an enhanced tool for analyzing CloudWatch logs using dedicated MCP
    """
    async def analyze_cloudwatch_logs(mcp_client, log_group: str, start_time: str, pattern: str) -> Dict:
        """Analyze CloudWatch logs with advanced filtering and insights"""
        try:
            # Use dedicated CloudWatch MCP for better log analysis
            result = await mcp_client.call_tool(
                server="cloudwatch-logs",
                tool="filter_log_events",
                arguments={
                    "log_group_name": log_group,
                    "start_time": start_time,
                    "filter_pattern": pattern,
                    "limit": 50
                }
            )
            
            events = []
            error_patterns = {}
            
            if result and 'events' in result:
                for event in result['events']:
                    message = event.get('message', '')
                    events.append({
                        'timestamp': event.get('timestamp'),
                        'message': message,
                        'log_stream': event.get('logStreamName')
                    })
                    
                    # Analyze error patterns
                    if 'ERROR' in message or 'Exception' in message:
                        error_type = self._extract_error_type(message)
                        error_patterns[error_type] = error_patterns.get(error_type, 0) + 1
            
            # Get log insights if available
            insights = await mcp_client.call_tool(
                server="cloudwatch-logs",
                tool="start_query",
                arguments={
                    "log_group_name": log_group,
                    "start_time": start_time,
                    "query": f"fields @timestamp, @message | filter @message like /{pattern}/ | stats count() by bin(5m)"
                }
            )
            
            return {
                'events': events,
                'event_count': len(events),
                'error_patterns': error_patterns,
                'insights': insights,
                'log_group': log_group
            }
            
        except Exception as e:
            logger.error(f"Error analyzing CloudWatch logs: {e}")
            return {'error': str(e), 'events': []}
    
    def _extract_error_type(self, message: str) -> str:
        """Extract error type from log message"""
        if 'Exception' in message:
            parts = message.split('Exception')
            if parts:
                return parts[0].split()[-1] + 'Exception' if parts[0] else 'Exception'
        elif 'ERROR' in message:
            return 'ERROR'
        return 'Unknown'
    
    return Tool(
        name="analyze_cloudwatch_logs",
        description="Analyze CloudWatch logs with advanced filtering and insights",
        function=analyze_cloudwatch_logs
    )

def create_lambda_analysis_tool() -> Tool:
    """
    Create a tool for analyzing Lambda function issues
    """
    async def analyze_lambda_function(mcp_client, function_name: str) -> Dict:
        """Analyze Lambda function configuration and recent executions"""
        try:
            # Get Lambda function configuration
            config_result = await mcp_client.call_tool(
                server="lambda-tools",
                tool="get_function_configuration",
                arguments={
                    "function_name": function_name
                }
            )
            
            # Get recent invocation errors
            errors_result = await mcp_client.call_tool(
                server="lambda-tools",
                tool="list_function_errors",
                arguments={
                    "function_name": function_name,
                    "start_time": (datetime.now() - timedelta(hours=24)).isoformat(),
                    "limit": 20
                }
            )
            
            # Get function metrics
            metrics_result = await mcp_client.call_tool(
                server="lambda-tools",
                tool="get_function_metrics",
                arguments={
                    "function_name": function_name,
                    "metric_names": ["Errors", "Throttles", "Duration", "ConcurrentExecutions"],
                    "period": 300,  # 5 minutes
                    "start_time": (datetime.now() - timedelta(hours=1)).isoformat()
                }
            )
            
            analysis = {
                'function_name': function_name,
                'configuration': {
                    'runtime': config_result.get('Runtime', ''),
                    'timeout': config_result.get('Timeout', 0),
                    'memory_size': config_result.get('MemorySize', 0),
                    'last_modified': config_result.get('LastModified', ''),
                    'environment': config_result.get('Environment', {}).get('Variables', {}),
                    'dead_letter_config': config_result.get('DeadLetterConfig', {})
                },
                'recent_errors': errors_result.get('errors', []),
                'metrics': metrics_result,
                'issues_detected': []
            }
            
            # Analyze for common issues
            if config_result.get('Timeout', 0) < 10:
                analysis['issues_detected'].append('Function timeout may be too low')
            
            if config_result.get('MemorySize', 0) < 256:
                analysis['issues_detected'].append('Memory allocation may be insufficient')
            
            if not config_result.get('DeadLetterConfig', {}).get('TargetArn'):
                analysis['issues_detected'].append('No DLQ configured for function')
            
            return analysis
            
        except Exception as e:
            logger.error(f"Error analyzing Lambda function: {e}")
            return {'error': str(e), 'function_name': function_name}
    
    return Tool(
        name="analyze_lambda_function",
        description="Analyze Lambda function configuration and recent executions",
        function=analyze_lambda_function
    )

def create_sequential_analysis_tool() -> Tool:
    """
    Create a tool for systematic root cause analysis
    """
    async def sequential_analysis(mcp_client, evidence: Dict) -> Dict:
        """Perform systematic root cause analysis using sequential thinking"""
        try:
            # Use sequential-thinking MCP for structured analysis
            result = await mcp_client.call_tool(
                server="sequential-thinking",
                tool="sequentialthinking",
                arguments={
                    "thought": f"Analyzing DLQ messages in {evidence.get('queue_name')}. Evidence: {json.dumps(evidence, indent=2)}",
                    "nextThoughtNeeded": True,
                    "thoughtNumber": 1,
                    "totalThoughts": 5
                }
            )
            
            analysis_steps = [result]
            
            # Continue sequential analysis
            for i in range(2, 6):
                if result.get('nextThoughtNeeded', False):
                    result = await mcp_client.call_tool(
                        server="sequential-thinking",
                        tool="sequentialthinking",
                        arguments={
                            "thought": f"Step {i}: Continuing analysis based on previous findings",
                            "nextThoughtNeeded": i < 5,
                            "thoughtNumber": i,
                            "totalThoughts": 5
                        }
                    )
                    analysis_steps.append(result)
            
            return {
                'analysis_steps': analysis_steps,
                'root_cause': analysis_steps[-1].get('thought', 'Unknown'),
                'evidence': evidence
            }
            
        except Exception as e:
            logger.error(f"Error in sequential analysis: {e}")
            return {'error': str(e)}
    
    return Tool(
        name="sequential_analysis",
        description="Perform systematic root cause analysis",
        function=sequential_analysis
    )

def create_investigator_agent() -> LlmAgent:
    """
    Create the Investigation agent for root cause analysis with enhanced MCP tools
    """
    
    investigator = LlmAgent(
        name="investigator",
        model="gemini-2.0-flash",
        description="Analyzes DLQ messages and finds root causes using advanced MCP tools",
        instruction="""
        You are the Investigation Agent for root cause analysis of DLQ issues.
        
        CONTEXT:
        - AWS Profile: FABIO-PROD
        - Region: sa-east-1
        
        AVAILABLE MCP TOOLS:
        1. **Context7** - Search documentation and code examples for error patterns
        2. **AWS Documentation** - Look up AWS service documentation and error codes
        3. **CloudWatch Logs** - Advanced log analysis with filtering and insights
        4. **Lambda Tools** - Analyze Lambda function configurations and issues
        5. **Sequential Thinking** - Systematic step-by-step root cause analysis
        
        YOUR RESPONSIBILITIES:
        1. **Analyze DLQ Messages**:
           - Parse error messages and stack traces
           - Identify error patterns and frequency
           - Extract relevant metadata
        
        2. **Use Context7 for Solutions**:
           - Search for documentation on the error types found
           - Find code examples and best practices
           - Look up library-specific solutions
        
        3. **Check AWS Documentation**:
           - Look up AWS error codes
           - Find service-specific troubleshooting guides
           - Identify AWS best practices violations
        
        4. **Deep CloudWatch Analysis**:
           - Use the dedicated CloudWatch MCP for advanced log queries
           - Correlate errors with system events
           - Generate insights from log patterns
           - Track error frequency over time
        
        5. **Lambda Function Analysis** (if applicable):
           - Check function configuration
           - Analyze timeout and memory issues
           - Review environment variables
           - Check DLQ configuration
        
        6. **Root Cause Identification**:
           - Use sequential thinking for systematic analysis
           - Consider multiple hypotheses
           - Validate with evidence from logs and documentation
           - Provide confidence level for each hypothesis
        
        7. **Generate Investigation Report**:
           - Summary of findings
           - Root cause with evidence
           - Recommended fixes with documentation references
           - Prevention measures
        
        INVESTIGATION WORKFLOW:
        1. Start with sequential_analysis to structure the investigation
        2. Parse DLQ messages for error patterns
        3. Use Context7 to find relevant documentation
        4. Search AWS documentation for error codes
        5. Analyze CloudWatch logs for patterns
        6. If Lambda-related, analyze function configuration
        7. Synthesize findings into actionable report
        
        OUTPUT FORMAT:
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
        
        Remember to leverage all available MCP tools for comprehensive investigation!
        """,
        tools=[
            create_context7_tool(),
            create_aws_docs_tool(),
            create_enhanced_cloudwatch_tool(),
            create_lambda_analysis_tool(),
            create_sequential_analysis_tool()
        ]
    )
    
    return investigator

# Export the agent
investigator = create_investigator_agent()