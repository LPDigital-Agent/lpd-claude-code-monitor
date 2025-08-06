"""
Coordinator Agent - Main orchestrator for the DLQ monitoring system
"""

from google.adk.agents import LlmAgent
from typing import Dict, List, Optional
from datetime import datetime, timedelta
import json
import logging

logger = logging.getLogger(__name__)

# Track investigations to prevent duplicates
investigation_state = {
    "active_investigations": {},
    "last_investigation": {},
    "cooldown_period": timedelta(hours=1)
}

def create_coordinator_agent(sub_agents: Dict) -> LlmAgent:
    """
    Create the main coordinator agent that orchestrates all monitoring activities
    """
    
    coordinator = LlmAgent(
        name="dlq_coordinator",
        model="gemini-2.0-flash",
        description="Main orchestrator for DLQ monitoring and investigation workflow",
        instruction="""
        You are the main coordinator for the Financial Move DLQ monitoring system.
        
        CRITICAL CONTEXT:
        - AWS Profile: FABIO-PROD
        - Region: sa-east-1
        - Environment: PRODUCTION
        
        YOUR RESPONSIBILITIES:
        
        1. MONITORING ORCHESTRATION:
           - Trigger DLQ Monitor Agent every 30 seconds
           - Process alerts from DLQ Monitor Agent
           - Track which DLQs have messages
        
        2. AUTO-INVESTIGATION TRIGGERS:
           Critical DLQs requiring immediate auto-investigation:
           - fm-digitalguru-api-update-dlq-prod
           - fm-transaction-processor-dlq-prd
           
           When messages detected in these DLQs:
           a) Check if investigation is already running (prevent duplicates)
           b) Verify cooldown period (1 hour between investigations)
           c) If clear, trigger Investigation Agent
        
        3. INVESTIGATION WORKFLOW:
           - Pass DLQ details to Investigation Agent
           - Wait for root cause analysis
           - Trigger Code Fixer Agent with investigation results
           - Coordinate PR creation via PR Manager Agent
           - Send notifications via Notification Agent
        
        4. STATE MANAGEMENT:
           - Track active investigations
           - Prevent duplicate investigations
           - Manage cooldown periods
           - Store investigation history
        
        5. NOTIFICATION COORDINATION:
           - Critical alerts for DLQ messages
           - Investigation status updates
           - PR creation notifications
           - Review reminders every 10 minutes
        
        WORKFLOW RULES:
        - Never run duplicate investigations for same DLQ
        - Respect 1-hour cooldown between investigations
        - Prioritize critical DLQs over others
        - Always notify on investigation start/end
        - Track all PR creation for audit
        
        AGENT COORDINATION:
        - Use DLQ Monitor Agent for queue checks
        - Use Investigation Agent for root cause analysis
        - Use Code Fixer Agent for implementing fixes
        - Use PR Manager Agent for GitHub operations
        - Use Notification Agent for all alerts
        
        Remember: This is PRODUCTION. Be careful but thorough.
        """,
        sub_agents=list(sub_agents.values()) if sub_agents else []
    )
    
    return coordinator

def should_auto_investigate(queue_name: str, message_count: int) -> bool:
    """
    Determine if auto-investigation should be triggered for a queue
    """
    critical_dlqs = [
        "fm-digitalguru-api-update-dlq-prod",
        "fm-transaction-processor-dlq-prd"
    ]
    
    if queue_name not in critical_dlqs:
        return False
    
    # Check if investigation is already active
    if queue_name in investigation_state["active_investigations"]:
        logger.info(f"Investigation already active for {queue_name}")
        return False
    
    # Check cooldown period
    if queue_name in investigation_state["last_investigation"]:
        last_time = investigation_state["last_investigation"][queue_name]
        time_since = datetime.now() - last_time
        if time_since < investigation_state["cooldown_period"]:
            remaining = investigation_state["cooldown_period"] - time_since
            logger.info(f"Cooldown active for {queue_name}: {remaining.total_seconds()/60:.1f} minutes remaining")
            return False
    
    return True

def mark_investigation_started(queue_name: str):
    """Mark an investigation as started"""
    investigation_state["active_investigations"][queue_name] = datetime.now()
    logger.info(f"Investigation started for {queue_name}")

def mark_investigation_completed(queue_name: str):
    """Mark an investigation as completed"""
    if queue_name in investigation_state["active_investigations"]:
        del investigation_state["active_investigations"][queue_name]
    investigation_state["last_investigation"][queue_name] = datetime.now()
    logger.info(f"Investigation completed for {queue_name}")

# Export the coordinator
coordinator = create_coordinator_agent({})