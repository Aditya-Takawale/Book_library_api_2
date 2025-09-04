from pydantic import BaseModel, EmailStr, validator, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum
import re

class UserRole(str, Enum):
    ADMIN = "admin"
    LIBRARIAN = "librarian"
    MEMBER = "member"
    GUEST = "guest"

class UserStatus(str, Enum):
    ACTIVE = "active"
    SUSPENDED = "suspended"
    PENDING = "pending"
    DELETED = "deleted"

class UserRegistration(BaseModel):
    email: EmailStr = Field(..., description="Valid email address")
    username: str = Field(..., min_length=3, max_length=50, description="Username (3-50 characters)")
    password: str = Field(..., min_length=8, description="Password (minimum 8 characters)")
    first_name: Optional[str] = Field(None, max_length=100, description="First name")
    last_name: Optional[str] = Field(None, max_length=100, description="Last name")
    role: UserRole = Field(UserRole.MEMBER, description="User role")
    
    @validator('username')
    def validate_username(cls, v):
        if not re.match("^[a-zA-Z0-9_-]+$", v):
            raise ValueError('Username can only contain letters, numbers, underscores, and hyphens')
        return v
    
    @validator('password')
    def validate_password_strength(cls, v):
        """
        Password requirements:
        - At least 8 characters
        - At least one uppercase letter
        - At least one lowercase letter
        - At least one digit
        - At least one special character
        """
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        
        if not re.search(r'[A-Z]', v):
            raise ValueError('Password must contain at least one uppercase letter')
        
        if not re.search(r'[a-z]', v):
            raise ValueError('Password must contain at least one lowercase letter')
        
        if not re.search(r'\d', v):
            raise ValueError('Password must contain at least one digit')
        
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', v):
            raise ValueError('Password must contain at least one special character (!@#$%^&*(),.?":{}|<>)')
        
        return v

class UserResponse(BaseModel):
    id: int
    email: str
    username: str
    first_name: Optional[str]
    last_name: Optional[str]
    role: UserRole
    status: UserStatus
    is_active: bool
    email_verified: bool
    last_login: Optional[datetime]
    failed_login_attempts: int
    permissions: List[str] = []
    created_at: datetime
    
    class Config:
        from_attributes = True
        use_enum_values = True

class UserUpdate(BaseModel):
    first_name: Optional[str] = Field(None, max_length=100)
    last_name: Optional[str] = Field(None, max_length=100)
    role: Optional[UserRole] = None
    status: Optional[UserStatus] = None
    email_verified: Optional[bool] = None

class UserLogin(BaseModel):
    email: EmailStr = Field(..., description="Email address")
    password: str = Field(..., description="Password")

class PasswordChangeRequest(BaseModel):
    current_password: str = Field(..., description="Current password")
    new_password: str = Field(..., min_length=8, description="New password")
    
    @validator('new_password')
    def validate_new_password_strength(cls, v):
        # Same validation as registration
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        
        if not re.search(r'[A-Z]', v):
            raise ValueError('Password must contain at least one uppercase letter')
        
        if not re.search(r'[a-z]', v):
            raise ValueError('Password must contain at least one lowercase letter')
        
        if not re.search(r'\d', v):
            raise ValueError('Password must contain at least one digit')
        
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', v):
            raise ValueError('Password must contain at least one special character')
        
        return v
