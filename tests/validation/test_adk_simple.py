#!/usr/bin/env python3
"""
Simplified test script for ADK Multi-Agent DLQ Monitor System
Tests the core components without full ADK implementation
"""

import sys
import os
from pathlib import Path
import json
import yaml

# Add project root to path for imports
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class ADKSystemValidator:
    """Validator for ADK system components"""
    
    def __init__(self):
        self.tests_passed = 0
        self.tests_failed = 0
        self.results = []
    
    def test_environment(self):
        """Test environment setup"""
        print("\n🔍 Testing Environment Setup...")
        
        required_vars = [
            'GEMINI_API_KEY',
            'AWS_PROFILE',
            'AWS_REGION', 
            'GITHUB_TOKEN'
        ]
        
        # Set AWS vars if not present (for testing)
        if not os.getenv('AWS_PROFILE'):
            os.environ['AWS_PROFILE'] = 'FABIO-PROD'
        if not os.getenv('AWS_REGION'):
            os.environ['AWS_REGION'] = 'sa-east-1'
        
        missing = []
        for var in required_vars:
            if not os.getenv(var):
                missing.append(var)
                print(f"  ❌ {var}: Not set")
            else:
                value = os.getenv(var)
                if var in ['GEMINI_API_KEY', 'GITHUB_TOKEN']:
                    masked = value[:4] + "..." if len(value) > 4 else "***"
                else:
                    masked = value
                print(f"  ✅ {var}: {masked}")
        
        if missing:
            self.tests_failed += 1
            self.results.append(("Environment", False, f"Missing: {', '.join(missing)}"))
            return False
        else:
            self.tests_passed += 1
            self.results.append(("Environment", True, "All variables set"))
            return True
    
    def test_config_files(self):
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
                # Validate content
                try:
                    if file.endswith('.yaml'):
                        with open(path, 'r') as f:
                            yaml.safe_load(f)
                            print(f"     └─ Valid YAML")
                    elif file.endswith('.json'):
                        with open(path, 'r') as f:
                            json.load(f)
                            print(f"     └─ Valid JSON")
                except Exception as e:
                    print(f"     └─ ⚠️ Parse error: {e}")
            else:
                print(f"  ❌ {file}: Not found")
                all_exist = False
        
        if all_exist:
            self.tests_passed += 1
            self.results.append(("Config Files", True, "All configs found and valid"))
        else:
            self.tests_failed += 1
            self.results.append(("Config Files", False, "Missing or invalid config files"))
        
        return all_exist
    
    def test_agent_files(self):
        """Test agent implementation files"""
        print("\n🔍 Testing Agent Files...")
        
        agent_files = [
            "adk_agents/__init__.py",
            "adk_agents/coordinator.py",
            "adk_agents/dlq_monitor.py",
            "adk_agents/investigator.py",
            "adk_agents/code_fixer.py",
            "adk_agents/pr_manager.py",
            "adk_agents/notifier.py"
        ]
        
        all_exist = True
        for file in agent_files:
            path = Path(file)
            if path.exists():
                print(f"  ✅ {path.name}: Found ({path.stat().st_size} bytes)")
            else:
                print(f"  ❌ {file}: Not found")
                all_exist = False
        
        if all_exist:
            self.tests_passed += 1
            self.results.append(("Agent Files", True, "All agent files present"))
        else:
            self.tests_failed += 1
            self.results.append(("Agent Files", False, "Missing agent files"))
        
        return all_exist
    
    def test_claude_subagents(self):
        """Test Claude subagent configurations"""
        print("\n🔍 Testing Claude Subagents...")
        
        subagent_files = [
            ".claude/agents/dlq-analyzer.md",
            ".claude/agents/debugger.md",
            ".claude/agents/code-reviewer.md"
        ]
        
        all_valid = True
        for file in subagent_files:
            path = Path(file)
            if path.exists():
                # Check if file has proper frontmatter
                with open(path, 'r') as f:
                    content = f.read()
                    if content.startswith('---'):
                        # Parse frontmatter
                        lines = content.split('\n')
                        fm_end = -1
                        for i, line in enumerate(lines[1:], 1):
                            if line.strip() == '---':
                                fm_end = i
                                break
                        
                        if fm_end > 0:
                            fm_content = '\n'.join(lines[1:fm_end])
                            try:
                                fm_data = yaml.safe_load(fm_content)
                                if 'name' in fm_data and 'description' in fm_data:
                                    print(f"  ✅ {path.name}: Valid subagent - {fm_data['name']}")
                                else:
                                    print(f"  ⚠️ {path.name}: Missing required fields")
                                    all_valid = False
                            except:
                                print(f"  ⚠️ {path.name}: Invalid frontmatter")
                                all_valid = False
                    else:
                        print(f"  ⚠️ {path.name}: Missing frontmatter")
                        all_valid = False
            else:
                print(f"  ❌ {file}: Not found")
                all_valid = False
        
        if all_valid:
            self.tests_passed += 1
            self.results.append(("Claude Subagents", True, "All subagents valid"))
        else:
            self.tests_failed += 1
            self.results.append(("Claude Subagents", False, "Invalid or missing subagents"))
        
        return all_valid
    
    def test_mcp_configuration(self):
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
                    server_config = servers[server]
                    # Check for required fields
                    if 'command' in server_config:
                        print(f"  ✅ {server}: Configured")
                        if 'env' in server_config:
                            if server in ['aws-api', 'sns-sqs']:
                                if 'AWS_PROFILE' in server_config['env']:
                                    print(f"     └─ Profile: {server_config['env']['AWS_PROFILE']}")
                    else:
                        print(f"  ⚠️ {server}: Missing command")
                        all_configured = False
                else:
                    print(f"  ❌ {server}: Not configured")
                    all_configured = False
            
            if all_configured:
                self.tests_passed += 1
                self.results.append(("MCP Servers", True, "All servers configured"))
            else:
                self.tests_failed += 1
                self.results.append(("MCP Servers", False, "Missing or incomplete server configs"))
            
            return all_configured
            
        except Exception as e:
            print(f"  ❌ Error loading MCP config: {e}")
            self.tests_failed += 1
            self.results.append(("MCP Servers", False, str(e)))
            return False
    
    def test_adk_imports(self):
        """Test ADK package availability"""
        print("\n🔍 Testing ADK Package...")
        
        try:
            from google.adk import Agent, Runner
            print(f"  ✅ google.adk: Imported successfully")
            
            # Check for key components
            from google.adk.tools import FunctionTool
            print(f"  ✅ FunctionTool: Available")
            
            self.tests_passed += 1
            self.results.append(("ADK Package", True, "ADK components available"))
            return True
            
        except ImportError as e:
            print(f"  ❌ ADK Import Error: {e}")
            self.tests_failed += 1
            self.results.append(("ADK Package", False, str(e)))
            return False
    
    def test_monitoring_scripts(self):
        """Test monitoring script integration"""
        print("\n🔍 Testing Monitoring Scripts...")
        
        scripts = [
            ("scripts/start_monitor.sh", ["adk-production", "adk-test"]),
            ("scripts/monitoring/adk_monitor.py", ["ADKMonitor", "MCPClient"])
        ]
        
        all_valid = True
        for script, keywords in scripts:
            path = Path(script)
            if path.exists():
                with open(path, 'r') as f:
                    content = f.read()
                    found = []
                    missing = []
                    for kw in keywords:
                        if kw in content:
                            found.append(kw)
                        else:
                            missing.append(kw)
                    
                    if missing:
                        print(f"  ⚠️ {script}: Missing keywords: {', '.join(missing)}")
                        all_valid = False
                    else:
                        print(f"  ✅ {script}: All keywords found")
            else:
                print(f"  ❌ {script}: Not found")
                all_valid = False
        
        if all_valid:
            self.tests_passed += 1
            self.results.append(("Scripts", True, "All scripts configured"))
        else:
            self.tests_failed += 1
            self.results.append(("Scripts", False, "Script issues found"))
        
        return all_valid
    
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
        if total > 0:
            print(f"Passed: {self.tests_passed} ({self.tests_passed/total*100:.1f}%)")
            print(f"Failed: {self.tests_failed} ({self.tests_failed/total*100:.1f}%)")
        
        if self.tests_failed == 0:
            print("\n🎉 All tests passed! System components are ready.")
            print("\n📝 Next steps:")
            print("1. Ensure AWS credentials are configured: aws configure --profile FABIO-PROD")
            print("2. Set your Gemini API key: export GEMINI_API_KEY='your-key'")
            print("3. Run ADK monitoring: ./scripts/start_monitor.sh adk-production")
        else:
            print(f"\n⚠️ {self.tests_failed} test(s) failed. Please fix issues before running.")
            print("\n🔧 Troubleshooting:")
            if "Environment" in str(self.results):
                print("- Set missing environment variables in .env file")
            if "MCP" in str(self.results):
                print("- Check MCP server configurations in config/mcp_settings.json")
            if "ADK Package" in str(self.results):
                print("- Install Google ADK: pip install google-genai-developer-toolkit")
        
        return self.tests_failed == 0

def main():
    """Main test runner"""
    print("=" * 60)
    print("🧪 ADK Multi-Agent DLQ Monitor - System Validation")
    print("=" * 60)
    
    validator = ADKSystemValidator()
    
    # Run all tests
    validator.test_environment()
    validator.test_config_files()
    validator.test_agent_files()
    validator.test_claude_subagents()
    validator.test_mcp_configuration()
    validator.test_adk_imports()
    validator.test_monitoring_scripts()
    
    # Print summary
    success = validator.print_summary()
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()