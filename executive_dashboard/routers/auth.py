"""
Authentication router for Executive Dashboard V4.0

Handles all authentication endpoints:
- POST /api/auth/register - Register new user
- POST /api/auth/login - Login and get tokens
- POST /api/auth/refresh - Refresh access token
- GET /api/auth/me - Get current user info
"""

import logging
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

from executive_dashboard.auth import (
    AuthService,
    create_access_token,
    create_refresh_token,
    get_auth_service,
)
from executive_dashboard.schemas import (
    LoginRequest,
    Token,
    UserCreate,
    UserResponse,
)

logger = logging.getLogger(__name__)

# Create router with prefix
router = APIRouter(prefix="/api/auth", tags=["Authentication"])


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(
    user_data: UserCreate,
    auth_service: AuthService = Depends(get_auth_service)
) -> UserResponse:
    """Register a new user account.
    
    Creates a new user with the provided credentials.
    The password will be hashed using bcrypt.
    
    Args:
        user_data: User registration data
        
    Returns:
        Created user information (without password)
        
    Raises:
        HTTPException 400: If username or email already exists
    """
    logger.info(f"Registration attempt for username: {user_data.username}")
    
    try:
        user = await auth_service.register_user(
            email=user_data.email,
            username=user_data.username,
            password=user_data.password,
            full_name=user_data.full_name
        )
        
        return UserResponse(
            id=user.id,
            email=user.email,
            username=user.username,
            full_name=user.full_name,
            created_at=user.created_at,
            is_active=user.is_active
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Registration failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Registration failed"
        )


@router.post("/login", response_model=Token)
async def login(
    login_data: LoginRequest,
    auth_service: AuthService = Depends(get_auth_service)
) -> Token:
    """Login with username and password.
    
    Authenticates the user and returns JWT access and refresh tokens.
    
    Args:
        login_data: Username and password
        
    Returns:
        Access and refresh tokens
        
    Raises:
        HTTPException 401: If credentials are invalid
    """
    logger.info(f"Login attempt for username: {login_data.username}")
    
    user = await auth_service.authenticate_user(
        username=login_data.username,
        password=login_data.password
    )
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    # Generate tokens
    access_token = create_access_token(user)
    refresh_token = create_refresh_token(user)
    
    logger.info(f"User '{user.username}' logged in successfully")
    
    return Token(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer"
    )


@router.post("/login/form", response_model=Token)
async def login_form(
    form_data: OAuth2PasswordRequestForm = Depends(),
    auth_service: AuthService = Depends(get_auth_service)
) -> Token:
    """Login with form data (OAuth2 compatible).
    
    This endpoint supports OAuth2 password flow for integration
    with standard OAuth2 clients.
    
    Args:
        form_data: Form with username and password
        
    Returns:
        Access and refresh tokens
    """
    logger.info(f"Login form attempt for username: {form_data.username}")
    
    user = await auth_service.authenticate_user(
        username=form_data.username,
        password=form_data.password
    )
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    access_token = create_access_token(user)
    refresh_token = create_refresh_token(user)
    
    return Token(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer"
    )


@router.post("/refresh", response_model=Token)
async def refresh_token(
    refresh_token: str,
    auth_service: AuthService = Depends(get_auth_service)
) -> Token:
    """Refresh access token using refresh token.
    
    Use this endpoint to get a new access token without
    requiring the user to log in again.
    
    Args:
        refresh_token: Valid refresh token
        
    Returns:
        New access and refresh tokens
        
    Raises:
        HTTPException 401: If refresh token is invalid
    """
    from executive_dashboard.auth import decode_token
    
    logger.info("Token refresh attempt")
    
    try:
        token_data = decode_token(refresh_token)
        
        if token_data.type != "refresh":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token type. Expected refresh token."
            )
        
        # Get user from database
        from executive_dashboard.database import get_data_service
        data_service = get_data_service()
        user = await data_service.get_user_by_id(token_data.sub)
        
        if not user or not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found or inactive"
            )
        
        # Generate new tokens
        access_token = create_access_token(user)
        new_refresh_token = create_refresh_token(user)
        
        logger.info(f"Token refreshed for user: {user.username}")
        
        return Token(
            access_token=access_token,
            refresh_token=new_refresh_token,
            token_type="bearer"
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Token refresh failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token"
        )


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user = Depends(get_auth_service)
) -> UserResponse:
    """Get current authenticated user information.
    
    Requires a valid access token.
    
    Returns:
        Current user information
    """
    from executive_dashboard.auth import get_current_user
    
    user = await get_current_user()
    
    return UserResponse(
        id=user.id,
        email=user.email,
        username=user.username,
        full_name=user.full_name,
        created_at=user.created_at,
        is_active=user.is_active
    )
