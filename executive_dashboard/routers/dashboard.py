"""
Dashboard router for Executive Dashboard V4.0

Handles all dashboard API endpoints:
- GET /api/dashboard/stats - Get overall statistics
- GET /api/dashboard/agents - Get agent list
- GET /api/dashboard/ledger - Get ledger transactions
"""

import logging

from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.security import OAuth2PasswordBearer

from executive_dashboard.auth import get_current_user
from executive_dashboard.database import get_data_service, DataService
from executive_dashboard.models import User
from executive_dashboard.schemas import (
    DashboardAgentsResponse,
    DashboardLedgerResponse,
    DashboardStatsResponse,
)
from executive_dashboard.services import DashboardService, get_dashboard_service

logger = logging.getLogger(__name__)

# Create router with prefix
router = APIRouter(prefix="/api/dashboard", tags=["Dashboard"])

# OAuth2 scheme (reuse from auth)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")


async def get_current_user_dep(
    token: str = Depends(oauth2_scheme)
) -> User:
    """Dependency to get current authenticated user."""
    from executive_dashboard.auth import get_current_user as gc_user
    return await gc_user(token, get_data_service())


@router.get("/stats", response_model=DashboardStatsResponse)
async def get_dashboard_stats(
    current_user: User = Depends(get_current_user_dep),
    dashboard_service: DashboardService = Depends(get_dashboard_service)
) -> DashboardStatsResponse:
    """Get dashboard statistics.
    
    Returns comprehensive statistics including:
    - Total and active agent counts
    - Task completion metrics
    - Financial summary (revenue, expenses, profit)
    
    Requires authentication.
    
    Args:
        current_user: Authenticated user
        dashboard_service: Dashboard service
        
    Returns:
        Dashboard statistics and recent activity
    """
    logger.info(f"Fetching dashboard stats for user: {current_user.username}")
    
    try:
        return await dashboard_service.get_stats()
    except Exception as e:
        logger.error(f"Failed to fetch dashboard stats: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch dashboard statistics"
        )


@router.get("/agents", response_model=DashboardAgentsResponse)
async def get_agents(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(10, ge=1, le=100, description="Items per page"),
    current_user: User = Depends(get_current_user_dep),
    dashboard_service: DashboardService = Depends(get_dashboard_service)
) -> DashboardAgentsResponse:
    """Get paginated list of agents.
    
    Returns agent information including:
    - Agent ID and name
    - Current status
    - Tasks completed/pending
    - Success rate
    
    Requires authentication.
    
    Args:
        page: Page number (1-indexed)
        page_size: Items per page
        current_user: Authenticated user
        dashboard_service: Dashboard service
        
    Returns:
        Paginated list of agents
    """
    logger.info(f"Fetching agents for user: {current_user.username}, page={page}")
    
    try:
        return await dashboard_service.get_agents(page=page, page_size=page_size)
    except Exception as e:
        logger.error(f"Failed to fetch agents: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch agents"
        )


@router.get("/ledger", response_model=DashboardLedgerResponse)
async def get_ledger(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(10, ge=1, le=100, description="Items per page"),
    current_user: User = Depends(get_current_user_dep),
    dashboard_service: DashboardService = Depends(get_dashboard_service)
) -> DashboardLedgerResponse:
    """Get paginated ledger transactions.
    
    Returns financial transactions including:
    - Transaction ID and timestamp
    - Type (credit/debit)
    - Amount and description
    - Associated agent (if applicable)
    - Status
    
    Also returns total credits and debits.
    
    Requires authentication.
    
    Args:
        page: Page number (1-indexed)
        page_size: Items per page
        current_user: Authenticated user
        dashboard_service: Dashboard service
        
    Returns:
        Paginated ledger entries with totals
    """
    logger.info(f"Fetching ledger for user: {current_user.username}, page={page}")
    
    try:
        return await dashboard_service.get_ledger(page=page, page_size=page_size)
    except Exception as e:
        logger.error(f"Failed to fetch ledger: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch ledger"
        )
