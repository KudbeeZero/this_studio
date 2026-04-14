"""
Pydantic schemas for Executive Dashboard V4.0

These models define all request/response schemas for the API.
They ensure type safety and input validation across the application.
"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr, Field, ConfigDict


# =============================================================================
# Auth Schemas
# =============================================================================

class UserCreate(BaseModel):
    """Schema for user registration."""
    email: EmailStr
    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=6)
    full_name: Optional[str] = None


class UserResponse(BaseModel):
    """Schema for user response (excludes sensitive data)."""
    model_config = ConfigDict(from_attributes=True)
    
    id: str
    email: EmailStr
    username: str
    full_name: Optional[str]
    created_at: datetime
    is_active: bool = True


class LoginRequest(BaseModel):
    """Schema for login request."""
    username: str
    password: str


class Token(BaseModel):
    """Schema for JWT token response."""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class TokenPayload(BaseModel):
    """Schema for decoded token payload."""
    sub: str  # user id
    username: str
    exp: int
    type: str  # "access" or "refresh"


class RefreshTokenRequest(BaseModel):
    """Schema for refresh token request."""
    refresh_token: str


# =============================================================================
# Dashboard Schemas
# =============================================================================

class AgentStats(BaseModel):
    """Schema for individual agent statistics."""
    agent_id: str
    agent_name: str
    status: str
    tasks_completed: int
    tasks_pending: int
    success_rate: float
    last_active: datetime


class LedgerEntry(BaseModel):
    """Schema for ledger transaction entry."""
    entry_id: str
    timestamp: datetime
    type: str  # "credit", "debit"
    amount: float
    description: str
    agent_id: Optional[str] = None
    status: str  # "completed", "pending", "failed"


class DashboardStats(BaseModel):
    """Schema for overall dashboard statistics."""
    total_agents: int
    active_agents: int
    total_tasks: int
    completed_tasks: int
    pending_tasks: int
    success_rate: float
    total_revenue: float
    total_expenses: float
    net_profit: float
    last_updated: datetime


class DashboardAgentsResponse(BaseModel):
    """Schema for agents list response."""
    agents: list[AgentStats]
    total: int
    page: int
    page_size: int


class DashboardLedgerResponse(BaseModel):
    """Schema for ledger response."""
    entries: list[LedgerEntry]
    total: int
    total_credits: float
    total_debits: float
    page: int
    page_size: int


class DashboardStatsResponse(BaseModel):
    """Schema for dashboard stats response."""
    stats: DashboardStats
    recent_activity: list[LedgerEntry] = Field(default_factory=list)


# =============================================================================
# Error Schemas
# =============================================================================

class ErrorResponse(BaseModel):
    """Schema for error responses."""
    error: str
    detail: Optional[str] = None
    status_code: int


class HealthCheckResponse(BaseModel):
    """Schema for health check response."""
    status: str
    version: str
    environment: str
    data_service: str
