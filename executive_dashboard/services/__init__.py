"""
Business services layer for Executive Dashboard V4.0

This module contains business logic that coordinates between
routers and the data layer. It encapsulates complex operations
and provides a clean interface for the API layer.
"""

import logging
from typing import Optional

from executive_dashboard.database import DataService, get_data_service
from executive_dashboard.models import User
from executive_dashboard.schemas import (
    AgentStats,
    DashboardAgentsResponse,
    DashboardLedgerResponse,
    DashboardStatsResponse,
    LedgerEntry,
)

logger = logging.getLogger(__name__)


class DashboardService:
    """Service for dashboard operations.
    
    This service handles all business logic related to the executive
    dashboard, including stats, agents, and ledger management.
    """
    
    def __init__(self, data_service: DataService):
        self.data_service = data_service
    
    async def get_stats(self) -> DashboardStatsResponse:
        """Get comprehensive dashboard statistics.
        
        Returns:
            DashboardStatsResponse with all metrics
        """
        logger.info("Fetching dashboard statistics")
        
        stats = await self.data_service.get_dashboard_stats()
        
        # Get recent activity (last 5 ledger entries)
        recent_entries, _, _ = await self.data_service.get_ledger(page=1, page_size=5)
        
        # Convert to schema format
        recent_activity = [
            LedgerEntry(
                entry_id=e.entry_id,
                timestamp=e.timestamp,
                type=e.type,
                amount=e.amount,
                description=e.description,
                agent_id=e.agent_id,
                status=e.status
            )
            for e in recent_entries
        ]
        
        from executive_dashboard.schemas import DashboardStats
        
        stats_schema = DashboardStats(
            total_agents=stats.total_agents,
            active_agents=stats.active_agents,
            total_tasks=stats.total_tasks,
            completed_tasks=stats.completed_tasks,
            pending_tasks=stats.pending_tasks,
            success_rate=stats.success_rate,
            total_revenue=stats.total_revenue,
            total_expenses=stats.total_expenses,
            net_profit=stats.net_profit,
            last_updated=stats.last_updated
        )
        
        return DashboardStatsResponse(
            stats=stats_schema,
            recent_activity=recent_activity
        )
    
    async def get_agents(
        self,
        page: int = 1,
        page_size: int = 10
    ) -> DashboardAgentsResponse:
        """Get paginated list of agents.
        
        Args:
            page: Page number (1-indexed)
            page_size: Number of items per page
            
        Returns:
            DashboardAgentsResponse with agents list
        """
        logger.info(f"Fetching agents: page={page}, page_size={page_size}")
        
        agents, total = await self.data_service.get_agents(page=page, page_size=page_size)
        
        # Convert to schema format
        agent_stats = [
            AgentStats(
                agent_id=a.agent_id,
                agent_name=a.agent_name,
                status=a.status,
                tasks_completed=a.tasks_completed,
                tasks_pending=a.tasks_pending,
                success_rate=a.success_rate,
                last_active=a.last_active
            )
            for a in agents
        ]
        
        return DashboardAgentsResponse(
            agents=agent_stats,
            total=total,
            page=page,
            page_size=page_size
        )
    
    async def get_ledger(
        self,
        page: int = 1,
        page_size: int = 10
    ) -> DashboardLedgerResponse:
        """Get paginated ledger entries.
        
        Args:
            page: Page number (1-indexed)
            page_size: Number of items per page
            
        Returns:
            DashboardLedgerResponse with ledger entries
        """
        logger.info(f"Fetching ledger: page={page}, page_size={page_size}")
        
        entries, total_credits, total_debits = await self.data_service.get_ledger(
            page=page, page_size=page_size
        )
        
        # Convert to schema format
        ledger_entries = [
            LedgerEntry(
                entry_id=e.entry_id,
                timestamp=e.timestamp,
                type=e.type,
                amount=e.amount,
                description=e.description,
                agent_id=e.agent_id,
                status=e.status
            )
            for e in entries
        ]
        
        # Get total count
        all_entries, _, _ = await self.data_service.get_ledger(page=1, page_size=10000)
        total = len(all_entries)
        
        return DashboardLedgerResponse(
            entries=ledger_entries,
            total=total,
            total_credits=total_credits,
            total_debits=total_debits,
            page=page,
            page_size=page_size
        )


def get_dashboard_service() -> DashboardService:
    """Get dashboard service instance.
    
    Returns:
        DashboardService instance
    """
    return DashboardService(get_data_service())
