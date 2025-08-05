#!/usr/bin/env python3
"""
Manual trigger for auto-investigation - useful for testing
"""
import subprocess
import sys
import os
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def trigger_investigation(queue_name):
    """Manually trigger Claude investigation for a specific queue"""
    
    print(f"🚀 Manually triggering investigation for: {queue_name}")
    print("=" * 60)
    
    # Prepare the enhanced Claude prompt with multi-agent capabilities
    claude_prompt = f"""🚨 CRITICAL DLQ INVESTIGATION REQUIRED: {queue_name}

📋 CONTEXT:
- AWS Profile: FABIO-PROD
- Region: sa-east-1
- Queue: {queue_name}
- Investigation Type: Manual Trigger

🎯 YOUR MISSION (USE CLAUDE CODE FOR ALL TASKS):

1. **MULTI-SUBAGENT INVESTIGATION**:
   - Deploy multiple subagents to investigate in parallel
   - Use ultrathink for deep analysis and root cause identification
   - Each subagent should focus on different aspects:
     * Subagent 1: Analyze DLQ messages and error patterns
     * Subagent 2: Check CloudWatch logs for related errors
     * Subagent 3: Review codebase for potential issues
     * Subagent 4: Identify configuration or deployment problems

2. **USE ALL MCP TOOLS**:
   - Use sequential-thinking MCP for step-by-step problem solving
   - Use filesystem MCP to analyze and fix code
   - Use GitHub MCP to check recent changes and create PRs
   - Use memory MCP to track investigation progress
   - Use any other relevant MCP tools available

3. **ULTRATHINK ANALYSIS**:
   - Apply ultrathink reasoning for complex problem solving
   - Consider multiple hypotheses for the root cause
   - Validate each hypothesis with evidence from logs and code
   - Choose the most likely solution based on evidence

4. **COMPREHENSIVE FIX**:
   - Identify ALL issues causing messages to go to DLQ
   - Fix the root cause in the codebase
   - Add proper error handling to prevent future occurrences
   - Include logging improvements for better debugging

5. **CODE CHANGES & DEPLOYMENT**:
   - Make necessary code changes using filesystem MCP
   - **COMMIT the code changes** with descriptive commit message
   - Create a Pull Request with detailed description of:
     * Root cause analysis
     * Changes made
     * Testing performed
     * Prevention measures

6. **DLQ CLEANUP**:
   - After fixes are committed, purge the DLQ messages
   - Verify the queue is clean
   - Document the incident resolution

⚡ IMPORTANT INSTRUCTIONS:
- Use CLAUDE CODE for all operations (not just responses)
- Deploy MULTIPLE SUBAGENTS working in parallel
- Use ULTRATHINK for deep reasoning
- Leverage ALL available MCP tools
- Be thorough and fix ALL issues, not just symptoms
- Create a comprehensive PR with full documentation
- This is PRODUCTION - be careful but thorough

🔄 Start the multi-agent investigation NOW!"""
    
    print(f"📝 Prompt prepared for queue: {queue_name}")
    print(f"🔍 Executing Claude command...")
    print("-" * 60)
    
    # Execute Claude command with proper format for Claude Code
    # According to docs: claude -p "prompt"
    cmd = ['claude', '-p', claude_prompt]
    
    try:
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        print(f"✅ Claude process started with PID: {process.pid}")
        print(f"⏰ This may take up to 30 minutes...")
        print(f"💡 You can check the process with: ps aux | grep {process.pid}")
        
        # Optionally wait for completion
        response = input("\nWait for completion? (y/n): ")
        if response.lower() == 'y':
            print("\n⏳ Waiting for Claude to complete...")
            stdout, stderr = process.communicate(timeout=1800)  # 30 minutes
            
            if process.returncode == 0:
                print("\n✅ Investigation completed successfully!")
                if stdout:
                    print("\n📋 Claude output (first 1000 chars):")
                    print(stdout[:1000])
            else:
                print(f"\n❌ Investigation failed with exit code: {process.returncode}")
                if stderr:
                    print(f"Error: {stderr[:500]}")
        else:
            print("\n📊 Investigation running in background")
            print(f"Check process status: ps aux | grep {process.pid}")
            
    except subprocess.TimeoutExpired:
        print("\n⏰ Investigation timed out after 30 minutes")
        process.kill()
    except Exception as e:
        print(f"\n❌ Error triggering investigation: {e}")

def main():
    print("=" * 60)
    print("🤖 Manual DLQ Auto-Investigation Trigger")
    print("=" * 60)
    
    # List available queues
    monitored_queues = [
        "fm-digitalguru-api-update-dlq-prod",
        "fm-transaction-processor-dlq-prd"
    ]
    
    print("\n📋 Monitored DLQ queues:")
    for i, queue in enumerate(monitored_queues, 1):
        print(f"   {i}. {queue}")
    
    print("\n💡 You can also enter a custom queue name")
    
    choice = input("\nEnter queue number or name: ").strip()
    
    if choice.isdigit():
        idx = int(choice) - 1
        if 0 <= idx < len(monitored_queues):
            queue_name = monitored_queues[idx]
        else:
            print("❌ Invalid choice")
            return
    else:
        queue_name = choice
    
    print(f"\n🎯 Selected queue: {queue_name}")
    confirm = input("Trigger investigation? (y/n): ")
    
    if confirm.lower() == 'y':
        trigger_investigation(queue_name)
    else:
        print("❌ Cancelled")

if __name__ == "__main__":
    main()
