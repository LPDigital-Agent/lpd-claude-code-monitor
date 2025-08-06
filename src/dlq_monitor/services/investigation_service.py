"""
BHiveQ NeuroCenter Investigation Service
Manages investigation lifecycle and timeline generation
"""

import json
import asyncio
from datetime import datetime
from typing import Dict, Any, List, Optional
from pathlib import Path

from .database_service import get_database_service


class InvestigationService:
    """Service for managing investigations and timeline events"""
    
    def __init__(self):
        self.db = get_database_service()
        self.active_investigations = {}
    
    def start_investigation(self, dlq_name: str, message_count: int, 
                           error_samples: Optional[List[Dict]] = None) -> str:
        """Start a new investigation"""
        # Find appropriate agent based on DLQ mappings
        agent_id = self.db.find_agent_for_dlq(dlq_name, message_count)
        
        # Create investigation
        investigation_id = self.db.create_investigation(
            dlq_name=dlq_name,
            message_count=message_count,
            agent_id=agent_id,
            initial_prompt=self._generate_prompt(dlq_name, message_count, error_samples)
        )
        
        # Update agent status
        self.db.update_agent_status(
            agent_id=agent_id,
            status='running',
            current_task=f'Investigating {dlq_name}',
            current_target=dlq_name
        )
        
        # Add timeline events
        self.db.add_timeline_event(
            investigation_id=investigation_id,
            event_type='launched',
            event_title=f'{agent_id.title()} Agent launched',
            event_description=f'Starting investigation of {message_count} messages',
            event_icon='play-circle',
            agent_id=agent_id
        )
        
        self.active_investigations[investigation_id] = {
            'dlq_name': dlq_name,
            'agent_id': agent_id,
            'started_at': datetime.now()
        }
        
        return investigation_id
    
    def update_investigation_progress(self, investigation_id: str, progress: int, 
                                    status: str, event_type: str, event_title: str,
                                    event_description: Optional[str] = None,
                                    data: Optional[Dict] = None):
        """Update investigation progress and add timeline event"""
        # Update investigation
        self.db.update_investigation(
            investigation_id=investigation_id,
            progress=progress,
            status=status
        )
        
        # Add timeline event
        if investigation_id in self.active_investigations:
            agent_id = self.active_investigations[investigation_id]['agent_id']
            
            self.db.add_timeline_event(
                investigation_id=investigation_id,
                event_type=event_type,
                event_title=event_title,
                event_description=event_description,
                event_icon=self._get_event_icon(event_type),
                data=data,
                agent_id=agent_id
            )
    
    def report_root_cause(self, investigation_id: str, error_type: str, 
                         error_message: str, stack_trace: str,
                         affected_code: Optional[Dict] = None):
        """Report root cause found during investigation"""
        self.db.update_investigation(
            investigation_id=investigation_id,
            error_type=error_type,
            error_message=error_message,
            stack_trace=stack_trace,
            progress=50,
            status='debugging'
        )
        
        self.db.add_timeline_event(
            investigation_id=investigation_id,
            event_type='found_cause',
            event_title=f'Root cause found: {error_type}',
            event_description=error_message[:200],
            event_icon='magnifying-glass',
            data={
                'error_type': error_type,
                'stack_trace': stack_trace,
                'affected_code': affected_code
            }
        )
    
    def propose_fix(self, investigation_id: str, proposed_fix: str, 
                    code_diff: str, files_affected: List[str]):
        """Record proposed fix for the issue"""
        self.db.update_investigation(
            investigation_id=investigation_id,
            proposed_fix=proposed_fix,
            code_diff=code_diff,
            progress=75,
            status='reviewing'
        )
        
        self.db.add_timeline_event(
            investigation_id=investigation_id,
            event_type='proposed_fix',
            event_title='Code fix proposed',
            event_description=f'{len(files_affected)} files will be modified',
            event_icon='wrench',
            data={
                'files_affected': files_affected,
                'diff_preview': code_diff[:500]
            }
        )
    
    def create_pr(self, investigation_id: str, pr_number: int, pr_url: str, pr_title: str):
        """Record PR creation"""
        self.db.update_investigation(
            investigation_id=investigation_id,
            pr_number=pr_number,
            pr_url=pr_url,
            pr_status='open',
            progress=90,
            status='awaiting_review'
        )
        
        self.db.add_timeline_event(
            investigation_id=investigation_id,
            event_type='pr_created',
            event_title=f'Pull Request #{pr_number} created',
            event_description=pr_title,
            event_icon='git-pull-request',
            data={
                'pr_number': pr_number,
                'pr_url': pr_url,
                'pr_title': pr_title
            }
        )
    
    def complete_investigation(self, investigation_id: str, success: bool = True,
                              resolution_notes: Optional[str] = None):
        """Complete an investigation"""
        status = 'completed' if success else 'failed'
        
        self.db.update_investigation(
            investigation_id=investigation_id,
            status=status,
            progress=100
        )
        
        if investigation_id in self.active_investigations:
            agent_id = self.active_investigations[investigation_id]['agent_id']
            started_at = self.active_investigations[investigation_id]['started_at']
            
            # Calculate duration
            duration = (datetime.now() - started_at).total_seconds()
            
            # Update agent status
            self.db.update_agent_status(
                agent_id=agent_id,
                status='idle',
                current_task=None,
                current_target=None
            )
            
            # Record performance
            self.db.record_agent_performance(
                agent_id=agent_id,
                success=success,
                duration_seconds=duration
            )
            
            # Add final timeline event
            self.db.add_timeline_event(
                investigation_id=investigation_id,
                event_type='completed',
                event_title='Investigation completed' if success else 'Investigation failed',
                event_description=resolution_notes,
                event_icon='check-circle' if success else 'x-circle',
                agent_id=agent_id
            )
            
            # Clean up
            del self.active_investigations[investigation_id]
    
    def get_investigation_timeline(self, investigation_id: str) -> Dict[str, Any]:
        """Get complete investigation timeline"""
        return self.db.get_investigation_details(investigation_id)
    
    def get_active_investigations(self) -> List[Dict[str, Any]]:
        """Get all active investigations"""
        return self.db.get_active_investigations()
    
    def _generate_prompt(self, dlq_name: str, message_count: int, 
                        error_samples: Optional[List[Dict]] = None) -> str:
        """Generate investigation prompt"""
        prompt = f"Investigate DLQ '{dlq_name}' with {message_count} messages.\n"
        
        if error_samples:
            prompt += "\nError samples:\n"
            for i, sample in enumerate(error_samples[:3], 1):
                prompt += f"\nSample {i}:\n{json.dumps(sample, indent=2)}\n"
        
        prompt += "\nAnalyze the errors, identify root cause, and propose a fix."
        
        return prompt
    
    def _get_event_icon(self, event_type: str) -> str:
        """Get appropriate icon for event type"""
        icon_map = {
            'detected': 'alert-triangle',
            'launched': 'rocket',
            'analyzing': 'cpu',
            'found_cause': 'search',
            'proposed_fix': 'wrench',
            'pr_created': 'git-pull-request',
            'completed': 'check-circle',
            'failed': 'x-circle',
            'error': 'alert-circle'
        }
        return icon_map.get(event_type, 'info')
    
    def simulate_investigation(self, dlq_name: str, message_count: int):
        """Simulate an investigation for demo purposes"""
        import time
        import random
        
        # Start investigation
        investigation_id = self.start_investigation(dlq_name, message_count)
        
        # Simulate progress
        time.sleep(1)
        self.update_investigation_progress(
            investigation_id, 25, 'analyzing',
            'analyzing', 'Analyzing DLQ messages',
            'Parsing message attributes and error patterns'
        )
        
        time.sleep(1)
        self.report_root_cause(
            investigation_id,
            'NullPointerException',
            'Null reference in handleUserUpdate() at line 125',
            'at com.lpd.api.handlers.UserHandler.handleUserUpdate(UserHandler.java:125)\n' +
            'at com.lpd.api.processors.MessageProcessor.process(MessageProcessor.java:45)'
        )
        
        time.sleep(1)
        self.propose_fix(
            investigation_id,
            'Add null check before accessing user.getProfile()',
            '- user.getProfile().updateLastSeen();\n+ if (user != null && user.getProfile() != null) {\n+     user.getProfile().updateLastSeen();\n+ }',
            ['src/main/java/com/lpd/api/handlers/UserHandler.java']
        )
        
        time.sleep(1)
        pr_number = random.randint(1000, 9999)
        self.create_pr(
            investigation_id,
            pr_number,
            f'https://github.com/lpd/api/pull/{pr_number}',
            f'Fix: Add null check in UserHandler to prevent NPE'
        )
        
        time.sleep(1)
        self.complete_investigation(
            investigation_id, True,
            'Successfully identified and fixed null pointer exception in user update handler'
        )


# Singleton instance
_investigation_service = None

def get_investigation_service() -> InvestigationService:
    """Get or create the investigation service singleton"""
    global _investigation_service
    if _investigation_service is None:
        _investigation_service = InvestigationService()
    return _investigation_service