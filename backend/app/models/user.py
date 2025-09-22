from sqlalchemy import Column, Integer, String, Boolean, DateTime, Enum, Index
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.db import Base
import enum
from typing import List

class UserRole(enum.Enum):
    ADMIN = "Admin"
    MEMBER = "Member"
    LIBRARIAN = "Librarian"  # New role for library staff
    GUEST = "Guest"  # New role for limited access

class UserStatus(enum.Enum):
    ACTIVE = "Active"
    SUSPENDED = "Suspended"
    PENDING = "Pending"
    DELETED = "Deleted"

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    username = Column(String(100), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    first_name = Column(String(100), nullable=True)
    last_name = Column(String(100), nullable=True)
    role = Column(Enum(UserRole), default=UserRole.MEMBER, nullable=False)
    status = Column(Enum(UserStatus), default=UserStatus.ACTIVE, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    email_verified = Column(Boolean, default=False, nullable=False)
    last_login = Column(DateTime(timezone=True), nullable=True)
    failed_login_attempts = Column(Integer, default=0, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships with proper cascade operations
    reviews = relationship("BookReview", back_populates="user", cascade="all, delete-orphan")
    review_votes = relationship("ReviewVote", back_populates="user", cascade="all, delete-orphan")
    borrowed_books = relationship("BookLoan", foreign_keys="BookLoan.user_id", back_populates="user", cascade="all, delete-orphan")
    created_loans = relationship("BookLoan", foreign_keys="BookLoan.created_by", cascade="all, delete-orphan")
    
    # Indexes for performance
    __table_args__ = (
        Index('idx_user_email_status', 'email', 'status'),
        Index('idx_user_role_status', 'role', 'status'),
        Index('idx_user_created_at', 'created_at'),
    )
    
    def __repr__(self):
        return f"<User(id={self.id}, email='{self.email}', username='{self.username}', role='{self.role.value}')>"
    
    # Permission methods for RBAC
    def is_admin(self) -> bool:
        """Check if user has admin privileges."""
        return self.role == UserRole.ADMIN and self.status == UserStatus.ACTIVE
    
    def is_librarian(self) -> bool:
        """Check if user has librarian privileges."""
        return self.role in [UserRole.ADMIN, UserRole.LIBRARIAN] and self.status == UserStatus.ACTIVE
    
    def can_manage_books(self) -> bool:
        """Check if user can create/edit/delete books."""
        return self.role in [UserRole.ADMIN, UserRole.LIBRARIAN] and self.status == UserStatus.ACTIVE
    
    def can_manage_authors(self) -> bool:
        """Check if user can create/edit/delete authors."""
        return self.role in [UserRole.ADMIN, UserRole.LIBRARIAN] and self.status == UserStatus.ACTIVE
    
    def can_manage_users(self) -> bool:
        """Check if user can manage other users."""
        return self.role == UserRole.ADMIN and self.status == UserStatus.ACTIVE
    
    def can_access_admin_panel(self) -> bool:
        """Check if user can access admin functionality."""
        return self.role in [UserRole.ADMIN, UserRole.LIBRARIAN] and self.status == UserStatus.ACTIVE
    
    def can_create_review(self) -> bool:
        """Check if user can create reviews."""
        return self.role in [UserRole.ADMIN, UserRole.LIBRARIAN, UserRole.MEMBER] and self.status == UserStatus.ACTIVE
    
    def can_vote_on_reviews(self) -> bool:
        """Check if user can vote on reviews."""
        return self.role in [UserRole.ADMIN, UserRole.LIBRARIAN, UserRole.MEMBER] and self.status == UserStatus.ACTIVE
    
    def can_borrow_books(self) -> bool:
        """Check if user can borrow books."""
        return self.role in [UserRole.ADMIN, UserRole.LIBRARIAN, UserRole.MEMBER] and self.status == UserStatus.ACTIVE
    
    def has_permission(self, permission: str) -> bool:
        """Generic permission checker."""
        permission_map = {
            'admin': self.is_admin(),
            'librarian': self.is_librarian(),
            'manage_books': self.can_manage_books(),
            'manage_authors': self.can_manage_authors(),
            'manage_users': self.can_manage_users(),
            'admin_panel': self.can_access_admin_panel(),
            'create_review': self.can_create_review(),
            'vote_reviews': self.can_vote_on_reviews(),
            'borrow_books': self.can_borrow_books(),
        }
        return permission_map.get(permission, False)
    
    @property
    def full_name(self) -> str:
        """Get user's full name."""
        if self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name}"
        return self.username
    
    @property
    def permissions(self) -> List[str]:
        """Get list of user permissions."""
        perms = []
        if self.is_admin():
            perms.extend(['admin', 'manage_books', 'manage_authors', 'manage_users', 'admin_panel'])
        if self.is_librarian():
            perms.extend(['librarian', 'manage_books', 'manage_authors', 'admin_panel'])
        if self.can_create_review():
            perms.append('create_review')
        if self.can_vote_on_reviews():
            perms.append('vote_reviews')
        if self.can_borrow_books():
            perms.append('borrow_books')
        return list(set(perms))

    def to_dict(self):
        """Convert model to dictionary for JSON serialization"""
        return {
            "id": self.id,
            "email": self.email,
            "username": self.username,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "role": self.role.value if self.role else None,
            "status": self.status.value if self.status else None,
            "full_name": self.full_name,
            "permissions": self.permissions,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "last_login": self.last_login.isoformat() if self.last_login else None
        }
