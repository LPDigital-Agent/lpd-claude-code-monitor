"""
BHiveQ NeuroCenter Database Models
SQLAlchemy ORM models for complete operational intelligence tracking
"""

from datetime import datetime
from typing import Optional, Dict, Any
from sqlalchemy import (
    create_engine, Column, Integer, String, DateTime, Float, Boolean,
    Text, JSON, ForeignKey, Index, UniqueConstraint, CheckConstraint
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy.sql import func

Base = declarative_base()


class Agent(Base):
    """Agent configuration and status tracking"""
    __tablename__ = 'agents'
    
    id = Column(Integer, primary_key=True)
    agent_id = Column(String(50), unique=True, nullable=False)  # e.g., 'investigator', 'analyzer'
    name = Column(String(100), nullable=False)
    description = Column(Text)
    agent_type = Column(String(50))  # 'investigation', 'analysis', 'debug', 'review'
    status = Column(String(20), default='idle')  # idle, running, completed, error
    
    # Performance metrics
    total_runs = Column(Integer, default=0)
    successful_runs = Column(Integer, default=0)
    failed_runs = Column(Integer, default=0)
    average_runtime = Column(Float, default=0.0)  # in seconds
    success_rate = Column(Float, default=0.0)  # percentage
    
    # Current activity
    current_task = Column(Text)
    current_target = Column(String(200))  # Queue, Error, or PR
    started_at = Column(DateTime)
    last_activity = Column(DateTime, default=func.now())
    
    # Configuration
    config = Column(JSON, default={})
    enabled = Column(Boolean, default=True)
    
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relationships
    dlq_mappings = relationship("AgentDLQMapping", back_populates="agent", cascade="all, delete-orphan")
    investigations = relationship("Investigation", back_populates="agent")
    timeline_events = relationship("InvestigationTimeline", back_populates="agent")
    
    __table_args__ = (
        Index('idx_agent_status', 'status'),
        Index('idx_agent_type', 'agent_type'),
    )


class Investigation(Base):
    """Complete investigation lifecycle tracking"""
    __tablename__ = 'investigations'
    
    id = Column(Integer, primary_key=True)
    investigation_id = Column(String(100), unique=True, nullable=False)
    
    # Investigation details
    dlq_name = Column(String(200), nullable=False)
    message_count = Column(Integer)
    error_type = Column(String(100))
    error_message = Column(Text)
    
    # Status tracking
    status = Column(String(20), default='initiated')  # initiated, analyzing, debugging, reviewing, completed, failed
    progress = Column(Integer, default=0)  # 0-100
    
    # Agent assignment
    agent_id = Column(Integer, ForeignKey('agents.id'))
    agent = relationship("Agent", back_populates="investigations")
    
    # Timing
    started_at = Column(DateTime, default=func.now())
    completed_at = Column(DateTime)
    duration_seconds = Column(Float)
    
    # Investigation data
    initial_prompt = Column(Text)
    root_cause = Column(Text)
    proposed_fix = Column(Text)
    code_diff = Column(Text)
    stack_trace = Column(Text)
    cloudwatch_logs = Column(JSON)
    
    # PR tracking
    pr_number = Column(Integer)
    pr_url = Column(String(500))
    pr_status = Column(String(20))  # open, merged, closed
    pr_created_at = Column(DateTime)
    
    # Metadata
    environment = Column(String(20), default='prod')  # prod, staging, dev
    region = Column(String(20), default='sa-east-1')
    extra_data = Column(JSON, default={})
    
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relationships
    timeline_events = relationship("InvestigationTimeline", back_populates="investigation", cascade="all, delete-orphan")
    
    __table_args__ = (
        Index('idx_investigation_status', 'status'),
        Index('idx_investigation_dlq', 'dlq_name'),
        Index('idx_investigation_started', 'started_at'),
    )


class InvestigationTimeline(Base):
    """Detailed timeline events for each investigation"""
    __tablename__ = 'investigation_timeline'
    
    id = Column(Integer, primary_key=True)
    investigation_id = Column(Integer, ForeignKey('investigations.id'), nullable=False)
    agent_id = Column(Integer, ForeignKey('agents.id'))
    
    # Event details
    event_type = Column(String(50), nullable=False)  # detected, launched, analyzing, found_cause, proposed_fix, pr_created, completed
    event_title = Column(String(200), nullable=False)
    event_description = Column(Text)
    event_icon = Column(String(50))  # Icon identifier for UI
    
    # Event data
    data = Column(JSON, default={})  # Flexible storage for event-specific data
    log_output = Column(Text)
    error_message = Column(Text)
    
    # Timing
    timestamp = Column(DateTime, default=func.now())
    duration_seconds = Column(Float)  # Time taken for this step
    
    # Relationships
    investigation = relationship("Investigation", back_populates="timeline_events")
    agent = relationship("Agent", back_populates="timeline_events")
    
    __table_args__ = (
        Index('idx_timeline_investigation', 'investigation_id'),
        Index('idx_timeline_timestamp', 'timestamp'),
    )


class AgentDLQMapping(Base):
    """Agent to DLQ assignment matrix"""
    __tablename__ = 'agent_dlq_mappings'
    
    id = Column(Integer, primary_key=True)
    agent_id = Column(Integer, ForeignKey('agents.id'), nullable=False)
    dlq_pattern = Column(String(200), nullable=False)  # Can be exact name or pattern
    
    # Trigger configuration
    trigger_type = Column(String(50), default='message_count')  # message_count, regex, always, manual
    trigger_rule = Column(JSON, default={})  # e.g., {"threshold": 50, "regex": ".*Error.*"}
    
    # Environment configuration
    environment = Column(String(20), default='all')  # all, prod, staging, dev
    region = Column(String(20), default='all')  # all, sa-east-1, us-east-1, etc.
    
    # Status
    enabled = Column(Boolean, default=True)
    priority = Column(Integer, default=10)  # Lower number = higher priority
    
    # Statistics
    times_triggered = Column(Integer, default=0)
    last_triggered = Column(DateTime)
    
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relationships
    agent = relationship("Agent", back_populates="dlq_mappings")
    
    __table_args__ = (
        UniqueConstraint('agent_id', 'dlq_pattern', 'environment', name='uq_agent_dlq_env'),
        Index('idx_mapping_enabled', 'enabled'),
        Index('idx_mapping_priority', 'priority'),
    )


class Metrics(Base):
    """System-wide metrics and statistics"""
    __tablename__ = 'metrics'
    
    id = Column(Integer, primary_key=True)
    metric_name = Column(String(100), nullable=False)
    metric_type = Column(String(50))  # counter, gauge, histogram
    
    # Values
    value = Column(Float, nullable=False)
    unit = Column(String(20))  # seconds, count, percentage, etc.
    
    # Context
    agent_id = Column(String(50))
    dlq_name = Column(String(200))
    environment = Column(String(20))
    
    # Time window
    period_start = Column(DateTime, nullable=False)
    period_end = Column(DateTime, nullable=False)
    
    # Aggregation
    samples = Column(Integer, default=1)
    min_value = Column(Float)
    max_value = Column(Float)
    avg_value = Column(Float)
    
    created_at = Column(DateTime, default=func.now())
    
    __table_args__ = (
        Index('idx_metrics_name', 'metric_name'),
        Index('idx_metrics_period', 'period_start', 'period_end'),
        Index('idx_metrics_agent', 'agent_id'),
    )


class PRHistory(Base):
    """Pull request tracking and history"""
    __tablename__ = 'pr_history'
    
    id = Column(Integer, primary_key=True)
    pr_number = Column(Integer, nullable=False)
    repo_name = Column(String(200), nullable=False)
    
    # PR details
    title = Column(String(500))
    description = Column(Text)
    author = Column(String(100))
    
    # Related investigation
    investigation_id = Column(String(100))
    dlq_name = Column(String(200))
    
    # Status tracking
    status = Column(String(20))  # open, merged, closed
    created_at = Column(DateTime)
    merged_at = Column(DateTime)
    closed_at = Column(DateTime)
    
    # Metrics
    lines_added = Column(Integer)
    lines_removed = Column(Integer)
    files_changed = Column(Integer)
    review_time_hours = Column(Float)
    
    # Approval tracking
    approved_by = Column(String(100))
    approval_time = Column(DateTime)
    
    extra_metadata = Column(JSON, default={})
    
    __table_args__ = (
        UniqueConstraint('pr_number', 'repo_name', name='uq_pr_repo'),
        Index('idx_pr_status', 'status'),
        Index('idx_pr_created', 'created_at'),
    )


class AgentPerformance(Base):
    """Agent performance tracking and ranking"""
    __tablename__ = 'agent_performance'
    
    id = Column(Integer, primary_key=True)
    agent_id = Column(String(50), nullable=False)
    
    # Time period
    period_type = Column(String(20))  # hourly, daily, weekly, monthly
    period_start = Column(DateTime, nullable=False)
    period_end = Column(DateTime, nullable=False)
    
    # Performance metrics
    investigations_count = Column(Integer, default=0)
    successful_count = Column(Integer, default=0)
    failed_count = Column(Integer, default=0)
    
    avg_resolution_time = Column(Float)  # seconds
    min_resolution_time = Column(Float)
    max_resolution_time = Column(Float)
    
    prs_created = Column(Integer, default=0)
    prs_merged = Column(Integer, default=0)
    
    # Calculated scores
    success_rate = Column(Float)  # percentage
    efficiency_score = Column(Float)  # custom calculation
    ranking = Column(Integer)  # rank among all agents
    
    created_at = Column(DateTime, default=func.now())
    
    __table_args__ = (
        UniqueConstraint('agent_id', 'period_type', 'period_start', name='uq_agent_period'),
        Index('idx_performance_agent', 'agent_id'),
        Index('idx_performance_period', 'period_type', 'period_start'),
        Index('idx_performance_ranking', 'ranking'),
    )


class SystemAlert(Base):
    """System alerts and notifications"""
    __tablename__ = 'system_alerts'
    
    id = Column(Integer, primary_key=True)
    alert_type = Column(String(50), nullable=False)  # critical, warning, info
    alert_category = Column(String(50))  # dlq, agent, investigation, system
    
    title = Column(String(200), nullable=False)
    message = Column(Text)
    
    # Related entities
    agent_id = Column(String(50))
    dlq_name = Column(String(200))
    investigation_id = Column(String(100))
    
    # Status
    status = Column(String(20), default='active')  # active, acknowledged, resolved
    acknowledged_by = Column(String(100))
    acknowledged_at = Column(DateTime)
    resolved_at = Column(DateTime)
    
    # Alert data
    data = Column(JSON, default={})
    actions = Column(JSON, default=[])  # Available actions for this alert
    
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    __table_args__ = (
        Index('idx_alert_type', 'alert_type'),
        Index('idx_alert_status', 'status'),
        Index('idx_alert_created', 'created_at'),
    )


# Database initialization helper
def init_database(db_path: str = "neurocenter.db"):
    """Initialize the database with all tables"""
    engine = create_engine(f'sqlite:///{db_path}', echo=False)
    Base.metadata.create_all(engine)
    return engine


def get_session(engine):
    """Get a database session"""
    Session = sessionmaker(bind=engine)
    return Session()