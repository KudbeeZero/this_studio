"""
Database layer with abstract DataService for Executive Dashboard V4.0

This module provides a switchable data layer architecture:
- PlaceholderDataService: Uses mock data (current default)
- RealDataService: Connects to external API (future)

Simply set DATA_SERVICE=real in .env to switch to real data.
"""

from abc import ABC, abstractmethod
from datetime import datetime
from typing import Optional

from executive_dashboard.models import Agent, DashboardMetrics, LedgerTransaction, User


class DataService(ABC):
    """Abstract base class for data services.
    
    This allows swapping between placeholder and real data sources
    without changing any business logic. Just update DATA_SERVICE env var.
    """
    
    @abstractmethod
    async def get_dashboard_stats(self) -> DashboardMetrics:
        """Get overall dashboard statistics."""
        pass
    
    @abstractmethod
    async def get_agents(
        self,
        page: int = 1,
        page_size: int = 10
    ) -> tuple[list[Agent], int]:
        """Get paginated list of agents."""
        pass
    
    @abstractmethod
    async def get_ledger(
        self,
        page: int = 1,
        page_size: int = 10
    ) -> tuple[list[LedgerTransaction], float, float]:
        """Get paginated ledger entries with totals."""
        pass
    
    @abstractmethod
    async def get_user_by_username(self, username: str) -> Optional[User]:
        """Get user by username."""
        pass
    
    @abstractmethod
    async def get_user_by_id(self, user_id: str) -> Optional[User]:
        """Get user by ID."""
        pass
    
    @abstractmethod
    async def create_user(self, user: User) -> User:
        """Create a new user."""
        pass


class PlaceholderDataService(DataService):
    """Mock data service using in-memory storage.
    
    This is the default service for development and testing.
    Replace with RealDataService for production.
    """
    
    def __init__(self):
        self._users: dict[str, User] = {}
        self._agents: list[Agent] = []
        self._ledger: list[LedgerTransaction] = []
        self._initialize_mock_data()
    
    def _initialize_mock_data(self):
        """Initialize with sample mock data."""
        from datetime import timedelta
        
        now = datetime.utcnow()
        
        # Initialize mock agents
        self._agents = [
            Agent(
                agent_id="agent-001",
                agent_name="Alpha Agent",
                status="active",
                tasks_completed=145,
                tasks_pending=12,
                success_rate=0.96,
                last_active=now - timedelta(minutes=5)
            ),
            Agent(
                agent_id="agent-002",
                agent_name="Beta Agent",
                status="active",
                tasks_completed=89,
                tasks_pending=8,
                success_rate=0.92,
                last_active=now - timedelta(minutes=15)
            ),
            Agent(
                agent_id="agent-003",
                agent_name="Gamma Agent",
                status="idle",
                tasks_completed=67,
                tasks_pending=3,
                success_rate=0.88,
                last_active=now - timedelta(hours=2)
            ),
            Agent(
                agent_id="agent-004",
                agent_name="Delta Agent",
                status="active",
                tasks_completed=203,
                tasks_pending=21,
                success_rate=0.94,
                last_active=now - timedelta(minutes=30)
            ),
            Agent(
                agent_id="agent-005",
                agent_name="Epsilon Agent",
                status="offline",
                tasks_completed=34,
                tasks_pending=0,
                success_rate=0.85,
                last_active=now - timedelta(days=1)
            ),
        ]
        
        # Initialize mock ledger
        self._ledger = [
            LedgerTransaction(
                entry_id="txn-001",
                timestamp=now - timedelta(hours=1),
                type="credit",
                amount=1500.00,
                description="Service payment - Alpha Agent",
                agent_id="agent-001",
                status="completed"
            ),
            LedgerTransaction(
                entry_id="txn-002",
                timestamp=now - timedelta(hours=2),
                type="debit",
                amount=250.00,
                description="Infrastructure costs",
                status="completed"
            ),
            LedgerTransaction(
                entry_id="txn-003",
                timestamp=now - timedelta(hours=3),
                type="credit",
                amount=850.00,
                description="Service payment - Beta Agent",
                agent_id="agent-002",
                status="completed"
            ),
            LedgerTransaction(
                entry_id="txn-004",
                timestamp=now - timedelta(hours=4),
                type="credit",
                amount=1200.00,
                description="Service payment - Delta Agent",
                agent_id="agent-004",
                status="completed"
            ),
            LedgerTransaction(
                entry_id="txn-005",
                timestamp=now - timedelta(hours=5),
                type="debit",
                amount=500.00,
                description="Licensing fees",
                status="completed"
            ),
            LedgerTransaction(
                entry_id="txn-006",
                timestamp=now - timedelta(hours=6),
                type="credit",
                amount=675.00,
                description="Service payment - Gamma Agent",
                agent_id="agent-003",
                status="completed"
            ),
            LedgerTransaction(
                entry_id="txn-007",
                timestamp=now - timedelta(hours=7),
                type="debit",
                amount=150.00,
                description="Maintenance costs",
                status="completed"
            ),
            LedgerTransaction(
                entry_id="txn-008",
                timestamp=now - timedelta(days=1),
                type="credit",
                amount=2100.00,
                description="Monthly subscription - Enterprise",
                status="completed"
            ),
        ]
    
    async def get_dashboard_stats(self) -> DashboardMetrics:
        """Calculate dashboard metrics from mock data."""
        active_count = sum(1 for a in self._agents if a.status == "active")
        completed = sum(a.tasks_completed for a in self._agents)
        pending = sum(a.tasks_pending for a in self._agents)
        
        total_credits = sum(t.amount for t in self._ledger if t.type == "credit")
        total_debits = sum(t.amount for t in self._ledger if t.type == "debit")
        
        success_rates = [a.success_rate for a in self._agents if a.tasks_completed > 0]
        avg_success = sum(success_rates) / len(success_rates) if success_rates else 0.0
        
        return DashboardMetrics(
            total_agents=len(self._agents),
            active_agents=active_count,
            total_tasks=completed + pending,
            completed_tasks=completed,
            pending_tasks=pending,
            success_rate=round(avg_success, 4),
            total_revenue=round(total_credits, 2),
            total_expenses=round(total_debits, 2),
            net_profit=round(total_credits - total_debits, 2),
            last_updated=datetime.utcnow()
        )
    
    async def get_agents(
        self,
        page: int = 1,
        page_size: int = 10
    ) -> tuple[list[Agent], int]:
        """Get paginated agents."""
        start = (page - 1) * page_size
        end = start + page_size
        return self._agents[start:end], len(self._agents)
    
    async def get_ledger(
        self,
        page: int = 1,
        page_size: int = 10
    ) -> tuple[list[LedgerTransaction], float, float]:
        """Get paginated ledger entries."""
        # Sort by timestamp descending (newest first)
        sorted_ledger = sorted(self._ledger, key=lambda x: x.timestamp, reverse=True)
        
        start = (page - 1) * page_size
        end = start + page_size
        page_entries = sorted_ledger[start:end]
        
        total_credits = sum(t.amount for t in self._ledger if t.type == "credit")
        total_debits = sum(t.amount for t in self._ledger if t.type == "debit")
        
        return page_entries, total_credits, total_debits
    
    async def get_user_by_username(self, username: str) -> Optional[User]:
        """Get user by username from in-memory store."""
        for user in self._users.values():
            if user.username == username:
                return user
        return None
    
    async def get_user_by_id(self, user_id: str) -> Optional[User]:
        """Get user by ID from in-memory store."""
        return self._users.get(user_id)
    
    async def create_user(self, user: User) -> User:
        """Create a new user in memory."""
        self._users[user.id] = user
        return user


