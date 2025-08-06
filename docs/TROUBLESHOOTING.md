# Troubleshooting Guide

## Common Issues and Solutions

### Installation Issues

#### 1. Blake2 Hash Warnings
**Error:**
```
ERROR:root:code for hash blake2b was not found.
ValueError: unsupported hash type blake2b
```

**Solution:** This is a harmless cosmetic warning in Python 3.11. It doesn't affect functionality and can be safely ignored.

---

#### 2. Wrong Package Name for Google ADK
**Error:**
```
ERROR: No matching distribution found for google-genai-developer-toolkit
```

**Solution:** The correct package name is `google-adk`, not `google-genai-developer-toolkit`:
```bash
# Correct installation
pip install google-adk
pip install google-generativeai  # Also needed for Gemini API
```

---

#### 3. MCP Server Version Issues
**Error:**
```
ERROR: Could not find a version that satisfies the requirement awslabs.aws-api-mcp-server>=1.0.0
```

**Solution:** MCP servers are optional and have been commented out in `requirements_adk.txt`. They can be installed separately via npm if needed:
```bash
npm install -g @mcp-servers/aws
npm install -g @modelcontextprotocol/server-github
```

---

#### 4. Duplicate TOML Sections
**Error:**
```
ERROR: Cannot declare ('tool', 'setuptools') twice
```

**Solution:** This has been fixed. Ensure your `pyproject.toml` has only one `[tool.setuptools]` section.

---

### Environment Issues

#### 1. Missing GitHub Token
**Error:**
```
❌ GITHUB_TOKEN: Not set
```

**Solution:** Use the GitHub CLI token:
```bash
# Export for current session
export GITHUB_TOKEN=$(gh auth token 2>/dev/null)

# Or add to .env file
echo "GITHUB_TOKEN=$(gh auth token 2>/dev/null)" >> .env
```

---

#### 2. Missing Gemini API Key
**Error:**
```
❌ GEMINI_API_KEY: Not set
```

**Solution:** 
1. Get API key from [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Add to `.env` file:
```bash
GEMINI_API_KEY=AIzaSy...your_key_here
```

---

#### 3. AWS Profile Not Found
**Error:**
```
ProfileNotFound: The config profile (FABIO-PROD) could not be found
```

**Solution:** Configure AWS profile:
```bash
aws configure --profile FABIO-PROD
# Enter your AWS credentials when prompted
```

---

### Python Environment Issues

#### 1. ModuleNotFoundError
**Error:**
```
ModuleNotFoundError: No module named 'dotenv'
```

**Solution:** Install in the correct Python environment:
```bash
# Activate virtual environment first
source venv/bin/activate

# Install missing module
pip install python-dotenv
```

---

#### 2. Mixed Python Versions
**Problem:** Packages installed in wrong Python version directory

**Solution:** Ensure using consistent Python version:
```bash
# Check Python version
python --version

# Reinstall all packages
pip install -r requirements.txt
pip install -r requirements_adk.txt
```

---

### Permission Issues

#### Script Permission Denied
**Error:**
```
zsh: permission denied: ./scripts/start_monitor.sh
```

**Solution:** Make scripts executable:
```bash
# Quick fix - run the permission fix script
chmod +x scripts/fix_permissions.sh
./scripts/fix_permissions.sh

# Or manually fix specific script
chmod +x ./scripts/start_monitor.sh
```

---

### Runtime Issues

#### 1. ADK Import Errors
**Error:**
```
ImportError: cannot import name 'FunctionTool' from 'google.adk.tools'
```

**Solution:** This is a known issue with some ADK versions. Use the alias:
```python
from google.adk import FunctionTool
```

---

#### 2. MCP Server Not Starting
**Error:**
```
MCP server 'context7' failed to start
```

**Solution:** Ensure MCP servers are installed:
```bash
# Install via npx (recommended)
npx -y @upstash/context7-mcp-server

# Or check config/mcp_settings.json for correct paths
```

---

### Testing Issues

#### 1. Validation Test Failures
**Running:** `python tests/validation/test_adk_simple.py`

**Common Failures:**
- Missing environment variables: Set in `.env` file
- Missing config files: Copy from templates
- Script validation: Ensure "MCPClient" reference exists in scripts

---

### macOS Specific Issues

#### 1. Notification Permissions
**Problem:** Notifications not appearing

**Solution:** 
1. Go to System Preferences → Notifications
2. Add Terminal/iTerm to allowed apps
3. Enable notifications for the app

---

#### 2. Audio Not Playing
**Problem:** ElevenLabs TTS not working

**Solution:**
1. Check ElevenLabs API key in `.env`
2. Verify voice ID: `19STyYD15bswVz51nqLf`
3. Test with: `./start_monitor.sh pr-audio-test`

---

## Debug Commands

### Check System Status
```bash
# Validate entire system
python tests/validation/test_adk_simple.py

# Check AWS connection
aws sqs list-queues --profile FABIO-PROD --region sa-east-1

# Check GitHub authentication
gh auth status

# Test Gemini API
python -c "import google.generativeai as genai; import os; genai.configure(api_key=os.getenv('GEMINI_API_KEY')); print('✅ Gemini OK')"

# Test Google ADK
python -c "from google.adk import Agent, Runner; print('✅ ADK OK')"
```

### View Logs
```bash
# Main application log
tail -f dlq_monitor_FABIO-PROD_sa-east-1.log

# ADK monitor log
tail -f logs/adk_monitor.log

# Claude sessions
cat .claude_sessions.json | jq .
```

### Clean Installation
```bash
# Remove virtual environment
rm -rf venv

# Create fresh environment
python3.11 -m venv venv
source venv/bin/activate

# Reinstall everything
pip install --upgrade pip
pip install -r requirements.txt
pip install google-adk google-generativeai
pip install -r requirements_adk.txt
pip install -e .
```

## Getting Help

If you encounter issues not covered here:

1. Check the documentation:
   - `README.md` - Overview and quick start
   - `docs/setup-deployment-guide.md` - Detailed setup
   - `CLAUDE.md` - Development guide
   - `docs/investigation-enhancements.md` - MCP tools details

2. Review recent changes:
   - `docs/RELEASE_NOTES_MCP_ENHANCEMENTS.md`
   - Git commit history

3. Run validation test for diagnostic information:
   ```bash
   python tests/validation/test_adk_simple.py
   ```

4. Check GitHub issues:
   - https://github.com/LPDigital-Agent/lpd-claude-code-monitor/issues