#!/usr/bin/env python3
"""
AWS SQS Helper Module - Implements AWS Best Practices
Provides robust SQS operations with error handling, retries, and monitoring
"""

import boto3
import logging
import time
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from datetime import datetime, timedelta
from botocore.exceptions import ClientError, NoCredentialsError, BotoCoreError
from botocore.config import Config
import json

logger = logging.getLogger(__name__)


@dataclass
class SQSQueueInfo:
    """Information about an SQS queue"""
    name: str
    url: str
    arn: str
    region: str
    account_id: str
    attributes: Dict[str, Any]
    is_dlq: bool = False
    message_count: int = 0
    messages_not_visible: int = 0
    messages_delayed: int = 0
    created_timestamp: Optional[datetime] = None
    last_modified_timestamp: Optional[datetime] = None
    redrive_policy: Optional[Dict] = None
    visibility_timeout: int = 30
    message_retention_period: int = 345600  # 4 days default
    max_message_size: int = 262144  # 256 KB default


class SQSHelper:
    """AWS SQS Helper with best practices implementation"""
    
    # AWS recommended retry configuration
    RETRY_CONFIG = Config(
        region_name='sa-east-1',
        retries={
            'max_attempts': 3,
            'mode': 'adaptive'  # Adaptive retry mode for better handling
        },
        max_pool_connections=50  # Increase connection pool for concurrent operations
    )
    
    # DLQ identification patterns
    DLQ_PATTERNS = ['-dlq', '-dead-letter', '-deadletter', '_dlq', '-dl', 'DLQ', 'DeadLetter']
    
    def __init__(self, profile: str = 'FABIO-PROD', region: str = 'sa-east-1'):
        """Initialize SQS helper with AWS best practices
        
        Args:
            profile: AWS profile to use
            region: AWS region
        """
        self.profile = profile
        self.region = region
        self.session = None
        self.sqs_client = None
        self.sts_client = None
        self.account_id = None
        self._initialize_clients()
    
    def _initialize_clients(self):
        """Initialize AWS clients with proper error handling"""
        try:
            # Create session with profile
            self.session = boto3.Session(
                profile_name=self.profile,
                region_name=self.region
            )
            
            # Initialize SQS client with retry configuration
            self.sqs_client = self.session.client('sqs', config=self.RETRY_CONFIG)
            
            # Initialize STS client for account information
            self.sts_client = self.session.client('sts', config=self.RETRY_CONFIG)
            
            # Get account ID
            response = self.sts_client.get_caller_identity()
            self.account_id = response['Account']
            
            logger.info(f"AWS SQS Helper initialized successfully")
            logger.info(f"Profile: {self.profile}, Region: {self.region}, Account: {self.account_id}")
            
        except NoCredentialsError:
            logger.error(f"AWS credentials not found for profile: {self.profile}")
            raise
        except ClientError as e:
            logger.error(f"Failed to initialize AWS clients: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error initializing AWS: {e}")
            raise
    
    def is_dlq(self, queue_name: str) -> bool:
        """Check if queue is a Dead Letter Queue
        
        Args:
            queue_name: Name of the queue
            
        Returns:
            True if queue appears to be a DLQ
        """
        return any(pattern.lower() in queue_name.lower() for pattern in self.DLQ_PATTERNS)
    
    def list_all_queues(self, prefix: Optional[str] = None) -> List[str]:
        """List all SQS queues with pagination support
        
        Args:
            prefix: Optional queue name prefix filter
            
        Returns:
            List of queue URLs
        """
        queues = []
        
        try:
            # Use paginator for handling large number of queues
            paginator = self.sqs_client.get_paginator('list_queues')
            
            # Build pagination parameters
            page_params = {}
            if prefix:
                page_params['QueueNamePrefix'] = prefix
            
            # Iterate through all pages
            for page in paginator.paginate(**page_params):
                if 'QueueUrls' in page:
                    queues.extend(page['QueueUrls'])
            
            logger.info(f"Found {len(queues)} queues")
            return queues
            
        except ClientError as e:
            error_code = e.response['Error']['Code']
            if error_code == 'AWS.SimpleQueueService.NonExistentQueue':
                logger.warning(f"No queues found with prefix: {prefix}")
                return []
            else:
                logger.error(f"Error listing queues: {e}")
                raise
        except Exception as e:
            logger.error(f"Unexpected error listing queues: {e}")
            raise
    
    def get_queue_info(self, queue_url: str) -> Optional[SQSQueueInfo]:
        """Get comprehensive queue information with error handling
        
        Args:
            queue_url: URL of the queue
            
        Returns:
            SQSQueueInfo object or None if error
        """
        try:
            # Get all queue attributes
            response = self.sqs_client.get_queue_attributes(
                QueueUrl=queue_url,
                AttributeNames=['All']
            )
            
            attributes = response.get('Attributes', {})
            queue_name = queue_url.split('/')[-1]
            
            # Parse timestamps
            created_timestamp = None
            if 'CreatedTimestamp' in attributes:
                created_timestamp = datetime.fromtimestamp(int(attributes['CreatedTimestamp']))
            
            last_modified = None
            if 'LastModifiedTimestamp' in attributes:
                last_modified = datetime.fromtimestamp(int(attributes['LastModifiedTimestamp']))
            
            # Parse redrive policy if exists
            redrive_policy = None
            if 'RedrivePolicy' in attributes:
                try:
                    redrive_policy = json.loads(attributes['RedrivePolicy'])
                except json.JSONDecodeError:
                    logger.warning(f"Failed to parse redrive policy for {queue_name}")
            
            # Create queue info object
            queue_info = SQSQueueInfo(
                name=queue_name,
                url=queue_url,
                arn=attributes.get('QueueArn', ''),
                region=self.region,
                account_id=self.account_id,
                attributes=attributes,
                is_dlq=self.is_dlq(queue_name),
                message_count=int(attributes.get('ApproximateNumberOfMessages', '0')),
                messages_not_visible=int(attributes.get('ApproximateNumberOfMessagesNotVisible', '0')),
                messages_delayed=int(attributes.get('ApproximateNumberOfMessagesDelayed', '0')),
                created_timestamp=created_timestamp,
                last_modified_timestamp=last_modified,
                redrive_policy=redrive_policy,
                visibility_timeout=int(attributes.get('VisibilityTimeout', '30')),
                message_retention_period=int(attributes.get('MessageRetentionPeriod', '345600')),
                max_message_size=int(attributes.get('MaximumMessageSize', '262144'))
            )
            
            return queue_info
            
        except ClientError as e:
            error_code = e.response['Error']['Code']
            if error_code == 'AWS.SimpleQueueService.NonExistentQueue':
                logger.warning(f"Queue no longer exists: {queue_url}")
                return None
            else:
                logger.error(f"Error getting queue attributes for {queue_url}: {e}")
                return None
        except Exception as e:
            logger.error(f"Unexpected error getting queue info: {e}")
            return None
    
    def list_dlq_queues(self) -> List[SQSQueueInfo]:
        """List all Dead Letter Queues with detailed information
        
        Returns:
            List of SQSQueueInfo objects for DLQs
        """
        dlqs = []
        
        try:
            # Get all queues
            all_queues = self.list_all_queues()
            
            # Process each queue
            for queue_url in all_queues:
                queue_name = queue_url.split('/')[-1]
                
                # Check if it's a DLQ
                if self.is_dlq(queue_name):
                    queue_info = self.get_queue_info(queue_url)
                    if queue_info:
                        dlqs.append(queue_info)
            
            # Sort by message count (highest first)
            dlqs.sort(key=lambda x: x.message_count, reverse=True)
            
            logger.info(f"Found {len(dlqs)} DLQ queues")
            for dlq in dlqs:
                if dlq.message_count > 0:
                    logger.warning(f"DLQ {dlq.name}: {dlq.message_count} messages")
            
            return dlqs
            
        except Exception as e:
            logger.error(f"Error listing DLQ queues: {e}")
            return []
    
    def receive_messages(self, queue_url: str, max_messages: int = 10, 
                        visibility_timeout: int = 30, wait_time: int = 0) -> List[Dict]:
        """Receive messages from queue with best practices
        
        Args:
            queue_url: URL of the queue
            max_messages: Maximum messages to receive (1-10)
            visibility_timeout: Message visibility timeout in seconds
            wait_time: Long polling wait time in seconds (0-20)
            
        Returns:
            List of message dictionaries
        """
        try:
            # Validate parameters
            max_messages = min(max(1, max_messages), 10)  # AWS limit is 10
            wait_time = min(max(0, wait_time), 20)  # AWS limit is 20
            
            response = self.sqs_client.receive_message(
                QueueUrl=queue_url,
                MaxNumberOfMessages=max_messages,
                VisibilityTimeout=visibility_timeout,
                WaitTimeSeconds=wait_time,  # Long polling for efficiency
                AttributeNames=['All'],
                MessageAttributeNames=['All']
            )
            
            messages = response.get('Messages', [])
            logger.info(f"Received {len(messages)} messages from queue")
            
            return messages
            
        except ClientError as e:
            logger.error(f"Error receiving messages: {e}")
            return []
        except Exception as e:
            logger.error(f"Unexpected error receiving messages: {e}")
            return []
    
    def delete_message(self, queue_url: str, receipt_handle: str) -> bool:
        """Delete a message from queue
        
        Args:
            queue_url: URL of the queue
            receipt_handle: Message receipt handle
            
        Returns:
            True if successful
        """
        try:
            self.sqs_client.delete_message(
                QueueUrl=queue_url,
                ReceiptHandle=receipt_handle
            )
            logger.debug(f"Message deleted successfully")
            return True
            
        except ClientError as e:
            logger.error(f"Error deleting message: {e}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error deleting message: {e}")
            return False
    
    def delete_message_batch(self, queue_url: str, messages: List[Dict]) -> Dict[str, List]:
        """Delete messages in batch for efficiency
        
        Args:
            queue_url: URL of the queue
            messages: List of message dictionaries with ReceiptHandle
            
        Returns:
            Dictionary with 'successful' and 'failed' lists
        """
        result = {'successful': [], 'failed': []}
        
        try:
            # Process in batches of 10 (AWS limit)
            for i in range(0, len(messages), 10):
                batch = messages[i:i+10]
                
                # Prepare batch entries
                entries = [
                    {
                        'Id': str(idx),
                        'ReceiptHandle': msg['ReceiptHandle']
                    }
                    for idx, msg in enumerate(batch)
                ]
                
                # Delete batch
                response = self.sqs_client.delete_message_batch(
                    QueueUrl=queue_url,
                    Entries=entries
                )
                
                # Process results
                result['successful'].extend(response.get('Successful', []))
                result['failed'].extend(response.get('Failed', []))
            
            logger.info(f"Batch delete: {len(result['successful'])} successful, {len(result['failed'])} failed")
            
        except ClientError as e:
            logger.error(f"Error in batch delete: {e}")
        except Exception as e:
            logger.error(f"Unexpected error in batch delete: {e}")
        
        return result
    
    def purge_queue(self, queue_url: str, confirm: bool = False) -> bool:
        """Purge all messages from queue (use with caution!)
        
        Args:
            queue_url: URL of the queue
            confirm: Safety confirmation flag
            
        Returns:
            True if successful
        """
        if not confirm:
            logger.warning("Queue purge not confirmed - skipping")
            return False
        
        try:
            queue_name = queue_url.split('/')[-1]
            logger.warning(f"PURGING QUEUE: {queue_name}")
            
            self.sqs_client.purge_queue(QueueUrl=queue_url)
            
            logger.info(f"Queue {queue_name} purged successfully")
            return True
            
        except ClientError as e:
            error_code = e.response['Error']['Code']
            if error_code == 'AWS.SimpleQueueService.PurgeQueueInProgress':
                logger.warning("Queue purge already in progress")
                return False
            else:
                logger.error(f"Error purging queue: {e}")
                return False
        except Exception as e:
            logger.error(f"Unexpected error purging queue: {e}")
            return False
    
    def get_queue_metrics(self, queue_info: SQSQueueInfo) -> Dict[str, Any]:
        """Get queue metrics for monitoring
        
        Args:
            queue_info: SQSQueueInfo object
            
        Returns:
            Dictionary of metrics
        """
        metrics = {
            'queue_name': queue_info.name,
            'region': queue_info.region,
            'account_id': queue_info.account_id,
            'is_dlq': queue_info.is_dlq,
            'message_count': queue_info.message_count,
            'messages_not_visible': queue_info.messages_not_visible,
            'messages_delayed': queue_info.messages_delayed,
            'total_messages': (queue_info.message_count + 
                             queue_info.messages_not_visible + 
                             queue_info.messages_delayed),
            'age_hours': None,
            'has_redrive_policy': queue_info.redrive_policy is not None,
            'visibility_timeout': queue_info.visibility_timeout,
            'retention_days': queue_info.message_retention_period / 86400
        }
        
        # Calculate queue age
        if queue_info.created_timestamp:
            age = datetime.now() - queue_info.created_timestamp
            metrics['age_hours'] = age.total_seconds() / 3600
        
        return metrics
    
    def monitor_dlqs(self, callback=None) -> List[Dict[str, Any]]:
        """Monitor all DLQs and return alerts
        
        Args:
            callback: Optional callback function for each DLQ with messages
            
        Returns:
            List of alert dictionaries
        """
        alerts = []
        
        try:
            dlqs = self.list_dlq_queues()
            
            for dlq in dlqs:
                if dlq.message_count > 0:
                    # Create alert
                    alert = {
                        'timestamp': datetime.now().isoformat(),
                        'queue_name': dlq.name,
                        'queue_url': dlq.url,
                        'message_count': dlq.message_count,
                        'region': dlq.region,
                        'account_id': dlq.account_id,
                        'metrics': self.get_queue_metrics(dlq)
                    }
                    alerts.append(alert)
                    
                    # Call callback if provided
                    if callback:
                        try:
                            callback(alert)
                        except Exception as e:
                            logger.error(f"Callback error: {e}")
            
            return alerts
            
        except Exception as e:
            logger.error(f"Error monitoring DLQs: {e}")
            return alerts


# Export the helper class
__all__ = ['SQSHelper', 'SQSQueueInfo']