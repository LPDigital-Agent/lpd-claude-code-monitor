"""Mock AWS services for testing."""

from typing import Dict, List, Any
from unittest.mock import Mock, MagicMock


class MockSQSClient:
    """Mock SQS client for testing."""
    
    def __init__(self):
        self.queues = {}
        self.messages = {}
    
    def list_queues(self, QueueNamePrefix: str = None) -> Dict[str, List[str]]:
        """Mock list_queues operation."""
        queue_urls = list(self.queues.values())
        
        if QueueNamePrefix:
            queue_urls = [url for url in queue_urls 
                         if QueueNamePrefix in url.split('/')[-1]]
        
        return {'QueueUrls': queue_urls}
    
    def get_queue_attributes(self, QueueUrl: str, AttributeNames: List[str]) -> Dict[str, Dict[str, str]]:
        """Mock get_queue_attributes operation."""
        queue_name = QueueUrl.split('/')[-1]
        message_count = len(self.messages.get(queue_name, []))
        
        attributes = {
            'ApproximateNumberOfMessages': str(message_count),
            'ApproximateNumberOfMessagesNotVisible': '0',
            'ApproximateNumberOfMessagesDelayed': '0',
            'CreatedTimestamp': '1704110400',
            'LastModifiedTimestamp': '1704110400',
            'QueueArn': f'arn:aws:sqs:us-east-1:123456789012:{queue_name}',
            'ReceiveMessageWaitTimeSeconds': '0',
            'VisibilityTimeoutSeconds': '30'
        }
        
        return {'Attributes': attributes}
    
    def create_queue(self, QueueName: str) -> Dict[str, str]:
        """Mock create_queue operation."""
        queue_url = f'https://sqs.us-east-1.amazonaws.com/123456789012/{QueueName}'
        self.queues[QueueName] = queue_url
        self.messages[QueueName] = []
        return {'QueueUrl': queue_url}
    
    def send_message(self, QueueUrl: str, MessageBody: str, **kwargs) -> Dict[str, str]:
        """Mock send_message operation."""
        queue_name = QueueUrl.split('/')[-1]
        if queue_name not in self.messages:
            self.messages[queue_name] = []
        
        message = {
            'MessageId': f'msg-{len(self.messages[queue_name]) + 1:03d}',
            'Body': MessageBody,
            'Attributes': kwargs.get('MessageAttributes', {})
        }
        
        self.messages[queue_name].append(message)
        return {'MessageId': message['MessageId']}
    
    def receive_message(self, QueueUrl: str, MaxNumberOfMessages: int = 1, **kwargs) -> Dict[str, List]:
        """Mock receive_message operation."""
        queue_name = QueueUrl.split('/')[-1]
        messages = self.messages.get(queue_name, [])
        
        if not messages:
            return {'Messages': []}
        
        return {'Messages': messages[:MaxNumberOfMessages]}


class MockBoto3Session:
    """Mock boto3 Session for testing."""
    
    def __init__(self, profile_name: str = None, region_name: str = None):
        self.profile_name = profile_name
        self.region_name = region_name
        self._clients = {}
    
    def client(self, service_name: str, **kwargs):
        """Mock client creation."""
        if service_name == 'sqs':
            if 'sqs' not in self._clients:
                self._clients['sqs'] = MockSQSClient()
            return self._clients['sqs']
        
        # Return a generic mock for other services
        return Mock()
    
    def get_available_regions(self, service_name: str) -> List[str]:
        """Mock get_available_regions."""
        return ['us-east-1', 'us-west-2', 'eu-west-1', 'sa-east-1']


class MockCloudWatchClient:
    """Mock CloudWatch client for testing."""
    
    def __init__(self):
        self.metrics = []
    
    def put_metric_data(self, Namespace: str, MetricData: List[Dict]) -> Dict:
        """Mock put_metric_data operation."""
        for metric in MetricData:
            self.metrics.append(metric)
        return {}
    
    def get_metric_statistics(self, **kwargs) -> Dict[str, List]:
        """Mock get_metric_statistics operation."""
        # Return sample metric data
        return {
            'Datapoints': [
                {
                    'Timestamp': '2024-01-01T10:00:00Z',
                    'Sum': 5.0,
                    'Average': 2.5,
                    'Maximum': 5.0,
                    'Minimum': 1.0
                }
            ]
        }