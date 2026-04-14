"""
Data models for Executive Dashboard V4.0

These are the internal domain models used throughout the application.
They differ from schemas which are used for API request/response.
"""

from datetime import datetime
from typing import Optional
from dataclasses import dataclass, field


@dataclass
class User:
    """Internal user model."""
    id: str
    email: str
    username: str
    hashed_password: str
    full_name: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.utcnow)
    is_active: bool = True
    is_superuser: bool = False


@dataclass
class Agent:
    """Internal agent model."""
    agent_id: str
    agent_name: str
    status: str
    tasks_completed: int = 0
    tasks_pending: int = 0
    success_rate: float = 0.0
    last_active: datetime = field(default_factory=datetime.utcnow)


@dataclass
class LedgerTransaction:
    """Internal ledger transaction model."""
    entry_id: str
    timestamp: datetime
    type: str  # "credit", "debit"
    amount: float
    description: str
    agent_id: Optional[str] = None
    status: str = "completed"


@dataclass
class DashboardMetrics:
    """Internal dashboard metrics model."""
    total_agents: int = 0
    active_agents: int = 0
    total_tasks: int = 0
    completed_tasks: int = 0
    pending_tasks: int = 0
    success_rate: float = 0.0
    total_revenue: float = 0.0
    total_expenses: float = 0.0
    net_profit: float = 0.0
    last_updated: datetime = field(default_factory=datetime.utcnow)
