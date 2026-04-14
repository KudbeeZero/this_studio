"""
Authentication layer for Executive Dashboard V4.0

This module handles:
- JWT token creation and validation
- Password hashing with bcrypt
- User authentication and authorization
- OAuth2 password bearer flow
"""

import logging
from datetime import datetime, timedelta
from typing import Optional

import bcrypt
import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

from executive_dashboard.config import get_settings
from executive_dashboard.database import DataService, get_data_service
from executive_dashboard.models import User
from executive_dashboard.schemas import TokenPayload

# Configure logging
logger = logging.getLogger(__name__)

# OAuth2 scheme
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")

# Password hashing constant
PASSWORD_HASH_ROUNDS = 12


# =============================================================================
# Password Utilities
# =============================================================================

def hash_password(password: str) -> str:
    """Hash a password using bcrypt.
    
    Args:
        password: Plain text password
        
    Returns:
        Hashed password string
    """
    salt = bcrypt.gensalt(rounds=PASSWORD_HASH_ROUNDS)
    return bcrypt.hashpw(password.encode("utf-8"), salt).decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash.
    
    Args:
        plain_password: Plain text password to verify
        hashed_password: Hashed password to compare against
        
    Returns:
        True if password matches, False otherwise
    """
    return bcrypt.checkpw(
        plain_password.encode("utf-8"),
        hashed_password.encode("utf-8")
    )


# =============================================================================
# JWT Token Utilities
# =============================================================================

def create_access_token(user: User) -> str:
    """Create a JWT access token for a user.
    
    Args:
        user: User object to create token for
        
    Returns:
        Encoded JWT token string
    """
    from uuid import uuid4
    
    settings = get_settings()
    
    expire = datetime.utcnow() + timedelta(minutes=settings.access_token_expire_minutes)
    
    payload = {
        "sub": user.id,
        "username": user.username,
        "exp": int(expire.timestamp()),
        "type": "access",
        "jti": str(uuid4())  # JWT ID for token revocation
    }
    
    return jwt.encode(payload, settings.secret_key, algorithm=settings.algorithm)


def create_refresh_token(user: User) -> str:
    """Create a JWT refresh token for a user.
    
    Args:
        user: User object to create token for
        
    Returns:
        Encoded JWT refresh token string
    """
    from uuid import uuid4
    
    settings = get_settings()
    
    expire = datetime.utcnow() + timedelta(minutes=settings.refresh_token_expire_minutes)
    
    payload = {
        "sub": user.id,
        "username": user.username,
        "exp": int(expire.timestamp()),
        "type": "refresh",
        "jti": str(uuid4())
    }
    
    return jwt.encode(payload, settings.secret_key, algorithm=settings.algorithm)


def decode_token(token: str) -> TokenPayload:
    """Decode and validate a JWT token.
    
    Args:
        token: JWT token string to decode
        
    Returns:
        TokenPayload if valid
        
    Raises:
        HTTPException: If token is invalid or expired
    """
    settings = get_settings()
    
    try:
        payload = jwt.decode(
            token,
            settings.secret_key,
            algorithms=[settings.algorithm]
        )
        
        return TokenPayload(
            sub=payload.get("sub"),
            username=payload.get("username"),
            exp=payload.get("exp"),
            type=payload.get("type")
        )
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired",
            headers={"WWW-Authenticate": "Bearer"}
        )
    except jwt.InvalidTokenError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid token: {str(e)}",
            headers={"WWW-Authenticate": "Bearer"}
        )


# =============================================================================
# Authentication Dependencies
# =============================================================================

async def get_current_user(
    token: str = Depends(oauth2_scheme),
    data_service: DataService = Depends(get_data_service)
) -> User:
    """Get current authenticated user from JWT token.
    
    This is a FastAPI dependency that validates the access token
    and returns the current user.
    
    Args:
        token: JWT access token from Authorization header
        data_service: Data service for user lookup
        
    Returns:
        User object if valid token
        
    Raises:
        HTTPException: If token is invalid or user not found
    """
    token_data = decode_token(token)
    
    if token_data.type != "access":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token type",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    user = await data_service.get_user_by_id(token_data.sub)
    
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User is inactive"
        )
    
    return user


async def get_current_active_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """Get current active user (ensures user is active).
    
    Args:
        current_user: Current user from token validation
        
    Returns:
        Active user object
        
    Raises:
        HTTPException: If user is inactive
    """
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User is inactive"
        )
    return current_user


# =============================================================================
# Authentication Service
# =============================================================================

class AuthService:
    """Service for handling authentication operations."""
    
    def __init__(self, data_service: DataService):
        self.data_service = data_service
    
    async def authenticate_user(self, username: str, password: str) -> Optional[User]:
        """Authenticate a user with username and password.
        
        Args:
            username: User's username
            password: User's plain text password
            
        Returns:
            User object if authentication successful, None otherwise
        """
        user = await self.data_service.get_user_by_username(username)
        
        if not user:
            logger.warning(f"Authentication failed: user '{username}' not found")
            return None
        
        if not verify_password(password, user.hashed_password):
            logger.warning(f"Authentication failed: invalid password for user '{username}'")
            return None
        
        if not user.is_active:
            logger.warning(f"Authentication failed: user '{username}' is inactive")
            return None
        
        logger.info(f"User '{username}' authenticated successfully")
        return user
    
    async def register_user(
        self,
        email: str,
        username: str,
        password: str,
        full_name: Optional[str] = None
    ) -> User:
        """Register a new user.
        
        Args:
            email: User's email address
            username: User's desired username
            password: User's plain text password
            full_name: User's full name (optional)
            
        Returns:
            Created User object
            
        Raises:
            HTTPException: If username or email already exists
        """
        # Check if username already exists
        existing_user = await self.data_service.get_user_by_username(username)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already registered"
            )
        
        # Create new user with hashed password
        from uuid import uuid4
        
        new_user = User(
            id=str(uuid4()),
            email=email,
            username=username,
            hashed_password=hash_password(password),
            full_name=full_name,
            created_at=datetime.utcnow(),
            is_active=True
        )
        
        created_user = await self.data_service.create_user(new_user)
        logger.info(f"New user registered: {username}")
        
        return created_user


def get_auth_service() -> AuthService:
    """Get authentication service instance.
    
    Returns:
        AuthService instance
    """
    return AuthService(get_data_service())
