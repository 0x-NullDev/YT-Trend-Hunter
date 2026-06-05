"""
YT Trend Hunter - Security & Authentication
JWT-based authentication, password hashing, and API key management.
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any, Dict, Optional

from jose import JWTError, jwt
from passlib.context import CryptContext
from loguru import logger

from app.core.config import settings

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# JWT constants
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24  # 24 hours
REFRESH_TOKEN_EXPIRE_DAYS = 30


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a plain text password against a hashed password.
    
    Args:
        plain_password: Plain text password
        hashed_password: Hashed password
        
    Returns:
        bool: True if password matches
    """
    return pwd_context.verify(plain_password, hashed_password)


def hash_password(password: str) -> str:
    """
    Hash a plain text password.
    
    Args:
        password: Plain text password
        
    Returns:
        str: Hashed password
    """
    return pwd_context.hash(password)


def create_access_token(
    data: Dict[str, Any],
    expires_delta: Optional[timedelta] = None,
) -> str:
    """
    Create a JWT access token.
    
    Args:
        data: Token payload data
        expires_delta: Token expiration time
        
    Returns:
        str: Encoded JWT token
    """
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (
        expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    to_encode.update({"exp": expire, "type": "access"})
    return jwt.encode(to_encode, settings.APP_SECRET_KEY, algorithm=ALGORITHM)


def create_refresh_token(
    data: Dict[str, Any],
    expires_delta: Optional[timedelta] = None,
) -> str:
    """
    Create a JWT refresh token.
    
    Args:
        data: Token payload data
        expires_delta: Token expiration time
        
    Returns:
        str: Encoded JWT token
    """
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (
        expires_delta or timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    )
    to_encode.update({"exp": expire, "type": "refresh"})
    return jwt.encode(to_encode, settings.APP_SECRET_KEY, algorithm=ALGORITHM)


def decode_token(token: str) -> Optional[Dict[str, Any]]:
    """
    Decode and validate a JWT token.
    
    Args:
        token: JWT token string
        
    Returns:
        Optional[Dict]: Decoded payload or None if invalid
    """
    try:
        payload = jwt.decode(
            token, settings.APP_SECRET_KEY, algorithms=[ALGORITHM]
        )
        return payload
    except JWTError as e:
        logger.warning(f"Token decode failed: {e}")
        return None


def validate_token_type(token: str, expected_type: str) -> Optional[Dict[str, Any]]:
    """
    Validate a token and check its type.
    
    Args:
        token: JWT token string
        expected_type: Expected token type (access/refresh)
        
    Returns:
        Optional[Dict]: Decoded payload or None if invalid
    """
    payload = decode_token(token)
    if payload is None:
        return None
    if payload.get("type") != expected_type:
        logger.warning(f"Invalid token type: expected {expected_type}, got {payload.get('type')}")
        return None
    return payload


def generate_api_key() -> str:
    """
    Generate a random API key.
    
    Returns:
        str: Generated API key
    """
    import secrets
    return f"ytth_{secrets.token_urlsafe(32)}"


class RateLimiter:
    """
    Simple in-memory rate limiter.
    Tracks request counts per client IP and enforces limits.
    """

    def __init__(self):
        self._requests: Dict[str, list] = {}

    async def check_rate_limit(self, client_ip: str) -> tuple:
        """
        Check if a client IP has exceeded the rate limit.
        
        Args:
            client_ip: Client IP address
            
        Returns:
            tuple: (is_limited: bool, remaining: int)
        """
        if not settings.RATE_LIMIT_ENABLED:
            return False, settings.RATE_LIMIT_REQUESTS

        now = datetime.now(timezone.utc)
        window_start = now - timedelta(seconds=settings.RATE_LIMIT_PERIOD)

        # Clean old entries
        if client_ip in self._requests:
            self._requests[client_ip] = [
                t for t in self._requests[client_ip] if t > window_start
            ]
        else:
            self._requests[client_ip] = []

        # Check limit
        current_count = len(self._requests.get(client_ip, []))
        if current_count >= settings.RATE_LIMIT_REQUESTS:
            return True, 0

        # Record request
        self._requests[client_ip].append(now)
        remaining = settings.RATE_LIMIT_REQUESTS - current_count - 1
        return False, remaining
