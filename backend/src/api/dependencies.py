"""
Authentication dependencies for FastAPI endpoints.
Provides JWT token extraction and role-based authorization.
Zero-LLM compliance: Simple deterministic auth validation.
"""

from typing import Optional
import uuid
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from jose import JWTError, jwt

from src.core.database import get_db
from src.core.config import settings
from src.models.database import User


# JWT Configuration (matches auth.py)
SECRET_KEY = settings.jwt_secret
ALGORITHM = settings.jwt_algorithm

# OAuth2 scheme for token extraction
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db)
) -> User:
    """
    Extract and validate user from JWT token.

    Args:
        token: JWT access token from Authorization header
        db: Database session

    Returns:
        User: Authenticated user object

    Raises:
        HTTPException 401: If token is invalid, expired, or user not found
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        # Decode JWT token
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        email: str = payload.get("email")
        role: str = payload.get("role")

        if user_id is None or email is None or role is None:
            raise credentials_exception

    except JWTError:
        raise credentials_exception

    # Query user from database
    try:
        user_id_uuid = uuid.UUID(user_id)
    except ValueError:
        raise credentials_exception

    result = await db.execute(select(User).where(User.id == user_id_uuid))
    user = result.scalar_one_or_none()

    if user is None:
        raise credentials_exception

    return user


async def require_teacher(
    current_user: User = Depends(get_current_user)
) -> User:
    """
    Verify user has teacher role.

    Use this dependency on endpoints that should only be accessible by teachers.

    Args:
        current_user: Authenticated user from get_current_user dependency

    Returns:
        User: The authenticated teacher user

    Raises:
        HTTPException 403: If user is not a teacher
    """
    if current_user.role != "teacher":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied. Teacher role required."
        )

    return current_user


async def require_student(
    current_user: User = Depends(get_current_user)
) -> User:
    """
    Verify user has student role.

    Use this dependency on endpoints that should only be accessible by students.

    Args:
        current_user: Authenticated user from get_current_user dependency

    Returns:
        User: The authenticated student user

    Raises:
        HTTPException 403: If user is not a student
    """
    if current_user.role != "student":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied. Student role required."
        )

    return current_user


async def get_optional_user(
    token: Optional[str] = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db)
) -> Optional[User]:
    """
    Optional authentication - returns user if token provided, None otherwise.

    Use this dependency on endpoints that work for both authenticated and
    anonymous users, but provide enhanced features for authenticated users.

    Args:
        token: JWT access token from Authorization header (optional)
        db: Database session

    Returns:
        Optional[User]: User object if token valid, None if no token or invalid
    """
    if token is None:
        return None

    try:
        return await get_current_user(token, db)
    except HTTPException:
        return None
