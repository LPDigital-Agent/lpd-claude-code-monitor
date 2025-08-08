#!/usr/bin/env python3
"""
Fix SSL certificate validation issues for AWS SDK.
This script configures boto3 to use the correct certificate bundle.
"""

import os
import ssl
import boto3
import certifi
from botocore.config import Config

def test_aws_connection():
    """Test AWS SQS connection with proper SSL configuration."""
    
    # Set the certificate bundle path
    os.environ['AWS_CA_BUNDLE'] = certifi.where()
    
    # Alternative: Set requests certificate bundle
    os.environ['REQUESTS_CA_BUNDLE'] = certifi.where()
    
    # Configure boto3 with custom settings
    config = Config(
        region_name='sa-east-1',
        signature_version='v4',
        retries={
            'max_attempts': 3,
            'mode': 'standard'
        }
    )
    
    try:
        # Create SQS client with custom config
        session = boto3.Session(profile_name='FABIO-PROD')
        sqs = session.client('sqs', config=config)
        
        # Test the connection
        print("🔍 Testing AWS SQS connection...")
        response = sqs.list_queues(MaxResults=1)
        print("✅ AWS connection successful!")
        print(f"   Certificate bundle: {certifi.where()}")
        
        # List DLQs
        if 'QueueUrls' in response:
            dlq_response = sqs.list_queues(QueueNamePrefix='dlq')
            if 'QueueUrls' in dlq_response:
                print(f"\n📊 Found {len(dlq_response['QueueUrls'])} DLQ(s)")
                for queue_url in dlq_response['QueueUrls'][:5]:  # Show first 5
                    queue_name = queue_url.split('/')[-1]
                    print(f"   - {queue_name}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        print("\n🔧 Troubleshooting steps:")
        print("1. Install/update certifi: pip install --upgrade certifi")
        print("2. Update boto3: pip install --upgrade boto3")
        print("3. Check AWS credentials: aws configure list")
        print("4. Set environment variable: export AWS_CA_BUNDLE=$(python3 -m certifi)")
        return False

if __name__ == "__main__":
    # Print environment info
    print("📋 Environment Information:")
    print(f"   Python SSL cert file: {ssl.get_default_verify_paths().cafile}")
    print(f"   Certifi bundle: {certifi.where()}")
    print(f"   AWS Profile: {os.environ.get('AWS_PROFILE', 'default')}")
    print(f"   AWS Region: {os.environ.get('AWS_REGION', 'sa-east-1')}")
    print()
    
    # Test the connection
    test_aws_connection()
    
    # Export the fix
    print("\n💡 To fix SSL issues, add this to your shell:")
    print(f"export AWS_CA_BUNDLE='{certifi.where()}'")
    print(f"export REQUESTS_CA_BUNDLE='{certifi.where()}'")