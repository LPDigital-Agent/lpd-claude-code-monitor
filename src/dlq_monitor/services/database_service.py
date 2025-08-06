"""
BHiveQ NeuroCenter Database Service
Handles all database operations and queries
"""

import os
import json
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from pathlib import Path
from sqlalchemy import create_engine, func, and_, or_, desc
from sqlalchemy.orm import sessionmaker, Session
from contextlib import contextmanager

from ..models.neurocenter_models import (
    Base, Agent, Investigation, InvestigationTimeline,
    AgentDLQMapping, Metrics, PRHistory, AgentPerformance,
    SystemAlert
)


class DatabaseService:
    """Main database service for NeuroCenter"""
    
    def __init__(self, db_path: Optional[str] = None):
        if db_path is None:
            # Default database location
            db_dir = Path(__file__).parent.parent / "database"
            db_dir.mkdir(exist_ok=True)
            db_path = str(db_dir / "neurocenter.db")
        
        self.db_path = db_path
        self.engine = create_engine(f'sqlite:///{db_path}', echo=False)
        self.SessionLocal = sessionmaker(bind=self.engine)
        
        # Create tables if they don't exist
        Base.metadata.create_all(self.engine)
        
        # Initialize default agents
        self._initialize_default_agents()
    
    @contextmanager
    def get_session(self) -> Session:
        """Context manager for database sessions"""
        session = self.SessionLocal()
        try:
            yield session
            session.commit()
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()
    
    def _initialize_default_agents(self):
        """Initialize default agents if they don't exist"""
        default_agents = [
            {
                'agent_id': 'investigator',
                'name': 'Investigation Agent',
                'description': 'Primary agent for investigating DLQ issues',
                'agent_type': 'investigation'
            },
            {
                'agent_id': 'analyzer',
                'name': 'DLQ Analyzer',
                'description': 'Analyzes DLQ messages and patterns',
                'agent_type': 'analysis'
            },
            {
                'agent_id': 'debugger',
                'name': 'Code Debugger',
                'description': 'Debugs code and proposes fixes',
                'agent_type': 'debug'
            },
            {
                'agent_id': 'reviewer',
                'name': 'Code Reviewer',
                'description': 'Reviews proposed fixes and creates PRs',
                'agent_type': 'review'
            }
        ]
        
        with self.get_session() as session:
            for agent_data in default_agents:
                existing = session.query(Agent).filter_by(agent_id=agent_data['agent_id']).first()
                if not existing:
                    agent = Agent(**agent_data)
                    session.add(agent)
    
    # Agent Operations
    
    def register_agent(self, agent_id: str, name: str, description: str, agent_type: str):
        """Register an agent in the database"""
        with self.get_session() as session:
            agent = session.query(Agent).filter_by(agent_id=agent_id).first()
            if not agent:
                agent = Agent(
                    agent_id=agent_id,
                    name=name,
                    description=description,
                    agent_type=agent_type,
                    status='idle',
                    created_at=datetime.now()
                )
                session.add(agent)
            else:
                # Update existing agent
                agent.name = name
                agent.description = description
                agent.agent_type = agent_type
            session.commit()
    
    def get_all_agents(self) -> List[Dict[str, Any]]:
        """Get all agents with their current status"""
        with self.get_session() as session:
            agents = session.query(Agent).all()
            return [self._agent_to_dict(agent) for agent in agents]
    
    def update_agent_status(self, agent_id: str, status: str, current_task: Optional[str] = None,
                           current_target: Optional[str] = None):
        """Update agent status and current activity"""
        with self.get_session() as session:
            agent = session.query(Agent).filter_by(agent_id=agent_id).first()
            if agent:
                agent.status = status
                agent.last_activity = datetime.now()
                
                if current_task:
                    agent.current_task = current_task
                if current_target:
                    agent.current_target = current_target
                
                if status == 'running' and not agent.started_at:
                    agent.started_at = datetime.now()
                elif status in ['completed', 'idle', 'error']:
                    agent.started_at = None
    
    def record_agent_performance(self, agent_id: str, success: bool, duration_seconds: float):
        """Record agent performance metrics"""
        with self.get_session() as session:
            agent = session.query(Agent).filter_by(agent_id=agent_id).first()
            if agent:
                agent.total_runs += 1
                if success:
                    agent.successful_runs += 1
                else:
                    agent.failed_runs += 1
                
                # Update average runtime
                total_runtime = agent.average_runtime * (agent.total_runs - 1) + duration_seconds
                agent.average_runtime = total_runtime / agent.total_runs
                
                # Update success rate
                if agent.total_runs > 0:
                    agent.success_rate = (agent.successful_runs / agent.total_runs) * 100
    
    # Investigation Operations
    
    def create_investigation(self, dlq_name: str, message_count: int, agent_id: str,
                           initial_prompt: Optional[str] = None) -> str:
        """Create a new investigation"""
        with self.get_session() as session:
            agent = session.query(Agent).filter_by(agent_id=agent_id).first()
            
            investigation_id = f"inv_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{dlq_name[:20]}"
            
            investigation = Investigation(
                investigation_id=investigation_id,
                dlq_name=dlq_name,
                message_count=message_count,
                agent_id=agent.id if agent else None,
                initial_prompt=initial_prompt,
                status='initiated'
            )
            session.add(investigation)
            
            # Add initial timeline event
            self.add_timeline_event(
                investigation_id=investigation_id,
                event_type='detected',
                event_title=f'Error detected in queue: {dlq_name}',
                event_description=f'{message_count} messages found in DLQ',
                event_icon='exclamation-triangle'
            )
            
            return investigation_id
    
    def update_investigation(self, investigation_id: str, **kwargs):
        """Update investigation details"""
        with self.get_session() as session:
            investigation = session.query(Investigation).filter_by(
                investigation_id=investigation_id
            ).first()
            
            if investigation:
                for key, value in kwargs.items():
                    if hasattr(investigation, key):
                        setattr(investigation, key, value)
                
                # Calculate duration if completed
                if kwargs.get('status') == 'completed' and investigation.started_at:
                    investigation.completed_at = datetime.now()
                    delta = investigation.completed_at - investigation.started_at
                    investigation.duration_seconds = delta.total_seconds()
    
    def get_active_investigations(self) -> List[Dict[str, Any]]:
        """Get all active investigations"""
        with self.get_session() as session:
            investigations = session.query(Investigation).filter(
                Investigation.status.notin_(['completed', 'failed'])
            ).order_by(desc(Investigation.started_at)).all()
            
            return [self._investigation_to_dict(inv) for inv in investigations]
    
    def get_investigation_details(self, investigation_id: str) -> Optional[Dict[str, Any]]:
        """Get detailed investigation information"""
        with self.get_session() as session:
            investigation = session.query(Investigation).filter_by(
                investigation_id=investigation_id
            ).first()
            
            if investigation:
                details = self._investigation_to_dict(investigation)
                
                # Add timeline events
                timeline = session.query(InvestigationTimeline).filter_by(
                    investigation_id=investigation.id
                ).order_by(InvestigationTimeline.timestamp).all()
                
                details['timeline'] = [self._timeline_to_dict(event) for event in timeline]
                
                return details
        return None
    
    # Timeline Operations
    
    def add_timeline_event(self, investigation_id: str, event_type: str, event_title: str,
                          event_description: Optional[str] = None, event_icon: Optional[str] = None,
                          data: Optional[Dict] = None, agent_id: Optional[str] = None):
        """Add a timeline event to an investigation"""
        with self.get_session() as session:
            investigation = session.query(Investigation).filter_by(
                investigation_id=investigation_id
            ).first()
            
            if investigation:
                agent = None
                if agent_id:
                    agent = session.query(Agent).filter_by(agent_id=agent_id).first()
                
                event = InvestigationTimeline(
                    investigation_id=investigation.id,
                    agent_id=agent.id if agent else None,
                    event_type=event_type,
                    event_title=event_title,
                    event_description=event_description,
                    event_icon=event_icon or 'info-circle',
                    data=data or {}
                )
                session.add(event)
    
    # Agent-DLQ Mapping Operations
    
    def get_dlq_mappings(self) -> List[Dict[str, Any]]:
        """Get all agent-DLQ mappings"""
        with self.get_session() as session:
            mappings = session.query(AgentDLQMapping).join(Agent).filter(
                AgentDLQMapping.enabled == True
            ).order_by(AgentDLQMapping.priority).all()
            
            result = []
            for mapping in mappings:
                result.append({
                    'id': mapping.id,
                    'agent_id': mapping.agent.agent_id,
                    'agent_name': mapping.agent.name,
                    'dlq_pattern': mapping.dlq_pattern,
                    'trigger_type': mapping.trigger_type,
                    'trigger_rule': mapping.trigger_rule,
                    'environment': mapping.environment,
                    'enabled': mapping.enabled,
                    'priority': mapping.priority,
                    'times_triggered': mapping.times_triggered,
                    'last_triggered': mapping.last_triggered.isoformat() if mapping.last_triggered else None
                })
            
            return result
    
    def create_dlq_mapping(self, agent_id: str, dlq_pattern: str, trigger_type: str = 'message_count',
                          trigger_rule: Optional[Dict] = None, environment: str = 'all'):
        """Create a new agent-DLQ mapping"""
        with self.get_session() as session:
            agent = session.query(Agent).filter_by(agent_id=agent_id).first()
            
            if agent:
                mapping = AgentDLQMapping(
                    agent_id=agent.id,
                    dlq_pattern=dlq_pattern,
                    trigger_type=trigger_type,
                    trigger_rule=trigger_rule or {},
                    environment=environment
                )
                session.add(mapping)
                return True
        return False
    
    def update_dlq_mapping(self, mapping_id: int, **kwargs):
        """Update a DLQ mapping"""
        with self.get_session() as session:
            mapping = session.query(AgentDLQMapping).filter_by(id=mapping_id).first()
            
            if mapping:
                for key, value in kwargs.items():
                    if hasattr(mapping, key):
                        setattr(mapping, key, value)
                return True
        return False
    
    def delete_dlq_mapping(self, mapping_id: int):
        """Delete a DLQ mapping"""
        with self.get_session() as session:
            mapping = session.query(AgentDLQMapping).filter_by(id=mapping_id).first()
            
            if mapping:
                session.delete(mapping)
                return True
        return False
    
    def find_agent_for_dlq(self, dlq_name: str, message_count: int, 
                          environment: str = 'prod') -> Optional[str]:
        """Find the best agent for a DLQ based on mappings"""
        with self.get_session() as session:
            mappings = session.query(AgentDLQMapping).join(Agent).filter(
                and_(
                    AgentDLQMapping.enabled == True,
                    or_(
                        AgentDLQMapping.environment == 'all',
                        AgentDLQMapping.environment == environment
                    )
                )
            ).order_by(AgentDLQMapping.priority).all()
            
            for mapping in mappings:
                # Check if DLQ matches pattern
                if mapping.dlq_pattern in dlq_name or mapping.dlq_pattern == '*':
                    # Check trigger conditions
                    if mapping.trigger_type == 'always':
                        return mapping.agent.agent_id
                    elif mapping.trigger_type == 'message_count':
                        threshold = mapping.trigger_rule.get('threshold', 0)
                        if message_count >= threshold:
                            # Update trigger statistics
                            mapping.times_triggered += 1
                            mapping.last_triggered = datetime.now()
                            return mapping.agent.agent_id
        
        # Default to investigator if no mapping found
        return 'investigator'
    
    # Metrics Operations
    
    def record_metric(self, metric_name: str, value: float, metric_type: str = 'gauge',
                      agent_id: Optional[str] = None, dlq_name: Optional[str] = None):
        """Record a metric"""
        with self.get_session() as session:
            metric = Metrics(
                metric_name=metric_name,
                metric_type=metric_type,
                value=value,
                agent_id=agent_id,
                dlq_name=dlq_name,
                period_start=datetime.now(),
                period_end=datetime.now()
            )
            session.add(metric)
    
    def get_metrics_summary(self, hours: int = 24) -> Dict[str, Any]:
        """Get metrics summary for the last N hours"""
        with self.get_session() as session:
            since = datetime.now() - timedelta(hours=hours)
            
            # Active agents
            active_agents = session.query(Agent).filter(
                Agent.status != 'idle'
            ).count()
            
            # Investigations in period
            investigations = session.query(Investigation).filter(
                Investigation.started_at >= since
            ).all()
            
            total_investigations = len(investigations)
            completed = len([i for i in investigations if i.status == 'completed'])
            
            # Average investigation time
            completed_investigations = [i for i in investigations if i.duration_seconds]
            avg_time = sum(i.duration_seconds for i in completed_investigations) / len(completed_investigations) if completed_investigations else 0
            
            # PRs created
            prs = session.query(PRHistory).filter(
                PRHistory.created_at >= since
            ).count()
            
            # Success rate
            success_rate = (completed / total_investigations * 100) if total_investigations > 0 else 0
            
            return {
                'active_agents': active_agents,
                'investigations_total': total_investigations,
                'investigations_completed': completed,
                'average_investigation_time': avg_time,
                'prs_created': prs,
                'success_rate': success_rate,
                'period_hours': hours
            }
    
    # Helper methods
    
    def _agent_to_dict(self, agent: Agent) -> Dict[str, Any]:
        """Convert agent object to dictionary"""
        elapsed_time = None
        if agent.started_at:
            delta = datetime.now() - agent.started_at
            elapsed_time = delta.total_seconds()
        
        return {
            'id': agent.agent_id,
            'name': agent.name,
            'description': agent.description,
            'type': agent.agent_type,
            'status': agent.status,
            'current_task': agent.current_task,
            'current_target': agent.current_target,
            'started_at': agent.started_at.isoformat() if agent.started_at else None,
            'elapsed_time': elapsed_time,
            'last_activity': agent.last_activity.isoformat() if agent.last_activity else None,
            'total_runs': agent.total_runs,
            'success_rate': agent.success_rate,
            'average_runtime': agent.average_runtime,
            'enabled': agent.enabled
        }
    
    def _investigation_to_dict(self, investigation: Investigation) -> Dict[str, Any]:
        """Convert investigation object to dictionary"""
        return {
            'id': investigation.investigation_id,
            'dlq_name': investigation.dlq_name,
            'message_count': investigation.message_count,
            'status': investigation.status,
            'progress': investigation.progress,
            'error_type': investigation.error_type,
            'error_message': investigation.error_message,
            'started_at': investigation.started_at.isoformat() if investigation.started_at else None,
            'completed_at': investigation.completed_at.isoformat() if investigation.completed_at else None,
            'duration_seconds': investigation.duration_seconds,
            'pr_number': investigation.pr_number,
            'pr_url': investigation.pr_url,
            'pr_status': investigation.pr_status,
            'environment': investigation.environment,
            'region': investigation.region
        }
    
    def _timeline_to_dict(self, event: InvestigationTimeline) -> Dict[str, Any]:
        """Convert timeline event to dictionary"""
        return {
            'id': event.id,
            'event_type': event.event_type,
            'event_title': event.event_title,
            'event_description': event.event_description,
            'event_icon': event.event_icon,
            'timestamp': event.timestamp.isoformat(),
            'data': event.data,
            'agent_name': event.agent.name if event.agent else None
        }


# Singleton instance
_db_service = None

def get_database_service() -> DatabaseService:
    """Get or create the database service singleton"""
    global _db_service
    if _db_service is None:
        _db_service = DatabaseService()
    return _db_service