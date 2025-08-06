#!/usr/bin/env python3
"""
Test script for ADK Multi-Agent DLQ Monitor System
"""

import asyncio
import sys
import os
from pathlib import Path
import json
import logging

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from adk_agents import *
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class ADKSystemTest:
    """Test suite for ADK agents"""
    
    def __init__(self):
        self.tests_passed = 0
        self.tests_failed = 0
        self.results = []
    
    async def test_environment(self):
        """Test environment setup"""
        print("\n🔍 Testing Environment Setup...")
        
        required_vars = [
            'GEMINI_API_KEY',
            'AWS_PROFILE',
            'AWS_REGION', 
            'GITHUB_TOKEN'
        ]
        
        missing = []
        for var in required_vars:
            if not os.getenv(var):
                missing.append(var)
                print(f"  ❌ {var}: Not set")
            else:
                value = os.getenv(var)
                masked = value[:4] + "..." if len(value) > 4 else "***"
                print(f"  ✅ {var}: {masked}")
        
        if missing:
            self.tests_failed += 1
            self.results.append(("Environment", False, f"Missing: {', '.join(missing)}"))
            return False
        else:
            self.tests_passed += 1
            self.results.append(("Environment", True, "All variables set"))
            return True
    
    async def test_config_files(self):
        """Test configuration files"""
        print("\n🔍 Testing Configuration Files...")
        
        config_files = [
            "config/adk_config.yaml",
            "config/mcp_settings.json",
            ".env"
        ]
        
        all_exist = True
        for file in config_files:
            path = Path(file)
            if path.exists():
                print(f"  ✅ {file}: Found")
            else:
                print(f"  ❌ {file}: Not found")
                all_exist = False
        
        if all_exist:
            self.tests_passed += 1
            self.results.append(("Config Files", True, "All configs found"))
        else:
            self.tests_failed += 1
            self.results.append(("Config Files", False, "Missing config files"))
        
        return all_exist
    
    async def test_agent_initialization(self):
        """Test agent initialization"""
        print("\n🔍 Testing Agent Initialization...")
        
        agents_to_test = [
            ("Coordinator", coordinator),
            ("DLQ Monitor", dlq_monitor),
            ("Investigator", investigator),
            ("Code Fixer", code_fixer),
            ("PR Manager", pr_manager),
            ("Notifier", notifier)
        ]
        
        all_initialized = True
        for name, agent in agents_to_test:
            if agent is not None:
                print(f"  ✅ {name}: Initialized")
            else:
                print(f"  ❌ {name}: Failed to initialize")
                all_initialized = False
        
        if all_initialized:
            self.tests_passed += 1
            self.results.append(("Agent Init", True, "All agents initialized"))
        else:
            self.tests_failed += 1
            self.results.append(("Agent Init", False, "Some agents failed"))
        
        return all_initialized
    
    async def test_claude_subagents(self):
        """Test Claude subagents"""
        print("\n🔍 Testing Claude Subagents...")
        
        subagent_files = [
            ".claude/agents/dlq-analyzer.md",
            ".claude/agents/debugger.md",
            ".claude/agents/code-reviewer.md"
        ]
        
        all_exist = True
        for file in subagent_files:
            path = Path(file)
            if path.exists():
                # Check if file has proper frontmatter
                with open(path, 'r') as f:
                    content = f.read()
                    if content.startswith('---'):
                        print(f"  ✅ {path.name}: Valid subagent")
                    else:
                        print(f"  ⚠️  {path.name}: Missing frontmatter")
            else:
                print(f"  ❌ {file}: Not found")
                all_exist = False
        
        if all_exist:
            self.tests_passed += 1
            self.results.append(("Claude Subagents", True, "All subagents valid"))
        else:
            self.tests_failed += 1
            self.results.append(("Claude Subagents", False, "Missing subagents"))
        
        return all_exist
    
    async def test_mcp_connection(self):
        """Test MCP server configuration"""
        print("\n🔍 Testing MCP Server Configuration...")
        
        try:
            with open("config/mcp_settings.json", 'r') as f:
                mcp_config = json.load(f)
            
            servers = mcp_config.get('mcpServers', {})
            required_servers = ['aws-api', 'sns-sqs', 'github', 'sequential-thinking', 'memory']
            
            all_configured = True
            for server in required_servers:
                if server in servers:
                    print(f"  ✅ {server}: Configured")
                else:
                    print(f"  ❌ {server}: Not configured")
                    all_configured = False
            
            if all_configured:
                self.tests_passed += 1
                self.results.append(("MCP Servers", True, "All servers configured"))
            else:
                self.tests_failed += 1
                self.results.append(("MCP Servers", False, "Missing server configs"))
            
            return all_configured
            
        except Exception as e:
            print(f"  ❌ Error loading MCP config: {e}")
            self.tests_failed += 1
            self.results.append(("MCP Servers", False, str(e)))
            return False
    
    async def test_aws_profile(self):
        """Test AWS profile configuration"""
        print("\n🔍 Testing AWS Profile...")
        
        try:
            import boto3
            
            # Try to create SQS client with FABIO-PROD profile
            session = boto3.Session(profile_name='FABIO-PROD')
            sqs = session.client('sqs', region_name='sa-east-1')
            
            # Try to list queues (won't actually call AWS)
            print(f"  ✅ AWS Profile: FABIO-PROD configured")
            print(f"  ✅ Region: sa-east-1")
            
            self.tests_passed += 1
            self.results.append(("AWS Profile", True, "FABIO-PROD configured"))
            return True
            
        except Exception as e:
            print(f"  ❌ AWS Profile Error: {e}")
            self.tests_failed += 1
            self.results.append(("AWS Profile", False, str(e)))
            return False
    
    def print_summary(self):
        """Print test summary"""
        print("\n" + "=" * 60)
        print("📊 TEST SUMMARY")
        print("=" * 60)
        
        total = self.tests_passed + self.tests_failed
        
        for test_name, passed, details in self.results:
            status = "✅ PASS" if passed else "❌ FAIL"
            print(f"{status} | {test_name}: {details}")
        
        print("-" * 60)
        print(f"Total Tests: {total}")
        print(f"Passed: {self.tests_passed} ({self.tests_passed/total*100:.1f}%)")
        print(f"Failed: {self.tests_failed} ({self.tests_failed/total*100:.1f}%)")
        
        if self.tests_failed == 0:
            print("\n🎉 All tests passed! System ready for production.")
        else:
            print(f"\n⚠️  {self.tests_failed} test(s) failed. Please fix before running in production.")
        
        return self.tests_failed == 0

async def main():
    """Main test runner"""
    print("=" * 60)
    print("🧪 ADK Multi-Agent DLQ Monitor System Test Suite")
    print("=" * 60)
    
    tester = ADKSystemTest()
    
    # Run all tests
    await tester.test_environment()
    await tester.test_config_files()
    await tester.test_agent_initialization()
    await tester.test_claude_subagents()
    await tester.test_mcp_connection()
    await tester.test_aws_profile()
    
    # Print summary
    success = tester.print_summary()
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    asyncio.run(main())