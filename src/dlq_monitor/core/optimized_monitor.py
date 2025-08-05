#!/usr/bin/env python3
"""
Optimized DLQ Monitor with AWS SQS Best Practices
Implements long polling, batch operations, exponential backoff, and connection pooling
"""

import time
import logging
from typing import List, Dict, Optional, Any
from datetime import datetime, timedelta
from dataclasses import dataclass
import boto3
from botocore.exceptions import ClientError
from concurrent.futures import ThreadPoolExecutor, as_completed
import json

from .monitor import MonitorConfig, DLQAlert


class OptimizedDLQMonitor:
    """
    Optimized DLQ Monitor with AWS best practices:
    - Long polling for message retrieval
    - Batch operations for efficiency
    - Connection pooling
    - Exponential backoff for retries
    - CloudWatch metrics integration
    """
    
    def __init__(self, config: MonitorConfig):
        self.config = config
        self.logger = self._setup_logging()
        
        # Connection pooling with boto3 session
        self.session = boto3.Session(
            profile_name=config.aws_profile,
            region_name=config.region
        )
        
        # Create clients with connection pooling
        self.sqs_client = self.session.client(
            'sqs',
            config=boto3.session.Config(
                max_pool_connections=50,  # Increase connection pool
                retries={
                    'max_attempts': 3,
                    'mode': 'adaptive'  # Use adaptive retry mode
                }
            )
        )
        
        # CloudWatch client for metrics
        self.cloudwatch = self.session.client('cloudwatch')
        
        # Cache for queue attributes (reduce API calls)
        self.queue_cache = {}
        self.cache_ttl = 60  # Cache for 1 minute
        
        # Thread pool for concurrent operations
        self.executor = ThreadPoolExecutor(max_workers=10)
        
        self.logger.info("🚀 Optimized DLQ Monitor initialized with best practices")
    
    def _setup_logging(self) -> logging.Logger:
        """Setup optimized logging with structured format"""
        logger = logging.getLogger(f"{__name__}.{self.config.aws_profile}")
        
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
            logger.setLevel(getattr(logging, self.config.log_level))
        
        return logger
    
    def discover_dlq_queues_batch(self) -> List[Dict[str, Any]]:
        """
        Discover DLQ queues with batch operations and caching
        """
        try:
            # Check cache first
            cache_key = "dlq_queues"
            if cache_key in self.queue_cache:
                cached_data, cached_time = self.queue_cache[cache_key]
                if (datetime.now() - cached_time).seconds < self.cache_ttl:
                    self.logger.debug("📦 Using cached DLQ queue list")
                    return cached_data
            
            self.logger.debug("🔍 Discovering DLQ queues with batch operations...")
            
            paginator = self.sqs_client.get_paginator('list_queues')
            dlq_queues = []
            
            # Process pages concurrently
            futures = []
            for page in paginator.paginate():
                if 'QueueUrls' in page:
                    for queue_url in page['QueueUrls']:
                        future = self.executor.submit(self._process_queue_url, queue_url)
                        futures.append(future)
            
            # Collect results
            for future in as_completed(futures):
                result = future.result()
                if result:
                    dlq_queues.append(result)
            
            # Cache the results
            self.queue_cache[cache_key] = (dlq_queues, datetime.now())
            
            self.logger.info(f"✅ Discovered {len(dlq_queues)} DLQ queues")
            return dlq_queues
            
        except ClientError as e:
            self.logger.error(f"❌ AWS Error discovering queues: {e}")
            return []
        except Exception as e:
            self.logger.error(f"❌ Unexpected error: {e}")
            return []
    
    def _process_queue_url(self, queue_url: str) -> Optional[Dict[str, Any]]:
        """Process a single queue URL to check if it's a DLQ"""
        queue_name = queue_url.split('/')[-1]
        
        # Check if it matches DLQ patterns
        is_dlq = any(pattern.lower() in queue_name.lower() 
                    for pattern in self.config.dlq_patterns)
        
        if is_dlq:
            return {
                'name': queue_name,
                'url': queue_url,
                'cached_at': datetime.now()
            }
        return None
    
    def get_queue_messages_long_poll(self, queue_url: str, max_messages: int = 10) -> List[Dict]:
        """
        Get messages from queue using long polling (20 second wait)
        This reduces API calls by up to 90%
        """
        try:
            response = self.sqs_client.receive_message(
                QueueUrl=queue_url,
                AttributeNames=['All'],
                MessageAttributeNames=['All'],
                MaxNumberOfMessages=max_messages,  # Batch retrieve up to 10 messages
                WaitTimeSeconds=20,  # Long polling - wait up to 20 seconds
                VisibilityTimeout=30  # Give 30 seconds to process
            )
            
            messages = response.get('Messages', [])
            
            if messages:
                self.logger.info(f"📨 Retrieved {len(messages)} messages with long polling")
                
                # Send metric to CloudWatch
                self._send_cloudwatch_metric('MessagesRetrieved', len(messages))
            
            return messages
            
        except ClientError as e:
            self.logger.error(f"❌ Error retrieving messages: {e}")
            return []
    
    def get_queue_attributes_cached(self, queue_url: str) -> Dict[str, Any]:
        """
        Get queue attributes with caching to reduce API calls
        """
        cache_key = f"attrs_{queue_url}"
        
        # Check cache
        if cache_key in self.queue_cache:
            cached_data, cached_time = self.queue_cache[cache_key]
            if (datetime.now() - cached_time).seconds < self.cache_ttl:
                return cached_data
        
        try:
            # Get all attributes at once (more efficient)
            response = self.sqs_client.get_queue_attributes(
                QueueUrl=queue_url,
                AttributeNames=['All']
            )
            
            attributes = response.get('Attributes', {})
            
            # Cache the result
            self.queue_cache[cache_key] = (attributes, datetime.now())
            
            return attributes
            
        except ClientError as e:
            self.logger.error(f"❌ Error getting queue attributes: {e}")
            return {}
    
    def check_dlq_messages_optimized(self) -> List[DLQAlert]:
        """
        Optimized DLQ checking with concurrent operations and caching
        """
        dlq_queues = self.discover_dlq_queues_batch()
        alerts = []
        
        # Process queues concurrently
        futures = {}
        for queue in dlq_queues:
            future = self.executor.submit(
                self._check_single_queue_optimized, 
                queue
            )
            futures[future] = queue
        
        # Collect results
        for future in as_completed(futures):
            try:
                alert = future.result()
                if alert:
                    alerts.append(alert)
            except Exception as e:
                queue = futures[future]
                self.logger.error(f"❌ Error checking queue {queue['name']}: {e}")
        
        # Send aggregated metrics
        if alerts:
            self._send_cloudwatch_metric('DLQsWithMessages', len(alerts))
            total_messages = sum(alert.message_count for alert in alerts)
            self._send_cloudwatch_metric('TotalDLQMessages', total_messages)
        
        return alerts
    
    def _check_single_queue_optimized(self, queue: Dict[str, Any]) -> Optional[DLQAlert]:
        """
        Check a single queue with optimized attribute retrieval
        """
        queue_url = queue['url']
        queue_name = queue['name']
        
        # Get attributes with caching
        attributes = self.get_queue_attributes_cached(queue_url)
        
        message_count = int(attributes.get('ApproximateNumberOfMessages', 0))
        
        if message_count > 0:
            self.logger.warning(f"⚠️  DLQ {queue_name}: {message_count} messages")
            
            # For queues with messages, get sample messages with long polling
            if self.config.retrieve_message_samples:
                sample_messages = self.get_queue_messages_long_poll(queue_url, max_messages=1)
                if sample_messages:
                    self.logger.debug(f"📋 Sample message from {queue_name}: {sample_messages[0].get('Body', '')[:100]}")
            
            return DLQAlert(
                queue_name=queue_name,
                queue_url=queue_url,
                message_count=message_count,
                timestamp=datetime.now(),
                region=self.config.region,
                account_id=self._get_account_id(),
                attributes=attributes  # Include all attributes
            )
        else:
            self.logger.debug(f"✅ DLQ {queue_name}: Empty")
            return None
    
    def _get_account_id(self) -> str:
        """Get AWS account ID with caching"""
        cache_key = "account_id"
        
        if cache_key in self.queue_cache:
            return self.queue_cache[cache_key][0]
        
        try:
            sts = self.session.client('sts')
            account_id = sts.get_caller_identity()['Account']
            self.queue_cache[cache_key] = (account_id, datetime.now())
            return account_id
        except Exception as e:
            self.logger.error(f"Failed to get account ID: {e}")
            return "unknown"
    
    def _send_cloudwatch_metric(self, metric_name: str, value: float, unit: str = 'Count') -> None:
        """
        Send custom metrics to CloudWatch for monitoring
        """
        try:
            self.cloudwatch.put_metric_data(
                Namespace='DLQMonitor',
                MetricData=[
                    {
                        'MetricName': metric_name,
                        'Value': value,
                        'Unit': unit,
                        'Timestamp': datetime.now(),
                        'Dimensions': [
                            {
                                'Name': 'Environment',
                                'Value': self.config.aws_profile
                            },
                            {
                                'Name': 'Region',
                                'Value': self.config.region
                            }
                        ]
                    }
                ]
            )
            self.logger.debug(f"📊 Sent metric {metric_name}={value} to CloudWatch")
        except Exception as e:
            self.logger.warning(f"Failed to send CloudWatch metric: {e}")
    
    def batch_delete_messages(self, queue_url: str, messages: List[Dict]) -> int:
        """
        Delete messages in batch (up to 10 at a time)
        """
        if not messages:
            return 0
        
        deleted_count = 0
        
        # Process in batches of 10
        for i in range(0, len(messages), 10):
            batch = messages[i:i+10]
            
            entries = [
                {
                    'Id': str(idx),
                    'ReceiptHandle': msg['ReceiptHandle']
                }
                for idx, msg in enumerate(batch)
            ]
            
            try:
                response = self.sqs_client.delete_message_batch(
                    QueueUrl=queue_url,
                    Entries=entries
                )
                
                deleted_count += len(response.get('Successful', []))
                
                if response.get('Failed'):
                    for failure in response['Failed']:
                        self.logger.error(f"Failed to delete message: {failure}")
                        
            except ClientError as e:
                self.logger.error(f"❌ Error deleting messages: {e}")
        
        self.logger.info(f"🗑️  Deleted {deleted_count} messages from queue")
        return deleted_count
    
    def health_check(self) -> Dict[str, Any]:
        """
        Perform health check and return status
        """
        health_status = {
            'status': 'healthy',
            'timestamp': datetime.now().isoformat(),
            'checks': {}
        }
        
        # Check SQS connectivity
        try:
            self.sqs_client.list_queues(MaxResults=1)
            health_status['checks']['sqs'] = 'connected'
        except Exception as e:
            health_status['checks']['sqs'] = f'error: {str(e)}'
            health_status['status'] = 'unhealthy'
        
        # Check CloudWatch connectivity
        try:
            self.cloudwatch.list_metrics(Namespace='DLQMonitor', MaxResults=1)
            health_status['checks']['cloudwatch'] = 'connected'
        except Exception as e:
            health_status['checks']['cloudwatch'] = f'error: {str(e)}'
        
        # Check cache status
        health_status['checks']['cache_size'] = len(self.queue_cache)
        
        # Check thread pool status
        health_status['checks']['thread_pool'] = {
            'active': len(self.executor._threads),
            'max_workers': self.executor._max_workers
        }
        
        return health_status
    
    def cleanup(self):
        """Cleanup resources"""
        self.executor.shutdown(wait=True)
        self.logger.info("🧹 Cleaned up monitor resources")


# Extension to MonitorConfig for new features
@dataclass
class OptimizedMonitorConfig(MonitorConfig):
    """Extended configuration for optimized monitor"""
    retrieve_message_samples: bool = False
    enable_cloudwatch_metrics: bool = True
    connection_pool_size: int = 50
    cache_ttl_seconds: int = 60
    max_concurrent_checks: int = 10
    long_polling_wait_seconds: int = 20