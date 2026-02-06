"""
Authentication API endpoints.
Handles user registration, login, and token management.
Zero-LLM compliance: Simple JWT-based auth without AI.
"""

from datetime import datetime, timedelta
from typing import Optional
import uuid
import bcrypt
from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from jose import JWTError, jwt
from pydantic import BaseModel
from fastapi.responses import JSONResponse

from src.core.database import get_db
from src.core.config import settings
from src.models.database import User


# Request/Response Models
class RegisterRequest(BaseModel):
    email: str
    password: str
    role: str = "student"


class LoginRequest(BaseModel):
    email: str
    password: str

router = APIRouter()


# JWT Configuration
SECRET_KEY = settings.jwt_secret if hasattr(settings, 'jwt_secret') else "your-secret-key-change-in-production"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30 * 24 * 60  # 30 days

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """Create JWT access token."""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


@router.post("/auth/register", tags=["Authentication"])
async def register(
    request: RegisterRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Register a new user account.

    - **email**: User email address (must be unique)
    - **password**: User password (min 6 characters)
    - **role**: User role - "student" or "teacher" (default: "student")

    Returns access token and user ID on successful registration.
    """
    email = request.email
    password = request.password
    role = request.role

    # Validate role
    if role not in ["student", "teacher"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Role must be either 'student' or 'teacher'"
        )

    # Validate password length
    if len(password) < 6:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Password must be at least 6 characters"
        )

    # Check if user already exists
    result = await db.execute(select(User).where(User.email == email))
    existing_user = result.scalar_one_or_none()

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )

    # Hash password
    salt = bcrypt.gensalt(rounds=12)
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')

    # Create new user
    new_user = User(
        id=uuid.uuid4(),
        email=email,
        hashed_password=hashed_password,
        tier="FREE",  # All users start at FREE tier
        role=role,
        created_at=datetime.utcnow(),
        last_login=datetime.utcnow()
    )

    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)

    # Create access token
    access_token = create_access_token(
        data={"sub": str(new_user.id), "email": new_user.email, "role": role}
    )

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user_id": str(new_user.id),
        "email": new_user.email,
        "role": role,
        "tier": "FREE"
    }


@router.post("/auth/login", tags=["Authentication"])
async def login(
    request: LoginRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Authenticate user and return access token.

    - **email**: User email address
    - **password**: User password

    Returns access token and user info on successful login.
    """
    email = request.email
    password = request.password

    # Find user by email
    result = await db.execute(select(User).where(User.email == email))
    user = result.scalar_one_or_none()

    # Verify user exists and password is correct
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Verify password
    try:
        is_valid = bcrypt.checkpw(password.encode('utf-8'), user.hashed_password.encode('utf-8'))
    except Exception:
        is_valid = False

    if not is_valid:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Update last login
    user.last_login = datetime.utcnow()
    await db.commit()

    # Create access token
    access_token = create_access_token(
        data={"sub": str(user.id), "email": user.email, "role": user.role}
    )

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user_id": str(user.id),
        "email": user.email,
        "role": user.role,
        "tier": user.tier
    }


@router.get("/auth/me", tags=["Authentication"])
async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db)
):
    """
    Get current user information from JWT token.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    # Get user from database
    result = await db.execute(select(User).where(User.id == uuid.UUID(user_id)))
    user = result.scalar_one_or_none()

    if user is None:
        raise credentials_exception

    return {
        "user_id": str(user.id),
        "email": user.email,
        "role": user.role,
        "tier": user.tier,
        "created_at": user.created_at.isoformat(),
        "last_login": user.last_login.isoformat()
    }
