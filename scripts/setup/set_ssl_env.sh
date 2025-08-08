#!/bin/bash

# Set SSL certificate bundle for AWS SDK
export AWS_CA_BUNDLE='/Users/fabio.santos/.pyenv/versions/3.11.10/lib/python3.11/site-packages/certifi/cacert.pem'
export REQUESTS_CA_BUNDLE='/Users/fabio.santos/.pyenv/versions/3.11.10/lib/python3.11/site-packages/certifi/cacert.pem'

# AWS Configuration
export AWS_PROFILE=FABIO-PROD
export AWS_REGION=sa-east-1

# Suppress Python warnings
export PYTHONWARNINGS="ignore"

echo "✅ Environment configured!"
echo "   AWS_CA_BUNDLE: $AWS_CA_BUNDLE"
echo "   AWS_PROFILE: $AWS_PROFILE"
echo "   AWS_REGION: $AWS_REGION"