class RealDataService(DataService):
    """Real data service connecting to external API.
    
    This service fetches data from an external API.
    Configure REAL_API_BASE_URL and REAL_API_KEY in .env.
    """
    
    def __init__(self, base_url: str, api_key: str):
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self._users: dict[str, User] = {}
    
    async def get_dashboard_stats(self) -> DashboardMetrics:
        """Fetch dashboard stats from external API."""
        # TODO: Implement actual API call
        # Example: async with httpx.AsyncClient() as client:
        #     response = await client.get(f"{self.base_url}/dashboard/stats")
        #     data = response.json()
        
        # Placeholder implementation - replace with real API call
        raise NotImplementedError("RealDataService.get_dashboard_stats not implemented. Connect to your friend's API!")
    
    async def get_agents(
        self,
        page: int = 1,
        page_size: int = 10
    ) -> tuple[list[Agent], int]:
        """Fetch agents from external API."""
        # TODO: Implement actual API call
        raise NotImplementedError("RealDataService.get_agents not implemented. Connect to your friend's API!")
    
    async def get_ledger(
        self,
        page: int = 1,
        page_size: int = 10
    ) -> tuple[list[LedgerTransaction], float, float]:
        """Fetch ledger from external API."""
        # TODO: Implement actual API call
        raise NotImplementedError("RealDataService.get_ledger not implemented. Connect to your friend's API!")
    
    async def get_user_by_username(self, username: str) -> Optional[User]:
        """Get user from local cache (for auth purposes)."""
        return None
    
    async def get_user_by_id(self, user_id: str) -> Optional[User]:
        """Get user from local cache."""
        return None
    
    async def create_user(self, user: User) -> User:
        """Create user in local cache (for auth purposes)."""
        self._users[user.id] = user
        return user


# =============================================================================
# Factory function for dependency injection
# =============================================================================

def get_data_service() -> DataService:
    """Factory function to get the appropriate data service.
    
    Simply change DATA_SERVICE environment variable to switch:
    - "placeholder" -> PlaceholderDataService (default, for dev)
    - "real" -> RealDataService (for production with external API)
    
    This is the ONE PLACE you need to change to switch data sources!
    
    Note: Uses singleton pattern to ensure user data persists across requests.
    """
    from executive_dashboard.config import get_settings
    
    # Use a global singleton to persist data across requests
    global _data_service_instance
    
    if _data_service_instance is None:
        settings = get_settings()
        
        if settings.data_service == "real":
            _data_service_instance = RealDataService(
                base_url=settings.real_api_base_url,
                api_key=settings.real_api_key
            )
        else:
            _data_service_instance = PlaceholderDataService()
    
    return _data_service_instance


# Global singleton instance
_data_service_instance: Optional[DataService] = None
