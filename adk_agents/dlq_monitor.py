"""
DLQ Monitor Agent - Monitors AWS SQS Dead Letter Queues
"""

from google.adk.agents import LlmAgent
from google.adk.tools import Tool
from typing import List, Dict, Any
import json
import logging

logger = logging.getLogger(__name__)

def create_check_dlq_tool() -> Tool:
    """
    Create a tool for checking DLQ messages using AWS MCP
    """
    async def check_dlq_messages(mcp_client) -> Dict[str, Any]:
        """Check all DLQs for messages"""
        try:
            # List all queues with DLQ patterns
            result = await mcp_client.call_tool(
                server="aws-api",
                tool="call_aws",
                arguments={
                    "command": "sqs list-queues --queue-name-prefix '-dlq'"
                }
            )
            
            dlq_alerts = []
            if result and 'QueueUrls' in result:
                for queue_url in result['QueueUrls']:
                    # Get queue attributes including message count
                    attrs = await mcp_client.call_tool(
                        server="aws-api",
                        tool="call_aws",
                        arguments={
                            "command": f"sqs get-queue-attributes --queue-url {queue_url} --attribute-names ApproximateNumberOfMessages"
                        }
                    )
                    
                    if attrs and 'Attributes' in attrs:
                        message_count = int(attrs['Attributes'].get('ApproximateNumberOfMessages', 0))
                        if message_count > 0:
                            queue_name = queue_url.split('/')[-1]
                            dlq_alerts.append({
                                'queue_name': queue_name,
                                'queue_url': queue_url,
                                'message_count': message_count
                            })
            
            return {'alerts': dlq_alerts}
            
        except Exception as e:
            logger.error(f"Error checking DLQs: {e}")
            return {'error': str(e), 'alerts': []}
    
    return Tool(
        name="check_dlq_messages",
        description="Check all DLQs for messages using AWS MCP",
        function=check_dlq_messages
    )

def create_get_dlq_messages_tool() -> Tool:
    """
    Create a tool for retrieving messages from a specific DLQ
    """
    async def get_dlq_messages(mcp_client, queue_url: str, max_messages: int = 10) -> List[Dict]:
        """Retrieve messages from a specific DLQ"""
        try:
            result = await mcp_client.call_tool(
                server="sns-sqs",
                tool="receive_messages",
                arguments={
                    "queue_url": queue_url,
                    "max_number_of_messages": min(max_messages, 10),
                    "wait_time_seconds": 1,
                    "visibility_timeout": 30
                }
            )
            
            messages = []
            if result and 'Messages' in result:
                for msg in result['Messages']:
                    messages.append({
                        'message_id': msg.get('MessageId'),
                        'body': msg.get('Body'),
                        'attributes': msg.get('Attributes', {}),
                        'receipt_handle': msg.get('ReceiptHandle')
                    })
            
            return messages
            
        except Exception as e:
            logger.error(f"Error retrieving DLQ messages: {e}")
            return []
    
    return Tool(
        name="get_dlq_messages",
        description="Retrieve messages from a specific DLQ",
        function=get_dlq_messages
    )

def create_dlq_monitor_agent() -> LlmAgent:
    """
    Create the DLQ Monitor agent
    """
    
    dlq_monitor = LlmAgent(
        name="dlq_monitor",
        model="gemini-2.0-flash",
        description="Monitors AWS SQS Dead Letter Queues for messages",
        instruction="""
        You are the DLQ Monitor Agent for the FABIO-PROD AWS account.
        
        CONTEXT:
        - AWS Profile: FABIO-PROD
        - Region: sa-east-1
        - Environment: PRODUCTION
        
        YOUR RESPONSIBILITIES:
        
        1. QUEUE DISCOVERY:
           - List all SQS queues matching DLQ patterns:
             * -dlq
             * -dead-letter
             * -deadletter
             * _dlq
             * -dl
           - Use AWS MCP server (aws-api) for SQS operations
        
        2. MESSAGE MONITORING:
           - Check ApproximateNumberOfMessages for each DLQ
           - Report any DLQ with message count > 0
           - Include queue name, URL, and exact message count
        
        3. CRITICAL DLQS:
           Pay special attention to these critical DLQs:
           - fm-digitalguru-api-update-dlq-prod
           - fm-transaction-processor-dlq-prd
           
        4. REPORTING FORMAT:
           For each DLQ with messages, report:
           {
             "queue_name": "queue-name-dlq",
             "queue_url": "https://sqs.region.amazonaws.com/account/queue",
             "message_count": 5,
             "is_critical": true/false,
             "timestamp": "2024-01-01T12:00:00Z"
           }
        
        5. MONITORING FREQUENCY:
           - Called by Coordinator every 30 seconds
           - Must complete check within 10 seconds
           - Report immediately if critical DLQ has messages
        
        AWS MCP TOOLS AVAILABLE:
        - call_aws: Execute AWS CLI commands
        - suggest_aws_commands: Get help with AWS CLI syntax
        
        SQS COMMANDS TO USE:
        - sqs list-queues --queue-name-prefix '-dlq'
        - sqs get-queue-attributes --queue-url <url> --attribute-names All
        - sqs receive-message --queue-url <url> (if detailed analysis needed)
        
        Remember: Accurate monitoring is critical for production stability.
        """,
        tools=[
            create_check_dlq_tool(),
            create_get_dlq_messages_tool()
        ]
    )
    
    return dlq_monitor

# Export the dlq_monitor
dlq_monitor = create_dlq_monitor_agent()