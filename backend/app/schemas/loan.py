"""
Schemas for book loan and reservation operations.
"""
from pydantic import BaseModel, Field, validator
from typing import Optional, List
from datetime import datetime, timedelta
from enum import Enum
from decimal import Decimal
from .author import AuthorSummary

class LoanStatus(str, Enum):
    ACTIVE = "Active"
    RETURNED = "Returned"
    OVERDUE = "Overdue"
    RENEWED = "Renewed"
    LOST = "Lost"
    DAMAGED = "Damaged"

class ReservationStatus(str, Enum):
    PENDING = "Pending"
    READY = "Ready"
    FULFILLED = "Fulfilled"
    EXPIRED = "Expired"
    CANCELLED = "Cancelled"

# Simplified book schema for loan responses
class BookSummary(BaseModel):
    """Lightweight book representation for loan listings"""
    id: int
    title: str
    authors: List[AuthorSummary] = []
    
    class Config:
        from_attributes = True

# Book Loan Schemas
class BookLoanCreate(BaseModel):
    book_id: int = Field(..., description="ID of the book to loan")
    user_id: int = Field(..., description="ID of the user borrowing the book")
    due_date: Optional[datetime] = Field(None, description="Due date for return (defaults to 2 weeks)")
    notes: Optional[str] = Field(None, max_length=500, description="Additional notes")

    @validator('due_date', pre=True, always=True)
    def set_default_due_date(cls, v):
        if v is None:
            return datetime.now() + timedelta(days=14)  # Default 2 weeks
        return v

class BookLoanUpdate(BaseModel):
    status: Optional[LoanStatus] = None
    return_date: Optional[datetime] = None
    due_date: Optional[datetime] = None
    fine_amount: Optional[Decimal] = Field(None, ge=0, description="Fine amount (non-negative)")
    notes: Optional[str] = Field(None, max_length=500)

class BookLoanResponse(BaseModel):
    id: int
    book_id: int
    user_id: int
    loan_date: datetime
    due_date: datetime
    return_date: Optional[datetime]
    status: LoanStatus
    renewal_count: int
    fine_amount: Decimal
    notes: Optional[str]
    is_overdue: bool
    days_until_due: Optional[int]
    created_at: datetime
    updated_at: datetime
    
    # Related objects
    book: Optional[BookSummary] = None
    user_email: Optional[str] = None
    
    class Config:
        from_attributes = True
        use_enum_values = True

class PaginatedLoanResponse(BaseModel):
    items: list[BookLoanResponse]
    total: int
    page: int
    size: int
    pages: int

class LoanListResponse(BaseModel):
    total: int
    loans: List[BookLoanResponse]

class BookLoanRenewal(BaseModel):
    extension_days: int = Field(14, ge=1, le=30, description="Number of days to extend (1-30)")
    notes: Optional[str] = Field(None, max_length=500)

# Book Reservation Schemas
class BookReservationCreate(BaseModel):
    book_id: int = Field(..., description="ID of the book to reserve")
    user_id: int = Field(..., description="ID of the user making the reservation")
    expiry_date: Optional[datetime] = Field(None, description="Expiration date (defaults to 7 days)")
    priority: int = Field(1, ge=1, le=5, description="Priority level (1-5, higher is more urgent)")
    notes: Optional[str] = Field(None, max_length=500, description="Additional notes")

    @validator('expiry_date', pre=True, always=True)
    def set_default_expiry_date(cls, v):
        if v is None:
            return datetime.now() + timedelta(days=7)  # Default 7 days
        return v

class BookReservationUpdate(BaseModel):
    status: Optional[ReservationStatus] = None
    expiry_date: Optional[datetime] = None
    priority: Optional[int] = Field(None, ge=1, le=5)
    notification_sent: Optional[bool] = None
    notes: Optional[str] = Field(None, max_length=500)

class BookReservationResponse(BaseModel):
    id: int
    book_id: int
    user_id: int
    reservation_date: datetime
    expiry_date: datetime
    status: ReservationStatus
    notification_sent: bool
    priority: int
    queue_position: Optional[int] = None
    notes: Optional[str]
    is_expired: bool
    created_at: datetime
    updated_at: datetime
    
    # Related objects
    book_title: Optional[str] = None
    user_email: Optional[str] = None
    
    class Config:
        from_attributes = True
        use_enum_values = True

# Loan Statistics
class LoanStatistics(BaseModel):
    total_loans: int
    active_loans: int
    overdue_loans: int
    returned_loans: int
    total_fine_amount: Decimal
    most_borrowed_books: list = []
    top_borrowers: list = []

class ReservationStatistics(BaseModel):
    total_reservations: int
    pending_reservations: int
    fulfilled_reservations: int
    expired_reservations: int
    cancelled_reservations: int
    most_reserved_books: list = []

# User Loan History
class UserLoanHistory(BaseModel):
    user_id: int
    total_loans: int
    active_loans: int
    overdue_loans: int
    total_fines: Decimal
    recent_loans: list = []

class UserReservationHistory(BaseModel):
    user_id: int
    total_reservations: int
    pending_reservations: int
    fulfilled_reservations: int
    recent_reservations: list = []

# Book Availability Info
class BookAvailabilityInfo(BaseModel):
    book_id: int
    total_copies: int
    available_copies: int
    reserved_copies: int
    loaned_copies: int
    reservation_queue_length: int
    estimated_availability_date: Optional[datetime] = None
    can_reserve: bool = True
